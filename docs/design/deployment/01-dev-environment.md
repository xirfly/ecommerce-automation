# 开发环境部署

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 环境要求

### 1.1 软件依赖

| 软件 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 后端开发 |
| Node.js | 18+ | 前端开发、OpenClaw |
| MySQL | 8.0+ | 数据库 |
| Redis | 7.0+ | 缓存/队列 |
| Git | 2.0+ | 版本控制 |

### 1.2 开发工具（推荐）

- **IDE：** VS Code / PyCharm
- **API测试：** Postman / Insomnia
- **数据库管理：** DBeaver / MySQL Workbench
- **Redis管理：** RedisInsight

---

## 2. 快速开始

### 2.1 克隆项目

```bash
git clone https://github.com/your-org/ecommerce-automation.git
cd ecommerce-automation
```

### 2.2 使用Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

**docker-compose.yml：**
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ecommerce_automation
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7.0
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - mysql
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    environment:
      REACT_APP_API_URL: http://localhost:8000

  celery:
    build: ./backend
    command: celery -A app.celery worker -l info
    depends_on:
      - redis
      - mysql
    volumes:
      - ./backend:/app

volumes:
  mysql_data:
  redis_data:
```

---

## 3. 手动部署

### 3.1 数据库配置

```bash
# 启动MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE ecommerce_automation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户（密码应从环境变量读取）
CREATE USER 'ecommerce'@'localhost' IDENTIFIED BY '${MYSQL_USER_PASSWORD}';
GRANT ALL PRIVILEGES ON ecommerce_automation.* TO 'ecommerce'@'localhost';
FLUSH PRIVILEGES;

# 导入表结构
mysql -u ecommerce -p ecommerce_automation < backend/sql/schema.sql
```

### 3.2 Redis配置

```bash
# 启动Redis
redis-server

# 测试连接
redis-cli ping
# 应返回：PONG
```

### 3.3 后端部署

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写数据库和Redis配置

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动Celery Worker（新终端）
celery -A app.celery worker -l info
```

**requirements.txt：**
```
fastapi==0.110.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
aiomysql==0.2.0
redis==5.0.1
celery==5.3.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
pydantic==2.6.0
pydantic-settings==2.1.0
```

### 3.4 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.local
# 编辑 .env.local，填写API地址

# 启动开发服务器
npm run dev
```

**package.json：**
```json
{
  "name": "ecommerce-automation-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "antd": "^5.12.0",
    "axios": "^1.6.0",
    "echarts": "^5.4.3",
    "echarts-for-react": "^3.0.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

### 3.5 OpenClaw Gateway配置

```bash
# 安装OpenClaw
npm install -g openclaw

# 初始化配置
openclaw setup --wizard

# 配置文件路径：~/.openclaw/openclaw.json
# 参考：docs/design/architecture/03-multi-channel.md

# 启动Gateway
openclaw start
```

---

## 4. 开发工作流

### 4.1 启动顺序

1. MySQL
2. Redis
3. OpenClaw Gateway
4. FastAPI后端
5. Celery Worker
6. React前端

### 4.2 常用命令

```bash
# 后端
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Celery
celery -A app.celery worker -l info

# 前端
cd frontend
npm run dev

# 数据库迁移
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

---

## 5. 调试技巧

### 5.1 后端调试

```python
# 使用debugpy
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

### 5.2 前端调试

- 使用Chrome DevTools
- React Developer Tools
- Redux DevTools（如果使用Redux）

### 5.3 数据库调试

```bash
# 查看慢查询
mysql -u root -p -e "SHOW VARIABLES LIKE 'slow_query%';"

# 查看当前连接
mysql -u root -p -e "SHOW PROCESSLIST;"
```

---

## 6. 常见问题

### 6.1 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 杀死进程
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### 6.2 数据库连接失败

- 检查MySQL是否启动
- 检查用户名密码是否正确
- 检查防火墙设置

### 6.3 Redis连接失败

- 检查Redis是否启动
- 检查端口是否正确（默认6379）

---

## 7. 相关文档

- [生产环境部署](02-prod-environment.md) - 生产环境配置
- [系统架构总览](../architecture/01-system-architecture.md) - 技术架构
