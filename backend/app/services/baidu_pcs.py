"""
百度网盘客户端（基于 baidupan / baiduban 命令行工具）

参考 libretv-enhanced 项目实现：所有网盘操作通过调用 CLI 完成，不保留
任何 PCS 协议细节。支持列出目录与下载文件。

二进制查找顺序：
  1. 环境变量 BAIDUPAN_BIN
  2. PATH 中的 baidupan
  3. PATH 中的 baiduban（兼容命名）

鉴权信息（cookies / BDUSS / STOKEN）通过环境变量传给 CLI，避免在进程
列表中泄露敏感值。
"""
import json
import logging
import os
import shutil
import subprocess
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BaiduPCSError(Exception):
    def __init__(self, message: str, errno: int = 0):
        super().__init__(message)
        self.errno = errno


def find_baidu_binary() -> str:
    """定位 baidupan / baiduban 可执行文件"""
    env_bin = os.environ.get("BAIDUPAN_BIN")
    if env_bin:
        if os.path.exists(env_bin) and os.access(env_bin, os.X_OK):
            return env_bin
        raise BaiduPCSError(f"BAIDUPAN_BIN 指向的文件不可执行: {env_bin}")

    for name in ("baidupan", "baiduban"):
        found = shutil.which(name)
        if found:
            return found

    raise BaiduPCSError(
        "未找到 baidupan/baiduban 命令。请先构建并安装：\n"
        "  cd tools/baidu-pan-cli && go build -o baidupan .\n"
        "  sudo cp baidupan /usr/local/bin/\n"
        "或设置 BAIDUPAN_BIN 环境变量。"
    )


class BaiduPCSClient:
    """基于 baidupan CLI 的轻量百度网盘客户端（列出目录 / 下载文件）"""

    def __init__(self, cookies: Optional[str] = None, bduss: Optional[str] = None, stoken: Optional[str] = None):
        self._binary = find_baidu_binary()
        self._env = os.environ.copy()
        if cookies:
            self._env["BAIDUPAN_COOKIES"] = cookies
        if bduss:
            self._env["BAIDUPAN_BDUSS"] = bduss
        if stoken:
            self._env["BAIDUPAN_STOKEN"] = stoken

    def _run(self, subcmd: str, args: List[str], timeout: int = 600) -> subprocess.CompletedProcess:
        cmd = [self._binary, subcmd] + args
        logger.debug("baidupan cli: %s", " ".join(cmd))
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=self._env)
        except FileNotFoundError as e:
            raise BaiduPCSError(f"baidupan 命令不存在: {e}") from e
        except subprocess.TimeoutExpired as e:
            raise BaiduPCSError(f"baidupan {subcmd} 执行超时") from e

        if result.returncode != 0:
            err = result.stderr.strip() or result.stdout.strip() or f"{subcmd} failed"
            raise BaiduPCSError(err)
        return result

    def list_dir(self, path: str) -> List[Dict]:
        """列出远程目录内容"""
        result = self._run("ls", ["--json", path], timeout=120)
        try:
            items = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise BaiduPCSError(f"baidupan ls 输出解析失败: {result.stdout[:200]}") from e

        return [
            {
                "server_filename": it.get("server_filename", ""),
                "path": it.get("path", ""),
                "isdir": 1 if it.get("isdir") else 0,
                "size": it.get("size", 0),
            }
            for it in items
        ]

    def file_exists(self, path: str) -> bool:
        """检查远程文件是否存在"""
        try:
            parent = os.path.dirname(path)
            filename = os.path.basename(path)
            for item in self.list_dir(parent):
                if item.get("server_filename") == filename and not item.get("isdir"):
                    return True
            return False
        except BaiduPCSError:
            return False

    def download_file(self, path: str, local_path: str, chunk_size: int = 1024 * 1024) -> None:
        """下载远程文件到本地路径"""
        local_abs = os.path.abspath(local_path)
        parent = os.path.dirname(local_abs)
        if parent:
            os.makedirs(parent, exist_ok=True)
        self._run("download", [path, local_abs], timeout=1800)


__all__ = ["BaiduPCSClient", "BaiduPCSError"]
