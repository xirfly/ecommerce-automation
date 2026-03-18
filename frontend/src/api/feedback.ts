/**
 * 反馈 API
 */
import { apiClient } from '@/utils/request'

export interface Feedback {
  id: number
  user_id: number
  username?: string
  title: string
  description: string
  images?: string[]
  status: 'pending' | 'processing' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  admin_reply?: string
  created_at: string
  updated_at: string
}

export interface FeedbackCreateParams {
  title: string
  description: string
  images?: string[]
}

export interface FeedbackUpdateParams {
  status?: string
  priority?: string
  admin_reply?: string
}

export interface FeedbackListParams {
  page?: number
  page_size?: number
  status?: string
  priority?: string
  user_id?: number
}

export interface FeedbackListResponse {
  items: Feedback[]
  total: number
  page: number
  page_size: number
}

export interface FeedbackStatistics {
  total: number
  by_status: Record<string, number>
  by_priority: Record<string, number>
}

/**
 * 上传反馈图片
 */
export const uploadImage = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post<{ url: string }>('/api/v1/feedback/upload-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/**
 * 创建反馈
 */
export const createFeedback = (data: FeedbackCreateParams) => {
  return apiClient.post<Feedback>('/api/v1/feedback/create', data)
}

/**
 * 获取反馈列表
 */
export const getFeedbackList = (params?: FeedbackListParams) => {
  return apiClient.get<FeedbackListResponse>('/api/v1/feedback/list', { params })
}

/**
 * 获取反馈详情
 */
export const getFeedbackDetail = (id: number) => {
  return apiClient.get<Feedback>(`/api/v1/feedback/${id}`)
}

/**
 * 更新反馈（管理员）
 */
export const updateFeedback = (id: number, data: FeedbackUpdateParams) => {
  return apiClient.put<Feedback>(`/api/v1/feedback/${id}`, data)
}

/**
 * 删除反馈（管理员）
 */
export const deleteFeedback = (id: number) => {
  return apiClient.delete(`/api/v1/feedback/${id}`)
}

/**
 * 获取反馈统计（管理员）
 */
export const getFeedbackStatistics = () => {
  return apiClient.get<FeedbackStatistics>('/api/v1/feedback/statistics/summary')
}
