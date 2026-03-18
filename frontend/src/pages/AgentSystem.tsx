/**
 * Agent 编排系统页面
 * 展示 Agent 列表、依赖关系、执行统计等信息
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Table,
  Statistic,
  Tag,
  Tabs,
  Select,
  DatePicker,
  Space,
  Typography,
  Descriptions,
  Timeline,
  message,
} from 'antd';
import {
  RobotOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  NodeIndexOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getAgentList,
  getAgentStatistics,
  getExecutionFlow,
  type AgentInfo,
  type AgentStatistics as AgentStatsType,
  type ExecutionFlow,
} from '../api/agent';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

const AgentSystem: React.FC = () => {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [statistics, setStatistics] = useState<AgentStatsType | null>(null);
  const [executionFlow, setExecutionFlow] = useState<ExecutionFlow | null>(null);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  const [flowLoading, setFlowLoading] = useState(false);
  const [selectedTaskType, setSelectedTaskType] = useState('publish');
  const [statsDays, setStatsDays] = useState(7);

  // 加载 Agent 列表
  const loadAgents = async () => {
    setLoading(true);
    try {
      const response = await getAgentList();
      if (response.code === 0) {
        setAgents(response.data);
      } else {
        message.error(response.message || '加载 Agent 列表失败');
      }
    } catch (error) {
      message.error('加载 Agent 列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载统计数据
  const loadStatistics = async (days: number) => {
    setStatsLoading(true);
    try {
      const response = await getAgentStatistics(days);
      if (response.code === 0) {
        setStatistics(response.data);
      } else {
        message.error(response.message || '加载统计数据失败');
      }
    } catch (error) {
      message.error('加载统计数据失败');
    } finally {
      setStatsLoading(false);
    }
  };

  // 加载执行流程
  const loadExecutionFlow = async (taskType: string) => {
    setFlowLoading(true);
    try {
      const response = await getExecutionFlow(taskType);
      if (response.code === 0) {
        setExecutionFlow(response.data);
      } else {
        message.error(response.message || '加载执行流程失败');
      }
    } catch (error) {
      message.error('加载执行流程失败');
    } finally {
      setFlowLoading(false);
    }
  };

  useEffect(() => {
    loadAgents();
    loadStatistics(7);
    loadExecutionFlow('publish');
  }, []);

  // Agent 列表表格列定义
  const agentColumns: ColumnsType<AgentInfo> = [
    {
      title: 'Agent 名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => (
        <Space>
          <RobotOutlined style={{ color: '#1890ff' }} />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '依赖',
      dataIndex: 'dependencies',
      key: 'dependencies',
      render: (deps: string[]) => (
        <>
          {deps.length === 0 ? (
            <Tag color="green">无依赖</Tag>
          ) : (
            deps.map((dep) => (
              <Tag key={dep} color="blue">
                {dep}
              </Tag>
            ))
          )}
        </>
      ),
    },
  ];

  // 统计数据表格列定义
  const statsColumns: ColumnsType<AgentStatsType['agents'][0]> = [
    {
      title: 'Agent',
      dataIndex: 'agent_name',
      key: 'agent_name',
      render: (name: string) => <Text strong>{name}</Text>,
    },
    {
      title: '总执行次数',
      dataIndex: 'total_executions',
      key: 'total_executions',
      sorter: (a, b) => a.total_executions - b.total_executions,
    },
    {
      title: '成功次数',
      dataIndex: 'success_count',
      key: 'success_count',
      render: (count: number) => (
        <Text type="success">
          <CheckCircleOutlined /> {count}
        </Text>
      ),
    },
    {
      title: '失败次数',
      dataIndex: 'error_count',
      key: 'error_count',
      render: (count: number) => (
        <Text type="danger">
          <CloseCircleOutlined /> {count}
        </Text>
      ),
    },
    {
      title: '成功率',
      dataIndex: 'success_rate',
      key: 'success_rate',
      sorter: (a, b) => a.success_rate - b.success_rate,
      render: (rate: number) => {
        let color = 'green';
        if (rate < 80) color = 'orange';
        if (rate < 60) color = 'red';
        return <Tag color={color}>{rate.toFixed(2)}%</Tag>;
      },
    },
  ];

  // 任务类型选项
  const taskTypeOptions = [
    { label: '选品分析', value: 'product_analysis' },
    { label: '内容生成', value: 'content_generation' },
    { label: '图片生成', value: 'image_generation' },
    { label: '视频生成', value: 'video_generation' },
    { label: '内容审核', value: 'review' },
    { label: '完整发布', value: 'publish' },
  ];

  const tabItems = [
    {
      key: 'list',
      label: 'Agent 列表',
      children: (
        <Card>
          <Table
            columns={agentColumns}
            dataSource={agents}
            rowKey="name"
            loading={loading}
            pagination={false}
          />
        </Card>
      ),
    },
    {
      key: 'statistics',
      label: '执行统计',
      children: (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Card>
              <Space>
                <Text>统计周期：</Text>
                <Select
                  value={statsDays}
                  onChange={(value) => {
                    setStatsDays(value);
                    loadStatistics(value);
                  }}
                  style={{ width: 120 }}
                >
                  <Option value={7}>最近 7 天</Option>
                  <Option value={14}>最近 14 天</Option>
                  <Option value={30}>最近 30 天</Option>
                </Select>
              </Space>
            </Card>

            {statistics && (
              <>
                <Row gutter={16}>
                  <Col span={8}>
                    <Card>
                      <Statistic
                        title="统计周期"
                        value={`${statistics.start_date} ~ ${statistics.end_date}`}
                        prefix={<ClockCircleOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={8}>
                    <Card>
                      <Statistic
                        title="活跃 Agent"
                        value={statistics.agents.length}
                        prefix={<RobotOutlined />}
                        suffix="个"
                      />
                    </Card>
                  </Col>
                  <Col span={8}>
                    <Card>
                      <Statistic
                        title="总执行次数"
                        value={statistics.agents.reduce(
                          (sum, a) => sum + a.total_executions,
                          0
                        )}
                        prefix={<CheckCircleOutlined />}
                      />
                    </Card>
                  </Col>
                </Row>

                <Card title="Agent 执行详情">
                  <Table
                    columns={statsColumns}
                    dataSource={statistics.agents}
                    rowKey="agent_name"
                    loading={statsLoading}
                    pagination={false}
                  />
                </Card>
              </>
            )}
          </Space>
      ),
    },
    {
      key: 'flow',
      label: '执行流程',
      children: (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Card>
              <Space>
                <Text>任务类型：</Text>
                <Select
                  value={selectedTaskType}
                  onChange={(value) => {
                    setSelectedTaskType(value);
                    loadExecutionFlow(value);
                  }}
                  style={{ width: 200 }}
                >
                  {taskTypeOptions.map((option) => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </Space>
            </Card>

            {executionFlow && (
              <Card
                title={`${
                  taskTypeOptions.find((t) => t.value === executionFlow.task_type)
                    ?.label
                } - 执行流程`}
                loading={flowLoading}
              >
                <Descriptions bordered column={1}>
                  <Descriptions.Item label="任务类型">
                    {executionFlow.task_type}
                  </Descriptions.Item>
                  <Descriptions.Item label="总步骤数">
                    {executionFlow.total_steps} 个 Agent
                  </Descriptions.Item>
                </Descriptions>

                <div style={{ marginTop: 24 }}>
                  <Title level={5}>执行顺序：</Title>
                  <Timeline>
                    {executionFlow.flow.map((step) => (
                      <Timeline.Item
                        key={step.step}
                        color="blue"
                        dot={<RobotOutlined />}
                      >
                        <Card size="small" style={{ marginBottom: 8 }}>
                          <Space direction="vertical" size="small">
                            <Text strong>
                              步骤 {step.step}: {step.agent_name}
                            </Text>
                            <Text type="secondary">{step.description}</Text>
                            {step.dependencies.length > 0 && (
                              <div>
                                <Text type="secondary">依赖：</Text>
                                {step.dependencies.map((dep) => (
                                  <Tag key={dep} color="blue">
                                    {dep}
                                  </Tag>
                                ))}
                              </div>
                            )}
                          </Space>
                        </Card>
                      </Timeline.Item>
                    ))}
                  </Timeline>
                </div>
              </Card>
            )}
          </Space>
      ),
    },
    {
      key: 'info',
      label: '系统说明',
      children: (
          <Card title="Agent 编排系统介绍">
            <Paragraph>
              Agent 编排系统是电商自动化管理系统的核心，实现了 7 个专业 Agent
              的协同工作，完成从选品到上架的全流程自动化。
            </Paragraph>

            <Title level={4}>7 个专业 Agent</Title>
            <Timeline>
              <Timeline.Item color="blue">
                <Text strong>ProductAnalysisAgent - 选品分析</Text>
                <br />
                <Text type="secondary">
                  分析产品市场潜力、竞争情况、利润率等
                </Text>
              </Timeline.Item>
              <Timeline.Item color="blue">
                <Text strong>PriceOptimizationAgent - 价格优化</Text>
                <br />
                <Text type="secondary">根据市场情况优化产品定价</Text>
              </Timeline.Item>
              <Timeline.Item color="blue">
                <Text strong>ContentGenerationAgent - 内容生成</Text>
                <br />
                <Text type="secondary">
                  生成产品标题、描述、关键词等营销内容
                </Text>
              </Timeline.Item>
              <Timeline.Item color="blue">
                <Text strong>ImageGenerationAgent - 图片生成</Text>
                <br />
                <Text type="secondary">生成产品主图、详情图</Text>
              </Timeline.Item>
              <Timeline.Item color="blue">
                <Text strong>VideoGenerationAgent - 视频生成</Text>
                <br />
                <Text type="secondary">生成产品宣传视频（可选）</Text>
              </Timeline.Item>
              <Timeline.Item color="blue">
                <Text strong>ContentReviewAgent - 内容审核</Text>
                <br />
                <Text type="secondary">审核生成的内容是否符合平台规范</Text>
              </Timeline.Item>
              <Timeline.Item color="green">
                <Text strong>PublishAgent - 发布上架</Text>
                <br />
                <Text type="secondary">将产品发布到电商平台</Text>
              </Timeline.Item>
            </Timeline>

            <Title level={4} style={{ marginTop: 24 }}>
              核心特性
            </Title>
            <ul>
              <li>自动依赖管理和拓扑排序</li>
              <li>Agent 之间数据共享机制</li>
              <li>执行历史记录</li>
              <li>验证机制和错误处理</li>
              <li>详细的日志记录</li>
            </ul>
          </Card>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <NodeIndexOutlined /> Agent 编排系统
      </Title>
      <Paragraph type="secondary">
        查看和管理 7 个专业 Agent 的信息、依赖关系和执行统计
      </Paragraph>

      <Tabs defaultActiveKey="list" items={tabItems} />
    </div>
  );
};

export default AgentSystem;
