"""日程表API"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schedule import ScheduleData, ScheduleResponse
from app.services.schedule_service import ScheduleService

router = APIRouter()


class ApiResponse(BaseModel):
    """通用API响应"""
    success: bool
    data: dict = {}
    message: str = ""


@router.get("/schedule")
async def get_schedule(db: Session = Depends(get_db)):
    """获取日程表数据"""
    service = ScheduleService(db)
    schedule = service.get_schedule()
    
    if not schedule:
        return ApiResponse(
            success=True,
            data={
                "student_name": "",
                "student_class": "",
                "week_offset": 0,
                "weekly_tasks": {}
            }
        )
    
    tasks = service.get_all_tasks()
    weekly_tasks = {}
    for date_key, task_list in tasks.items():
        weekly_tasks[date_key] = {
            "tasks": [
                {
                    "id": t.id,
                    "task_name": t.task_name,
                    "name": t.task_name,
                    "stars": t.stars
                }
                for t in task_list
            ]
        }
    
    return ApiResponse(
        success=True,
        data={
            "student_name": schedule.student_name,
            "student_class": schedule.student_class,
            "week_offset": schedule.week_offset,
            "weekly_tasks": weekly_tasks
        }
    )


@router.post("/schedule")
async def save_schedule(data: ScheduleData, db: Session = Depends(get_db)):
    """保存日程表数据"""
    service = ScheduleService(db)
    schedule = service.create_or_update_schedule(data)
    
    return ApiResponse(
        success=True,
        message="日程表保存成功"
    )


@router.delete("/schedule")
async def clear_schedule(db: Session = Depends(get_db)):
    """清空所有日程表数据"""
    service = ScheduleService(db)
    service.clear_all_data()
    
    return ApiResponse(
        success=True,
        message="日程表已清空"
    )
