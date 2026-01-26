import axios from 'axios'
import type {
  Achievement,
  StudentRanking,
  TimelineEvent,
  StatisticsData,
  ApiResponse
} from '@/types'

const API_BASE = '/api/achievements'

export const achievementApi = {
  // 获取所有成就定义
  getAllAchievements: async (): Promise<ApiResponse<Achievement[]>> => {
    const response = await axios.get(`${API_BASE}`)
    return response.data
  },

  // 获取学生的所有成就
  getStudentAchievements: async (scheduleId: number): Promise<ApiResponse<Achievement[]>> => {
    const response = await axios.get(`${API_BASE}/student/${scheduleId}`)
    return response.data
  },

  // 获取所有学生的成就排名
  getAllStudentsRanking: async (): Promise<ApiResponse<StudentRanking[]>> => {
    const response = await axios.get(`${API_BASE}/ranking`)
    return response.data
  },

  // 获取学生的统计数据
  getStatistics: async (scheduleId: number): Promise<ApiResponse<StatisticsData>> => {
    const response = await axios.get(`${API_BASE}/statistics/${scheduleId}`)
    return response.data
  },

  // 获取学生的时间线事件
  getTimeline: async (scheduleId: number): Promise<ApiResponse<TimelineEvent[]>> => {
    const response = await axios.get(`${API_BASE}/timeline/${scheduleId}`)
    return response.data
  },

  // 检查并解锁成就
  checkAndUnlock: async (scheduleId: number): Promise<ApiResponse<any>> => {
    const response = await axios.post(`${API_BASE}/check-unlock/${scheduleId}`)
    return response.data
  },

  // 初始化默认成就
  initializeAchievements: async (): Promise<ApiResponse<void>> => {
    const response = await axios.post(`${API_BASE}/initialize`)
    return response.data
  }
}
