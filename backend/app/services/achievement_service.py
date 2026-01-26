"""成就业务逻辑服务"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.schedule import Schedule, Task
from app.models.achievement import Achievement, UserAchievement
from app.schemas.achievement import (
    AchievementResponse,
    AchievementDetail,
    StudentRanking,
    TimelineEvent,
    AchievementsSummary,
    StatisticsData
)


class AchievementService:
    """成就服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_achievements(self) -> List[AchievementResponse]:
        """获取所有成就定义"""
        achievements = self.db.query(Achievement).order_by(Achievement.id).all()
        return [AchievementResponse.model_validate(a) for a in achievements]
    
    def get_student_achievements(self, schedule_id: int) -> List[AchievementDetail]:
        """获取学生的所有成就（包含解锁状态）"""
        all_achievements = self.db.query(Achievement).order_by(Achievement.id).all()
        user_achievements = self.db.query(UserAchievement).filter(
            UserAchievement.schedule_id == schedule_id
        ).all()
        
        unlocked_ids = {ua.achievement_id for ua in user_achievements}
        result = []
        
        # 已解锁的成就排在前面
        unlocked_achievements = []
        locked_achievements = []
        
        for achievement in all_achievements:
            user_ach = next((ua for ua in user_achievements if ua.achievement_id == achievement.id), None)
            detail = AchievementDetail.model_validate(achievement)
            detail.unlocked = achievement.id in unlocked_ids
            if user_ach:
                detail.unlocked_at = user_ach.unlocked_at
                detail.unlock_count = user_ach.unlock_count
            
            if detail.unlocked:
                unlocked_achievements.append(detail)
            else:
                locked_achievements.append(detail)
        
        # 已解锁在前，未解锁在后
        result = unlocked_achievements + locked_achievements
        return result
    
    def get_all_students_ranking(self) -> List[StudentRanking]:
        """获取所有学生的成就排名"""
        # 获取所有日程表（即所有学生）
        schedules = self.db.query(Schedule).all()
        
        rankings = []
        for schedule in schedules:
            # 获取该学生解锁的成就数量
            user_achievements = self.db.query(UserAchievement).filter(
                UserAchievement.schedule_id == schedule.id
            ).all()
            
            # 获取成就详细信息
            achievement_list = []
            for ua in user_achievements:
                achievement = self.db.query(Achievement).get(ua.achievement_id)
                if achievement:
                    achievement_list.append(AchievementResponse.model_validate(achievement))
            
            ranking = StudentRanking(
                schedule_id=schedule.id,
                student_name=schedule.student_name,
                student_class=schedule.student_class,
                total_achievements=len(achievement_list),
                achievement_list=achievement_list
            )
            rankings.append(ranking)
        
        # 按成就数量降序排序，成就数量相同按姓名排序
        rankings.sort(key=lambda x: (-x.total_achievements, x.student_name))
        return rankings
    
    def get_statistics(self, schedule_id: int) -> StatisticsData:
        """获取学生的统计数据"""
        # 获取该学生的所有任务
        tasks = self.db.query(Task).filter(Task.schedule_id == schedule_id).all()
        
        # 统计数据
        reading_days = 0
        exercise_duration = 0
        challenges_completed = 0
        total_stars = sum(task.stars for task in tasks)
        
        # 根据任务名称统计
        for task in tasks:
            task_name = task.task_name.lower()
            
            if '阅读' in task_name or '读书' in task_name:
                if task.stars > 0:
                    reading_days += 1
            elif '运动' in task_name or '锻炼' in task_name or '体育' in task_name:
                if task.stars > 0:
                    exercise_duration += 30  # 假设每次运动30分钟
            elif '挑战' in task_name or '习题' in task_name:
                if task.stars > 0:
                    challenges_completed += 1
        
        # 获取成就统计
        all_achievements = self.db.query(Achievement).count()
        hidden_achievements = self.db.query(Achievement).filter(
            Achievement.is_hidden == True
        ).count()
        unlocked_achievements = self.db.query(UserAchievement).filter(
            UserAchievement.schedule_id == schedule_id
        ).count()
        locked_achievements = all_achievements - unlocked_achievements
        completion_rate = round((unlocked_achievements / all_achievements * 100) if all_achievements > 0 else 0, 2)
        
        achievements_summary = AchievementsSummary(
            total_achievements=all_achievements,
            unlocked_achievements=unlocked_achievements,
            locked_achievements=locked_achievements,
            hidden_achievements=hidden_achievements,
            completion_rate=completion_rate
        )
        
        return StatisticsData(
            reading_days=reading_days,
            exercise_duration=exercise_duration,
            challenges_completed=challenges_completed,
            total_stars=total_stars,
            achievements_summary=achievements_summary
        )
    
    def get_timeline(self, schedule_id: int) -> List[TimelineEvent]:
        """获取时间线事件"""
        # 获取任务完成记录
        tasks = self.db.query(Task).filter(
            Task.schedule_id == schedule_id,
            Task.stars > 0
        ).order_by(Task.date_key).all()
        
        # 获取成就解锁记录
        user_achievements = self.db.query(UserAchievement).join(Achievement).filter(
            UserAchievement.schedule_id == schedule_id
        ).order_by(UserAchievement.unlocked_at).all()
        
        events = []
        
        # 添加任务完成事件
        seen_dates = set()
        for task in tasks:
            if task.date_key not in seen_dates:
                events.append(TimelineEvent(
                    date=task.date_key,
                    event_type="task_completed",
                    description=f"完成当日任务，获得 {task.stars} 颗星",
                    icon="⭐"
                ))
                seen_dates.add(task.date_key)
        
        # 添加成就解锁事件
        for ua in user_achievements:
            achievement = ua.achievement
            if achievement:
                events.append(TimelineEvent(
                    date=ua.unlocked_at.strftime("%Y-%m-%d") if ua.unlocked_at else "",
                    event_type="achievement_unlocked",
                    description=f"解锁成就：{achievement.name}",
                    icon=achievement.icon or "🏆"
                ))
        
        # 按日期排序
        events.sort(key=lambda x: x.date)
        return events
    
    def check_and_unlock_achievements(self, schedule_id: int) -> List[Achievement]:
        """检查并解锁成就"""
        # 获取该学生的所有任务（不再限制 stars > 0，只要任务名称匹配即可）
        tasks = self.db.query(Task).filter(
            Task.schedule_id == schedule_id
        ).all()
        
        # 获取所有成就定义
        all_achievements = self.db.query(Achievement).all()
        
        # 获取已解锁的成就ID
        unlocked_ids = set(
            ua.achievement_id for ua in self.db.query(UserAchievement).filter(
                UserAchievement.schedule_id == schedule_id
            ).all()
        )
        
        newly_unlocked = []
        
        for achievement in all_achievements:
            if achievement.id in unlocked_ids:
                continue  # 已解锁，跳过
            
            # 检查是否满足解锁条件
            if self._check_achievement_unlock(achievement, tasks, schedule_id):
                # 解锁成就
                user_achievement = UserAchievement(
                    achievement_id=achievement.id,
                    schedule_id=schedule_id,
                    unlock_count=self._count_matching_tasks(achievement, tasks)
                )
                self.db.add(user_achievement)
                self.db.commit()
                self.db.refresh(user_achievement)
                newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def _check_achievement_unlock(self, achievement: Achievement, tasks: List[Task], schedule_id: int) -> bool:
        """检查单个成就是否解锁"""
        # 处理逻辑类型的成就
        if achievement.task_match_type == "logic":
            if achievement.code == "lucky_day":
                return self._check_lucky_day(tasks)
            elif achievement.code == "first_blood":
                return self._check_first_blood(tasks)
            elif achievement.code == "all_rounder":
                return self._check_all_rounder(schedule_id)
            return False
        
        count = self._count_matching_tasks(achievement, tasks)
        
        # 解析解锁条件，如 "完成10次"
        condition = achievement.unlock_condition or "完成 1 次"
        
        # 从条件中提取数字
        import re
        numbers = re.findall(r'\d+', str(condition))
        required_count = int(numbers[0]) if numbers else 1
        
        return count >= required_count
    
    def _count_matching_tasks(self, achievement: Achievement, tasks: List[Task]) -> int:
        """计算匹配要求的任务数量"""
        # logic 类型的成就返回1（表示解锁一次）
        if achievement.task_match_type == "logic":
            return 1
        
        if not achievement.task_keywords:
            return 0
        
        keywords = achievement.task_keywords.split(',')
        keywords = [k.strip().lower() for k in keywords]
        
        count = 0
        for task in tasks:
            task_name = task.task_name.lower()
            
            if achievement.task_match_type == "exact":
                if task_name in keywords:
                    count += 1
            elif achievement.task_match_type == "contains":
                if any(kw in task_name for kw in keywords):
                    count += 1
            elif achievement.task_match_type == "any":
                count += 1
            elif achievement.task_match_type == "prefix":
                if any(task_name.startswith(kw) for kw in keywords):
                    count += 1
        
        return count
    
    def _get_schedule_id_from_tasks(self, tasks: List[Task]) -> int:
        """从任务列表中获取日程表ID"""
        if not tasks:
            return 0
        return tasks[0].schedule_id
    
    def _check_lucky_day(self, tasks: List[Task]) -> bool:
        """检查幸运日：一天内完成所有日常任务"""
        if not tasks:
            return False
        
        # 按日期分组任务
        tasks_by_date = {}
        for task in tasks:
            if task.date_key not in tasks_by_date:
                tasks_by_date[task.date_key] = []
            tasks_by_date[task.date_key].append(task)
        
        # 检查是否有任何一天所有任务都完成了（stars > 0）
        for date_key, date_tasks in tasks_by_date.items():
            if all(task.stars > 0 for task in date_tasks):
                # 至少有3个任务才算一天的任务
                if len(date_tasks) >= 3:
                    return True
        
        return False
    
    def _check_first_blood(self, tasks: List[Task]) -> bool:
        """检查首胜达人：制作日程第一天就完成所有任务"""
        if not tasks:
            return False
        
        # 获取最早的日期
        sorted_dates = sorted(set(task.date_key for task in tasks))
        if not sorted_dates:
            return False
        
        first_day = sorted_dates[0]
        
        # 检查第一天的所有任务是否都完成了
        first_day_tasks = [task for task in tasks if task.date_key == first_day]
        if len(first_day_tasks) >= 3 and all(task.stars > 0 for task in first_day_tasks):
            return True
        
        return False
    
    def _check_all_rounder(self, schedule_id: int) -> bool:
        """检查全能小博士：在所有类别（阅读、运动、挑战、家务、亲子）都获得铜牌以上成就"""
        if schedule_id == 0:
            return False
        
        # 定义各类别的成就代码
        categories = {
            'reading': ['reading_bronze', 'reading_silver', 'reading_gold'],
            'exercise': ['exercise_bronze', 'exercise_silver', 'exercise_gold'],
            'challenge': ['challenge_bronze', 'challenge_silver', 'challenge_gold'],
            'housework': ['housework_bronze', 'housework_silver', 'housework_gold'],
            'family': ['family_teamwork', 'family_chef', 'storyteller']
        }
        
        # 获取用户已解锁的成就
        unlocked_achievements = self.db.query(UserAchievement).filter(
            UserAchievement.schedule_id == schedule_id
        ).all()
        
        unlocked_codes = {
            self.db.query(Achievement).get(ua.achievement_id).code 
            for ua in unlocked_achievements 
            if self.db.query(Achievement).get(ua.achievement_id)
        }
        
        # 检查每个类别是否至少有铜牌成就
        categories_unlocked = 0
        for category, codes in categories.items():
            if any(code in unlocked_codes for code in codes):
                categories_unlocked += 1
        
        return categories_unlocked >= 5
    
    def initialize_default_achievements(self):
        """初始化默认成就（如果没有成就数据）"""
        existing = self.db.query(Achievement).count()
        if existing > 0:
            return
        
        # 创建默认成就
        achievements = [
            # 阅读相关
            Achievement(
                code="reading_bronze",
                name="阅读小达人",
                description="完成3天阅读任务",
                icon="📚",
                level="bronze",
                task_match_type="contains",
                task_keywords="阅读,读书",
                unlock_condition="完成 3 次"
            ),
            Achievement(
                code="reading_silver",
                name="阅读小能手",
                description="完成10天阅读任务",
                icon="📖",
                level="silver",
                task_match_type="contains",
                task_keywords="阅读,读书",
                unlock_condition="完成 10 次"
            ),
            Achievement(
                code="reading_gold",
                name="阅读小博士",
                description="完成20天阅读任务",
                icon="📕",
                level="gold",
                task_match_type="contains",
                task_keywords="阅读,读书",
                unlock_condition="完成 20 次"
            ),
            # 运动相关
            Achievement(
                code="exercise_bronze",
                name="运动健儿",
                description="完成3天运动任务",
                icon="🏃",
                level="bronze",
                task_match_type="contains",
                task_keywords="运动,锻炼,体育",
                unlock_condition="完成 3 次"
            ),
            Achievement(
                code="exercise_silver",
                name="运动达人",
                description="完成10天运动任务",
                icon="⚽",
                level="silver",
                task_match_type="contains",
                task_keywords="运动,锻炼,体育",
                unlock_condition="完成 10 次"
            ),
            Achievement(
                code="exercise_gold",
                name="运动冠军",
                description="完成20天运动任务",
                icon="🏆",
                level="gold",
                task_match_type="contains",
                task_keywords="运动,锻炼,体育",
                unlock_condition="完成 20 次"
            ),
            # 挑战相关
            Achievement(
                code="challenge_bronze",
                name="挑战者",
                description="完成3次挑战任务",
                icon="🎯",
                level="bronze",
                task_match_type="contains",
                task_keywords="挑战,习题,作业,练习",
                unlock_condition="完成 3 次"
            ),
            Achievement(
                code="challenge_silver",
                name="挑战勇士",
                description="完成10次挑战任务",
                icon="⚔️",
                level="silver",
                task_match_type="contains",
                task_keywords="挑战,习题,作业,练习",
                unlock_condition="完成 10 次"
            ),
            Achievement(
                code="challenge_gold",
                name="挑战之王",
                description="完成20次挑战任务",
                icon="👑",
                level="gold",
                task_match_type="contains",
                task_keywords="挑战,习题,作业,练习",
                unlock_condition="完成 20 次"
            ),
            # 综合相关
            Achievement(
                code="streak_10",
                name="坚持10天",
                description="连续完成10天任务",
                icon="🔥",
                level="silver",
                task_match_type="contains",
                task_keywords="晨读,阅读,读书,运动,锻炼,体育,挑战,习题,作业,练习",
                unlock_condition="完成 10 次"
            ),
            Achievement(
                code="streak_20",
                name="坚持20天",
                description="连续完成20天任务",
                icon="💫",
                level="gold",
                task_match_type="contains",
                task_keywords="晨读,阅读,读书,运动,锻炼,体育,挑战,习题,作业,练习",
                unlock_condition="完成 20 次"
            ),
            Achievement(
                code="streak_30",
                name="寒假满勤",
                description="连续完成30天任务",
                icon="🌟",
                level="gold",
                task_match_type="contains",
                task_keywords="晨读,阅读,读书,运动,锻炼,体育,挑战,习题,作业,练习",
                unlock_condition="完成 30 次"
            ),
            # 家务相关
            Achievement(
                code="housework_bronze",
                name="家务小能手",
                description="完成3次家务任务",
                icon="🧹",
                level="bronze",
                task_match_type="contains",
                task_keywords="家务,劳动",
                unlock_condition="完成 3 次"
            ),
            Achievement(
                code="housework_silver",
                name="家务达人",
                description="完成10次家务任务",
                icon="🧼",
                level="silver",
                task_match_type="contains",
                task_keywords="家务,劳动",
                unlock_condition="完成 10 次"
            ),
            Achievement(
                code="housework_gold",
                name="家务小天使",
                description="完成20次家务任务",
                icon="✨",
                level="gold",
                task_match_type="contains",
                task_keywords="家务,劳动",
                unlock_condition="完成 20 次"
            ),
            # 星星相关
            Achievement(
                code="stars_50",
                name="星光璀璨",
                description="累计获得50颗星星",
                icon="⭐",
                level="silver",
                task_match_type="any",
                task_keywords="",
                unlock_condition="获得 50 颗星"
            ),
            Achievement(
                code="stars_100",
                name="星光闪耀",
                description="累计获得100颗星星",
                icon="💎",
                level="gold",
                task_match_type="any",
                task_keywords="",
                unlock_condition="获得 100 颗星"
            ),
            # 特殊成就
            Achievement(
                code="early_bird",
                name="早起鸟",
                description="完成晨读任务",
                icon="🌅",
                level="bronze",
                task_match_type="exact",
                task_keywords="晨读",
                unlock_condition="完成 1 次"
            ),
            Achievement(
                code="homework_master",
                name="作业达人",
                description="完成作业任务",
                icon="📝",
                level="bronze",
                task_match_type="exact",
                task_keywords="完成作业",
                unlock_condition="完成 1 次"
            ),
            # 亲子互动类
            Achievement(
                code="family_teamwork",
                name="最佳拍档",
                description="完成5次亲子合作任务",
                icon="👨‍👩‍👧‍👦",
                level="silver",
                task_match_type="contains",
                task_keywords="亲子,家庭,一起",
                unlock_condition="完成 5 次"
            ),
            Achievement(
                code="family_chef",
                name="小小厨神",
                description="与家人共同完成3次烹饪任务",
                icon="👨‍🍳",
                level="bronze",
                task_match_type="contains",
                task_keywords="做饭,烹饪,烘焙,包饺子",
                unlock_condition="完成 3 次"
            ),
            Achievement(
                code="storyteller",
                name="故事大王",
                description="给家人讲3个完整的故事",
                icon="📖",
                level="bronze",
                task_match_type="contains", 
                task_keywords="讲故事,睡前故事,家庭故事会",
                unlock_condition="完成 3 次"
            ),

            # 表演展示类
            Achievement(
                code="little_performer",
                name="才艺小明星",
                description="完成3次才艺展示",
                icon="🎭",
                level="silver",
                task_match_type="contains",
                task_keywords="表演,唱歌,跳舞,朗诵,才艺",
                unlock_condition="完成 3 次"
            ),
            Achievement(
                code="family_concert",
                name="家庭音乐会",
                description="组织或参与一次家庭音乐会",
                icon="🎵",
                level="gold",
                task_match_type="exact",
                task_keywords="家庭音乐会",
                unlock_condition="完成 1 次"
            ),
            Achievement(
                code="drama_king",
                name="小小戏剧家", 
                description="与家人合作表演一个小剧目",
                icon="🎬",
                level="silver",
                task_match_type="contains",
                task_keywords="角色扮演,小剧场,家庭剧",
                unlock_condition="完成 1 次"
            ),

            # 创造力特别成就
            Achievement(
                code="inventor",
                name="小小发明家",
                description="完成3项创意发明或手工作品",
                icon="🔧",
                level="silver",
                task_match_type="contains",
                task_keywords="发明,手工,创意制作,乐高设计",
                unlock_condition="完成 3 次"
            ),
            Achievement(
                code="art_exhibition",
                name="个人画展",
                description="收集10幅自己的绘画作品并展示",
                icon="🖼️",
                level="gold",
                task_match_type="any",
                task_keywords="画画,绘画,美术作品",
                unlock_condition="完成 10 次"
            ),
            Achievement(
                code="recycle_master",
                name="环保小卫士",
                description="用废旧物品制作3件手工作品",
                icon="♻️",
                level="bronze",
                task_match_type="contains",
                task_keywords="废旧利用,环保手工,变废为宝",
                unlock_condition="完成 3 次"
            ),

            # 趣味挑战类
            Achievement(
                code="no_screen_day",
                name="无屏挑战者",
                description="成功完成一天无电子屏幕挑战",
                icon="📵",
                level="silver",
                task_match_type="exact",
                task_keywords="无屏幕日",
                unlock_condition="完成 1 次"
            ),
            Achievement(
                code="bookworm",
                name="小书虫",
                description="连续7天每天阅读超过30分钟",
                icon="🐛",
                level="gold",
                task_match_type="contains",
                task_keywords="阅读,读书",
                unlock_condition="连续 7 天"
            ),
            Achievement(
                code="weather_reporter",
                name="小小气象员",
                description="连续5天记录天气并做简单预报",
                icon="🌤️",
                level="bronze",
                task_match_type="contains",
                task_keywords="天气记录,气象观察",
                unlock_condition="完成 5 次"
            ),

            # 社交分享类
            Achievement(
                code="kindness_angel",
                name="爱心小天使",
                description="完成3次帮助他人的任务",
                icon="😇",
                level="silver",
                task_match_type="contains",
                task_keywords="帮助,分享,关心,爱心",
                unlock_condition="完成 3 次"
            ),
            Achievement(
                code="phone_call_expert",
                name="电话小达人",
                description="主动给爷爷奶奶/外公外婆打电话3次",
                icon="📞",
                level="bronze",
                task_match_type="contains",
                task_keywords="打电话,问候长辈",
                unlock_condition="完成 3 次"
            ),

            # 惊喜隐藏成就
            Achievement(
                code="midnight_rider",
                name="午夜骑士",
                description="在除夕夜守岁到午夜",
                icon="🌙",
                level="gold",
                task_match_type="exact",
                task_keywords="除夕守岁",
                unlock_condition="完成 1 次",
                is_hidden=True  # 隐藏成就，达成时惊喜解锁
            ),
            Achievement(
                code="lucky_day",
                name="幸运日",
                description="一天内完成所有日常任务",
                icon="🍀",
                level="silver",
                task_match_type="logic",
                task_keywords="",  # 通过程序逻辑判断
                unlock_condition="一天完成所有任务",
                is_hidden=True
            ),
            Achievement(
                code="first_blood",
                name="首胜达人",
                description="制作任务第一天就完成所有任务",
                icon="🥇",
                level="gold",
                task_match_type="logic",
                task_keywords="",
                unlock_condition="制作任务第一天完成任务",
                is_hidden=True
            ),

            # 综合全能成就
            Achievement(
                code="all_rounder",
                name="全能小博士",
                description="在所有类别（阅读、运动、挑战、家务、亲子）都获得铜牌以上成就",
                icon="🏅",
                level="gold",
                task_match_type="logic",
                task_keywords="",
                unlock_condition="获得5类成就",
                is_hidden=True
            )
        ]
        
        for achievement in achievements:
            self.db.add(achievement)
        
        self.db.commit()
        print(f"✅ 已初始化 {len(achievements)} 个成就")
