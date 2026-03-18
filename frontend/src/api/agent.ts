/**
 * Agent API 接口
 */
import { apiClient } from '../utils/request';

// Agent 信息接口
export interface AgentInfo {
  name: string;
  description: string;
  dependencies: string[];
}

// Agent 依赖关系图接口
export interface AgentGraph {
  nodes: Array<{
    id: string;
    label: string;
    name: string;
  }>;
  edges: Array<{
    from: string;
    to: string;
  }>;
}

// Agent 统计接口
export interface AgentStatistics {
  period_days: number;
  start_date: string;
  end_date: string;
  agents: Array<{
    agent_name: string;
    total_executions: number;
    success_count: number;
    error_count: number;
    success_rate: number;
  }>;
}

// 任务执行流程接口
export interface ExecutionFlow {
  task_type: string;
  total_steps: number;
  flow: Array<{
    step: number;
    agent_name: string;
    description: string;
    dependencies: string[];
  }>;
}

// Agent 日志接口
export interface AgentLog {
  id: number;
  agent_name: string;
  log_level: string;
  message: string;
  extra_data: any;
  created_at: string;
}

/**
 * 获取 Agent 列表
 */
export const getAgentList = () => {
  return apiClient.get<AgentInfo[]>('/api/v1/agents/list');
};

/**
 * 获取 Agent 依赖关系图
 */
export const getAgentGraph = () => {
  return apiClient.get<AgentGraph>('/api/v1/agents/graph');
};

/**
 * 获取 Agent 执行统计
 */
export const getAgentStatistics = (days: number = 7) => {
  return apiClient.get<AgentStatistics>('/api/v1/agents/statistics', {
    params: { days },
  });
};

/**
 * 获取任务执行流程
 */
export const getExecutionFlow = (taskType: string) => {
  return apiClient.get<ExecutionFlow>('/api/v1/agents/execution-flow', {
    params: { task_type: taskType },
  });
};

/**
 * 获取任务的 Agent 执行日志
 */
export const getAgentLogs = (taskId: number) => {
  return apiClient.get<AgentLog[]>(`/api/v1/agents/logs/${taskId}`);
};

/**
 * 获取 Agent 详细信息
 */
export const getAgentInfo = (agentName: string) => {
  return apiClient.get<AgentInfo>(`/api/v1/agents/info/${agentName}`);
};
