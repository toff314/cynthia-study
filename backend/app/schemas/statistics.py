"""统计数据Schema"""

from pydantic import BaseModel
from datetime import datetime


class StatisticsSummary(BaseModel):
    """统计摘要响应"""
    total_users: int  # 总用户数
    total_visits: int  # 总访问次数
    total_schedules: int  # 创建的日程数量
    total_quizzes: int  # 生成的阅读题数量（文件数）
    total_achievements: int  # 完成的成就数量
    last_updated: datetime  # 最后更新时间

    class Config:
        from_attributes = True


class RecordVisitRequest(BaseModel):
    """记录访问请求"""
    ip_address: str
    user_agent: str | None = None


class RecordVisitResponse(BaseModel):
    """记录访问响应"""
    success: bool
    message: str


class StatisticsResponse(BaseModel):
    """通用统计响应"""
    success: bool
    data: StatisticsSummary | None = None
    message: str | None = None
