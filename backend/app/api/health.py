"""健康检查API"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    data_dir: str
    quiz_dir: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="ok",
        data_dir=str(settings.DATA_DIR),
        quiz_dir=str(settings.QUIZ_DIR)
    )
