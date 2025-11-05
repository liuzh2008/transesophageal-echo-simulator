# 系统架构模式

## 整体架构
```
食道超声模拟软件
├── 前端应用层 (React + TypeScript)
│   ├── UI组件层 - 用户界面和交互
│   ├── 3D渲染层 - Three.js场景管理
│   └── 状态管理层 - 应用状态和数据流
├── 核心算法层 (TypeScript)
│   ├── 几何计算模块 - 切面计算和空间变换
│   ├── 模型处理模块 - 3D模型加载和优化
│   └── 路径计算模块 - 食道路径插值和探头定位
├── 数据管理层
│   ├── 本地存储 - Capacitor文件系统和Preferences
│   ├── 模型缓存 - 3D模型数据缓存机制
│   └── 配置管理 - 应用设置和用户偏好
└── 平台适配层
    ├── Android适配 - Capacitor Android插件
    ├── 触摸优化 - 移动端手势交互
    └── 性能优化 - 平台特定性能调优
```

## 核心设计模式

### 1. 组件化架构
- **React函数组件**: 使用Hooks管理状态和副作用
- **组件分层**: 基础组件 → 业务组件 → 页面组件
- **Props传递**: 单向数据流，避免深层嵌套

### 2. 状态管理
```typescript
// 使用Zustand或Context API管理状态
interface AppState {
  currentPatient: PatientData | null;
  probePosition: ProbePosition;
  sectionData: SectionData | null;
  isLoading: boolean;
}

// 状态更新采用不可变更新模式
setAppState(prev => ({
  ...prev,
  probePosition: newPosition,
  sectionData: calculateSection(newPosition)
}));
```

### 3. 3D渲染模式
- **场景图管理**: Three.js场景、相机、渲染器分离
- **资源加载**: 异步加载3D模型，显示加载进度
- **性能优化**: 按需渲染，避免不必要的重渲染

### 4. 数据流模式
```
用户交互 → 状态更新 → 计算触发 → 渲染更新
    ↓          ↓          ↓          ↓
触摸事件 → 探头位置 → 切面计算 → 3D更新
```

## 关键技术决策

### 1. 技术栈选择理由
- **React + TypeScript**: 类型安全，开发效率高，LLM支持好
- **Three.js**: 成熟的WebGL库，丰富的3D功能
- **Capacitor**: Web转原生，支持离线运行
- **Vite**: 快速的开发体验，优秀的构建性能

### 2. 架构分离原则
- **关注点分离**: UI、业务逻辑、数据管理分离
- **平台无关性**: 核心算法不依赖特定平台API
- **可测试性**: 各模块可独立测试

### 3. 性能优化策略
- **计算缓存**: 切面计算结果缓存，避免重复计算
- **渐进加载**: 大型3D模型分块加载
- **内存管理**: 及时释放无用资源，避免内存泄漏

## 接口设计

### 核心接口定义
```typescript
// 病人数据接口
interface PatientData {
  id: string;
  name: string;
  heartModel: THREE.Mesh;
  esophagusPath: Vector3[];
  metadata: PatientMetadata;
}

// 探头位置接口
interface ProbePosition {
  depth: number;      // 0-100
  angle: number;      // 0-360度
  worldPosition: Vector3;
  direction: Vector3;
}

// 切面数据接口
interface SectionData {
  lines: THREE.LineSegments;
  plane: THREE.Plane;
  isValid: boolean;
}
```

### 模块间通信
- **事件驱动**: 使用自定义事件或状态管理进行模块通信
- **异步处理**: 耗时操作使用Promise或async/await
- **错误边界**: React错误边界处理渲染错误

## 扩展性考虑

### 1. 插件架构
- **算法插件**: 支持不同的切面计算算法
- **模型插件**: 支持多种3D模型格式
- **UI插件**: 可扩展的界面组件

### 2. 配置驱动
- **可配置参数**: 通过配置文件调整应用行为
- **主题系统**: 支持自定义UI主题
- **本地化**: 支持多语言配置

### 3. 平台扩展
- **新平台支持**: 通过Capacitor添加新平台
- **功能分级**: 不同平台提供适当的功能子集
- **渐进增强**: 基础功能+平台特定增强功能
