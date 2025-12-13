/**
 * 素材管理API服务
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5030/api'

export interface Material {
  id: string
  name: string
  type: 'text' | 'image' | 'mixed' | 'reference'
  content: any
  tags: string[]
  description: string
  created_at: string
  updated_at: string
}

export interface MaterialListResponse {
  success: boolean
  data: {
    items: Material[]
    pagination: {
      page: number
      page_size: number
      total: number
      total_pages: number
      has_more: boolean
    }
  }
}

export interface MaterialResponse {
  success: boolean
  data?: Material
  error?: string
}

export interface CreateMaterialRequest {
  name: string
  type: 'text' | 'image' | 'mixed' | 'reference'
  category?: string
  content: any
  tags?: string[]
  description?: string
}

export interface UpdateMaterialRequest {
  name?: string
  content?: any
  tags?: string[]
  description?: string
}

export interface ProcessReferencesRequest {
  material_ids: string[]
  base_prompt: string
}

export interface ProcessReferencesResponse {
  success: boolean
  data?: {
    enhanced_prompt: string
    reference_images: string[]
    style_params: any
    materials_used: Material[]
  }
  error?: string
}

/**
 * 素材API类
 */
class MaterialApi {
  /**
   * 创建素材
   */
  async createMaterial(data: CreateMaterialRequest): Promise<{ success: boolean; material_id?: string; error?: string }> {
    try {
      const response = await axios.post(`${API_BASE_URL}/materials`, data)
      return response.data
    } catch (error: any) {
      console.error('创建素材失败:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || '创建素材失败'
      }
    }
  }

  /**
   * 获取素材列表
   */
  async getMaterials(params?: {
    type?: string
    tags?: string
    page?: number
    page_size?: number
    keyword?: string
  }): Promise<MaterialListResponse> {
    try {
      const response = await axios.get(`${API_BASE_URL}/materials`, { params })
      return response.data
    } catch (error: any) {
      console.error('获取素材列表失败:', error)
      return {
        success: false,
        data: {
          items: [],
          pagination: {
            page: 1,
            page_size: 20,
            total: 0,
            total_pages: 0,
            has_more: false
          }
        }
      }
    }
  }

  /**
   * 获取单个素材
   */
  async getMaterial(materialId: string): Promise<MaterialResponse> {
    try {
      const response = await axios.get(`${API_BASE_URL}/materials/${materialId}`)
      return response.data
    } catch (error: any) {
      console.error('获取素材详情失败:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || '获取素材详情失败'
      }
    }
  }

  /**
   * 更新素材
   */
  async updateMaterial(materialId: string, data: UpdateMaterialRequest): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await axios.put(`${API_BASE_URL}/materials/${materialId}`, data)
      return response.data
    } catch (error: any) {
      console.error('更新素材失败:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || '更新素材失败'
      }
    }
  }

  /**
   * 删除素材
   */
  async deleteMaterial(materialId: string): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await axios.delete(`${API_BASE_URL}/materials/${materialId}`)
      return response.data
    } catch (error: any) {
      console.error('删除素材失败:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || '删除素材失败'
      }
    }
  }

  /**
   * 批量获取素材
   */
  async getMaterialsBatch(materialIds: string[]): Promise<{ success: boolean; data?: Material[]; error?: string }> {
    try {
      const response = await axios.post(`${API_BASE_URL}/materials/batch`, {
        material_ids: materialIds
      })
      return response.data
    } catch (error: any) {
      console.error('批量获取素材失败:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || '批量获取素材失败'
      }
    }
  }

  /**
   * 获取所有分类
   */

  /**
   * 获取所有标签
   */
  async getTags(): Promise<{ success: boolean; data?: string[]; error?: string }> {
    try {
      const response = await axios.get(`${API_BASE_URL}/materials/tags`)
      return response.data
    } catch (error: any) {
      console.error('获取标签列表失败:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || '获取标签列表失败'
      }
    }
  }

  /**
   * 处理素材引用
   */
  async processReferences(data: ProcessReferencesRequest): Promise<ProcessReferencesResponse> {
    try {
      const response = await axios.post(`${API_BASE_URL}/materials/process-references`, data)
      return response.data
    } catch (error: any) {
      console.error('处理素材引用失败:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || '处理素材引用失败'
      }
    }
  }

  /**
   * 从文本中提取素材引用ID
   * 格式: @[素材名](material_id)
   */
  extractMaterialIds(text: string): string[] {
    const pattern = /@\[([^\]]+)\]\(([^)]+)\)/g
    const matches = Array.from(text.matchAll(pattern))
    return matches.map(match => match[2])
  }

  /**
   * 批量处理多个提示词的素材引用
   */
  async processBatchPrompts(prompts: string[]): Promise<{
    success: boolean
    enhanced_prompts?: string[]
    reference_images?: string[]
    style_params?: any
    error?: string
  }> {
    try {
      // 从所有提示词中提取素材ID
      const allMaterialIds = new Set<string>()
      prompts.forEach(prompt => {
        const ids = this.extractMaterialIds(prompt)
        ids.forEach(id => allMaterialIds.add(id))
      })

      if (allMaterialIds.size === 0) {
        // 没有素材引用，直接返回原始提示词
        return {
          success: true,
          enhanced_prompts: prompts,
          reference_images: [],
          style_params: {}
        }
      }

      // 处理所有引用的素材
      const response = await this.processReferences({
        material_ids: Array.from(allMaterialIds),
        base_prompt: ''
      })

      if (!response.success || !response.data) {
        return {
          success: false,
          error: response.error || '处理素材引用失败'
        }
      }

      // 获取素材映射
      const materialMap = new Map<string, any>()
      response.data.materials_used.forEach(mat => {
        materialMap.set(mat.id, mat)
      })

      // 为每个提示词替换素材引用
      const enhanced_prompts = prompts.map(prompt => {
        let enhanced = prompt
        
        // 提取当前提示词中的素材ID
        const pattern = /@\[([^\]]+)\]\(([^)]+)\)/g
        const matches = Array.from(prompt.matchAll(pattern))
        
        matches.forEach(match => {
          const [fullMatch, materialName, materialId] = match
          const material = materialMap.get(materialId)
          
          if (material) {
            let replacement = ''
            
            // 根据素材类型生成替换内容
            if (material.type === 'text') {
              replacement = material.content.text || ''
            } else if (material.type === 'image') {
              replacement = material.content.description || `[图片素材：${materialName}]`
            } else if (material.type === 'reference') {
              replacement = material.content.content || ''
              if (material.content.reference_type) {
                replacement = `[参考：${material.content.reference_type}]`
              }
            }
            
            // 替换引用标记
            enhanced = enhanced.replace(fullMatch, replacement)
          }
        })
        
        return enhanced
      })

      return {
        success: true,
        enhanced_prompts,
        reference_images: response.data.reference_images || [],
        style_params: response.data.style_params || {}
      }

    } catch (error: any) {
      console.error('批量处理素材引用失败:', error)
      return {
        success: false,
        error: error.message || '批量处理素材引用失败'
      }
    }
  }
}

export default new MaterialApi()