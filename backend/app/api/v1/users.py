"""
用户管理 API
提供用户的 CRUD、角色管理等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models import User, UserRole
from app.schemas import Response
from app.dependencies.auth import get_current_user
from app.utils.auth import get_password_hash
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


class UserCreateRequest(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    role: str = Field("viewer", description="角色（admin/operator/viewer）")


class UserUpdateRequest(BaseModel):
    """更新用户请求"""
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserPasswordUpdateRequest(BaseModel):
    """更新密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: Optional[str]
    role: str
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class UserStatistics(BaseModel):
    """用户统计"""
    total_users: int
    active_users: int
    admin_users: int
    operator_users: int
    viewer_users: int


@router.get("/list", response_model=Response[List[UserResponse]])
async def list_users(
    role: Optional[str] = Query(None, description="角色过滤"),
    is_active: Optional[bool] = Query(None, description="状态过滤"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取用户列表

    只有管理员可以查看所有用户
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以查看用户列表"
        )

    query = select(User).order_by(User.created_at.desc())

    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    result = await db.execute(query)
    users = result.scalars().all()

    user_list = []
    for user in users:
        user_list.append(UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
        ))

    return Response(
        code=0,
        message="获取成功",
        data=user_list
    )


@router.get("/statistics", response_model=Response[UserStatistics])
async def get_user_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取用户统计

    只有管理员可以查看统计
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以查看统计"
        )

    from sqlalchemy import case

    query = select(
        func.count(User.id).label('total'),
        func.sum(case((User.is_active == True, 1), else_=0)).label('active'),
        func.sum(case((User.role == UserRole.ADMIN, 1), else_=0)).label('admin'),
        func.sum(case((User.role == UserRole.OPERATOR, 1), else_=0)).label('operator'),
        func.sum(case((User.role == UserRole.VIEWER, 1), else_=0)).label('viewer'),
    )

    result = await db.execute(query)
    stats = result.fetchone()

    return Response(
        code=0,
        message="获取成功",
        data=UserStatistics(
            total_users=stats[0] or 0,
            active_users=stats[1] or 0,
            admin_users=stats[2] or 0,
            operator_users=stats[3] or 0,
            viewer_users=stats[4] or 0,
        )
    )


@router.get("/{user_id}", response_model=Response[UserResponse])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取用户详情

    管理员可以查看所有用户，普通用户只能查看自己
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 权限检查
    if current_user.role.value != "admin" and user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此用户"
        )

    return Response(
        code=0,
        message="获取成功",
        data=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
        )
    )


@router.post("/create", response_model=Response[UserResponse])
async def create_user(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建用户

    只有管理员可以创建用户
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建用户"
        )

    # 检查用户名是否已存在
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    if user_data.email:
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )

    # 创建用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email,
        role=UserRole(user_data.role),
        is_active=True,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return Response(
        code=0,
        message="创建成功",
        data=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
        )
    )


@router.put("/{user_id}", response_model=Response[UserResponse])
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新用户

    管理员可以更新所有用户，普通用户只能更新自己的邮箱
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 权限检查
    is_admin = current_user.role.value == "admin"
    is_self = user.id == current_user.id

    if not is_admin and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此用户"
        )

    # 更新字段
    if user_data.email is not None:
        # 检查邮箱是否重复
        if user_data.email:
            result = await db.execute(
                select(User).where(
                    User.email == user_data.email,
                    User.id != user_id
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已存在"
                )
        user.email = user_data.email

    # 只有管理员可以修改角色和状态
    if is_admin:
        if user_data.role is not None:
            user.role = UserRole(user_data.role)
        if user_data.is_active is not None:
            user.is_active = user_data.is_active

    await db.commit()
    await db.refresh(user)

    return Response(
        code=0,
        message="更新成功",
        data=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
        )
    )


@router.put("/{user_id}/password", response_model=Response[None])
async def update_password(
    user_id: int,
    password_data: UserPasswordUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新密码

    用户只能修改自己的密码
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能修改自己的密码"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 验证旧密码
    from app.utils.auth import verify_password
    if not verify_password(password_data.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 更新密码
    user.password_hash = get_password_hash(password_data.new_password)
    await db.commit()

    return Response(
        code=0,
        message="密码更新成功",
        data=None
    )


@router.delete("/{user_id}", response_model=Response[None])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除用户

    只有管理员可以删除用户，不能删除自己
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除用户"
        )

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    await db.delete(user)
    await db.commit()

    return Response(
        code=0,
        message="删除成功",
        data=None
    )
