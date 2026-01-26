/** 类型定义 */

// 日程表相关
export interface Task {
  id?: number
  task_name: string
  name?: string  // 兼容旧版
  stars: number
  order_index?: number
}

export interface DailyTasks {
  tasks: Task[]
}

export interface WeeklyTasks {
  [dateKey: string]: DailyTasks
}

export interface ScheduleData {
  student_name: string
  student_class?: string
  week_offset: number
  weekly_tasks: WeeklyTasks
}

// 阅读题相关
export interface QuizSection {
  title: string
  questions: QuizQuestion[]
}

export interface QuizQuestion {
  number: number
  text: string
  type: string
  options?: string[]
  answer?: string
  explanation?: string
  placeholder?: string
}

export interface QuizData {
  title: string
  subtitle?: string
  sections: QuizSection[]
}

// 成就相关
export interface Achievement {
  id: number
  code: string
  name: string
  description?: string
  icon?: string
  level?: 'bronze' | 'silver' | 'gold'
  is_hidden?: boolean  // 是否隐藏成就
  task_match_type?: string
  task_keywords?: string
  unlock_condition?: string
  created_at: string
  unlocked?: boolean
  unlocked_at?: string
  unlock_count?: number
}

export interface StudentRanking {
  schedule_id: number
  student_name: string
  student_class?: string
  total_achievements: number
  achievement_list: Achievement[]
}

export interface TimelineEvent {
  date: string
  event_type: 'task_completed' | 'achievement_unlocked'
  description: string
  icon?: string
}

export interface AchievementsSummary {
  total_achievements: number
  unlocked_achievements: number
  locked_achievements: number
  hidden_achievements: number  // 隐藏成就数量
  completion_rate: number
}

export interface StatisticsData {
  reading_days: number
  exercise_duration: number
  challenges_completed: number
  total_stars: number
  achievements_summary: AchievementsSummary
}

// API 响应
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
}
