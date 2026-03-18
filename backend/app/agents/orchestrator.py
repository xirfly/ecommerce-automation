"""
Agent 编排器
负责协调多个 Agent 的执行顺序和数据流转
"""
from typing import Dict, List, Optional, Any
from app.agents.base import AgentBase, AgentContext, AgentResult, AgentStatus
from app.core.logging_config import setup_logging
import time
import asyncio

logger = setup_logging()


class AgentOrchestrator:
    """Agent 编排器"""

    def __init__(self):
        self._agents: Dict[str, AgentBase] = {}
        self._execution_graph: Dict[str, List[str]] = {}

    def register_agent(self, agent: AgentBase):
        """
        注册 Agent

        Args:
            agent: Agent 实例
        """
        self._agents[agent.name] = agent
        self._execution_graph[agent.name] = agent.get_dependencies()
        logger.info(f"[Orchestrator] 注册 Agent: {agent.name}")

    def get_agent(self, name: str) -> Optional[AgentBase]:
        """
        获取 Agent

        Args:
            name: Agent 名称

        Returns:
            Agent 实例
        """
        return self._agents.get(name)

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        列出所有 Agent

        Returns:
            Agent 信息列表
        """
        return [agent.get_info() for agent in self._agents.values()]

    def _build_execution_order(self, target_agents: Optional[List[str]] = None) -> List[str]:
        """
        构建执行顺序（拓扑排序）

        Args:
            target_agents: 目标 Agent 列表，如果为 None 则执行所有 Agent

        Returns:
            执行顺序列表
        """
        if target_agents is None:
            target_agents = list(self._agents.keys())

        # 计算入度
        in_degree = {name: 0 for name in target_agents}
        graph = {name: [] for name in target_agents}

        for agent_name in target_agents:
            dependencies = self._execution_graph.get(agent_name, [])
            for dep in dependencies:
                if dep in target_agents:
                    graph[dep].append(agent_name)
                    in_degree[agent_name] += 1

        # 拓扑排序
        queue = [name for name in target_agents if in_degree[name] == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # 检查是否有循环依赖
        if len(result) != len(target_agents):
            raise ValueError("检测到循环依赖")

        return result

    async def execute(
        self,
        context: AgentContext,
        target_agents: Optional[List[str]] = None,
        stop_on_error: bool = True
    ) -> List[AgentResult]:
        """
        执行 Agent 编排

        Args:
            context: 执行上下文
            target_agents: 目标 Agent 列表，如果为 None 则执行所有 Agent
            stop_on_error: 遇到错误是否停止

        Returns:
            执行结果列表
        """
        logger.info(f"[Orchestrator] 开始执行 Agent 编排，任务 ID: {context.task_id}")

        # 构建执行顺序
        try:
            execution_order = self._build_execution_order(target_agents)
            logger.info(f"[Orchestrator] 执行顺序: {' -> '.join(execution_order)}")
        except ValueError as e:
            logger.error(f"[Orchestrator] 构建执行顺序失败: {e}")
            return [AgentResult(
                agent_name="orchestrator",
                status=AgentStatus.FAILED,
                error=str(e)
            )]

        results = []

        # 按顺序执行 Agent
        for agent_name in execution_order:
            agent = self._agents.get(agent_name)
            if not agent:
                logger.warning(f"[Orchestrator] Agent 不存在: {agent_name}")
                continue

            logger.info(f"[Orchestrator] 执行 Agent: {agent_name}")
            start_time = time.time()

            try:
                # 验证是否可以执行
                if not await agent.validate(context):
                    logger.warning(f"[Orchestrator] Agent 验证失败，跳过: {agent_name}")
                    result = AgentResult(
                        agent_name=agent_name,
                        status=AgentStatus.SKIPPED,
                        error="验证失败"
                    )
                    results.append(result)
                    continue

                # 执行 Agent
                result = await agent.execute(context)
                result.execution_time = time.time() - start_time

                # 记录执行历史
                context.execution_history.append(result.to_dict())

                # 如果成功，将结果添加到共享数据
                if result.status == AgentStatus.SUCCESS:
                    context.shared_data[agent_name] = result.data
                    logger.info(
                        f"[Orchestrator] Agent 执行成功: {agent_name}, "
                        f"耗时: {result.execution_time:.2f}s"
                    )
                else:
                    logger.error(
                        f"[Orchestrator] Agent 执行失败: {agent_name}, "
                        f"错误: {result.error}"
                    )

                    # 如果设置了遇到错误停止，则中断执行
                    if stop_on_error:
                        logger.warning("[Orchestrator] 遇到错误，停止执行")
                        results.append(result)
                        break

                results.append(result)

            except Exception as e:
                logger.error(f"[Orchestrator] Agent 执行异常: {agent_name}, {e}", exc_info=True)
                result = AgentResult(
                    agent_name=agent_name,
                    status=AgentStatus.FAILED,
                    error=str(e),
                    execution_time=time.time() - start_time
                )
                results.append(result)

                if stop_on_error:
                    logger.warning("[Orchestrator] 遇到异常，停止执行")
                    break

        logger.info(f"[Orchestrator] Agent 编排执行完成，共执行 {len(results)} 个 Agent")
        return results

    async def execute_single(
        self,
        agent_name: str,
        context: AgentContext
    ) -> AgentResult:
        """
        执行单个 Agent

        Args:
            agent_name: Agent 名称
            context: 执行上下文

        Returns:
            执行结果
        """
        agent = self._agents.get(agent_name)
        if not agent:
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                error=f"Agent 不存在: {agent_name}"
            )

        logger.info(f"[Orchestrator] 执行单个 Agent: {agent_name}")
        start_time = time.time()

        try:
            # 验证是否可以执行
            if not await agent.validate(context):
                return AgentResult(
                    agent_name=agent_name,
                    status=AgentStatus.SKIPPED,
                    error="验证失败"
                )

            # 执行 Agent
            result = await agent.execute(context)
            result.execution_time = time.time() - start_time

            # 记录执行历史
            context.execution_history.append(result.to_dict())

            return result

        except Exception as e:
            logger.error(f"[Orchestrator] Agent 执行异常: {agent_name}, {e}", exc_info=True)
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start_time
            )


# 全局编排器实例
orchestrator = AgentOrchestrator()
