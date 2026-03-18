# 交互设计细节

**文档版本：** v1.0
**最后更新：** 2026-03-16

---

## 1. 加载状态

### 1.1 骨架屏

**使用场景：** 页面首次加载、列表加载

```tsx
const ProductListSkeleton: React.FC = () => (
  <div className="skeleton-container">
    {[1, 2, 3, 4, 5].map(i => (
      <div key={i} className="skeleton-row">
        <div className="skeleton-avatar" />
        <div className="skeleton-content">
          <div className="skeleton-title" />
          <div className="skeleton-text" />
        </div>
      </div>
    ))}
  </div>
);
```

### 1.2 加载动画

**使用场景：** 按钮点击、表单提交

```tsx
<Button loading={isLoading} onClick={handleSubmit}>
  提交
</Button>
```

### 1.3 进度条

**使用场景：** 任务执行进度

```tsx
<Progress
  percent={taskProgress}
  status={taskStatus === 'success' ? 'success' : 'active'}
  format={percent => `${percent}% 完成`}
/>
```

---

## 2. 错误处理

### 2.1 表单验证错误

```tsx
<Form.Item
  name="name"
  rules={[
    { required: true, message: '请输入产品名称' },
    { min: 2, message: '产品名称至少2个字符' }
  ]}
>
  <Input placeholder="请输入产品名称" />
</Form.Item>
```

### 2.2 API错误提示

```tsx
try {
  await createProduct(data);
  message.success('创建成功');
} catch (error) {
  if (error.response?.status === 400) {
    message.error(error.response.data.message);
  } else if (error.response?.status === 403) {
    message.error('权限不足');
  } else {
    message.error('操作失败，请稍后重试');
  }
}
```

### 2.3 网络错误

```tsx
// 全局错误拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    if (!error.response) {
      message.error('网络连接失败，请检查网络');
    } else if (error.response.status === 401) {
      message.error('登录已过期，请重新登录');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);
```

---

## 3. 确认操作

### 3.1 删除确认

```tsx
const handleDelete = (id: number) => {
  Modal.confirm({
    title: '确认删除',
    content: '删除后无法恢复，确定要删除这个产品吗？',
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      await deleteProduct(id);
      message.success('删除成功');
      loadProducts();
    }
  });
};
```

### 3.2 批量操作确认

```tsx
const handleBatchDelete = () => {
  Modal.confirm({
    title: `确认删除 ${selectedIds.length} 个产品？`,
    content: '批量删除后无法恢复',
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      await batchDelete(selectedIds);
      message.success(`成功删除 ${selectedIds.length} 个产品`);
      setSelectedIds([]);
      loadProducts();
    }
  });
};
```

---

## 4. 实时更新

### 4.1 WebSocket连接

```tsx
useEffect(() => {
  const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'task_update') {
      // 更新任务状态
      setTasks(prev => prev.map(task =>
        task.id === message.data.id ? { ...task, ...message.data } : task
      ));

      // 显示通知
      notification.info({
        message: '任务状态更新',
        description: `${message.data.name} 已${message.data.status}`
      });
    }
  };

  return () => ws.close();
}, [userId]);
```

### 4.2 轮询更新

```tsx
useEffect(() => {
  const interval = setInterval(() => {
    loadTasks();
  }, 5000); // 每5秒刷新一次

  return () => clearInterval(interval);
}, []);
```

---

## 5. 搜索与筛选

### 5.1 防抖搜索

```tsx
const [searchKeyword, setSearchKeyword] = useState('');
const debouncedSearch = useMemo(
  () => debounce((value: string) => {
    setFilters(prev => ({ ...prev, keyword: value }));
  }, 500),
  []
);

<Input
  placeholder="搜索产品名称"
  onChange={(e) => {
    setSearchKeyword(e.target.value);
    debouncedSearch(e.target.value);
  }}
  value={searchKeyword}
/>
```

### 5.2 筛选器

```tsx
<Space>
  <Select
    placeholder="状态"
    onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
    allowClear
  >
    <Select.Option value="draft">草稿</Select.Option>
    <Select.Option value="published">已发布</Select.Option>
  </Select>

  <Select
    placeholder="分类"
    onChange={(value) => setFilters(prev => ({ ...prev, category: value }))}
    allowClear
  >
    <Select.Option value="数码">数码</Select.Option>
    <Select.Option value="服饰">服饰</Select.Option>
  </Select>
</Space>
```

---

## 6. 分页

### 6.1 表格分页

```tsx
<Table
  dataSource={products}
  columns={columns}
  pagination={{
    current: page,
    pageSize: pageSize,
    total: total,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total) => `共 ${total} 条`,
    onChange: (page, pageSize) => {
      setPage(page);
      setPageSize(pageSize);
    }
  }}
/>
```

---

## 7. 拖拽排序

### 7.1 列表拖拽

```tsx
import { DndContext, closestCenter } from '@dnd-kit/core';
import { SortableContext, useSortable } from '@dnd-kit/sortable';

const SortableItem: React.FC<{ id: string }> = ({ id, children }) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });

  return (
    <div
      ref={setNodeRef}
      style={{ transform, transition }}
      {...attributes}
      {...listeners}
    >
      {children}
    </div>
  );
};

const handleDragEnd = (event) => {
  const { active, over } = event;
  if (active.id !== over.id) {
    // 更新排序
    reorderItems(active.id, over.id);
  }
};
```

---

## 8. 快捷键

### 8.1 全局快捷键

```tsx
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    // Ctrl/Cmd + K: 打开搜索
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      openSearch();
    }

    // Ctrl/Cmd + N: 新建产品
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
      e.preventDefault();
      openCreateModal();
    }

    // ESC: 关闭弹窗
    if (e.key === 'Escape') {
      closeModal();
    }
  };

  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, []);
```

---

## 9. 响应式交互

### 9.1 移动端适配

```tsx
const isMobile = useMediaQuery({ maxWidth: 768 });

return (
  <div>
    {isMobile ? (
      <MobileView />
    ) : (
      <DesktopView />
    )}
  </div>
);
```

---

## 10. 动画效果

### 10.1 页面切换动画

```tsx
import { CSSTransition } from 'react-transition-group';

<CSSTransition
  in={show}
  timeout={300}
  classNames="fade"
  unmountOnExit
>
  <div className="modal-content">
    {children}
  </div>
</CSSTransition>
```

```css
.fade-enter {
  opacity: 0;
}
.fade-enter-active {
  opacity: 1;
  transition: opacity 300ms;
}
.fade-exit {
  opacity: 1;
}
.fade-exit-active {
  opacity: 0;
  transition: opacity 300ms;
}
```

---

## 11. 相关文档

- [设计原则与规范](01-design-principles.md) - 动画时长规范
- [核心页面设计](03-core-pages.md) - 页面结构
