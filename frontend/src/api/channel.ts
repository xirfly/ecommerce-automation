/**
 * 渠道管理 API 接口
 */
import { apiClient } from '../utils/request';

// 渠道信息接口
export interface Channel {
  id: number;
  name: string;
  channel_type: 'ecommerce' | 'notification';
  platform: string;
  description?: string;
  config: Record<string, any>;
  status: 'active' | 'inactive' | 'error';
  is_default: boolean;
  usage_count: number;
  last_used_at?: string;
  last_error?: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

// 创建渠道请求
export interface ChannelCreateRequest {
  name: string;
  channel_type: 'ecommerce' | 'notification';
  platform: string;
  description?: string;
  config: Record<string, any>;
  is_default?: boolean;
}

// 更新渠道请求
export interface ChannelUpdateRequest {
  name?: string;
  description?: string;
  config?: Record<string, any>;
  status?: 'active' | 'inactive' | 'error';
  is_default?: boolean;
}

// 测试渠道请求
export interface ChannelTestRequest {
  channel_id: number;
}

// 测试渠道响应
export interface ChannelTestResponse {
  success: boolean;
  message: string;
  details?: Record<string, any>;
}

// 渠道统计
export interface ChannelStatistics {
  total_channels: number;
  active_channels: number;
  ecommerce_channels: number;
  notification_channels: number;
  total_usage: number;
}

/**
 * 获取渠道列表
 */
export const getChannelList = (params?: {
  channel_type?: string;
  status?: string;
}) => {
  return apiClient.get<Channel[]>('/api/v1/channels/list', { params });
};

/**
 * 获取渠道详情
 */
export const getChannel = (channelId: number) => {
  return apiClient.get<Channel>(`/api/v1/channels/${channelId}`);
};

/**
 * 创建渠道
 */
export const createChannel = (data: ChannelCreateRequest) => {
  return apiClient.post<Channel>('/api/v1/channels/create', data);
};

/**
 * 更新渠道
 */
export const updateChannel = (channelId: number, data: ChannelUpdateRequest) => {
  return apiClient.put<Channel>(`/api/v1/channels/${channelId}`, data);
};

/**
 * 删除渠道
 */
export const deleteChannel = (channelId: number) => {
  return apiClient.delete<null>(`/api/v1/channels/${channelId}`);
};

/**
 * 测试渠道连接
 */
export const testChannel = (data: ChannelTestRequest) => {
  return apiClient.post<ChannelTestResponse>('/api/v1/channels/test', data);
};

/**
 * 获取渠道统计
 */
export const getChannelStatistics = () => {
  return apiClient.get<ChannelStatistics>('/api/v1/channels/statistics/summary');
};
