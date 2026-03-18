import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Table, Spin } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { analyticsApi, AnalyticsOverview } from '@/api/analytics'
import { taskApi, Task } from '@/api/task'
import { useNavigate } from 'react-router-dom'

const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<AnalyticsOverview | null>(null)
  const [recentTasks, setRecentTasks] = useState<Task[]>([])

  useEffect(() => {
    loadData()
    loadRecentTasks()
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

  const loadRecentTasks = async () => {
    try {
      const response = await taskApi.getList({ page: 1, page_size: 5 })
      setRecentTasks(response.data.items)
    } catch (error) {
      // 错误已在拦截器中处理
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
  const trendOption = {
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: data.tasks.trend.map((item) => {
        const date = new Date(item.date)
        return `${date.getMonth() + 1}/${date.getDate()}`
      }),
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
      },
    ],
  }

  // 任务状态饼图
  const taskStatusOption = {
    tooltip: {
      trigger: 'item',
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: Object.entries(data.tasks.by_status).map(([key, value]) => {
          const statusMap: Record<string, { name: string; color: string }> = {
            pending: { name: '待执行', color: '#d9d9d9' },
            running: { name: '执行中', color: '#1890ff' },
            success: { name: '成功', color: '#22C55E' },
            failed: { name: '失败', color: '#ff4d4f' },
            timeout: { name: '超时', color: '#F59E0B' },
          }
          return {
            name: statusMap[key]?.name || key,
            value: value,
            itemStyle: { color: statusMap[key]?.color },
          }
        }),
      },
    ],
  }

  // 最近任务表格
  const columns = [
    {
      title: '任务ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '任务类型',
      dataIndex: 'task_type',
      key: 'task_type',
      render: (type: string) => {
        const typeMap: Record<string, string> = {
          product_analysis: '选品分析',
          content_generation: '内容生成',
          image_generation: '图片生成',
          video_generation: '视频生成',
          review: '内容审核',
          publish: '发布上架',
        }
        return typeMap[type] || type
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, string> = {
          pending: '待执行',
          running: '执行中',
          success: '成功',
          failed: '失败',
          timeout: '超时',
        }
        return statusMap[status] || status
      },
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number) => `${progress}%`,
    },
  ]

  // 计算新增产品数（草稿状态）
  const newProducts = data.products.by_status.draft || 0

  // 计算执行中的任务数
  const runningTasks = data.tasks.by_status.running || 0

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>仪表盘</h2>

      {/* KPI卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总产品数"
              value={data.products.total}
              suffix={
                newProducts > 0 ? (
                  <span style={{ fontSize: 14, color: '#22C55E' }}>
                    <ArrowUpOutlined /> +{newProducts}
                  </span>
                ) : null
              }
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总任务数"
              value={data.tasks.total}
              suffix={
                runningTasks > 0 ? (
                  <span style={{ fontSize: 14, color: '#22C55E' }}>
                    <ArrowUpOutlined /> +{runningTasks}
                  </span>
                ) : null
              }
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="成功率"
              value={data.tasks.success_rate}
              suffix="%"
              precision={1}
              valueStyle={{
                color: data.tasks.success_rate >= 80 ? '#22C55E' : '#ff4d4f',
              }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待执行任务"
              value={data.tasks.by_status.pending || 0}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={16}>
          <Card title="任务执行趋势（最近7天）">
            <ReactECharts option={trendOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="任务状态分布">
            <ReactECharts option={taskStatusOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      {/* 最近任务 */}
      <Card
        title="最近任务"
        extra={
          <a onClick={() => navigate('/tasks')} style={{ cursor: 'pointer' }}>
            查看全部
          </a>
        }
      >
        <Table
          columns={columns}
          dataSource={recentTasks}
          rowKey="id"
          pagination={false}
          onRow={(record) => ({
            onClick: () => navigate(`/tasks/${record.id}`),
            style: { cursor: 'pointer' },
          })}
        />
      </Card>
    </div>
  )
}

export default Dashboard
