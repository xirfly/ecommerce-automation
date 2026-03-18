# UI/UX设计原则与规范

**文档版本：** v1.0
**最后更新：** 2026-03-16
**基于：** ui-ux-pro-max skill 设计指南

---

## 1. 设计目标

为电商自动化系统设计一个：
- **专业高效** - 适合运营人员日常使用的后台系统
- **信息密集** - 在有限空间内展示最多有用信息
- **清晰易用** - 降低学习成本，提高操作效率
- **响应式** - 适配桌面端和平板端

---

## 2. 设计风格定位

### 2.1 风格选择

**主风格：Executive Dashboard + Data-Dense Dashboard 混合**

**理由：**
- Executive Dashboard：适合仪表盘页面，展示核心KPI
- Data-Dense Dashboard：适合产品管理、任务中心等数据密集页面

**风格特点：**
- 大号KPI卡片（仪表盘）
- 紧凑的数据表格（列表页）
- 清晰的视觉层级
- 最小化装饰，最大化信息

### 2.2 设计关键词

```
专业 | 高效 | 数据驱动 | 简洁 | 现代
```

---

## 3. 颜色系统

### 3.1 主色调（基于ui-ux-pro-max推荐）

**品牌色：**
```css
--primary: #1890ff;        /* 蓝色 - 科技感、信任感 */
--primary-hover: #40a9ff;  /* 悬停态 */
--primary-active: #096dd9; /* 激活态 */
```

**功能色：**
```css
--success: #22C55E;  /* 成功 - 绿色 */
--warning: #F59E0B;  /* 警告 - 橙色 */
--error: #EF4444;    /* 错误 - 红色 */
--info: #1890ff;     /* 信息 - 蓝色 */
```

**中性色：**
```css
--text-primary: #262626;    /* 主要文字 */
--text-secondary: #595959;  /* 次要文字 */
--text-tertiary: #8c8c8c;   /* 辅助文字 */
--text-disabled: #bfbfbf;   /* 禁用文字 */

--border: #d9d9d9;          /* 边框 */
--divider: #f0f0f0;         /* 分割线 */
--background: #ffffff;      /* 背景 */
--background-grey: #fafafa; /* 灰色背景 */
--background-dark: #f5f5f5; /* 深灰背景 */
```

**状态色（任务/产品状态）：**
```css
--status-draft: #8c8c8c;      /* 草稿 - 灰色 */
--status-analyzing: #1890ff;  /* 分析中 - 蓝色 */
--status-generating: #722ED1; /* 生成中 - 紫色 */
--status-success: #22C55E;    /* 成功 - 绿色 */
--status-failed: #EF4444;     /* 失败 - 红色 */
--status-published: #52c41a;  /* 已发布 - 绿色 */
```

### 3.2 颜色使用规范

**对比度要求（WCAG AA）：**
- 正常文字：至少 4.5:1
- 大号文字（18px+）：至少 3:1
- 交互元素：至少 3:1

**颜色语义：**
- 蓝色：主要操作、链接、信息提示
- 绿色：成功状态、正向数据（增长、利润）
- 红色：错误状态、负向数据（下降、亏损）
- 橙色：警告状态、需要注意的信息
- 灰色：禁用状态、次要信息

---

## 4. 字体系统

### 4.1 字体家族

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
             'Helvetica Neue', Arial, 'Noto Sans', sans-serif,
             'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
```

**理由：**
- 系统字体优先，加载速度快
- 跨平台兼容性好
- 中文显示友好

### 4.2 字号规范

```css
--font-size-xs: 12px;    /* 辅助文字、标签 */
--font-size-sm: 14px;    /* 正文、表格内容 */
--font-size-base: 16px;  /* 基础字号 */
--font-size-lg: 18px;    /* 小标题 */
--font-size-xl: 20px;    /* 中标题 */
--font-size-2xl: 24px;   /* 大标题 */
--font-size-3xl: 30px;   /* 超大标题 */
--font-size-4xl: 36px;   /* KPI数值 */
--font-size-5xl: 48px;   /* 超大KPI数值 */
```

**使用场景：**
- 12px：表格辅助信息、时间戳、标签
- 14px：表格内容、表单标签、正文
- 16px：页面正文、按钮文字
- 20px：卡片标题、模块标题
- 24px：页面标题
- 36-48px：仪表盘KPI数值

### 4.3 行高规范

```css
--line-height-tight: 1.25;   /* 标题 */
--line-height-normal: 1.5;   /* 正文 */
--line-height-relaxed: 1.75; /* 长文本 */
```

**使用规则：**
- 标题：1.25（紧凑）
- 正文：1.5（舒适）
- 长文本：1.75（易读）

### 4.4 字重规范

```css
--font-weight-normal: 400;   /* 正文 */
--font-weight-medium: 500;   /* 强调 */
--font-weight-semibold: 600; /* 小标题 */
--font-weight-bold: 700;     /* 大标题、KPI */
```

---

## 5. 间距系统

### 5.1 基础单位

**基础单位：** 8px（0.5rem）

**间距规范：**
```css
--spacing-0: 0px;
--spacing-1: 4px;    /* 0.25rem - 极小间距 */
--spacing-2: 8px;    /* 0.5rem - 小间距 */
--spacing-3: 12px;   /* 0.75rem - 中小间距 */
--spacing-4: 16px;   /* 1rem - 中间距 */
--spacing-5: 20px;   /* 1.25rem - 中大间距 */
--spacing-6: 24px;   /* 1.5rem - 大间距 */
--spacing-8: 32px;   /* 2rem - 超大间距 */
--spacing-10: 40px;  /* 2.5rem - 巨大间距 */
--spacing-12: 48px;  /* 3rem - 页面边距 */
```

### 5.2 使用场景

| 间距 | 使用场景 |
|------|----------|
| 4px | 图标与文字间距、标签内边距 |
| 8px | 表单项间距、按钮内边距 |
| 12px | 卡片内边距（紧凑） |
| 16px | 卡片内边距（标准）、列表项间距 |
| 24px | 模块间距、卡片间距 |
| 32px | 页面内容区边距 |
| 48px | 页面顶部/底部边距 |

---

## 6. 圆角与阴影

### 6.1 圆角规范

```css
--radius-sm: 2px;    /* 小圆角 - 标签、徽章 */
--radius-base: 4px;  /* 基础圆角 - 按钮、输入框 */
--radius-md: 6px;    /* 中圆角 - 卡片 */
--radius-lg: 8px;    /* 大圆角 - 模态框 */
--radius-xl: 12px;   /* 超大圆角 - 特殊卡片 */
--radius-full: 9999px; /* 圆形 - 头像、徽章 */
```

### 6.2 阴影规范

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1),
               0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
             0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
             0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
             0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

**使用场景：**
- sm：表格行悬停
- base：按钮、输入框
- md：卡片
- lg：下拉菜单、弹出框
- xl：模态框

---

## 7. 组件规范

### 7.1 按钮

**尺寸：**
```css
/* 小按钮 */
height: 24px;
padding: 0 8px;
font-size: 12px;

/* 中按钮（默认） */
height: 32px;
padding: 0 16px;
font-size: 14px;

/* 大按钮 */
height: 40px;
padding: 0 20px;
font-size: 16px;
```

**类型：**
- Primary：主要操作（蓝色背景）
- Default：次要操作（白色背景，灰色边框）
- Danger：危险操作（红色背景）
- Text：文字按钮（无背景）
- Link：链接按钮（蓝色文字）

**状态：**
- Normal：正常状态
- Hover：悬停态（背景色加深10%）
- Active：激活态（背景色加深20%）
- Disabled：禁用态（灰色，不可点击）
- Loading：加载态（显示加载图标，禁用点击）

### 7.2 输入框

**尺寸：**
```css
/* 小输入框 */
height: 24px;
padding: 0 8px;
font-size: 12px;

/* 中输入框（默认） */
height: 32px;
padding: 0 12px;
font-size: 14px;

/* 大输入框 */
height: 40px;
padding: 0 16px;
font-size: 16px;
```

**状态：**
- Normal：灰色边框
- Focus：蓝色边框 + 蓝色阴影
- Error：红色边框 + 红色阴影
- Disabled：灰色背景，不可编辑

### 7.3 表格

**行高：**
```css
--table-row-height-sm: 36px;   /* 紧凑 */
--table-row-height-base: 48px; /* 标准 */
--table-row-height-lg: 56px;   /* 宽松 */
```

**样式：**
- 表头：灰色背景（#fafafa），字重600
- 斑马纹：奇数行白色，偶数行浅灰（#fafafa）
- 悬停：浅蓝背景（#e6f7ff）
- 边框：浅灰色（#f0f0f0）

**固定列：**
- 操作列固定在右侧
- 使用 `position: sticky` 实现

### 7.4 卡片

**内边距：**
```css
--card-padding-sm: 12px;   /* 紧凑卡片 */
--card-padding-base: 16px; /* 标准卡片 */
--card-padding-lg: 24px;   /* 宽松卡片 */
```

**样式：**
- 背景：白色
- 边框：1px 浅灰色
- 圆角：6px
- 阴影：shadow-base

**KPI卡片（仪表盘）：**
```css
min-width: 280px;
padding: 24px;
border-radius: 8px;
box-shadow: var(--shadow-md);
```

---

## 8. 布局规范

### 8.1 栅格系统

**12列栅格：**
```css
display: grid;
grid-template-columns: repeat(12, 1fr);
gap: 24px;
```

**响应式断点：**
```css
--breakpoint-sm: 640px;   /* 平板竖屏 */
--breakpoint-md: 768px;   /* 平板横屏 */
--breakpoint-lg: 1024px;  /* 小屏笔记本 */
--breakpoint-xl: 1280px;  /* 桌面 */
--breakpoint-2xl: 1536px; /* 大屏 */
```

### 8.2 页面布局

**整体布局：**
```
┌─────────────────────────────────────────┐
│  顶部导航栏 (64px)                       │
├──────────┬──────────────────────────────┤
│          │                              │
│  侧边栏  │        内容区域              │
│  (240px) │                              │
│          │                              │
└──────────┴──────────────────────────────┘
```

**尺寸规范：**
```css
--header-height: 64px;
--sidebar-width: 240px;
--sidebar-collapsed-width: 64px;
--content-max-width: 1440px;
--content-padding: 24px;
```

---

## 9. 交互规范

### 9.1 动画时长

```css
--duration-fast: 150ms;    /* 快速交互 */
--duration-base: 200ms;    /* 标准交互 */
--duration-slow: 300ms;    /* 慢速交互 */
--duration-slower: 500ms;  /* 页面切换 */
```

**使用场景：**
- 150ms：按钮悬停、输入框聚焦
- 200ms：下拉菜单展开、模态框淡入
- 300ms：抽屉滑出、折叠面板展开
- 500ms：页面切换、路由动画

### 9.2 缓动函数

```css
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

**使用规则：**
- ease-in：元素消失
- ease-out：元素出现
- ease-in-out：元素移动

### 9.3 触摸目标尺寸

**最小尺寸：** 44x44px（WCAG AAA标准）

**推荐尺寸：**
- 按钮：至少 32x32px
- 图标按钮：至少 40x40px
- 复选框/单选框：至少 20x20px（点击区域44x44px）

---

## 10. 无障碍规范

### 10.1 颜色对比度

**WCAG AA标准：**
- 正常文字（<18px）：至少 4.5:1
- 大号文字（≥18px）：至少 3:1
- 交互元素：至少 3:1

**检查工具：**
- Chrome DevTools - Lighthouse
- WebAIM Contrast Checker

### 10.2 键盘导航

**Tab顺序：**
- 按视觉顺序从左到右、从上到下
- 跳过隐藏元素
- 模态框打开时，焦点锁定在模态框内

**焦点样式：**
```css
:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

### 10.3 ARIA标签

**必需场景：**
- 图标按钮：`aria-label="操作名称"`
- 表单输入：`<label for="input-id">`
- 图片：`alt="描述性文字"`
- 加载状态：`aria-busy="true"`
- 错误提示：`aria-invalid="true"`

---

## 11. 响应式设计

### 11.1 断点策略

| 断点 | 屏幕宽度 | 布局调整 |
|------|----------|----------|
| sm | 640px+ | 平板竖屏，侧边栏可折叠 |
| md | 768px+ | 平板横屏，表格显示更多列 |
| lg | 1024px+ | 小屏笔记本，完整布局 |
| xl | 1280px+ | 桌面，最佳体验 |
| 2xl | 1536px+ | 大屏，内容居中限宽 |

### 11.2 移动端适配

**< 768px：**
- 侧边栏改为抽屉式
- 表格改为卡片列表
- 多列布局改为单列
- 隐藏次要信息

**建议：**
- 移动端使用飞书/Telegram等即时通讯工具
- Web后台主要服务桌面端和平板端

---

## 12. 性能优化

### 12.1 图片优化

```html
<!-- 使用WebP格式 -->
<img src="image.webp" alt="描述" loading="lazy" />

<!-- 响应式图片 -->
<img
  srcset="image-320w.webp 320w,
          image-640w.webp 640w,
          image-1280w.webp 1280w"
  sizes="(max-width: 640px) 100vw, 640px"
  src="image-640w.webp"
  alt="描述"
/>
```

### 12.2 动画性能

**使用 transform 和 opacity：**
```css
/* 好的做法 */
.element {
  transform: translateX(100px);
  opacity: 0.5;
}

/* 避免使用 */
.element {
  left: 100px;  /* 触发重排 */
  width: 200px; /* 触发重排 */
}
```

### 12.3 减少重绘

**使用 will-change：**
```css
.animated-element {
  will-change: transform, opacity;
}
```

**注意：** 不要滥用 will-change，只在需要时使用

---

## 13. 设计系统变量汇总

```css
:root {
  /* 颜色 */
  --primary: #1890ff;
  --success: #22C55E;
  --warning: #F59E0B;
  --error: #EF4444;

  /* 字体 */
  --font-size-base: 14px;
  --line-height-normal: 1.5;
  --font-weight-normal: 400;

  /* 间距 */
  --spacing-base: 16px;

  /* 圆角 */
  --radius-base: 4px;

  /* 阴影 */
  --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1);

  /* 动画 */
  --duration-base: 200ms;
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

  /* 布局 */
  --header-height: 64px;
  --sidebar-width: 240px;
  --content-padding: 24px;
}
```

---

## 14. 相关文档

- [页面布局设计](02-page-layouts.md) - 具体页面布局
- [核心页面设计](03-core-pages.md) - 6个核心页面详细设计
- [交互设计细节](04-interaction-design.md) - 交互流程和状态管理
