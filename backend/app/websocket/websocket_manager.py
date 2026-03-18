"""
WebSocket 连接管理器
"""
from fastapi import WebSocket
from typing import Dict, Set
from app.core.logging_config import setup_logging
import json
import asyncio

logger = setup_logging()


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 存储所有活跃的连接：{user_id: Set[WebSocket]}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # 存储连接到用户的映射：{WebSocket: user_id}
        self.connection_to_user: Dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """接受新的 WebSocket 连接"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        self.connection_to_user[websocket] = user_id

        logger.info(f"用户 {user_id} 建立 WebSocket 连接，当前连接数: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket):
        """断开 WebSocket 连接"""
        user_id = self.connection_to_user.get(websocket)

        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # 如果该用户没有其他连接了，删除该用户的记录
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        if websocket in self.connection_to_user:
            del self.connection_to_user[websocket]

        logger.info(f"用户 {user_id} 断开 WebSocket 连接")

    async def send_personal_message(self, message: dict, user_id: int):
        """发送消息给特定用户的所有连接"""
        if user_id in self.active_connections:
            disconnected = set()

            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"发送消息失败: {e}")
                    disconnected.add(connection)

            # 清理断开的连接
            for connection in disconnected:
                self.disconnect(connection)

    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)

    async def send_task_update(self, task_data: dict, user_id: int):
        """发送任务更新消息"""
        message = {
            "type": "task_update",
            "data": task_data
        }
        await self.send_personal_message(message, user_id)
        logger.debug(f"已向用户 {user_id} 发送任务更新")

    async def send_notification(self, title: str, content: str, user_id: int, level: str = "info"):
        """发送通知消息"""
        message = {
            "type": "notification",
            "data": {
                "title": title,
                "content": content,
                "level": level,
                "timestamp": asyncio.get_event_loop().time()
            }
        }
        await self.send_personal_message(message, user_id)
        logger.debug(f"已向用户 {user_id} 发送通知: {content}")


# 全局 WebSocket 管理器实例
manager = ConnectionManager()
