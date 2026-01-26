"""日程表业务逻辑服务"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.schedule import Schedule, Task
from app.schemas.schedule import ScheduleData, TaskCreate, TaskResponse


class ScheduleService:
    """日程表服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_schedule(self, student_name: str, student_class: str) -> Optional[Schedule]:
        """获取日程表（必传学生姓名和班级）"""
        # 根据学生姓名和班级精确匹配
        return self.db.query(Schedule).filter(
            Schedule.student_name == student_name,
            Schedule.student_class == student_class
        ).first()
    
    def create_or_update_schedule(self, data: ScheduleData) -> Schedule:
        """创建或更新日程表"""
        schedule = self.get_schedule(data.student_name, data.student_class)
        
        if schedule:
            # 更新现有日程表
            schedule.student_name = data.student_name
            schedule.student_class = data.student_class
            schedule.week_offset = data.week_offset
        else:
            # 创建新日程表
            schedule = Schedule(
                student_name=data.student_name,
                student_class=data.student_class,
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
                    
                db_task = Task(
                    schedule_id=schedule_id,
                    date_key=date_key,
                    task_name=task_name,
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
