/**
 * 反馈管理页面（管理员）
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Modal,
  Form,
  Select,
  Input,
  message,
  Row,
  Col,
  Statistic,
  Image,
  Descriptions,
  Typography,
} from 'antd';
import {
  BugOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getFeedbackList,
  getFeedbackDetail,
  updateFeedback,
  deleteFeedback,
  getFeedbackStatistics,
  type Feedback,
  type FeedbackStatistics,
} from '@/api/feedback';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const FeedbackManagement: React.FC = () => {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [statistics, setStatistics] = useState<FeedbackStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [priorityFilter, setPriorityFilter] = useState<string | undefined>();
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [updateModalVisible, setUpdateModalVisible] = useState(false);
  const [selectedFeedback, setSelectedFeedback] = useState<Feedback | null>(null);
  const [updateForm] = Form.useForm();

  useEffect(() => {
    loadFeedbacks();
    loadStatistics();
  }, [page, pageSize, statusFilter, priorityFilter]);

  const loadFeedbacks = async () => {
    setLoading(true);
    try {
      const response = await getFeedbackList({
        page,
        page_size: pageSize,
        status: statusFilter,
        priority: priorityFilter,
      });
      if (response.code === 0) {
        setFeedbacks(response.data.items);
        setTotal(response.data.total);
      } else {
        message.error(response.message || '加载失败');
      }
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await getFeedbackStatistics();
      if (response.code === 0) {
        setStatistics(response.data);
      }
    } catch (error) {
      // 忽略统计加载错误
    }
  };

  const handleViewDetail = async (record: Feedback) => {
    try {
      const response = await getFeedbackDetail(record.id);
      if (response.code === 0) {
        setSelectedFeedback(response.data);
        setDetailModalVisible(true);
      } else {
        message.error(response.message || '加载详情失败');
      }
    } catch (error) {
      message.error('加载详情失败');
    }
  };

  const handleUpdate = (record: Feedback) => {
    setSelectedFeedback(record);
    updateForm.setFieldsValue({
      status: record.status,
      priority: record.priority,
      admin_reply: record.admin_reply,
    });
    setUpdateModalVisible(true);
  };

  const handleUpdateSubmit = async (values: any) => {
    if (!selectedFeedback) return;

    try {
      const response = await updateFeedback(selectedFeedback.id, values);
      if (response.code === 0) {
        message.success('更新成功');
        setUpdateModalVisible(false);
        loadFeedbacks();
        loadStatistics();
      } else {
        message.error(response.message || '更新失败');
      }
    } catch (error) {
      message.error('更新失败');
    }
  };

  const handleDelete = (record: Feedback) => {
    Modal.confirm({
      title: '确认删除',
      icon: <ExclamationCircleOutlined />,
      content: `确定要删除反馈「${record.title}」吗？`,
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await deleteFeedback(record.id);
          if (response.code === 0) {
            message.success('删除成功');
            loadFeedbacks();
            loadStatistics();
          } else {
            message.error(response.message || '删除失败');
          }
        } catch (error) {
          message.error('删除失败');
        }
      },
    });
  };

  const getStatusTag = (status: Feedback['status']) => {
    const statusMap = {
      pending: { color: 'default', text: '待处理' },
      processing: { color: 'blue', text: '处理中' },
      resolved: { color: 'green', text: '已解决' },
      closed: { color: 'red', text: '已关闭' },
    };
    const config = statusMap[status];
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const getPriorityTag = (priority: Feedback['priority']) => {
    const priorityMap = {
      low: { color: 'default', text: '低' },
      medium: { color: 'blue', text: '中' },
      high: { color: 'orange', text: '高' },
      urgent: { color: 'red', text: '紧急' },
    };
    const config = priorityMap[priority];
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const columns: ColumnsType<Feedback> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '提交人',
      dataIndex: 'username',
      key: 'username',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: Feedback['status']) => getStatusTag(status),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: Feedback['priority']) => getPriorityTag(priority),
    },
    {
      title: '提交时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
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
            onClick={() => handleViewDetail(record)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleUpdate(record)}
          >
            处理
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <BugOutlined /> 反馈管理
      </Title>

      {/* 统计卡片 */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总反馈数"
                value={statistics.total}
                prefix={<BugOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="待处理"
                value={statistics.by_status.pending || 0}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="处理中"
                value={statistics.by_status.processing || 0}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="已解决"
                value={statistics.by_status.resolved || 0}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 筛选器 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Text>状态：</Text>
          <Select
            style={{ width: 120 }}
            placeholder="全部"
            allowClear
            value={statusFilter}
            onChange={setStatusFilter}
          >
            <Option value="pending">待处理</Option>
            <Option value="processing">处理中</Option>
            <Option value="resolved">已解决</Option>
            <Option value="closed">已关闭</Option>
          </Select>

          <Text>优先级：</Text>
          <Select
            style={{ width: 120 }}
            placeholder="全部"
            allowClear
            value={priorityFilter}
            onChange={setPriorityFilter}
          >
            <Option value="low">低</Option>
            <Option value="medium">中</Option>
            <Option value="high">高</Option>
            <Option value="urgent">紧急</Option>
          </Select>

          <Button onClick={loadFeedbacks}>刷新</Button>
        </Space>
      </Card>

      {/* 反馈列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={feedbacks}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setPage(page);
              setPageSize(pageSize);
            },
          }}
        />
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title="反馈详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {selectedFeedback && (
          <div>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="反馈ID">{selectedFeedback.id}</Descriptions.Item>
              <Descriptions.Item label="提交人">{selectedFeedback.username}</Descriptions.Item>
              <Descriptions.Item label="状态">
                {getStatusTag(selectedFeedback.status)}
              </Descriptions.Item>
              <Descriptions.Item label="优先级">
                {getPriorityTag(selectedFeedback.priority)}
              </Descriptions.Item>
              <Descriptions.Item label="提交时间" span={2}>
                {new Date(selectedFeedback.created_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
              <Descriptions.Item label="标题" span={2}>
                {selectedFeedback.title}
              </Descriptions.Item>
              <Descriptions.Item label="问题描述" span={2}>
                <div style={{ whiteSpace: 'pre-wrap' }}>{selectedFeedback.description}</div>
              </Descriptions.Item>
              {selectedFeedback.images && selectedFeedback.images.length > 0 && (
                <Descriptions.Item label="截图" span={2}>
                  <Image.PreviewGroup>
                    <Space>
                      {selectedFeedback.images.map((url, index) => (
                        <Image
                          key={index}
                          width={100}
                          src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${url}`}
                        />
                      ))}
                    </Space>
                  </Image.PreviewGroup>
                </Descriptions.Item>
              )}
              {selectedFeedback.admin_reply && (
                <Descriptions.Item label="管理员回复" span={2}>
                  <div style={{ whiteSpace: 'pre-wrap' }}>{selectedFeedback.admin_reply}</div>
                </Descriptions.Item>
              )}
            </Descriptions>
          </div>
        )}
      </Modal>

      {/* 更新弹窗 */}
      <Modal
        title="处理反馈"
        open={updateModalVisible}
        onCancel={() => setUpdateModalVisible(false)}
        onOk={() => updateForm.submit()}
        okText="保存"
        cancelText="取消"
        afterOpenChange={(open) => {
          if (open && selectedFeedback) {
            updateForm.setFieldsValue({
              status: selectedFeedback.status,
              priority: selectedFeedback.priority,
              admin_reply: selectedFeedback.admin_reply,
            });
          }
        }}
      >
        <Form
          form={updateForm}
          layout="vertical"
          onFinish={handleUpdateSubmit}
        >
          <Form.Item label="状态" name="status">
            <Select>
              <Option value="pending">待处理</Option>
              <Option value="processing">处理中</Option>
              <Option value="resolved">已解决</Option>
              <Option value="closed">已关闭</Option>
            </Select>
          </Form.Item>

          <Form.Item label="优先级" name="priority">
            <Select>
              <Option value="low">低</Option>
              <Option value="medium">中</Option>
              <Option value="high">高</Option>
              <Option value="urgent">紧急</Option>
            </Select>
          </Form.Item>

          <Form.Item label="管理员回复" name="admin_reply">
            <TextArea rows={4} placeholder="回复用户的反馈..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default FeedbackManagement;
