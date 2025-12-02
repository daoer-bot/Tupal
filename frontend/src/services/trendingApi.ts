/**
 * 热榜数据 API 服务
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5030/api'

export interface TrendingItem {
  id: string
  title: string
  url: string
  mobile_url?: string
  hot_value?: string
  index?: number
  extra?: {
    desc?: string
    pic?: string
    label?: string
    [key: string]: any
  }
}

export interface TrendingSource {
  id: string
  name: string
  icon: string
  interval: number
}

export interface TrendingResponse {
  success: boolean
  source_id: string
  data: TrendingItem[]
  from_cache?: boolean
  update_time?: string
  error?: string
}

/**
 * 获取所有可用的热榜数据源
 */
export async function getTrendingSources(): Promise<TrendingSource[]> {
  const response = await fetch(`${API_BASE_URL}/trending/sources`)
  const result = await response.json()
  
  if (!result.success) {
    throw new Error(result.error || '获取数据源列表失败')
  }
  
  return result.data
}

/**
 * 获取指定数据源的热榜数据
 */
export async function getTrendingBySource(
  sourceId: string,
  forceRefresh: boolean = false
): Promise<TrendingResponse> {
  const url = `${API_BASE_URL}/trending/${sourceId}${forceRefresh ? '?force_refresh=true' : ''}`
  const response = await fetch(url)
  const result = await response.json()
  
  if (!result.success) {
    throw new Error(result.error || '获取热榜数据失败')
  }
  
  return result
}

/**
 * 获取所有数据源的热榜数据
 */
export async function getAllTrending(
  forceRefresh: boolean = false
): Promise<Record<string, TrendingResponse>> {
  const url = `${API_BASE_URL}/trending${forceRefresh ? '?force_refresh=true' : ''}`
  const response = await fetch(url)
  const result = await response.json()
  
  if (!result.success) {
    throw new Error(result.error || '获取热榜数据失败')
  }
  
  return result.data
}

export default {
  getTrendingSources,
  getTrendingBySource,
  getAllTrending
}