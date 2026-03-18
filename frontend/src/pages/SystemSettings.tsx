/**
 * 系统设置页面
 * 管理系统配置信息
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  Tabs,
  Form,
  Input,
  InputNumber,
  Switch,
  Button,
  message,
  Space,
  Typography,
  Divider,
  Alert,
} from 'antd';
import {
  SettingOutlined,
  SaveOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import {
  getAllSettings,
  batchUpdateConfigs,
  type SystemSettings,
} from '../api/settings';

const { Title, Text } = Typography;
const { TextArea } = Input;

const SystemSettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm();

  // 加载设置
  const loadSettings = async () => {
    setLoading(true);
    try {
      const response = await getAllSettings();
      if (response.code === 0) {
        setSettings(response.data);
        // 设置表单初始值
        const formValues: Record<string, any> = {};
        Object.entries(response.data).forEach(([category, configs]) => {
          Object.entries(configs as Record<string, any>).forEach(([key, config]) => {
            formValues[key] = config.value;
          });
        });
        form.setFieldsValue(formValues);
      } else {
        message.error(response.message || '加载设置失败');
      }
    } catch (error) {
      message.error('加载设置失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 保存设置
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);

      // 构建批量更新数据
      const configs: Array<{
        config_key: string;
        config_value: any;
      }> = [];

      Object.entries(values).forEach(([key, value]) => {
        configs.push({
          config_key: key,
          config_value: value,
        });
      });

      const response = await batchUpdateConfigs({ configs });
      if (response.code === 0) {
        message.success('保存成功');
        loadSettings();
      } else {
        message.error(response.message || '保存失败');
      }
    } catch (error) {
      console.error('表单验证失败', error);
    } finally {
      setSaving(false);
    }
  };

  // 重置设置
  const handleReset = () => {
    if (settings) {
      const formValues: Record<string, any> = {};
      Object.entries(settings).forEach(([category, configs]) => {
        Object.entries(configs as Record<string, any>).forEach(([key, config]) => {
          formValues[key] = config.value;
        });
      });
      form.setFieldsValue(formValues);
      message.info('已重置为当前保存的值');
    }
  };

  const tabItems = [
    {
      key: 'basic',
      label: '基本设置',
      children: (
        <Card loading={loading}>
          <Form form={form} layout="vertical">
            <Form.Item
              name="system_name"
              label="系统名称"
              rules={[{ required: true, message: '请输入系统名称' }]}
            >
              <Input placeholder="电商自动化管理系统" />
            </Form.Item>

            <Form.Item name="system_description" label="系统描述">
              <TextArea rows={3} placeholder="系统描述信息" />
            </Form.Item>

            <Form.Item name="timezone" label="时区设置">
              <Input placeholder="Asia/Shanghai" />
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'ai',
      label: 'AI 服务配置',
      children: (
        <Card loading={loading}>
          <Alert
            message="敏感信息提示"
            description="API Key 等敏感信息将被加密存储，请妥善保管"
            type="warning"
            showIcon
            style={{ marginBottom: 24 }}
          />
          <Form form={form} layout="vertical">
            <Divider orientation="left">OpenAI 配置</Divider>
            <Form.Item name="openai_api_key" label="OpenAI API Key">
              <Input.Password placeholder="sk-..." />
            </Form.Item>

            <Form.Item name="openai_model" label="OpenAI 模型">
              <Input placeholder="gpt-4" />
            </Form.Item>

            <Divider orientation="left">Midjourney 配置</Divider>
            <Form.Item name="midjourney_api_key" label="Midjourney API Key">
              <Input.Password placeholder="输入 API Key" />
            </Form.Item>

            <Divider orientation="left">Runway 配置</Divider>
            <Form.Item name="runway_api_key" label="Runway API Key">
              <Input.Password placeholder="输入 API Key" />
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'task',
      label: '任务配置',
      children: (
        <Card loading={loading}>
          <Form form={form} layout="vertical">
            <Form.Item
              name="task_timeout"
              label="任务超时时间（秒）"
              rules={[{ required: true, message: '请输入任务超时时间' }]}
            >
              <InputNumber min={60} max={86400} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="task_max_retries"
              label="最大重试次数"
              rules={[{ required: true, message: '请输入最大重试次数' }]}
            >
              <InputNumber min={0} max={10} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="task_concurrent_limit"
              label="并发任务数限制"
              rules={[{ required: true, message: '请输入并发任务数限制' }]}
            >
              <InputNumber min={1} max={20} style={{ width: '100%' }} />
            </Form.Item>

            <Alert
              message="配置说明"
              description={
                <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                  <li>任务超时时间：单个任务执行的最长时间</li>
                  <li>最大重试次数：任务失败后的重试次数</li>
                  <li>并发任务数：同时执行的最大任务数量</li>
                </ul>
              }
              type="info"
              showIcon
            />
          </Form>
        </Card>
      ),
    },
    {
      key: 'notification',
      label: '通知配置',
      children: (
        <Card loading={loading}>
          <Form form={form} layout="vertical">
            <Form.Item
              name="notification_enabled"
              label="启用通知"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="notification_on_success"
              label="任务成功时通知"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="notification_on_error"
              label="任务失败时通知"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Alert
              message="通知渠道配置"
              description="请在「渠道配置」页面中配置具体的通知渠道（飞书、Telegram、企业微信等）"
              type="info"
              showIcon
            />
          </Form>
        </Card>
      ),
    },
    {
      key: 'security',
      label: '安全设置',
      children: (
        <Card loading={loading}>
          <Form form={form} layout="vertical">
            <Form.Item
              name="session_timeout"
              label="会话超时时间（秒）"
              rules={[{ required: true, message: '请输入会话超时时间' }]}
            >
              <InputNumber min={300} max={604800} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="password_min_length"
              label="密码最小长度"
              rules={[{ required: true, message: '请输入密码最小长度' }]}
            >
              <InputNumber min={6} max={32} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="api_rate_limit"
              label="API 速率限制（次/分钟）"
              rules={[{ required: true, message: '请输入 API 速率限制' }]}
            >
              <InputNumber min={10} max={1000} style={{ width: '100%' }} />
            </Form.Item>

            <Alert
              message="安全提示"
              description={
                <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                  <li>会话超时时间：用户登录后的有效时间</li>
                  <li>密码最小长度：用户密码的最小字符数</li>
                  <li>API 速率限制：防止 API 滥用的请求频率限制</li>
                </ul>
              }
              type="warning"
              showIcon
            />
          </Form>
        </Card>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <SettingOutlined /> 系统设置
      </Title>
      <Text type="secondary">配置系统运行参数和服务集成</Text>

      <Card style={{ marginTop: 24 }}>
        <Space style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={saving}
          >
            保存设置
          </Button>
          <Button icon={<ReloadOutlined />} onClick={handleReset}>
            重置
          </Button>
        </Space>

        <Tabs items={tabItems} />
      </Card>
    </div>
  );
};

export default SystemSettingsPage;
