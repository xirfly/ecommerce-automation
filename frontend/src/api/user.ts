/**
 * 用户管理 API 接口
 */
import { apiClient } from '../utils/request';

// 用户信息接口
export interface User {
  id: number;
  username: string;
  email: string | null;
  role: 'admin' | 'operator' | 'viewer';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 创建用户请求
export interface UserCreateRequest {
  username: string;
  password: string;
  email?: string;
  role?: 'admin' | 'operator' | 'viewer';
}

// 更新用户请求
export interface UserUpdateRequest {
  email?: string;
  role?: 'admin' | 'operator' | 'viewer';
  is_active?: boolean;
}

// 更新密码请求
export interface UserPasswordUpdateRequest {
  old_password: string;
  new_password: string;
}

// 用户统计
export interface UserStatistics {
  total_users: number;
  active_users: number;
  admin_users: number;
  operator_users: number;
  viewer_users: number;
}

/**
 * 获取用户列表
 */
export const getUserList = (params?: {
  role?: string;
  is_active?: boolean;
}) => {
  return apiClient.get<User[]>('/api/v1/users/list', { params });
};

/**
 * 获取用户统计
 */
export const getUserStatistics = () => {
  return apiClient.get<UserStatistics>('/api/v1/users/statistics');
};

/**
 * 获取用户详情
 */
export const getUser = (userId: number) => {
  return apiClient.get<User>(`/api/v1/users/${userId}`);
};

/**
 * 创建用户
 */
export const createUser = (data: UserCreateRequest) => {
  return apiClient.post<User>('/api/v1/users/create', data);
};

/**
 * 更新用户
 */
export const updateUser = (userId: number, data: UserUpdateRequest) => {
  return apiClient.put<User>(`/api/v1/users/${userId}`, data);
};

/**
 * 更新密码
 */
export const updatePassword = (userId: number, data: UserPasswordUpdateRequest) => {
  return apiClient.put<null>(`/api/v1/users/${userId}/password`, data);
};

/**
 * 删除用户
 */
export const deleteUser = (userId: number) => {
  return apiClient.delete<null>(`/api/v1/users/${userId}`);
};
