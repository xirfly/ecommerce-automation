# Agent 编排系统说明

## 概述

Agent 编排系统是电商自动化管理系统的核心，实现了 7 个专业 Agent 的协同工作，完成从选品到上架的全流程自动化。

## 7 个专业 Agent

### 1. ProductAnalysisAgent - 选品分析
- 分析产品市场潜力、竞争情况、利润率
- 依赖：无

### 2. PriceOptimizationAgent - 价格优化
- 根据市场情况优化产品定价
- 依赖：product_analysis

### 3. ContentGenerationAgent - 内容生成
- 生成产品标题、描述、关键词等营销内容
- 依赖：product_analysis

### 4. ImageGenerationAgent - 图片生成
- 生成产品主图、详情图
- 依赖：content_generation

### 5. VideoGenerationAgent - 视频生成
- 生成产品宣传视频（可选）
- 依赖：image_generation

### 6. ContentReviewAgent - 内容审核
- 审核生成的内容是否符合平台规范
- 依赖：content_generation

### 7. PublishAgent - 发布上架
- 将产品发布到电商平台
- 依赖：content_review, image_generation

## 任务类型与执行流程

1. **product_analysis**: 只执行选品分析
2. **content_generation**: 选品分析 → 内容生成
3. **image_generation**: 选品分析 → 内容生成 → 图片生成
4. **video_generation**: 选品分析 → 内容生成 → 图片生成 → 视频生成
5. **review**: 选品分析 → 内容生成 → 内容审核
6. **publish**: 完整流程（选品分析 → 价格优化 → 内容生成 → 图片生成 → 内容审核 → 发布上架）

## 核心特性

- **依赖管理**: 自动处理 Agent 之间的依赖关系
- **拓扑排序**: 自动计算最优执行顺序
- **数据共享**: Agent 之间通过 shared_data 传递数据
- **错误处理**: 支持遇到错误停止或继续执行
- **执行历史**: 记录所有 Agent 的执行结果
- **验证机制**: 执行前验证是否满足条件

## 代码位置

- `app/agents/base.py` - Agent 基类和数据结构
- `app/agents/orchestrator.py` - Agent 编排器
- `app/agents/registry.py` - Agent 注册中心
- `app/agents/*.py` - 7 个专业 Agent 实现
- `app/workers/tasks.py` - Celery 任务集成

## 使用方式

系统已自动集成到 Celery 任务中，创建任务时会自动调用相应的 Agent 编排流程。

