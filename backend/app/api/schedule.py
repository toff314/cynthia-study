"""日程表API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

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
async def get_schedule(
    student_name: str = Query(..., description="学生姓名"),
    student_class: str = Query(..., description="学生班级"),
    db: Session = Depends(get_db)
):
    """获取日程表数据（必传学生姓名和班级）"""
    service = ScheduleService(db)
    schedule = service.get_schedule(student_name, student_class)
    
    if not schedule:
        return ApiResponse(
            success=True,
            data={
                "id": None,
                "student_name": student_name,
                "student_class": student_class,
                "week_offset": 0,
                "weekly_tasks": {}
            }
        )
    
    tasks = service.get_all_tasks(student_name, student_class)
    weekly_tasks = {}
    if tasks:
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
            "id": schedule.id,
            "student_name": schedule.student_name,
            "student_class": schedule.student_class,
            "week_offset": schedule.week_offset,
            "weekly_tasks": weekly_tasks
        }
    )


@router.get("/schedule/students")
async def get_all_students(db: Session = Depends(get_db)):
    """获取所有学生列表"""
    service = ScheduleService(db)
    students = service.get_all_students()
    
    return ApiResponse(
        success=True,
        data={
            "students": [
                {
                    "id": s.id,
                    "student_name": s.student_name,
                    "student_class": s.student_class
                }
                for s in students
            ]
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
