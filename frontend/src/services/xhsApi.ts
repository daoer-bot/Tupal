/**
 * 小红书 API 封装
 * 提供与后端小红书服务交互的接口
 */

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:5030/api').replace(/\/$/, '')
const API_BASE = `${API_BASE_URL}/xiaohongshu`

// ==================== 类型定义 ====================

export interface XhsClientConfig {
  cookie: string
  user_agent?: string
  timeout?: number
  proxies?: string
}

export interface XhsClientInfo {
  client_id: string
  created_at: string
  expires_at: string
}

export interface XhsNote {
  note_id: string
  title: string
  desc: string
  type: string
  user: {
    user_id: string
    nickname: string
    avatar: string
  }
  image_list: Array<{
    url: string
    width: number
    height: number
  }>
  video_url?: string
  tag_list: string[]
  at_user_list: string[]
  liked_count: number
  collected_count: number
  comment_count: number
  share_count: number
  time: number
  last_update_time: number
}

export interface XhsUser {
  user_id: string
  nickname: string
  avatar: string
  desc: string
  gender: number
  ip_location: string
  follows: number
  fans: number
  interaction: number
  tags: string[]
}

export interface XhsComment {
  id: string
  content: string
  user: {
    user_id: string
    nickname: string
    avatar: string
  }
  like_count: number
  sub_comment_count: number
  create_time: number
}

export interface XhsSearchResult {
  items: XhsNote[]
  has_more: boolean
  cursor?: string
}

export interface XhsUserSearchResult {
  items: XhsUser[]
  has_more: boolean
  cursor?: string
}

export interface XhsFeedResult {
  items: XhsNote[]
  cursor?: string
}

export type FeedType = 'recommend' | 'homefeed_recommend' | 'homefeed.fashion_v3' | 'homefeed.food_v3' | 'homefeed.cosmetics_v3' | 'homefeed.movie_and_tv_v3' | 'homefeed.career_v3' | 'homefeed.love_v3' | 'homefeed.household_product_v3' | 'homefeed.gaming_v3' | 'homefeed.travel_v3' | 'homefeed.fitness_v3'

export type SearchSortType = 'general' | 'popularity_descending' | 'time_descending'

export type SearchNoteType = 'all' | 'video' | 'image'

// ==================== API 响应类型 ====================

interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

// ==================== 辅助函数 ====================

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })
    
    const data = await response.json()
    return data
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : '网络请求失败',
    }
  }
}

// ==================== 客户端管理 ====================

/**
 * 创建小红书客户端
 */
export async function createClient(config: XhsClientConfig): Promise<ApiResponse<XhsClientInfo>> {
  return request<XhsClientInfo>('/client', {
    method: 'POST',
    body: JSON.stringify(config),
  })
}

/**
 * 获取客户端信息
 */
export async function getClient(clientId: string): Promise<ApiResponse<XhsClientInfo>> {
  return request<XhsClientInfo>(`/client/${clientId}`)
}

/**
 * 删除客户端
 */
export async function deleteClient(clientId: string): Promise<ApiResponse<{ message: string }>> {
  return request<{ message: string }>(`/client/${clientId}`, {
    method: 'DELETE',
  })
}

// ==================== 笔记相关 ====================

/**
 * 获取笔记详情
 */
export async function getNoteById(
  clientId: string,
  noteId: string,
  xsecToken?: string
): Promise<ApiResponse<XhsNote>> {
  const params = new URLSearchParams({ client_id: clientId })
  if (xsecToken) {
    params.append('xsec_token', xsecToken)
  }
  return request<XhsNote>(`/note/${noteId}?${params}`)
}

/**
 * 解析笔记链接
 */
export async function parseNoteUrl(url: string): Promise<ApiResponse<XhsNote>> {
  return request<XhsNote>('/parse', {
    method: 'POST',
    body: JSON.stringify({ url }),
  })
}

/**
 * 搜索笔记
 */
export async function searchNotes(
  clientId: string,
  keyword: string,
  options?: {
    page?: number
    page_size?: number
    sort?: SearchSortType
    note_type?: SearchNoteType
  }
): Promise<ApiResponse<XhsSearchResult>> {
  return request<XhsSearchResult>('/search/notes', {
    method: 'POST',
    body: JSON.stringify({
      client_id: clientId,
      keyword,
      page: options?.page ?? 1,
      page_size: options?.page_size ?? 20,
      sort: options?.sort ?? 'general',
      note_type: options?.note_type ?? 'all',
    }),
  })
}

// ==================== 用户相关 ====================

/**
 * 搜索用户
 */
export async function searchUsers(
  clientId: string,
  keyword: string,
  options?: {
    page?: number
    page_size?: number
  }
): Promise<ApiResponse<XhsUserSearchResult>> {
  return request<XhsUserSearchResult>('/search/users', {
    method: 'POST',
    body: JSON.stringify({
      client_id: clientId,
      keyword,
      page: options?.page ?? 1,
      page_size: options?.page_size ?? 20,
    }),
  })
}

/**
 * 获取用户信息
 */
export async function getUserInfo(
  clientId: string,
  userId: string
): Promise<ApiResponse<XhsUser>> {
  return request<XhsUser>(`/user/${userId}?client_id=${clientId}`)
}

/**
 * 获取用户笔记列表
 */
export async function getUserNotes(
  clientId: string,
  userId: string,
  cursor?: string
): Promise<ApiResponse<{ notes: XhsNote[]; cursor: string; has_more: boolean }>> {
  const params = new URLSearchParams({ client_id: clientId })
  if (cursor) {
    params.append('cursor', cursor)
  }
  return request<{ notes: XhsNote[]; cursor: string; has_more: boolean }>(
    `/user/${userId}/notes?${params}`
  )
}

/**
 * 获取用户收藏笔记
 */
export async function getUserCollectedNotes(
  clientId: string,
  userId: string,
  cursor?: string
): Promise<ApiResponse<{ notes: XhsNote[]; cursor: string; has_more: boolean }>> {
  const params = new URLSearchParams({ client_id: clientId })
  if (cursor) {
    params.append('cursor', cursor)
  }
  return request<{ notes: XhsNote[]; cursor: string; has_more: boolean }>(
    `/user/${userId}/collected?${params}`
  )
}

/**
 * 获取用户点赞笔记
 */
export async function getUserLikedNotes(
  clientId: string,
  userId: string,
  cursor?: string
): Promise<ApiResponse<{ notes: XhsNote[]; cursor: string; has_more: boolean }>> {
  const params = new URLSearchParams({ client_id: clientId })
  if (cursor) {
    params.append('cursor', cursor)
  }
  return request<{ notes: XhsNote[]; cursor: string; has_more: boolean }>(
    `/user/${userId}/liked?${params}`
  )
}

// ==================== 信息流 ====================

/**
 * 获取首页信息流
 */
export async function getHomeFeed(
  clientId: string,
  feedType?: FeedType,
  cursor?: string
): Promise<ApiResponse<XhsFeedResult>> {
  return request<XhsFeedResult>('/feed', {
    method: 'POST',
    body: JSON.stringify({
      client_id: clientId,
      feed_type: feedType ?? 'recommend',
      cursor,
    }),
  })
}

// ==================== 评论相关 ====================

/**
 * 获取笔记评论
 */
export async function getNoteComments(
  clientId: string,
  noteId: string,
  cursor?: string
): Promise<ApiResponse<{ comments: XhsComment[]; cursor: string; has_more: boolean }>> {
  const params = new URLSearchParams({ client_id: clientId })
  if (cursor) {
    params.append('cursor', cursor)
  }
  return request<{ comments: XhsComment[]; cursor: string; has_more: boolean }>(
    `/note/${noteId}/comments?${params}`
  )
}

/**
 * 获取评论的子评论
 */
export async function getSubComments(
  clientId: string,
  noteId: string,
  commentId: string,
  cursor?: string
): Promise<ApiResponse<{ comments: XhsComment[]; cursor: string; has_more: boolean }>> {
  const params = new URLSearchParams({ client_id: clientId })
  if (cursor) {
    params.append('cursor', cursor)
  }
  return request<{ comments: XhsComment[]; cursor: string; has_more: boolean }>(
    `/note/${noteId}/comments/${commentId}/sub?${params}`
  )
}

// ==================== 工具函数 ====================

/**
 * 从 localStorage 获取保存的小红书配置
 */
export function getStoredXhsConfig(): XhsClientConfig | null {
  const stored = localStorage.getItem('xhsConfig')
  if (!stored) return null
  
  try {
    const config = JSON.parse(stored)
    if (!config.cookie) return null
    
    return {
      cookie: config.cookie,
      user_agent: config.userAgent || undefined,
      timeout: config.timeout || 10,
      proxies: config.proxy || undefined,
    }
  } catch {
    return null
  }
}

/**
 * 自动创建客户端（使用存储的配置）
 */
export async function autoCreateClient(): Promise<ApiResponse<XhsClientInfo>> {
  const config = getStoredXhsConfig()
  if (!config) {
    return {
      success: false,
      error: '未配置小红书 Cookie，请在设置中配置',
    }
  }
  
  return createClient(config)
}

// ==================== 导出默认对象 ====================

export default {
  // 客户端管理
  createClient,
  getClient,
  deleteClient,
  autoCreateClient,
  
  // 笔记相关
  getNoteById,
  parseNoteUrl,
  searchNotes,
  
  // 用户相关
  searchUsers,
  getUserInfo,
  getUserNotes,
  getUserCollectedNotes,
  getUserLikedNotes,
  
  // 信息流
  getHomeFeed,
  
  // 评论相关
  getNoteComments,
  getSubComments,
  
  // 工具函数
  getStoredXhsConfig,
}
