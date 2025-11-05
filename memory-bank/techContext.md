# 技术上下文

## 开发环境配置

### 核心开发工具
- **代码编辑器**: VS Code + Cline扩展
- **版本控制**: Git + GitHub
- **包管理器**: npm (Node.js 18+)
- **构建工具**: Vite
- **移动端打包**: Capacitor
- **Android开发**: Android Studio

### 开发依赖
```json
{
  "核心运行时依赖": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "three": "^0.158.0",
    "@types/three": "^0.158.0",
    "@capacitor/core": "^5.0.0",
    "@capacitor/android": "^5.0.0"
  },
  "UI组件库": {
    "@mui/material": "^5.14.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0"
  },
  "开发工具": {
    "typescript": "^5.0.0",
    "vite": "^4.4.0",
    "@vitejs/plugin-react": "^4.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  }
}
```

## 技术约束

### 性能约束
- **切面计算响应时间**: < 100ms
- **内存使用**: < 500MB
- **启动时间**: < 3秒
- **帧率**: 在目标设备上保持60fps

### 平台约束
- **Android版本**: 支持Android 8.0+
- **存储空间**: 应用安装包 < 50MB
- **网络**: 支持完全离线运行
- **权限**: 需要文件存储权限

### 数据约束
- **3D模型格式**: 主要支持STL，可选支持OBJ
- **文件大小**: 单个模型文件 < 20MB
- **数据安全**: 医疗数据本地存储，不传输到服务器

## 开发工作流

### 1. 本地开发
```bash
# 启动开发服务器
npm run dev

# 代码质量检查
npm run lint
npm run lint:fix

# 类型检查
npx tsc --noEmit
```

### 2. 构建和测试
```bash
# 生产构建
npm run build

# 预览构建结果
npm run preview

# 移动端同步
npm run cap:sync
```

### 3. 移动端部署
```bash
# Android开发
npm run cap:android

# Android构建
npm run cap:build:android

# iOS开发 (需要macOS)
npm run cap:ios
```

## 架构决策记录

### 1. 技术栈选择
**决策**: 选择React + TypeScript + Three.js + Capacitor
**理由**:
- VS Code + Cline + LLM对Web技术栈支持最佳
- 一次开发，多平台部署
- 丰富的生态系统和社区支持
- 符合现代Web开发标准

### 2. 状态管理
**决策**: 使用React Context + useReducer或Zustand
**理由**:
- 应用状态相对简单，不需要复杂的状态管理
- 保持代码简洁，减少学习成本
- 与React生态良好集成

### 3. 3D渲染方案
**决策**: 使用Three.js而非其他3D引擎
**理由**:
- 成熟的WebGL解决方案
- 丰富的加载器和工具
- 活跃的社区和文档
- 良好的性能表现

### 4. 移动端方案
**决策**: 使用Capacitor而非React Native
**理由**:
- 基于Web技术，开发体验一致
- 支持渐进式Web应用
- 更好的3D渲染性能
- 更简单的构建流程

## 开发规范

### 代码规范
- **命名约定**: 使用camelCase（变量、函数）、PascalCase（组件、类）
- **文件组织**: 按功能模块组织，避免过深的嵌套
- **导入顺序**: 第三方库 → 内部模块 → 相对路径
- **注释要求**: 公共API必须有JSDoc注释

### 组件设计原则
- **单一职责**: 每个组件只负责一个特定功能
- **可组合性**: 组件应该易于组合和重用
- **可测试性**: 组件逻辑应该易于单元测试
- **性能意识**: 避免不必要的重渲染

### 错误处理
- **用户友好**: 向用户显示清晰的错误信息
- **开发友好**: 在开发环境提供详细的错误堆栈
- **恢复机制**: 提供错误恢复和重试机制
- **监控日志**: 记录关键操作和错误信息

## 测试策略

### 单元测试
- **测试框架**: Jest + React Testing Library
- **测试范围**: 核心算法、工具函数、组件逻辑
- **测试目标**: 80%+代码覆盖率

### 集成测试
- **测试框架**: Playwright或Cypress
- **测试范围**: 用户交互流程、3D渲染功能
- **测试环境**: 真实浏览器环境

### 性能测试
- **测试工具**: Chrome DevTools Performance面板
- **测试指标**: 加载时间、内存使用、帧率
- **测试设备**: 目标Android平板设备

## 部署和运维

### 构建配置
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  build: {
    target: 'es2015',
    rollupOptions: {
      output: {
        manualChunks: {
          three: ['three'],
          vendor: ['react', 'react-dom']
        }
      }
    }
  }
});
```

### 发布流程
1. **版本管理**: 遵循语义化版本控制
2. **构建验证**: 在目标设备上测试构建结果
3. **发布检查**: 检查所有功能在发布版本中正常工作
4. **文档更新**: 更新用户手册和发布说明

### 监控和维护
- **错误监控**: 前端错误监控和报告
- **性能监控**: 关键性能指标收集
- **用户反馈**: 收集用户使用反馈和改进建议
- **定期更新**: 依赖库更新和安全补丁
