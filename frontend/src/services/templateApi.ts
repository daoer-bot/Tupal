import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('Template API Error:', error)
    return Promise.reject(error)
  }
)

/**
 * 模板数据结构
 */
export interface Template {
  id: string
  name: string
  description: string
  preview_image?: string
  type: 'system' | 'user'  // 系统模板或用户模板
  category?: string
  style?: string
  content_structure?: {
    pages?: number
    layout?: string
    [key: string]: any
  }
  structure?: {
    pages?: Array<{
      title: string
      description: string
      xiaohongshu_content?: string
    }>
    [key: string]: any
  }
  tags?: string[]
  usage_count?: number
  created_at: string
  updated_at?: string
}

/**
 * 模板列表响应
 */
export interface TemplateListResponse {
  success: boolean
  data: {
    items: Template[]
    total: number
    page: number
    page_size: number
  }
}

/**
 * 单个模板响应
 */
export interface TemplateResponse {
  success: boolean
  data: Template
}

/**
 * 获取模板列表参数
 */
export interface GetTemplatesParams {
  type?: 'system' | 'user' | 'all'
  category?: string
  page?: number
  page_size?: number
  keyword?: string
  tags?: string[]
}

/**
 * 使用模板的响应
 */
export interface UseTemplateResponse {
  success: boolean
  data: {
    task_id: string
    topic: string
    template_id: string
    template_name: string
    pages: Array<{
      page_number: number
      title: string
      description: string
      xiaohongshu_content?: string
    }>
  }
}

/**
 * 获取模板列表
 * @param params 查询参数
 */
export const getTemplates = (params?: GetTemplatesParams): Promise<TemplateListResponse> => {
  return api.get('/templates', { params })
}

/**
 * 获取系统模板（官方模板）
 */
export const getOfficialTemplates = (params?: Omit<GetTemplatesParams, 'type'>): Promise<TemplateListResponse> => {
  return api.get('/templates', { params: { ...params, type: 'system' } })
}

/**
 * 获取用户模板（个人模板/收藏模板）
 */
export const getPersonalTemplates = (params?: Omit<GetTemplatesParams, 'type'>): Promise<TemplateListResponse> => {
  return api.get('/templates', { params: { ...params, type: 'user' } })
}

/**
 * 获取单个模板详情
 * @param templateId 模板ID
 */
export const getTemplate = (templateId: string): Promise<TemplateResponse> => {
  return api.get(`/templates/${templateId}`)
}

/**
 * 使用模板创建大纲
 * @param templateId 模板ID
 * @param topic 创作主题
 */
export const useTemplate = (templateId: string, topic: string): Promise<UseTemplateResponse> => {
  return api.post(`/templates/${templateId}/use`, { topic })
}

/**
 * 使用模板（参数填充方式）
 * @param templateId 模板ID
 * @param parameters 参数字典
 */
export const useTemplateWithParams = (templateId: string, parameters: Record<string, any>): Promise<{
  success: boolean
  data: {
    template_id: string
    template_name: string
    filled_structure: any
    parameters_used: Record<string, any>
  }
}> => {
  return api.post(`/templates/${templateId}/use`, { parameters })
}

/**
 * 创建模板
 * @param templateData 模板数据
 */
export const createTemplate = (templateData: {
  name: string
  category: string
  structure: any
  parameters?: Array<{
    name: string
    label: string
    type: string
    required?: boolean
    default?: any
    placeholder?: string
  }>
  type?: 'system' | 'user'
  description?: string
  tags?: string[]
  preview?: string
  thumbnail?: string
}): Promise<{
  success: boolean
  data: { template_id: string }
}> => {
  return api.post('/templates', templateData)
}

/**
 * 更新模板
 * @param templateId 模板ID
 * @param templateData 更新数据
 */
export const updateTemplate = (templateId: string, templateData: Partial<{
  name: string
  structure: any
  parameters: any[]
  description: string
  tags: string[]
  preview: string
  thumbnail: string
}>): Promise<{
  success: boolean
  message: string
}> => {
  return api.put(`/templates/${templateId}`, templateData)
}

/**
 * 删除模板
 * @param templateId 模板ID
 */
export const deleteTemplate = (templateId: string): Promise<{
  success: boolean
  message: string
}> => {
  return api.delete(`/templates/${templateId}`)
}

/**
 * 将案例设为模板
 * @param materialId 素材/案例ID
 * @param templateName 模板名称
 */
export const markAsTemplate = (materialId: string, templateName: string): Promise<{
  success: boolean
  message: string
}> => {
  return api.patch(`/materials/${materialId}`, {
    is_template: true,
    template_name: templateName
  })
}

/**
 * 取消模板标记
 * @param materialId 素材/案例ID
 */
export const unmarkAsTemplate = (materialId: string): Promise<{
  success: boolean
  message: string
}> => {
  return api.patch(`/materials/${materialId}`, {
    is_template: false,
    template_name: null
  })
}

/**
 * 获取热门模板
 * @param limit 数量限制
 */
export const getPopularTemplates = (limit: number = 10): Promise<{
  success: boolean
  data: Template[]
}> => {
  return api.get('/templates/popular', { params: { limit } })
}

/**
 * 获取模板分类列表
 */
export const getCategories = (): Promise<{
  success: boolean
  data: string[]
}> => {
  return api.get('/templates/categories')
}

/**
 * 获取模板标签列表
 */
export const getTags = (): Promise<{
  success: boolean
  data: string[]
}> => {
  return api.get('/templates/tags')
}

export default {
  getTemplates,
  getOfficialTemplates,
  getPersonalTemplates,
  getTemplate,
  useTemplate,
  useTemplateWithParams,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  markAsTemplate,
  unmarkAsTemplate,
  getPopularTemplates,
  getCategories,
  getTags
}