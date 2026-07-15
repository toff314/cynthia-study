"""
绘本阅读业务服务：云端目录列表、下载、转换、清理。
"""
import json
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from app.config import settings
from app.services.baidu_pcs import BaiduPCSClient, BaiduPCSError


def load_baidu_config() -> dict:
    """读取 ~/.config/cynthia-study/baidu_config.json"""
    config_file = settings.READING_CONFIG_FILE
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise BaiduPCSError(f"Failed to load baidu config: {e}")
    return {}


def create_baidu_client() -> BaiduPCSClient:
    config = load_baidu_config()
    if not config.get("baidu_cookies") and not config.get("baidu_bduss"):
        raise BaiduPCSError(
            "Baidu credentials not configured. "
            f"Please create {settings.READING_CONFIG_FILE} with baidu_cookies / baidu_bduss / baidu_stoken."
        )
    return BaiduPCSClient(
        cookies=config.get("baidu_cookies") or None,
        bduss=config.get("baidu_bduss") or None,
        stoken=config.get("baidu_stoken") or None,
    )


def list_reading_directory(path: Optional[str] = None):
    """列出云端目录内容。path 为 None 时使用默认根路径。"""
    client = create_baidu_client()
    target_path = path or settings.READING_ROOT_PATH
    items = client.list_dir(target_path)
    return [
        {
            "name": item.get("server_filename"),
            "path": item.get("path"),
            "is_dir": item.get("isdir") == 1,
            "size": item.get("size"),
        }
        for item in items
    ]


def _convert_ppt_to_pdf(ppt_file: Path, output_dir: Path) -> Path:
    """使用 LibreOffice 将 PPT 转为 PDF"""
    cmd = [
        "soffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(output_dir),
        str(ppt_file),
    ]
    try:
        subprocess.run(cmd, check=True, timeout=300, capture_output=True, text=True)
    except FileNotFoundError as e:
        raise RuntimeError("LibreOffice (soffice) not found. Please install libreoffice-impress.") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"PPT to PDF conversion failed: {e.stderr}") from e

    pdf_file = output_dir / f"{ppt_file.stem}.pdf"
    if not pdf_file.exists():
        raise RuntimeError(f"PPT conversion did not produce expected PDF: {pdf_file}")
    return pdf_file


def _convert_pdf_to_images(pdf_file: Path, output_dir: Path) -> int:
    """使用 PyMuPDF 将 PDF 逐页转为 PNG 图片"""
    doc = fitz.open(str(pdf_file))
    for i in range(len(doc)):
        page = doc.load_page(i)
        # 150 dpi 兼顾清晰度与文件大小
        pix = page.get_pixmap(dpi=150)
        pix.save(str(output_dir / f"page_{i + 1}.png"))
    return len(doc)


def convert_to_images(remote_path: str) -> dict:
    """下载远程文件并转换为图片，返回 task_id 与页数。"""
    client = create_baidu_client()
    task_id = str(uuid.uuid4())
    task_dir = settings.READING_CACHE_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    try:
        ext = Path(remote_path).suffix.lower()
        if ext not in (".pdf", ".ppt", ".pptx"):
            raise ValueError(f"Unsupported file format: {ext}")

        source_file = task_dir / f"source{ext}"
        client.download_file(remote_path, str(source_file))

        pdf_file = source_file
        if ext in (".ppt", ".pptx"):
            pdf_file = _convert_ppt_to_pdf(source_file, task_dir)

        pages = _convert_pdf_to_images(pdf_file, task_dir)

        # 清理中间产物，只保留 PNG 图片
        if source_file.exists():
            source_file.unlink()
        if pdf_file != source_file and pdf_file.exists():
            pdf_file.unlink()

        return {"task_id": task_id, "pages": pages}
    except Exception:
        # 失败时清理本次任务目录
        if task_dir.exists():
            shutil.rmtree(task_dir)
        raise


def get_image_path(task_id: str, page: int) -> Path:
    return settings.READING_CACHE_DIR / task_id / f"page_{page}.png"


def cleanup_reading_cache() -> None:
    """删除所有绘本阅读临时缓存。"""
    if settings.READING_CACHE_DIR.exists():
        shutil.rmtree(settings.READING_CACHE_DIR)
    settings.READING_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def task_dir_exists(task_id: str) -> bool:
    return (settings.READING_CACHE_DIR / task_id).exists()
