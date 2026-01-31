/** 统计相关API */

import request from './index'

/**
 * 统计摘要数据接口
 */
export interface StatisticsSummary {
  total_users: number
  total_visits: number
  total_schedules: number
  total_quizzes: number
  total_achievements: number
  last_updated: string
}

/**
 * 统计响应接口
 */
export interface StatisticsResponse {
  success: boolean
  data?: StatisticsSummary
  message?: string
}

/**
 * 获取统计摘要
 */
export const getStatisticsSummary = async (): Promise<StatisticsResponse> => {
  return request.get('/api/statistics/summary')
}

/**
 * 记录页面访问
 */
export const recordVisit = async (): Promise<{ success: boolean; message: string }> => {
  return request.post('/api/statistics/record')
}
