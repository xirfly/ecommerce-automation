"""
通知服务
支持多种通知渠道：飞书、Telegram、企业微信等
"""
import httpx
import json
from typing import Dict, Any, Optional
from app.models.channel import Channel, ChannelType
from app.core.logging_config import setup_logging

logger = setup_logging()


class NotificationService:
    """通知服务"""

    @staticmethod
    async def send_notification(
        channel: Channel,
        title: str,
        content: str,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        发送通知

        Args:
            channel: 通知渠道
            title: 通知标题
            content: 通知内容
            extra_data: 额外数据

        Returns:
            是否发送成功
        """
        if channel.channel_type != ChannelType.NOTIFICATION:
            logger.error(f"渠道 {channel.name} 不是通知渠道")
            return False

        try:
            if channel.platform == "lark":
                return await NotificationService._send_lark(channel, title, content, extra_data)
            elif channel.platform == "telegram":
                return await NotificationService._send_telegram(channel, title, content, extra_data)
            elif channel.platform == "wechat":
                return await NotificationService._send_wechat(channel, title, content, extra_data)
            else:
                logger.error(f"不支持的通知平台: {channel.platform}")
                return False
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}", exc_info=True)
            return False

    @staticmethod
    async def _send_lark(
        channel: Channel,
        title: str,
        content: str,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """发送飞书通知"""
        config = channel.config
        webhook_url = config.get("webhook_url")

        if not webhook_url:
            logger.error("飞书 Webhook URL 未配置")
            return False

        # 构建飞书消息卡片
        message = {
            "msg_type": "interactive",
            "card": {
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
                            "tag": "lark_md",
                            "content": content
                        }
                    }
                ]
            }
        }

        # 添加额外字段
        if extra_data:
            fields = []
            for key, value in extra_data.items():
                fields.append({
                    "is_short": True,
                    "text": {
                        "tag": "lark_md",
                        "content": f"**{key}**\n{value}"
                    }
                })
            if fields:
                message["card"]["elements"].append({
                    "tag": "div",
                    "fields": fields
                })

        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=message,
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.info(f"飞书通知发送成功: {title}")
                    return True
                else:
                    logger.error(f"飞书通知发送失败: {result.get('msg')}")
                    return False
            else:
                logger.error(f"飞书通知发送失败: HTTP {response.status_code}")
                return False

    @staticmethod
    async def _send_telegram(
        channel: Channel,
        title: str,
        content: str,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """发送 Telegram 通知"""
        config = channel.config
        bot_token = config.get("bot_token")
        chat_id = config.get("chat_id")

        if not bot_token or not chat_id:
            logger.error("Telegram Bot Token 或 Chat ID 未配置")
            return False

        # 构建消息
        message_text = f"<b>{title}</b>\n\n{content}"

        if extra_data:
            message_text += "\n\n"
            for key, value in extra_data.items():
                message_text += f"<b>{key}:</b> {value}\n"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message_text,
            "parse_mode": "HTML"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)

            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    logger.info(f"Telegram 通知发送成功: {title}")
                    return True
                else:
                    logger.error(f"Telegram 通知发送失败: {result.get('description')}")
                    return False
            else:
                logger.error(f"Telegram 通知发送失败: HTTP {response.status_code}")
                return False

    @staticmethod
    async def _send_wechat(
        channel: Channel,
        title: str,
        content: str,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """发送企业微信通知"""
        config = channel.config
        webhook_url = config.get("webhook_url")

        if not webhook_url:
            logger.error("企业微信 Webhook URL 未配置")
            return False

        # 构建企业微信消息
        message_content = f"**{title}**\n\n{content}"

        if extra_data:
            message_content += "\n\n"
            for key, value in extra_data.items():
                message_content += f"> {key}: {value}\n"

        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": message_content
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=message,
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("errcode") == 0:
                    logger.info(f"企业微信通知发送成功: {title}")
                    return True
                else:
                    logger.error(f"企业微信通知发送失败: {result.get('errmsg')}")
                    return False
            else:
                logger.error(f"企业微信通知发送失败: HTTP {response.status_code}")
                return False


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
        """
        任务状态变更通知

        Args:
            db: 数据库会话
            task_id: 任务ID
            status: 任务状态
            message: 通知消息
            extra_data: 额外数据
        """
        from sqlalchemy import select
        from app.models.channel import Channel, ChannelStatus
        from app.models.system_config import SystemConfig

        # 检查是否启用通知
        config_query = select(SystemConfig).where(
            SystemConfig.config_key == "notification_enabled"
        )
        config_result = await db.execute(config_query)
        config = config_result.scalar_one_or_none()

        if not config or config.config_value != "true":
            return

        # 根据状态判断是否需要通知
        if status == "success":
            config_query = select(SystemConfig).where(
                SystemConfig.config_key == "notification_on_success"
            )
            config_result = await db.execute(config_query)
            config = config_result.scalar_one_or_none()
            if not config or config.config_value != "true":
                return
        elif status in ["failed", "timeout"]:
            config_query = select(SystemConfig).where(
                SystemConfig.config_key == "notification_on_error"
            )
            config_result = await db.execute(config_query)
            config = config_result.scalar_one_or_none()
            if not config or config.config_value != "true":
                return

        # 获取默认通知渠道
        channel_query = select(Channel).where(
            Channel.channel_type == ChannelType.NOTIFICATION,
            Channel.status == ChannelStatus.ACTIVE,
            Channel.is_default == True
        )
        channel_result = await db.execute(channel_query)
        channel = channel_result.scalar_one_or_none()

        if not channel:
            logger.warning("未找到默认通知渠道")
            return

        # 构建通知标题
        status_map = {
            "success": "✅ 任务成功",
            "failed": "❌ 任务失败",
            "timeout": "⏰ 任务超时",
            "running": "🔄 任务运行中",
        }
        title = status_map.get(status, "📢 任务通知")

        # 发送通知
        await NotificationService.send_notification(
            channel=channel,
            title=title,
            content=message,
            extra_data=extra_data or {}
        )

    @staticmethod
    async def notify_feedback_submitted(
        db,
        feedback_id: int,
        title: str,
        username: str
    ):
        """
        反馈提交通知

        Args:
            db: 数据库会话
            feedback_id: 反馈ID
            title: 反馈标题
            username: 提交人
        """
        from sqlalchemy import select
        from app.models.channel import Channel, ChannelStatus

        # 获取默认通知渠道
        channel_query = select(Channel).where(
            Channel.channel_type == ChannelType.NOTIFICATION,
            Channel.status == ChannelStatus.ACTIVE,
            Channel.is_default == True
        )
        channel_result = await db.execute(channel_query)
        channel = channel_result.scalar_one_or_none()

        if not channel:
            return

        # 发送通知
        await NotificationService.send_notification(
            channel=channel,
            title="🐛 新的 Bug 反馈",
            content=f"用户 **{username}** 提交了新的反馈",
            extra_data={
                "反馈ID": f"#{feedback_id}",
                "标题": title,
                "提交人": username,
            }
        )
