# Agent 管理 API 端点文档

## 概述

Agent 管理 API 提供了查询和管理 Agent 编排系统的接口，包括 Agent 列表、依赖关系、执行统计等功能。

## 基础信息

- **Base URL**: `/api/v1/agents`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON

## API 端点列表

### 1. 获取 Agent 列表

**端点**: `GET /api/v1/agents/list`

**描述**: 获取所有已注册的 Agent 信息

**请求参数**: 无

**响应示例**:
```json
{
  "code": 0,
  "message": "获取成功",
  "data": [
    {
      "name": "product_analysis",
      "description": "分析产品市场潜力、竞争情况、利润率等",
      "dependencies": []
    },
    {
      "name": "content_generation",
      "description": "生成产品标题、描述、关键词等营销内容",
      "dependencies": ["product_analysis"]
    }
  ]
}
```

### 2. 获取 Agent 依赖关系图

**端点**: `GET /api/v1/agents/graph`

**描述**: 获取 Agent 之间的依赖关系，用于可视化展示

**请求参数**: 无

**响应示例**:
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "nodes": [
      {
        "id": "product_analysis",
        "label": "分析产品市场潜力、竞争情况、利润率等",
        "name": "product_analysis"
      }
    ],
    "edges": [
      {
        "from": "product_analysis",
        "to": "content_generation"
      }
    ]
  }
}
```

### 3. 获取 Agent 执行统计

**端点**: `GET /api/v1/agents/statistics`

**描述**: 统计最近 N 天内各个 Agent 的执行情况

**请求参数**:
- `days` (query, optional): 统计天数，默认 7 天，范围 1-30

**响应示例**:
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "period_days": 7,
    "start_date": "2026-03-10",
    "end_date": "2026-03-17",
    "agents": [
      {
        "agent_name": "product_analysis",
        "total_executions": 150,
        "success_count": 145,
        "error_count": 5,
        "success_rate": 96.67,
        "avg_duration": 3.5
      }
    ]
  }
}
```

### 4. 获取任务执行流程

**端点**: `GET /api/v1/agents/execution-flow`

**描述**: 获取指定任务类型的 Agent 执行流程

**请求参数**:
- `task_type` (query, required): 任务类型
  - `product_analysis`: 选品分析
  - `content_generation`: 内容生成
  - `image_generation`: 图片生成
  - `video_generation`: 视频生成
  - `review`: 内容审核
  - `publish`: 完整发布流程

**响应示例**:
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "task_type": "publish",
    "total_steps": 6,
    "flow": [
      {
        "step": 1,
        "agent_name": "product_analysis",
        "description": "分析产品市场潜力、竞争情况、利润率等",
        "dependencies": []
      },
      {
        "step": 2,
        "agent_name": "price_optimization",
        "description": "根据市场情况优化产品定价",
        "dependencies": ["product_analysis"]
      }
    ]
  }
}
```

### 5. 获取任务的 Agent 执行日志

**端点**: `GET /api/v1/agents/logs/{task_id}`

**描述**: 获取指定任务中所有 Agent 的执行日志

**路径参数**:
- `task_id` (integer, required): 任务 ID

**响应示例**:
```json
{
  "code": 0,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "agent_name": "product_analysis",
      "log_level": "INFO",
      "message": "Agent [product_analysis] 执行成功",
      "extra_data": {
        "market_potential": "高",
        "competition_level": "中等"
      },
      "created_at": "2026-03-17T10:30:00"
    }
  ]
}
```

### 6. 获取 Agent 详细信息

**端点**: `GET /api/v1/agents/info/{agent_name}`

**描述**: 获取指定 Agent 的详细信息

**路径参数**:
- `agent_name` (string, required): Agent 名称

**响应示例**:
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "name": "product_analysis",
    "description": "分析产品市场潜力、竞争情况、利润率等",
    "dependencies": []
  }
}
```

## 错误响应

所有 API 在发生错误时返回统一格式：

```json
{
  "code": 400,
  "message": "错误描述",
  "errors": []
}
```

常见错误码：
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 无权限
- `404`: 资源不存在
- `500`: 服务器内部错误

## 使用示例

### JavaScript/TypeScript

```typescript
// 获取 Agent 列表
const response = await fetch('/api/v1/agents/list', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const data = await response.json();

// 获取执行统计
const stats = await fetch('/api/v1/agents/statistics?days=7', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Python

```python
import requests

# 获取 Agent 列表
response = requests.get(
    'http://localhost:8000/api/v1/agents/list',
    headers={'Authorization': f'Bearer {token}'}
)
agents = response.json()

# 获取执行流程
flow = requests.get(
    'http://localhost:8000/api/v1/agents/execution-flow',
    params={'task_type': 'publish'},
    headers={'Authorization': f'Bearer {token}'}
)
```

## 相关文档

- [Agent 编排系统说明](AGENT_SYSTEM.md)
- [后端代码结构](BACKEND_STRUCTURE.md)
- [API 文档](API_DOCUMENTATION.md)

