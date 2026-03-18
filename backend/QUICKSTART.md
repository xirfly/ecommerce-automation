# 快速启动指南

## ⚠️ 重要提示
**必须从 backend 目录启动，不是 app 目录！**

## 🚀 启动步骤

### 1. 进入正确的目录
```powershell
cd D:\Desktop\ai-agent\backend
```

### 2. 激活虚拟环境（如果还没激活）
```powershell
.\venv\Scripts\activate
# 或者
conda activate intelli-serve
```

### 3. 启动服务
```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 🔧 常见问题

### 问题1: ModuleNotFoundError: No module named 'app'
**原因**: 在错误的目录运行
**解决**: 必须在 `backend` 目录，不是 `app` 目录
```powershell
pwd  # 应该显示 D:\Desktop\ai-agent\backend
```

### 问题2: ValidationError: Field required
**原因**: 缺少 .env 文件或配置不完整
**解决**:
```powershell
# 检查 .env 文件是否存在
ls .env

# 如果不存在，复制模板
cp .env.example .env
```

### 问题3: 端口被占用
**解决**: 换个端口
```powershell
python -m uvicorn app.main:app --reload --port 8001
```

## 📝 默认配置

- 数据库: `mysql://root:root@localhost:3306/ecommerce_automation`
- Redis: `redis://localhost:6379/0`
- 端口: `8000`
- 默认账号: `admin / admin123`

## 🎯 测试登录

1. 访问 http://localhost:8000/docs
2. 点击 `POST /api/v1/auth/login`
3. 点击 "Try it out"
4. 输入:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
5. 点击 "Execute"
6. 复制返回的 `access_token`
7. 点击页面右上角 "Authorize" 按钮
8. 输入 `Bearer {token}`
9. 现在可以测试其他API了！
