"""成就相关API路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.achievement_service import AchievementService
from app.models.achievement import UserAchievement

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get("")
def get_all_achievements(db: Session = Depends(get_db)):
    """获取所有成就定义"""
    service = AchievementService(db)
    achievements = service.get_all_achievements()
    return {"success": True, "data": achievements}


@router.get("/student/{schedule_id}")
def get_student_achievements(schedule_id: int, db: Session = Depends(get_db)):
    """获取学生的所有成就（包含解锁状态）"""
    service = AchievementService(db)
    achievements = service.get_student_achievements(schedule_id)
    return {"success": True, "data": achievements}


@router.get("/ranking")
def get_all_students_ranking(db: Session = Depends(get_db)):
    """获取所有学生的成就排名"""
    service = AchievementService(db)
    rankings = service.get_all_students_ranking()
    return {"success": True, "data": rankings}


@router.get("/statistics/{schedule_id}")
def get_statistics(schedule_id: int, db: Session = Depends(get_db)):
    """获取学生的统计数据"""
    service = AchievementService(db)
    statistics = service.get_statistics(schedule_id)
    return {"success": True, "data": statistics}


@router.get("/timeline/{schedule_id}")
def get_timeline(schedule_id: int, db: Session = Depends(get_db)):
    """获取学生的时间线事件"""
    service = AchievementService(db)
    timeline = service.get_timeline(schedule_id)
    return {"success": True, "data": timeline}


@router.post("/check-unlock/{schedule_id}")
def check_and_unlock_achievements(schedule_id: int, db: Session = Depends(get_db)):
    """检查并解锁成就"""
    service = AchievementService(db)
    newly_unlocked = service.check_and_unlock_achievements(schedule_id)
    unlocked_count = len(newly_unlocked)
    
    # 转换为 Pydantic 模型
    from app.schemas.achievement import AchievementResponse
    newly_unlocked_data = [AchievementResponse.model_validate(a) for a in newly_unlocked]
    
    result = {
        "success": True,
        "data": {
            "newly_unlocked_count": unlocked_count,
            "newly_unlocked": newly_unlocked_data
        },
        "message": f"解锁了 {unlocked_count} 个新成就！" if newly_unlocked else "没有新成就解锁"
    }
    return result


@router.post("/initialize")
def initialize_default_achievements(db: Session = Depends(get_db)):
    """初始化默认成就"""
    service = AchievementService(db)
    service.initialize_default_achievements()
    return {"success": True, "message": "成就数据已初始化"}


@router.delete("/reset/{schedule_id}")
def reset_student_achievements(schedule_id: int, db: Session = Depends(get_db)):
    """重置学生的成就记录（删除所有已解锁的成就）"""
    # 删除该学生的所有成就记录
    deleted_count = db.query(UserAchievement).filter(
        UserAchievement.schedule_id == schedule_id
    ).delete()
    db.commit()
    
    return {
        "success": True,
        "message": f"已删除 {deleted_count} 条成就记录",
        "data": {"deleted_count": deleted_count}
    }
