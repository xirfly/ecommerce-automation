/**
 * 系统设置 API 接口
 */
import { apiClient } from '../utils/request';

// 系统配置接口
export interface SystemConfig {
  id: number;
  config_key: string;
  config_value: string | null;
  config_type: string;
  category: string;
  description: string | null;
  is_public: boolean;
  is_encrypted: boolean;
  created_at: string;
  updated_at: string;
}

// 系统设置响应（按分类组织）
export interface SystemSettings {
  basic: Record<string, any>;
  ai: Record<string, any>;
  task: Record<string, any>;
  notification: Record<string, any>;
  security: Record<string, any>;
}

// 创建配置请求
export interface SystemConfigCreateRequest {
  config_key: string;
  config_value?: string;
  config_type?: string;
  category: string;
  description?: string;
  is_public?: boolean;
  is_encrypted?: boolean;
}

// 更新配置请求
export interface SystemConfigUpdateRequest {
  config_value?: string;
  description?: string;
  is_public?: boolean;
}

// 批量更新请求
export interface BatchUpdateRequest {
  configs: Array<{
    config_key: string;
    config_value: any;
    config_type?: string;
    category?: string;
    description?: string;
    is_public?: boolean;
    is_encrypted?: boolean;
  }>;
}

/**
 * 获取所有系统设置（按分类组织）
 */
export const getAllSettings = () => {
  return apiClient.get<SystemSettings>('/api/v1/settings/all');
};

/**
 * 获取系统配置列表
 */
export const getConfigList = (params?: { category?: string }) => {
  return apiClient.get<SystemConfig[]>('/api/v1/settings/list', { params });
};

/**
 * 获取指定配置
 */
export const getConfig = (configKey: string) => {
  return apiClient.get<SystemConfig>(`/api/v1/settings/${configKey}`);
};

/**
 * 创建系统配置
 */
export const createConfig = (data: SystemConfigCreateRequest) => {
  return apiClient.post<SystemConfig>('/api/v1/settings/create', data);
};

/**
 * 更新系统配置
 */
export const updateConfig = (configKey: string, data: SystemConfigUpdateRequest) => {
  return apiClient.put<SystemConfig>(`/api/v1/settings/${configKey}`, data);
};

/**
 * 批量更新系统配置
 */
export const batchUpdateConfigs = (data: BatchUpdateRequest) => {
  return apiClient.post<{ updated: number; created: number; total: number }>(
    '/api/v1/settings/batch-update',
    data
  );
};

/**
 * 删除系统配置
 */
export const deleteConfig = (configKey: string) => {
  return apiClient.delete<null>(`/api/v1/settings/${configKey}`);
};
