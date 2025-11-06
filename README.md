# 食道超声模拟软件

基于React + TypeScript + Three.js的3D食道超声模拟软件项目。

## 项目结构

```
食道超声模拟软件/
├── src/                    # 源代码目录
│   ├── core/              # 核心业务逻辑
│   │   └── Scene3D.tsx    # 3D场景组件
│   ├── ui/                # 用户界面组件
│   │   ├── App.tsx        # 主应用组件
│   │   └── styles.css     # 样式文件
│   ├── data/              # 数据管理
│   └── main.tsx           # 应用入口文件
├── tests/                 # 测试文件
│   └── framework/         # 框架测试
│       └── project-structure.test.ts
├── doc/                   # 项目文档
├── config/                # 配置文件
├── memory-bank/           # 项目记忆库
├── package.json           # 项目依赖配置
├── tsconfig.json          # TypeScript配置
├── tsconfig.node.json     # Node.js TypeScript配置
├── vite.config.ts         # Vite构建配置
├── jest.config.cjs        # Jest测试配置
└── index.html             # HTML模板
```

## 技术栈

- **前端框架**: React 18 + TypeScript
- **3D渲染**: Three.js
- **构建工具**: Vite
- **测试框架**: Jest
- **开发语言**: TypeScript

## 开发指南

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```

### 构建项目
```bash
npm run build
```

### 运行测试
```bash
npm test
```

### 测试覆盖率
```bash
npm run test:coverage
```

## TDD实施

本项目采用测试驱动开发(TDD)流程：

1. **红阶段**: 编写会失败的测试用例
2. **绿阶段**: 编写最小代码使测试通过
3. **重构阶段**: 优化代码结构，保持测试通过

## 功能特性

- ✅ React + TypeScript项目结构
- ✅ 3D场景渲染基础
- ✅ 组件化架构
- ✅ 测试驱动开发
- ✅ 现代化构建工具链

## 开发进度

- [x] 基础项目结构搭建
- [x] React + TypeScript配置
- [x] 3D场景基础功能
- [x] 测试框架配置
- [ ] 食道模型加载
- [ ] 超声探头模拟
- [ ] 实时渲染优化
- [ ] 用户交互控制

## 注意事项

整个TDD实施指南完成后，请手动运行 `npm test` 来进行整个系统的测试。
