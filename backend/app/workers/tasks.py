"""
Celery 异步任务（使用 Agent 编排系统）
"""
from celery import Task
from app.workers.celery_app import celery_app
from app.core.logging_config import setup_logging
from app.core.database import AsyncSessionLocal
from app.models import Task as TaskModel, TaskLog, TaskStatus, Product
from app.websocket.websocket_manager import manager
from app.agents.base import AgentContext, AgentStatus
from app.agents.orchestrator import orchestrator
from app.agents import registry  # 自动注册所有 Agent
from app.services.notification import NotificationManager
from app.monitoring.metrics import (
    task_running,
    record_task_execution,
    record_agent_execution,
)
from sqlalchemy import select
import asyncio
import time
from datetime import datetime, timezone, timedelta

logger = setup_logging()

# 北京时区
BEIJING_TZ = timezone(timedelta(hours=8))


@celery_app.task(bind=True)
def execute_task(self, task_id: int, task_type: str):
    """
    执行任务的主入口

    Args:
        task_id: 任务ID
        task_type: 任务类型
    """
    logger.info(f"开始执行任务 #{task_id}，类型: {task_type}")

    # 获取或创建 event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_execute_task_async(task_id, task_type))
        return result
    except Exception as e:
        logger.error(f"任务执行异常: {e}", exc_info=True)
        raise


async def _execute_task_async(task_id: int, task_type: str):
    """异步执行任务"""
    start_time = time.time()

    # 增加运行中任务计数
    task_running.labels(task_type=task_type).inc()

    async with AsyncSessionLocal() as db:
        # 获取任务
        result = await db.execute(select(TaskModel).where(TaskModel.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            logger.error(f"任务 #{task_id} 不存在")
            task_running.labels(task_type=task_type).dec()
            return {"success": False, "error": "任务不存在"}

        try:
            # 更新任务状态为执行中
            task.status = TaskStatus.RUNNING
            task.progress = 0
            task.started_at = datetime.now(BEIJING_TZ)
            await db.commit()
            await db.refresh(task)

            # 发送 WebSocket 更新
            await _send_task_update(task, db)

            # 添加开始日志
            await _add_task_log(
                task_id=task_id,
                log_level="INFO",
                message=f"开始执行 {_get_task_type_name(task_type)} 任务",
                agent_name="TaskExecutor",
                db=db
            )

            # 获取产品信息
            product_result = await db.execute(select(Product).where(Product.id == task.product_id))
            product = product_result.scalar_one_or_none()

            if not product:
                raise ValueError(f"产品 #{task.product_id} 不存在")

            # 准备产品数据
            product_data = {
                'name': product.name,
                'category': product.category,
                'price': float(product.price),
                'description': product.description,
                'platform': product.platform,
            }

            # 创建 Agent 执行上下文
            context = AgentContext(
                task_id=task_id,
                product_id=task.product_id,
                product_data=product_data,
                user_id=task.created_by,
                config={
                    'enable_video_generation': False,  # 默认不生成视频
                }
            )

            # 根据任务类型执行不同的 Agent
            if task_type == "product_analysis":
                # 只执行选品分析 Agent
                agent_results = await orchestrator.execute(
                    context=context,
                    target_agents=["product_analysis"],
                    stop_on_error=True
                )
            elif task_type == "content_generation":
                # 执行选品分析 + 内容生成
                agent_results = await orchestrator.execute(
                    context=context,
                    target_agents=["product_analysis", "content_generation"],
                    stop_on_error=True
                )
            elif task_type == "image_generation":
                # 执行选品分析 + 内容生成 + 图片生成
                agent_results = await orchestrator.execute(
                    context=context,
                    target_agents=["product_analysis", "content_generation", "image_generation"],
                    stop_on_error=True
                )
            elif task_type == "video_generation":
                # 执行选品分析 + 内容生成 + 图片生成 + 视频生成
                context.config['enable_video_generation'] = True
                agent_results = await orchestrator.execute(
                    context=context,
                    target_agents=[
                        "product_analysis",
                        "content_generation",
                        "image_generation",
                        "video_generation"
                    ],
                    stop_on_error=True
                )
            elif task_type == "review":
                # 执行选品分析 + 内容生成 + 内容审核
                agent_results = await orchestrator.execute(
                    context=context,
                    target_agents=["product_analysis", "content_generation", "content_review"],
                    stop_on_error=True
                )
            elif task_type == "publish":
                # 执行完整流程：选品分析 -> 价格优化 -> 内容生成 -> 图片生成 -> 内容审核 -> 发布上架
                agent_results = await orchestrator.execute(
                    context=context,
                    target_agents=[
                        "product_analysis",
                        "price_optimization",
                        "content_generation",
                        "image_generation",
                        "content_review",
                        "publish"
                    ],
                    stop_on_error=True
                )
            else:
                raise ValueError(f"未知的任务类型: {task_type}")

            # 记录每个 Agent 的执行结果
            total_agents = len(agent_results)
            for idx, agent_result in enumerate(agent_results):
                # 记录 Agent 执行指标
                agent_duration_val = agent_result.data.get('duration', 0) if agent_result.data else 0
                record_agent_execution(
                    agent_name=agent_result.agent_name,
                    status='success' if agent_result.status == AgentStatus.SUCCESS else 'failed',
                    duration=agent_duration_val
                )

                # 计算进度
                progress = int((idx + 1) / total_agents * 100)
                task.progress = progress
                await db.commit()
                await db.refresh(task)
                await _send_task_update(task, db)

                # 添加日志
                log_level = "INFO" if agent_result.status == AgentStatus.SUCCESS else "ERROR"
                message = f"Agent [{agent_result.agent_name}] 执行{'成功' if agent_result.status == AgentStatus.SUCCESS else '失败'}"
                if agent_result.error:
                    message += f": {agent_result.error}"

                await _add_task_log(
                    task_id=task_id,
                    log_level=log_level,
                    message=message,
                    agent_name=agent_result.agent_name,
                    db=db,
                    extra_data=agent_result.data if agent_result.status == AgentStatus.SUCCESS else None
                )

            # 检查是否所有 Agent 都执行成功
            all_success = all(r.status == AgentStatus.SUCCESS for r in agent_results)

            if all_success:
                # 更新任务状态为成功
                task.status = TaskStatus.SUCCESS
                task.progress = 100
                task.completed_at = datetime.now(BEIJING_TZ)
                task.result = {
                    "agents": [r.to_dict() for r in agent_results],
                    "shared_data": context.shared_data,
                }
                await db.commit()
                await db.refresh(task)

                # 发送 WebSocket 更新
                await _send_task_update(task, db)

                # 发送成功通知（WebSocket）
                await manager.send_notification(
                    title="任务执行成功",
                    content=f"任务 #{task_id} 已完成",
                    user_id=task.created_by,
                    level="success"
                )

                # 发送外部通知（飞书/Telegram/企业微信）
                try:
                    await NotificationManager.notify_task_status(
                        db=db,
                        task_id=task_id,
                        status="success",
                        message=f"任务 #{task_id} ({_get_task_type_name(task_type)}) 执行成功",
                        extra_data={
                            "任务类型": _get_task_type_name(task_type),
                            "产品": product_data['name'],
                            "执行时长": f"{(datetime.now(BEIJING_TZ) - task.started_at).total_seconds():.1f}秒",
                        }
                    )
                except Exception as e:
                    logger.error(f"发送外部通知失败: {e}")

                # 添加完成日志
                await _add_task_log(
                    task_id=task_id,
                    log_level="INFO",
                    message=f"任务执行成功，共执行 {len(agent_results)} 个 Agent",
                    agent_name="TaskExecutor",
                    db=db
                )

                # 记录任务执行指标
                duration = time.time() - start_time
                record_task_execution(task_type=task_type, status='success', duration=duration)
                task_running.labels(task_type=task_type).dec()

                logger.info(f"任务 #{task_id} 执行成功")
                return {"success": True, "result": task.result}
            else:
                # 有 Agent 执行失败
                failed_agents = [r for r in agent_results if r.status == AgentStatus.FAILED]
                error_message = f"部分 Agent 执行失败: {', '.join([r.agent_name for r in failed_agents])}"

                raise Exception(error_message)

        except Exception as e:
            logger.error(f"任务 #{task_id} 执行失败: {e}", exc_info=True)

            # 更新任务状态为失败
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now(BEIJING_TZ)
            task.error_message = str(e)
            await db.commit()
            await db.refresh(task)

            # 发送 WebSocket 更新
            await _send_task_update(task, db)

            # 发送失败通知（WebSocket）
            await manager.send_notification(
                title="任务执行失败",
                content=f"任务 #{task_id} 执行失败: {str(e)}",
                user_id=task.created_by,
                level="error"
            )

            # 发送外部通知（飞书/Telegram/企业微信）
            try:
                await NotificationManager.notify_task_status(
                    db=db,
                    task_id=task_id,
                    status="failed",
                    message=f"任务 #{task_id} ({_get_task_type_name(task_type)}) 执行失败",
                    extra_data={
                        "任务类型": _get_task_type_name(task_type),
                        "错误信息": str(e)[:200],  # 限制长度
                    }
                )
            except Exception as notify_error:
                logger.error(f"发送外部通知失败: {notify_error}")

            # 添加错误日志
            await _add_task_log(
                task_id=task_id,
                log_level="ERROR",
                message=f"任务执行失败: {str(e)}",
                agent_name="TaskExecutor",
                db=db
            )

            # 记录任务执行指标
            duration = time.time() - start_time
            record_task_execution(task_type=task_type, status='failed', duration=duration)
            task_running.labels(task_type=task_type).dec()

            return {"success": False, "error": str(e)}


async def _add_task_log(task_id: int, log_level: str, message: str, agent_name: str, db, extra_data: dict = None):
    """添加任务日志"""
    log = TaskLog(
        task_id=task_id,
        log_level=log_level,
        message=message,
        agent_name=agent_name,
        extra_data=extra_data
    )
    db.add(log)
    await db.commit()


async def _send_task_update(task: TaskModel, db):
    """发送任务更新到 WebSocket"""
    from app.schemas import TaskResponse

    await manager.send_task_update(
        task_data=TaskResponse.model_validate(task).model_dump(mode='json'),
        user_id=task.created_by
    )


def _get_task_type_name(task_type: str) -> str:
    """获取任务类型名称"""
    type_map = {
        "product_analysis": "选品分析",
        "content_generation": "内容生成",
        "image_generation": "图片生成",
        "video_generation": "视频生成",
        "review": "内容审核",
        "publish": "发布上架",
    }
    return type_map.get(task_type, task_type)
