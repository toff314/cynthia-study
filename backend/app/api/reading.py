"""
绘本阅读模块 API 路由
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.services.reading_service import (
    list_reading_directory,
    convert_to_images,
    get_image_path,
    cleanup_reading_cache,
    task_dir_exists,
)
from app.services.baidu_pcs import BaiduPCSError

router = APIRouter(prefix="/reading", tags=["reading"])


class ReadRequest(BaseModel):
    path: str


@router.get("/list")
def api_list(path: str | None = Query(None)):
    try:
        items = list_reading_directory(path)
        return {"success": True, "data": items}
    except BaiduPCSError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read")
def api_read(req: ReadRequest):
    try:
        result = convert_to_images(req.path)
        return {
            "success": True,
            "data": {
                "task_id": result["task_id"],
                "pages": result["pages"],
                "image_urls": [
                    f"/api/reading/images/{result['task_id']}/{i}"
                    for i in range(1, result["pages"] + 1)
                ],
            },
        }
    except BaiduPCSError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{task_id}/{page}")
def api_image(task_id: str, page: int):
    image_path = get_image_path(task_id, page)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(str(image_path), media_type="image/png")


@router.post("/cleanup")
def api_cleanup():
    try:
        cleanup_reading_cache()
        return {"success": True, "message": "Cleanup completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
