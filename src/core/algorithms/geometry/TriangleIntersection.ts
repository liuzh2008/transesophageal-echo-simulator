import { Vector3 } from './Vector3';
import { Plane } from './Plane';

/**
 * 平面与三角形求交算法
 * 计算平面与三角形的交点
 */
export class TriangleIntersection {
  /**
   * 计算平面与三角形的交点
   * @param plane 平面对象
   * @param triangle 三角形顶点数组 [v0, v1, v2]
   * @param tolerance 浮点数精度容差
   * @returns 交点数组，如果没有交点则返回空数组
   */
  static planeTriangleIntersection(
    plane: Plane, 
    triangle: [Vector3, Vector3, Vector3], 
    tolerance: number = 1e-10
  ): Vector3[] {
    const [v0, v1, v2] = triangle;
    
    // 计算三个顶点到平面的距离
    const d0 = plane.distanceToPoint(v0);
    const d1 = plane.distanceToPoint(v1);
    const d2 = plane.distanceToPoint(v2);
    
    // 检查顶点是否在平面上
    const onPlane0 = Math.abs(d0) < tolerance;
    const onPlane1 = Math.abs(d1) < tolerance;
    const onPlane2 = Math.abs(d2) < tolerance;
    
    // 统计在平面上的顶点数量
    const onPlaneCount = [onPlane0, onPlane1, onPlane2].filter(Boolean).length;
    
    // 如果所有顶点都在平面上，返回所有顶点
    if (onPlaneCount === 3) {
      return [v0.clone(), v1.clone(), v2.clone()];
    }
    
    // 如果两个顶点在平面上，返回这两个顶点
    if (onPlaneCount === 2) {
      const points: Vector3[] = [];
      if (onPlane0) points.push(v0.clone());
      if (onPlane1) points.push(v1.clone());
      if (onPlane2) points.push(v2.clone());
      return points;
    }
    
    // 如果一个顶点在平面上，还需要检查边与平面的交点
    if (onPlaneCount === 1) {
      const points: Vector3[] = [];
      
      // 添加在平面上的顶点
      if (onPlane0) points.push(v0.clone());
      if (onPlane1) points.push(v1.clone());
      if (onPlane2) points.push(v2.clone());
      
      // 检查边与平面的交点
      // 边 v0-v1
      if (d0 * d1 < 0) {
        const t = d0 / (d0 - d1);
        const intersection = v0.add(v1.subtract(v0).multiplyScalar(t));
        points.push(intersection);
      }
      
      // 边 v1-v2
      if (d1 * d2 < 0) {
        const t = d1 / (d1 - d2);
        const intersection = v1.add(v2.subtract(v1).multiplyScalar(t));
        points.push(intersection);
      }
      
      // 边 v2-v0
      if (d2 * d0 < 0) {
        const t = d2 / (d2 - d0);
        const intersection = v2.add(v0.subtract(v2).multiplyScalar(t));
        points.push(intersection);
      }
      
      return points;
    }
    
    // 检查边与平面的交点
    const intersections: Vector3[] = [];
    
    // 边 v0-v1
    if (d0 * d1 < 0) {
      const t = d0 / (d0 - d1);
      const intersection = v0.add(v1.subtract(v0).multiplyScalar(t));
      intersections.push(intersection);
    }
    
    // 边 v1-v2
    if (d1 * d2 < 0) {
      const t = d1 / (d1 - d2);
      const intersection = v1.add(v2.subtract(v1).multiplyScalar(t));
      intersections.push(intersection);
    }
    
    // 边 v2-v0
    if (d2 * d0 < 0) {
      const t = d2 / (d2 - d0);
      const intersection = v2.add(v0.subtract(v2).multiplyScalar(t));
      intersections.push(intersection);
    }
    
    // 处理退化情况（三个点共线）
    if (intersections.length === 0 && onPlaneCount > 0) {
      // 如果有点在平面上但没有边相交，可能是退化三角形
      if (onPlane0) intersections.push(v0.clone());
      if (onPlane1) intersections.push(v1.clone());
      if (onPlane2) intersections.push(v2.clone());
    }
    
    return intersections;
  }

  /**
   * 检查三角形是否与平面相交
   * @param plane 平面对象
   * @param triangle 三角形顶点数组
   * @param tolerance 浮点数精度容差
   * @returns 是否相交
   */
  static intersectsPlane(
    plane: Plane, 
    triangle: [Vector3, Vector3, Vector3], 
    tolerance: number = 1e-10
  ): boolean {
    const [v0, v1, v2] = triangle;
    
    const d0 = plane.distanceToPoint(v0);
    const d1 = plane.distanceToPoint(v1);
    const d2 = plane.distanceToPoint(v2);
    
    // 如果所有距离符号相同且不在平面上，则不相交
    const allPositive = d0 > tolerance && d1 > tolerance && d2 > tolerance;
    const allNegative = d0 < -tolerance && d1 < -tolerance && d2 < -tolerance;
    
    return !(allPositive || allNegative);
  }
}

/**
 * 平面与三角形求交的便捷函数
 */
export function planeTriangleIntersection(
  plane: Plane, 
  triangle: [Vector3, Vector3, Vector3], 
  tolerance: number = 1e-10
): Vector3[] {
  return TriangleIntersection.planeTriangleIntersection(plane, triangle, tolerance);
}
