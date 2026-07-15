"""
百度网盘 PCS 客户端（基于新版 Web API）
参考 libretv-enhanced 项目实现，仅保留列出目录与下载能力。
"""
import json
import os
import re
import logging
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import quote, quote_plus

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

PAN_BAIDU_COM = "https://pan.baidu.com"
PCS_BAIDU_COM = "https://pcs.baidu.com"
PAN_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
PAN_HEADERS = {"User-Agent": PAN_UA, "Referer": "https://pan.baidu.com/"}
PAN_APP_ID = "250528"


class BaiduPCSError(Exception):
    def __init__(self, message: str, errno: int = 0):
        super().__init__(message)
        self.errno = errno


class BaiduPCSClient:
    """轻量级百度网盘 PCS 客户端，支持目录列出与文件下载"""

    def __init__(self, cookies: Optional[str] = None, bduss: Optional[str] = None, stoken: Optional[str] = None):
        self._session = requests.Session()
        self._bdstoken: Optional[str] = None

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

        cookie_dict: Dict[str, str] = {}
        if cookies:
            for part in cookies.split(';'):
                part = part.strip()
                if '=' in part:
                    k, v = part.split('=', 1)
                    cookie_dict[k.strip()] = v.strip()

        if bduss:
            cookie_dict['BDUSS'] = bduss
        if stoken:
            cookie_dict['STOKEN'] = stoken

        if not cookie_dict.get('BDUSS'):
            raise BaiduPCSError("BDUSS not found. Please set baidu_cookies or baidu_bduss.")

        self._session.cookies.update(cookie_dict)
        self._session.trust_env = False
        self._cookie_dict = cookie_dict

    def _get_bdstoken(self) -> str:
        if self._bdstoken:
            return self._bdstoken
        url = f"{PAN_BAIDU_COM}/disk/home"
        resp = self._session.get(url, headers=PAN_HEADERS, timeout=10)
        m = re.search(r'bdstoken[\'":\s]+([0-9a-f]{32})', resp.text)
        if m:
            self._bdstoken = m.group(1)
            return self._bdstoken
        return ""

    def _make_logid(self) -> str:
        import random
        return str(random.randint(10**17, 10**18))

    def _request(self, method: str, url: str, params: Optional[Dict] = None,
                 data=None, headers=None, **kwargs) -> requests.Response:
        hdrs = dict(PAN_HEADERS)
        if headers:
            hdrs.update(headers)
        try:
            resp = self._session.request(method, url, params=params, data=data,
                                         headers=hdrs, **kwargs)
            return resp
        except Exception as err:
            raise BaiduPCSError(f"Request failed: {err}")

    def _request_json(self, method: str, url: str, params: Optional[Dict] = None,
                      data=None, headers=None, **kwargs) -> Dict:
        resp = self._request(method, url, params=params, data=data, headers=headers, **kwargs)
        try:
            result = resp.json()
        except Exception:
            raise BaiduPCSError(f"Invalid JSON response: {resp.text[:200]}")
        errno = result.get('errno', 0)
        if errno != 0:
            errmsg = result.get('errmsg', f'errno={errno}')
            raise BaiduPCSError(errmsg, errno=errno)
        return result

    def user_info(self) -> Dict:
        url = f"{PAN_BAIDU_COM}/api/loginStatus"
        resp = self._request("GET", url, params={"clienttype": "0", "app_id": PAN_APP_ID, "web": "1"})
        return resp.json()

    def list_dir(self, path: str) -> List[Dict]:
        """列出远程目录内容"""
        url = f"{PAN_BAIDU_COM}/api/list"
        params = {
            "dir": path,
            "bdstoken": self._get_bdstoken(),
            "app_id": PAN_APP_ID,
            "channel": "chunlei",
            "web": "1",
            "clienttype": "0",
            "dp-logid": self._make_logid(),
        }
        resp = self._session.get(url, params=params, headers=PAN_HEADERS)
        data = resp.json()
        if data.get("errno") != 0:
            raise BaiduPCSError(f"list_dir failed: errno={data.get('errno')}")
        return data.get("list", [])

    def file_exists(self, path: str) -> bool:
        """检查远程文件是否存在"""
        try:
            parent = os.path.dirname(path)
            filename = os.path.basename(path)
            items = self.list_dir(parent)
            for item in items:
                if item.get("server_filename") == filename and not item.get("isdir"):
                    return True
            return False
        except BaiduPCSError:
            return False

    def _get_download_url(self, path: str) -> str:
        """通过旧版 PCS API 获取文件下载 URL（会自动 302 到真实 CDN 地址）"""
        encoded_path = quote(path, safe="")
        url = f"{PCS_BAIDU_COM}/rest/2.0/pcs/file"
        params = {
            "method": "download",
            "app_id": PAN_APP_ID,
            "path": encoded_path,
        }
        return f"{url}?method=download&app_id={PAN_APP_ID}&path={encoded_path}"

    def download_file(self, path: str, local_path: str, chunk_size: int = 1024 * 1024) -> None:
        """下载远程文件到本地路径"""
        download_url = self._get_download_url(path)
        resp = self._session.get(
            download_url,
            headers=PAN_HEADERS,
            stream=True,
            timeout=(30, 600),
            allow_redirects=True,
        )
        resp.raise_for_status()
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)


__all__ = ["BaiduPCSClient", "BaiduPCSError"]
