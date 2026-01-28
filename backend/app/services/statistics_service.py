"""统计服务"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
from pathlib import Path

from app.models.statistics import Statistics
from app.models.schedule import Schedule
from app.models.achievement import UserAchievement
from app.schemas.statistics import StatisticsSummary, RecordVisitRequest
from app.config import settings


class StatisticsService:
    """统计服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_summary(self) -> StatisticsSummary:
        """
        获取统计摘要信息
        
        返回:
            StatisticsSummary: 包含总用户数、总访问次数、日程数、阅读题数、成就数和最后更新时间
        """
        # 查询总用户数
        total_users = self.db.query(Statistics).count()
        
        # 查询总访问次数
        total_visits = self.db.query(func.sum(Statistics.visit_count)).scalar() or 0
        
        # 查询日程表数量
        total_schedules = self.db.query(Schedule).count()
        
        # 查询阅读题数量（文件数）
        quiz_dir = settings.QUIZ_DIR
        total_quizzes = len(list(quiz_dir.glob("*.json")))
        
        # 查询成就解锁数量
        total_achievements = self.db.query(UserAchievement).count()
        
        # 获取最后更新时间（最新访问时间）
        last_visit = self.db.query(func.max(Statistics.last_visit)).scalar()
        if last_visit is None:
            last_visit = datetime.now()
        
        return StatisticsSummary(
            total_users=total_users,
            total_visits=total_visits,
            total_schedules=total_schedules,
            total_quizzes=total_quizzes,
            total_achievements=total_achievements,
            last_updated=last_visit
        )

    def record_visit(self, request: RecordVisitRequest) -> bool:
        """
        记录用户访问
        
        参数:
            request: RecordVisitRequest 包含IP地址和用户代理信息
            
        返回:
            bool: 记录是否成功
        """
        try:
            # 查找是否已存在该IP的记录
            existing_record = self.db.query(Statistics).filter(
                Statistics.ip_address == request.ip_address
            ).first()

            if existing_record:
                # 更新现有记录
                existing_record.visit_count += 1
                existing_record.last_visit = datetime.now()
                if request.user_agent:
                    existing_record.user_agent = request.user_agent
            else:
                # 创建新记录
                new_record = Statistics(
                    ip_address=request.ip_address,
                    user_agent=request.user_agent,
                    visit_count=1,
                    first_visit=datetime.now(),
                    last_visit=datetime.now()
                )
                self.db.add(new_record)

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"记录访问失败: {e}")
            return False

    def get_client_ip(self, request) -> str:
        """
        从请求对象中获取客户端真实IP地址
        
        参数:
            request: FastAPI Request 对象
            
        返回:
            str: 客户端IP地址
        """
        # 优先使用直接连接的客户端IP
        if request.client and request.client.host:
            return request.client.host

        # 检查代理头（支持反向代理场景）
        ip = request.headers.get("X-Forwarded-For")
        if ip:
            # X-Forwarded-For 可能包含多个IP，取第一个
            return ip.split(",")[0].strip()

        ip = request.headers.get("X-Real-IP")
        if ip:
            return ip.strip()

        # 如果都获取不到，返回默认值
        return "unknown"
