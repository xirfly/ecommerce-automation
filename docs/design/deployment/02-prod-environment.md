# 生产环境部署

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 架构设计

### 1.1 生产环境架构

```
┌─────────────────────────────────────────────────────────┐
│                    负载均衡（Nginx）                     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              应用服务器（多实例）                        │
│  FastAPI (Gunicorn + Uvicorn) × 3                       │
│  OpenClaw Gateway × 1                                    │
│  Celery Worker × 3                                       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    数据层                                │
│  MySQL (主从复制)  |  Redis (哨兵模式)                  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 服务器配置

### 2.1 推荐配置

**应用服务器：**
- CPU：4核+
- 内存：8GB+
- 硬盘：100GB+ SSD
- 操作系统：Ubuntu 22.04 LTS

**数据库服务器：**
- CPU：4核+
- 内存：16GB+
- 硬盘：200GB+ SSD
- 操作系统：Ubuntu 22.04 LTS

---

## 3. Nginx配置

### 3.1 反向代理配置

```nginx
# /etc/nginx/sites-available/ecommerce-automation
upstream backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name your-domain.com;

    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL证书
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # 前端静态文件
    location / {
        root /var/www/ecommerce-automation/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 4. FastAPI部署

### 4.1 使用Gunicorn + Uvicorn

```bash
# 安装
pip install gunicorn uvicorn[standard]

# 启动（3个worker）
gunicorn app.main:app \
  --workers 3 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --access-logfile /var/log/ecommerce/access.log \
  --error-logfile /var/log/ecommerce/error.log \
  --daemon
```

### 4.2 Systemd服务配置

```ini
# /etc/systemd/system/ecommerce-backend.service
[Unit]
Description=Ecommerce Automation Backend
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/ecommerce-automation/backend
Environment="PATH=/var/www/ecommerce-automation/backend/venv/bin"
ExecStart=/var/www/ecommerce-automation/backend/venv/bin/gunicorn \
  app.main:app \
  --workers 3 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable ecommerce-backend
sudo systemctl start ecommerce-backend
sudo systemctl status ecommerce-backend
```

---

## 5. Celery部署

### 5.1 Systemd服务配置

```ini
# /etc/systemd/system/ecommerce-celery.service
[Unit]
Description=Ecommerce Automation Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/ecommerce-automation/backend
Environment="PATH=/var/www/ecommerce-automation/backend/venv/bin"
ExecStart=/var/www/ecommerce-automation/backend/venv/bin/celery \
  -A app.celery worker \
  --loglevel=info \
  --concurrency=4 \
  --logfile=/var/log/ecommerce/celery.log \
  --pidfile=/var/run/celery/worker.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 6. MySQL主从复制

### 6.1 主库配置

```ini
# /etc/mysql/mysql.conf.d/mysqld.cnf
[mysqld]
server-id = 1
log_bin = /var/log/mysql/mysql-bin.log
binlog_do_db = ecommerce_automation

# 性能优化
innodb_buffer_pool_size = 2G
innodb_buffer_pool_instances = 4
max_connections = 500
thread_cache_size = 100
```

```sql
-- 创建复制用户（密码应从环境变量读取）
CREATE USER 'repl'@'%' IDENTIFIED BY '${MYSQL_REPL_PASSWORD}';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;

-- 查看主库状态
SHOW MASTER STATUS;
```

### 6.2 从库配置

```ini
# /etc/mysql/mysql.conf.d/mysqld.cnf
[mysqld]
server-id = 2
relay-log = /var/log/mysql/mysql-relay-bin.log
```

```sql
-- 配置主库信息（密码应从环境变量读取）
CHANGE MASTER TO
  MASTER_HOST='${MYSQL_MASTER_HOST}',
  MASTER_USER='repl',
  MASTER_PASSWORD='${MYSQL_REPL_PASSWORD}',
  MASTER_LOG_FILE='mysql-bin.000001',
  MASTER_LOG_POS=154;

-- 启动复制
START SLAVE;

-- 查看从库状态
SHOW SLAVE STATUS\G
```

---

## 7. Redis哨兵模式

### 7.1 哨兵配置

```conf
# /etc/redis/sentinel.conf
port 26379
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel auth-pass mymaster ${REDIS_PASSWORD}
sentinel down-after-milliseconds mymaster 5000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 10000
```

```bash
# 启动哨兵
redis-sentinel /etc/redis/sentinel.conf
```

---

## 8. 监控与日志

### 8.1 Prometheus + Grafana

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['localhost:8001', 'localhost:8002', 'localhost:8003']

  - job_name: 'mysql'
    static_configs:
      - targets: ['localhost:9104']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
```

### 8.2 日志收集（ELK）

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/ecommerce/*.log

output.elasticsearch:
  hosts: ["localhost:9200"]
```

---

## 9. 备份策略

### 9.1 数据库备份

```bash
#!/bin/bash
# /usr/local/bin/backup-mysql.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/mysql"

mysqldump -u root -p ecommerce_automation \
  --single-transaction \
  --routines \
  --triggers \
  > $BACKUP_DIR/backup_$DATE.sql

# 保留最近7天的备份
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

```cron
# 每天凌晨2点执行备份
0 2 * * * /usr/local/bin/backup-mysql.sh
```

---

## 10. 安全加固

### 10.1 防火墙配置

```bash
# 允许HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 允许SSH（限制IP）
sudo ufw allow from 你的IP地址 to any port 22

# 启用防火墙
sudo ufw enable
```

### 10.2 SSL证书（Let's Encrypt）

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 11. 性能优化

### 11.1 数据库优化

```sql
-- 慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- InnoDB Buffer Pool优化（MySQL 8.0已移除查询缓存）
SET GLOBAL innodb_buffer_pool_size = 2147483648;  -- 2GB
SET GLOBAL innodb_buffer_pool_instances = 4;

-- 连接池优化
SET GLOBAL max_connections = 500;
SET GLOBAL thread_cache_size = 100;
```

### 11.2 Redis优化

```conf
# /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

---

## 12. 相关文档

- [开发环境部署](01-dev-environment.md) - 开发环境配置
- [系统架构总览](../architecture/01-system-architecture.md) - 技术架构
