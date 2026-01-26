import request from './index'
import type { ApiResponse, ScheduleData } from '@/types'

export const scheduleApi = {
  // 获取日程表数据
  getSchedule: (params?: { student_name?: string; student_class?: string }): Promise<ApiResponse<ScheduleData>> => {
    return request.get<ApiResponse<ScheduleData>>('/api/schedule', { params })
  },

  // 获取所有学生列表
  getAllStudents: (): Promise<ApiResponse<{ students: Array<{ id: number; student_name: string; student_class: string }> }>> => {
    return request.get<ApiResponse<{ students: Array<{ id: number; student_name: string; student_class: string }> }>>('/api/schedule/students')
  },

  // 保存日程表数据
  saveSchedule: (data: ScheduleData): Promise<ApiResponse> => {
    return request.post<ApiResponse>('/api/schedule', data)
  },

  // 清空日程表数据
  clearSchedule: (): Promise<ApiResponse> => {
    return request.delete<ApiResponse>('/api/schedule')
  }
}
