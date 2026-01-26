"""文件辅助函数"""

import random
import string
from datetime import datetime
from pathlib import Path

from app.config import settings


def generate_random_string(length: int = 6) -> str:
    """生成随机字符串"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_filename(title: str) -> str:
    """生成文件名：标题 + 日期 + 随机值"""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    random_str = generate_random_string(settings.FILENAME_RANDOM_LENGTH)
    
    # 清理标题中的特殊字符
    clean_title = title.replace('<', '_')\
                      .replace('>', '_')\
                      .replace(':', '_')\
                      .replace('/', '_')\
                      .replace('\\', '_')\
                      .replace('|', '_')\
                      .replace('?', '_')\
                      .replace('*', '_')
    
    return f"{clean_title}_{date_str}_{random_str}.json"


def get_file_size(file_path: Path) -> int:
    """获取文件大小"""
    return file_path.stat().st_size


def format_file_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"
