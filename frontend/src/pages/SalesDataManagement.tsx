/**
 * 销售数据管理页面
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  DatePicker,
  InputNumber,
  Select,
  message,
  Row,
  Col,
  Statistic,
  Typography,
} from 'antd';
import {
  LineChartOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getSalesDataList,
  createSalesData,
  updateSalesData,
  deleteSalesData,
  getSalesAnalytics,
  type SalesData,
  type SalesAnalyticsResponse,
} from '@/api/sales';
import { productApi, type Product } from '@/api/product';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

const SalesDataManagement: React.FC = () => {
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [analytics, setAnalytics] = useState<SalesAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [productFilter, setProductFilter] = useState<number | undefined>();
  const [dateRange, setDateRange] = useState<[string, string] | undefined>();
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [updateModalVisible, setUpdateModalVisible] = useState(false);
  const [selectedSales, setSelectedSales] = useState<SalesData | null>(null);
  const [createForm] = Form.useForm();
  const [updateForm] = Form.useForm();
  const [analyticsDays, setAnalyticsDays] = useState(30);

  useEffect(() => {
    loadSalesData();
    loadProducts();
    loadAnalytics();
  }, [page, pageSize, productFilter, dateRange]);

  const loadSalesData = async () => {
    setLoading(true);
    try {
      const response = await getSalesDataList({
        page,
        page_size: pageSize,
        product_id: productFilter,
        start_date: dateRange?.[0],
        end_date: dateRange?.[1],
      });
      if (response.code === 0) {
        setSalesData(response.data.items);
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

  const loadProducts = async () => {
    try {
      const response = await productApi.getList({ page: 1, page_size: 100 });
      if (response.code === 0) {
        setProducts(response.data.items);
      }
    } catch (error) {
      // 忽略产品加载错误
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await getSalesAnalytics(analyticsDays, productFilter);
      if (response.code === 0) {
        setAnalytics(response.data);
      }
    } catch (error) {
      // 忽略分析数据加载错误
    }
  };

  const handleCreate = async (values: any) => {
    try {
      const response = await createSalesData({
        product_id: values.product_id,
        date: values.date.format('YYYY-MM-DD'),
        views: values.views || 0,
        clicks: values.clicks || 0,
        orders: values.orders || 0,
        sales_amount: values.sales_amount || 0,
      });
      if (response.code === 0) {
        message.success('创建成功');
        setCreateModalVisible(false);
        createForm.resetFields();
        loadSalesData();
        loadAnalytics();
      } else {
        message.error(response.message || '创建失败');
      }
    } catch (error) {
      message.error('创建失败');
    }
  };

  const handleUpdate = async (values: any) => {
    if (!selectedSales) return;

    try {
      const response = await updateSalesData(selectedSales.id, values);
      if (response.code === 0) {
        message.success('更新成功');
        setUpdateModalVisible(false);
        loadSalesData();
        loadAnalytics();
      } else {
        message.error(response.message || '更新失败');
      }
    } catch (error) {
      message.error('更新失败');
    }
  };

  const handleDelete = (record: SalesData) => {
    Modal.confirm({
      title: '确认删除',
      icon: <ExclamationCircleOutlined />,
      content: `确定要删除 ${record.product_name} 在 ${record.date} 的销售数据吗？`,
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await deleteSalesData(record.id);
          if (response.code === 0) {
            message.success('删除成功');
            loadSalesData();
            loadAnalytics();
          } else {
            message.error(response.message || '删除失败');
          }
        } catch (error) {
          message.error('删除失败');
        }
      },
    });
  };

  const columns: ColumnsType<SalesData> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
    },
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      width: 120,
    },
    {
      title: '浏览量',
      dataIndex: 'views',
      key: 'views',
      width: 100,
      render: (val: number) => val.toLocaleString(),
    },
    {
      title: '点击量',
      dataIndex: 'clicks',
      key: 'clicks',
      width: 100,
      render: (val: number) => val.toLocaleString(),
    },
    {
      title: '订单量',
      dataIndex: 'orders',
      key: 'orders',
      width: 100,
      render: (val: number) => val.toLocaleString(),
    },
    {
      title: '销售额',
      dataIndex: 'sales_amount',
      key: 'sales_amount',
      width: 120,
      render: (val: number) => `¥${val.toFixed(2)}`,
    },
    {
      title: '转化率',
      key: 'conversion_rate',
      width: 100,
      render: (_, record) => {
        const rate = record.clicks > 0 ? (record.orders / record.clicks * 100) : 0;
        return `${rate.toFixed(2)}%`;
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setSelectedSales(record);
              updateForm.setFieldsValue({
                views: record.views,
                clicks: record.clicks,
                orders: record.orders,
                sales_amount: record.sales_amount,
              });
              setUpdateModalVisible(true);
            }}
          >
            编辑
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
        <LineChartOutlined /> 销售数据管理
      </Title>

      {/* 统计卡片 */}
      {analytics && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总浏览量"
                value={analytics.statistics.total_views}
                precision={0}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="总点击量"
                value={analytics.statistics.total_clicks}
                precision={0}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="总订单量"
                value={analytics.statistics.total_orders}
                precision={0}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="总销售额"
                value={analytics.statistics.total_sales_amount}
                precision={2}
                prefix="¥"
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 销售趋势数据表格 */}
      {analytics && analytics.statistics.trend_data.length > 0 && (
        <Card title="销售趋势" style={{ marginBottom: 24 }}>
          <Table
            dataSource={analytics.statistics.trend_data}
            rowKey="date"
            pagination={false}
            scroll={{ y: 300 }}
            size="small"
            columns={[
              {
                title: '日期',
                dataIndex: 'date',
                key: 'date',
              },
              {
                title: '浏览量',
                dataIndex: 'views',
                key: 'views',
                render: (val: number) => val.toLocaleString(),
              },
              {
                title: '点击量',
                dataIndex: 'clicks',
                key: 'clicks',
                render: (val: number) => val.toLocaleString(),
              },
              {
                title: '订单量',
                dataIndex: 'orders',
                key: 'orders',
                render: (val: number) => val.toLocaleString(),
              },
              {
                title: '销售额',
                dataIndex: 'sales_amount',
                key: 'sales_amount',
                render: (val: number) => `¥${val.toFixed(2)}`,
              },
            ]}
          />
        </Card>
      )}

      {/* 筛选和操作 */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Text>产品：</Text>
          <Select
            style={{ width: 200 }}
            placeholder="全部产品"
            allowClear
            value={productFilter}
            onChange={setProductFilter}
          >
            {products.map((p) => (
              <Option key={p.id} value={p.id}>
                {p.name}
              </Option>
            ))}
          </Select>

          <Text>日期范围：</Text>
          <RangePicker
            value={dateRange ? [dayjs(dateRange[0]), dayjs(dateRange[1])] : undefined}
            onChange={(dates) => {
              if (dates) {
                setDateRange([dates[0]!.format('YYYY-MM-DD'), dates[1]!.format('YYYY-MM-DD')]);
              } else {
                setDateRange(undefined);
              }
            }}
          />

          <Text>统计周期：</Text>
          <Select
            style={{ width: 120 }}
            value={analyticsDays}
            onChange={(val) => {
              setAnalyticsDays(val);
              loadAnalytics();
            }}
          >
            <Option value={7}>最近7天</Option>
            <Option value={30}>最近30天</Option>
            <Option value={90}>最近90天</Option>
          </Select>

          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalVisible(true)}>
            添加数据
          </Button>
          <Button onClick={loadSalesData}>刷新</Button>
        </Space>
      </Card>

      {/* 数据表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={salesData}
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

      {/* 创建弹窗 */}
      <Modal
        title="添加销售数据"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        onOk={() => createForm.submit()}
        okText="创建"
        cancelText="取消"
      >
        <Form form={createForm} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            label="产品"
            name="product_id"
            rules={[{ required: true, message: '请选择产品' }]}
          >
            <Select placeholder="选择产品">
              {products.map((p) => (
                <Option key={p.id} value={p.id}>
                  {p.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="日期"
            name="date"
            rules={[{ required: true, message: '请选择日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="浏览量" name="views" initialValue={0}>
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="点击量" name="clicks" initialValue={0}>
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="订单量" name="orders" initialValue={0}>
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="销售额" name="sales_amount" initialValue={0}>
            <InputNumber min={0} precision={2} style={{ width: '100%' }} prefix="¥" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 更新弹窗 */}
      <Modal
        title="编辑销售数据"
        open={updateModalVisible}
        onCancel={() => setUpdateModalVisible(false)}
        onOk={() => updateForm.submit()}
        okText="保存"
        cancelText="取消"
      >
        <Form form={updateForm} layout="vertical" onFinish={handleUpdate}>
          <Form.Item label="浏览量" name="views">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="点击量" name="clicks">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="订单量" name="orders">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="销售额" name="sales_amount">
            <InputNumber min={0} precision={2} style={{ width: '100%' }} prefix="¥" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SalesDataManagement;
