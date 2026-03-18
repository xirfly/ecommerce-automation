# 多渠道接入设计

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 目标

设计灵活的多渠道接入架构，支持：
- Web后台和飞书（一期）
- 动态配置扩展其他渠道（Telegram、企业微信、Discord等）
- 统一的消息路由和会话管理
- 渠道级权限控制

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    渠道层                                │
│  Web后台 | 飞书 | Telegram | 企业微信 | Discord         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              OpenClaw Gateway（统一网关）                │
│  • 渠道适配器  • 消息路由  • 会话管理  • 权限验证      │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Agent层                               │
│  7个专业Agent处理业务逻辑                                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  业务后端（FastAPI）                     │
│  数据持久化、业务规则、API服务                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

| 组件 | 职责 | 技术实现 |
|------|------|----------|
| **渠道适配器** | 适配不同渠道的消息格式 | OpenClaw Bindings |
| **消息路由** | 根据规则路由到对应Agent | OpenClaw Routing Rules |
| **会话管理** | 维护用户会话状态 | Redis + OpenClaw Session |
| **权限验证** | 验证用户身份和权限 | JWT + 白名单 |

---

## 3. 渠道配置管理

### 3.1 渠道配置数据结构

**数据库表：** `channels`（参考数据模型设计文档）

**配置示例（飞书）：**
```json
{
  "id": 1,
  "name": "飞书客服Bot",
  "type": "feishu",
  "config": {
    "app_id": "cli_xxx",
    "app_secret": "xxx",
    "verification_token": "xxx",
    "encrypt_key": "xxx",
    "webhook_url": "https://your-domain/webhook/feishu"
  },
  "routing_rules": {
    "default_agent": "product-analyzer",
    "keyword_routing": {
      "分析": "product-analyzer",
      "生成": "content-generator",
      "报表": "data-analyzer"
    },
    "whitelist_users": ["ou_xxx", "ou_yyy"]
  },
  "is_enabled": true
}
```

### 3.2 渠道类型定义

```python
from enum import Enum

class ChannelType(str, Enum):
    """渠道类型"""
    WEB = "web"              # Web后台
    FEISHU = "feishu"        # 飞书
    TELEGRAM = "telegram"    # Telegram
    WECHAT = "wechat"        # 企业微信
    DISCORD = "discord"      # Discord
    WHATSAPP = "whatsapp"    # WhatsApp
```

---

## 4. OpenClaw Gateway配置

### 4.1 配置文件结构

**文件路径：** `~/.openclaw/openclaw.json`

**配置示例：**
```json
{
  "agents": {
    "list": [
      {
        "name": "product-analyzer",
        "model": {
          "primary": "claude-opus-4"
        },
        "workspace": "~/.openclaw/workspace/analyzer",
        "systemPrompt": "你是一个专业的产品分析师..."
      },
      {
        "name": "content-generator",
        "model": {
          "primary": "claude-opus-4"
        },
        "workspace": "~/.openclaw/workspace/generator",
        "systemPrompt": "你是一个内容生成专家..."
      }
    ]
  },
  "bindings": [
    {
      "channel": "feishu",
      "agent": "product-analyzer",
      "filter": {
        "userWhitelist": ["ou_xxx", "ou_yyy"]
      }
    },
    {
      "channel": "web",
      "agent": "product-analyzer"
    }
  ]
}
```

### 4.2 动态配置更新

**流程：**
1. 用户在Web后台添加/修改渠道配置
2. FastAPI后端保存到MySQL数据库
3. 后端生成新的`openclaw.json`配置文件
4. 通知OpenClaw Gateway重新加载配置

**实现代码：**
```python
import json
from pathlib import Path

class OpenClawConfigManager:
    """OpenClaw配置管理器"""

    def __init__(self, config_path: str = "~/.openclaw/openclaw.json"):
        self.config_path = Path(config_path).expanduser()

    def generate_config(self, channels: list, agents: list) -> dict:
        """生成OpenClaw配置"""
        config = {
            "agents": {
                "list": [
                    {
                        "name": agent.name,
                        "model": {"primary": agent.model},
                        "workspace": f"~/.openclaw/workspace/{agent.name}",
                        "systemPrompt": agent.system_prompt
                    }
                    for agent in agents
                ]
            },
            "bindings": []
        }

        # 生成渠道绑定
        for channel in channels:
            if not channel.is_enabled:
                continue

            binding = {
                "channel": channel.type,
                "agent": channel.routing_rules.get("default_agent", "product-analyzer")
            }

            # 添加白名单过滤
            if "whitelist_users" in channel.routing_rules:
                binding["filter"] = {
                    "userWhitelist": channel.routing_rules["whitelist_users"]
                }

            config["bindings"].append(binding)

        return config

    def save_config(self, config: dict):
        """保存配置到文件"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def reload_gateway(self):
        """通知OpenClaw Gateway重新加载配置"""
        # 方式1：发送信号
        # os.kill(gateway_pid, signal.SIGHUP)

        # 方式2：调用OpenClaw CLI
        # subprocess.run(["openclaw", "reload"])

        # 方式3：通过API（如果OpenClaw提供）
        # requests.post("http://localhost:3000/api/reload")
        pass
```

---

## 5. 渠道适配器实现

### 5.1 Web后台渠道

**实现方式：** 直接调用FastAPI后端API

**流程：**
```
用户操作（React前端）
    ↓
调用FastAPI API
    ↓
创建Celery任务
    ↓
调用OpenClaw Gateway
    ↓
Agent处理
    ↓
WebSocket推送结果给前端
```

**无需OpenClaw Gateway适配器**

### 5.2 飞书渠道

**实现方式：** OpenClaw Gateway + 飞书Bot

**配置步骤：**

1. **创建飞书Bot**
   - 登录飞书开放平台
   - 创建企业自建应用
   - 获取 App ID 和 App Secret
   - 配置事件订阅URL：`https://your-domain/webhook/feishu`

2. **配置OpenClaw Gateway**
   ```json
   {
     "bindings": [
       {
         "channel": "feishu",
         "agent": "product-analyzer",
         "config": {
           "appId": "cli_xxx",
           "appSecret": "xxx",
           "verificationToken": "xxx",
           "encryptKey": "xxx"
         }
       }
     ]
   }
   ```

3. **消息处理流程**
   ```
   用户发送飞书消息
       ↓
   飞书服务器推送到Webhook
       ↓
   OpenClaw Gateway接收
       ↓
   路由到对应Agent
       ↓
   Agent处理并返回
       ↓
   OpenClaw Gateway发送回复
       ↓
   用户收到飞书消息
   ```

### 5.3 Telegram渠道

**实现方式：** OpenClaw Gateway + Telegram Bot

**配置步骤：**

1. **创建Telegram Bot**
   - 与 @BotFather 对话
   - 使用 `/newbot` 创建Bot
   - 获取 Bot Token

2. **配置OpenClaw Gateway**
   ```json
   {
     "bindings": [
       {
         "channel": "telegram",
         "agent": "product-analyzer",
         "config": {
           "botToken": "123456:ABC-DEF..."
         }
       }
     ]
   }
   ```

3. **消息处理流程**
   - 使用Webhook或Long Polling接收消息
   - 路由到Agent处理
   - 通过Telegram Bot API发送回复

### 5.4 企业微信渠道

**实现方式：** OpenClaw Gateway + 企业微信应用

**配置步骤：**

1. **创建企业微信应用**
   - 登录企业微信管理后台
   - 创建自建应用
   - 获取 Corp ID、Agent ID、Secret

2. **配置OpenClaw Gateway**
   ```json
   {
     "bindings": [
       {
         "channel": "wechat",
         "agent": "product-analyzer",
         "config": {
           "corpId": "ww_xxx",
           "agentId": "1000001",
           "secret": "xxx"
         }
       }
     ]
   }
   ```

---

## 6. 消息路由规则

### 6.1 路由策略

**默认路由：**
- 所有消息路由到默认Agent（如 `product-analyzer`）

**关键词路由：**
```json
{
  "keyword_routing": {
    "分析": "product-analyzer",
    "生成图片": "image-generator",
    "生成视频": "video-generator",
    "生成文案": "text-generator",
    "报表": "data-analyzer"
  }
}
```

**正则路由：**
```json
{
  "regex_routing": {
    "^分析.*产品$": "product-analyzer",
    "^生成.*详情页$": "page-builder"
  }
}
```

**意图识别路由（高级）：**
- 使用LLM识别用户意图
- 根据意图路由到对应Agent

### 6.2 路由实现

```python
class MessageRouter:
    """消息路由器"""

    def __init__(self, routing_rules: dict):
        self.routing_rules = routing_rules

    def route(self, message: str) -> str:
        """路由消息到对应Agent"""

        # 1. 关键词路由
        keyword_routing = self.routing_rules.get("keyword_routing", {})
        for keyword, agent in keyword_routing.items():
            if keyword in message:
                return agent

        # 2. 正则路由
        regex_routing = self.routing_rules.get("regex_routing", {})
        for pattern, agent in regex_routing.items():
            if re.match(pattern, message):
                return agent

        # 3. 默认路由
        return self.routing_rules.get("default_agent", "product-analyzer")
```

---

## 7. 会话管理

### 7.1 会话数据结构

**Redis存储：**
```
Key: session:openclaw:{session_id}
Type: List
TTL: 3600秒（1小时）

Data:
[
  {
    "role": "user",
    "content": "帮我分析这个产品",
    "timestamp": "2026-03-16T10:00:00Z"
  },
  {
    "role": "assistant",
    "content": "好的，正在分析...",
    "timestamp": "2026-03-16T10:00:05Z"
  }
]
```

### 7.2 会话管理实现

```python
from app.constants import RedisKeys, RedisTTL

class SessionManager:
    """会话管理器"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def add_message(self, session_id: str, role: str, content: str):
        """添加消息到会话"""
        key = RedisKeys.session_openclaw(session_id)
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.redis.lpush(key, json.dumps(message))
        self.redis.expire(key, RedisTTL.SESSION_OPENCLAW)

    def get_messages(self, session_id: str, limit: int = 10) -> list:
        """获取最近N条消息"""
        key = RedisKeys.session_openclaw(session_id)
        messages = self.redis.lrange(key, 0, limit - 1)
        return [json.loads(msg) for msg in messages]

    def clear_session(self, session_id: str):
        """清除会话"""
        key = RedisKeys.session_openclaw(session_id)
        self.redis.delete(key)
```

---

## 8. 权限验证

### 8.1 白名单机制

**配置：**
```json
{
  "routing_rules": {
    "whitelist_users": ["ou_xxx", "ou_yyy"]
  }
}
```

**验证逻辑：**
```python
def verify_user(user_id: str, channel_config: dict) -> bool:
    """验证用户是否在白名单中"""
    whitelist = channel_config.get("routing_rules", {}).get("whitelist_users", [])

    # 如果没有配置白名单，允许所有用户
    if not whitelist:
        return True

    # 检查用户是否在白名单中
    return user_id in whitelist
```

### 8.2 权限级别

| 权限级别 | 说明 | 可用功能 |
|---------|------|----------|
| **游客** | 未登录用户 | 仅查询功能 |
| **普通用户** | 已登录用户 | 查询 + 基础操作 |
| **运营人员** | Operator角色 | 产品管理 + 任务执行 |
| **管理员** | Admin角色 | 所有功能 |

---

## 9. 错误处理

### 9.1 渠道连接失败

**场景：** 飞书Bot Token过期、Telegram Bot被封禁

**处理：**
1. 记录错误日志
2. 标记渠道为"异常"状态
3. 发送告警通知管理员
4. 自动禁用该渠道

### 9.2 消息发送失败

**场景：** 网络超时、API限流

**处理：**
1. 重试3次（指数退避：1s、2s、4s）
2. 仍失败则记录到失败队列
3. 定时任务重新发送失败消息

### 9.3 Agent处理超时

**场景：** Agent执行时间过长

**处理：**
1. 设置超时时间（30秒）
2. 超时后返回友好提示："处理中，请稍后查看结果"
3. 后台继续执行，完成后主动推送

---

## 10. 监控与日志

### 10.1 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 消息接收量 | 每分钟接收的消息数 | > 1000/min |
| 消息处理时长 | Agent处理平均时长 | > 10秒 |
| 错误率 | 消息处理失败比例 | > 5% |
| 渠道可用性 | 渠道连接状态 | 离线 > 5分钟 |

### 10.2 日志记录

**日志内容：**
```json
{
  "timestamp": "2026-03-16T10:00:00Z",
  "channel": "feishu",
  "user_id": "ou_xxx",
  "message": "帮我分析这个产品",
  "agent": "product-analyzer",
  "duration_ms": 3500,
  "status": "success",
  "error": null
}
```

**日志存储：**
- 实时日志：输出到控制台
- 持久化日志：写入文件或ELK
- 错误日志：单独存储，便于排查

---

## 11. 扩展新渠道

### 11.1 扩展步骤

1. **在数据库中添加渠道类型**
   ```python
   class ChannelType(str, Enum):
       # ... 现有渠道
       NEW_CHANNEL = "new_channel"  # 新渠道
   ```

2. **实现渠道适配器**
   - 如果OpenClaw支持，直接配置
   - 如果不支持，需要开发适配器

3. **配置路由规则**
   ```json
   {
     "bindings": [
       {
         "channel": "new_channel",
         "agent": "product-analyzer",
         "config": {
           "api_key": "xxx"
         }
       }
     ]
   }
   ```

4. **测试验证**
   - 发送测试消息
   - 验证路由正确
   - 验证回复正常

### 11.2 常见渠道对接

| 渠道 | 难度 | 所需信息 | 预计工时 |
|------|------|----------|----------|
| 飞书 | 简单 | App ID、Secret | 1天 |
| Telegram | 简单 | Bot Token | 1天 |
| 企业微信 | 中等 | Corp ID、Agent ID、Secret | 2天 |
| Discord | 简单 | Bot Token | 1天 |
| WhatsApp | 困难 | Business API | 3-5天 |
| 钉钉 | 中等 | App Key、Secret | 2天 |

---

## 12. 相关文档

- [系统架构总览](../architecture/01-system-architecture.md) - 整体架构
- [Agent编排设计](../architecture/02-agent-orchestration.md) - Agent实现
- [渠道配置模块](../features/04-channel-config.md) - 渠道配置功能
- [Redis数据结构](../database/02-redis-structure.md) - 会话存储
