"""
渠道基类
定义统一的消息处理接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum


class MessageType(Enum):
    """消息类型"""
    TEXT = "text"
    IMAGE = "image"
    CARD = "card"
    INTERACTIVE = "interactive"


class ChannelBase(ABC):
    """渠道基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def send_message(
        self,
        user_id: str,
        message: str,
        message_type: MessageType = MessageType.TEXT,
        extra: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        发送消息

        Args:
            user_id: 用户ID
            message: 消息内容
            message_type: 消息类型
            extra: 额外参数

        Returns:
            是否发送成功
        """
        pass

    @abstractmethod
    async def send_card(
        self,
        user_id: str,
        title: str,
        content: str,
        buttons: Optional[List[Dict[str, str]]] = None
    ) -> bool:
        """
        发送卡片消息

        Args:
            user_id: 用户ID
            title: 卡片标题
            content: 卡片内容
            buttons: 按钮列表

        Returns:
            是否发送成功
        """
        pass

    @abstractmethod
    async def handle_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理接收到的消息

        Args:
            message_data: 消息数据

        Returns:
            处理结果
        """
        pass

    @abstractmethod
    async def verify_webhook(self, request_data: Dict[str, Any]) -> bool:
        """
        验证 Webhook 请求

        Args:
            request_data: 请求数据

        Returns:
            是否验证通过
        """
        pass
