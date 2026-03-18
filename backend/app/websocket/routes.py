"""
WebSocket API 路由
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.websocket_manager import manager
from app.core.logging_config import setup_logging
import json

router = APIRouter(tags=["WebSocket"])
logger = setup_logging()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT Token"),
):
    """
    WebSocket 连接端点

    客户端需要在 URL 中传递 token 参数进行认证
    例如: ws://localhost:8000/ws?token=your_jwt_token
    """
    logger.info("[WebSocket] 收到连接请求")

    # 验证 token 并获取用户信息
    try:
        from app.utils.auth import verify_token
        logger.debug("[WebSocket] 开始验证 token")
        payload = await verify_token(token)
        user_id = int(payload.get("sub"))
        logger.info(f"[WebSocket] Token 验证成功，用户 ID: {user_id}")
    except Exception as e:
        logger.error(f"[WebSocket] Token 验证失败: {e}")
        # 必须先 accept 才能 close
        await websocket.accept()
        await websocket.close(code=1008, reason="认证失败")
        return

    # 建立连接
    logger.debug("[WebSocket] 准备建立连接")
    await manager.connect(websocket, user_id)
    logger.info(f"[WebSocket] 用户 {user_id} 连接已建立")

    try:
        # 发送欢迎消息
        logger.debug("[WebSocket] 发送欢迎消息")
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket 连接成功",
            "user_id": user_id
        })
        logger.debug("[WebSocket] 欢迎消息已发送")

        # 保持连接并接收消息
        while True:
            try:
                # 接收客户端消息
                data = await websocket.receive_text()
                logger.debug(f"[WebSocket] 收到消息: {data[:100]}")

                try:
                    message = json.loads(data)
                    message_type = message.get("type")

                    # 处理心跳消息
                    if message_type == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": message.get("timestamp")
                        })
                        logger.debug(f"[WebSocket] 已响应心跳")

                    # 处理其他类型的消息
                    elif message_type == "subscribe":
                        # 订阅特定资源的更新
                        resource = message.get("resource")
                        await websocket.send_json({
                            "type": "subscribed",
                            "resource": resource
                        })
                        logger.info(f"[WebSocket] 用户 {user_id} 已订阅资源: {resource}")

                except json.JSONDecodeError as e:
                    logger.warning(f"[WebSocket] JSON 解析错误: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "无效的 JSON 格式"
                    })

            except Exception as e:
                logger.error(f"[WebSocket] 接收消息时出错: {e}")
                raise

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"[WebSocket] 用户 {user_id} 主动断开连接")
    except Exception as e:
        manager.disconnect(websocket)
        logger.error(f"[WebSocket] 连接异常: {type(e).__name__}: {e}", exc_info=True)
