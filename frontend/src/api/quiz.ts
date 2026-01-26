import request from './index'
import type { ApiResponse, QuizData } from '@/types'

export interface FileInfo {
  name: string
  size: number
  modified: string
}

export const quizApi = {
  // 获取文件列表
  getFiles: () => {
    return request.get<ApiResponse<{ files: FileInfo[] }>>('/api/quiz/files')
  },

  // 获取文件内容
  getFile: (filename: string) => {
    return request.get<ApiResponse<{ content: string }>>('/api/quiz/file', {
      params: { name: filename }
    })
  },

  // 保存阅读题
  saveQuiz: (data: QuizData) => {
    return request.post<ApiResponse>('/api/quiz/save', data)
  },

  // 下载文件
  downloadFile: (filename: string) => {
    window.open(`/api/quiz/download?name=${encodeURIComponent(filename)}`, '_blank')
  }
}
