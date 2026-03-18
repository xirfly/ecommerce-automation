import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Table,
  Button,
  Space,
  Tag,
  Select,
  Card,
  Statistic,
  Row,
  Col,
  Modal,
  Form,
  message,
} from 'antd'
import { ReloadOutlined, DeleteOutlined, EyeOutlined, PlusOutlined } from '@ant-design/icons'
import { taskApi, Task } from '@/api/task'
import { productApi, Product } from '@/api/product'
import type { ColumnsType } from 'antd/es/table'

const { Option } = Select

const TaskCenter: React.FC = () => {
  const navigate = useNavigate()
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [taskType, setTaskType] = useState<string>()
  const [status, setStatus] = useState<string>()
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [products, setProducts] = useState<Product[]>([])
  const [form] = Form.useForm()
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    running: 0,
    success: 0,
    failed: 0,
  })

  useEffect(() => {
    loadTasks()
    loadProducts()
  }, [page, pageSize, taskType, status])

  const loadProducts = async () => {
    try {
      const response = await productApi.getList({ page: 1, page_size: 100 })
      setProducts(response.data.items)
    } catch (error) {
      // 错误已在拦截器中处理
    }
  }

  const loadTasks = async () => {
    setLoading(true)
    try {
      const response = await taskApi.getList({
        page,
        page_size: pageSize,
        task_type: taskType,
        status,
      })
      setTasks(response.data.items)
      setTotal(response.data.total)

      // 计算统计数据
      const allTasks = response.data.items
      setStats({
        total: response.data.total,
        pending: allTasks.filter(t => t.status === 'pending').length,
        running: allTasks.filter(t => t.status === 'running').length,
        success: allTasks.filter(t => t.status === 'success').length,
        failed: allTasks.filter(t => t.status === 'failed').length,
      })
    } catch (error) {
      // 错误已在拦截器中处理
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = async (taskId: number) => {
    try {
      await taskApi.retry(taskId)
      message.success('任务已重新提交')
      loadTasks()
    } catch (error) {
      // 错误已在拦截器中处理
    }
  }

  const handleDelete = (taskId: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个任务吗？',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        await taskApi.delete(taskId)
        message.success('删除成功')
        loadTasks()
      },
    })
  }

  const handleCreate = async () => {
    try {
      const values = await form.validateFields()

      // 先关闭弹窗，提升响应速度
      setCreateModalVisible(false)
      form.resetFields()

      // 后台创建任务
      await taskApi.create({
        product_id: values.product_id,
        task_type: values.task_type,
      })

      message.success('任务创建成功')

      // 延迟刷新列表，避免阻塞
      setTimeout(() => {
        loadTasks()
      }, 100)
    } catch (error) {
      // 错误已在拦截器中处理
      // 如果出错，重新打开弹窗
      setCreateModalVisible(true)
    }
  }

  const getStatusTag = (status: Task['status']) => {
    const statusMap = {
      pending: { color: 'default', text: '待执行' },
      running: { color: 'blue', text: '执行中' },
      success: { color: 'green', text: '成功' },
      failed: { color: 'red', text: '失败' },
      timeout: { color: 'orange', text: '超时' },
    }
    const config = statusMap[status]
    return <Tag color={config.color}>{config.text}</Tag>
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

  const columns: ColumnsType<Task> = [
    {
      title: '任务ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '产品ID',
      dataIndex: 'product_id',
      key: 'product_id',
      width: 100,
      render: (productId: number) => (
        <Button
          type="link"
          size="small"
          onClick={() => navigate(`/products/${productId}`)}
        >
          #{productId}
        </Button>
      ),
    },
    {
      title: '任务类型',
      dataIndex: 'task_type',
      key: 'task_type',
      render: (type: string) => getTaskTypeName(type),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: Task['status']) => getStatusTag(status),
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 100,
      render: (progress: number) => `${progress}%`,
    },
    {
      title: '重试次数',
      dataIndex: 'retry_count',
      key: 'retry_count',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/tasks/${record.id}`)}
          >
            详情
          </Button>
          {(record.status === 'failed' || record.status === 'timeout') && (
            <Button
              type="link"
              size="small"
              icon={<ReloadOutlined />}
              onClick={() => handleRetry(record.id)}
            >
              重试
            </Button>
          )}
          {record.status !== 'running' && (
            <Button
              type="link"
              danger
              size="small"
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(record.id)}
            >
              删除
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>任务中心</h2>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="总任务数" value={stats.total} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待执行"
              value={stats.pending}
              valueStyle={{ color: '#8c8c8c' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="执行中"
              value={stats.running}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="成功"
              value={stats.success}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选栏 */}
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalVisible(true)}>
          创建任务
        </Button>
        <Select
          placeholder="任务类型"
          style={{ width: 150 }}
          value={taskType}
          onChange={setTaskType}
          allowClear
        >
          <Option value="product_analysis">选品分析</Option>
          <Option value="content_generation">内容生成</Option>
          <Option value="image_generation">图片生成</Option>
          <Option value="video_generation">视频生成</Option>
          <Option value="review">内容审核</Option>
          <Option value="publish">发布上架</Option>
        </Select>
        <Select
          placeholder="状态"
          style={{ width: 120 }}
          value={status}
          onChange={setStatus}
          allowClear
        >
          <Option value="pending">待执行</Option>
          <Option value="running">执行中</Option>
          <Option value="success">成功</Option>
          <Option value="failed">失败</Option>
          <Option value="timeout">超时</Option>
        </Select>
        <Button icon={<ReloadOutlined />} onClick={loadTasks}>
          刷新
        </Button>
      </Space>

      {/* 任务表格 */}
      <Table
        columns={columns}
        dataSource={tasks}
        rowKey="id"
        loading={loading}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setPage(page)
            setPageSize(pageSize)
          },
        }}
      />

      {/* 创建任务弹窗 */}
      <Modal
        title="创建任务"
        open={createModalVisible}
        onOk={handleCreate}
        onCancel={() => {
          setCreateModalVisible(false)
          form.resetFields()
        }}
        okText="创建"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="product_id"
            label="选择产品"
            rules={[{ required: true, message: '请选择产品' }]}
          >
            <Select placeholder="请选择产品" showSearch optionFilterProp="children">
              {products.map((product) => (
                <Option key={product.id} value={product.id}>
                  {product.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="task_type"
            label="任务类型"
            rules={[{ required: true, message: '请选择任务类型' }]}
          >
            <Select placeholder="请选择任务类型">
              <Option value="product_analysis">选品分析</Option>
              <Option value="content_generation">内容生成</Option>
              <Option value="image_generation">图片生成</Option>
              <Option value="video_generation">视频生成</Option>
              <Option value="review">内容审核</Option>
              <Option value="publish">发布上架</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default TaskCenter
