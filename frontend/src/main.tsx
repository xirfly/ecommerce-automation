import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { ConfigProvider, App } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { router } from './router'
import './styles/global.css'

dayjs.locale('zh-cn')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <ConfigProvider
    locale={zhCN}
    theme={{
      token: {
        colorPrimary: '#1890ff',
        colorSuccess: '#22C55E',
        colorWarning: '#F59E0B',
        colorError: '#EF4444',
        colorInfo: '#1890ff',
        borderRadius: 6,
        fontSize: 14,
      },
    }}
  >
    <App>
      <RouterProvider router={router} />
    </App>
  </ConfigProvider>,
)
