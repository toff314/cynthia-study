"""阅读题API"""

import json
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
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
    try:
        service = QuizService()
        result = service.save_quiz(data)
        
        return ApiResponse(
            success=True,
            data={
                "filename": result["filename"],
                "path": f"@quizzes/{result['filename']}"
            },
            message=f"文件已保存为 {result['filename']}"
        )
    except ValueError as e:
        # 处理验证错误（文件名验证、路径安全等）
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 处理其他错误
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.post("/quiz/upload")
async def upload_quiz(content: str = Query(..., description="JSON内容")):
    """上传JSON文件内容"""
    try:
        service = QuizService()
        title = ""
        result = service.upload_file(content, title)
        
        return ApiResponse(
            success=True,
            data={
                "filename": result["filename"],
                "path": f"@data/quizzes/{result['filename']}"
            },
            message=f"文件已保存为 {result['filename']}"
        )
    except ValueError as e:
        # 处理验证错误（文件大小、格式、安全性等）
        raise HTTPException(status_code=400, detail=str(e))
    except json.JSONDecodeError as e:
        # 处理JSON解析错误
        raise HTTPException(status_code=400, detail=f"JSON格式错误: {str(e)}")
    except Exception as e:
        # 处理其他未知错误
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/quiz/download")
async def download_quiz_file(name: str = Query(..., description="文件名")):
    """下载JSON文件"""
    from app.config import settings
    from fastapi.responses import Response
    
    service = QuizService()
    content = service.get_file_content(name)
    # 打印日志
    print(f"Attempting to download file: {name}")
    print(f"File content found: {content is not None}")
    
    if content is None:
        # 尝试 glob 匹配文件（处理编码问题）
        import glob
        pattern = str(settings.QUIZ_DIR / "*.json")
        matching_files = glob.glob(pattern)
        
        # 查找匹配的文件（按文件名部分匹配）
        base_name = name.rsplit('_', 1)[0] if '_' in name else name
        for file_path in matching_files:
            file_name = Path(file_path).name
            if file_name == name or (base_name in file_name):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                break
        
        if content is None:
            raise HTTPException(status_code=404, detail=f"文件不存在: {name}")
    
    # 使用URL编码处理中文文件名
    from urllib.parse import quote
    encoded_filename = quote(name)
    
    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{encoded_filename}"'
        }
    )
