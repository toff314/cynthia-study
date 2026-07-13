"""学习题库数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, func
from app.database import Base


class QuestionBank(Base):
    """题库表"""
    __tablename__ = "question_bank"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    subject = Column(String(20), nullable=False, comment="科目：math/chinese/english")
    grade = Column(Integer, nullable=False, comment="年级：1-6")
    question_type = Column(String(30), nullable=False, comment="题目类型：choice/fill_blank/true_false/short_answer")
    difficulty = Column(String(10), nullable=False, default="medium", comment="难度：easy/medium/hard")
    question_text = Column(Text, nullable=False, comment="题目内容")
    options = Column(JSON, nullable=True, comment="选项（选择题）")
    answer = Column(Text, nullable=False, comment="正确答案")
    explanation = Column(Text, nullable=True, comment="答案解析")
    source = Column(String(255), nullable=True, comment="来源URL")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")


class StudyRecord(Base):
    """答题记录表"""
    __tablename__ = "study_record"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    question_id = Column(Integer, ForeignKey("question_bank.id"), nullable=False, comment="题目ID")
    student_name = Column(String(50), nullable=True, comment="学生姓名")
    student_answer = Column(Text, nullable=True, comment="学生答案")
    is_correct = Column(Boolean, nullable=True, comment="是否正确")
    created_at = Column(DateTime, server_default=func.now(), comment="答题时间")
