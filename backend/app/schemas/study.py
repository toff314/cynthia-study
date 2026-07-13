"""学习题库相关的Pydantic模型"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Union
from datetime import datetime
import json


class QuestionBankBase(BaseModel):
    subject: str = Field(..., description="科目：math/chinese/english")
    grade: int = Field(..., ge=1, le=6, description="年级：1-6")
    question_type: str = Field(..., description="题目类型：choice/fill_blank/true_false/short_answer")
    difficulty: str = Field(default="medium", description="难度：easy/medium/hard")
    question_text: str = Field(..., description="题目内容")
    options: Optional[Union[List[Any], str]] = Field(None, description="选项（选择题）")
    answer: str = Field(..., description="正确答案")
    explanation: Optional[str] = Field(None, description="答案解析")
    source: Optional[str] = Field(None, description="来源URL")

    @field_validator('options', mode='before')
    @classmethod
    def parse_options(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return None


class QuestionBankCreate(QuestionBankBase):
    pass


class QuestionBankResponse(QuestionBankBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionBankBatchCreate(BaseModel):
    questions: List[QuestionBankCreate] = Field(..., description="批量导入的题目列表")


class QuestionBankBatchResponse(BaseModel):
    success: bool
    total: int
    created: int
    skipped: int
    message: str


class StudyRecordBase(BaseModel):
    question_id: int = Field(..., description="题目ID")
    student_name: Optional[str] = Field(None, description="学生姓名")
    student_answer: Optional[str] = Field(None, description="学生答案")
    is_correct: Optional[bool] = Field(None, description="是否正确")


class StudyRecordCreate(StudyRecordBase):
    pass


class StudyRecordResponse(StudyRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StudyStatsResponse(BaseModel):
    total_questions: int
    total_records: int
    correct_count: int
    accuracy: float
    by_subject: dict[str, Any]
    by_grade: dict[str, Any]


class QuestionQueryParams(BaseModel):
    subject: Optional[str] = Field(None, description="科目筛选")
    grade: Optional[int] = Field(None, ge=1, le=6, description="年级筛选")
    question_type: Optional[str] = Field(None, description="题目类型筛选")
    difficulty: Optional[str] = Field(None, description="难度筛选")
    limit: int = Field(default=50, ge=1, le=200, description="返回数量")
    offset: int = Field(default=0, ge=0, description="偏移量")
