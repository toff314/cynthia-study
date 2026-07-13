"""学习题库业务逻辑服务"""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func as sql_func
from app.models.study import QuestionBank, StudyRecord
from app.schemas.study import QuestionBankCreate, StudyRecordCreate


class StudyService:
    def __init__(self, db: Session):
        self.db = db

    # ---- QuestionBank CRUD ----

    def get_questions(self, subject: Optional[str] = None, grade: Optional[int] = None,
                      question_type: Optional[str] = None, difficulty: Optional[str] = None,
                      limit: int = 50, offset: int = 0) -> tuple[List[QuestionBank], int]:
        query = self.db.query(QuestionBank)
        total = query.count()
        if subject:
            query = query.filter(QuestionBank.subject == subject)
        if grade:
            query = query.filter(QuestionBank.grade == grade)
        if question_type:
            query = query.filter(QuestionBank.question_type == question_type)
        if difficulty:
            query = query.filter(QuestionBank.difficulty == difficulty)
        items = query.order_by(QuestionBank.created_at.desc()).limit(limit).offset(offset).all()
        return items, total

    def get_question(self, question_id: int) -> Optional[QuestionBank]:
        return self.db.query(QuestionBank).filter(QuestionBank.id == question_id).first()

    def create_question(self, data: QuestionBankCreate) -> QuestionBank:
        question = QuestionBank(**data.model_dump())
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def batch_create_questions(self, questions_data: list) -> dict:
        created = 0
        skipped = 0
        for q_data in questions_data:
            try:
                if isinstance(q_data, dict):
                    q = QuestionBank(**q_data)
                else:
                    q = QuestionBank(**q_data.model_dump())
                self.db.add(q)
                created += 1
            except Exception:
                skipped += 1
        if created > 0:
            self.db.commit()
        return {"created": created, "skipped": skipped}

    def delete_question(self, question_id: int) -> bool:
        question = self.get_question(question_id)
        if not question:
            return False
        self.db.delete(question)
        self.db.commit()
        return True

    def count_by_subject(self) -> dict:
        results = self.db.query(QuestionBank.subject, sql_func.count(QuestionBank.id)) \
            .group_by(QuestionBank.subject).all()
        return {row[0]: row[1] for row in results}

    def count_by_grade(self) -> dict:
        results = self.db.query(QuestionBank.grade, sql_func.count(QuestionBank.id)) \
            .group_by(QuestionBank.grade).all()
        return {str(row[0]): row[1] for row in results}

    # ---- StudyRecord ----

    def create_record(self, data: StudyRecordCreate) -> StudyRecord:
        record = StudyRecord(**data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_records(self, student_name: Optional[str] = None, limit: int = 100) -> List[StudyRecord]:
        query = self.db.query(StudyRecord).order_by(StudyRecord.created_at.desc())
        if student_name:
            query = query.filter(StudyRecord.student_name == student_name)
        return query.limit(limit).all()

    def get_stats(self) -> dict:
        total_questions = self.db.query(sql_func.count(QuestionBank.id)).scalar() or 0
        total_records = self.db.query(sql_func.count(StudyRecord.id)).scalar() or 0
        correct_count = self.db.query(sql_func.count(StudyRecord.id)) \
            .filter(StudyRecord.is_correct == True).scalar() or 0
        accuracy = (correct_count / total_records * 100) if total_records > 0 else 0
        by_subject = self.count_by_subject()
        by_grade = self.count_by_grade()
        return {
            "total_questions": total_questions,
            "total_records": total_records,
            "correct_count": correct_count,
            "accuracy": round(accuracy, 1),
            "by_subject": by_subject,
            "by_grade": by_grade
        }
