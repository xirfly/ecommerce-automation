# 数据模型设计

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 目标

设计清晰、规范的数据库表结构，支持：
- 产品全生命周期管理
- 任务执行和状态追踪
- 多渠道配置管理
- 用户权限控制
- Agent记忆存储

---

## 2. ER图

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   users     │──────<│   products  │>──────│    tasks    │
│             │ 1:N   │             │ 1:N   │             │
└─────────────┘       └─────────────┘       └─────────────┘
                              │                     │
                              │ 1:N                 │ 1:N
                              ↓                     ↓
                      ┌─────────────┐       ┌─────────────┐
                      │ sales_data  │       │ task_logs   │
                      └─────────────┘       └─────────────┘

┌─────────────┐       ┌─────────────┐
│  channels   │       │agent_memory │
└─────────────┘       └─────────────┘
```

---

## 3. 表结构设计

### 3.1 users表（用户信息）

**用途：** 存储用户账号、角色、权限信息

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(100) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    email VARCHAR(255) COMMENT '邮箱',
    role ENUM('admin', 'operator', 'viewer') DEFAULT 'operator' COMMENT '角色',
    team_id BIGINT COMMENT '团队ID',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    last_login_at TIMESTAMP COMMENT '最后登录时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_team (team_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

**字段说明：**
- `role`: admin（管理员）、operator（运营人员）、viewer（查看者）
- `team_id`: 预留字段，支持多租户/多团队
- `is_active`: 软删除标记

---

### 3.2 products表（产品信息）

**用途：** 存储产品基础信息和状态

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '产品ID',
    name VARCHAR(255) NOT NULL COMMENT '产品名称',
    category VARCHAR(100) COMMENT '产品分类',
    price DECIMAL(10,2) COMMENT '价格',
    cost DECIMAL(10,2) COMMENT '成本',
    status ENUM('draft', 'analyzing', 'generating', 'reviewing', 'published', 'offline', 'failed')
        DEFAULT 'draft' COMMENT '状态',
    target_platforms JSON COMMENT '目标平台 ["淘宝", "京东"]',
    platform_product_ids JSON COMMENT '平台产品ID {"淘宝": "123", "京东": "456"}',
    detail_page_url TEXT COMMENT '详情页链接',
    images JSON COMMENT '图片URLs',
    videos JSON COMMENT '视频URLs',
    description TEXT COMMENT '产品描述',
    created_by BIGINT COMMENT '创建人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_status (status),
    INDEX idx_category (category),
    INDEX idx_created_by (created_by),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产品表';
```

**状态流转：**
```
draft → analyzing → generating → reviewing → published → offline
                                     ↓
                                  failed
```

**JSON字段示例：**
```json
{
  "target_platforms": ["淘宝", "京东"],
  "platform_product_ids": {
    "淘宝": "123456789",
    "京东": "987654321"
  },
  "images": {
    "main": "https://cdn.example.com/main.jpg",
    "detail": ["https://cdn.example.com/detail1.jpg"]
  }
}
```

---

### 3.3 tasks表（任务记录）

**用途：** 记录Agent任务的执行情况

```sql
CREATE TABLE tasks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '任务ID',
    task_uuid VARCHAR(36) UNIQUE NOT NULL COMMENT '任务UUID',
    product_id BIGINT COMMENT '关联产品ID',
    task_type ENUM('analyze', 'generate_image', 'generate_video', 'generate_text',
                   'create_page', 'publish', 'report') NOT NULL COMMENT '任务类型',
    status ENUM('pending', 'running', 'success', 'failed', 'timeout', 'cancelled')
        DEFAULT 'pending' COMMENT '状态',
    input_data JSON COMMENT '输入参数',
    output_data JSON COMMENT '输出结果',
    error_message TEXT COMMENT '错误信息',
    retry_count INT DEFAULT 0 COMMENT '重试次数',
    duration_ms INT COMMENT '执行耗时（毫秒）',
    started_at TIMESTAMP COMMENT '开始时间',
    completed_at TIMESTAMP COMMENT '完成时间',
    created_by BIGINT COMMENT '创建人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_task_uuid (task_uuid),
    INDEX idx_product_id (product_id),
    INDEX idx_status (status),
    INDEX idx_task_type (task_type),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务表';
```

**任务类型说明：**
- `analyze`: Agent 1 选品分析
- `generate_image`: Agent 2 图片生成
- `generate_video`: Agent 3 视频生成
- `generate_text`: Agent 4 文案生成
- `create_page`: Agent 5 详情页制作
- `publish`: Agent 6 上下架管理
- `report`: Agent 7 数据分析

---

### 3.4 task_logs表（任务日志）

**用途：** 记录任务执行的详细日志

```sql
CREATE TABLE task_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    task_id BIGINT NOT NULL COMMENT '任务ID',
    log_level ENUM('debug', 'info', 'warning', 'error') DEFAULT 'info' COMMENT '日志级别',
    message TEXT NOT NULL COMMENT '日志内容',
    extra_data JSON COMMENT '额外数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_task_id (task_id),
    INDEX idx_log_level (log_level),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务日志表';
```

---

### 3.5 channels表（渠道配置）

**用途：** 存储多渠道接入配置

```sql
CREATE TABLE channels (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '渠道ID',
    name VARCHAR(100) NOT NULL COMMENT '渠道名称',
    type ENUM('web', 'feishu', 'telegram', 'wechat', 'discord', 'whatsapp')
        NOT NULL COMMENT '渠道类型',
    config JSON NOT NULL COMMENT '渠道配置',
    routing_rules JSON COMMENT '路由规则',
    is_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_by BIGINT COMMENT '创建人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_type (type),
    INDEX idx_enabled (is_enabled),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='渠道配置表';
```

**config字段示例（飞书）：**
```json
{
  "bot_token": "xxx",
  "app_id": "xxx",
  "app_secret": "xxx",
  "webhook_url": "https://your-domain/webhook/feishu"
}
```

**routing_rules字段示例：**
```json
{
  "default_agent": "product-analyzer",
  "keyword_routing": {
    "分析": "product-analyzer",
    "生成": "content-generator"
  },
  "whitelist_users": ["user_id_1", "user_id_2"]
}
```

---

### 3.6 agent_memory表（Agent记忆）

**用途：** 存储Agent的长期记忆

```sql
CREATE TABLE agent_memory (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记忆ID',
    session_id VARCHAR(100) NOT NULL COMMENT '会话ID',
    agent_name VARCHAR(50) NOT NULL COMMENT 'Agent名称',
    memory_type ENUM('user_preference', 'history', 'decision', 'context')
        DEFAULT 'context' COMMENT '记忆类型',
    memory_data JSON NOT NULL COMMENT '记忆内容',
    importance INT DEFAULT 5 COMMENT '重要性（1-10）',
    expires_at TIMESTAMP COMMENT '过期时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_session (session_id),
    INDEX idx_agent (agent_name),
    INDEX idx_type (memory_type),
    INDEX idx_importance (importance),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent记忆表';
```

**memory_data字段示例：**
```json
{
  "type": "user_preference",
  "content": "用户偏好简约风格的产品图片",
  "context": "在第3次对话中提到",
  "confidence": 0.9
}
```

---

### 3.7 sales_data表（销售数据）

**用途：** 存储产品销售数据

```sql
CREATE TABLE sales_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '销售记录ID',
    product_id BIGINT NOT NULL COMMENT '产品ID',
    platform VARCHAR(50) NOT NULL COMMENT '平台名称',
    date DATE NOT NULL COMMENT '日期',
    order_count INT DEFAULT 0 COMMENT '订单数',
    sales_volume INT DEFAULT 0 COMMENT '销量',
    revenue DECIMAL(12,2) DEFAULT 0 COMMENT '收入',
    cost DECIMAL(12,2) DEFAULT 0 COMMENT '成本',
    profit DECIMAL(12,2) DEFAULT 0 COMMENT '利润',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    UNIQUE KEY uk_product_platform_date (product_id, platform, date),
    INDEX idx_product_id (product_id),
    INDEX idx_platform (platform),
    INDEX idx_date (date),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='销售数据表';
```

---

## 4. 索引设计

### 4.1 索引策略

| 表名 | 索引类型 | 索引字段 | 用途 |
|------|----------|----------|------|
| users | 唯一索引 | username | 登录查询 |
| users | 普通索引 | role | 权限过滤 |
| products | 普通索引 | status | 状态筛选 |
| products | 普通索引 | created_at | 时间排序 |
| tasks | 唯一索引 | task_uuid | UUID查询 |
| tasks | 普通索引 | product_id, status | 产品任务查询 |
| tasks | 复合索引 | task_type, status | 任务类型统计 |
| sales_data | 唯一索引 | product_id, platform, date | 防止重复 |
| sales_data | 普通索引 | date | 时间范围查询 |

### 4.2 索引优化建议

**查询优化：**
```sql
-- 好的查询（使用索引）
SELECT * FROM tasks
WHERE product_id = 123 AND status = 'running'
ORDER BY created_at DESC;

-- 不好的查询（全表扫描）
SELECT * FROM tasks
WHERE DATE(created_at) = '2026-03-16';  -- 函数导致索引失效

-- 优化后
SELECT * FROM tasks
WHERE created_at >= '2026-03-16 00:00:00'
  AND created_at < '2026-03-17 00:00:00';
```

---

## 5. 数据完整性

### 5.1 外键约束

```sql
-- products表
ALTER TABLE products
ADD CONSTRAINT fk_products_created_by
FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- tasks表
ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_product_id
FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;

ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_created_by
FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- task_logs表
ALTER TABLE task_logs
ADD CONSTRAINT fk_task_logs_task_id
FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE;

-- sales_data表
ALTER TABLE sales_data
ADD CONSTRAINT fk_sales_data_product_id
FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;
```

### 5.2 级联删除策略

| 父表 | 子表 | 策略 | 说明 |
|------|------|------|------|
| users | products | SET NULL | 用户删除后，产品保留但创建人置空 |
| users | tasks | SET NULL | 用户删除后，任务保留但创建人置空 |
| products | tasks | CASCADE | 产品删除后，相关任务全部删除 |
| products | sales_data | CASCADE | 产品删除后，销售数据全部删除 |
| tasks | task_logs | CASCADE | 任务删除后，日志全部删除 |

---

## 6. 数据迁移脚本

### 6.1 初始化脚本

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS ecommerce_automation
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;

USE ecommerce_automation;

-- 创建所有表（按依赖顺序）
SOURCE tables/01_users.sql;
SOURCE tables/02_products.sql;
SOURCE tables/03_tasks.sql;
SOURCE tables/04_task_logs.sql;
SOURCE tables/05_channels.sql;
SOURCE tables/06_agent_memory.sql;
SOURCE tables/07_sales_data.sql;

-- 创建初始管理员用户
INSERT INTO users (username, password_hash, email, role)
VALUES ('admin', '$2b$12$...', 'admin@example.com', 'admin');
```

### 6.2 测试数据

```sql
-- 插入测试用户
INSERT INTO users (username, password_hash, role) VALUES
('operator1', '$2b$12$...', 'operator'),
('viewer1', '$2b$12$...', 'viewer');

-- 插入测试产品
INSERT INTO products (name, category, price, status, created_by) VALUES
('无线蓝牙耳机', '数码', 199.00, 'draft', 1),
('智能手表', '数码', 299.00, 'analyzing', 1);

-- 插入测试渠道
INSERT INTO channels (name, type, config, is_enabled, created_by) VALUES
('Web后台', 'web', '{}', TRUE, 1),
('飞书Bot', 'feishu', '{"bot_token": "test"}', TRUE, 1);
```

---

## 7. 性能优化

### 7.1 分区策略

**sales_data表按日期分区：**
```sql
ALTER TABLE sales_data
PARTITION BY RANGE (TO_DAYS(date)) (
    PARTITION p202601 VALUES LESS THAN (TO_DAYS('2026-02-01')),
    PARTITION p202602 VALUES LESS THAN (TO_DAYS('2026-03-01')),
    PARTITION p202603 VALUES LESS THAN (TO_DAYS('2026-04-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### 7.2 查询优化

**慢查询优化：**
```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- 1秒以上的查询

-- 分析慢查询
EXPLAIN SELECT * FROM tasks
WHERE product_id = 123 AND status = 'running';
```

---

## 8. 备份策略

### 8.1 备份方案

**每日全量备份：**
```bash
#!/bin/bash
mysqldump -u root -p ecommerce_automation \
  --single-transaction \
  --routines \
  --triggers \
  > backup_$(date +%Y%m%d).sql
```

**增量备份（binlog）：**
```sql
-- 开启binlog
SET GLOBAL binlog_format = 'ROW';
SET GLOBAL expire_logs_days = 7;
```

### 8.2 恢复方案

```bash
# 恢复全量备份
mysql -u root -p ecommerce_automation < backup_20260316.sql

# 恢复增量备份
mysqlbinlog binlog.000001 | mysql -u root -p ecommerce_automation
```

---

## 9. 相关文档

- [Redis数据结构](02-redis-structure.md) - 缓存和队列设计
- [系统架构总览](../architecture/01-system-architecture.md) - 整体架构
- [任务拆分与优先级](../implementation/01-task-breakdown.md) - 开发任务
