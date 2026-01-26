"""日程表数据模型"""

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Schedule(Base):
    """日程表基本信息表"""
    __tablename__ = "schedule"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    student_name = Column(String(50), nullable=False, comment="学生姓名")
    student_class = Column(String(50), comment="学生班级")
    week_offset = Column(Integer, default=0, comment="周次偏移量")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    tasks = relationship("Task", backref="schedule", cascade="all, delete-orphan")


class Task(Base):
    """日常任务表"""
    __tablename__ = "task"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedule.id"), nullable=False, comment="日程表ID")
    date_key = Column(String(20), nullable=False, comment="日期键 YYYY-MM-DD")
    task_name = Column(String(200), nullable=False, comment="任务名称")
    stars = Column(Integer, default=0, comment="星星数量 0-5")
    order_index = Column(Integer, default=0, comment="排序索引")
