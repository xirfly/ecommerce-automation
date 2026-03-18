import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Descriptions,
  Button,
  Space,
  Tag,
  Timeline,
  Progress,
  Modal,
  message,
  Spin,
  Empty,
  Alert,
} from 'antd'
import {
  ArrowLeftOutlined,
  ReloadOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons'
import { taskApi, Task, TaskLog } from '@/api/task'
import { productApi, Product } from '@/api/product'

const TaskDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [task, setTask] = useState<Task | null>(null)
  const [product, setProduct] = useState<Product | null>(null)
  const [logs, setLogs] = useState<TaskLog[]>([])
  const [loading, setLoading] = useState(false)
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (id) {
      loadTask()
      loadLogs()
    }
  }, [id])

  // 自动滚动到日志底部
  useEffect(() => {
    if (logs.length > 0 && task?.status === 'running') {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, task?.status])

  const loadTask = async () => {
    setLoading(true)
    try {
      const response = await taskApi.getDetail(Number(id))
      setTask(response.data)

      // 加载关联的产品信息
      if (response.data.product_id) {
        const productResponse = await productApi.getDetail(response.data.product_id)
        setProduct(productResponse.data)
      }
    } catch (error) {
      // 错误已在拦截器中处理
    } finally {
      setLoading(false)
    }
  }

  const loadLogs = async () => {
    try {
      const response = await taskApi.getLogs(Number(id))
      setLogs(response.data)
    } catch (error) {
      // 错误已在拦截器中处理
    }
  }

  const handleRetry = async () => {
    try {
      await taskApi.retry(Number(id))
      message.success('任务已重新提交')
      loadTask()
      loadLogs()
    } catch (error) {
      // 错误已在拦截器中处理
    }
  }

  const handleDelete = () => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个任务吗？',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        await taskApi.delete(Number(id))
        message.success('删除成功')
        navigate('/tasks')
      },
    })
  }

  const getStatusTag = (status: Task['status']) => {
    const statusMap = {
      pending: { color: 'default', text: '待执行', icon: <ClockCircleOutlined /> },
      running: { color: 'blue', text: '执行中', icon: <SyncOutlined spin /> },
      success: { color: 'green', text: '成功', icon: <CheckCircleOutlined /> },
      failed: { color: 'red', text: '失败', icon: <CloseCircleOutlined /> },
      timeout: { color: 'orange', text: '超时', icon: <ClockCircleOutlined /> },
    }
    const config = statusMap[status]
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    )
  }

  const getTaskTypeName = (type: string) => {
    const typeMap: Record<string, string> = {
      product_analysis: '选品分析',
      content_generation: '内容生成',
      image_generation: '图片生成',
      video_generation: '视频生成',
      review: '内容审核',
      publish: '发布上架',
    }
    return typeMap[type] || type
  }

  const getLogLevelColor = (level: string) => {
    const colorMap: Record<string, string> = {
      DEBUG: 'default',
      INFO: 'blue',
      WARNING: 'orange',
      ERROR: 'red',
    }
    return colorMap[level] || 'default'
  }

  if (loading || !task) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/tasks')}>
          返回
        </Button>
        {(task.status === 'failed' || task.status === 'timeout') && (
          <Button icon={<ReloadOutlined />} onClick={handleRetry}>
            重试
          </Button>
        )}
        {task.status !== 'running' && (
          <Button icon={<DeleteOutlined />} danger onClick={handleDelete}>
            删除
          </Button>
        )}
      </Space>

      {/* 任务基本信息 */}
      <Card title="任务信息" style={{ marginBottom: 16 }}>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="任务 ID">{task.id}</Descriptions.Item>
          <Descriptions.Item label="任务类型">
            {getTaskTypeName(task.task_type)}
          </Descriptions.Item>
          <Descriptions.Item label="状态">{getStatusTag(task.status)}</Descriptions.Item>
          <Descriptions.Item label="进度">
            <Progress percent={task.progress} status={task.status === 'failed' ? 'exception' : undefined} />
          </Descriptions.Item>
          <Descriptions.Item label="重试次数">{task.retry_count}</Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {new Date(task.created_at).toLocaleString('zh-CN')}
          </Descriptions.Item>
          {task.started_at && (
            <Descriptions.Item label="开始时间">
              {new Date(task.started_at).toLocaleString('zh-CN')}
            </Descriptions.Item>
          )}
          {task.completed_at && (
            <Descriptions.Item label="完成时间">
              {new Date(task.completed_at).toLocaleString('zh-CN')}
            </Descriptions.Item>
          )}
          {task.started_at && task.completed_at && (
            <Descriptions.Item label="执行时长" span={2}>
              {Math.round(
                (new Date(task.completed_at).getTime() - new Date(task.started_at).getTime()) / 1000
              )}{' '}
              秒
            </Descriptions.Item>
          )}
        </Descriptions>

        {task.error_message && (
          <Alert
            message="错误信息"
            description={task.error_message}
            type="error"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </Card>

      {/* 关联产品信息 */}
      {product && (
        <Card
          title="关联产品"
          extra={
            <Button type="link" onClick={() => navigate(`/products/${product.id}`)}>
              查看详情
            </Button>
          }
          style={{ marginBottom: 16 }}
        >
          <Descriptions column={2}>
            <Descriptions.Item label="产品名称">{product.name}</Descriptions.Item>
            <Descriptions.Item label="分类">{product.category}</Descriptions.Item>
            <Descriptions.Item label="价格">¥{product.price.toFixed(2)}</Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={product.status === 'published' ? 'green' : 'default'}>
                {product.status}
              </Tag>
            </Descriptions.Item>
          </Descriptions>
        </Card>
      )}

      {/* 任务结果 */}
      {task.result && (
        <Card title="任务结果" style={{ marginBottom: 16 }}>
          <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 4, overflow: 'auto' }}>
            {JSON.stringify(task.result, null, 2)}
          </pre>
        </Card>
      )}

      {/* 执行日志 */}
      <Card title="执行日志">
        {logs.length > 0 ? (
          <div style={{ maxHeight: 500, overflow: 'auto' }}>
            <Timeline>
              {logs.map((log) => (
                <Timeline.Item
                  key={log.id}
                  color={
                    log.log_level === 'ERROR'
                      ? 'red'
                      : log.log_level === 'WARNING'
                      ? 'orange'
                      : 'blue'
                  }
                >
                  <div>
                    <Space>
                      <Tag color={getLogLevelColor(log.log_level)}>{log.log_level}</Tag>
                      <span style={{ color: '#8c8c8c' }}>
                        {new Date(log.created_at).toLocaleString('zh-CN')}
                      </span>
                      <span style={{ color: '#1890ff' }}>[{log.agent_name}]</span>
                    </Space>
                    <div style={{ marginTop: 8 }}>{log.message}</div>
                    {log.extra_data && (
                      <pre
                        style={{
                          background: '#f5f5f5',
                          padding: 8,
                          marginTop: 8,
                          borderRadius: 4,
                          fontSize: 12,
                        }}
                      >
                        {JSON.stringify(log.extra_data, null, 2)}
                      </pre>
                    )}
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
            <div ref={logsEndRef} />
          </div>
        ) : (
          <Empty description="暂无日志" />
        )}
      </Card>
    </div>
  )
}

export default TaskDetail
