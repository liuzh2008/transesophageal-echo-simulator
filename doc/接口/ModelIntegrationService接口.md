# ModelIntegrationService接口文档

**接口路径**: `src/core/services/ModelIntegrationService.ts`

## 功能说明
ModelIntegrationService是连接文件选择器与模型状态管理的集成服务，负责处理完整的文件加载流程，包括文件选择、状态管理、模型解析和数据转换。

## 请求参数

### 构造函数参数
- **modelStore**: ModelStore - 模型状态管理实例
- **stlLoaderService**: STLLoaderService - STL文件解析服务实例  
- **fileSystemService**: FileSystemService - 文件系统抽象服务实例

### loadModelFromFile方法参数
- **file**: File - 用户选择的STL文件对象

### handleFileSelectionError方法参数
- **error**: string - 文件选择错误信息

## 响应格式

### loadModelFromFile方法返回值
- **Promise<THREE.Mesh>** - 加载成功的Three.js网格对象

### getCurrentState方法返回值
- **ModelState** - 当前模型状态对象

## 逻辑

### 文件加载流程
1. **开始加载状态** - 调用modelStore.startLoading()设置加载状态
2. **文件解析** - 使用STLLoaderService.loadFromFile()解析STL文件
3. **进度更新** - 更新加载进度到100%
4. **数据转换** - 将THREE.Mesh转换为STLModel数据结构
5. **成功状态** - 调用modelStore.setSuccess()设置成功状态
6. **错误处理** - 捕获异常并设置错误状态

### 数据转换逻辑
- **顶点数据**: 从geometry.attributes.position.array提取
- **法线数据**: 从geometry.attributes.normal.array提取  
- **面数据**: 从geometry.index.array提取或生成顺序索引

### 错误处理逻辑
- 捕获所有异常并转换为用户友好的错误信息
- 调用modelStore.setError()设置错误状态
- 重新抛出异常以便上层处理

## 响应示例

### 成功响应示例
```typescript
// 返回的THREE.Mesh对象
{
  geometry: {
    attributes: {
      position: { array: Float32Array, itemSize: 3 },
      normal: { array: Float32Array, itemSize: 3 }
    },
    index: { array: Uint16Array }
  },
  material: {
    color: 0x00ff00,
    specular: 0x111111,
    shininess: 200
  }
}

// 转换后的STLModel
{
  vertices: [0, 0, 0, 1, 0, 0, 0, 1, 0],
  normals: [0, 0, 1, 0, 0, 1, 0, 0, 1],
  faces: [0, 1, 2]
}
```

### 错误响应示例
```typescript
// 错误状态
{
  isLoading: false,
  currentModel: null,
  error: "文件加载失败: 无效的STL文件格式",
  progress: 0
}
```

## 相关文件

### 依赖文件
- `src/data/models/ModelStore.ts` - 模型状态管理
- `src/core/services/STLLoaderService.ts` - STL文件解析服务
- `src/core/services/FileSystemService.ts` - 文件系统抽象服务
- `src/core/types/STLModel.ts` - STL模型数据类型定义

### 使用文件
- `src/ui/components/FileSelector.tsx` - 文件选择器组件
- `tests/integration/file-selector-integration.test.tsx` - 集成测试

### 测试文件
- `tests/integration/file-selector-integration.test.tsx` - 集成测试用例

## 接口方法

### loadModelFromFile(file: File): Promise<THREE.Mesh>
处理文件选择并加载模型，返回Three.js网格对象。

### handleFileSelectionError(error: string): void
处理文件选择错误，更新模型状态。

### resetModelState(): void
重置模型状态到初始状态。

### getCurrentState(): ModelState
获取当前模型状态。

### convertMeshToSTLModel(mesh: THREE.Mesh): STLModel (私有)
将THREE.Mesh转换为STLModel数据结构。
