import { apiClient } from '@/utils/request'

export interface Task {
  id: number
  task_id: string
  product_id: number
  task_type: string
  status: 'pending' | 'running' | 'success' | 'failed' | 'timeout'
  progress: number
  result?: any
  error_message?: string
  retry_count: number
  started_at?: string
  completed_at?: string
  created_by: number
  created_at: string
  updated_at: string
}

export interface TaskListParams {
  page?: number
  page_size?: number
  product_id?: number
  task_type?: string
  status?: string
}

export interface TaskListResponse {
  code: number
  data: {
    items: Task[]
    total: number
    page: number
    page_size: number
  }
}

export interface CreateTaskParams {
  product_id: number
  task_type: string
}

export interface TaskLog {
  id: number
  task_id: number
  agent_name: string
  log_level: string
  message: string
  extra_data?: any
  created_at: string
}

export const taskApi = {
  // 获取任务列表
  getList: (params: TaskListParams) => {
    return apiClient.get<TaskListResponse>('/api/v1/tasks', { params })
  },

  // 获取任务详情
  getDetail: (id: number) => {
    return apiClient.get<{ code: number; data: Task }>(`/api/v1/tasks/${id}`)
  },

  // 创建任务
  create: (data: CreateTaskParams) => {
    return apiClient.post<{ code: number; data: Task }>('/api/v1/tasks', data)
  },

  // 重试任务
  retry: (id: number) => {
    return apiClient.post<{ code: number; data: Task }>(`/api/v1/tasks/${id}/retry`)
  },

  // 获取任务日志
  getLogs: (id: number) => {
    return apiClient.get<{ code: number; data: TaskLog[] }>(`/api/v1/tasks/${id}/logs`)
  },

  // 删除任务
  delete: (id: number) => {
    return apiClient.delete<{ code: number; message: string }>(`/api/v1/tasks/${id}`)
  },
}
