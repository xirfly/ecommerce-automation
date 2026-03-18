# 页面布局设计

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 整体布局

### 1.1 经典后台布局

采用**顶部导航 + 侧边菜单 + 内容区**的经典布局：

```
┌─────────────────────────────────────────────────────────┐
│  Logo  |  电商自动化系统  |  🔔 通知  👤 用户  ⚙️      │ 顶部导航 (64px)
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│  📊 仪表盘│                                              │
│  📦 产品  │              内容区域                        │
│  ⚡ 任务  │                                              │
│  📈 数据  │                                              │
│  🔌 渠道  │                                              │
│  ⚙️ 系统  │                                              │
│          │                                              │
│  侧边栏  │                                              │
│  (240px) │                                              │
└──────────┴──────────────────────────────────────────────┘
```

### 1.2 布局尺寸

```css
/* 顶部导航栏 */
--header-height: 64px;
--header-padding: 0 24px;
--header-z-index: 1000;

/* 侧边栏 */
--sidebar-width: 240px;
--sidebar-collapsed-width: 64px;
--sidebar-z-index: 900;

/* 内容区 */
--content-max-width: 1440px;
--content-padding: 24px;
--content-min-height: calc(100vh - 64px);
```

---

## 2. 顶部导航栏

### 2.1 结构

```
┌─────────────────────────────────────────────────────────┐
│ [Logo] 电商自动化系统    [搜索框]    🔔 👤 ⚙️ 🌙       │
└─────────────────────────────────────────────────────────┘
```

### 2.2 左侧区域

**Logo + 系统名称：**
- Logo尺寸：32x32px
- 系统名称：16px，字重600
- 间距：Logo与名称间距12px

**折叠按钮（可选）：**
- 图标按钮，40x40px
- 点击折叠/展开侧边栏

### 2.3 中间区域

**全局搜索框：**
- 宽度：400px
- 高度：36px
- 占位符："搜索产品、任务..."
- 快捷键：Ctrl/Cmd + K

### 2.4 右侧区域

**通知图标：**
- 图标按钮，40x40px
- 红点提示未读数量
- 点击展开通知下拉菜单

**用户菜单：**
- 头像 + 用户名
- 点击展开下拉菜单：
  - 个人设置
  - 修改密码
  - 退出登录

**设置图标：**
- 图标按钮，40x40px
- 快速访问系统设置

**主题切换：**
- 图标按钮，40x40px
- 切换亮色/暗色主题

---

## 3. 侧边栏

### 3.1 菜单结构

```
📊 仪表盘
📦 产品管理
   ├─ 产品列表
   └─ 新建产品
⚡ 任务中心
   ├─ 任务列表
   └─ 任务日志
📈 数据分析
   ├─ 销售报表
   └─ Agent性能
🔌 渠道配置 (仅管理员)
   ├─ 渠道列表
   └─ 添加渠道
⚙️ 系统设置 (仅管理员)
   ├─ 用户管理
   ├─ 权限管理
   └─ 系统配置
```

### 3.2 菜单项样式

**正常状态：**
```css
padding: 12px 16px;
font-size: 14px;
color: var(--text-secondary);
border-radius: 4px;
```

**悬停状态：**
```css
background: var(--background-grey);
color: var(--text-primary);
```

**激活状态：**
```css
background: var(--primary);
color: #ffffff;
font-weight: 600;
```

### 3.3 折叠状态

**展开状态（240px）：**
- 显示图标 + 文字
- 显示子菜单

**折叠状态（64px）：**
- 仅显示图标
- 悬停时显示Tooltip
- 子菜单改为弹出菜单

---

## 4. 内容区布局

### 4.1 页面容器

```css
.page-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px;
  min-height: calc(100vh - 64px);
}
```

### 4.2 页面头部

**结构：**
```
┌─────────────────────────────────────────────────────────┐
│ 页面标题                    [筛选] [搜索] [新建按钮]     │
│ 面包屑导航                                              │
└─────────────────────────────────────────────────────────┘
```

**样式：**
```css
.page-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--divider);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.breadcrumb {
  font-size: 14px;
  color: var(--text-tertiary);
}
```

### 4.3 内容区域

**卡片布局（仪表盘）：**
```css
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}
```

**列表布局（产品管理、任务中心）：**
```css
.list-container {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: var(--shadow-base);
  padding: 0;
}
```

**表格布局：**
```css
.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}
```

---

## 5. 响应式布局

### 5.1 桌面端（≥1024px）

**完整布局：**
- 侧边栏展开（240px）
- 内容区最大宽度1440px
- 表格显示所有列

### 5.2 平板端（768px - 1023px）

**调整：**
- 侧边栏可折叠
- 内容区自适应宽度
- 表格隐藏次要列

**示例：**
```css
@media (max-width: 1023px) {
  .sidebar {
    width: 64px; /* 默认折叠 */
  }

  .sidebar.expanded {
    width: 240px;
    position: fixed;
    z-index: 1000;
    box-shadow: var(--shadow-xl);
  }

  .table-column-secondary {
    display: none; /* 隐藏次要列 */
  }
}
```

### 5.3 移动端（<768px）

**不推荐使用Web后台，建议使用飞书/Telegram**

**如果必须支持：**
- 侧边栏改为抽屉式（从左滑出）
- 顶部导航简化（仅Logo + 菜单按钮 + 用户）
- 表格改为卡片列表
- 多列布局改为单列

---

## 6. 栅格系统

### 6.1 12列栅格

```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
}

/* 占据不同列数 */
.col-1 { grid-column: span 1; }
.col-2 { grid-column: span 2; }
.col-3 { grid-column: span 3; }
.col-4 { grid-column: span 4; }
.col-6 { grid-column: span 6; }
.col-12 { grid-column: span 12; }
```

### 6.2 响应式栅格

```css
/* 桌面端：4列 */
@media (min-width: 1024px) {
  .col-lg-3 { grid-column: span 3; }
  .col-lg-4 { grid-column: span 4; }
  .col-lg-6 { grid-column: span 6; }
}

/* 平板端：2列 */
@media (min-width: 768px) and (max-width: 1023px) {
  .col-md-6 { grid-column: span 6; }
  .col-md-12 { grid-column: span 12; }
}

/* 移动端：1列 */
@media (max-width: 767px) {
  .col-sm-12 { grid-column: span 12; }
}
```

---

## 7. 特殊布局

### 7.1 仪表盘布局

**KPI卡片行：**
```css
.kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}
```

**图表区域：**
```css
.chart-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

@media (max-width: 1023px) {
  .chart-section {
    grid-template-columns: 1fr;
  }
}
```

### 7.2 详情页布局

**左右分栏：**
```css
.detail-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

/* 左侧：主要内容 */
.detail-main {
  /* 产品信息、任务详情等 */
}

/* 右侧：辅助信息 */
.detail-sidebar {
  /* 操作按钮、状态信息、历史记录等 */
}

@media (max-width: 1023px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
```

### 7.3 表单布局

**单列表单：**
```css
.form-single-column {
  max-width: 600px;
  margin: 0 auto;
}

.form-item {
  margin-bottom: 24px;
}
```

**双列表单：**
```css
.form-double-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 767px) {
  .form-double-column {
    grid-template-columns: 1fr;
  }
}
```

---

## 8. 滚动与固定

### 8.1 固定顶部导航

```css
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.content-wrapper {
  margin-top: 64px; /* header高度 */
}
```

### 8.2 固定侧边栏

```css
.sidebar {
  position: fixed;
  top: 64px; /* header高度 */
  left: 0;
  bottom: 0;
  width: 240px;
  overflow-y: auto;
  z-index: 900;
}

.main-content {
  margin-left: 240px; /* sidebar宽度 */
}
```

### 8.3 表格固定表头

```css
.table-container {
  max-height: 600px;
  overflow-y: auto;
}

thead th {
  position: sticky;
  top: 0;
  background: #fafafa;
  z-index: 10;
}
```

### 8.4 表格固定列

```css
.table-fixed-column {
  position: sticky;
  right: 0;
  background: #ffffff;
  box-shadow: -2px 0 4px rgba(0, 0, 0, 0.05);
}
```

---

## 9. 空状态与加载

### 9.1 空状态布局

```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 48px 24px;
  text-align: center;
}

.empty-icon {
  width: 120px;
  height: 120px;
  margin-bottom: 24px;
  opacity: 0.5;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}
```

### 9.2 加载状态布局

**骨架屏：**
```css
.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

**加载遮罩：**
```css
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
```

---

## 10. Z-Index管理

```css
/* Z-Index层级规范 */
--z-index-dropdown: 1000;
--z-index-sticky: 1020;
--z-index-fixed: 1030;
--z-index-modal-backdrop: 1040;
--z-index-modal: 1050;
--z-index-popover: 1060;
--z-index-tooltip: 1070;
```

**使用规则：**
- 1000-1019：下拉菜单、弹出框
- 1020-1029：固定元素（表头、侧边栏）
- 1030-1039：固定导航栏
- 1040-1049：模态框背景
- 1050-1059：模态框
- 1060-1069：Popover
- 1070+：Tooltip

---

## 11. 打印样式

```css
@media print {
  /* 隐藏导航和侧边栏 */
  .header,
  .sidebar,
  .page-actions {
    display: none !important;
  }

  /* 内容区全宽 */
  .main-content {
    margin-left: 0;
    max-width: 100%;
  }

  /* 移除阴影和背景 */
  .card {
    box-shadow: none;
    border: 1px solid #e0e0e0;
  }

  /* 强制分页 */
  .page-break {
    page-break-after: always;
  }
}
```

---

## 12. 相关文档

- [设计原则与规范](01-design-principles.md) - 颜色、字体、间距规范
- [核心页面设计](03-core-pages.md) - 6个核心页面详细设计
- [交互设计细节](04-interaction-design.md) - 交互流程和状态管理
