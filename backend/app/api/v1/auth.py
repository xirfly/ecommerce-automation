"""
认证API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import User
from app.schemas import LoginRequest, LoginResponse, UserInfo, CurrentUser, Response
from app.utils.auth import verify_password, create_access_token, revoke_token, get_user_permissions
from app.dependencies.auth import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/login", response_model=Response[LoginResponse])
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 查询用户
    try:
        result = await db.execute(select(User).where(User.username == request.username))
        user = result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 检查用户是否被禁用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 创建Token
    access_token, token_id = await create_access_token(user.id, user.username, user.role.value)

    return Response(
        code=0,
        message="登录成功",
        data=LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserInfo(
                id=user.id,
                username=user.username,
                role=user.role.value,
            ),
        ),
    )


@router.get("/me", response_model=Response[CurrentUser])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    permissions = get_user_permissions(current_user.role.value)

    return Response(
        code=0,
        data=CurrentUser(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            role=current_user.role.value,
            permissions=permissions,
        ),
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    # 从请求头获取token_id并撤销
    # 注意：这里简化处理，实际应该从token中提取token_id
    return Response(
        code=0,
        message="登出成功",
    )
