/**
 * 渠道配置页面
 * 管理电商平台和通知渠道
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
  Popconfirm,
  Row,
  Col,
  Statistic,
  Typography,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ApiOutlined,
  ThunderboltOutlined,
  ShopOutlined,
  BellOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getChannelList,
  createChannel,
  updateChannel,
  deleteChannel,
  testChannel,
  getChannelStatistics,
  type Channel,
  type ChannelCreateRequest,
  type ChannelUpdateRequest,
  type ChannelStatistics,
} from '../api/channel';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const ChannelConfig: React.FC = () => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [statistics, setStatistics] = useState<ChannelStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingChannel, setEditingChannel] = useState<Channel | null>(null);
  const [form] = Form.useForm();
  const [filterType, setFilterType] = useState<string | undefined>(undefined);
  const [filterStatus, setFilterStatus] = useState<string | undefined>(undefined);

  // 平台配置模板
  const platformTemplates = {
    // 电商平台
    taobao: {
      name: '淘宝',
      fields: ['app_key', 'app_secret', 'session_key'],
    },
    jd: {
      name: '京东',
      fields: ['app_key', 'app_secret', 'access_token'],
    },
    pdd: {
      name: '拼多多',
      fields: ['client_id', 'client_secret'],
    },
    // 通知渠道
    lark: {
      name: '飞书',
      fields: ['webhook_url', 'secret'],
    },
    telegram: {
      name: 'Telegram',
      fields: ['bot_token', 'chat_id'],
    },
    wecom: {
      name: '企业微信',
      fields: ['webhook_url', 'key'],
    },
  };

  // 加载渠道列表
  const loadChannels = async () => {
    setLoading(true);
    try {
      const response = await getChannelList({
        channel_type: filterType,
        status: filterStatus,
      });
      if (response.code === 0) {
        setChannels(response.data);
      } else {
        message.error(response.message || '加载渠道列表失败');
      }
    } catch (error) {
      message.error('加载渠道列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载统计数据
  const loadStatistics = async () => {
    try {
      const response = await getChannelStatistics();
      if (response.code === 0) {
        setStatistics(response.data);
      }
    } catch (error) {
      console.error('加载统计数据失败', error);
    }
  };

  useEffect(() => {
    loadChannels();
    loadStatistics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterType, filterStatus]);

  // 打开添加/编辑模态框
  const handleOpenModal = (channel?: Channel) => {
    if (channel) {
      setEditingChannel(channel);
      form.setFieldsValue({
        name: channel.name,
        channel_type: channel.channel_type,
        platform: channel.platform,
        description: channel.description,
        config: JSON.stringify(channel.config, null, 2),
        is_default: channel.is_default,
        status: channel.status,
      });
    } else {
      setEditingChannel(null);
      form.resetFields();
    }
    setModalVisible(true);
  };

  // 关闭模态框
  const handleCloseModal = () => {
    setModalVisible(false);
    setEditingChannel(null);
    form.resetFields();
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      // 解析 config JSON
      let config;
      try {
        config = JSON.parse(values.config);
      } catch (e) {
        message.error('配置 JSON 格式错误');
        return;
      }

      if (editingChannel) {
        // 更新渠道
        const updateData: ChannelUpdateRequest = {
          name: values.name,
          description: values.description,
          config,
          status: values.status,
          is_default: values.is_default,
        };
        const response = await updateChannel(editingChannel.id, updateData);
        if (response.code === 0) {
          message.success('更新成功');
          handleCloseModal();
          loadChannels();
          loadStatistics();
        } else {
          message.error(response.message || '更新失败');
        }
      } else {
        // 创建渠道
        const createData: ChannelCreateRequest = {
          name: values.name,
          channel_type: values.channel_type,
          platform: values.platform,
          description: values.description,
          config,
          is_default: values.is_default,
        };
        const response = await createChannel(createData);
        if (response.code === 0) {
          message.success('创建成功');
          handleCloseModal();
          loadChannels();
          loadStatistics();
        } else {
          message.error(response.message || '创建失败');
        }
      }
    } catch (error) {
      console.error('表单验证失败', error);
    }
  };

  // 删除渠道
  const handleDelete = async (channelId: number) => {
    try {
      const response = await deleteChannel(channelId);
      if (response.code === 0) {
        message.success('删除成功');
        loadChannels();
        loadStatistics();
      } else {
        message.error(response.message || '删除失败');
      }
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 测试连接
  const handleTest = async (channelId: number) => {
    try {
      const response = await testChannel({ channel_id: channelId });
      if (response.code === 0) {
        if (response.data.success) {
          message.success(response.data.message);
        } else {
          message.error(response.data.message);
        }
      } else {
        message.error(response.message || '测试失败');
      }
    } catch (error) {
      message.error('测试失败');
    }
  };

  // 表格列定义
  const columns: ColumnsType<Channel> = [
    {
      title: '渠道名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Channel) => (
        <Space>
          {record.channel_type === 'ecommerce' ? (
            <ShopOutlined style={{ color: '#1890ff' }} />
          ) : (
            <BellOutlined style={{ color: '#52c41a' }} />
          )}
          <Text strong>{name}</Text>
          {record.is_default && <Tag color="gold">默认</Tag>}
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'channel_type',
      key: 'channel_type',
      render: (type: string) => (
        <Tag color={type === 'ecommerce' ? 'blue' : 'green'}>
          {type === 'ecommerce' ? '电商平台' : '通知渠道'}
        </Tag>
      ),
    },
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      render: (platform: string) => {
        const template = platformTemplates[platform as keyof typeof platformTemplates];
        return template ? template.name : platform;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusConfig = {
          active: { color: 'success', icon: <CheckCircleOutlined />, text: '启用' },
          inactive: { color: 'default', icon: <CloseCircleOutlined />, text: '禁用' },
          error: { color: 'error', icon: <CloseCircleOutlined />, text: '错误' },
        };
        const config = statusConfig[status as keyof typeof statusConfig];
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      },
    },
    {
      title: '使用次数',
      dataIndex: 'usage_count',
      key: 'usage_count',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record: Channel) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<ThunderboltOutlined />}
            onClick={() => handleTest(record.id)}
          >
            测试
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleOpenModal(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个渠道吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <ApiOutlined /> 渠道配置
      </Title>

      {/* 统计卡片 */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总渠道数"
                value={statistics.total_channels}
                prefix={<ApiOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="启用渠道"
                value={statistics.active_channels}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="电商平台"
                value={statistics.ecommerce_channels}
                prefix={<ShopOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="通知渠道"
                value={statistics.notification_channels}
                prefix={<BellOutlined />}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 渠道列表 */}
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            添加渠道
          </Button>
          <Select
            placeholder="渠道类型"
            style={{ width: 150 }}
            allowClear
            value={filterType}
            onChange={setFilterType}
          >
            <Option value="ecommerce">电商平台</Option>
            <Option value="notification">通知渠道</Option>
          </Select>
          <Select
            placeholder="状态"
            style={{ width: 120 }}
            allowClear
            value={filterStatus}
            onChange={setFilterStatus}
          >
            <Option value="active">启用</Option>
            <Option value="inactive">禁用</Option>
            <Option value="error">错误</Option>
          </Select>
        </Space>

        <Table
          columns={columns}
          dataSource={channels}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 添加/编辑模态框 */}
      <Modal
        title={editingChannel ? '编辑渠道' : '添加渠道'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={handleCloseModal}
        width={600}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="渠道名称"
            rules={[{ required: true, message: '请输入渠道名称' }]}
          >
            <Input placeholder="例如：淘宝主店" />
          </Form.Item>

          {!editingChannel && (
            <>
              <Form.Item
                name="channel_type"
                label="渠道类型"
                rules={[{ required: true, message: '请选择渠道类型' }]}
              >
                <Select placeholder="选择渠道类型">
                  <Option value="ecommerce">电商平台</Option>
                  <Option value="notification">通知渠道</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="platform"
                label="平台"
                rules={[{ required: true, message: '请选择平台' }]}
              >
                <Select placeholder="选择平台">
                  <Option value="taobao">淘宝</Option>
                  <Option value="jd">京东</Option>
                  <Option value="pdd">拼多多</Option>
                  <Option value="lark">飞书</Option>
                  <Option value="telegram">Telegram</Option>
                  <Option value="wecom">企业微信</Option>
                </Select>
              </Form.Item>
            </>
          )}

          <Form.Item name="description" label="描述">
            <TextArea rows={2} placeholder="渠道描述" />
          </Form.Item>

          <Form.Item
            name="config"
            label="配置（JSON 格式）"
            rules={[{ required: true, message: '请输入配置' }]}
          >
            <TextArea
              rows={6}
              placeholder='{"app_key": "xxx", "app_secret": "xxx"}'
            />
          </Form.Item>

          {editingChannel && (
            <Form.Item name="status" label="状态">
              <Select>
                <Option value="active">启用</Option>
                <Option value="inactive">禁用</Option>
              </Select>
            </Form.Item>
          )}

          <Form.Item name="is_default" label="设为默认" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ChannelConfig;
