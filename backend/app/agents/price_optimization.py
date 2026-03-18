"""
价格优化 Agent
根据市场情况优化产品定价
"""
from app.agents.base import AgentBase, AgentContext, AgentResult, AgentStatus
from app.core.logging_config import setup_logging
import random

logger = setup_logging()


class PriceOptimizationAgent(AgentBase):
    """价格优化 Agent"""

    def __init__(self):
        super().__init__(
            name="price_optimization",
            description="根据市场情况优化产品定价"
        )

    def get_dependencies(self) -> list:
        """依赖选品分析 Agent"""
        return ["product_analysis"]

    async def validate(self, context: AgentContext) -> bool:
        """验证是否可以执行"""
        # 检查是否有选品分析结果
        if "product_analysis" not in context.shared_data:
            logger.warning("[PriceOptimizationAgent] 缺少选品分析结果")
            return False

        # 检查产品是否有价格
        if "price" not in context.product_data:
            logger.warning("[PriceOptimizationAgent] 产品缺少价格信息")
            return False

        return True

    async def execute(self, context: AgentContext) -> AgentResult:
        """执行价格优化"""
        try:
            logger.info(f"[PriceOptimizationAgent] 开始优化价格")

            # 获取选品分析结果
            analysis_data = context.shared_data["product_analysis"]
            competition_level = analysis_data.get("competition_level", "中等")
            profit_margin = analysis_data.get("profit_margin", 0)

            # 获取原始价格
            original_price = float(context.product_data.get("price", 0))

            # 根据竞争程度和利润率调整价格
            if competition_level == "高":
                # 高竞争，降价 5-10%
                adjustment = random.uniform(-0.10, -0.05)
            elif competition_level == "低":
                # 低竞争，提价 5-15%
                adjustment = random.uniform(0.05, 0.15)
            else:
                # 中等竞争，微调 ±5%
                adjustment = random.uniform(-0.05, 0.05)

            optimized_price = round(original_price * (1 + adjustment), 2)

            # 确保价格不低于成本
            min_price = original_price * 0.8  # 最低不低于原价的 80%
            optimized_price = max(optimized_price, min_price)

            logger.info(
                f"[PriceOptimizationAgent] 价格优化完成，"
                f"原价: {original_price}, 优化后: {optimized_price}"
            )

            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                data={
                    "original_price": original_price,
                    "optimized_price": optimized_price,
                    "adjustment_rate": adjustment,
                    "competition_level": competition_level,
                    "recommendation": f"建议定价 {optimized_price} 元",
                }
            )

        except Exception as e:
            logger.error(f"[PriceOptimizationAgent] 执行失败: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e)
            )
