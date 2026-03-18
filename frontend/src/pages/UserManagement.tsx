/**
 * 用户管理页面
 * 管理系统用户、角色和权限
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
  UserOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  KeyOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getUserList,
  getUserStatistics,
  createUser,
  updateUser,
  deleteUser,
  updatePassword,
  type User,
  type UserCreateRequest,
  type UserUpdateRequest,
  type UserPasswordUpdateRequest,
  type UserStatistics,
} from '../api/user';

const { Title, Text } = Typography;
const { Option } = Select;

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [statistics, setStatistics] = useState<UserStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [passwordModalVisible, setPasswordModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [filterRole, setFilterRole] = useState<string | undefined>(undefined);
  const [filterStatus, setFilterStatus] = useState<boolean | undefined>(undefined);

  // 加载用户列表
  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await getUserList({
        role: filterRole,
        is_active: filterStatus,
      });
      if (response.code === 0) {
        setUsers(response.data);
      } else {
        message.error(response.message || '加载用户列表失败');
      }
    } catch (error) {
      message.error('加载用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载统计数据
  const loadStatistics = async () => {
    try {
      const response = await getUserStatistics();
      if (response.code === 0) {
        setStatistics(response.data);
      }
    } catch (error) {
      console.error('加载统计数据失败', error);
    }
  };

  useEffect(() => {
    loadUsers();
    loadStatistics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterRole, filterStatus]);

  // 打开添加/编辑模态框
  const handleOpenModal = (user?: User) => {
    if (user) {
      setEditingUser(user);
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        role: user.role,
        is_active: user.is_active,
      });
    } else {
      setEditingUser(null);
      form.resetFields();
    }
    setModalVisible(true);
  };

  // 关闭模态框
  const handleCloseModal = () => {
    setModalVisible(false);
    setEditingUser(null);
    form.resetFields();
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      if (editingUser) {
        // 更新用户
        const updateData: UserUpdateRequest = {
          email: values.email,
          role: values.role,
          is_active: values.is_active,
        };
        const response = await updateUser(editingUser.id, updateData);
        if (response.code === 0) {
          message.success('更新成功');
          handleCloseModal();
          loadUsers();
          loadStatistics();
        } else {
          message.error(response.message || '更新失败');
        }
      } else {
        // 创建用户
        const createData: UserCreateRequest = {
          username: values.username,
          password: values.password,
          email: values.email,
          role: values.role,
        };
        const response = await createUser(createData);
        if (response.code === 0) {
          message.success('创建成功');
          handleCloseModal();
          loadUsers();
          loadStatistics();
        } else {
          message.error(response.message || '创建失败');
        }
      }
    } catch (error) {
      console.error('表单验证失败', error);
    }
  };

  // 删除用户
  const handleDelete = async (userId: number) => {
    try {
      const response = await deleteUser(userId);
      if (response.code === 0) {
        message.success('删除成功');
        loadUsers();
        loadStatistics();
      } else {
        message.error(response.message || '删除失败');
      }
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 打开修改密码模态框
  const handleOpenPasswordModal = (userId: number) => {
    setSelectedUserId(userId);
    passwordForm.resetFields();
    setPasswordModalVisible(true);
  };

  // 关闭修改密码模态框
  const handleClosePasswordModal = () => {
    setPasswordModalVisible(false);
    setSelectedUserId(null);
    passwordForm.resetFields();
  };

  // 提交修改密码
  const handlePasswordSubmit = async () => {
    try {
      const values = await passwordForm.validateFields();
      if (selectedUserId) {
        const passwordData: UserPasswordUpdateRequest = {
          old_password: values.old_password,
          new_password: values.new_password,
        };
        const response = await updatePassword(selectedUserId, passwordData);
        if (response.code === 0) {
          message.success('密码修改成功');
          handleClosePasswordModal();
        } else {
          message.error(response.message || '密码修改失败');
        }
      }
    } catch (error) {
      console.error('表单验证失败', error);
    }
  };

  // 角色标签颜色
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'red';
      case 'operator':
        return 'blue';
      case 'viewer':
        return 'green';
      default:
        return 'default';
    }
  };

  // 角色名称
  const getRoleName = (role: string) => {
    switch (role) {
      case 'admin':
        return '管理员';
      case 'operator':
        return '操作员';
      case 'viewer':
        return '查看者';
      default:
        return role;
    }
  };

  // 表格列定义
  const columns: ColumnsType<User> = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      render: (username: string) => (
        <Space>
          <UserOutlined />
          <Text strong>{username}</Text>
        </Space>
      ),
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      render: (email: string | null) => email || '-',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => (
        <Tag color={getRoleColor(role)}>{getRoleName(role)}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'} icon={isActive ? <CheckCircleOutlined /> : <CloseCircleOutlined />}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record: User) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleOpenModal(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            icon={<KeyOutlined />}
            onClick={() => handleOpenPasswordModal(record.id)}
          >
            改密
          </Button>
          <Popconfirm
            title="确定要删除这个用户吗？"
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
        <TeamOutlined /> 用户管理
      </Title>

      {/* 统计卡片 */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总用户数"
                value={statistics.total_users}
                prefix={<TeamOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="启用用户"
                value={statistics.active_users}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card>
              <Statistic
                title="管理员"
                value={statistics.admin_users}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card>
              <Statistic
                title="操作员"
                value={statistics.operator_users}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card>
              <Statistic
                title="查看者"
                value={statistics.viewer_users}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 用户列表 */}
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            添加用户
          </Button>
          <Select
            placeholder="角色"
            style={{ width: 120 }}
            allowClear
            value={filterRole}
            onChange={setFilterRole}
          >
            <Option value="admin">管理员</Option>
            <Option value="operator">操作员</Option>
            <Option value="viewer">查看者</Option>
          </Select>
          <Select
            placeholder="状态"
            style={{ width: 120 }}
            allowClear
            value={filterStatus}
            onChange={setFilterStatus}
          >
            <Option value={true}>启用</Option>
            <Option value={false}>禁用</Option>
          </Select>
        </Space>

        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 添加/编辑模态框 */}
      <Modal
        title={editingUser ? '编辑用户' : '添加用户'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={handleCloseModal}
        width={500}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="username"
            label="用户名"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, max: 50, message: '用户名长度为3-50个字符' },
            ]}
          >
            <Input placeholder="请输入用户名" disabled={!!editingUser} />
          </Form.Item>

          {!editingUser && (
            <Form.Item
              name="password"
              label="密码"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' },
              ]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
          )}

          <Form.Item name="email" label="邮箱" rules={[{ type: 'email', message: '请输入有效的邮箱' }]}>
            <Input placeholder="请输入邮箱" />
          </Form.Item>

          <Form.Item
            name="role"
            label="角色"
            rules={[{ required: true, message: '请选择角色' }]}
            initialValue="viewer"
          >
            <Select>
              <Option value="admin">管理员</Option>
              <Option value="operator">操作员</Option>
              <Option value="viewer">查看者</Option>
            </Select>
          </Form.Item>

          {editingUser && (
            <Form.Item name="is_active" label="状态" valuePropName="checked" initialValue={true}>
              <Switch checkedChildren="启用" unCheckedChildren="禁用" />
            </Form.Item>
          )}
        </Form>
      </Modal>

      {/* 修改密码模态框 */}
      <Modal
        title="修改密码"
        open={passwordModalVisible}
        onOk={handlePasswordSubmit}
        onCancel={handleClosePasswordModal}
        width={400}
        okText="确定"
        cancelText="取消"
      >
        <Form form={passwordForm} layout="vertical">
          <Form.Item
            name="old_password"
            label="旧密码"
            rules={[{ required: true, message: '请输入旧密码' }]}
          >
            <Input.Password placeholder="请输入旧密码" />
          </Form.Item>

          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码至少6个字符' },
            ]}
          >
            <Input.Password placeholder="请输入新密码" />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            label="确认密码"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password placeholder="请再次输入新密码" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManagement;
