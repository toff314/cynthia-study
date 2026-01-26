"""成就数据模型"""

from sqlalchemy import Column, Integer, Boolean, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Achievement(Base):
    """成就定义表"""
    __tablename__ = "achievement"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    is_hidden = Column(Boolean, default=False, comment="是否隐藏成就")
    code = Column(String(50), nullable=False, unique=True, comment="成就代码")
    name = Column(String(100), nullable=False, comment="成就名称")
    description = Column(String(500), comment="成就描述")
    icon = Column(String(50), comment="成就图标emoji")
    level = Column(String(20), comment="成就等级：bronze/silver/gold")
    task_match_type = Column(String(20), comment="匹配类型：exact/contains/prefix")
    task_keywords = Column(String(500), comment="任务关键词，逗号分隔")
    unlock_condition = Column(String(500), comment="解锁条件描述")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    user_achievements = relationship("UserAchievement", backref="achievement", cascade="all, delete-orphan")


class UserAchievement(Base):
    """用户成就表"""
    __tablename__ = "user_achievement"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    achievement_id = Column(Integer, ForeignKey("achievement.id"), nullable=False, comment="成就ID")
    schedule_id = Column(Integer, ForeignKey("schedule.id"), nullable=False, comment="日程表ID")
    unlocked_at = Column(DateTime, server_default=func.now(), comment="解锁时间")
    unlock_count = Column(Integer, default=1, comment="解锁次数（完成对应任务次数）")
