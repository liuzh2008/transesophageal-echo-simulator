# **UI组件接口文档**

## **ResponsiveLayout组件接口**

**接口路径**: `src/ui/components/ResponsiveLayout.tsx`

**功能说明**: 响应式布局容器组件，提供自适应屏幕尺寸的布局容器

**请求参数**:
- `children`: React.ReactNode - 子组件内容

**响应格式**: React组件，返回包含子组件的div元素

**逻辑**:
1. 提供全宽全高的布局容器
2. 支持响应式设计，适配不同屏幕尺寸
3. 提供data-testid属性用于测试

**响应示例**:
```typescript
<ResponsiveLayout>
  <div>内容区域</div>
</ResponsiveLayout>
```

**相关文件**: `src/ui/components/ResponsiveLayout.tsx`

---

## **Button组件接口**

**接口路径**: `src/ui/components/Button.tsx`

**功能说明**: 按钮组件，提供基础的按钮交互功能，支持多种变体

**请求参数**:
- `children`: React.ReactNode - 按钮文本或内容
- `onClick`: () => void - 点击事件处理函数（可选）
- `disabled`: boolean - 是否禁用按钮（默认false）
- `variant`: 'primary' | 'secondary' | 'danger' - 按钮变体（默认'primary'）

**响应格式**: React组件，返回button元素

**逻辑**:
1. 根据variant参数应用不同的样式类
2. 支持禁用状态和点击事件
3. 提供data-testid属性用于测试
4. 支持所有标准按钮属性

**响应示例**:
```typescript
<Button onClick={() => console.log('点击')} variant="primary">
  主要按钮
</Button>

<Button disabled variant="secondary">
  禁用按钮
</Button>

<Button variant="danger">
  危险操作
</Button>
```

**相关文件**: `src/ui/components/Button.tsx`

---

## **Slider组件接口**

**接口路径**: `src/ui/components/Slider.tsx`

**功能说明**: 滑块组件，提供数值范围选择功能

**请求参数**:
- `value`: number - 当前值
- `min`: number - 最小值（默认0）
- `max`: number - 最大值（默认100）
- `step`: number - 步长（默认1）
- `onChange`: (value: number) => void - 值变化回调函数（可选）

**响应格式**: React组件，返回包含input和span元素的div

**逻辑**:
1. 使用HTML5 range input实现滑块功能
2. 显示当前数值
3. 支持自定义范围、步长和初始值
4. 提供data-testid属性用于测试

**响应示例**:
```typescript
<Slider 
  value={50} 
  min={0} 
  max={100} 
  step={1}
  onChange={(value) => console.log('当前值:', value)}
/>
```

**相关文件**: `src/ui/components/Slider.tsx`

---

## **Panel组件接口**

**接口路径**: `src/ui/components/Panel.tsx`

**功能说明**: 面板组件，提供内容容器和布局功能

**请求参数**:
- `children`: React.ReactNode - 面板内容
- `title`: string - 面板标题（可选）
- `className`: string - 自定义CSS类名（可选）

**响应格式**: React组件，返回包含标题和内容的面板元素

**逻辑**:
1. 支持带标题的面板和无标题面板
2. 提供标准的面板样式和阴影效果
3. 支持自定义类名扩展样式
4. 提供data-testid属性用于测试

**响应示例**:
```typescript
<Panel title="控制面板">
  <Button>操作按钮</Button>
  <Slider value={50} />
</Panel>

<Panel className="custom-panel">
  无标题面板内容
</Panel>
```

**相关文件**: `src/ui/components/Panel.tsx`

---

## **ThemeProvider组件接口**

**接口路径**: `src/ui/components/ThemeProvider.tsx`

**功能说明**: 主题配置组件，提供主题管理和切换功能

**请求参数**:
- `children`: React.ReactNode - 子组件
- `initialTheme`: Theme - 初始主题配置（可选）

**响应格式**: React Context Provider组件

**逻辑**:
1. 提供默认主题配置
2. 支持动态主题切换
3. 通过React Context提供主题数据
4. 提供useTheme钩子访问主题

**响应示例**:
```typescript
<ThemeProvider>
  <App />
</ThemeProvider>

// 在组件中使用主题
const { theme, setTheme } = useTheme();
```

**相关文件**: `src/ui/components/ThemeProvider.tsx`

---

## **useTheme钩子接口**

**接口路径**: `src/ui/components/ThemeProvider.tsx`

**功能说明**: 主题使用钩子，提供对主题状态的访问和修改

**请求参数**: 无

**响应格式**: ThemeContextType对象

**逻辑**:
1. 必须在ThemeProvider内部使用
2. 提供当前主题和设置主题的方法
3. 类型安全的主题配置访问

**响应示例**:
```typescript
const { theme, setTheme } = useTheme();

// 获取主题颜色
const primaryColor = theme.primaryColor;

// 更新主题
setTheme({
  ...theme,
  primaryColor: '#ff0000'
});
```

**相关文件**: `src/ui/components/ThemeProvider.tsx`

---

## **App组件接口**

**接口路径**: `src/ui/App.tsx`

**功能说明**: 主应用组件，集成所有UI组件和功能

**请求参数**: 无

**响应格式**: React组件，返回完整的应用界面

**逻辑**:
1. 使用ThemeProvider提供主题支持
2. 使用ResponsiveLayout提供响应式布局
3. 集成3D场景和控件面板
4. 提供场景重置和缩放控制功能

**响应示例**:
```typescript
// 完整的应用界面，包含：
// - 响应式布局
// - 3D场景面板
// - 控制面板
// - 按钮和滑块控件
```

**相关文件**: `src/ui/App.tsx`

---

## **测试接口**

**接口路径**: `tests/ui/layout.test.ts`, `tests/ui/components.test.ts`

**功能说明**: UI组件功能的测试用例

**测试覆盖**:
1. 响应式布局组件存在性验证
2. 基础控件组件功能验证
3. 组件交互和状态管理
4. 主题配置功能

**测试方法**:
- 使用Jest测试框架
- 验证组件存在性和功能正确性
- 测试组件间的集成使用

**相关文件**: `tests/ui/layout.test.ts`, `tests/ui/components.test.ts`
