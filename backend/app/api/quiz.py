"""阅读题API"""

import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.schemas.quiz import FilesResponse, FileContentResponse, QuizSaveResponse
from app.services.quiz_service import QuizService

router = APIRouter()


class ApiResponse(BaseModel):
    """通用API响应"""
    success: bool
    data: dict = {}
    message: str = ""


@router.get("/quiz/files", response_model=ApiResponse)
async def get_quiz_files():
    """获取JSON文件列表"""
    service = QuizService()
    files = service.get_files()
    
    return ApiResponse(
        success=True,
        data={"files": [f.model_dump() for f in files]}
    )


@router.get("/quiz/file")
async def get_quiz_file(name: str = Query(..., description="文件名")):
    """获取单个文件内容"""
    service = QuizService()
    content = service.get_file_content(name)
    
    if content is None:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return ApiResponse(
        success=True,
        data={"content": content}
    )


@router.post("/quiz/save")
async def save_quiz(data: Dict[str, Any]):
    """保存JSON文件"""
    service = QuizService()
    result = service.save_quiz(data)
    
    if not result["filename"]:
        raise HTTPException(status_code=400, detail="保存失败")
    
    from app.config import settings
    return ApiResponse(
        success=True,
        data={
            "filename": result["filename"],
            "path": f"@quizzes/{result['filename']}"
        },
        message=f"文件已保存至 @data/quizzes/{result['filename']}"
    )


@router.post("/quiz/upload")
async def upload_quiz(content: str = Query(..., description="JSON内容")):
    """上传JSON文件内容"""
    try:
        data = json.loads(content)
        service = QuizService()
        result = service.save_quiz(data)
        
        return ApiResponse(
            success=True,
            data={
                "filename": result["filename"],
                "path": f"@data/quizzes/{result['filename']}"
            },
            message=f"文件已保存至 @data/quizzes/{result['filename']}"
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON格式错误")
