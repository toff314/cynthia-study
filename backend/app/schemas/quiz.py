"""阅读题相关的 Pydantic 模型"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class FileInfo(BaseModel):
    """文件信息模型"""
    name: str
    size: int
    modified: str


class FilesResponse(BaseModel):
    """文件列表响应模型"""
    files: List[FileInfo]


class FileContentResponse(BaseModel):
    """文件内容响应模型"""
    content: str


class QuizData(BaseModel):
    """阅读题数据模型"""
    title: str
    subtitle: Optional[str] = None
    sections: List[Dict[str, Any]] = []


class QuizSaveResponse(BaseModel):
    """保存阅读题响应模型"""
    filename: str
    path: str
