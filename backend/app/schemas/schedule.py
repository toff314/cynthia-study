"""日程表相关的 Pydantic 模型"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ScheduleBase(BaseModel):
    """日程表基础模型"""
    student_name: str
    student_class: Optional[str] = None
    week_offset: int = 0


class ScheduleCreate(ScheduleBase):
    """创建日程表模型"""
    pass


class ScheduleUpdate(ScheduleBase):
    """更新日程表模型"""
    pass


class ScheduleResponse(ScheduleBase):
    """日程表响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    """任务基础模型"""
    date_key: str
    task_name: str
    stars: int = 0
    order_index: int = 0


class TaskCreate(TaskBase):
    """创建任务模型"""
    pass


class taskUpdate(BaseModel):
    """更新任务模型"""
    task_name: Optional[str] = None
    stars: Optional[int] = None


class TaskResponse(TaskBase):
    """任务响应模型"""
    id: int
    
    class Config:
        from_attributes = True


class ScheduleData(BaseModel):
    """完整日程表数据模型"""
    student_name: str
    student_class: Optional[str] = None
    week_offset: int = 0
    weekly_tasks: dict = {}  # {"2024-01-22": {"tasks": [...]}}
