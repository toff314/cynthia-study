"""数据库连接配置"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 需要
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话依赖注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表 - 强制重建以支持表结构变更"""
    from app.models.schedule import Schedule, Task
    from app.models.achievement import Achievement, UserAchievement
    from app.services.achievement_service import AchievementService
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 初始化成就数据
    db = SessionLocal()
    try:
        achievement_service = AchievementService(db)
        achievement_service.initialize_default_achievements()
    finally:
        db.close()
