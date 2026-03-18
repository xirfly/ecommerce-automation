# 用户权限模块

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 目标

实现基于角色的访问控制（RBAC），支持：
- 用户认证（JWT）
- 角色管理
- 权限控制
- 用户管理

---

## 2. 角色定义

| 角色 | 权限范围 | 典型用户 |
|------|----------|----------|
| **admin** | 全部功能 | 老板、技术负责人 |
| **operator** | 产品管理 + 任务执行 + 数据查看 | 运营专员 |
| **viewer** | 只读权限 | 实习生、外部顾问 |

---

## 3. 权限矩阵

| 功能模块 | admin | operator | viewer |
|---------|-------|----------|--------|
| 仪表盘 | ✅ 全局 | ✅ 团队 | ✅ 只读 |
| 产品管理 | ✅ 增删改查 | ✅ 增删改查 | ✅ 只读 |
| 任务中心 | ✅ 全部 | ✅ 自己的 | ✅ 只读 |
| 数据分析 | ✅ 全局 | ✅ 团队 | ✅ 只读 |
| 渠道配置 | ✅ 增删改查 | ❌ | ❌ |
| 用户管理 | ✅ 增删改查 | ❌ | ❌ |
| 系统设置 | ✅ 全部 | ❌ | ❌ |

---

## 4. API设计

### 4.1 用户登录

```http
POST /api/v1/auth/login
Content-Type: application/json

Request Body:
{
  "username": "admin",
  "password": "password123"
}

Response (200 OK):
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
}
```

### 4.2 获取当前用户

```http
GET /api/v1/auth/me
Authorization: Bearer {token}

Response (200 OK):
{
  "code": 0,
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "permissions": ["*"]
  }
}
```

---

## 5. JWT实现

### 5.1 Token生成

```python
from datetime import datetime, timedelta
from jose import jwt
from app.constants import RedisKeys, RedisTTL
from app.config import settings

# 从环境变量读取密钥
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"

def create_access_token(user_id: int, username: str, role: str) -> str:
    """创建访问令牌"""
    token_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=1)

    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "token_id": token_id,
        "exp": expires_at
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # 存储到Redis
    session_key = RedisKeys.session_user(user_id, token_id)
    redis.setex(session_key, RedisTTL.SESSION_USER, json.dumps(payload))

    return token
```

### 5.2 权限验证装饰器

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> User:
    """获取当前用户"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        token_id = payload.get("token_id")

        # 验证Token是否在Redis中
        session_key = RedisKeys.session_user(user_id, token_id)
        if not redis.exists(session_key):
            raise HTTPException(status_code=401, detail="Token已失效")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token无效")

def require_role(*allowed_roles: str):
    """角色权限装饰器"""
    def decorator(func):
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(status_code=403, detail="权限不足")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# 使用示例
@router.post("/channels")
@require_role("admin")
async def create_channel(data: ChannelCreate, current_user: User = Depends(get_current_user)):
    """创建渠道（仅管理员）"""
    pass
```

---

## 6. 前端权限控制

### 6.1 路由守卫

```typescript
// src/router/guards.ts
import { useAuthStore } from '@/stores/auth';

export function setupRouterGuards(router: Router) {
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();

    // 需要登录的页面
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } });
      return;
    }

    // 需要特定角色的页面
    if (to.meta.roles && !to.meta.roles.includes(authStore.user?.role)) {
      next({ name: 'Forbidden' });
      return;
    }

    next();
  });
}
```

### 6.2 组件级权限

```tsx
// src/components/PermissionGuard.tsx
interface Props {
  roles?: string[];
  children: React.ReactNode;
}

const PermissionGuard: React.FC<Props> = ({ roles, children }) => {
  const { user } = useAuth();

  if (roles && !roles.includes(user?.role)) {
    return null;
  }

  return <>{children}</>;
};

// 使用示例
<PermissionGuard roles={['admin']}>
  <Button onClick={handleDelete}>删除</Button>
</PermissionGuard>
```

---

## 7. 相关文档

- [数据模型设计](../database/01-data-model.md) - users表
- [Redis数据结构](../database/02-redis-structure.md) - 会话存储
