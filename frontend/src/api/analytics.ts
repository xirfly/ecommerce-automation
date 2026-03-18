import { apiClient } from '@/utils/request'

export interface AnalyticsOverview {
  products: {
    total: number
    by_status: Record<string, number>
    by_category: Record<string, number>
  }
  tasks: {
    total: number
    by_status: Record<string, number>
    by_type: Record<string, number>
    success_rate: number
    trend: Array<{
      date: string
      count: number
    }>
  }
}

export interface TaskStats {
  by_status: Record<string, number>
  by_type: Record<string, number>
  avg_execution_time: number
}

export interface ProductStats {
  by_status: Record<string, number>
  by_category: Record<string, number>
  by_platform: Record<string, number>
}

export const analyticsApi = {
  // 获取概览统计
  getOverview: () => {
    return apiClient.get<{ code: number; data: AnalyticsOverview }>('/api/v1/analytics/overview')
  },

  // 获取任务统计
  getTaskStats: () => {
    return apiClient.get<{ code: number; data: TaskStats }>('/api/v1/analytics/tasks/stats')
  },

  // 获取产品统计
  getProductStats: () => {
    return apiClient.get<{ code: number; data: ProductStats }>('/api/v1/analytics/products/stats')
  },
}
