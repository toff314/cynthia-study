import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import type { ApiResponse } from '@/types'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000
}) as any

// 请求拦截器
request.interceptors.request.use(
  (config: any) => config,
  (error: any) => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => response.data as any,
  (error: any) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default request
