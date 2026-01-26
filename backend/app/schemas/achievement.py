"""成就相关的Pydantic模型"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AchievementBase(BaseModel):
    """成就基础模型"""
    code: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    level: Optional[str] = None
    task_match_type: str = "contains"
    task_keywords: Optional[str] = None
    unlock_condition: Optional[str] = None


class AchievementCreate(AchievementBase):
    """创建成就模型"""
    pass


class AchievementResponse(AchievementBase):
    """成就响应模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AchievementDetail(AchievementResponse):
    """成就详情（包含解锁状态）"""
    is_hidden: bool = False  # 是否隐藏成就
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    unlock_count: int = 0


class UserAchievementResponse(BaseModel):
    """用户成就响应模型"""
    id: int
    achievement_id: int
    achievement_name: str
    achievement_icon: str
    achievement_level: str
    unlocked_at: datetime
    unlock_count: int
    
    class Config:
        from_attributes = True


class StudentRanking(BaseModel):
    """学生排名模型"""
    schedule_id: int
    student_name: str
    student_class: Optional[str] = None
    total_achievements: int
    achievement_list: List[AchievementResponse]


class TimelineEvent(BaseModel):
    """时间线事件模型"""
    date: str
    event_type: str  # "task_completed", "achievement_unlocked"
    description: str
    icon: Optional[str] = None


class AchievementsSummary(BaseModel):
    """成就统计摘要"""
    total_achievements: int
    unlocked_achievements: int
    locked_achievements: int
    hidden_achievements: int  # 隐藏成就数量
    completion_rate: float  # 百分比


class StatisticsData(BaseModel):
    """统计数据模型"""
    reading_days: int  # 阅读天数
    exercise_duration: int  # 运动时长（分钟）
    challenges_completed: int  # 挑战完成数
    total_stars: int  # 总星星数
    achievements_summary: AchievementsSummary
