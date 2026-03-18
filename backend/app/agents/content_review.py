"""
内容审核 Agent
审核生成的内容是否符合平台规范
"""
from app.agents.base import AgentBase, AgentContext, AgentResult, AgentStatus
from app.services.ai_service import get_ai_service
from app.core.config import settings
from app.core.logging_config import setup_logging

logger = setup_logging()


class ContentReviewAgent(AgentBase):
    """内容审核 Agent"""

    def __init__(self):
        super().__init__(
            name="content_review",
            description="审核生成的内容是否符合平台规范"
        )
        self.ai_service = get_ai_service(
            service_type=settings.AI_SERVICE_TYPE,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    def get_dependencies(self) -> list:
        """依赖内容生成 Agent"""
        return ["content_generation"]

    async def validate(self, context: AgentContext) -> bool:
        """验证是否可以执行"""
        # 检查是否有内容生成结果
        if "content_generation" not in context.shared_data:
            logger.warning("[ContentReviewAgent] 缺少内容生成结果")
            return False
        return True

    async def execute(self, context: AgentContext) -> AgentResult:
        """执行内容审核"""
        try:
            logger.info(f"[ContentReviewAgent] 开始审核内容")

            # 获取生成的内容
            content_data = context.shared_data["content_generation"]
            title = content_data.get("title", "")
            description = content_data.get("description", "")

            # 合并标题和描述进行审核
            content_to_review = f"{title}\n\n{description}"

            # 调用 AI 服务进行审核
            review_result = await self.ai_service.review_content(content_to_review)

            is_approved = review_result.get("approved", False)
            logger.info(f"[ContentReviewAgent] 审核完成，结果: {'通过' if is_approved else '不通过'}")

            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                data={
                    "approved": is_approved,
                    "risk_level": review_result.get("risk_level"),
                    "issues": review_result.get("issues", []),
                    "suggestions": review_result.get("suggestions", []),
                    "compliance_score": review_result.get("compliance_score", 0),
                }
            )

        except Exception as e:
            logger.error(f"[ContentReviewAgent] 执行失败: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e)
            )
