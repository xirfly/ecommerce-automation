"""
认证工具函数
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.redis_client import async_redis_client
from app.constants import RedisKeys, RedisTTL
import json
import uuid


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"密码验证错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


async def create_access_token(user_id: int, username: str, role: str) -> tuple[str, str]:
    """
    创建访问令牌
    返回: (token, token_id)
    """
    token_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "token_id": token_id,
        "exp": expires_at,
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # 存储到Redis（异步）
    session_key = RedisKeys.session_user(user_id, token_id)
    await async_redis_client.setex(session_key, RedisTTL.SESSION_USER, json.dumps(payload))

    return token, token_id


def decode_token(token: str) -> dict:
    """解码Token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_token(token: str) -> dict:
    """验证Token是否有效"""
    payload = decode_token(token)

    user_id = int(payload.get("sub"))
    token_id = payload.get("token_id")

    # 验证Token是否在Redis中（异步）
    session_key = RedisKeys.session_user(user_id, token_id)
    if not await async_redis_client.exists(session_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已失效",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def revoke_token(user_id: int, token_id: str):
    """撤销Token"""
    session_key = RedisKeys.session_user(user_id, token_id)
    await async_redis_client.delete(session_key)


def get_user_permissions(role: str) -> list[str]:
    """根据角色获取权限列表"""
    permissions_map = {
        "admin": ["*"],  # 所有权限
        "operator": [
            "products:read",
            "products:write",
            "tasks:read",
            "tasks:write",
            "analytics:read",
        ],
        "viewer": [
            "products:read",
            "tasks:read",
            "analytics:read",
        ],
    }
    return permissions_map.get(role, [])
