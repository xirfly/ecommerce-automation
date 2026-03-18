# 快速启动脚本

## Windows (PowerShell)
```powershell
# 从backend目录启动
cd D:\Desktop\ai-agent\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Linux/Mac (Bash)
```bash
# 从backend目录启动
cd /path/to/ai-agent/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 或者使用启动脚本
```bash
cd backend
python run.py
```

## 访问
- API文档 (Swagger): http://localhost:8000/docs
- API文档 (ReDoc): http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health
