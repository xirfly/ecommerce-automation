"""
选品分析 Agent
分析产品市场潜力、竞争情况、利润率等
"""
from app.agents.base import AgentBase, AgentContext, AgentResult, AgentStatus
from app.services.ai_service import get_ai_service
from app.core.config import settings
from app.core.logging_config import setup_logging

logger = setup_logging()


class ProductAnalysisAgent(AgentBase):
    """选品分析 Agent"""

    def __init__(self):
        super().__init__(
            name="product_analysis",
            description="分析产品市场潜力、竞争情况、利润率等"
        )
        self.ai_service = get_ai_service(
            service_type=settings.AI_SERVICE_TYPE,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    async def validate(self, context: AgentContext) -> bool:
        """验证是否可以执行"""
        # 检查产品数据是否完整
        required_fields = ["name", "category", "price"]
        for field in required_fields:
            if field not in context.product_data:
                logger.warning(f"[ProductAnalysisAgent] 缺少必需字段: {field}")
                return False
        return True

    async def execute(self, context: AgentContext) -> AgentResult:
        """执行选品分析"""
        try:
            logger.info(f"[ProductAnalysisAgent] 开始分析产品: {context.product_data.get('name')}")

            # 调用 AI 服务进行分析
            analysis_result = await self.ai_service.analyze_product(context.product_data)

            logger.info(f"[ProductAnalysisAgent] 分析完成，市场潜力: {analysis_result.get('market_potential')}")

            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                data={
                    "market_potential": analysis_result.get("market_potential"),
                    "competition_level": analysis_result.get("competition_level"),
                    "profit_margin": analysis_result.get("profit_margin"),
                    "recommendation": analysis_result.get("recommendation"),
                    "analysis_details": analysis_result.get("analysis_details", {}),
                }
            )

        except Exception as e:
            logger.error(f"[ProductAnalysisAgent] 执行失败: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e)
            )
