"""统计数据模型"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Statistics(Base):
    """访问统计表"""
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="主键ID")
    ip_address = Column(String(50), unique=True, index=True, comment="访问IP地址")
    user_agent = Column(String(500), comment="用户代理")
    visit_count = Column(Integer, default=1, comment="访问次数")
    first_visit = Column(DateTime, default=func.now(), comment="首次访问时间")
    last_visit = Column(DateTime, default=func.now(), onupdate=func.now(), comment="最后访问时间")

    def __repr__(self):
        return f"<Statistics(ip_address='{self.ip_address}', visit_count={self.visit_count})>"
