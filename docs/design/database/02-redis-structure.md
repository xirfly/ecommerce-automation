# Redis数据结构设计

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 目标

设计高效的Redis数据结构，支持：
- 热点数据缓存
- Celery任务队列
- 用户会话管理
- OpenClaw Gateway会话状态
- API限流控制

---

## 2. Redis使用场景

| 场景 | 数据结构 | TTL | 用途 |
|------|----------|-----|------|
| 数据缓存 | String/Hash | 5-10分钟 | 产品信息、用户信息 |
| 任务队列 | List | 永久 | Celery任务队列 |
| 会话管理 | String/Hash | 1小时 | 用户会话、OpenClaw会话 |
| 限流控制 | String | 1分钟 | API限流计数器 |
| 短期记忆 | List | 1小时 | Agent对话记忆 |

---

## 3. 数据结构设计

### 3.1 数据缓存

#### 3.1.1 产品信息缓存

**Key格式：** `cache:product:{product_id}`
**数据类型：** Hash
**TTL：** 300秒（5分钟）

**字段：**
```
HSET cache:product:123
  id 123
  name "无线蓝牙耳机"
  category "数码"
  price 199.00
  status "published"
  updated_at "2026-03-16T10:30:00Z"
```

**操作示例：**
```python
# 写入缓存
redis.hset(f"cache:product:{product_id}", mapping={
    "id": product.id,
    "name": product.name,
    "category": product.category,
    "price": str(product.price),
    "status": product.status,
    "updated_at": product.updated_at.isoformat()
})
redis.expire(f"cache:product:{product_id}", 300)

# 读取缓存
product_data = redis.hgetall(f"cache:product:{product_id}")
if not product_data:
    # 缓存未命中，从数据库查询
    product = db.query(Product).get(product_id)
    # 写入缓存
    ...
```

#### 3.1.2 用户信息缓存

**Key格式：** `cache:user:{user_id}`
**数据类型：** Hash
**TTL：** 600秒（10分钟）

**字段：**
```
HSET cache:user:1
  id 1
  username "admin"
  role "admin"
  team_id 1
```

---

### 3.2 任务队列

#### 3.2.1 Celery任务队列

**Key格式：** `celery:queue:{queue_name}`
**数据类型：** List
**TTL：** 永久

**队列类型：**
- `celery:queue:default` - 默认队列
- `celery:queue:agent` - Agent任务队列
- `celery:queue:report` - 报表任务队列

**操作示例：**
```python
# Celery自动管理，无需手动操作
# 配置示例
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

#### 3.2.2 任务结果缓存

**Key格式：** `celery:result:{task_id}`
**数据类型：** String (JSON)
**TTL：** 3600秒（1小时）

**数据示例：**
```json
{
  "status": "SUCCESS",
  "result": {
    "product_id": 123,
    "analysis": {...}
  },
  "traceback": null,
  "children": []
}
```

---

### 3.3 会话管理

#### 3.3.1 用户会话（JWT Token）

**Key格式：** `session:user:{user_id}:{token_id}`
**数据类型：** String (JSON)
**TTL：** 86400秒（24小时）

**数据示例：**
```json
{
  "user_id": 1,
  "username": "admin",
  "role": "admin",
  "token_id": "abc123",
  "created_at": "2026-03-16T10:00:00Z",
  "expires_at": "2026-03-17T10:00:00Z"
}
```

**操作示例：**
```python
# 创建会话
token_id = str(uuid.uuid4())
session_data = {
    "user_id": user.id,
    "username": user.username,
    "role": user.role,
    "token_id": token_id,
    "created_at": datetime.now().isoformat(),
    "expires_at": (datetime.now() + timedelta(days=1)).isoformat()
}
redis.setex(
    f"session:user:{user.id}:{token_id}",
    86400,
    json.dumps(session_data)
)

# 验证会话
session_data = redis.get(f"session:user:{user_id}:{token_id}")
if session_data:
    return json.loads(session_data)
else:
    raise Unauthorized("Session expired")

# 撤销会话（登出）
redis.delete(f"session:user:{user_id}:{token_id}")
```

#### 3.3.2 OpenClaw Gateway会话

**Key格式：** `session:openclaw:{session_id}`
**数据类型：** List (消息列表)
**TTL：** 3600秒（1小时）

**数据示例：**
```
LPUSH session:openclaw:abc123
  '{"role": "user", "content": "帮我分析这个产品", "timestamp": "2026-03-16T10:00:00Z"}'
  '{"role": "assistant", "content": "好的，正在分析...", "timestamp": "2026-03-16T10:00:05Z"}'
```

**操作示例：**
```python
# 添加消息
redis.lpush(
    f"session:openclaw:{session_id}",
    json.dumps({
        "role": "user",
        "content": message,
        "timestamp": datetime.now().isoformat()
    })
)
redis.expire(f"session:openclaw:{session_id}", 3600)

# 获取最近10条消息
messages = redis.lrange(f"session:openclaw:{session_id}", 0, 9)
messages = [json.loads(msg) for msg in messages]

# 清理旧消息（保留最近10条）
redis.ltrim(f"session:openclaw:{session_id}", 0, 9)
```

---

### 3.4 限流控制

#### 3.4.1 用户级限流

**Key格式：** `ratelimit:user:{user_id}:{endpoint}`
**数据类型：** String (计数器)
**TTL：** 60秒（1分钟）

**限流规则：**
- 普通用户：60次/分钟
- 管理员：300次/分钟

**操作示例：**
```python
def check_rate_limit(user_id: int, endpoint: str, limit: int = 60):
    """检查限流"""
    key = f"ratelimit:user:{user_id}:{endpoint}"
    current = redis.incr(key)

    if current == 1:
        # 第一次请求，设置过期时间
        redis.expire(key, 60)

    if current > limit:
        raise TooManyRequests(f"Rate limit exceeded: {limit}/min")

    return current
```

#### 3.4.2 IP级限流

**Key格式：** `ratelimit:ip:{ip_address}`
**数据类型：** String (计数器)
**TTL：** 60秒（1分钟）

**限流规则：**
- 未登录用户：30次/分钟

---

### 3.5 Agent短期记忆

#### 3.5.1 对话记忆

**Key格式：** `memory:agent:{session_id}`
**数据类型：** List (消息列表)
**TTL：** 3600秒（1小时）

**数据示例：**
```
LPUSH memory:agent:session123
  '{"agent": "product-analyzer", "message": "市场容量约500万/月", "timestamp": "..."}'
  '{"agent": "image-generator", "message": "图片生成完成", "timestamp": "..."}'
```

**清理策略：**
```python
def clean_agent_memory(session_id: str, max_messages: int = 10):
    """清理Agent记忆，保留最近N条"""
    key = f"memory:agent:{session_id}"
    messages = redis.lrange(key, 0, -1)

    if len(messages) > max_messages:
        # 保留最近10条
        redis.ltrim(key, 0, max_messages - 1)

        # 提取重要信息存入MySQL
        important_info = extract_important_info(messages[max_messages:])
        if important_info:
            save_to_mysql(session_id, important_info)
```

---

## 4. 缓存策略

### 4.1 缓存更新策略

#### 4.1.1 Cache-Aside（旁路缓存）

**读取流程：**
```python
def get_product(product_id: int):
    # 1. 先查缓存
    cached = redis.hgetall(f"cache:product:{product_id}")
    if cached:
        return cached

    # 2. 缓存未命中，查数据库
    product = db.query(Product).get(product_id)
    if not product:
        return None

    # 3. 写入缓存
    redis.hset(f"cache:product:{product_id}", mapping=product.dict())
    redis.expire(f"cache:product:{product_id}", 300)

    return product
```

**更新流程：**
```python
def update_product(product_id: int, data: dict):
    # 1. 更新数据库
    product = db.query(Product).get(product_id)
    product.update(data)
    db.commit()

    # 2. 删除缓存（下次读取时重新加载）
    redis.delete(f"cache:product:{product_id}")

    return product
```

#### 4.1.2 Write-Through（写穿透）

**适用场景：** 高一致性要求的数据

```python
def update_product_write_through(product_id: int, data: dict):
    # 1. 同时更新数据库和缓存
    product = db.query(Product).get(product_id)
    product.update(data)
    db.commit()

    # 2. 更新缓存
    redis.hset(f"cache:product:{product_id}", mapping=product.dict())
    redis.expire(f"cache:product:{product_id}", 300)

    return product
```

### 4.2 缓存失效策略

#### 4.2.1 主动失效

**场景：** 数据更新时主动删除缓存

```python
# 产品更新时
redis.delete(f"cache:product:{product_id}")

# 批量删除
keys = redis.keys("cache:product:*")
if keys:
    redis.delete(*keys)
```

#### 4.2.2 被动失效

**场景：** 设置TTL，自动过期

```python
# 设置5分钟过期
redis.setex(f"cache:product:{product_id}", 300, data)
```

---

## 5. 性能优化

### 5.1 Pipeline批量操作

**场景：** 批量读取多个产品

```python
def get_products_batch(product_ids: List[int]):
    """批量获取产品（使用Pipeline）"""
    pipe = redis.pipeline()

    # 批量查询
    for product_id in product_ids:
        pipe.hgetall(f"cache:product:{product_id}")

    results = pipe.execute()

    # 处理结果
    products = []
    for i, result in enumerate(results):
        if result:
            products.append(result)
        else:
            # 缓存未命中，从数据库查询
            product = db.query(Product).get(product_ids[i])
            if product:
                products.append(product)
                # 写入缓存
                redis.hset(f"cache:product:{product_ids[i]}", mapping=product.dict())
                redis.expire(f"cache:product:{product_ids[i]}", 300)

    return products
```

### 5.2 连接池配置

```python
from redis import ConnectionPool, Redis

# 创建连接池
pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50,
    decode_responses=True
)

# 使用连接池
redis_client = Redis(connection_pool=pool)
```

---

## 6. 监控与维护

### 6.1 内存监控

**查看内存使用：**
```bash
redis-cli INFO memory
```

**关键指标：**
- `used_memory`: 已使用内存
- `used_memory_peak`: 内存使用峰值
- `mem_fragmentation_ratio`: 内存碎片率

### 6.2 慢查询监控

**配置慢查询：**
```bash
redis-cli CONFIG SET slowlog-log-slower-than 10000  # 10ms
redis-cli CONFIG SET slowlog-max-len 128
```

**查看慢查询：**
```bash
redis-cli SLOWLOG GET 10
```

### 6.3 Key过期监控

**查看Key数量：**
```bash
redis-cli DBSIZE
```

**查看过期Key：**
```bash
redis-cli INFO keyspace
```

---

## 7. 持久化配置

### 7.1 RDB持久化

**配置：**
```conf
# redis.conf
save 900 1      # 900秒内至少1个key变化
save 300 10     # 300秒内至少10个key变化
save 60 10000   # 60秒内至少10000个key变化

dbfilename dump.rdb
dir /var/lib/redis
```

### 7.2 AOF持久化

**配置：**
```conf
# redis.conf
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec  # 每秒同步一次

# AOF重写
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

### 7.3 混合持久化（推荐）

**配置：**
```conf
# redis.conf
aof-use-rdb-preamble yes  # 开启混合持久化
```

**优势：**
- RDB快照 + AOF增量日志
- 恢复速度快，数据丢失少

---

## 8. 高可用方案

### 8.1 主从复制

**配置从节点：**
```conf
# redis.conf (从节点)
replicaof 192.168.1.100 6379
masterauth <password>
```

### 8.2 哨兵模式

**配置哨兵：**
```conf
# sentinel.conf
sentinel monitor mymaster 192.168.1.100 6379 2
sentinel auth-pass mymaster <password>
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 10000
```

**Python客户端配置：**
```python
from redis.sentinel import Sentinel

sentinel = Sentinel([
    ('localhost', 26379),
    ('localhost', 26380),
    ('localhost', 26381)
], socket_timeout=0.1)

# 获取主节点
master = sentinel.master_for('mymaster', socket_timeout=0.1)

# 获取从节点（读操作）
slave = sentinel.slave_for('mymaster', socket_timeout=0.1)
```

---

## 9. 常用命令

### 9.1 调试命令

```bash
# 查看所有Key
redis-cli KEYS *

# 查看Key类型
redis-cli TYPE cache:product:123

# 查看Key过期时间
redis-cli TTL cache:product:123

# 查看Key内存占用
redis-cli MEMORY USAGE cache:product:123

# 删除所有Key（危险！）
redis-cli FLUSHDB
```

### 9.2 性能测试

```bash
# 基准测试
redis-benchmark -h localhost -p 6379 -c 50 -n 10000

# 测试特定命令
redis-benchmark -t set,get -n 100000 -q
```

---

## 10. 相关文档

- [数据模型设计](01-data-model.md) - MySQL表结构
- [系统架构总览](../architecture/01-system-architecture.md) - 整体架构
- [任务调度模块](../features/02-task-scheduling.md) - Celery任务队列
