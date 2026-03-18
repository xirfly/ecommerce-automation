"""
渠道管理 API
提供渠道的 CRUD、测试连接、统计等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.core.database import get_db
from app.models import User, Channel, ChannelType, ChannelStatus
from app.schemas import Response
from app.schemas.channel import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    ChannelTestRequest,
    ChannelTestResponse,
    ChannelStatistics,
)
from app.dependencies.auth import get_current_user
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/channels", tags=["渠道管理"])


@router.get("/list", response_model=Response[List[ChannelResponse]])
async def list_channels(
    channel_type: Optional[str] = Query(None, description="渠道类型过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取渠道列表

    支持按渠道类型和状态过滤
    """
    query = select(Channel).order_by(Channel.created_at.desc())

    # 过滤条件
    if channel_type:
        query = query.where(Channel.channel_type == channel_type)
    if status:
        query = query.where(Channel.status == status)

    # 非管理员只能看到自己创建的
    if current_user.role.value != "admin":
        query = query.where(Channel.created_by == current_user.id)

    result = await db.execute(query)
    channels = result.scalars().all()

    # 转换为响应格式
    channel_list = []
    for channel in channels:
        channel_list.append(ChannelResponse(
            id=channel.id,
            name=channel.name,
            channel_type=channel.channel_type.value,
            platform=channel.platform,
            description=channel.description,
            config=channel.config,
            status=channel.status.value,
            is_default=channel.is_default,
            usage_count=channel.usage_count,
            last_used_at=channel.last_used_at,
            last_error=channel.last_error,
            created_by=channel.created_by,
            created_at=channel.created_at.isoformat() if channel.created_at else None,
            updated_at=channel.updated_at.isoformat() if channel.updated_at else None,
        ))

    return Response(
        code=0,
        message="获取成功",
        data=channel_list
    )


@router.get("/{channel_id}", response_model=Response[ChannelResponse])
async def get_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取渠道详情
    """
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="渠道不存在"
        )

    # 权限检查
    if current_user.role.value != "admin" and channel.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此渠道"
        )

    return Response(
        code=0,
        message="获取成功",
        data=ChannelResponse(
            id=channel.id,
            name=channel.name,
            channel_type=channel.channel_type.value,
            platform=channel.platform,
            description=channel.description,
            config=channel.config,
            status=channel.status.value,
            is_default=channel.is_default,
            usage_count=channel.usage_count,
            last_used_at=channel.last_used_at,
            last_error=channel.last_error,
            created_by=channel.created_by,
            created_at=channel.created_at.isoformat() if channel.created_at else None,
            updated_at=channel.updated_at.isoformat() if channel.updated_at else None,
        )
    )


@router.post("/create", response_model=Response[ChannelResponse])
async def create_channel(
    channel_data: ChannelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建渠道
    """
    # 检查渠道名称是否已存在
    result = await db.execute(
        select(Channel).where(Channel.name == channel_data.name)
    )
    existing_channel = result.scalar_one_or_none()
    if existing_channel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="渠道名称已存在"
        )

    # 如果设置为默认渠道，取消其他同类型的默认渠道
    if channel_data.is_default:
        result = await db.execute(
            select(Channel).where(
                Channel.channel_type == channel_data.channel_type,
                Channel.is_default == True
            )
        )
        default_channels = result.scalars().all()
        for ch in default_channels:
            ch.is_default = False

    # 创建渠道
    channel = Channel(
        name=channel_data.name,
        channel_type=ChannelType(channel_data.channel_type),
        platform=channel_data.platform,
        description=channel_data.description,
        config=channel_data.config,
        is_default=channel_data.is_default,
        status=ChannelStatus.ACTIVE,
        created_by=current_user.id,
    )

    db.add(channel)
    await db.commit()
    await db.refresh(channel)

    return Response(
        code=0,
        message="创建成功",
        data=ChannelResponse(
            id=channel.id,
            name=channel.name,
            channel_type=channel.channel_type.value,
            platform=channel.platform,
            description=channel.description,
            config=channel.config,
            status=channel.status.value,
            is_default=channel.is_default,
            usage_count=channel.usage_count,
            last_used_at=channel.last_used_at,
            last_error=channel.last_error,
            created_by=channel.created_by,
            created_at=channel.created_at.isoformat() if channel.created_at else None,
            updated_at=channel.updated_at.isoformat() if channel.updated_at else None,
        )
    )


@router.put("/{channel_id}", response_model=Response[ChannelResponse])
async def update_channel(
    channel_id: int,
    channel_data: ChannelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新渠道
    """
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="渠道不存在"
        )

    # 权限检查
    if current_user.role.value != "admin" and channel.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此渠道"
        )

    # 更新字段
    if channel_data.name is not None:
        # 检查名称是否重复
        result = await db.execute(
            select(Channel).where(
                Channel.name == channel_data.name,
                Channel.id != channel_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="渠道名称已存在"
            )
        channel.name = channel_data.name

    if channel_data.description is not None:
        channel.description = channel_data.description
    if channel_data.config is not None:
        channel.config = channel_data.config
    if channel_data.status is not None:
        channel.status = ChannelStatus(channel_data.status)
    if channel_data.is_default is not None:
        # 如果设置为默认，取消其他同类型的默认渠道
        if channel_data.is_default:
            result = await db.execute(
                select(Channel).where(
                    Channel.channel_type == channel.channel_type,
                    Channel.is_default == True,
                    Channel.id != channel_id
                )
            )
            default_channels = result.scalars().all()
            for ch in default_channels:
                ch.is_default = False
        channel.is_default = channel_data.is_default

    await db.commit()
    await db.refresh(channel)

    return Response(
        code=0,
        message="更新成功",
        data=ChannelResponse(
            id=channel.id,
            name=channel.name,
            channel_type=channel.channel_type.value,
            platform=channel.platform,
            description=channel.description,
            config=channel.config,
            status=channel.status.value,
            is_default=channel.is_default,
            usage_count=channel.usage_count,
            last_used_at=channel.last_used_at,
            last_error=channel.last_error,
            created_by=channel.created_by,
            created_at=channel.created_at.isoformat() if channel.created_at else None,
            updated_at=channel.updated_at.isoformat() if channel.updated_at else None,
        )
    )


@router.delete("/{channel_id}", response_model=Response[None])
async def delete_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除渠道
    """
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="渠道不存在"
        )

    # 权限检查
    if current_user.role.value != "admin" and channel.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此渠道"
        )

    await db.delete(channel)
    await db.commit()

    return Response(
        code=0,
        message="删除成功",
        data=None
    )


@router.post("/test", response_model=Response[ChannelTestResponse])
async def test_channel(
    test_data: ChannelTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    测试渠道连接

    验证渠道配置是否正确，能否正常连接
    """
    result = await db.execute(select(Channel).where(Channel.id == test_data.channel_id))
    channel = result.scalar_one_or_none()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="渠道不存在"
        )

    # 权限检查
    if current_user.role.value != "admin" and channel.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权测试此渠道"
        )

    # TODO: 实现真实的渠道测试逻辑
    # 这里先返回模拟数据
    test_result = ChannelTestResponse(
        success=True,
        message=f"渠道 {channel.name} 连接测试成功",
        details={
            "platform": channel.platform,
            "test_time": datetime.now().isoformat(),
            "response_time": "120ms"
        }
    )

    return Response(
        code=0,
        message="测试完成",
        data=test_result
    )


@router.get("/statistics/summary", response_model=Response[ChannelStatistics])
async def get_channel_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取渠道统计信息
    """
    # 构建查询
    query = select(
        func.count(Channel.id).label('total'),
        func.sum(case((Channel.status == ChannelStatus.ACTIVE, 1), else_=0)).label('active'),
        func.sum(case((Channel.channel_type == ChannelType.ECOMMERCE, 1), else_=0)).label('ecommerce'),
        func.sum(case((Channel.channel_type == ChannelType.NOTIFICATION, 1), else_=0)).label('notification'),
        func.sum(Channel.usage_count).label('total_usage')
    )

    # 非管理员只统计自己的
    if current_user.role.value != "admin":
        query = query.where(Channel.created_by == current_user.id)

    result = await db.execute(query)
    stats = result.fetchone()

    return Response(
        code=0,
        message="获取成功",
        data=ChannelStatistics(
            total_channels=stats[0] or 0,
            active_channels=stats[1] or 0,
            ecommerce_channels=stats[2] or 0,
            notification_channels=stats[3] or 0,
            total_usage=stats[4] or 0,
        )
    )
