"""
渠道管理器
统一管理所有渠道实例
"""
from typing import Dict, Optional
from app.channels.base import ChannelBase
from app.channels.lark import LarkChannel
from app.core.config import settings
from app.core.logging_config import setup_logging

logger = setup_logging()


class ChannelManager:
    """渠道管理器"""

    def __init__(self):
        self._channels: Dict[str, ChannelBase] = {}
        self._initialize_channels()

    def _initialize_channels(self):
        """初始化所有渠道"""
        # 初始化飞书渠道
        if settings.FEISHU_APP_ID and settings.FEISHU_APP_SECRET:
            try:
                self._channels['lark'] = LarkChannel({
                    'app_id': settings.FEISHU_APP_ID,
                    'app_secret': settings.FEISHU_APP_SECRET,
                    'verification_token': settings.FEISHU_VERIFICATION_TOKEN,
                    'encrypt_key': settings.FEISHU_ENCRYPT_KEY,
                })
                logger.info("[ChannelManager] 飞书渠道初始化成功")
            except Exception as e:
                logger.error(f"[ChannelManager] 飞书渠道初始化失败: {e}")

        # TODO: 初始化其他渠道（Telegram、企业微信等）

    def get_channel(self, channel_name: str) -> Optional[ChannelBase]:
        """获取渠道实例"""
        return self._channels.get(channel_name)

    def list_channels(self) -> list:
        """列出所有可用渠道"""
        return list(self._channels.keys())


# 全局渠道管理器实例
channel_manager = ChannelManager()
