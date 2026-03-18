"""
AlertManager Webhook 接收端点
"""
from fastapi import APIRouter, Request, Header
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.channel import Channel, ChannelType, ChannelStatus
from app.services.notification import NotificationService
from app.core.logging_config import setup_logging

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
logger = setup_logging()


@router.post("/alertmanager")
async def alertmanager_webhook(
    request: Request,
    x_alert_priority: Optional[str] = Header(None),
):
    """
    接收 AlertManager 告警 Webhook
    """
    try:
        # 解析告警数据
        alert_data = await request.json()

        # 获取告警列表
        alerts = alert_data.get("alerts", [])

        if not alerts:
            return {"status": "ok", "message": "No alerts to process"}

        # 处理每个告警
        for alert in alerts:
            status = alert.get("status")  # firing 或 resolved
            labels = alert.get("labels", {})
            annotations = alert.get("annotations", {})

            # 构建告警消息
            severity = labels.get("severity", "info")
            category = labels.get("category", "unknown")
            alert_name = labels.get("alertname", "Unknown Alert")
            summary = annotations.get("summary", "")
            description = annotations.get("description", "")

            # 确定告警标题
            if status == "firing":
                title = f"🚨 告警触发: {alert_name}"
                emoji = "🔥" if severity == "critical" else "⚠️" if severity == "warning" else "ℹ️"
            else:
                title = f"✅ 告警恢复: {alert_name}"
                emoji = "✅"

            # 构建消息内容
            content = f"{emoji} **{summary}**\n\n{description}"

            # 额外数据
            extra_data = {
                "严重程度": severity.upper(),
                "类别": category,
                "状态": "触发" if status == "firing" else "已恢复",
            }

            # 发送通知
            await send_alert_notification(
                title=title,
                content=content,
                extra_data=extra_data,
                severity=severity
            )

        return {"status": "ok", "message": f"Processed {len(alerts)} alerts"}

    except Exception as e:
        logger.error(f"处理 AlertManager Webhook 失败: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def send_alert_notification(
    title: str,
    content: str,
    extra_data: dict,
    severity: str
):
    """
    发送告警通知到配置的通知渠道
    """
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        # 获取默认通知渠道
        channel_query = select(Channel).where(
            Channel.channel_type == ChannelType.NOTIFICATION,
            Channel.status == ChannelStatus.ACTIVE,
            Channel.is_default == True
        )
        channel_result = await db.execute(channel_query)
        channel = channel_result.scalar_one_or_none()

        if not channel:
            logger.warning("未找到默认通知渠道，无法发送告警通知")
            return

        # 发送通知
        try:
            await NotificationService.send_notification(
                channel=channel,
                title=title,
                content=content,
                extra_data=extra_data
            )
            logger.info(f"告警通知已发送: {title}")
        except Exception as e:
            logger.error(f"发送告警通知失败: {e}", exc_info=True)
