import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Spin } from 'antd'
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { analyticsApi, AnalyticsOverview } from '@/api/analytics'

const DataAnalytics: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<AnalyticsOverview | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await analyticsApi.getOverview()
      setData(response.data)
    } catch (error) {
      // 错误已在拦截器中处理
    } finally {
      setLoading(false)
    }
  }

  if (loading || !data) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    )
  }

  // 任务趋势图配置
  const taskTrendOption = {
    title: {
      text: '任务执行趋势（最近7天）',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: data.tasks.trend.map((item) => item.date),
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '任务数',
        type: 'line',
        data: data.tasks.trend.map((item) => item.count),
        smooth: true,
        itemStyle: { color: '#1890ff' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
              { offset: 1, color: 'rgba(24, 144, 255, 0.05)' },
            ],
          },
        },
      },
    ],
  }

  // 任务状态饼图配置
  const taskStatusOption = {
    title: {
      text: '任务状态分布',
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        center: ['60%', '50%'],
        data: Object.entries(data.tasks.by_status).map(([key, value]) => {
          const statusMap: Record<string, { name: string; color: string }> = {
            pending: { name: '待执行', color: '#d9d9d9' },
            running: { name: '执行中', color: '#1890ff' },
            success: { name: '成功', color: '#52c41a' },
            failed: { name: '失败', color: '#ff4d4f' },
            timeout: { name: '超时', color: '#faad14' },
          }
          return {
            name: statusMap[key]?.name || key,
            value: value,
            itemStyle: { color: statusMap[key]?.color },
          }
        }),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  }

  // 任务类型柱状图配置
  const taskTypeOption = {
    title: {
      text: '任务类型分布',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    xAxis: {
      type: 'category',
      data: Object.keys(data.tasks.by_type).map((key) => {
        const typeMap: Record<string, string> = {
          product_analysis: '选品分析',
          content_generation: '内容生成',
          image_generation: '图片生成',
          video_generation: '视频生成',
          review: '内容审核',
          publish: '发布上架',
        }
        return typeMap[key] || key
      }),
      axisLabel: {
        rotate: 30,
      },
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '任务数',
        type: 'bar',
        data: Object.values(data.tasks.by_type),
        itemStyle: {
          color: '#1890ff',
        },
      },
    ],
  }

  // 产品分类饼图配置
  const productCategoryOption = {
    title: {
      text: '产品分类分布',
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        center: ['60%', '50%'],
        data: Object.entries(data.products.by_category).map(([key, value]) => ({
          name: key,
          value: value,
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  }

  // 产品状态柱状图配置
  const productStatusOption = {
    title: {
      text: '产品状态分布',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    xAxis: {
      type: 'category',
      data: Object.keys(data.products.by_status).map((key) => {
        const statusMap: Record<string, string> = {
          draft: '草稿',
          analyzing: '分析中',
          generating: '生成中',
          reviewing: '审核中',
          published: '已发布',
          offline: '已下架',
        }
        return statusMap[key] || key
      }),
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '产品数',
        type: 'bar',
        data: Object.values(data.products.by_status),
        itemStyle: {
          color: '#52c41a',
        },
      },
    ],
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>数据分析</h2>

      {/* KPI 卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总产品数"
              value={data.products.total}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总任务数"
              value={data.tasks.total}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="任务成功率"
              value={data.tasks.success_rate}
              suffix="%"
              precision={2}
              valueStyle={{
                color: data.tasks.success_rate >= 80 ? '#3f8600' : '#cf1322',
              }}
              prefix={
                data.tasks.success_rate >= 80 ? (
                  <ArrowUpOutlined />
                ) : (
                  <ArrowDownOutlined />
                )
              }
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待执行任务"
              value={data.tasks.by_status.pending || 0}
              valueStyle={{ color: '#8c8c8c' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 任务趋势图 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card>
            <ReactECharts option={taskTrendOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      {/* 任务统计图表 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card>
            <ReactECharts option={taskStatusOption} style={{ height: 350 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card>
            <ReactECharts option={taskTypeOption} style={{ height: 350 }} />
          </Card>
        </Col>
      </Row>

      {/* 产品统计图表 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card>
            <ReactECharts option={productCategoryOption} style={{ height: 350 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card>
            <ReactECharts option={productStatusOption} style={{ height: 350 }} />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default DataAnalytics
