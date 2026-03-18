"""
用户反馈 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.feedback import Feedback, FeedbackStatus, FeedbackPriority
from app.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackUpdateRequest,
    FeedbackResponse,
    FeedbackListResponse,
)
from app.schemas.common import Response
from app.services.notification import NotificationManager
from app.core.logging_config import setup_logging
import os
import uuid
from pathlib import Path

logger = setup_logging()

router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])

# 文件上传目录
UPLOAD_DIR = Path("uploads/feedback")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 文件大小限制（5MB）
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/upload-image", response_model=Response[dict])
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """上传反馈图片"""
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        return Response(code=400, message="不支持的图片格式，仅支持 JPG、PNG、GIF、WebP")

    # 读取文件内容
    try:
        content = await file.read()

        # 验证文件大小
        if len(content) > MAX_FILE_SIZE:
            return Response(code=400, message=f"图片大小不能超过 {MAX_FILE_SIZE // 1024 // 1024}MB")

        # 验证文件不为空
        if len(content) == 0:
            return Response(code=400, message="图片文件为空")

        # 生成唯一文件名
        ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = UPLOAD_DIR / filename

        # 保存文件
        with open(filepath, "wb") as f:
            f.write(content)

        # 返回访问URL
        url = f"/uploads/feedback/{filename}"
        return Response(code=0, message="上传成功", data={"url": url})
    except Exception as e:
        return Response(code=500, message=f"上传失败: {str(e)}")


@router.post("/create", response_model=Response[FeedbackResponse])
async def create_feedback(
    feedback_data: FeedbackCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建反馈"""
    feedback = Feedback(
        user_id=current_user.id,
        title=feedback_data.title,
        description=feedback_data.description,
        images=feedback_data.images,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    # 发送通知
    try:
        await NotificationManager.notify_feedback_submitted(
            db=db,
            feedback_id=feedback.id,
            title=feedback.title,
            username=current_user.username,
        )
    except Exception as e:
        # 通知失败不影响反馈创建
        logger.error(f"发送反馈通知失败: {str(e)}")

    # 构建响应
    response_data = FeedbackResponse(
        id=feedback.id,
        user_id=feedback.user_id,
        username=current_user.username,
        title=feedback.title,
        description=feedback.description,
        images=feedback.images,
        status=feedback.status.value,
        priority=feedback.priority.value,
        admin_reply=feedback.admin_reply,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at,
    )

    return Response(code=0, message="提交成功", data=response_data)


@router.get("/list", response_model=Response[FeedbackListResponse])
async def get_feedback_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取反馈列表（管理员查看所有，普通用户只看自己的）"""
    # 构建查询
    query = select(Feedback).options(joinedload(Feedback.user))

    # 权限控制：非管理员只能看自己的反馈
    if current_user.role != "admin":
        query = query.where(Feedback.user_id == current_user.id)
    else:
        # 管理员可以按用户ID筛选
        if user_id:
            query = query.where(Feedback.user_id == user_id)

    # 状态筛选
    if status:
        query = query.where(Feedback.status == status)

    # 优先级筛选
    if priority:
        query = query.where(Feedback.priority == priority)

    # 按创建时间倒序
    query = query.order_by(desc(Feedback.created_at))

    # 计算总数
    count_query = select(func.count()).select_from(Feedback)
    if current_user.role != "admin":
        count_query = count_query.where(Feedback.user_id == current_user.id)
    else:
        if user_id:
            count_query = count_query.where(Feedback.user_id == user_id)
    if status:
        count_query = count_query.where(Feedback.status == status)
    if priority:
        count_query = count_query.where(Feedback.priority == priority)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    feedbacks = result.scalars().all()

    # 构建响应
    items = [
        FeedbackResponse(
            id=f.id,
            user_id=f.user_id,
            username=f.user.username if f.user else None,
            title=f.title,
            description=f.description,
            images=f.images,
            status=f.status.value,
            priority=f.priority.value,
            admin_reply=f.admin_reply,
            created_at=f.created_at,
            updated_at=f.updated_at,
        )
        for f in feedbacks
    ]

    return Response(
        code=0,
        message="获取成功",
        data=FeedbackListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        ),
    )


@router.get("/{feedback_id}", response_model=Response[FeedbackResponse])
async def get_feedback_detail(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取反馈详情"""
    query = select(Feedback).options(joinedload(Feedback.user)).where(Feedback.id == feedback_id)
    result = await db.execute(query)
    feedback = result.scalar_one_or_none()

    if not feedback:
        return Response(code=404, message="反馈不存在")

    # 权限检查：非管理员只能查看自己的反馈
    if current_user.role != "admin" and feedback.user_id != current_user.id:
        return Response(code=403, message="无权访问")

    response_data = FeedbackResponse(
        id=feedback.id,
        user_id=feedback.user_id,
        username=feedback.user.username if feedback.user else None,
        title=feedback.title,
        description=feedback.description,
        images=feedback.images,
        status=feedback.status.value,
        priority=feedback.priority.value,
        admin_reply=feedback.admin_reply,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at,
    )

    return Response(code=0, message="获取成功", data=response_data)


@router.put("/{feedback_id}", response_model=Response[FeedbackResponse])
async def update_feedback(
    feedback_id: int,
    update_data: FeedbackUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新反馈（管理员）"""
    if current_user.role != "admin":
        return Response(code=403, message="无权操作")

    query = select(Feedback).options(joinedload(Feedback.user)).where(Feedback.id == feedback_id)
    result = await db.execute(query)
    feedback = result.scalar_one_or_none()

    if not feedback:
        return Response(code=404, message="反馈不存在")

    # 更新字段
    if update_data.status:
        feedback.status = FeedbackStatus(update_data.status)
    if update_data.priority:
        feedback.priority = FeedbackPriority(update_data.priority)
    if update_data.admin_reply is not None:
        feedback.admin_reply = update_data.admin_reply

    await db.commit()
    await db.refresh(feedback)

    response_data = FeedbackResponse(
        id=feedback.id,
        user_id=feedback.user_id,
        username=feedback.user.username if feedback.user else None,
        title=feedback.title,
        description=feedback.description,
        images=feedback.images,
        status=feedback.status.value,
        priority=feedback.priority.value,
        admin_reply=feedback.admin_reply,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at,
    )

    return Response(code=0, message="更新成功", data=response_data)


@router.delete("/{feedback_id}", response_model=Response[None])
async def delete_feedback(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除反馈（管理员）"""
    if current_user.role != "admin":
        return Response(code=403, message="无权操作")

    query = select(Feedback).where(Feedback.id == feedback_id)
    result = await db.execute(query)
    feedback = result.scalar_one_or_none()

    if not feedback:
        return Response(code=404, message="反馈不存在")

    await db.delete(feedback)
    await db.commit()

    return Response(code=0, message="删除成功")


@router.get("/statistics/summary", response_model=Response[dict])
async def get_feedback_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取反馈统计（管理员）"""
    if current_user.role != "admin":
        return Response(code=403, message="无权访问")

    # 统计各状态数量
    status_query = select(
        Feedback.status,
        func.count(Feedback.id).label("count")
    ).group_by(Feedback.status)
    status_result = await db.execute(status_query)
    status_stats = {row[0].value: row[1] for row in status_result}

    # 统计各优先级数量
    priority_query = select(
        Feedback.priority,
        func.count(Feedback.id).label("count")
    ).group_by(Feedback.priority)
    priority_result = await db.execute(priority_query)
    priority_stats = {row[0].value: row[1] for row in priority_result}

    # 总数
    total_query = select(func.count(Feedback.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    return Response(
        code=0,
        message="获取成功",
        data={
            "total": total,
            "by_status": status_stats,
            "by_priority": priority_stats,
        },
    )
