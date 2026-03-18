/**
 * 销售数据 API
 */
import { apiClient } from '@/utils/request'

export interface SalesData {
  id: number
  product_id: number
  product_name?: string
  date: string
  views: number
  clicks: number
  orders: number
  sales_amount: number
  created_at: string
}

export interface SalesDataCreateParams {
  product_id: number
  date: string
  views?: number
  clicks?: number
  orders?: number
  sales_amount?: number
}

export interface SalesDataUpdateParams {
  views?: number
  clicks?: number
  orders?: number
  sales_amount?: number
}

export interface SalesDataListParams {
  page?: number
  page_size?: number
  product_id?: number
  start_date?: string
  end_date?: string
}

export interface SalesDataListResponse {
  items: SalesData[]
  total: number
  page: number
  page_size: number
}

export interface SalesTrendData {
  date: string
  views: number
  clicks: number
  orders: number
  sales_amount: number
}

export interface SalesStatistics {
  total_views: number
  total_clicks: number
  total_orders: number
  total_sales_amount: number
  avg_conversion_rate: number
  trend_data: SalesTrendData[]
}

export interface ProductSalesRanking {
  product_id: number
  product_name: string
  total_orders: number
  total_sales_amount: number
  total_views: number
  conversion_rate: number
}

export interface SalesAnalyticsResponse {
  statistics: SalesStatistics
  top_products: ProductSalesRanking[]
  period_start: string
  period_end: string
}

/**
 * 创建销售数据
 */
export const createSalesData = (data: SalesDataCreateParams) => {
  return apiClient.post<SalesData>('/api/v1/sales/create', data)
}

/**
 * 获取销售数据列表
 */
export const getSalesDataList = (params?: SalesDataListParams) => {
  return apiClient.get<SalesDataListResponse>('/api/v1/sales/list', { params })
}

/**
 * 更新销售数据
 */
export const updateSalesData = (id: number, data: SalesDataUpdateParams) => {
  return apiClient.put<SalesData>(`/api/v1/sales/${id}`, data)
}

/**
 * 删除销售数据
 */
export const deleteSalesData = (id: number) => {
  return apiClient.delete(`/api/v1/sales/${id}`)
}

/**
 * 获取销售分析数据
 */
export const getSalesAnalytics = (days: number = 30, product_id?: number) => {
  return apiClient.get<SalesAnalyticsResponse>('/api/v1/sales/analytics', {
    params: { days, product_id },
  })
}
