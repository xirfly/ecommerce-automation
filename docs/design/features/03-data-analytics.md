# 数据分析模块

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 目标

提供数据分析和可视化功能，支持：
- 销售数据统计
- Agent性能分析
- 趋势预测
- AI生成分析报告

---

## 2. 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 仪表盘概览 | 核心KPI展示 | P0 |
| 销售报表 | 销售数据统计 | P0 |
| Agent性能 | Agent执行统计 | P1 |
| 趋势分析 | 数据趋势图表 | P1 |
| AI分析报告 | Agent 7生成报告 | P2 |
| 数据导出 | 导出Excel/PDF | P2 |

---

## 3. API设计

### 3.1 仪表盘数据

```http
GET /api/v1/analytics/dashboard?date_range=7d
Authorization: Bearer {token}

Response (200 OK):
{
  "code": 0,
  "data": {
    "kpi": {
      "total_products": 245,
      "total_tasks": 1234,
      "success_rate": 96.5,
      "avg_duration_min": 8.5
    },
    "task_trend": [
      {"date": "2026-03-10", "count": 120},
      {"date": "2026-03-11", "count": 135}
    ],
    "agent_status": {
      "product-analyzer": {"status": "normal", "success_rate": 95.2},
      "image-generator": {"status": "normal", "success_rate": 92.8}
    }
  }
}
```

### 3.2 销售报表

```http
GET /api/v1/analytics/sales?start_date=2026-03-01&end_date=2026-03-16
Authorization: Bearer {token}

Response (200 OK):
{
  "code": 0,
  "data": {
    "summary": {
      "total_revenue": 245600,
      "total_orders": 1234,
      "avg_order_value": 199
    },
    "by_platform": [
      {"platform": "淘宝", "revenue": 150000, "orders": 750},
      {"platform": "京东", "revenue": 95600, "orders": 484}
    ],
    "daily_trend": [
      {"date": "2026-03-01", "revenue": 15000, "orders": 75}
    ]
  }
}
```

---

## 4. 图表配置

### 4.1 ECharts配置

```typescript
// 任务执行趋势图
const taskTrendOption = {
  title: { text: '任务执行趋势' },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: dates },
  yAxis: { type: 'value' },
  series: [{
    name: '任务数',
    type: 'line',
    data: counts,
    smooth: true
  }]
};

// Agent性能柱状图
const agentPerformanceOption = {
  title: { text: 'Agent性能分析' },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: agentNames },
  yAxis: { type: 'value', max: 100 },
  series: [{
    name: '成功率',
    type: 'bar',
    data: successRates
  }]
};
```

---

## 5. Agent 7实现

### 5.1 AI分析报告生成

```python
async def generate_ai_report(date_range: str) -> dict:
    """生成AI分析报告"""

    # 1. 查询数据
    stats = await get_statistics(date_range)

    # 2. 构建提示词
    prompt = f"""
    基于以下数据生成分析报告：

    - 任务总数：{stats['total_tasks']}
    - 成功率：{stats['success_rate']}%
    - 平均耗时：{stats['avg_duration']}分钟

    请分析：
    1. 核心发现
    2. 优化建议
    3. 趋势预测
    """

    # 3. 调用LLM生成报告
    report = await call_llm(prompt)

    return {
        "summary": report,
        "generated_at": datetime.now().isoformat()
    }
```

---

## 6. 相关文档

- [Agent编排设计](../architecture/02-agent-orchestration.md) - Agent 7实现
- [数据模型设计](../database/01-data-model.md) - sales_data表
