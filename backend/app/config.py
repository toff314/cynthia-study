"""配置文件"""

from pathlib import Path
from typing import Optional


class Settings:
    """应用配置类"""
    
    # 项目根目录
    BASE_DIR: Path = Path(__file__).parent.parent
    
    # 数据库配置
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/cynthia.db"
    
    # 数据目录
    DATA_DIR: Path = BASE_DIR / "data"
    QUIZ_DIR: Path = DATA_DIR / "quizzes"
    
    # API 配置
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list = ["*"]  # 开发环境允许所有跨域
    
    # 文件命名配置
    FILENAME_RANDOM_LENGTH: int = 6
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 绘本阅读模块配置
    READING_CACHE_DIR: Path = DATA_DIR / "cache" / "reading"
    READING_CONFIG_DIR: Path = Path.home() / ".config" / "cynthia-study"
    READING_CONFIG_FILE: Path = READING_CONFIG_DIR / "baidu_config.json"
    READING_ROOT_PATH: str = "/团团园圆/绘本/【1】3000套中文绘本（67G）"
    
    # 确保 data 目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    QUIZ_DIR.mkdir(parents=True, exist_ok=True)
    READING_CACHE_DIR.mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()
