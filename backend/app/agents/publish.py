"""
发布上架 Agent
将产品发布到电商平台
"""
from app.agents.base import AgentBase, AgentContext, AgentResult, AgentStatus
from app.core.logging_config import setup_logging

logger = setup_logging()


class PublishAgent(AgentBase):
    """发布上架 Agent"""

    def __init__(self):
        super().__init__(
            name="publish",
            description="将产品发布到电商平台"
        )

    def get_dependencies(self) -> list:
        """依赖内容审核和图片生成 Agent"""
        return ["content_review", "image_generation"]

    async def validate(self, context: AgentContext) -> bool:
        """验证是否可以执行"""
        # 检查内容审核是否通过
        if "content_review" not in context.shared_data:
            logger.warning("[PublishAgent] 缺少内容审核结果")
            return False

        review_data = context.shared_data["content_review"]
        if not review_data.get("approved", False):
            logger.info("[PublishAgent] 内容审核未通过，跳过发布")
            return False

        # 检查是否有图片
        if "image_generation" not in context.shared_data:
            logger.warning("[PublishAgent] 缺少图片生成结果")
            return False

        return True

    async def execute(self, context: AgentContext) -> AgentResult:
        """执行发布上架"""
        try:
            logger.info(f"[PublishAgent] 开始发布产品")

            # 收集所有需要的数据
            content_data = context.shared_data.get("content_generation", {})
            image_data = context.shared_data.get("image_generation", {})
            price_data = context.shared_data.get("price_optimization", {})
            video_data = context.shared_data.get("video_generation", {})

            # 构建发布数据
            publish_data = {
                "product_id": context.product_id,
                "title": content_data.get("title"),
                "description": content_data.get("description"),
                "keywords": content_data.get("keywords", []),
                "main_image": image_data.get("main_image"),
                "detail_images": image_data.get("detail_images", []),
                "price": price_data.get("optimized_price") or context.product_data.get("price"),
                "category": context.product_data.get("category"),
                "platform": context.product_data.get("platform", "淘宝"),
            }

            # 如果有视频，添加视频
            if video_data:
                publish_data["video_url"] = video_data.get("video_url")

            # TODO: 调用真实的电商平台 API 进行发布
            # 目前使用模拟发布
            publish_id = f"PUB_{context.product_id}_{context.task_id}"

            logger.info(f"[PublishAgent] 产品发布完成，发布 ID: {publish_id}")

            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                data={
                    "publish_id": publish_id,
                    "platform": publish_data["platform"],
                    "publish_url": f"https://{publish_data['platform']}.com/item/{publish_id}",
                    "publish_time": "2026-03-17 18:00:00",
                    "status": "已上架",
                }
            )

        except Exception as e:
            logger.error(f"[PublishAgent] 执行失败: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e)
            )
