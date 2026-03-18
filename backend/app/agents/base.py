"""
Agent 基类
定义所有 Agent 的通用接口和行为
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent 执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentContext:
    """Agent 执行上下文"""
    task_id: int
    product_id: int
    product_data: Dict[str, Any]
    user_id: int

    # 共享数据（Agent 之间传递）
    shared_data: Dict[str, Any] = field(default_factory=dict)

    # 执行历史
    execution_history: List[Dict[str, Any]] = field(default_factory=list)

    # 配置参数
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Agent 执行结果"""
    agent_name: str
    status: AgentStatus
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "agent_name": self.agent_name,
            "status": self.status.value,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat(),
        }


class AgentBase(ABC):
    """Agent 基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        执行 Agent 任务

        Args:
            context: 执行上下文

        Returns:
            执行结果
        """
        pass

    @abstractmethod
    async def validate(self, context: AgentContext) -> bool:
        """
        验证是否可以执行

        Args:
            context: 执行上下文

        Returns:
            是否可以执行
        """
        pass

    def get_dependencies(self) -> List[str]:
        """
        获取依赖的 Agent 列表

        Returns:
            依赖的 Agent 名称列表
        """
        return []

    def get_info(self) -> Dict[str, Any]:
        """
        获取 Agent 信息

        Returns:
            Agent 信息字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "dependencies": self.get_dependencies(),
        }
