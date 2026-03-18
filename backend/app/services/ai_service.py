"""
AI 服务抽象层
支持多种 AI 服务提供商（OpenAI、本地模型、模拟模式）
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.core.logging_config import setup_logging
import asyncio
import random

logger = setup_logging()


class AIServiceBase(ABC):
    """AI 服务基类"""

    @abstractmethod
    async def analyze_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        选品分析

        Args:
            product_data: 产品信息（名称、分类、价格等）

        Returns:
            分析结果（市场趋势、竞争情况、利润率、建议）
        """
        pass

    @abstractmethod
    async def generate_content(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        内容生成

        Args:
            product_data: 产品信息

        Returns:
            生成的内容（标题、描述、关键词）
        """
        pass

    @abstractmethod
    async def review_content(self, content: str) -> Dict[str, Any]:
        """
        内容审核

        Args:
            content: 待审核的内容

        Returns:
            审核结果（状态、问题、建议）
        """
        pass


class MockAIService(AIServiceBase):
    """模拟 AI 服务（用于开发测试）"""

    async def analyze_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """模拟选品分析"""
        logger.info(f"[MockAI] 分析产品: {product_data.get('name', 'Unknown')}")

        # 模拟 AI 处理时间
        await asyncio.sleep(random.uniform(1, 2))

        category = product_data.get('category', '未知')
        price = product_data.get('price', 0)

        # 根据分类和价格生成不同的分析结果
        market_trends = {
            '数码': '上升',
            '服饰': '稳定',
            '家居': '上升',
            '美妆': '快速上升',
        }

        competition_levels = {
            '数码': '激烈',
            '服饰': '中等',
            '家居': '中等',
            '美妆': '激烈',
        }

        # 根据价格计算利润率
        if price < 50:
            profit_margin = random.uniform(0.25, 0.35)
        elif price < 200:
            profit_margin = random.uniform(0.30, 0.45)
        else:
            profit_margin = random.uniform(0.35, 0.55)

        market_trend = market_trends.get(category, '稳定')
        competition = competition_levels.get(category, '中等')

        # 生成建议
        if profit_margin > 0.4 and market_trend == '上升':
            recommendation = '强烈建议上架'
            reason = '利润率高且市场需求旺盛'
        elif profit_margin > 0.3:
            recommendation = '建议上架'
            reason = '利润率适中，市场前景良好'
        else:
            recommendation = '谨慎考虑'
            reason = '利润率偏低，建议优化成本'

        return {
            'market_trend': market_trend,
            'competition_level': competition,
            'profit_margin': round(profit_margin, 2),
            'recommendation': recommendation,
            'reason': reason,
            'target_audience': self._generate_target_audience(category),
            'selling_points': self._generate_selling_points(product_data),
        }

    async def generate_content(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """模拟内容生成"""
        logger.info(f"[MockAI] 生成内容: {product_data.get('name', 'Unknown')}")

        # 模拟 AI 处理时间
        await asyncio.sleep(random.uniform(1, 2))

        name = product_data.get('name', '产品')
        category = product_data.get('category', '商品')
        price = product_data.get('price', 0)
        description = product_data.get('description', '')

        # 生成标题
        title_templates = [
            f"【爆款推荐】{name} - 高品质{category}",
            f"{name} | 精选{category} 限时优惠",
            f"热销{category} - {name} 品质保证",
            f"{name} 新品上市 | {category}首选",
        ]
        title = random.choice(title_templates)

        # 生成描述
        desc_parts = [
            f"这款{name}是我们精心挑选的优质{category}产品。",
            f"采用优质材料制作，注重每一个细节。",
            f"适合追求品质生活的您。",
        ]

        if description:
            desc_parts.insert(1, description)

        if price < 100:
            desc_parts.append("超值价格，性价比之选！")
        elif price < 500:
            desc_parts.append("品质与价格的完美平衡。")
        else:
            desc_parts.append("高端品质，彰显品味。")

        generated_description = " ".join(desc_parts)

        # 生成关键词
        keywords = [
            name,
            category,
            "高品质",
            "热销",
            "推荐",
        ]

        # 根据分类添加特定关键词
        category_keywords = {
            '数码': ['科技', '智能', '便携'],
            '服饰': ['时尚', '舒适', '百搭'],
            '家居': ['实用', '美观', '耐用'],
            '美妆': ['天然', '温和', '有效'],
        }
        keywords.extend(category_keywords.get(category, ['优质', '实惠']))

        return {
            'title': title,
            'description': generated_description,
            'keywords': keywords[:8],  # 限制关键词数量
            'highlights': self._generate_highlights(product_data),
        }

    async def review_content(self, content: str) -> Dict[str, Any]:
        """模拟内容审核"""
        logger.info(f"[MockAI] 审核内容: {content[:50]}...")

        # 模拟 AI 处理时间
        await asyncio.sleep(random.uniform(0.5, 1))

        # 敏感词检测
        sensitive_words = ['假货', '仿品', '山寨', '欺诈', '违法']
        issues = []

        for word in sensitive_words:
            if word in content:
                issues.append({
                    'type': 'sensitive_word',
                    'word': word,
                    'severity': 'high',
                    'suggestion': f'请移除敏感词"{word}"'
                })

        # 长度检查
        if len(content) < 20:
            issues.append({
                'type': 'length',
                'severity': 'medium',
                'suggestion': '内容过短，建议补充更多产品信息'
            })
        elif len(content) > 1000:
            issues.append({
                'type': 'length',
                'severity': 'low',
                'suggestion': '内容较长，建议精简以提高可读性'
            })

        # 判断审核状态
        if any(issue['severity'] == 'high' for issue in issues):
            status = 'rejected'
        elif issues:
            status = 'needs_revision'
        else:
            status = 'approved'

        suggestions = [
            '标题建议控制在30字以内',
            '描述中突出产品核心卖点',
            '添加使用场景描述',
            '补充产品参数信息',
        ]

        return {
            'status': status,
            'issues': issues,
            'suggestions': random.sample(suggestions, 2) if status == 'approved' else [],
            'score': random.randint(75, 95) if status == 'approved' else random.randint(40, 70),
        }

    def _generate_target_audience(self, category: str) -> str:
        """生成目标受众"""
        audiences = {
            '数码': '18-35岁科技爱好者，追求新潮数码产品',
            '服饰': '20-40岁注重穿搭的都市白领',
            '家居': '25-45岁追求生活品质的家庭用户',
            '美妆': '18-35岁注重护肤的女性用户',
        }
        return audiences.get(category, '广泛的消费群体')

    def _generate_selling_points(self, product_data: Dict[str, Any]) -> List[str]:
        """生成卖点"""
        category = product_data.get('category', '')

        selling_points_map = {
            '数码': ['高性能配置', '轻薄便携', '长续航', '智能功能'],
            '服饰': ['优质面料', '精致做工', '百搭款式', '舒适透气'],
            '家居': ['实用设计', '耐用材质', '简约美观', '易于清洁'],
            '美妆': ['天然成分', '温和配方', '显著效果', '适合敏感肌'],
        }

        points = selling_points_map.get(category, ['高品质', '性价比高', '值得信赖'])
        return random.sample(points, min(3, len(points)))

    def _generate_highlights(self, product_data: Dict[str, Any]) -> List[str]:
        """生成产品亮点"""
        highlights = [
            '✓ 品质保证，正品承诺',
            '✓ 7天无理由退换',
            '✓ 全国包邮',
        ]

        price = product_data.get('price', 0)
        if price > 200:
            highlights.append('✓ 赠送精美礼盒')

        return highlights


class OpenAIService(AIServiceBase):
    """OpenAI GPT-4 服务（真实 API）"""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        # TODO: 初始化 OpenAI 客户端

    async def analyze_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用 GPT-4 分析产品"""
        # TODO: 实现真实的 OpenAI API 调用
        logger.info("[OpenAI] 调用 GPT-4 分析产品")
        raise NotImplementedError("OpenAI 服务暂未实现，请先配置 API Key")

    async def generate_content(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用 GPT-4 生成内容"""
        # TODO: 实现真实的 OpenAI API 调用
        logger.info("[OpenAI] 调用 GPT-4 生成内容")
        raise NotImplementedError("OpenAI 服务暂未实现，请先配置 API Key")

    async def review_content(self, content: str) -> Dict[str, Any]:
        """使用 GPT-4 审核内容"""
        # TODO: 实现真实的 OpenAI API 调用
        logger.info("[OpenAI] 调用 GPT-4 审核内容")
        raise NotImplementedError("OpenAI 服务暂未实现，请先配置 API Key")


# AI 服务工厂
def get_ai_service(service_type: str = "mock", **kwargs) -> AIServiceBase:
    """
    获取 AI 服务实例

    Args:
        service_type: 服务类型（mock/openai）
        **kwargs: 服务配置参数

    Returns:
        AI 服务实例
    """
    if service_type == "mock":
        return MockAIService()
    elif service_type == "openai":
        api_key = kwargs.get('api_key')
        if not api_key:
            raise ValueError("OpenAI 服务需要提供 api_key")
        return OpenAIService(api_key=api_key, base_url=kwargs.get('base_url'))
    else:
        raise ValueError(f"不支持的 AI 服务类型: {service_type}")
