"""
飞书（Lark）渠道实现
"""
import httpx
import hashlib
import json
from typing import Dict, Any, Optional, List
from app.channels.base import ChannelBase, MessageType
from app.core.logging_config import setup_logging

logger = setup_logging()


class LarkChannel(ChannelBase):
    """飞书渠道"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config.get('app_id')
        self.app_secret = config.get('app_secret')
        self.verification_token = config.get('verification_token')
        self.encrypt_key = config.get('encrypt_key')
        self.base_url = "https://open.feishu.cn/open-apis"
        self._access_token = None
        self._token_expires_at = 0

    async def get_access_token(self) -> str:
        """获取访问令牌"""
        import time

        # 检查 token 是否过期
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        # 获取新 token
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            result = response.json()

            if result.get('code') == 0:
                self._access_token = result['tenant_access_token']
                self._token_expires_at = time.time() + result.get('expire', 7200) - 300  # 提前5分钟刷新
                logger.info("[Lark] 获取访问令牌成功")
                return self._access_token
            else:
                logger.error(f"[Lark] 获取访问令牌失败: {result}")
                raise Exception(f"获取飞书访问令牌失败: {result.get('msg')}")

    async def send_message(
        self,
        user_id: str,
        message: str,
        message_type: MessageType = MessageType.TEXT,
        extra: Optional[Dict[str, Any]] = None
    ) -> bool:
        """发送消息"""
        try:
            token = await self.get_access_token()
            url = f"{self.base_url}/im/v1/messages"

            # 构建消息内容
            if message_type == MessageType.TEXT:
                content = {"text": message}
            else:
                content = extra or {}

            data = {
                "receive_id": user_id,
                "msg_type": message_type.value,
                "content": json.dumps(content)
            }

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            params = {"receive_id_type": "open_id"}

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers, params=params)
                result = response.json()

                if result.get('code') == 0:
                    logger.info(f"[Lark] 发送消息成功: {user_id}")
                    return True
                else:
                    logger.error(f"[Lark] 发送消息失败: {result}")
                    return False

        except Exception as e:
            logger.error(f"[Lark] 发送消息异常: {e}")
            return False

    async def send_card(
        self,
        user_id: str,
        title: str,
        content: str,
        buttons: Optional[List[Dict[str, str]]] = None
    ) -> bool:
        """发送卡片消息"""
        try:
            # 构建飞书卡片
            card = {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "plain_text",
                            "content": content
                        }
                    }
                ]
            }

            # 添加按钮
            if buttons:
                actions = []
                for button in buttons:
                    actions.append({
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": button.get('text', '')
                        },
                        "type": button.get('type', 'default'),
                        "value": button.get('value', {})
                    })

                card['elements'].append({
                    "tag": "action",
                    "actions": actions
                })

            return await self.send_message(
                user_id=user_id,
                message="",
                message_type=MessageType.INTERACTIVE,
                extra={"card": card}
            )

        except Exception as e:
            logger.error(f"[Lark] 发送卡片消息异常: {e}")
            return False

    async def handle_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理接收到的消息"""
        try:
            # 解析消息
            event = message_data.get('event', {})
            message = event.get('message', {})
            sender = event.get('sender', {})

            user_id = sender.get('sender_id', {}).get('open_id')
            msg_type = message.get('message_type')
            content = json.loads(message.get('content', '{}'))

            logger.info(f"[Lark] 收到消息: user={user_id}, type={msg_type}")

            # 处理文本消息
            if msg_type == 'text':
                text = content.get('text', '').strip()
                return await self._handle_text_command(user_id, text)

            return {"success": True}

        except Exception as e:
            logger.error(f"[Lark] 处理消息异常: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_text_command(self, user_id: str, text: str) -> Dict[str, Any]:
        """处理文本命令"""
        # 命令路由
        if text.startswith('/help') or text == '帮助':
            await self._send_help(user_id)
        elif text.startswith('/products') or text == '产品列表':
            await self._send_products(user_id)
        elif text.startswith('/tasks') or text == '任务列表':
            await self._send_tasks(user_id)
        elif text.startswith('/create') or text.startswith('创建任务'):
            await self._send_create_task_card(user_id)
        else:
            await self.send_message(user_id, "未知命令，发送 /help 查看帮助")

        return {"success": True}

    async def _send_help(self, user_id: str):
        """发送帮助信息"""
        help_text = """
📖 电商自动化系统 - 命令帮助

🔹 /help 或 帮助 - 显示此帮助信息
🔹 /products 或 产品列表 - 查看产品列表
🔹 /tasks 或 任务列表 - 查看任务列表
🔹 /create 或 创建任务 - 创建新任务

💡 提示：点击下方按钮快速操作
        """
        await self.send_card(
            user_id=user_id,
            title="命令帮助",
            content=help_text.strip(),
            buttons=[
                {"text": "产品列表", "value": {"cmd": "products"}},
                {"text": "任务列表", "value": {"cmd": "tasks"}},
                {"text": "创建任务", "value": {"cmd": "create"}, "type": "primary"}
            ]
        )

    async def _send_products(self, user_id: str):
        """发送产品列表"""
        from app.database import AsyncSessionLocal
        from app.models import Product
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Product).limit(10))
            products = result.scalars().all()

            if not products:
                await self.send_message(user_id, "暂无产品")
                return

            content = "📦 产品列表（最近10个）\n\n"
            for product in products:
                content += f"• {product.name}\n"
                content += f"  分类: {product.category} | 价格: ¥{product.price}\n\n"

            await self.send_card(
                user_id=user_id,
                title="产品列表",
                content=content.strip()
            )

    async def _send_tasks(self, user_id: str):
        """发送任务列表"""
        from app.database import AsyncSessionLocal
        from app.models import Task
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Task).order_by(Task.created_at.desc()).limit(10))
            tasks = result.scalars().all()

            if not tasks:
                await self.send_message(user_id, "暂无任务")
                return

            content = "📋 任务列表（最近10个）\n\n"
            status_emoji = {
                'pending': '⏳',
                'running': '🔄',
                'success': '✅',
                'failed': '❌',
                'timeout': '⏰'
            }

            for task in tasks:
                emoji = status_emoji.get(task.status.value, '❓')
                content += f"{emoji} 任务 #{task.id}\n"
                content += f"  类型: {task.task_type} | 进度: {task.progress}%\n\n"

            await self.send_card(
                user_id=user_id,
                title="任务列表",
                content=content.strip()
            )

    async def _send_create_task_card(self, user_id: str):
        """发送创建任务卡片"""
        content = """
请选择要创建的任务类型：

• 选品分析 - 分析产品市场趋势
• 内容生成 - 生成产品营销文案
• 图片生成 - 生成产品图片
• 视频生成 - 生成产品视频
• 内容审核 - 审核产品内容
• 发布上架 - 发布产品到平台
        """
        await self.send_card(
            user_id=user_id,
            title="创建任务",
            content=content.strip(),
            buttons=[
                {"text": "选品分析", "value": {"cmd": "create_task", "type": "product_analysis"}},
                {"text": "内容生成", "value": {"cmd": "create_task", "type": "content_generation"}},
                {"text": "内容审核", "value": {"cmd": "create_task", "type": "review"}}
            ]
        )

    async def verify_webhook(self, request_data: Dict[str, Any]) -> bool:
        """验证 Webhook 请求"""
        try:
            # URL 验证
            if 'challenge' in request_data:
                return True

            # 事件验证
            token = request_data.get('header', {}).get('token')
            if token == self.verification_token:
                return True

            logger.warning(f"[Lark] Webhook 验证失败: token不匹配")
            return False

        except Exception as e:
            logger.error(f"[Lark] Webhook 验证异常: {e}")
            return False
