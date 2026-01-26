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
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # 如果表已存在且缺少schedule_id列，则删除所有表重建
    if 'task' in tables:
        task_columns = [col['name'] for col in inspector.get_columns('task')]
        if 'schedule_id' not in task_columns:
            print("⚠️  检测到旧表结构，正在重建数据库...")
            Base.metadata.drop_all(bind=engine)
            print("✅ 旧表已删除")
    
    Base.metadata.create_all(bind=engine)
