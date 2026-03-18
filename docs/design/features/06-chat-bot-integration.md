# 聊天机器人接入指南

**文档版本：** v1.0
**最后更新：** 2026-03-18

---

## 1. 概述

本系统支持通过飞书、Telegram、企业微信等聊天平台进行操作和接收通知，让用户无需打开网页即可完成所有操作。

### 1.1 核心功能

| 功能 | 说明 | 支持平台 |
|------|------|----------|
| 实时通知推送 | 任务状态变更自动推送 | 飞书、Telegram、企业微信 |
| 命令交互 | 通过聊天命令操作系统 | 飞书、Telegram |
| 产品查询 | 查看产品列表和详情 | 飞书、Telegram |
| 任务管理 | 创建、查询任务 | 飞书、Telegram |
| 卡片交互 | 富文本卡片和按钮交互 | 飞书、企业微信 |

### 1.2 技术架构

```
┌─────────────────────────────────────────────────┐
│  前端 Web 界面                                   │
│  http://localhost:5173                          │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  FastAPI 后端                                    │
│  - API 接口                                      │
│  - WebSocket 实时通信                            │
│  - Celery 任务队列                               │
└─────────────────────────────────────────────────┘
                      ↓
        ┌─────────────┴─────────────┐
        ↓                           ↓
┌──────────────┐            ┌──────────────┐
│  飞书机器人   │            │ Telegram Bot │
│              │            │              │
│ • 接收命令    │            │ • 接收命令    │
│ • 发送通知    │            │ • 发送通知    │
│ • 卡片交互    │            │ • 按钮交互    │
└──────────────┘            └──────────────┘
        ↓                           ↓
┌──────────────┐            ┌──────────────┐
│  飞书用户     │            │ Telegram 用户 │
└──────────────┘            └──────────────┘
```

---

## 2. 飞书机器人接入

### 2.1 配置步骤

#### 步骤 1：创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 `App ID` 和 `App Secret`
4. 配置机器人能力，开启以下权限：
   - `im:message` - 发送消息
   - `im:message.group_at_msg` - 接收群聊@消息
   - `im:message.p2p_msg` - 接收私聊消息

#### 步骤 2：配置 Webhook

1. 在飞书应用后台配置事件订阅
2. 设置请求地址：`https://your-domain.com/api/v1/webhooks/lark`
3. 获取 `Verification Token` 和 `Encrypt Key`

#### 步骤 3：配置环境变量

编辑 `backend/.env` 文件：

```bash
# 飞书配置
FEISHU_APP_ID=cli_a1b2c3d4e5f6g7h8
FEISHU_APP_SECRET=your_app_secret_here
FEISHU_VERIFICATION_TOKEN=your_verification_token
FEISHU_ENCRYPT_KEY=your_encrypt_key
```

#### 步骤 4：重启服务

```bash
cd backend
python run.py
```

### 2.2 支持的命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/help` 或 `帮助` | 显示帮助信息 | `/help` |
| `/products` 或 `产品列表` | 查看产品列表 | `/products` |
| `/tasks` 或 `任务列表` | 查看任务列表 | `/tasks` |
| `/create` 或 `创建任务` | 创建新任务 | `/create` |

### 2.3 交互示例

#### 示例 1：查看产品列表

```
用户: /products

机器人:
┌─────────────────────────────────┐
│ 📦 产品列表（最近10个）          │
├─────────────────────────────────┤
│ • 无线蓝牙耳机                   │
│   分类: 数码 | 价格: ¥299        │
│                                 │
│ • 运动手环                       │
│   分类: 运动 | 价格: ¥199        │
│                                 │
│ • 智能手表                       │
│   分类: 数码 | 价格: ¥899        │
└─────────────────────────────────┘
```

#### 示例 2：查看任务列表

```
用户: /tasks

机器人:
┌─────────────────────────────────┐
│ 📋 任务列表（最近10个）          │
├─────────────────────────────────┤
│ ✅ 任务 #123                     │
│   类型: publish | 进度: 100%    │
│                                 │
│ 🔄 任务 #124                     │
│   类型: content_generation      │
│   进度: 45%                      │
│                                 │
│ ❌ 任务 #125                     │
│   类型: image_generation        │
│   进度: 30%                      │
└─────────────────────────────────┘
```

#### 示例 3：创建任务

```
用户: /create

机器人:
┌─────────────────────────────────┐
│ 创建任务                         │
├─────────────────────────────────┤
│ 请选择要创建的任务类型：         │
│                                 │
│ • 选品分析 - 分析产品市场趋势    │
│ • 内容生成 - 生成产品营销文案    │
│ • 图片生成 - 生成产品图片        │
│ • 视频生成 - 生成产品视频        │
│ • 内容审核 - 审核产品内容        │
│ • 发布上架 - 发布产品到平台      │
│                                 │
│ [选品分析] [内容生成] [内容审核] │
└─────────────────────────────────┘

用户: 点击 [发布上架]

机器人:
✅ 任务创建成功！
任务 ID: #126
类型: publish
状态: 运行中

系统将自动执行以下 Agent：
1. 选品分析
2. 价格优化
3. 内容生成
4. 图片生成
5. 内容审核
6. 发布上架

预计耗时: 2-3 分钟
```

### 2.4 通知推送示例

#### 任务成功通知

```
┌─────────────────────────────────┐
│ ✅ 任务成功                      │
├─────────────────────────────────┤
│ 产品已成功上架到淘宝             │
│                                 │
│ 任务ID: #123                     │
│ 产品名称: 无线蓝牙耳机           │
│ 上架平台: 淘宝                   │
│ 执行时间: 2.5 分钟               │
│ 完成时间: 2026-03-18 10:23:45   │
└─────────────────────────────────┘
```

#### 任务失败通知

```
┌─────────────────────────────────┐
│ ❌ 任务失败                      │
├─────────────────────────────────┤
│ 图片生成超时，请检查 AI 服务     │
│                                 │
│ 任务ID: #124                     │
│ 失败阶段: image_generation       │
│ 错误信息: AI service timeout     │
│ 失败时间: 2026-03-18 10:25:30   │
│                                 │
│ [重试任务] [查看日志]            │
└─────────────────────────────────┘
```

#### Bug 反馈通知

```
┌─────────────────────────────────┐
│ 🐛 新的 Bug 反馈                 │
├─────────────────────────────────┤
│ 用户 张三 提交了新的反馈         │
│                                 │
│ 反馈ID: #42                      │
│ 标题: 任务列表页面加载缓慢       │
│ 提交人: 张三                     │
│ 优先级: 高                       │
│                                 │
│ [查看详情] [标记已读]            │
└─────────────────────────────────┘
```

---

## 3. Telegram Bot 接入

### 3.1 配置步骤

#### 步骤 1：创建 Telegram Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取 `Bot Token`（格式：`123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`）

#### 步骤 2：获取 Chat ID

1. 将机器人添加到群组或私聊
2. 发送任意消息
3. 访问 `https://api.telegram.org/bot<YourBOTToken>/getUpdates`
4. 在返回的 JSON 中找到 `chat.id`

#### 步骤 3：配置环境变量

编辑 `backend/.env` 文件：

```bash
# Telegram 配置
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
```

#### 步骤 4：重启服务

```bash
cd backend
python run.py
```

### 3.2 通知示例

#### 任务成功通知

```
✅ 任务成功

产品已成功上架到淘宝

任务ID: #123
产品名称: 无线蓝牙耳机
上架平台: 淘宝
执行时间: 2.5 分钟
完成时间: 2026-03-18 10:23:45
```

#### 任务失败通知

```
❌ 任务失败

图片生成超时，请检查 AI 服务

任务ID: #124
失败阶段: image_generation
错误信息: AI service timeout
失败时间: 2026-03-18 10:25:30
```

---

## 4. 企业微信接入

### 4.1 配置步骤

#### 步骤 1：创建企业微信应用

1. 访问 [企业微信管理后台](https://work.weixin.qq.com/)
2. 创建自建应用
3. 获取 `Corp ID` 和 `Agent Secret`

#### 步骤 2：配置 Webhook

1. 在应用管理中配置群机器人
2. 获取 Webhook URL

#### 步骤 3：配置环境变量

编辑 `backend/.env` 文件：

```bash
# 企业微信配置
WECHAT_CORP_ID=your_corp_id
WECHAT_AGENT_SECRET=your_agent_secret
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
```

### 4.2 通知示例

```
**✅ 任务成功**

产品已成功上架到淘宝

> 任务ID: #123
> 产品名称: 无线蓝牙耳机
> 上架平台: 淘宝
> 执行时间: 2.5 分钟
```

---

## 5. 实际使用场景

### 场景 1：运营人员移动办公

**背景：** 运营人员在地铁上，需要快速上架新产品

**操作流程：**

```
1. 打开飞书，发送 "/products"
   → 查看最新导入的产品列表

2. 发送 "/create"
   → 选择"发布上架"
   → 选择产品 ID

3. 系统自动执行 6 个 Agent
   → 选品分析
   → 价格优化
   → 内容生成
   → 图片生成
   → 内容审核
   → 发布上架

4. 2 分钟后，飞书推送通知
   → "✅ 任务成功，产品已上架到淘宝"

5. 点击通知查看详情
   → 产品链接、上架时间、执行日志
```

**优势：**
- ✅ 无需打开电脑或网页
- ✅ 2 分钟完成原本需要 2 小时的工作
- ✅ 实时接收任务进度通知

### 场景 2：开发人员监控系统

**背景：** 开发人员在家休息，系统出现异常

**操作流程：**

```
1. Telegram 收到通知
   → "❌ 任务失败，图片生成超时"

2. 点击通知查看详情
   → 任务 ID: #124
   → 失败阶段: image_generation
   → 错误信息: AI service timeout

3. 在 Telegram 中发送 "/tasks"
   → 查看最近的任务列表
   → 发现多个任务都在图片生成阶段失败

4. 判断是 AI 服务问题
   → 立即登录服务器检查
   → 发现 Midjourney API 配额用完

5. 处理完成后，Telegram 推送
   → "✅ 系统恢复正常"
```

**优势：**
- ✅ 第一时间发现问题
- ✅ 无需登录系统即可查看任务状态
- ✅ 快速定位问题根源

### 场景 3：团队协作

**背景：** 产品团队在飞书群讨论新产品上架策略

**操作流程：**

```
1. 产品经理在飞书群发送 "/create"
   → 选择"选品分析"
   → 输入产品信息：无线蓝牙耳机

2. 系统自动分析
   → 市场趋势：蓝牙耳机市场增长 15%
   → 竞品价格：平均 299-599 元
   → 热门关键词：降噪、长续航、运动防水
   → 目标人群：25-35 岁年轻人

3. 2 分钟后，飞书群推送分析结果
   → 团队成员直接在群里讨论

4. 产品经理：建议定价 399 元
   运营经理：同意，首发 8 折促销
   设计师：主打降噪和长续航卖点

5. 决策后，产品经理发送 "/create"
   → 选择"发布上架"
   → 系统自动执行完整流程

6. 3 分钟后，飞书群推送
   → "✅ 产品已上架到淘宝、京东、拼多多"
   → 附带产品链接和预览图
```

**优势：**
- ✅ 团队实时协作，无需切换工具
- ✅ 决策过程透明，所有人都能看到
- ✅ 从分析到上架，全程在聊天软件完成

### 场景 4：自动化监控告警

**背景：** 系统自动监控任务执行情况

**自动推送规则：**

```
✅ 任务成功（可配置是否推送）
   → 默认：不推送
   → 可选：推送到指定群组

❌ 任务失败（自动推送）
   → 推送到运维群
   → @相关负责人

⏰ 任务超时（自动推送）
   → 推送到运维群
   → 附带任务详情和日志

🐛 Bug 反馈（自动推送）
   → 推送到开发群
   → 附带反馈详情和截图
```

**配置方式：**

在系统设置中配置通知规则：

```json
{
  "notification_enabled": true,
  "notification_on_success": false,
  "notification_on_error": true,
  "notification_on_timeout": true,
  "default_channel": "lark",
  "channels": {
    "lark": {
      "webhook_url": "https://open.feishu.cn/...",
      "chat_id": "oc_xxx"
    },
    "telegram": {
      "bot_token": "123456:ABC-DEF",
      "chat_id": "123456789"
    }
  }
}
```

---

## 6. 代码实现

### 6.1 飞书渠道实现

**文件位置：** `backend/app/channels/lark.py`

**核心方法：**

```python
class LarkChannel(ChannelBase):
    """飞书渠道"""

    async def send_message(
        self,
        user_id: str,
        message: str,
        message_type: MessageType = MessageType.TEXT
    ) -> bool:
        """发送消息"""
        token = await self.get_access_token()
        url = f"{self.base_url}/im/v1/messages"

        data = {
            "receive_id": user_id,
            "msg_type": message_type.value,
            "content": json.dumps({"text": message})
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers={
                "Authorization": f"Bearer {token}"
            })
            return response.json().get('code') == 0

    async def send_card(
        self,
        user_id: str,
        title: str,
        content: str,
        buttons: Optional[List[Dict[str, str]]] = None
    ) -> bool:
        """发送卡片消息"""
        card = {
            "header": {"title": {"content": title}},
            "elements": [
                {"tag": "div", "text": {"content": content}}
            ]
        }

        if buttons:
            card['elements'].append({
                "tag": "action",
                "actions": [
                    {"tag": "button", "text": {"content": btn['text']}}
                    for btn in buttons
                ]
            })

        return await self.send_message(
            user_id, "", MessageType.INTERACTIVE, {"card": card}
        )

    async def handle_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理接收到的消息"""
        event = message_data.get('event', {})
        message = event.get('message', {})
        content = json.loads(message.get('content', '{}'))
        text = content.get('text', '').strip()

        # 命令路由
        if text.startswith('/help'):
            await self._send_help(user_id)
        elif text.startswith('/products'):
            await self._send_products(user_id)
        elif text.startswith('/tasks'):
            await self._send_tasks(user_id)
        elif text.startswith('/create'):
            await self._send_create_task_card(user_id)

        return {"success": True}
```

### 6.2 通知服务实现

**文件位置：** `backend/app/services/notification.py`

**核心方法：**

```python
class NotificationManager:
    """通知管理器"""

    @staticmethod
    async def notify_task_status(
        db,
        task_id: int,
        status: str,
        message: str,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        """任务状态变更通知"""

        # 检查是否启用通知
        config = await db.execute(
            select(SystemConfig).where(
                SystemConfig.config_key == "notification_enabled"
            )
        )
        if not config or config.config_value != "true":
            return

        # 获取默认通知渠道
        channel = await db.execute(
            select(Channel).where(
                Channel.channel_type == ChannelType.NOTIFICATION,
                Channel.status == ChannelStatus.ACTIVE,
                Channel.is_default == True
            )
        )

        if not channel:
            return

        # 构建通知标题
        status_map = {
            "success": "✅ 任务成功",
            "failed": "❌ 任务失败",
            "timeout": "⏰ 任务超时",
        }
        title = status_map.get(status, "📢 任务通知")

        # 发送通知
        await NotificationService.send_notification(
            channel=channel,
            title=title,
            content=message,
            extra_data=extra_data or {}
        )
```

### 6.3 Webhook 接口

**文件位置：** `backend/app/api/webhooks/lark.py`

```python
@router.post("/lark")
async def lark_webhook(request: Request):
    """飞书 Webhook 接口"""

    # 解析请求数据
    data = await request.json()

    # URL 验证
    if 'challenge' in data:
        return {"challenge": data['challenge']}

    # 验证签名
    channel = channel_manager.get_channel('lark')
    if not await channel.verify_webhook(data):
        raise HTTPException(status_code=401, detail="验证失败")

    # 处理消息
    result = await channel.handle_message(data)

    return {"success": True}
```

---

## 7. 配置管理

### 7.1 系统配置

在系统设置页面配置通知规则：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `notification_enabled` | 是否启用通知 | `true` |
| `notification_on_success` | 任务成功时推送 | `false` |
| `notification_on_error` | 任务失败时推送 | `true` |
| `notification_on_timeout` | 任务超时时推送 | `true` |
| `default_channel` | 默认通知渠道 | `lark` |

### 7.2 渠道配置

在渠道管理页面添加和配置渠道：

**飞书渠道配置：**
```json
{
  "name": "飞书运维群",
  "platform": "lark",
  "channel_type": "notification",
  "config": {
    "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    "app_id": "cli_xxx",
    "app_secret": "xxx"
  },
  "is_default": true,
  "status": "active"
}
```

**Telegram 渠道配置：**
```json
{
  "name": "Telegram 告警",
  "platform": "telegram",
  "channel_type": "notification",
  "config": {
    "bot_token": "123456:ABC-DEF",
    "chat_id": "123456789"
  },
  "is_default": false,
  "status": "active"
}
```

---

## 8. 常见问题

### 8.1 飞书机器人收不到消息

**问题：** 配置完成后，飞书机器人无法收到消息

**解决方案：**

1. 检查应用权限是否正确配置
2. 确认 Webhook URL 是否可访问
3. 查看后端日志：`tail -f backend/logs/app.log`
4. 测试连接：`POST /api/v1/channels/{id}/test`

### 8.2 Telegram 通知发送失败

**问题：** Telegram 通知无法发送

**解决方案：**

1. 确认 Bot Token 是否正确
2. 确认 Chat ID 是否正确
3. 检查网络是否可访问 Telegram API
4. 查看错误日志：`grep "Telegram" backend/logs/app.log`

### 8.3 通知延迟

**问题：** 通知推送有延迟

**解决方案：**

1. 检查 Celery Worker 是否正常运行
2. 检查 Redis 连接是否正常
3. 查看任务队列积压情况：`celery -A app.workers.celery_app inspect active`

---

## 9. 相关文档

- [渠道配置模块](./04-channel-config.md) - 渠道管理界面
- [多渠道接入设计](../architecture/03-multi-channel.md) - 渠道架构设计
- [任务调度模块](./02-task-scheduling.md) - 任务系统设计
- [数据模型设计](../database/01-data-model.md) - channels 表结构

---

## 10. 附录

### 10.1 飞书 API 文档

- [飞书开放平台](https://open.feishu.cn/document/)
- [消息发送 API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create)
- [事件订阅](https://open.feishu.cn/document/ukTMukTMukTM/uUTNz4SN1MjL1UzM)

### 10.2 Telegram Bot API 文档

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [sendMessage](https://core.telegram.org/bots/api#sendmessage)
- [getUpdates](https://core.telegram.org/bots/api#getupdates)

### 10.3 企业微信 API 文档

- [企业微信 API](https://developer.work.weixin.qq.com/document/)
- [群机器人配置](https://developer.work.weixin.qq.com/document/path/91770)
- [消息发送](https://developer.work.weixin.qq.com/document/path/90236)
