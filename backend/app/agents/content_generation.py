"""
内容生成 Agent
生成产品标题、描述、关键词等营销内容
"""
from app.agents.base import AgentBase, AgentContext, AgentResult, AgentStatus
from app.services.ai_service import get_ai_service
from app.core.config import settings
from app.core.logging_config import setup_logging

logger = setup_logging()


class ContentGenerationAgent(AgentBase):
    """内容生成 Agent"""

    def __init__(self):
        super().__init__(
            name="content_generation",
            description="生成产品标题、描述、关键词等营销内容"
        )
        self.ai_service = get_ai_service(
            service_type=settings.AI_SERVICE_TYPE,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    def get_dependencies(self) -> list:
        """依赖选品分析 Agent"""
        return ["product_analysis"]

    async def validate(self, context: AgentContext) -> bool:
        """验证是否可以执行"""
        # 检查是否有选品分析结果
        if "product_analysis" not in context.shared_data:
            logger.warning("[ContentGenerationAgent] 缺少选品分析结果")
            return False

        # 检查选品分析是否推荐继续
        analysis_data = context.shared_data["product_analysis"]
        recommendation = analysis_data.get("recommendation", "")
        if "不推荐" in recommendation or "不建议" in recommendation:
            logger.info("[ContentGenerationAgent] 选品分析不推荐，跳过内容生成")
            return False

        return True

    async def execute(self, context: AgentContext) -> AgentResult:
        """执行内容生成"""
        try:
            logger.info(f"[ContentGenerationAgent] 开始生成内容: {context.product_data.get('name')}")

            # 获取选品分析结果，用于优化内容生成
            analysis_data = context.shared_data.get("product_analysis", {})

            # 合并产品数据和分析结果
            enhanced_product_data = {
                **context.product_data,
                "market_potential": analysis_data.get("market_potential"),
                "competition_level": analysis_data.get("competition_level"),
            }

            # 调用 AI 服务生成内容
            content_result = await self.ai_service.generate_content(enhanced_product_data)

            logger.info(f"[ContentGenerationAgent] 内容生成完成，标题: {content_result.get('title')}")

            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                data={
                    "title": content_result.get("title"),
                    "description": content_result.get("description"),
                    "keywords": content_result.get("keywords", []),
                    "selling_points": content_result.get("selling_points", []),
                    "seo_optimized": content_result.get("seo_optimized", False),
                }
            )

        except Exception as e:
            logger.error(f"[ContentGenerationAgent] 执行失败: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e)
            )
