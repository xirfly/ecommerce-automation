import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Table,
  Button,
  Input,
  Select,
  Space,
  Modal,
  Form,
  InputNumber,
  Checkbox,
  message,
  Tag,
  Image,
} from 'antd'
import { PlusOutlined, SearchOutlined, DeleteOutlined } from '@ant-design/icons'
import { productApi, Product, CreateProductParams } from '@/api/product'
import type { ColumnsType } from 'antd/es/table'

const { Option } = Select

const ProductList: React.FC = () => {
  const navigate = useNavigate()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [keyword, setKeyword] = useState('')
  const [category, setCategory] = useState<string>()
  const [status, setStatus] = useState<string>()
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadProducts()
  }, [page, pageSize, keyword, category, status])

  const loadProducts = async () => {
    setLoading(true)
    try {
      const response = await productApi.getList({
        page,
        page_size: pageSize,
        keyword,
        category,
        status,
      })
      setProducts(response.data.items)
      setTotal(response.data.total)
    } catch (error) {
      // 错误已在拦截器中处理
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (values: any) => {
    try {
      // 将平台数组转换为逗号分隔的字符串
      const submitData = {
        ...values,
        platform: Array.isArray(values.platform)
          ? values.platform.join(',')
          : values.platform
      }
      await productApi.create(submitData)
      message.success('创建成功')
      setCreateModalVisible(false)
      form.resetFields()
      loadProducts()
    } catch (error) {
      // 错误已在拦截器中处理
    }
  }

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除这个产品吗？',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        await productApi.delete(id)
        message.success('删除成功')
        loadProducts()
      },
    })
  }

  const handleBatchDelete = () => {
    Modal.confirm({
      title: `确认删除 ${selectedRowKeys.length} 个产品？`,
      content: '批量删除后无法恢复',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        await productApi.batchDelete(selectedRowKeys as number[])
        message.success(`成功删除 ${selectedRowKeys.length} 个产品`)
        setSelectedRowKeys([])
        loadProducts()
      },
    })
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

  const columns: ColumnsType<Product> = [
    {
      title: '图片',
      dataIndex: 'images',
      key: 'images',
      width: 80,
      render: (images: string[]) =>
        images?.[0] ? (
          <Image src={images[0]} width={50} height={50} style={{ objectFit: 'cover' }} />
        ) : (
          <div
            style={{
              width: 50,
              height: 50,
              background: '#f0f0f0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            暂无
          </div>
        ),
    },
    {
      title: '产品名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: Product['status']) => getStatusTag(status),
    },
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      render: (platform: string) => platform || '-',
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
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" onClick={() => navigate(`/products/${record.id}`)}>
            查看
          </Button>
          <Button type="link" size="small" onClick={() => navigate(`/products/${record.id}`)}>
            编辑
          </Button>
          <Button type="link" danger size="small" onClick={() => handleDelete(record.id)}>
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>产品管理</h2>

      {/* 搜索栏 */}
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索产品名称"
          prefix={<SearchOutlined />}
          style={{ width: 200 }}
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          allowClear
        />
        <Select
          placeholder="产品分类"
          style={{ width: 120 }}
          value={category}
          onChange={setCategory}
          allowClear
        >
          <Option value="数码">数码</Option>
          <Option value="服饰">服饰</Option>
          <Option value="家居">家居</Option>
          <Option value="美妆">美妆</Option>
        </Select>
        <Select
          placeholder="状态"
          style={{ width: 120 }}
          value={status}
          onChange={setStatus}
          allowClear
        >
          <Option value="draft">草稿</Option>
          <Option value="analyzing">分析中</Option>
          <Option value="generating">生成中</Option>
          <Option value="published">已发布</Option>
        </Select>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalVisible(true)}>
          新建产品
        </Button>
      </Space>

      {/* 批量操作 */}
      {selectedRowKeys.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <Space>
            <span>已选 {selectedRowKeys.length} 项</span>
            <Button danger icon={<DeleteOutlined />} onClick={handleBatchDelete}>
              批量删除
            </Button>
          </Space>
        </div>
      )}

      {/* 表格 */}
      <Table
        rowSelection={{
          selectedRowKeys,
          onChange: setSelectedRowKeys,
        }}
        columns={columns}
        dataSource={products}
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

      {/* 新建产品弹窗 */}
      <Modal
        title="新建产品"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false)
          form.resetFields()
        }}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            label="产品名称"
            name="name"
            rules={[{ required: true, message: '请输入产品名称' }]}
          >
            <Input placeholder="请输入产品名称" />
          </Form.Item>

          <Form.Item
            label="产品分类"
            name="category"
            rules={[{ required: true, message: '请选择产品分类' }]}
          >
            <Select placeholder="请选择产品分类">
              <Option value="数码">数码</Option>
              <Option value="服饰">服饰</Option>
              <Option value="家居">家居</Option>
              <Option value="美妆">美妆</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="目标价格"
            name="price"
            rules={[{ required: true, message: '请输入目标价格' }]}
          >
            <InputNumber
              placeholder="请输入目标价格"
              style={{ width: '100%' }}
              min={0}
              precision={2}
              prefix="¥"
            />
          </Form.Item>

          <Form.Item label="目标平台" name="platform">
            <Checkbox.Group>
              <Checkbox value="淘宝">淘宝</Checkbox>
              <Checkbox value="京东">京东</Checkbox>
              <Checkbox value="拼多多">拼多多</Checkbox>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item label="产品描述" name="description">
            <Input.TextArea rows={4} placeholder="请输入产品描述（可选）" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button onClick={() => setCreateModalVisible(false)}>取消</Button>
              <Button type="default" htmlType="submit">
                保存草稿
              </Button>
              <Button type="primary" htmlType="submit">
                立即分析
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ProductList
