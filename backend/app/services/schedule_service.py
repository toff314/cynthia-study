"""日程表业务逻辑服务"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.schedule import Schedule, Task
from app.schemas.schedule import ScheduleData, TaskCreate, TaskResponse
from app.utils.file_helper import validate_text_input, sanitize_text


class ScheduleService:
    """日程表服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_schedule(self, student_name: str, student_class: str) -> Optional[Schedule]:
        """获取日程表（必传学生姓名和班级）"""
        # 验证学生姓名
        is_valid, error_msg = validate_text_input(student_name, "学生姓名", max_length=50)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 验证班级
        is_valid, error_msg = validate_text_input(student_class, "班级", max_length=50)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 根据学生姓名和班级精确匹配
        return self.db.query(Schedule).filter(
            Schedule.student_name == sanitize_text(student_name),
            Schedule.student_class == sanitize_text(student_class)
        ).first()
    
    def create_or_update_schedule(self, data: ScheduleData) -> Schedule:
        """创建或更新日程表"""
        # 验证学生姓名
        is_valid, error_msg = validate_text_input(data.student_name, "学生姓名", max_length=50)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 验证班级
        is_valid, error_msg = validate_text_input(data.student_class, "班级", max_length=50)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 清理输入
        clean_name = sanitize_text(data.student_name)
        clean_class = sanitize_text(data.student_class)
        
        schedule = self.get_schedule(clean_name, clean_class)
        
        if schedule:
            # 更新现有日程表
            schedule.student_name = clean_name
            schedule.student_class = clean_class
            schedule.week_offset = data.week_offset
        else:
            # 创建新日程表
            schedule = Schedule(
                student_name=clean_name,
                student_class=clean_class,
                week_offset=data.week_offset
            )
            self.db.add(schedule)
        
        self.db.commit()
        self.db.refresh(schedule)
        
        # 更新任务数据
        self._update_tasks(schedule.id, data.weekly_tasks)
        
        return schedule
    
    def _update_tasks(self, schedule_id: int, weekly_tasks: Dict[str, Any]):
        """更新任务数据"""
        # 只清除当前日程表的任务
        self.db.query(Task).filter(Task.schedule_id == schedule_id).delete()
        
        # 插入新任务
        for date_key, day_data in weekly_tasks.items():
            tasks = day_data.get("tasks", [])
            for idx, task in enumerate(tasks):
                # 跳过null值
                if task is None:
                    continue
                    
                # 确保task是字典类型
                if not isinstance(task, dict):
                    continue
                    
                # 获取任务信息
                task_name = task.get("task_name", task.get("name", ""))
                stars = task.get("stars", 0)
                
                # 跳过空任务
                if not task_name or task_name.strip() == "":
                    continue
                
                # 验证任务名（防止XSS和注入）
                is_valid, error_msg = validate_text_input(task_name, "任务名", max_length=200)
                if not is_valid:
                    raise ValueError(error_msg)
                
                # 清理任务名
                clean_task_name = sanitize_text(task_name)
                    
                db_task = Task(
                    schedule_id=schedule_id,
                    date_key=date_key,
                    task_name=clean_task_name,
                    stars=stars,
                    order_index=idx
                )
                self.db.add(db_task)
        
        self.db.commit()
    
    def get_tasks_by_date(self, date_key: str) -> List[TaskResponse]:
        """根据日期获取任务列表"""
        tasks = self.db.query(Task).filter(Task.date_key == date_key).order_by(Task.order_index).all()
        return [TaskResponse.model_validate(t) for t in tasks]
    
    def get_all_tasks(self, student_name: str, student_class: str) -> Optional[Dict[str, List[TaskResponse]]]:
        """获取日程表的所有任务，按日期分组（必传学生姓名和班级）"""
        # 验证参数（get_schedule方法中已经有验证）
        schedule = self.get_schedule(student_name, student_class)
        if not schedule:
            return None
        
        tasks = self.db.query(Task).filter(
            Task.schedule_id == schedule.id
        ).order_by(Task.date_key, Task.order_index).all()
        
        result = {}
        for task in tasks:
            if task.date_key not in result:
                result[task.date_key] = []
            result[task.date_key].append(TaskResponse.model_validate(task))
        return result
    
    def get_all_students(self) -> List[Schedule]:
        """获取所有学生的日程表信息"""
        return self.db.query(Schedule).order_by(Schedule.student_name).all()
    
    def clear_all_data(self):
        """清空所有数据"""
        self.db.query(Task).delete()
        self.db.query(Schedule).delete()
        self.db.commit()
