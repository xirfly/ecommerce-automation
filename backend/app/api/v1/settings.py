"""
系统配置管理 API
提供系统配置的 CRUD 和批量更新功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import User, SystemConfig
from app.schemas import Response
from app.schemas.system_config import (
    SystemConfigCreate,
    SystemConfigUpdate,
    SystemConfigResponse,
    SystemConfigBatchUpdate,
    SystemSettingsResponse,
)
from app.dependencies.auth import get_current_user
from typing import List, Dict, Any
import json

router = APIRouter(prefix="/api/v1/settings", tags=["系统设置"])


def parse_config_value(value: str, config_type: str) -> Any:
    """解析配置值"""
    if value is None:
        return None

    if config_type == "int":
        return int(value)
    elif config_type == "bool":
        return value.lower() in ("true", "1", "yes")
    elif config_type == "json":
        return json.loads(value)
    else:
        return value


def serialize_config_value(value: Any) -> str:
    """序列化配置值"""
    if value is None:
        return None

    if isinstance(value, (dict, list)):
        return json.dumps(value)
    else:
        return str(value)


@router.get("/all", response_model=Response[SystemSettingsResponse])
async def get_all_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取所有系统设置（按分类组织）

    只有管理员可以查看所有设置，普通用户只能查看公开设置
    """
    query = select(SystemConfig)

    # 非管理员只能查看公开配置
    if current_user.role.value != "admin":
        query = query.where(SystemConfig.is_public == True)

    result = await db.execute(query)
    configs = result.scalars().all()

    # 按分类组织配置
    settings = {
        "basic": {},
        "ai": {},
        "task": {},
        "notification": {},
        "security": {},
    }

    for config in configs:
        category = config.category
        if category in settings:
            # 解析配置值
            value = parse_config_value(config.config_value, config.config_type)
            settings[category][config.config_key] = {
                "value": value,
                "type": config.config_type,
                "description": config.description,
                "is_public": config.is_public,
            }

    return Response(
        code=0,
        message="获取成功",
        data=SystemSettingsResponse(**settings)
    )


@router.get("/list", response_model=Response[List[SystemConfigResponse]])
async def list_configs(
    category: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取系统配置列表

    支持按分类过滤
    """
    query = select(SystemConfig)

    if category:
        query = query.where(SystemConfig.category == category)

    # 非管理员只能查看公开配置
    if current_user.role.value != "admin":
        query = query.where(SystemConfig.is_public == True)

    result = await db.execute(query)
    configs = result.scalars().all()

    config_list = []
    for config in configs:
        config_list.append(SystemConfigResponse(
            id=config.id,
            config_key=config.config_key,
            config_value=config.config_value,
            config_type=config.config_type,
            category=config.category,
            description=config.description,
            is_public=config.is_public,
            is_encrypted=config.is_encrypted,
            created_at=config.created_at.isoformat() if config.created_at else None,
            updated_at=config.updated_at.isoformat() if config.updated_at else None,
        ))

    return Response(
        code=0,
        message="获取成功",
        data=config_list
    )


@router.get("/{config_key}", response_model=Response[SystemConfigResponse])
async def get_config(
    config_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取指定配置
    """
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.config_key == config_key)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )

    # 权限检查
    if current_user.role.value != "admin" and not config.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此配置"
        )

    return Response(
        code=0,
        message="获取成功",
        data=SystemConfigResponse(
            id=config.id,
            config_key=config.config_key,
            config_value=config.config_value,
            config_type=config.config_type,
            category=config.category,
            description=config.description,
            is_public=config.is_public,
            is_encrypted=config.is_encrypted,
            created_at=config.created_at.isoformat() if config.created_at else None,
            updated_at=config.updated_at.isoformat() if config.updated_at else None,
        )
    )


@router.post("/create", response_model=Response[SystemConfigResponse])
async def create_config(
    config_data: SystemConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建系统配置

    只有管理员可以创建配置
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建配置"
        )

    # 检查配置键是否已存在
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.config_key == config_data.config_key)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="配置键已存在"
        )

    # 创建配置
    config = SystemConfig(
        config_key=config_data.config_key,
        config_value=config_data.config_value,
        config_type=config_data.config_type,
        category=config_data.category,
        description=config_data.description,
        is_public=config_data.is_public,
        is_encrypted=config_data.is_encrypted,
    )

    db.add(config)
    await db.commit()
    await db.refresh(config)

    return Response(
        code=0,
        message="创建成功",
        data=SystemConfigResponse(
            id=config.id,
            config_key=config.config_key,
            config_value=config.config_value,
            config_type=config.config_type,
            category=config.category,
            description=config.description,
            is_public=config.is_public,
            is_encrypted=config.is_encrypted,
            created_at=config.created_at.isoformat() if config.created_at else None,
            updated_at=config.updated_at.isoformat() if config.updated_at else None,
        )
    )


@router.put("/{config_key}", response_model=Response[SystemConfigResponse])
async def update_config(
    config_key: str,
    config_data: SystemConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新系统配置

    只有管理员可以更新配置
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以更新配置"
        )

    result = await db.execute(
        select(SystemConfig).where(SystemConfig.config_key == config_key)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )

    # 更新字段
    if config_data.config_value is not None:
        config.config_value = config_data.config_value
    if config_data.description is not None:
        config.description = config_data.description
    if config_data.is_public is not None:
        config.is_public = config_data.is_public

    await db.commit()
    await db.refresh(config)

    return Response(
        code=0,
        message="更新成功",
        data=SystemConfigResponse(
            id=config.id,
            config_key=config.config_key,
            config_value=config.config_value,
            config_type=config.config_type,
            category=config.category,
            description=config.description,
            is_public=config.is_public,
            is_encrypted=config.is_encrypted,
            created_at=config.created_at.isoformat() if config.created_at else None,
            updated_at=config.updated_at.isoformat() if config.updated_at else None,
        )
    )


@router.post("/batch-update", response_model=Response[Dict[str, Any]])
async def batch_update_configs(
    batch_data: SystemConfigBatchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    批量更新系统配置

    只有管理员可以批量更新配置
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以更新配置"
        )

    updated_count = 0
    created_count = 0

    for config_item in batch_data.configs:
        config_key = config_item.get("config_key")
        config_value = config_item.get("config_value")

        if not config_key:
            continue

        # 查找配置
        result = await db.execute(
            select(SystemConfig).where(SystemConfig.config_key == config_key)
        )
        config = result.scalar_one_or_none()

        if config:
            # 更新现有配置
            config.config_value = serialize_config_value(config_value)
            updated_count += 1
        else:
            # 创建新配置
            config = SystemConfig(
                config_key=config_key,
                config_value=serialize_config_value(config_value),
                config_type=config_item.get("config_type", "string"),
                category=config_item.get("category", "basic"),
                description=config_item.get("description"),
                is_public=config_item.get("is_public", False),
                is_encrypted=config_item.get("is_encrypted", False),
            )
            db.add(config)
            created_count += 1

    await db.commit()

    return Response(
        code=0,
        message="批量更新成功",
        data={
            "updated": updated_count,
            "created": created_count,
            "total": updated_count + created_count,
        }
    )


@router.delete("/{config_key}", response_model=Response[None])
async def delete_config(
    config_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除系统配置

    只有管理员可以删除配置
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除配置"
        )

    result = await db.execute(
        select(SystemConfig).where(SystemConfig.config_key == config_key)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )

    await db.delete(config)
    await db.commit()

    return Response(
        code=0,
        message="删除成功",
        data=None
    )
