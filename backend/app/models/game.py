"""益智游戏数据模型"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from ..database import Base


class Game(Base):
    """游戏模型"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    game_type = Column(String(50), nullable=False, comment="游戏类型")
    age_group = Column(String(20), nullable=False, comment="年龄段：low/mid/high")
    title = Column(String(200), nullable=False, comment="游戏标题")
    difficulty = Column(String(20), default="normal", comment="难度：easy/normal/hard")
    content = Column(JSON, nullable=False, comment="游戏内容（JSON格式）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Game {self.game_type} - {self.title}>"
