# 任务调度模块

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 目标

实现Agent任务的调度和管理，支持：
- 任务创建和执行
- 任务状态追踪
- 超时重试机制
- 任务日志记录

---

## 2. 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 创建任务 | 触发Agent执行 | P0 |
| 查询任务状态 | 实时查看任务进度 | P0 |
| 任务列表 | 查看所有任务 | P0 |
| 取消任务 | 取消正在执行的任务 | P1 |
| 重试任务 | 重新执行失败的任务 | P1 |
| 任务日志 | 查看详细执行日志 | P1 |

---

## 3. 任务类型

```python
from enum import Enum

class TaskType(str, Enum):
    """任务类型"""
    ANALYZE = "analyze"              # Agent 1: 选品分析
    GENERATE_IMAGE = "generate_image"  # Agent 2: 图片生成
    GENERATE_VIDEO = "generate_video"  # Agent 3: 视频生成
    GENERATE_TEXT = "generate_text"    # Agent 4: 文案生成
    CREATE_PAGE = "create_page"        # Agent 5: 详情页制作
    PUBLISH = "publish"                # Agent 6: 上下架管理
    REPORT = "report"                  # Agent 7: 数据分析
```

---

## 4. 任务状态流转

```
pending (待执行)
    ↓
running (执行中)
    ↓
success (成功) / failed (失败) / timeout (超时) / cancelled (已取消)
```

---

## 5. API设计

### 5.1 创建任务

```http
POST /api/v1/tasks/analyze
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "product_id": 123,
  "input_data": {
    "keyword": "无线蓝牙耳机",
    "target_market": "国内",
    "price_range": [99, 299]
  }
}

Response (201 Created):
{
  "code": 0,
  "message": "任务创建成功",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_type": "analyze",
    "status": "pending",
    "created_at": "2026-03-16T10:00:00Z"
  }
}
```

### 5.2 查询任务状态

```http
GET /api/v1/tasks/{task_id}
Authorization: Bearer {token}

Response (200 OK):
{
  "code": 0,
  "message": "查询成功",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "product_id": 123,
    "task_type": "analyze",
    "status": "success",
    "input_data": {...},
    "output_data": {...},
    "duration_ms": 3500,
    "started_at": "2026-03-16T10:00:01Z",
    "completed_at": "2026-03-16T10:00:04Z"
  }
}
```

---

## 6. Celery任务实现

### 6.1 任务定义

```python
from celery import Celery
from app.constants import RedisKeys

celery_app = Celery('tasks', broker='redis://localhost:6379/1')

@celery_app.task(bind=True, max_retries=3)
def execute_agent_task(self, task_id: str, agent_name: str, input_data: dict):
    """执行Agent任务"""
    try:
        # 1. 更新任务状态为running
        update_task_status(task_id, 'running')

        # 2. 调用OpenClaw Gateway执行Agent
        result = call_openclaw_agent(agent_name, input_data)

        # 3. 更新任务状态为success
        update_task_status(task_id, 'success', output_data=result)

        return result

    except Exception as exc:
        # 重试机制
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=5 * (self.request.retries + 1))
        else:
            # 最终失败
            update_task_status(task_id, 'failed', error_message=str(exc))
            raise
```

### 6.2 超时控制

```python
@celery_app.task(bind=True, time_limit=30, soft_time_limit=25)
def execute_agent_task_with_timeout(self, task_id: str, agent_name: str, input_data: dict):
    """带超时控制的任务执行"""
    try:
        result = call_openclaw_agent(agent_name, input_data)
        return result
    except SoftTimeLimitExceeded:
        # 软超时，记录日志
        logger.warning(f"Task {task_id} approaching time limit")
        raise
    except TimeLimitExceeded:
        # 硬超时，标记为timeout
        update_task_status(task_id, 'timeout')
        raise
```

---

## 7. WebSocket实时推送

### 7.1 后端实现

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_task_update(self, user_id: str, task_data: dict):
        """发送任务更新"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json({
                "type": "task_update",
                "data": task_data
            })

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
```

### 7.2 前端实现

```typescript
// src/services/websocket.ts
class WebSocketService {
  private ws: WebSocket | null = null;

  connect(userId: string) {
    this.ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'task_update') {
        // 更新任务状态
        this.handleTaskUpdate(message.data);
      }
    };
  }

  handleTaskUpdate(taskData: any) {
    // 触发状态更新
    eventBus.emit('task:update', taskData);
  }
}

export default new WebSocketService();
```

---

## 8. 相关文档

- [Agent编排设计](../architecture/02-agent-orchestration.md) - Agent实现细节
- [数据模型设计](../database/01-data-model.md) - tasks表结构
- [Redis数据结构](../database/02-redis-structure.md) - Celery队列
