import request from './index'

export interface ReadingItem {
  name: string
  path: string
  is_dir: boolean
  size?: number
}

export interface ReadingReadResult {
  task_id: string
  pages: number
  image_urls: string[]
}

export function listReadingDirectory(path?: string) {
  return request.get('/api/reading/list', { params: { path } })
}

export function readBook(path: string) {
  return request.post('/api/reading/read', { path }, { timeout: 300000 })
}

export function cleanupReadingCache() {
  return request.post('/api/reading/cleanup')
}
