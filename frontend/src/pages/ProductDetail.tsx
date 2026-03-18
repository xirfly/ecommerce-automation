import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Descriptions,
  Button,
  Space,
  Tag,
  Image,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  message,
  Table,
  Tabs,
} from 'antd'
import { ArrowLeftOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons'
import { productApi, Product } from '@/api/product'
import { taskApi, Task, CreateTaskParams } from '@/api/task'
import type { ColumnsType } from 'antd/es/table'

const { Option } = Select
const { TextArea } = Input

const ProductDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [product, setProduct] = useState<Product | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(false)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [createTaskModalVisible, setCreateTaskModalVisible] = useState(false)
  const [form] = Form.useForm()
  const [taskForm] = Form.useForm()

  useEffect(() => {
    if (id) {
      loadProduct()
      loadTasks()
    }
  }, [id])

  const loadProduct = async () => {
    setLoading(true)
    try {
      const response = await productApi.getDetail(Number(id))
      setProduct(response.data)
    } catch (error) {
      // 错误已在拦截器中处理
    } finally {
      setLoading(false)
    }
  }

  const loadTasks = async () => {
    try {
      const response = await taskApi.getList({ product_id: Number(id) })
      setTasks(response.data.items)
    } catch (error) {
      // 错误已在拦截器中处理
    }
  }

  const handleEdit = async (values: any) => {
    try {
      await productApi.update(Number(id), values)
      message.success('更新成功')
      setEditModalVisible(false)
      loadProduct()
    } catch (error) {
      // 错误已在拦截器中处理
    }
  }

  const handleDelete = () => {
    Modal.confirm({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除这个产品吗？',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        await productApi.delete(Number(id))
        message.success('删除成功')
        navigate('/products')
      },
    })
  }

  const handleCreateTask = async (values: CreateTaskParams) => {
    try {
      await taskApi.create({
        ...values,
        product_id: Number(id),
      })
      message.success('任务创建成功')
      setCreateTaskModalVisible(false)
      taskForm.resetFields()
      loadTasks()
    } catch (error) {
      // 错误已在拦截器中处理
    }
  }

  const handleRetryTask = async (taskId: number) => {
    try {
      await taskApi.retry(taskId)
      message.success('任务已重新提交')
      loadTasks()
    } catch (error) {
      // 错误已在拦截器中处理
    }
  }

  const getStatusTag = (status: Product['status']) => {
    const statusMap = {
      draft: { color: 'default', text: '草稿' },
      analyzing: { color: 'blue', text: '分析中' },
      generating: { color: 'purple', text: '生成中' },
      reviewing: { color: 'orange', text: '审核中' },
      published: { color: 'green', text: '已发布' },
      offline: { color: 'red', text: '已下架' },
    }
    const config = statusMap[status]
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const getTaskStatusTag = (status: Task['status']) => {
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

  const taskColumns: ColumnsType<Task> = [
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
      render: (status: Task['status']) => getTaskStatusTag(status),
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number) => `${progress}%`,
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
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            onClick={() => navigate(`/tasks/${record.id}`)}
          >
            查看详情
          </Button>
          {(record.status === 'failed' || record.status === 'timeout') && (
            <Button
              type="link"
              size="small"
              onClick={() => handleRetryTask(record.id)}
            >
              重试
            </Button>
          )}
        </Space>
      ),
    },
  ]

  if (!product) {
    return <div>加载中...</div>
  }

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/products')}>
          返回
        </Button>
        <Button icon={<EditOutlined />} onClick={() => setEditModalVisible(true)}>
          编辑
        </Button>
        <Button
          icon={<PlayCircleOutlined />}
          type="primary"
          onClick={() => setCreateTaskModalVisible(true)}
        >
          创建任务
        </Button>
        <Button icon={<DeleteOutlined />} danger onClick={handleDelete}>
          删除
        </Button>
      </Space>

      <Tabs
        items={[
          {
            key: 'info',
            label: '基本信息',
            children: (
              <Card>
                <Descriptions column={2} bordered>
                  <Descriptions.Item label="产品名称">{product.name}</Descriptions.Item>
                  <Descriptions.Item label="分类">{product.category}</Descriptions.Item>
                  <Descriptions.Item label="价格">¥{product.price.toFixed(2)}</Descriptions.Item>
                  <Descriptions.Item label="成本">
                    {product.cost ? `¥${product.cost.toFixed(2)}` : '-'}
                  </Descriptions.Item>
                  <Descriptions.Item label="状态">{getStatusTag(product.status)}</Descriptions.Item>
                  <Descriptions.Item label="平台">{product.platform || '-'}</Descriptions.Item>
                  <Descriptions.Item label="创建时间" span={2}>
                    {new Date(product.created_at).toLocaleString('zh-CN')}
                  </Descriptions.Item>
                  <Descriptions.Item label="产品描述" span={2}>
                    {product.description || '-'}
                  </Descriptions.Item>
                  {product.detail_page_url && (
                    <Descriptions.Item label="详情页链接" span={2}>
                      <a href={product.detail_page_url} target="_blank" rel="noopener noreferrer">
                        {product.detail_page_url}
                      </a>
                    </Descriptions.Item>
                  )}
                </Descriptions>

                {product.images && product.images.length > 0 && (
                  <div style={{ marginTop: 24 }}>
                    <h3>产品图片</h3>
                    <Image.PreviewGroup>
                      <Space>
                        {product.images.map((img, index) => (
                          <Image key={index} width={100} src={img} />
                        ))}
                      </Space>
                    </Image.PreviewGroup>
                  </div>
                )}
              </Card>
            ),
          },
          {
            key: 'tasks',
            label: `任务列表 (${tasks.length})`,
            children: (
              <Card>
                <Table
                  columns={taskColumns}
                  dataSource={tasks}
                  rowKey="id"
                  pagination={false}
                />
              </Card>
            ),
          },
        ]}
      />

      {/* 编辑产品弹窗 */}
      <Modal
        title="编辑产品"
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        onOk={() => form.submit()}
        okText="保存"
        cancelText="取消"
        width={600}
        afterOpenChange={(open) => {
          if (open && product) {
            form.setFieldsValue(product)
          }
        }}
      >
        <Form form={form} layout="vertical" onFinish={handleEdit}>
          <Form.Item label="产品名称" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="分类" name="category" rules={[{ required: true }]}>
            <Select>
              <Option value="数码">数码</Option>
              <Option value="服饰">服饰</Option>
              <Option value="家居">家居</Option>
              <Option value="美妆">美妆</Option>
            </Select>
          </Form.Item>
          <Form.Item label="价格" name="price" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={0} precision={2} prefix="¥" />
          </Form.Item>
          <Form.Item label="成本" name="cost">
            <InputNumber style={{ width: '100%' }} min={0} precision={2} prefix="¥" />
          </Form.Item>
          <Form.Item label="平台" name="platform">
            <Input />
          </Form.Item>
          <Form.Item label="产品描述" name="description">
            <TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 创建任务弹窗 */}
      <Modal
        title="创建任务"
        open={createTaskModalVisible}
        onCancel={() => setCreateTaskModalVisible(false)}
        footer={null}
      >
        <Form form={taskForm} layout="vertical" onFinish={handleCreateTask}>
          <Form.Item
            label="任务类型"
            name="task_type"
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
          <Form.Item>
            <Space>
              <Button onClick={() => setCreateTaskModalVisible(false)}>取消</Button>
              <Button type="primary" htmlType="submit">
                创建
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ProductDetail
