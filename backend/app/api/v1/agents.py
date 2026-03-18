"""
Agent 管理 API
提供 Agent 信息查询、执行历史统计等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.core.database import get_db
from app.models import User, Task, TaskLog
from app.schemas import Response
from app.dependencies.auth import get_current_user
from app.agents.orchestrator import orchestrator
from app.agents.base import AgentContext
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/agents", tags=["Agent管理"])


@router.get("/list", response_model=Response[List[Dict[str, Any]]])
async def list_agents(
    current_user: User = Depends(get_current_user),
):
    """
    获取所有可用的 Agent 列表

    返回所有已注册的 Agent 信息，包括名称、描述、依赖关系
    """
    agents = orchestrator.list_agents()

    return Response(
        code=0,
        message="获取成功",
        data=agents
    )


@router.get("/graph", response_model=Response[Dict[str, Any]])
async def get_agent_graph(
    current_user: User = Depends(get_current_user),
):
    """
    获取 Agent 依赖关系图

    返回 Agent 之间的依赖关系，用于可视化展示
    """
    agents = orchestrator.list_agents()

    # 构建节点和边
    nodes = []
    edges = []

    for agent in agents:
        nodes.append({
            "id": agent["name"],
            "label": agent["description"],
            "name": agent["name"],
        })

        # 添加依赖边
        for dep in agent.get("dependencies", []):
            edges.append({
                "from": dep,
                "to": agent["name"],
            })

    return Response(
        code=0,
        message="获取成功",
        data={
            "nodes": nodes,
            "edges": edges,
        }
    )


@router.get("/statistics", response_model=Response[Dict[str, Any]])
async def get_agent_statistics(
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取 Agent 执行统计

    统计最近 N 天内各个 Agent 的执行次数、成功率、平均执行时间等
    """
    # 计算时间范围
    start_date = datetime.now() - timedelta(days=days)

    # 查询任务日志
    # 使用 case 语句代替 func.if_ 以提高兼容性
    query = select(
        TaskLog.agent_name,
        func.count(TaskLog.id).label('total_count'),
        func.sum(
            case((TaskLog.log_level == 'ERROR', 1), else_=0)
        ).label('error_count')
    ).where(
        TaskLog.created_at >= start_date
    ).group_by(TaskLog.agent_name)

    # 如果不是管理员，只查询自己的
    if current_user.role.value != "admin":
        # 需要 join Task 表来过滤
        from app.models import Task as TaskModel
        query = query.join(TaskModel, TaskLog.task_id == TaskModel.id).where(
            TaskModel.created_by == current_user.id
        )

    result = await db.execute(query)
    stats = result.fetchall()

    # 构建统计数据
    agent_stats = []
    for row in stats:
        agent_name = row[0]
        total_count = row[1] or 0
        error_count = row[2] or 0

        success_count = total_count - error_count
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        agent_stats.append({
            "agent_name": agent_name,
            "total_executions": total_count,
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": round(success_rate, 2),
        })

    # 按执行次数排序
    agent_stats.sort(key=lambda x: x["total_executions"], reverse=True)

    return Response(
        code=0,
        message="获取成功",
        data={
            "period_days": days,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "agents": agent_stats,
        }
    )


@router.get("/execution-flow", response_model=Response[Dict[str, Any]])
async def get_execution_flow(
    task_type: str = Query(..., description="任务类型"),
    current_user: User = Depends(get_current_user),
):
    """
    获取指定任务类型的 Agent 执行流程

    返回该任务类型会执行哪些 Agent，以及执行顺序
    """
    # 定义任务类型对应的 Agent 列表
    task_agent_mapping = {
        "product_analysis": ["product_analysis"],
        "content_generation": ["product_analysis", "content_generation"],
        "image_generation": ["product_analysis", "content_generation", "image_generation"],
        "video_generation": [
            "product_analysis",
            "content_generation",
            "image_generation",
            "video_generation"
        ],
        "review": ["product_analysis", "content_generation", "content_review"],
        "publish": [
            "product_analysis",
            "price_optimization",
            "content_generation",
            "image_generation",
            "content_review",
            "publish"
        ],
    }

    if task_type not in task_agent_mapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"未知的任务类型: {task_type}"
        )

    agent_names = task_agent_mapping[task_type]

    # 使用编排器的拓扑排序来获取正确的执行顺序
    try:
        # 调用编排器的内部方法进行拓扑排序
        execution_order = orchestrator._build_execution_order(agent_names)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"构建执行顺序失败: {str(e)}"
        )

    # 获取 Agent 详细信息
    all_agents = orchestrator.list_agents()
    agent_map = {a["name"]: a for a in all_agents}

    flow = []
    for idx, agent_name in enumerate(execution_order):
        agent_info = agent_map.get(agent_name, {})
        flow.append({
            "step": idx + 1,
            "agent_name": agent_name,
            "description": agent_info.get("description", ""),
            "dependencies": agent_info.get("dependencies", []),
        })

    return Response(
        code=0,
        message="获取成功",
        data={
            "task_type": task_type,
            "total_steps": len(flow),
            "flow": flow,
        }
    )


@router.get("/logs/{task_id}", response_model=Response[List[Dict[str, Any]]])
async def get_agent_logs(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取指定任务的 Agent 执行日志

    返回该任务中所有 Agent 的执行日志，按时间顺序排列
    """
    # 检查任务是否存在
    from app.models import Task as TaskModel
    task_result = await db.execute(select(TaskModel).where(TaskModel.id == task_id))
    task = task_result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    # 权限检查
    if current_user.role.value != "admin" and task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务"
        )

    # 查询日志
    result = await db.execute(
        select(TaskLog)
        .where(TaskLog.task_id == task_id)
        .order_by(TaskLog.created_at.asc())
    )
    logs = result.scalars().all()

    # 构建日志列表
    log_list = []
    for log in logs:
        log_list.append({
            "id": log.id,
            "agent_name": log.agent_name,
            "log_level": log.log_level,
            "message": log.message,
            "extra_data": log.extra_data,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        })

    return Response(
        code=0,
        message="获取成功",
        data=log_list
    )


@router.get("/info/{agent_name}", response_model=Response[Dict[str, Any]])
async def get_agent_info(
    agent_name: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取指定 Agent 的详细信息

    返回 Agent 的名称、描述、依赖关系等详细信息
    """
    agent = orchestrator.get_agent(agent_name)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent 不存在: {agent_name}"
        )

    agent_info = agent.get_info()

    return Response(
        code=0,
        message="获取成功",
        data=agent_info
    )
