import { lazy, Suspense } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { Spin } from 'antd'
import MainLayout from '@/layouts/MainLayout'

// 懒加载组件
const Dashboard = lazy(() => import('@/pages/Dashboard'))
const ProductList = lazy(() => import('@/pages/ProductList'))
const ProductDetail = lazy(() => import('@/pages/ProductDetail'))
const TaskCenter = lazy(() => import('@/pages/TaskCenter'))
const TaskDetail = lazy(() => import('@/pages/TaskDetail'))
const DataAnalytics = lazy(() => import('@/pages/DataAnalytics'))
const ChannelConfig = lazy(() => import('@/pages/ChannelConfig'))
const AgentSystem = lazy(() => import('@/pages/AgentSystem'))
const SystemSettings = lazy(() => import('@/pages/SystemSettings'))
const UserManagement = lazy(() => import('@/pages/UserManagement'))
const FeedbackSubmit = lazy(() => import('@/pages/FeedbackSubmit'))
const FeedbackManagement = lazy(() => import('@/pages/FeedbackManagement'))
const SalesDataManagement = lazy(() => import('@/pages/SalesDataManagement'))
const Login = lazy(() => import('@/pages/Login'))

// 加载中组件
const LoadingFallback = () => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh'
  }}>
    <Spin size="large" />
  </div>
)

// 路由配置
export const router = createBrowserRouter(
  [
    {
      path: '/login',
      element: (
        <Suspense fallback={<LoadingFallback />}>
          <Login />
        </Suspense>
      ),
    },
    {
      path: '/',
      element: <MainLayout />,
      children: [
        {
          index: true,
          element: <Navigate to="/dashboard" replace />,
        },
        {
          path: 'dashboard',
          element: (
            <Suspense fallback={<Spin />}>
              <Dashboard />
            </Suspense>
          ),
        },
        {
          path: 'products',
          element: (
            <Suspense fallback={<Spin />}>
              <ProductList />
            </Suspense>
          ),
        },
        {
          path: 'products/:id',
          element: (
            <Suspense fallback={<Spin />}>
              <ProductDetail />
            </Suspense>
          ),
        },
        {
          path: 'tasks',
          element: (
            <Suspense fallback={<Spin />}>
              <TaskCenter />
            </Suspense>
          ),
        },
        {
          path: 'tasks/:id',
          element: (
            <Suspense fallback={<Spin />}>
              <TaskDetail />
            </Suspense>
          ),
        },
        {
          path: 'analytics',
          element: (
            <Suspense fallback={<Spin />}>
              <DataAnalytics />
            </Suspense>
          ),
        },
        {
          path: 'channels',
          element: (
            <Suspense fallback={<Spin />}>
              <ChannelConfig />
            </Suspense>
          ),
        },
        {
          path: 'agents',
          element: (
            <Suspense fallback={<Spin />}>
              <AgentSystem />
            </Suspense>
          ),
        },
        {
          path: 'settings',
          element: (
            <Suspense fallback={<Spin />}>
              <SystemSettings />
            </Suspense>
          ),
        },
        {
          path: 'users',
          element: (
            <Suspense fallback={<Spin />}>
              <UserManagement />
            </Suspense>
          ),
        },
        {
          path: 'feedback/submit',
          element: (
            <Suspense fallback={<Spin />}>
              <FeedbackSubmit />
            </Suspense>
          ),
        },
        {
          path: 'feedback/management',
          element: (
            <Suspense fallback={<Spin />}>
              <FeedbackManagement />
            </Suspense>
          ),
        },
        {
          path: 'sales',
          element: (
            <Suspense fallback={<Spin />}>
              <SalesDataManagement />
            </Suspense>
          ),
        },
      ],
    },
  ],
  {
    future: {
      v7_startTransition: true,
    },
  }
)
