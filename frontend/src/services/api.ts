import axios from 'axios'
import type { Outline, Page } from '../store'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export interface GenerateOutlineParams {
  topic: string
  reference_image?: string
  generator_type?: string  // 新增：生成器类型
  text_model_config?: any  // 新增：文本模型配置
}

export interface GenerateImagesParams {
  task_id: string
  pages: Page[]
  topic?: string
  reference_image?: string
  generator_type?: string
  image_model_config?: any  // 图片模型配置
  image_generation_config?: {  // 新增：图片生成配置
    quality: '1k' | '2k' | '4k'
    aspectRatio: string
  }
  full_outline?: string  // 新增：完整内容大纲
}

export interface ProgressData {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  total_pages: number
  completed_pages: number
  current_page: number
  message: string
  images: Array<{
    page_number: number
    url: string
    created_at: string
  }>
  failed_pages: Array<{
    page_number: number
    error: string
    failed_at: string
  }>
  timestamp: string
  done?: boolean
  error?: string
}

// 生成大纲
export const generateOutline = (params: GenerateOutlineParams) => {
  return api.post<any, { success: boolean; data: Outline }>('/generate-outline', params)
}

// 生成图片
export const generateImages = (params: GenerateImagesParams) => {
  return api.post<any, {
    success: boolean
    task_id: string
    total_pages: number
    message?: string
  }>('/generate-images', params)
}

// 订阅进度更新（SSE）
export const subscribeProgress = (
  taskId: string,
  onProgress: (data: ProgressData) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
): EventSource => {
  const eventSource = new EventSource(`${API_BASE_URL}/progress/${taskId}`)
  
  eventSource.onmessage = (event) => {
    try {
      const data: ProgressData = JSON.parse(event.data)
      
      // 检查是否有错误
      if (data.error) {
        console.error('Progress error:', data.error)
        if (onError) {
          onError(new Error(data.error))
        }
        eventSource.close()
        return
      }
      
      // 调用进度回调
      onProgress(data)
      
      // 如果任务完成，关闭连接
      if (data.done) {
        if (onComplete) {
          onComplete()
        }
        eventSource.close()
      }
    } catch (error) {
      console.error('Failed to parse SSE data:', error)
      if (onError) {
        onError(error as Error)
      }
    }
  }
  
  eventSource.onerror = (error) => {
    console.error('SSE connection error:', error)
    if (onError) {
      onError(new Error('SSE连接错误'))
    }
    eventSource.close()
  }
  
  return eventSource
}

// 获取进度（兼容旧API）
export const getProgress = (taskId: string, onProgress: (data: any) => void) => {
  return subscribeProgress(taskId, onProgress)
}

// 保存历史记录
export const saveHistory = (data: {
  task_id: string
  topic: string
  pages: any[]
  reference_image?: string
  generator_type?: string
  status?: string
}) => {
  return api.post<any, { success: boolean; history_id: string }>('/history', data)
}

// 获取历史记录列表
export const getHistory = (params?: { page?: number; page_size?: number; keyword?: string }) => {
  return api.get<any, { success: boolean; data: any }>('/history', { params })
}

// 获取特定历史记录
export const getHistoryItem = (historyId: string) => {
  return api.get<any, { success: boolean; data: any }>(`/history/${historyId}`)
}

// 删除历史记录
export const deleteHistory = (historyId: string) => {
  return api.delete<any, { success: boolean }>(`/history/${historyId}`)
}

// 上传参考图片
export const uploadReference = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  
  return api.post<any, { success: boolean; file_url: string }>('/upload-reference', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export default api