import { Vector3, Plane } from '../../../src/core/algorithms/geometry/index';
import { RealTimeUpdateService } from '../../../src/core/algorithms/services/RealTimeUpdateService';

/**
 * 实时切面更新服务测试
 * 测试1.3 实时切面更新用户故事相关功能
 */
describe('实时切面更新服务', () => {
  let service: RealTimeUpdateService;

  beforeEach(() => {
    service = new RealTimeUpdateService();
  });

  describe('探头位置更新', () => {
    test('探头移动时切面实时计算', () => {
      // 模拟探头位置
      const probePosition = new Vector3(0, 0, 0);
      const probeDirection = new Vector3(0, 1, 0);
      
      // 模拟心脏模型数据
      const heartModel = {
        triangles: [
          [new Vector3(-1, -1, 0), new Vector3(1, -1, 0), new Vector3(0, 1, 0)]
        ]
      };

      // 更新探头位置并计算切面
      const result = service.updateSection(probePosition, probeDirection, heartModel);
      
      // 验证切面计算结果
      expect(result.lines).toBeDefined();
      expect(result.isValid).toBe(true);
      expect(result.calculationTime).toBeLessThan(100); // 响应时间 < 100ms
    });

    test('切面更新响应时间要求', () => {
      const probePosition = new Vector3(0, 0, 0);
      const probeDirection = new Vector3(0, 1, 0);
      const heartModel = {
        triangles: [
          [new Vector3(-1, -1, 0), new Vector3(1, -1, 0), new Vector3(0, 1, 0)]
        ]
      };

      const startTime = performance.now();
      const result = service.updateSection(probePosition, probeDirection, heartModel);
      const endTime = performance.now();
      
      const calculationTime = endTime - startTime;
      expect(calculationTime).toBeLessThan(100); // 响应时间 < 100ms
      expect(result.calculationTime).toBeLessThan(100);
    });

    test('连续移动时切面显示流畅', () => {
      const heartModel = {
        triangles: [
          [new Vector3(-1, -1, 0), new Vector3(1, -1, 0), new Vector3(0, 1, 0)]
        ]
      };

      // 模拟连续移动
      const positions = [
        new Vector3(0, 0, 0),
        new Vector3(0.1, 0, 0),
        new Vector3(0.2, 0, 0),
        new Vector3(0.3, 0, 0)
      ];
      const direction = new Vector3(0, 1, 0);

      let lastResult = null;
      for (const position of positions) {
        const result = service.updateSection(position, direction, heartModel);
        
        // 验证每次计算都成功
        expect(result.isValid).toBe(true);
        expect(result.calculationTime).toBeLessThan(100);
        
        // 验证结果连续性（如果存在上次结果）
        if (lastResult) {
          // 切面应该随着探头位置变化而平滑变化
          expect(result.lines.length).toBeGreaterThan(0);
        }
        
        lastResult = result;
      }
    });

    test('支持离散位置更新', () => {
      const heartModel = {
        triangles: [
          [new Vector3(-1, -1, 0), new Vector3(1, -1, 0), new Vector3(0, 1, 0)]
        ]
      };

      // 模拟离散位置 - 确保所有位置都与三角形相交
      const positions = [
        new Vector3(0, 0, 0),    // 在三角形内部
        new Vector3(0, 0.5, 0),  // 在三角形内部
        new Vector3(-0.5, 0, 0)  // 在三角形内部
      ];
      const direction = new Vector3(0, 1, 0);

      for (const position of positions) {
        const result = service.updateSection(position, direction, heartModel);
        
        expect(result.isValid).toBe(true);
        expect(result.lines).toBeDefined();
      }
    });
  });

  describe('性能优化', () => {
    test('结果缓存机制', () => {
      const probePosition = new Vector3(0, 0, 0);
      const probeDirection = new Vector3(0, 1, 0);
      const heartModel = {
        triangles: [
          [new Vector3(-1, -1, 0), new Vector3(1, -1, 0), new Vector3(0, 1, 0)]
        ]
      };

      // 第一次计算
      const firstResult = service.updateSection(probePosition, probeDirection, heartModel);
      
      // 相同参数第二次计算应该使用缓存
      const secondResult = service.updateSection(probePosition, probeDirection, heartModel);
      
      // 验证缓存机制工作
      expect(secondResult.calculationTime).toBeLessThan(firstResult.calculationTime);
      expect(secondResult.fromCache).toBe(true);
    });

    test('增量计算策略', () => {
      const heartModel = {
        triangles: [
          [new Vector3(-1, -1, 0), new Vector3(1, -1, 0), new Vector3(0, 1, 0)]
        ]
      };

      // 模拟小幅度移动
      const startPosition = new Vector3(0, 0, 0);
      const smallMove = new Vector3(0.01, 0, 0);
      const direction = new Vector3(0, 1, 0);

      const firstResult = service.updateSection(startPosition, direction, heartModel);
      const secondResult = service.updateSection(
        startPosition.add(smallMove), 
        direction, 
        heartModel
      );

      // 验证增量计算正确性
      expect(secondResult.isValid).toBe(true);
      expect(secondResult.lines.length).toBeGreaterThan(0);
    });
  });

  describe('错误处理', () => {
    test('无效探头位置处理', () => {
      const invalidPosition = new Vector3(NaN, 0, 0);
      const direction = new Vector3(0, 1, 0);
      const heartModel = {
        triangles: [
          [new Vector3(-1, -1, 0), new Vector3(1, -1, 0), new Vector3(0, 1, 0)]
        ]
      };

      const result = service.updateSection(invalidPosition, direction, heartModel);
      
      expect(result.isValid).toBe(false);
      expect(result.error).toBeDefined();
    });

    test('空模型处理', () => {
      const probePosition = new Vector3(0, 0, 0);
      const probeDirection = new Vector3(0, 1, 0);
      const emptyModel = { triangles: [] };

      const result = service.updateSection(probePosition, probeDirection, emptyModel);
      
      expect(result.isValid).toBe(false);
      expect(result.lines).toHaveLength(0);
    });
  });
});
