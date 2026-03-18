# Agent编排设计

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 目标

设计7个专业Agent的职责划分、编排策略和协作机制，实现：
- 清晰的职责边界，每个Agent专注一个领域
- 高效的编排策略，串行+并行混合执行
- 可靠的错误处理，超时重试和降级机制
- 完整的Memory管理，支持上下文对话

---

## 2. Agent职责定义

### 2.1 Agent 1: 选品分析Agent

**职责：** 分析产品市场潜力，提供选品建议

**输入：**
```json
{
  "product_keyword": "无线蓝牙耳机",
  "target_market": "国内",
  "price_range": [99, 299]
}
```

**处理逻辑：**
1. 市场容量分析（基于关键词搜索量）
2. 竞品分析（价格分布、销量排名）
3. 趋势预测（季节性、增长趋势）
4. 利润预估（成本估算、利润率）

**输出：**
```json
{
  "market_size": "500万/月",
  "competition_level": "中等",
  "recommended_price": 199,
  "profit_margin": "35%",
  "trend": "上升",
  "suggestions": ["建议主打降噪功能", "目标人群：上班族"]
}
```

**实现方式（一期）：**
- 使用规则引擎 + 模板数据
- 预设不同品类的市场数据
- 随机生成合理的分析结果

**实现方式（二期）：**
- 对接真实市场数据API（如淘宝指数、百度指数）
- 使用AI模型分析趋势
- 爬取竞品数据进行对比

---

### 2.2 Agent 2: 图片生成Agent

**职责：** 生成产品主图、详情图、场景图

**输入：**
```json
{
  "product_info": {
    "name": "无线蓝牙耳机",
    "category": "数码",
    "features": ["降噪", "长续航", "轻便"]
  },
  "style": "简约科技风",
  "image_types": ["main", "detail", "scene"]
}
```

**处理逻辑：**
1. 根据产品信息生成图片提示词
2. 调用AI图片生成服务
3. 图片质量检查和优化
4. 返回图片URL

**输出：**
```json
{
  "images": {
    "main": "https://cdn.example.com/main.jpg",
    "detail": ["https://cdn.example.com/detail1.jpg", "..."],
    "scene": ["https://cdn.example.com/scene1.jpg", "..."]
  },
  "generation_time": "5.2s"
}
```

**实现方式（一期）：**
- 返回占位图URL（使用placeholder.com）
- 根据产品类型返回不同风格的占位图

**实现方式（二期）：**
- 对接Midjourney API / Stable Diffusion API
- 本地部署SDXL模型
- 图片后处理（裁剪、压缩、水印）

---

### 2.3 Agent 3: 视频生成Agent

**职责：** 生成产品展示视频、短视频

**输入：**
```json
{
  "product_info": {
    "name": "无线蓝牙耳机",
    "features": ["降噪", "长续航"]
  },
  "video_type": "product_demo",
  "duration": 15
}
```

**处理逻辑：**
1. 生成视频脚本
2. 调用AI视频生成服务
3. 视频质量检查
4. 返回视频URL

**输出：**
```json
{
  "video_url": "https://cdn.example.com/demo.mp4",
  "thumbnail": "https://cdn.example.com/thumb.jpg",
  "duration": 15,
  "generation_time": "6.8s"
}
```

**实现方式（一期）：**
- 返回模板视频URL
- 根据产品类型返回不同的模板视频

**实现方式（二期）：**
- 对接Runway API / Pika API
- 本地视频编辑（FFmpeg）
- 自动配音和字幕

---

### 2.4 Agent 4: 文案生成Agent

**职责：** 生成产品标题、描述、卖点、详情文案

**输入：**
```json
{
  "product_info": {
    "name": "无线蓝牙耳机",
    "features": ["降噪", "长续航", "轻便"],
    "target_audience": "上班族"
  },
  "platform": "淘宝"
}
```

**处理逻辑：**
1. 分析产品特点和目标人群
2. 生成吸引人的标题
3. 提炼核心卖点
4. 编写详情文案

**输出：**
```json
{
  "title": "【降噪黑科技】无线蓝牙耳机 长续航48小时 上班通勤必备",
  "description": "专为上班族设计，主动降噪技术...",
  "selling_points": [
    "主动降噪，隔绝嘈杂",
    "48小时超长续航",
    "轻至4.5g，佩戴无感"
  ],
  "detail_content": "产品详情长文案..."
}
```

**实现方式（一期）：**
- 使用模板 + 变量替换
- 预设不同品类的文案模板
- 根据产品特点填充模板

**实现方式（二期）：**
- 对接GPT-4 API / Claude API
- 本地部署Llama等开源模型
- 根据平台风格调整文案

---

### 2.5 Agent 5: 详情页制作Agent

**职责：** 组装图片、视频、文案，生成详情页HTML

**输入：**
```json
{
  "images": {...},
  "video": {...},
  "text": {...},
  "template": "default"
}
```

**处理逻辑：**
1. 选择详情页模板
2. 按顺序组装内容
3. 生成HTML/JSON
4. 预览链接生成

**输出：**
```json
{
  "html": "<div>...</div>",
  "preview_url": "https://preview.example.com/xxx",
  "json_data": {...}
}
```

**实现方式：**
- 预设多种详情页模板
- 使用模板引擎（Jinja2）渲染
- 生成静态HTML或JSON数据

---

### 2.6 Agent 6: 上下架管理Agent

**职责：** 多平台产品发布、库存同步、状态管理

**输入：**
```json
{
  "product_data": {...},
  "platforms": ["淘宝", "京东"],
  "publish_strategy": "immediate"
}
```

**处理逻辑：**
1. 转换为平台API格式
2. 调用平台API发布
3. 记录发布结果
4. 返回产品链接

**输出：**
```json
{
  "results": [
    {
      "platform": "淘宝",
      "status": "success",
      "product_id": "123456",
      "product_url": "https://item.taobao.com/123456"
    }
  ]
}
```

**实现方式（一期）：**
- Mock Adapter，模拟发布成功
- 返回模拟的产品链接

**实现方式（二期）：**
- 对接真实平台API
- 实现平台适配器（Adapter模式）
- 库存同步和状态管理

---

### 2.7 Agent 7: 数据分析Agent

**职责：** 销售报表、运营建议、趋势分析

**输入：**
```json
{
  "date_range": ["2026-03-01", "2026-03-16"],
  "report_type": "weekly"
}
```

**处理逻辑：**
1. 从数据库查询销售数据
2. 统计分析（销量、收入、转化率）
3. 生成图表数据
4. AI生成分析报告

**输出：**
```json
{
  "summary": {
    "total_sales": 1234,
    "total_revenue": 245600,
    "avg_conversion_rate": "3.2%"
  },
  "charts": {...},
  "ai_insights": "本周销量增长27%，建议..."
}
```

**实现方式：**
- SQL聚合查询
- 使用ECharts生成图表配置
- AI分析（一期用规则，二期用LLM）

---

## 3. 编排策略

### 3.1 串行+并行混合编排

```
产品创建
    ↓
Agent 1: 选品分析（串行，必须先执行）
    ↓
┌───────────────┬───────────────┬───────────────┐
│ Agent 2:      │ Agent 3:      │ Agent 4:      │
│ 图片生成      │ 视频生成      │ 文案生成      │ (并行执行)
└───────────────┴───────────────┴───────────────┘
    ↓
Agent 5: 详情页制作（串行，等待2/3/4完成）
    ↓
Agent 6: 上下架管理（串行）
    ↓
完成

Agent 7: 数据分析（独立执行，不依赖其他Agent）
```

### 3.2 编排代码示例

```python
async def product_workflow(product_id: int):
    """产品全流程编排"""

    # 1. 串行：选品分析
    analysis_result = await execute_agent(
        agent_name="product-analyzer",
        input_data={"product_id": product_id}
    )

    # 2. 并行：内容生成
    tasks = [
        execute_agent("image-generator", analysis_result),
        execute_agent("video-generator", analysis_result),
        execute_agent("text-generator", analysis_result)
    ]
    image, video, text = await asyncio.gather(*tasks)

    # 3. 串行：详情页制作
    detail_page = await execute_agent(
        "page-builder",
        {"image": image, "video": video, "text": text}
    )

    # 4. 串行：上架发布
    publish_result = await execute_agent(
        "publisher",
        {"detail_page": detail_page}
    )

    return publish_result
```

---

## 4. 超时重试机制

### 4.1 重试策略

```python
async def execute_agent_with_retry(
    agent_name: str,
    input_data: dict,
    max_retries: int = 3,
    timeout: int = 30
):
    """带重试的Agent执行"""

    for attempt in range(max_retries):
        try:
            result = await asyncio.wait_for(
                execute_agent(agent_name, input_data),
                timeout=timeout
            )
            return result

        except asyncio.TimeoutError:
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)  # 5秒、10秒
                logger.warning(
                    f"Agent {agent_name} timeout, "
                    f"retry {attempt + 1}/{max_retries} "
                    f"after {wait_time}s"
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    f"Agent {agent_name} failed after "
                    f"{max_retries} attempts"
                )
                return None  # 返回None，触发降级
```

### 4.2 降级策略

| Agent | 失败后降级方案 |
|-------|----------------|
| Agent 1 | 使用默认分析结果，继续流程 |
| Agent 2 | 使用占位图，标记需要人工补充 |
| Agent 3 | 跳过视频，仅使用图片 |
| Agent 4 | 使用基础模板文案 |
| Agent 5 | 使用简化版详情页模板 |
| Agent 6 | 保存为草稿，等待人工发布 |
| Agent 7 | 返回基础统计数据，不生成AI分析 |

---

## 5. Memory管理

### 5.1 短期记忆（Redis）

**存储内容：** 最近10轮对话

**数据结构：**
```
session:{session_id} -> List[Message]
```

**清理策略：**
```python
def clean_short_term_memory(session_id: str):
    """清理短期记忆，保留最近10条"""
    messages = redis.lrange(f"session:{session_id}", 0, -1)
    if len(messages) > 10:
        redis.ltrim(f"session:{session_id}", -10, -1)
```

**TTL：** 1小时

### 5.2 长期记忆（MySQL）

**存储内容：** 重要信息（用户偏好、历史订单、关键决策）

**表结构：**
```sql
CREATE TABLE agent_memory (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(100),
    agent_name VARCHAR(50),
    memory_type ENUM('user_preference', 'history', 'decision'),
    memory_data JSON,
    created_at TIMESTAMP
);
```

**提取策略：**
```python
def extract_important_info(messages: List[dict]) -> dict:
    """从对话中提取重要信息"""
    important_info = {
        "user_preferences": [],
        "key_decisions": []
    }

    for msg in messages:
        # 识别用户偏好（如"我喜欢简约风格"）
        if "喜欢" in msg["content"] or "偏好" in msg["content"]:
            important_info["user_preferences"].append(msg["content"])

        # 识别关键决策（如"选择方案A"）
        if "选择" in msg["content"] or "决定" in msg["content"]:
            important_info["key_decisions"].append(msg["content"])

    return important_info
```

---

## 6. 依赖关系

### 6.1 Agent间依赖

```
Agent 1 (选品分析)
    ↓ 提供产品分析结果
┌───┴───┬───────┬───────┐
Agent 2  Agent 3  Agent 4
    └───┬───┴───────┘
        ↓ 提供内容素材
    Agent 5 (详情页制作)
        ↓ 提供详情页数据
    Agent 6 (上下架管理)

Agent 7 (数据分析) - 独立，不依赖其他Agent
```

### 6.2 外部依赖

| Agent | 外部依赖 | 是否必需 |
|-------|----------|----------|
| Agent 1 | 市场数据API | ❌ 一期用模拟数据 |
| Agent 2 | 图片生成API | ❌ 一期用占位图 |
| Agent 3 | 视频生成API | ❌ 一期用模板视频 |
| Agent 4 | LLM API | ❌ 一期用模板文案 |
| Agent 5 | 无 | - |
| Agent 6 | 电商平台API | ❌ 一期用Mock |
| Agent 7 | 无 | - |

---

## 7. 实施要点

### 7.1 开发顺序

1. **Agent 1** - 选品分析（基础，其他Agent依赖）
2. **Agent 2/3/4** - 内容生成（可并行开发）
3. **Agent 5** - 详情页制作（依赖2/3/4）
4. **Agent 6** - 上下架管理（依赖5）
5. **Agent 7** - 数据分析（独立，可随时开发）

### 7.2 测试策略

**单元测试：** 每个Agent独立测试
- 输入验证
- 输出格式验证
- 错误处理验证

**集成测试：** 测试Agent编排流程
- 串行执行测试
- 并行执行测试
- 超时重试测试
- 降级策略测试

**性能测试：** 测试并发和耗时
- 单Agent执行时间
- 全流程执行时间
- 并发执行能力

---

## 8. 相关文档

- [系统架构总览](01-system-architecture.md) - 整体架构设计
- [多渠道接入设计](03-multi-channel.md) - 渠道配置和路由
- [任务调度模块](../features/02-task-scheduling.md) - 任务执行机制
