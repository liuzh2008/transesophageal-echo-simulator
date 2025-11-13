import { Vector3 } from '../../../src/core/algorithms/geometry/index';
import { SectionVisualizationService } from '../../../src/core/algorithms/services/SectionVisualizationService';

/**
 * 切面可视化服务测试
 * 测试1.4 切面可视化用户故事相关功能
 */
describe('切面可视化服务', () => {
  let service: SectionVisualizationService;

  beforeEach(() => {
    service = new SectionVisualizationService();
  });

  describe('切面轮廓显示', () => {
    test('切面轮廓清晰可见', () => {
      // 模拟切面交线数据
      const intersectionLines = [
        [new Vector3(-1, 0, 0), new Vector3(1, 0, 0)],
        [new Vector3(0, -1, 0), new Vector3(0, 1, 0)]
      ];

      // 获取可视化配置
      const visualizationConfig = service.getVisualizationConfig(intersectionLines);
      
      // 验证轮廓可见性配置
      expect(visualizationConfig.visible).toBe(true);
      expect(visualizationConfig.lineWidth).toBeGreaterThan(0);
      expect(visualizationConfig.color).toBeDefined();
    });

    test('支持不同颜色设置', () => {
      const intersectionLines = [
        [new Vector3(-1, 0, 0), new Vector3(1, 0, 0)]
      ];

      // 测试自定义颜色
      const customColor = '#ff0000';
      const config = service.getVisualizationConfig(intersectionLines, { color: customColor });
      
      expect(config.color).toBe(customColor);
    });

    test('支持不同线宽设置', () => {
      const intersectionLines = [
        [new Vector3(-1, 0, 0), new Vector3(1, 0, 0)]
      ];

      // 测试自定义线宽
      const customLineWidth = 3;
      const config = service.getVisualizationConfig(intersectionLines, { lineWidth: customLineWidth });
      
      expect(config.lineWidth).toBe(customLineWidth);
    });
  });

  describe('切面高亮显示', () => {
    test('切面可以高亮显示', () => {
      const intersectionLines = [
        [new Vector3(-1, 0, 0), new Vector3(1, 0, 0)]
      ];

      // 启用高亮模式
      const config = service.getVisualizationConfig(intersectionLines, { highlight: true });
      
      expect(config.highlight).toBe(true);
      expect(config.lineWidth).toBeGreaterThan(2); // 高亮时线宽应该更大
      expect(config.color).toMatch(/^#[0-9a-fA-F]{6}$/); // 应该是有效的颜色值
    });

    test('高亮颜色可自定义', () => {
      const intersectionLines = [
        [new Vector3(-1, 0, 0), new Vector3(1, 0, 0)]
      ];

      const highlightColor = '#ffff00';
      const config = service.getVisualizationConfig(intersectionLines, { 
        highlight: true, 
        highlightColor: highlightColor 
      });
      
      expect(config.color).toBe(highlightColor);
    });
  });

  describe('透明度调整', () => {
    test('支持切面透明度调整', () => {
      const intersectionLines = [
        [new Vector3(-1, 0, 0), new Vector3(1, 0, 0)]
      ];

      // 测试透明度设置
      const opacity = 0.5;
      const config = service.getVisualizationConfig(intersectionLines, { opacity });
      
      expect(config.opacity).toBe(opacity);
      expect(config.opacity).toBeGreaterThanOrEqual(0);
      expect(config.opacity).toBeLessThanOrEqual(1);
    });

    test('透明度边界值处理', () => {
      const intersectionLines = [
        [new Vector3(-1, 0, 0), new Vector3(1, 0, 0)]
      ];

      // 测试边界值
      const minOpacityConfig = service.getVisualizationConfig(intersectionLines, { opacity: 0 });
      const maxOpacityConfig = service.getVisualizationConfig(intersectionLines, { opacity: 1 });
      
      expect(minOpacityConfig.opacity).toBe(0);
      expect(maxOpacityConfig.opacity).toBe(1);
    });
  });

  describe('性能优化', () => {
    test('大量交线数据可视化性能', () => {
      // 生成大量交线数据模拟复杂切面
      const complexIntersectionLines = [];
      for (let i = 0; i < 1000; i++) {
        complexIntersectionLines.push([
          new Vector3(Math.random() * 2 - 1, Math.random() * 2 - 1, 0),
          new Vector3(Math.random() * 2 - 1, Math.random() * 2 - 1, 0)
        ]);
      }

      const startTime = performance.now();
      const config = service.getVisualizationConfig(complexIntersectionLines);
      const endTime = performance.now();
      
      const calculationTime = endTime - startTime;
      
      // 验证性能要求
      expect(calculationTime).toBeLessThan(50); // 可视化配置计算时间 < 50ms
      expect(config).toBeDefined();
      expect(config.visible).toBe(true);
    });
  });

  describe('错误处理', () => {
    test('空交线数据处理', () => {
      const emptyLines: Vector3[][] = [];
      
      const config = service.getVisualizationConfig(emptyLines);
      
      expect(config.visible).toBe(false);
      expect(config.lineWidth).toBe(0);
    });

    test('无效交线数据格式', () => {
      const invalidLines = [
        [new Vector3(0, 0, 0)] // 只有单个点，不是线段
      ] as Vector3[][];

      const config = service.getVisualizationConfig(invalidLines);
      
      // 应该能够处理无效格式，返回默认配置
      expect(config).toBeDefined();
      expect(config.visible).toBe(false);
    });
  });
});
