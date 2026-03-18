# 前端开发指南

## 📦 安装依赖

```bash
cd frontend
npm install
```

## 🚀 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:3000

## 📁 项目结构

```
frontend/
├── src/
│   ├── api/                 # API 接口层
│   │   ├── auth.ts         # 认证接口
│   │   └── product.ts      # 产品接口
│   ├── layouts/            # 布局组件
│   │   └── MainLayout.tsx  # 主布局（侧边栏+顶栏）
│   ├── pages/              # 页面组件
│   │   ├── Login.tsx       # 登录页
│   │   ├── Dashboard.tsx   # 仪表盘
│   │   ├── ProductList.tsx # 产品列表（完整CRUD）
│   │   ├── ProductDetail.tsx # 产品详情
│   │   ├── TaskCenter.tsx  # 任务中心
│   │   ├── DataAnalytics.tsx # 数据分析
│   │   ├── ChannelConfig.tsx # 渠道配置
│   │   └── SystemSettings.tsx # 系统设置
│   ├── router/             # 路由配置
│   │   └── index.tsx       # 路由定义（懒加载）
│   ├── styles/             # 样式文件
│   │   └── global.css      # 全局样式（CSS变量）
│   ├── utils/              # 工具函数
│   │   └── request.ts      # Axios封装
│   └── main.tsx            # 应用入口
├── index.html              # HTML模板
├── package.json            # 依赖配置
├── tsconfig.json           # TypeScript配置
├── vite.config.ts          # Vite构建配置
└── .env.example            # 环境变量模板
```

## 🎨 已实现功能

### 1. 登录页面
- JWT 认证
- 表单验证
- 错误提示
- 默认账号：admin / admin123

### 2. 主布局
- 侧边栏导航（可折叠）
- 顶部导航栏
- 用户下拉菜单
- 响应式设计

### 3. 仪表盘
- 4 个 KPI 卡片（新增产品、执行任务、成功率、平均耗时）
- 任务执行趋势图（ECharts 折线图）
- Agent 状态饼图
- 最近任务表格

### 4. 产品管理
- 产品列表（分页、搜索、筛选）
- 新建产品（表单验证）
- 编辑产品
- 删除产品（确认弹窗）
- 批量删除
- 状态标签（草稿/分析中/生成中/已发布）

### 5. 其他页面
- 任务中心（占位）
- 数据分析（占位）
- 渠道配置（占位）
- 系统设置（占位）

## 🔧 核心功能

### Axios 请求封装
- 自动添加 JWT Token
- 统一错误处理
- 401 自动跳转登录
- 429 速率限制提示

### 路由懒加载
- 代码分割
- 按需加载
- 减少首屏加载时间

### 主题配置
- Ant Design 主题定制
- CSS 变量（颜色系统）
- 响应式断点

## 🎯 待开发功能

### 产品详情页
- 产品信息展示
- 图片/视频预览
- 任务执行历史
- 编辑功能

### 任务中心
- 任务列表
- 实时状态更新（WebSocket）
- 任务详情
- 重试/取消操作

### 数据分析
- 销售数据图表
- 趋势分析
- AI 生成报告

### 渠道配置
- 渠道列表
- 添加/编辑渠道
- 测试连接
- 启用/禁用

### 系统设置
- 用户管理
- 角色权限
- 系统参数

## 📝 开发规范

### 组件命名
- 使用 PascalCase
- 文件名与组件名一致
- 例：`ProductList.tsx` → `const ProductList: React.FC = () => {}`

### API 调用
```typescript
import { productApi } from '@/api/product'

// 获取列表
const response = await productApi.getList({ page: 1, page_size: 10 })

// 创建产品
await productApi.create({ name: '产品名', category: '数码', price: 199 })
```

### 路由跳转
```typescript
import { useNavigate } from 'react-router-dom'

const navigate = useNavigate()
navigate('/products')
```

### 状态管理
- 使用 React Hooks（useState, useEffect）
- 复杂状态考虑 Context API
- 全局状态可使用 Zustand（待引入）

## 🐛 常见问题

### 1. 端口被占用
```bash
# 修改端口
vite --port 3001
```

### 2. API 请求失败
- 检查后端是否启动（http://localhost:8000）
- 检查 `.env.local` 中的 API 地址
- 查看浏览器控制台错误信息

### 3. 依赖安装失败
```bash
# 清除缓存
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## 📚 相关文档

- [UI/UX 设计规范](../docs/design/ui-ux/01-design-principles.md)
- [核心页面设计](../docs/design/ui-ux/03-core-pages.md)
- [交互设计细节](../docs/design/ui-ux/04-interaction-design.md)
- [产品管理模块](../docs/design/features/01-product-management.md)

## 🚀 构建部署

### 开发环境
```bash
npm run dev
```

### 生产构建
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

### 构建分析
构建后查看 `dist/stats.html` 查看打包分析报告

## 📊 性能优化

- ✅ 代码分割（React/Ant Design/ECharts 独立 chunk）
- ✅ Gzip + Brotli 压缩
- ✅ 路由懒加载
- ✅ 图片懒加载
- ✅ 生产环境移除 console

## 🎉 下一步

1. 安装依赖：`npm install`
2. 启动开发：`npm run dev`
3. 访问系统：http://localhost:3000
4. 使用默认账号登录：admin / admin123
5. 开始开发其他页面功能
