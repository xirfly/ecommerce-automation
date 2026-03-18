import React, { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Avatar, Dropdown, Space, Badge } from 'antd'
import {
  DashboardOutlined,
  ShoppingOutlined,
  UnorderedListOutlined,
  BarChartOutlined,
  LineChartOutlined,
  ApiOutlined,
  NodeIndexOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  WifiOutlined,
  TeamOutlined,
  BugOutlined,
} from '@ant-design/icons'
import type { MenuProps } from 'antd'
import { useWebSocket } from '@/hooks/useWebSocket'

const { Header, Sider, Content } = Layout

const MainLayout: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)

  // 启用 WebSocket 连接
  const { isConnected } = useWebSocket({
    onTaskUpdate: (task) => {
      console.log('任务更新:', task)
      // 可以在这里触发全局状态更新
    },
    onNotification: (notification) => {
      console.log('收到通知:', notification)
    },
    onConnected: () => {
      console.log('WebSocket 已连接')
    },
    onDisconnected: () => {
      console.log('WebSocket 已断开')
    },
  })

  const menuItems: MenuProps['items'] = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/products',
      icon: <ShoppingOutlined />,
      label: '产品管理',
    },
    {
      key: '/tasks',
      icon: <UnorderedListOutlined />,
      label: '任务中心',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: '数据分析',
    },
    {
      key: '/sales',
      icon: <LineChartOutlined />,
      label: '销售数据',
    },
    {
      key: '/agents',
      icon: <NodeIndexOutlined />,
      label: 'Agent 系统',
    },
    {
      key: '/channels',
      icon: <ApiOutlined />,
      label: '渠道配置',
    },
    {
      key: '/users',
      icon: <TeamOutlined />,
      label: '用户管理',
    },
    {
      key: '/feedback',
      icon: <BugOutlined />,
      label: 'Bug 反馈',
      children: [
        {
          key: '/feedback/submit',
          label: '提交反馈',
        },
        {
          key: '/feedback/management',
          label: '反馈管理',
        },
      ],
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ]

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  const handleUserMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      localStorage.removeItem('access_token')
      navigate('/login')
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: 18,
            fontWeight: 'bold',
          }}
        >
          {collapsed ? 'EC' : 'ecommerce-auto'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 80 : 200, transition: 'margin-left 0.2s' }}>
        <Header
          style={{
            padding: '0 24px',
            background: '#fff',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            position: 'fixed',
            top: 0,
            right: 0,
            left: collapsed ? 80 : 200,
            zIndex: 1,
            transition: 'left 0.2s',
          }}
        >
          <div style={{ fontSize: 18, fontWeight: 500 }}>
            电商自动化管理系统
            <Badge
              status={isConnected ? 'success' : 'error'}
              text={isConnected ? '已连接' : '未连接'}
              style={{ marginLeft: 16, fontSize: 12 }}
            />
          </div>
          <Dropdown menu={{ items: userMenuItems, onClick: handleUserMenuClick }}>
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <span>管理员</span>
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ margin: '88px 16px 24px', padding: 24, background: '#fff', minHeight: 'calc(100vh - 112px)' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout
