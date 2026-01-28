"""文件元数据模型"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class FileMetadata(Base):
    """文件元数据表"""
    
    __tablename__ = "file_metadata"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    filename = Column(String(512), unique=True, nullable=False, index=True, comment="文件名")
    md5_hash = Column(String(32), nullable=False, index=True, comment="MD5哈希值")
    file_type = Column(String(50), default="quiz", index=True, comment="文件类型")
    file_size = Column(Integer, default=0, comment="文件大小（字节）")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
