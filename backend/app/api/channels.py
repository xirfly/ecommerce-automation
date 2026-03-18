"""
多渠道 Webhook API
"""
from fastapi import APIRouter, Request, HTTPException, status
from app.channels.manager import channel_manager
from app.core.logging_config import setup_logging

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = setup_logging()


@router.post("/lark")
async def lark_webhook(request: Request):
    """
    飞书 Webhook 回调

    接收飞书发送的事件消息
    """
    try:
        data = await request.json()
        logger.info(f"[Webhook] 收到飞书消息: {data.get('header', {}).get('event_type')}")

        # 获取飞书渠道
        lark = channel_manager.get_channel('lark')
        if not lark:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="飞书渠道未配置"
            )

        # URL 验证
        if 'challenge' in data:
            logger.info("[Webhook] 飞书 URL 验证")
            return {"challenge": data['challenge']}

        # 验证请求
        if not await lark.verify_webhook(data):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="验证失败"
            )

        # 处理消息
        result = await lark.handle_message(data)

        return {"success": True, "data": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Webhook] 处理飞书消息失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/telegram")
async def telegram_webhook(request: Request):
    """
    Telegram Webhook 回调

    接收 Telegram Bot 发送的消息
    """
    # TODO: 实现 Telegram Webhook
    return {"message": "Telegram webhook - 待实现"}


@router.post("/wecom")
async def wecom_webhook(request: Request):
    """
    企业微信 Webhook 回调

    接收企业微信发送的消息
    """
    # TODO: 实现企业微信 Webhook
    return {"message": "企业微信 webhook - 待实现"}


@router.get("/channels")
async def list_channels():
    """
    列出所有可用渠道

    返回已配置的渠道列表
    """
    channels = channel_manager.list_channels()
    return {
        "channels": channels,
        "count": len(channels)
    }
