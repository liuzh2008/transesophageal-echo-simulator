# **STL文件加载接口**

## **接口路径**
- 服务类：`src/core/services/STLLoaderService.ts`
- 服务类：`src/core/services/FileSystemService.ts`
- 管理器类：`src/core/managers/ModelManager.ts`

## **功能说明**
STL文件加载功能提供完整的3D模型文件加载、解析和管理能力，支持从用户选择的STL文件加载心脏模型并在3D场景中显示。

## **请求参数**

### STLLoaderService.parseSTLBuffer
**功能**: 解析STL二进制数据为Three.js网格
**参数**:
- `buffer: ArrayBuffer` - STL文件的二进制数据
**返回**: `THREE.Mesh` - Three.js网格对象
**异常**: 当STL数据无效时抛出错误

### STLLoaderService.validateSTLFile
**功能**: 验证STL文件是否有效
**参数**:
- `file: File` - 要验证的文件对象
**返回**: `boolean` - 文件是否有效

### STLLoaderService.loadFromFile
**功能**: 从文件对象加载STL模型
**参数**:
- `file: File` - STL文件对象
**返回**: `Promise<THREE.Mesh>` - 解析后的Three.js网格
**异常**: 当文件无效或加载失败时抛出错误

### FileSystemService.readFile
**功能**: 读取文件内容为ArrayBuffer
**参数**:
- `file: File` - 要读取的文件对象
**返回**: `Promise<ArrayBuffer>` - 文件的ArrayBuffer数据
**异常**: 当文件读取失败时抛出错误

### FileSystemService.listDirectory
**功能**: 列出指定目录中的文件
**参数**:
- `path: string` - 目录路径
**返回**: `Promise<string[]>` - 文件路径数组
**异常**: 当目录访问失败时抛出错误

### ModelManager.loadModel
**功能**: 加载STL模型文件
**参数**:
- `file: File` - STL文件对象
**返回**: `Promise<THREE.Mesh>` - 加载的Three.js网格
**异常**: 当文件无效或加载失败时抛出错误

### ModelManager.disposeModel
**功能**: 释放模型资源
**参数**:
- `mesh: THREE.Mesh | null` - 要释放的网格对象

## **响应格式**

### STLLoaderService响应
```typescript
// 成功响应：THREE.Mesh对象
const mesh: THREE.Mesh = {
  geometry: THREE.BufferGeometry,
  material: THREE.Material,
  // ...其他Three.js网格属性
}

// 错误响应：Error对象
const error: Error = new Error('STL文件解析失败: 具体错误信息')
```

### FileSystemService响应
```typescript
// 成功响应：ArrayBuffer
const buffer: ArrayBuffer = new ArrayBuffer(fileSize)

// 成功响应：文件列表
const files: string[] = ['patient_001.stl', 'patient_002.stl', 'patient_003.stl']

// 错误响应：Error对象
const error: Error = new Error('文件读取失败: 具体错误信息')
```

### ModelManager响应
```typescript
// 成功响应：THREE.Mesh对象
const mesh: THREE.Mesh = {
  geometry: THREE.BufferGeometry,
  material: THREE.Material,
  // ...其他Three.js网格属性
}

// 缓存统计信息
const cacheStats: CacheStats = {
  totalModels: number,
  memoryUsage: number,
  fileNames: string[]
}

// 预加载结果
const preloadResult: PreloadResult = {
  total: number,
  loaded: number,
  failed: number,
  errors: Array<{ fileName: string, error: string }>
}
```

## **逻辑**

### STL文件加载流程
1. **文件验证** - 验证文件类型、大小和格式
2. **文件读取** - 将文件读取为ArrayBuffer
3. **STL解析** - 使用Three.js STLLoader解析二进制数据
4. **网格创建** - 创建Three.js网格对象
5. **缓存管理** - 将模型添加到缓存中
6. **资源管理** - 提供资源释放机制

### 错误处理逻辑
- **文件验证失败**: 立即返回错误，不进行后续处理
- **文件读取失败**: 捕获FileReader错误并抛出
- **STL解析失败**: 捕获Three.js解析错误并抛出
- **内存管理**: 提供dispose方法释放Three.js资源

### 缓存管理逻辑
- **缓存策略**: 基于文件名的LRU缓存
- **内存统计**: 估算几何体数据内存使用量
- **缓存清理**: 支持手动清空缓存和释放资源

## **响应示例**

### 成功加载STL文件
```typescript
// 调用
const file = new File([stlData], 'heart_model.stl', { type: 'application/sla' });
const mesh = await modelManager.loadModel(file);

// 响应
console.log(mesh);
// THREE.Mesh {
//   geometry: THREE.BufferGeometry { ... },
//   material: THREE.MeshPhongMaterial { ... },
//   // ...其他属性
// }
```

### 文件验证失败
```typescript
// 调用
const invalidFile = new File([], 'invalid.txt', { type: 'text/plain' });
try {
  await modelManager.loadModel(invalidFile);
} catch (error) {
  console.error(error.message);
  // "无效的STL文件"
}
```

### 获取缓存统计
```typescript
// 调用
const stats = modelManager.getCacheStats();

// 响应
console.log(stats);
// {
//   totalModels: 3,
//   memoryUsage: 1520432,
//   fileNames: ['patient_001.stl', 'patient_002.stl', 'patient_003.stl']
// }
```

## **相关文件**

### 核心实现文件
- `src/core/services/STLLoaderService.ts` - STL文件解析服务
- `src/core/services/FileSystemService.ts` - 文件系统抽象服务
- `src/core/managers/ModelManager.ts` - 模型生命周期管理器

### 测试文件
- `tests/unit/services/STLLoaderService.test.ts` - STL加载服务测试
- `tests/unit/services/FileSystemService.test.ts` - 文件系统服务测试
- `tests/unit/managers/ModelManager.test.ts` - 模型管理器测试

### 类型定义文件
- `src/core/services/STLLoaderService.ts` - 包含STL加载相关类型
- `src/core/services/FileSystemService.ts` - 包含文件系统相关类型
- `src/core/managers/ModelManager.ts` - 包含模型管理相关类型

### 文档文件
- `doc/方案/TDD实施指南-STL文件加载功能.md` - TDD实施指南
- `memory-bank/activeContext.md` - 当前工作状态
- `memory-bank/progress.md` - 项目进度跟踪

## **技术特点**

### 关注点分离
- **数据层**: 纯STL文件解析，不涉及UI或状态管理
- **业务逻辑层**: 模型生命周期管理，包含缓存和资源管理
- **表示层**: 用户界面组件，负责文件选择和状态显示

### 错误处理
- 完整的错误类型定义和错误消息
- 边界情况处理（空文件、无效格式等）
- 资源释放和内存管理

### 性能优化
- 模型缓存机制避免重复加载
- 内存使用统计和监控
- 渐进式加载支持

### 跨平台支持
- 文件系统抽象层支持不同平台
- 浏览器环境适配
- 移动端优化考虑
