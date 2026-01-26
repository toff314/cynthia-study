"""日程表业务逻辑服务"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.schedule import Schedule, Task
from app.schemas.schedule import ScheduleData, TaskCreate, TaskResponse


class ScheduleService:
    """日程表服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_schedule(self) -> Optional[Schedule]:
        """获取单个日程表（简化版本，只保留一条记录）"""
        return self.db.query(Schedule).order_by(Schedule.id.desc()).first()
    
    def create_or_update_schedule(self, data: ScheduleData) -> Schedule:
        """创建或更新日程表"""
        schedule = self.get_schedule()
        
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
    
    def get_all_tasks(self) -> Dict[str, List[TaskResponse]]:
        """获取当前日程表的所有任务，按日期分组"""
        schedule = self.get_schedule()
        if not schedule:
            return {}
        
        tasks = self.db.query(Task).filter(
            Task.schedule_id == schedule.id
        ).order_by(Task.date_key, Task.order_index).all()
        
        result = {}
        for task in tasks:
            if task.date_key not in result:
                result[task.date_key] = []
            result[task.date_key].append(TaskResponse.model_validate(task))
        return result
    
    def clear_all_data(self):
        """清空所有数据"""
        self.db.query(Task).delete()
        self.db.query(Schedule).delete()
        self.db.commit()
