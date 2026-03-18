"""
Celery Worker 启动脚本
"""
import sys
import os
from pathlib import Path

# 强制使用 UTF-8 编码
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.workers.celery_app import celery_app
# 显式导入任务模块以确保任务被注册
from app.workers import tasks  # noqa: F401
from app.workers.startup_tasks import run_startup_tasks

if __name__ == "__main__":
    # 启动时处理待执行任务
    run_startup_tasks()

    # 启动 Celery Worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=4",
        "--pool=solo",  # Windows 使用 solo 模式
    ])
