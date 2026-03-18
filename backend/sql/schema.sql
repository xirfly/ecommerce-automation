-- 电商自动化系统数据库表结构
-- 版本: v1.0
-- 创建日期: 2026-03-16

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 1. 用户表
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
  `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
  `role` ENUM('admin', 'operator', 'viewer') NOT NULL DEFAULT 'viewer' COMMENT '角色',
  `team_id` INT UNSIGNED DEFAULT NULL COMMENT '团队ID',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`),
  KEY `idx_team_id` (`team_id`),
  KEY `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ----------------------------
-- 2. 产品表
-- ----------------------------
DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '产品ID',
  `name` VARCHAR(200) NOT NULL COMMENT '产品名称',
  `category` VARCHAR(50) NOT NULL COMMENT '产品分类',
  `price` DECIMAL(10,2) NOT NULL COMMENT '价格',
  `cost` DECIMAL(10,2) DEFAULT NULL COMMENT '成本',
  `status` ENUM('draft', 'analyzing', 'generating', 'reviewing', 'published', 'offline') NOT NULL DEFAULT 'draft' COMMENT '状态',
  `platform` VARCHAR(50) DEFAULT NULL COMMENT '目标平台',
  `analysis_result` JSON DEFAULT NULL COMMENT '选品分析结果',
  `images` JSON DEFAULT NULL COMMENT '图片URL列表',
  `videos` JSON DEFAULT NULL COMMENT '视频URL列表',
  `description` TEXT DEFAULT NULL COMMENT '产品描述',
  `detail_page_url` VARCHAR(500) DEFAULT NULL COMMENT '详情页URL',
  `created_by` INT UNSIGNED NOT NULL COMMENT '创建人',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_status` (`status`),
  KEY `idx_category` (`category`),
  KEY `idx_created_by` (`created_by`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_products_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品表';

-- ----------------------------
-- 3. 任务表
-- ----------------------------
DROP TABLE IF EXISTS `tasks`;
CREATE TABLE `tasks` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  `task_id` VARCHAR(100) NOT NULL COMMENT 'Celery任务ID',
  `product_id` INT UNSIGNED NOT NULL COMMENT '产品ID',
  `task_type` VARCHAR(50) NOT NULL COMMENT '任务类型',
  `status` ENUM('pending', 'running', 'success', 'failed', 'timeout') NOT NULL DEFAULT 'pending' COMMENT '状态',
  `progress` INT NOT NULL DEFAULT 0 COMMENT '进度(0-100)',
  `result` JSON DEFAULT NULL COMMENT '任务结果',
  `error_message` TEXT DEFAULT NULL COMMENT '错误信息',
  `retry_count` INT NOT NULL DEFAULT 0 COMMENT '重试次数',
  `started_at` TIMESTAMP NULL DEFAULT NULL COMMENT '开始时间',
  `completed_at` TIMESTAMP NULL DEFAULT NULL COMMENT '完成时间',
  `created_by` INT UNSIGNED NOT NULL COMMENT '创建人',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_task_id` (`task_id`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_tasks_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tasks_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务表';

-- ----------------------------
-- 4. 任务日志表
-- ----------------------------
DROP TABLE IF EXISTS `task_logs`;
CREATE TABLE `task_logs` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `task_id` INT UNSIGNED NOT NULL COMMENT '任务ID',
  `agent_name` VARCHAR(50) NOT NULL COMMENT 'Agent名称',
  `log_level` ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR') NOT NULL DEFAULT 'INFO' COMMENT '日志级别',
  `message` TEXT NOT NULL COMMENT '日志内容',
  `extra_data` JSON DEFAULT NULL COMMENT '额外数据',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_task_id` (`task_id`),
  KEY `idx_agent_name` (`agent_name`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_task_logs_task_id` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务日志表';

-- ----------------------------
-- 5. 渠道配置表
-- ----------------------------
DROP TABLE IF EXISTS `channels`;
CREATE TABLE `channels` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '渠道ID',
  `name` VARCHAR(100) NOT NULL COMMENT '渠道名称',
  `channel_type` ENUM('ecommerce', 'notification') NOT NULL COMMENT '渠道类型（电商平台/通知渠道）',
  `platform` VARCHAR(50) NOT NULL COMMENT '平台标识（taobao/jd/lark/telegram等）',
  `description` TEXT DEFAULT NULL COMMENT '渠道描述',
  `config` JSON NOT NULL COMMENT '渠道配置（API密钥、Webhook等）',
  `status` ENUM('active', 'inactive', 'error') NOT NULL DEFAULT 'active' COMMENT '渠道状态',
  `is_default` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否为默认渠道',
  `usage_count` INT NOT NULL DEFAULT 0 COMMENT '使用次数',
  `last_used_at` VARCHAR(50) DEFAULT NULL COMMENT '最后使用时间',
  `last_error` TEXT DEFAULT NULL COMMENT '最后错误信息',
  `created_by` INT UNSIGNED NOT NULL COMMENT '创建人',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`name`),
  KEY `idx_channel_type` (`channel_type`),
  KEY `idx_platform` (`platform`),
  KEY `idx_status` (`status`),
  KEY `idx_created_by` (`created_by`),
  CONSTRAINT `fk_channels_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='渠道配置表';

-- ----------------------------
-- 6. Agent记忆表
-- ----------------------------
DROP TABLE IF EXISTS `agent_memory`;
CREATE TABLE `agent_memory` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记忆ID',
  `session_id` VARCHAR(100) NOT NULL COMMENT '会话ID',
  `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
  `agent_name` VARCHAR(50) NOT NULL COMMENT 'Agent名称',
  `memory_type` ENUM('short_term', 'long_term') NOT NULL DEFAULT 'short_term' COMMENT '记忆类型',
  `content` JSON NOT NULL COMMENT '记忆内容',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `expires_at` TIMESTAMP NULL DEFAULT NULL COMMENT '过期时间',
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_agent_name` (`agent_name`),
  KEY `idx_expires_at` (`expires_at`),
  CONSTRAINT `fk_agent_memory_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Agent记忆表';

-- ----------------------------
-- 7. 销售数据表
-- ----------------------------
DROP TABLE IF EXISTS `sales_data`;
CREATE TABLE `sales_data` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '数据ID',
  `product_id` INT UNSIGNED NOT NULL COMMENT '产品ID',
  `date` DATE NOT NULL COMMENT '日期',
  `views` INT NOT NULL DEFAULT 0 COMMENT '浏览量',
  `clicks` INT NOT NULL DEFAULT 0 COMMENT '点击量',
  `orders` INT NOT NULL DEFAULT 0 COMMENT '订单量',
  `sales_amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '销售额',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_product_date` (`product_id`, `date`),
  KEY `idx_date` (`date`),
  CONSTRAINT `fk_sales_data_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='销售数据表';

-- ----------------------------
-- 8. 系统配置表
-- ----------------------------
DROP TABLE IF EXISTS `system_configs`;
CREATE TABLE `system_configs` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `config_key` VARCHAR(100) NOT NULL COMMENT '配置键',
  `config_value` TEXT DEFAULT NULL COMMENT '配置值',
  `config_type` VARCHAR(20) NOT NULL DEFAULT 'string' COMMENT '配置类型（string/int/bool/json）',
  `category` VARCHAR(50) NOT NULL COMMENT '配置分类（basic/ai/task/notification/security）',
  `description` TEXT DEFAULT NULL COMMENT '配置描述',
  `is_public` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否公开（前端可见）',
  `is_encrypted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否加密存储',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`),
  KEY `idx_category` (`category`),
  KEY `idx_is_public` (`is_public`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- ----------------------------
-- 初始化数据
-- ----------------------------

-- 插入默认管理员用户（密码: admin123，需要使用bcrypt加密）
INSERT INTO `users` (`username`, `password_hash`, `email`, `role`) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfLKZZRi', 'admin@example.com', 'admin');

-- 插入默认渠道配置
INSERT INTO `channels` (`name`, `channel_type`, `platform`, `description`, `config`, `status`, `created_by`) VALUES
('飞书通知', 'notification', 'lark', '默认飞书通知渠道', '{"webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"}', 'active', 1);

-- 插入默认系统配置
INSERT INTO `system_configs` (`config_key`, `config_value`, `config_type`, `category`, `description`, `is_public`) VALUES
-- 基本设置
('system_name', '电商自动化管理系统', 'string', 'basic', '系统名称', 1),
('system_description', '基于 OpenClaw 框架的智能电商自动化系统', 'string', 'basic', '系统描述', 1),
('timezone', 'Asia/Shanghai', 'string', 'basic', '时区设置', 1),

-- AI 服务配置
('openai_api_key', '', 'string', 'ai', 'OpenAI API Key', 0),
('openai_model', 'gpt-4', 'string', 'ai', 'OpenAI 模型', 1),
('midjourney_api_key', '', 'string', 'ai', 'Midjourney API Key', 0),
('runway_api_key', '', 'string', 'ai', 'Runway API Key', 0),

-- 任务配置
('task_timeout', '3600', 'int', 'task', '任务超时时间（秒）', 1),
('task_max_retries', '3', 'int', 'task', '最大重试次数', 1),
('task_concurrent_limit', '5', 'int', 'task', '并发任务数限制', 1),

-- 通知配置
('notification_enabled', 'true', 'bool', 'notification', '启用通知', 1),
('notification_on_success', 'true', 'bool', 'notification', '任务成功时通知', 1),
('notification_on_error', 'true', 'bool', 'notification', '任务失败时通知', 1),

-- 安全设置
('session_timeout', '86400', 'int', 'security', '会话超时时间（秒）', 0),
('password_min_length', '8', 'int', 'security', '密码最小长度', 1),
('api_rate_limit', '60', 'int', 'security', 'API 速率限制（次/分钟）', 0);

SET FOREIGN_KEY_CHECKS = 1;
