# 渠道配置模块

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 目标

提供可视化的渠道配置管理，支持：
- 动态添加/删除渠道
- 渠道配置编辑
- 路由规则配置
- 渠道状态监控

---

## 2. 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 渠道列表 | 查看所有渠道 | P0 |
| 添加渠道 | 配置新渠道 | P0 |
| 编辑渠道 | 修改渠道配置 | P0 |
| 删除渠道 | 删除渠道 | P0 |
| 测试连接 | 验证渠道配置 | P1 |
| 启用/禁用 | 控制渠道状态 | P1 |

---

## 3. API设计

### 3.1 添加渠道

```http
POST /api/v1/channels
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "name": "飞书客服Bot",
  "type": "feishu",
  "config": {
    "app_id": "cli_xxx",
    "app_secret": "xxx",
    "verification_token": "xxx"
  },
  "routing_rules": {
    "default_agent": "product-analyzer",
    "whitelist_users": ["ou_xxx"]
  }
}

Response (201 Created):
{
  "code": 0,
  "message": "渠道添加成功",
  "data": {
    "id": 1,
    "name": "飞书客服Bot",
    "type": "feishu",
    "is_enabled": true,
    "created_at": "2026-03-16T10:00:00Z"
  }
}
```

### 3.2 测试连接

```http
POST /api/v1/channels/{id}/test
Authorization: Bearer {token}

Response (200 OK):
{
  "code": 0,
  "message": "连接测试成功",
  "data": {
    "status": "success",
    "latency_ms": 150,
    "message": "连接正常"
  }
}
```

---

## 4. 前端实现

### 4.1 添加渠道表单

```tsx
const ChannelForm: React.FC = () => {
  const [form] = Form.useForm();
  const [channelType, setChannelType] = useState('');

  const channelConfigs = {
    feishu: [
      { name: 'app_id', label: 'App ID', required: true },
      { name: 'app_secret', label: 'App Secret', required: true },
      { name: 'verification_token', label: 'Verification Token', required: true }
    ],
    telegram: [
      { name: 'bot_token', label: 'Bot Token', required: true }
    ]
  };

  return (
    <Form form={form} onFinish={handleSubmit}>
      <Form.Item name="name" label="渠道名称" rules={[{ required: true }]}>
        <Input />
      </Form.Item>

      <Form.Item name="type" label="渠道类型" rules={[{ required: true }]}>
        <Select onChange={setChannelType}>
          <Select.Option value="feishu">飞书</Select.Option>
          <Select.Option value="telegram">Telegram</Select.Option>
          <Select.Option value="wechat">企业微信</Select.Option>
        </Select>
      </Form.Item>

      {/* 动态渲染配置项 */}
      {channelType && channelConfigs[channelType]?.map(field => (
        <Form.Item
          key={field.name}
          name={['config', field.name]}
          label={field.label}
          rules={[{ required: field.required }]}
        >
          <Input.Password />
        </Form.Item>
      ))}

      <Form.Item>
        <Button type="primary" htmlType="submit">保存</Button>
        <Button onClick={handleTest}>测试连接</Button>
      </Form.Item>
    </Form>
  );
};
```

---

## 5. 相关文档

- [多渠道接入设计](../architecture/03-multi-channel.md) - 渠道架构
- [数据模型设计](../database/01-data-model.md) - channels表
