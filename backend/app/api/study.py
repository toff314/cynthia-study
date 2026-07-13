"""学习题库API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.study_service import StudyService
from app.schemas.study import (
    QuestionBankCreate, QuestionBankResponse, QuestionBankBatchCreate,
    QuestionBankBatchResponse, StudyRecordCreate, StudyRecordResponse,
    StudyStatsResponse
)

router = APIRouter(prefix="/study", tags=["study"])


@router.get("/questions")
async def get_questions(
    subject: Optional[str] = Query(None, description="科目筛选"),
    grade: Optional[int] = Query(None, ge=1, le=6, description="年级筛选"),
    question_type: Optional[str] = Query(None, description="题目类型筛选"),
    difficulty: Optional[str] = Query(None, description="难度筛选"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db)
):
    """获取题目列表"""
    try:
        service = StudyService(db)
        items, total = service.get_questions(subject, grade, question_type, difficulty, limit, offset)
        return {
            "success": True,
            "data": {
                "questions": [QuestionBankResponse.model_validate(q).model_dump() for q in items],
                "total": total
            },
            "message": "获取成功"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/questions/{question_id}")
async def get_question(question_id: int, db: Session = Depends(get_db)):
    """获取单道题目"""
    service = StudyService(db)
    question = service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return {
        "success": True,
        "data": QuestionBankResponse.model_validate(question).model_dump(),
        "message": "获取成功"
    }


@router.post("/questions")
async def create_question(data: QuestionBankCreate, db: Session = Depends(get_db)):
    """创建单道题目"""
    try:
        service = StudyService(db)
        question = service.create_question(data)
        return {
            "success": True,
            "data": QuestionBankResponse.model_validate(question).model_dump(),
            "message": "创建成功"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions/batch")
async def batch_create_questions(data: QuestionBankBatchCreate, db: Session = Depends(get_db)):
    """批量导入题目"""
    try:
        service = StudyService(db)
        result = service.batch_create_questions(data.questions)
        return QuestionBankBatchResponse(
            success=True,
            total=len(data.questions),
            created=result["created"],
            skipped=result["skipped"],
            message=f"成功导入 {result['created']} 道题目，跳过 {result['skipped']} 道"
        ).model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/questions/{question_id}")
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    """删除题目"""
    service = StudyService(db)
    if not service.delete_question(question_id):
        raise HTTPException(status_code=404, detail="题目不存在")
    return {"success": True, "message": "删除成功"}


@router.post("/records")
async def create_record(data: StudyRecordCreate, db: Session = Depends(get_db)):
    """提交答题记录"""
    try:
        service = StudyService(db)
        record = service.create_record(data)
        return {
            "success": True,
            "data": StudyRecordResponse.model_validate(record).model_dump(),
            "message": "提交成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/records")
async def get_records(
    student_name: Optional[str] = Query(None, description="学生姓名"),
    limit: int = Query(100, ge=1, le=500, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取答题记录"""
    service = StudyService(db)
    records = service.get_records(student_name, limit)
    return {
        "success": True,
        "data": [StudyRecordResponse.model_validate(r).model_dump() for r in records],
        "message": "获取成功"
    }


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """获取学习统计"""
    service = StudyService(db)
    stats = service.get_stats()
    return {
        "success": True,
        "data": stats,
        "message": "获取成功"
    }


@router.get("/random")
async def get_random_questions(
    subject: Optional[str] = Query(None, description="科目筛选"),
    grade: Optional[int] = Query(None, ge=1, le=6, description="年级筛选"),
    count: int = Query(10, ge=1, le=100, description="题目数量"),
    db: Session = Depends(get_db)
):
    """随机获取题目（用于练习模式）"""
    try:
        service = StudyService(db)
        items, _ = service.get_questions(subject, grade, limit=count * 2, offset=0)
        import random
        random.shuffle(items)
        items = items[:count]
        return {
            "success": True,
            "data": {
                "questions": [QuestionBankResponse.model_validate(q).model_dump() for q in items],
                "total": len(items)
            },
            "message": "获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
