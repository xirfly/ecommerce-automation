"""
图片生成 Agent
生成产品主图、详情图等
"""
from app.agents.base import AgentBase, AgentContext, AgentResult, AgentStatus
from app.core.logging_config import setup_logging
import random

logger = setup_logging()


class ImageGenerationAgent(AgentBase):
    """图片生成 Agent"""

    def __init__(self):
        super().__init__(
            name="image_generation",
            description="生成产品主图、详情图等"
        )

    def get_dependencies(self) -> list:
        """依赖内容生成 Agent"""
        return ["content_generation"]

    async def validate(self, context: AgentContext) -> bool:
        """验证是否可以执行"""
        # 检查是否有内容生成结果
        if "content_generation" not in context.shared_data:
            logger.warning("[ImageGenerationAgent] 缺少内容生成结果")
            return False
        return True

    async def execute(self, context: AgentContext) -> AgentResult:
        """执行图片生成"""
        try:
            logger.info(f"[ImageGenerationAgent] 开始生成图片")

            # 获取内容数据用于生成图片提示词
            content_data = context.shared_data["content_generation"]
            title = content_data.get("title", "")
            keywords = content_data.get("keywords", [])

            # TODO: 集成真实的图片生成服务（Midjourney/DALL-E）
            # 目前使用模拟数据
            image_urls = [
                f"https://placeholder.com/product_{context.product_id}_main.jpg",
                f"https://placeholder.com/product_{context.product_id}_detail_1.jpg",
                f"https://placeholder.com/product_{context.product_id}_detail_2.jpg",
            ]

            logger.info(f"[ImageGenerationAgent] 图片生成完成，共 {len(image_urls)} 张")

            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                data={
                    "main_image": image_urls[0],
                    "detail_images": image_urls[1:],
                    "image_count": len(image_urls),
                    "generation_prompt": f"{title} - {', '.join(keywords[:3])}",
                }
            )

        except Exception as e:
            logger.error(f"[ImageGenerationAgent] 执行失败: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e)
            )
