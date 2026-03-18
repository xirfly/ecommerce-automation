# 监控告警系统部署指南

## 系统架构

监控告警系统由以下组件组成：

```
┌─────────────────────────────────────────────────────────────┐
│                     监控告警系统架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   应用服务    │───▶│  Prometheus  │───▶│   Grafana    │  │
│  │  /metrics    │    │   (指标采集)  │    │  (可视化)    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                               │
│         │                    ▼                               │
│         │            ┌──────────────┐                        │
│         │            │ AlertManager │                        │
│         │            │  (告警管理)   │                        │
│         │            └──────────────┘                        │
│         │                    │                               │
│         │                    ▼                               │
│         │            ┌──────────────┐                        │
│         └───────────▶│  Webhook API │                        │
│                      │  (告警接收)   │                        │
│                      └──────────────┘                        │
│                             │                                │
│                             ▼                                │
│                      ┌──────────────┐                        │
│                      │ 通知渠道      │                        │
│                      │ 飞书/Telegram │                        │
│                      └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 1. 启动监控服务

使用 Docker Compose 一键启动所有监控组件：

```bash
cd monitoring
docker-compose up -d
```

这将启动以下服务：
- **Prometheus** (端口 9090) - 指标采集和存储
- **Grafana** (端口 3001) - 数据可视化
- **AlertManager** (端口 9093) - 告警管理
- **Node Exporter** (端口 9100) - 系统资源监控
- **Redis Exporter** (端口 9121) - Redis 监控
- **MySQL Exporter** (端口 9104) - MySQL 监控

### 2. 访问监控界面

#### Prometheus
- URL: http://localhost:9090
- 功能: 查询指标、查看告警规则、查看目标状态

#### Grafana
- URL: http://localhost:3001
- 默认账号: admin / admin123
- 功能: 查看仪表盘、创建图表、配置告警

#### AlertManager
- URL: http://localhost:9093
- 功能: 查看活跃告警、管理静默规则

### 3. 配置 Grafana 数据源

首次登录 Grafana 后，需要配置 Prometheus 数据源：

1. 登录 Grafana (admin/admin123)
2. 进入 Configuration → Data Sources
3. 点击 "Add data source"
4. 选择 "Prometheus"
5. 配置 URL: `http://prometheus:9090`
6. 点击 "Save & Test"

### 4. 导入仪表盘

系统提供了预配置的仪表盘：

1. 进入 Dashboards → Import
2. 上传 `monitoring/grafana/dashboards/system_overview.json`
3. 选择 Prometheus 数据源
4. 点击 "Import"

## 监控指标说明

### 任务指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `task_total` | Counter | 任务总数（按类型和状态） |
| `task_duration_seconds` | Histogram | 任务执行时长 |
| `task_running` | Gauge | 当前运行中的任务数 |
| `task_retries_total` | Counter | 任务重试次数 |
| `task_queue_length` | Gauge | 任务队列长度 |

### Agent 指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `agent_executions_total` | Counter | Agent 执行总数 |
| `agent_duration_seconds` | Histogram | Agent 执行时长 |
| `agent_errors_total` | Counter | Agent 错误次数 |

### API 指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `http_requests_total` | Counter | HTTP 请求总数 |
| `http_request_duration_seconds` | Histogram | HTTP 请求时长 |
| `http_active_connections` | Gauge | 活跃连接数 |

### 数据库指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `db_queries_total` | Counter | 数据库查询总数 |
| `db_query_duration_seconds` | Histogram | 数据库查询时长 |
| `db_pool_size` | Gauge | 连接池大小 |
| `db_pool_available` | Gauge | 可用连接数 |

### Redis 指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `redis_operations_total` | Counter | Redis 操作总数 |
| `redis_operation_duration_seconds` | Histogram | Redis 操作时长 |
| `redis_connected` | Gauge | Redis 连接状态 |

## 告警规则

系统预配置了以下告警规则：

### 关键告警 (Critical)

- **HighAPIErrorRate**: API 5xx 错误率 > 5%
- **HighAgentErrorRate**: Agent 错误率 > 30%
- **DatabasePoolExhausted**: 数据库连接池即将耗尽
- **RedisDisconnected**: Redis 连接断开
- **CeleryWorkerOffline**: Celery Worker 离线

### 警告告警 (Warning)

- **HighTaskFailureRate**: 任务失败率 > 20%
- **TaskExecutionTooSlow**: 任务执行时间 > 10 分钟
- **SlowAPIResponse**: API P95 响应时间 > 2 秒
- **SlowDatabaseQuery**: 数据库查询 P95 时间 > 1 秒

### 信息告警 (Info)

- **TooManyPendingFeedback**: 待处理反馈 > 50 个
- **HighPriorityFeedbackPending**: 高优先级反馈 > 5 个

## 告警通知配置

告警通过以下流程发送：

1. **Prometheus** 检测到告警条件触发
2. **AlertManager** 接收告警并根据路由规则分组
3. **Webhook** 发送到应用后端 `/api/webhooks/alertmanager`
4. **通知服务** 通过配置的渠道发送（飞书/Telegram/企业微信）

### 配置通知渠道

1. 登录系统管理后台
2. 进入 "渠道配置" 页面
3. 添加通知渠道（飞书/Telegram/企业微信）
4. 设置为默认渠道
5. 进入 "系统设置" → "通知配置"
6. 启用通知功能

## 常用查询示例

### Prometheus 查询

```promql
# 任务成功率
sum(rate(task_total{status="success"}[5m])) / sum(rate(task_total[5m])) * 100

# API P95 响应时间
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (endpoint, le))

# Agent 错误率
sum(rate(agent_executions_total{status="failed"}[5m])) by (agent_name) / sum(rate(agent_executions_total[5m])) by (agent_name)

# 数据库连接池使用率
(db_pool_size - db_pool_available) / db_pool_size * 100
```

## 故障排查

### Prometheus 无法抓取指标

1. 检查应用是否正常运行：`curl http://localhost:8000/health`
2. 检查 metrics 端点：`curl http://localhost:8000/metrics`
3. 查看 Prometheus 目标状态：http://localhost:9090/targets

### Grafana 无数据

1. 检查 Prometheus 数据源配置
2. 确认 Prometheus 正在抓取数据
3. 检查时间范围设置

### 告警未发送

1. 检查 AlertManager 状态：http://localhost:9093
2. 查看应用日志：`tail -f backend/backend.log`
3. 确认通知渠道已配置并启用

## 性能优化建议

1. **指标保留时间**: 默认 15 天，可根据需求调整
2. **抓取间隔**: 默认 15 秒，高负载时可增加到 30 秒
3. **告警评估间隔**: 默认 15 秒，可根据需求调整
4. **数据压缩**: Prometheus 自动压缩历史数据

## 维护操作

### 备份监控数据

```bash
# 备份 Prometheus 数据
docker exec ecommerce-prometheus tar czf /tmp/prometheus-backup.tar.gz /prometheus
docker cp ecommerce-prometheus:/tmp/prometheus-backup.tar.gz ./backups/

# 备份 Grafana 数据
docker exec ecommerce-grafana tar czf /tmp/grafana-backup.tar.gz /var/lib/grafana
docker cp ecommerce-grafana:/tmp/grafana-backup.tar.gz ./backups/
```

### 清理旧数据

```bash
# 清理 Prometheus 数据（保留最近 7 天）
docker exec ecommerce-prometheus promtool tsdb delete --retention.time=7d /prometheus
```

### 重启监控服务

```bash
cd monitoring
docker-compose restart
```

## 扩展功能

### 添加自定义告警规则

1. 编辑 `monitoring/prometheus/alert_rules.yml`
2. 添加新的告警规则
3. 重新加载配置：`docker-compose restart prometheus`

### 创建自定义仪表盘

1. 登录 Grafana
2. 创建新仪表盘
3. 添加面板和查询
4. 导出 JSON 配置保存到 `monitoring/grafana/dashboards/`

## 相关文档

- [Prometheus 官方文档](https://prometheus.io/docs/)
- [Grafana 官方文档](https://grafana.com/docs/)
- [AlertManager 官方文档](https://prometheus.io/docs/alerting/latest/alertmanager/)
