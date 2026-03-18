import { apiClient } from '@/utils/request'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: {
    id: number
    username: string
    role: string
  }
}

export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'operator' | 'viewer'
  permissions: string[]
}

export const authApi = {
  // 登录
  login: (params: LoginParams) => {
    return apiClient.post<{ code: number; message: string; data: LoginResponse }>('/api/v1/auth/login', params)
  },

  // 获取当前用户信息
  getCurrentUser: () => {
    return apiClient.get<{ code: number; data: User }>('/api/v1/auth/me')
  },

  // 登出
  logout: () => {
    return apiClient.post('/api/v1/auth/logout')
  },
}
