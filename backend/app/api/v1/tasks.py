"""
任务API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.core.database import get_db
from app.models import User, Task, TaskLog, Product, TaskStatus
from app.schemas import (
    TaskCreate,
    TaskResponse,
    TaskListResponse,
    TaskLogResponse,
    Response,
)
from app.dependencies.auth import get_current_user, require_operator
from app.websocket.websocket_manager import manager
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/v1/tasks", tags=["任务管理"])


@router.get("", response_model=Response[TaskListResponse])
async def get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    product_id: Optional[int] = Query(None, description="产品ID"),
    task_type: Optional[str] = Query(None, description="任务类型"),
    status: Optional[str] = Query(None, description="任务状态"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取任务列表"""
    # 构建查询
    query = select(Task)

    # 产品筛选
    if product_id:
        query = query.where(Task.product_id == product_id)

    # 任务类型筛选
    if task_type:
        query = query.where(Task.task_type == task_type)

    # 状态筛选
    if status:
        query = query.where(Task.status == status)

    # 权限过滤（非管理员只能看自己的）
    if current_user.role.value != "admin":
        query = query.where(Task.created_by == current_user.id)

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Task.created_at.desc())

    # 执行查询
    result = await db.execute(query)
    tasks = result.scalars().all()

    return Response(
        code=0,
        data=TaskListResponse(
            items=[TaskResponse.model_validate(t) for t in tasks],
            total=total,
            page=page,
            page_size=page_size,
        ),
    )


@router.get("/{task_id}", response_model=Response[TaskResponse])
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取任务详情"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    # 权限检查（非管理员只能看自己的）
    if current_user.role.value != "admin" and task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务",
        )

    return Response(
        code=0,
        data=TaskResponse.model_validate(task),
    )


@router.post("", response_model=Response[TaskResponse])
async def create_task(
    request: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    """创建任务"""
    # 检查产品是否存在
    product_result = await db.execute(
        select(Product).where(Product.id == request.product_id)
    )
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在",
        )

    # 权限检查（非管理员只能为自己的产品创建任务）
    if current_user.role.value != "admin" and product.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权为此产品创建任务",
        )

    # 生成任务ID
    celery_task_id = str(uuid.uuid4())

    # 创建任务
    task = Task(
        task_id=celery_task_id,
        product_id=request.product_id,
        task_type=request.task_type,
        status=TaskStatus.PENDING,
        created_by=current_user.id,
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    # 提交到 Celery 异步执行
    from app.workers.tasks import execute_task
    execute_task.delay(task.id, request.task_type)

    # 立即返回响应，不等待 WebSocket
    response_data = TaskResponse.model_validate(task)

    # 后台发送 WebSocket 通知（不阻塞）
    import asyncio
    asyncio.create_task(manager.send_task_update(
        task_data=response_data.model_dump(mode='json'),
        user_id=current_user.id
    ))
    asyncio.create_task(manager.send_notification(
        title="任务创建成功",
        content=f"任务 #{task.id} 已创建",
        user_id=current_user.id,
        level="success"
    ))

    return Response(
        code=0,
        message="任务创建成功",
        data=response_data,
    )


@router.post("/{task_id}/retry", response_model=Response[TaskResponse])
async def retry_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    """重试任务"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    # 权限检查
    if current_user.role.value != "admin" and task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权重试此任务",
        )

    # 只有失败或超时的任务可以重试
    if task.status not in [TaskStatus.FAILED, TaskStatus.TIMEOUT]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有失败或超时的任务可以重试",
        )

    # 更新任务状态
    task.status = TaskStatus.PENDING
    task.retry_count += 1
    task.error_message = None
    task.started_at = None
    task.completed_at = None

    await db.commit()
    await db.refresh(task)

    # 重新提交到 Celery
    from app.tasks import execute_task
    execute_task.delay(task.id, task.task_type)

    # WebSocket 推送任务重试通知
    await manager.send_task_update(
        task_data=TaskResponse.model_validate(task).model_dump(),
        user_id=current_user.id
    )
    await manager.send_notification(
        title="任务重试",
        content=f"任务 #{task.id} 已重新提交",
        user_id=current_user.id,
        level="info"
    )

    return Response(
        code=0,
        message="任务已重新提交",
        data=TaskResponse.model_validate(task),
    )


@router.get("/{task_id}/logs", response_model=Response[List[TaskLogResponse]])
async def get_task_logs(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取任务日志"""
    # 检查任务是否存在
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    task = task_result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    # 权限检查
    if current_user.role.value != "admin" and task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务日志",
        )

    # 查询日志
    result = await db.execute(
        select(TaskLog)
        .where(TaskLog.task_id == task_id)
        .order_by(TaskLog.created_at.asc())
    )
    logs = result.scalars().all()

    return Response(
        code=0,
        data=[TaskLogResponse.model_validate(log) for log in logs],
    )


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    """删除任务"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    # 权限检查
    if current_user.role.value != "admin" and task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此任务",
        )

    # 不能删除正在运行的任务
    if task.status == TaskStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除正在运行的任务",
        )

    await db.delete(task)
    await db.commit()

    return Response(
        code=0,
        message="删除成功",
    )
