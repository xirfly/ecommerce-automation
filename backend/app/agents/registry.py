"""
Agent 注册中心
注册所有可用的 Agent
"""
from app.agents.orchestrator import orchestrator
from app.agents.product_analysis import ProductAnalysisAgent
from app.agents.content_generation import ContentGenerationAgent
from app.agents.content_review import ContentReviewAgent
from app.agents.image_generation import ImageGenerationAgent
from app.agents.video_generation import VideoGenerationAgent
from app.agents.price_optimization import PriceOptimizationAgent
from app.agents.publish import PublishAgent
from app.core.logging_config import setup_logging

logger = setup_logging()


def register_all_agents():
    """注册所有 Agent"""
    logger.info("[AgentRegistry] 开始注册 Agent")

    # 注册 7 个专业 Agent
    agents = [
        ProductAnalysisAgent(),      # 1. 选品分析
        PriceOptimizationAgent(),    # 2. 价格优化
        ContentGenerationAgent(),    # 3. 内容生成
        ImageGenerationAgent(),      # 4. 图片生成
        VideoGenerationAgent(),      # 5. 视频生成（可选）
        ContentReviewAgent(),        # 6. 内容审核
        PublishAgent(),              # 7. 发布上架
    ]

    for agent in agents:
        orchestrator.register_agent(agent)

    logger.info(f"[AgentRegistry] 成功注册 {len(agents)} 个 Agent")


# 自动注册所有 Agent
register_all_agents()
