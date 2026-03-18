import { apiClient } from '@/utils/request'

export interface Product {
  id: number
  name: string
  category: string
  price: number
  cost?: number
  status: 'draft' | 'analyzing' | 'generating' | 'reviewing' | 'published' | 'offline'
  platform?: string
  analysis_result?: any
  images?: string[]
  videos?: string[]
  description?: string
  detail_page_url?: string
  created_by: number
  created_at: string
  updated_at: string
}

export interface ProductListParams {
  page?: number
  page_size?: number
  keyword?: string
  category?: string
  status?: string
}

export interface ProductListResponse {
  code: number
  data: {
    items: Product[]
    total: number
    page: number
    page_size: number
  }
}

export interface CreateProductParams {
  name: string
  category: string
  price: number
  platform?: string
  description?: string
}

export const productApi = {
  // 获取产品列表
  getList: (params: ProductListParams) => {
    return apiClient.get<ProductListResponse>('/api/v1/products', { params })
  },

  // 获取产品详情
  getDetail: (id: number) => {
    return apiClient.get<{ code: number; data: Product }>(`/api/v1/products/${id}`)
  },

  // 创建产品
  create: (data: CreateProductParams) => {
    return apiClient.post<{ code: number; data: Product }>('/api/v1/products', data)
  },

  // 更新产品
  update: (id: number, data: Partial<Product>) => {
    return apiClient.put<{ code: number; data: Product }>(`/api/v1/products/${id}`, data)
  },

  // 删除产品
  delete: (id: number) => {
    return apiClient.delete<{ code: number; message: string }>(`/api/v1/products/${id}`)
  },

  // 批量删除
  batchDelete: (ids: number[]) => {
    return apiClient.post<{ code: number; message: string }>('/api/v1/products/batch-delete', {
      ids,
    })
  },
}
