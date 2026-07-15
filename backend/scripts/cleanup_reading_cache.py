#!/usr/bin/env python3
"""
清理绘本阅读模块临时缓存。
建议通过 crontab 每日执行一次。
"""
import sys
from pathlib import Path

# 将 backend 目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.reading_service import cleanup_reading_cache


if __name__ == "__main__":
    cleanup_reading_cache()
    print("Reading cache cleaned up")
