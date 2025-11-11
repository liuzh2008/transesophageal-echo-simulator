# 食道超声模拟软件 - 切面计算算法TDD实施指南

## 1. 用户故事拆分

### 1.1 切割平面定义用户故事
**作为** 超声医生  
**我希望** 能够定义切割平面  
**以便** 对心脏模型进行切面分析

**验收标准：**
- [x] 能够通过探头位置和方向定义切割平面
- [x] 切割平面参数可以实时调整
- [x] 平面定义支持法向量和距离参数
- [ ] 平面可视化显示在3D场景中

### 1.2 几何交线计算用户故事
**作为** 超声医生  
**我希望** 能够计算切割平面与心脏模型的交线  
**以便** 获得准确的切面轮廓

**验收标准：**
- [ ] 能够计算平面与STL网格的交点
- [ ] 交线计算准确且完整
- [ ] 支持不同复杂度的网格模型
- [ ] 交线结果可以实时可视化

### 1.3 实时切面更新用户故事
**作为** 超声医生  
**我希望** 切面能够随着探头移动实时更新  
**以便** 模拟真实的超声检查过程

**验收标准：**
- [ ] 探头移动时切面实时计算
- [ ] 切面更新响应时间 < 100ms
- [ ] 切面显示流畅无卡顿
- [ ] 支持连续移动和离散位置

### 1.4 切面可视化用户故事
**作为** 超声医生  
**我希望** 能够清晰看到切面轮廓  
**以便** 进行准确的诊断分析

**验收标准：**
- [ ] 切面轮廓清晰可见
- [ ] 支持不同颜色和线宽设置
- [ ] 切面可以高亮显示
- [ ] 支持切面透明度调整

## 2. TDD实施计划

### 2.1 数学基础模块（2天）

#### 测试用例设计
```typescript
// tests/unit/algorithms/geometry.test.ts
describe('几何计算基础', () => {
  test('平面定义和参数计算', () => {
    // 验证平面参数计算正确性
  });
  
  test('点面距离计算', () => {
    // 验证点到平面距离计算
  });
  
  test('向量运算', () => {
    // 验证向量点积、叉积等运算
  });
  
  test('矩阵变换', () => {
    // 验证坐标变换矩阵计算
  });
});
```

#### 实施步骤
1. **红**：编写几何计算测试用例
2. **绿**：实现基础几何计算函数
3. **重构**：优化数学计算性能和精度

### 2.2 平面-网格求交算法（3天）

#### 测试用例设计
```typescript
// tests/unit/algorithms/intersection.test.ts
describe('平面-网格求交算法', () => {
  test('简单几何体求交', () => {
    // 验证平面与立方体、球体等简单几何体的交线
  });
  
  test('三角形求交计算', () => {
    // 验证平面与单个三角形的交点计算
  });
  
  test('复杂网格求交', () => {
    // 验证平面与复杂STL网格的交线计算
  });
  
  test('边界情况处理', () => {
    // 验证平行平面、切平面等边界情况
  });
});
```

#### 实施步骤
1. **红**：编写求交算法测试用例
2. **绿**：实现平面-网格求交核心算法
3. **重构**：优化算法性能和内存使用

### 2.3 实时计算优化（2天）

#### 测试用例设计
```typescript
// tests/unit/algorithms/performance.test.ts
describe('性能优化', () => {
  test('计算性能基准', () => {
    // 验证计算时间满足性能要求
  });
  
  test('内存使用优化', () => {
    // 验证内存使用在合理范围内
  });
  
  test('结果缓存机制', () => {
    // 验证缓存机制正确工作
  });
  
  test('增量计算', () => {
    // 验证增量计算正确性
  });
});
```

#### 实施步骤
1. **红**：编写性能测试用例
2. **绿**：实现性能优化策略
3. **重构**：优化算法实现和数据结构

## 3. 持续集成策略

### 3.1 测试金字塔

#### 单元测试（基础层）
- **目标**：测试单个算法函数
- **覆盖率要求**：≥ 90%
- **测试框架**：Jest
- **执行频率**：每次提交

```typescript
// 示例单元测试
test('平面与三角形求交', () => {
  const plane = new Plane(new Vector3(0, 1, 0), 0);
  const triangle = [
    new Vector3(-1, -1, 0),
    new Vector3(1, -1, 0),
    new Vector3(0, 1, 0)
  ];
  const intersection = planeTriangleIntersection(plane, triangle);
  expect(intersection).toHaveLength(2);
});
```

#### 集成测试（中间层）
- **目标**：测试算法模块集成
- **通过率要求**：100%
- **测试框架**：Jest + Testing Library
- **执行频率**：每次构建

```typescript
// 示例集成测试
test('切面计算服务集成', async () => {
  const service = new SectionCalculationService();
  const result = await service.calculateSection(probePosition, heartModel);
  expect(result.intersectionLines).toBeDefined();
  expect(result.isValid).toBe(true);
});
```

#### E2E测试（顶层）
- **目标**：测试完整切面计算流程
- **测试框架**：Playwright
- **执行频率**：每日构建

```typescript
// 示例E2E测试
test('完整切面计算流程', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-testid="load-heart-model"]');
  await page.drag('[data-testid="probe-control"]', { x: 100, y: 50 });
  await expect(page.locator('[data-testid="section-display"]')).toBeVisible();
});
```

### 3.2 自动化测试配置

#### GitHub Actions增强配置
```yaml
# .github/workflows/algorithm-ci.yml
name: Algorithm CI Pipeline

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'src/core/algorithms/**'
      - 'tests/unit/algorithms/**'
  pull_request:
    branches: [ main ]

jobs:
  algorithm-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run algorithm unit tests
        run: npm run test:algorithm -- --coverage
      
      - name: Run performance tests
        run: npm run test:performance
      
      - name: Upload algorithm coverage
        uses: codecov/codecov-action@v3
        with:
          flags: algorithm
```

#### 专用测试脚本配置
```json
// package.json 新增脚本
{
  "scripts": {
    "test:algorithm": "jest tests/unit/algorithms/ --coverage",
    "test:performance": "jest tests/unit/algorithms/performance.test.ts",
    "test:geometry": "jest tests/unit/algorithms/geometry.test.ts",
    "test:intersection": "jest tests/unit/algorithms/intersection.test.ts"
  }
}
```

### 3.3 代码质量门禁

#### 质量门禁标准
- **单元测试覆盖率**：≥ 90%
- **集成测试通过率**：100%
- **性能测试通过率**：100%
- **静态代码分析**：无严重问题
- **所有TDD测试用例**：通过
- **构建状态**：绿色

#### 算法专用质量检查
```json
// package.json 新增质量检查脚本
{
  "scripts": {
    "lint:algorithm": "eslint src/core/algorithms/",
    "type-check:algorithm": "tsc --noEmit src/core/algorithms/",
    "quality:algorithm": "npm run lint:algorithm && npm run type-check:algorithm && npm run test:algorithm"
  }
}
```

## 4. 验收测试驱动开发(ATDD)

### 4.1 Gherkin场景定义

#### 切割平面定义场景
```gherkin
功能: 切割平面定义
  作为超声医生
  我希望能够定义切割平面
  以便对心脏模型进行切面分析

  场景: 通过探头位置定义平面
    当 我移动探头到特定位置
    而且 我设置探头方向
    那么 切割平面应该正确定义
    而且 平面参数应该可以实时调整

  场景: 平面可视化
    当 我定义切割平面时
    那么 平面应该可视化显示在3D场景中
    而且 平面显示应该清晰可见
```

#### 几何交线计算场景
```gherkin
功能: 几何交线计算
  作为超声医生
  我希望能够计算切割平面与心脏模型的交线
  以便获得准确的切面轮廓

  场景: 简单几何体交线计算
    当 我对简单几何体进行切面计算
    那么 应该得到正确的交线轮廓
    而且 交线应该完整且连续

  场景: 复杂网格交线计算
    当 我对复杂心脏模型进行切面计算
    那么 应该得到准确的切面轮廓
    而且 计算应该在性能要求内完成
```

#### 实时切面更新场景
```gherkin
功能: 实时切面更新
  作为超声医生
  我希望切面能够随着探头移动实时更新
  以便模拟真实的超声检查过程

  场景: 探头移动实时更新
    当 我连续移动探头位置
    那么 切面应该实时更新
    而且 更新响应时间应该小于100ms

  场景: 切面显示流畅性
    当 我快速移动探头时
    那么 切面显示应该流畅无卡顿
    而且 不应该出现计算延迟
```

## 5. 迭代交付计划

### 第1-2天：数学基础模块
**目标**：完成几何计算基础函数
- [ ] 平面定义和参数计算测试用例
- [ ] 向量和矩阵运算函数实现
- [ ] 点面距离计算功能
- [ ] 坐标变换工具函数

**交付物**：
- 完整的几何计算基础库
- 数学函数单元测试通过率100%
- 代码覆盖率≥90%

### 第3-5天：平面-网格求交算法
**目标**：实现核心求交算法
- [ ] 三角形求交算法测试用例
- [ ] 平面-网格求交核心算法
- [ ] 边界情况处理逻辑
- [ ] 算法性能基准测试

**交付物**：
- 可用的平面-网格求交算法
- 算法测试用例全部通过
- 性能基准测试报告

### 第6-7天：实时计算优化
**目标**：优化算法性能和实时性
- [ ] 性能优化测试用例
- [ ] 结果缓存机制实现
- [ ] 增量计算策略
- [ ] 内存使用优化

**交付物**：
- 优化后的切面计算算法
- 性能测试满足要求
- 实时计算功能完整

### 第8-10天：集成和测试
**目标**：完整功能集成和测试
- [ ] 与3D场景集成测试
- [ ] 用户界面集成测试
- [ ] 端到端功能测试
- [ ] 性能压力测试

**交付物**：
- 完整的切面计算功能
- 集成测试全部通过
- 性能验收测试报告

## 6. 风险缓解策略

### 技术风险
**风险**：算法复杂度超出预期
- **缓解措施**：
  - 每个迭代都有完整的测试覆盖
  - 性能测试作为每个迭代的验收标准
  - 采用渐进式算法开发策略

**风险**：3D计算性能不达标
- **缓解措施**：
  - 早期性能基准测试
  - 多种优化策略备选
  - 目标设备性能验证

### 需求变更风险
**风险**：切面计算需求变更
- **缓解措施**：
  - TDD便于重构，降低变更成本
  - 小步提交，每次变更影响范围小
  - 模块化设计，算法与界面分离

### 集成问题风险
**风险**：算法与3D引擎集成问题
- **缓解措施**：
  - 持续集成及早发现问题
  - 接口先行设计
  - 模拟测试环境搭建

### 精度问题风险
**风险**：几何计算精度不足
- **缓解措施**：
  - 高精度数学库使用
  - 浮点数误差处理
  - 边界情况充分测试

## 7. 性能和质量监控

### 性能指标监控
- **计算响应时间**：目标 < 100ms
- **内存使用量**：监控算法内存占用
- **CPU使用率**：监控计算负载
- **帧率稳定性**：确保UI流畅性

### 质量指标监控
- **算法正确性**：通过测试用例验证
- **代码覆盖率**：目标 ≥ 90%
- **静态分析结果**：无严重问题
- **性能回归**：监控性能变化趋势

## 8. 技术架构设计

### 算法模块结构
```
src/core/algorithms/
├── geometry/
│   ├── Plane.ts           # 平面定义和计算
│   ├── Vector3.ts         # 三维向量运算
│   └── Matrix4.ts         # 变换矩阵
├── intersection/
│   ├── TriangleIntersection.ts    # 三角形求交
│   ├── MeshIntersection.ts        # 网格求交
│   └── IntersectionResult.ts      # 交线结果
├── optimization/
│   ├── CacheManager.ts    # 结果缓存
│   ├── IncrementalCalculator.ts   # 增量计算
│   └── PerformanceMonitor.ts      # 性能监控
└── services/
    ├── SectionCalculationService.ts   # 切面计算服务
    └── RealTimeUpdateService.ts       # 实时更新服务
```

### 核心接口设计
```typescript
// 切面计算服务接口
interface ISectionCalculationService {
  calculateSection(plane: Plane, mesh: Mesh3D): IntersectionResult;
  calculateRealTimeSection(probe: ProbePosition, mesh: Mesh3D): IntersectionResult;
  optimizePerformance(config: PerformanceConfig): void;
}

// 交线结果接口
interface IntersectionResult {
  lines: Vector3[][];
  isValid: boolean;
  calculationTime: number;
  error?: string;
}
```

这个TDD实施指南为切面计算算法的开发提供了详细的执行框架，确保算法开发按照敏捷开发和测试驱动开发的原则高质量推进，满足项目的性能和质量要求。
