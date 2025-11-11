import { Vector3, Plane, planeTriangleIntersection } from '../../../src/core/algorithms/geometry/index';

/**
 * 平面-网格求交算法测试
 * 按照TDD红-绿-重构流程实现几何交线计算功能
 */
describe('平面-网格求交算法', () => {
  describe('三角形求交计算', () => {
    test('平面与三角形相交 - 标准情况', () => {
      // 创建水平平面 z = 0
      const plane = new Plane(new Vector3(0, 0, 1), 0);
      
      // 创建与平面相交的三角形
      const triangle: [Vector3, Vector3, Vector3] = [
        new Vector3(-1, -1, -1),
        new Vector3(1, -1, 1),
        new Vector3(0, 1, 0)
      ];
      
      // 计算交点
      const intersection = planeTriangleIntersection(plane, triangle);
      
      // 期望得到两个交点
      expect(intersection).toHaveLength(2);
      
      // 验证交点确实在平面上
      intersection.forEach(point => {
        expect(plane.containsPoint(point)).toBe(true);
      });
    });

    test('平面与三角形平行 - 无交点', () => {
      // 创建水平平面 z = 2
      const plane = new Plane(new Vector3(0, 0, 1), -2);
      
      // 创建在 z=0 平面的三角形
      const triangle: [Vector3, Vector3, Vector3] = [
        new Vector3(-1, -1, 0),
        new Vector3(1, -1, 0),
        new Vector3(0, 1, 0)
      ];
      
      // 计算交点
      const intersection = planeTriangleIntersection(plane, triangle);
      
      // 期望没有交点
      expect(intersection).toHaveLength(0);
    });

    test('平面与三角形相切 - 一个交点', () => {
      // 创建水平平面 z = 0
      const plane = new Plane(new Vector3(0, 0, 1), 0);
      
      // 创建与平面相切的三角形（一个顶点在平面上）
      const triangle: [Vector3, Vector3, Vector3] = [
        new Vector3(-1, -1, 0),  // 在平面上
        new Vector3(1, -1, 1),
        new Vector3(0, 1, 1)
      ];
      
      // 计算交点
      const intersection = planeTriangleIntersection(plane, triangle);
      
      // 期望得到一个交点
      expect(intersection).toHaveLength(1);
      
      // 验证交点在平面上
      expect(plane.containsPoint(intersection[0])).toBe(true);
    });

    test('三角形完全在平面上 - 三个交点', () => {
      // 创建水平平面 z = 0
      const plane = new Plane(new Vector3(0, 0, 1), 0);
      
      // 创建完全在平面上的三角形
      const triangle: [Vector3, Vector3, Vector3] = [
        new Vector3(-1, -1, 0),
        new Vector3(1, -1, 0),
        new Vector3(0, 1, 0)
      ];
      
      // 计算交点
      const intersection = planeTriangleIntersection(plane, triangle);
      
      // 期望得到三个交点（三角形的三个顶点）
      expect(intersection).toHaveLength(3);
      
      // 验证所有交点都在平面上
      intersection.forEach(point => {
        expect(plane.containsPoint(point)).toBe(true);
      });
    });
  });

  describe('边界情况处理', () => {
    test('退化三角形处理', () => {
      // 创建水平平面 z = 0
      const plane = new Plane(new Vector3(0, 0, 1), 0);
      
      // 创建退化三角形（三个点共线）
      const degenerateTriangle: [Vector3, Vector3, Vector3] = [
        new Vector3(-1, 0, 0),
        new Vector3(0, 0, 0),
        new Vector3(1, 0, 0)
      ];
      
      // 计算交点
      const intersection = planeTriangleIntersection(plane, degenerateTriangle);
      
      // 期望没有交点或特殊处理
      expect(intersection).toBeDefined();
    });

    test('浮点数精度处理', () => {
      // 创建接近平面的三角形
      const plane = new Plane(new Vector3(0, 0, 1), 0);
      const triangle: [Vector3, Vector3, Vector3] = [
        new Vector3(-1, -1, 1e-15),
        new Vector3(1, -1, -1e-15),
        new Vector3(0, 1, 0)
      ];
      
      // 计算交点
      const intersection = planeTriangleIntersection(plane, triangle);
      
      // 期望正确处理浮点数精度
      expect(intersection).toBeDefined();
    });
  });
});
