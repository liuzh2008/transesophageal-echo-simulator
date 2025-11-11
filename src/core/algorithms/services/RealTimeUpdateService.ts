import { Vector3, Plane } from '../geometry/index';

/**
 * 交线结果接口
 */
export interface IntersectionResult {
  lines: Vector3[][];
  isValid: boolean;
  calculationTime: number;
  fromCache?: boolean;
  error?: string;
}

/**
 * 心脏模型接口
 */
export interface HeartModel {
  triangles: Vector3[][];
}

/**
 * 实时切面更新服务
 * 负责处理探头移动时的实时切面计算和更新
 */
export class RealTimeUpdateService {
  private cache: Map<string, IntersectionResult> = new Map();
  private lastResult: IntersectionResult | null = null;
  private cacheHits: number = 0;
  private cacheMisses: number = 0;
  private totalCalculations: number = 0;

  /**
   * 更新切面计算
   * @param probePosition 探头位置
   * @param probeDirection 探头方向
   * @param heartModel 心脏模型数据
   * @returns 切面计算结果
   */
  updateSection(
    probePosition: Vector3,
    probeDirection: Vector3,
    heartModel: HeartModel
  ): IntersectionResult {
    const startTime = performance.now();

    try {
      // 参数验证
      if (!this.isValidVector(probePosition) || !this.isValidVector(probeDirection)) {
        return {
          lines: [],
          isValid: false,
          calculationTime: 0,
          error: '无效的探头位置或方向'
        };
      }

      // 检查空模型
      if (!heartModel.triangles || heartModel.triangles.length === 0) {
        return {
          lines: [],
          isValid: false,
          calculationTime: 0,
          error: '心脏模型为空'
        };
      }

      // 检查缓存
      const cacheKey = this.generateCacheKey(probePosition, probeDirection, heartModel);
      const cachedResult = this.cache.get(cacheKey);
      if (cachedResult) {
        this.cacheHits++;
        return {
          ...cachedResult,
          fromCache: true,
          calculationTime: 0 // 缓存命中，计算时间为0
        };
      }
      this.cacheMisses++;

      // 创建切割平面
      const cuttingPlane = Plane.fromPointAndNormal(probePosition, probeDirection);

      // 计算平面与模型的交线
      const intersectionLines = this.calculateIntersectionLines(cuttingPlane, heartModel);

      const calculationTime = performance.now() - startTime;

      const result: IntersectionResult = {
        lines: intersectionLines,
        isValid: intersectionLines.length > 0,
        calculationTime
      };

      // 缓存结果（只缓存有效结果）
      if (result.isValid) {
        this.cache.set(cacheKey, result);
      }
      this.lastResult = result;
      this.totalCalculations++;

      return result;

    } catch (error) {
      const calculationTime = performance.now() - startTime;
      return {
        lines: [],
        isValid: false,
        calculationTime,
        error: error instanceof Error ? error.message : '未知错误'
      };
    }
  }

  /**
   * 计算平面与模型的交线
   * 使用增量计算优化：如果上次结果存在，优先检查可能相交的三角形
   */
  private calculateIntersectionLines(plane: Plane, heartModel: HeartModel): Vector3[][] {
    const intersectionLines: Vector3[][] = [];

    // 增量计算优化：如果存在上次结果，可以优化计算顺序
    const trianglesToCheck = this.optimizeTriangleOrder(heartModel.triangles);

    for (const triangle of trianglesToCheck) {
      const line = this.calculateTriangleIntersection(plane, triangle);
      if (line && line.length === 2) {
        intersectionLines.push(line);
      }
    }

    return intersectionLines;
  }

  /**
   * 计算平面与三角形的交线
   */
  private calculateTriangleIntersection(plane: Plane, triangle: Vector3[]): Vector3[] | null {
    if (triangle.length !== 3) {
      return null;
    }

    const [v0, v1, v2] = triangle;
    
    // 计算三个顶点到平面的距离
    const d0 = plane.distanceToPoint(v0);
    const d1 = plane.distanceToPoint(v1);
    const d2 = plane.distanceToPoint(v2);

    // 检查三角形是否与平面相交
    const hasIntersection = 
      (d0 * d1 < 0) || (d0 * d2 < 0) || (d1 * d2 < 0);

    if (!hasIntersection) {
      return null;
    }

    // 计算交点
    const intersectionPoints: Vector3[] = [];

    // 检查每条边与平面的交点
    const edges = [
      [v0, v1], [v1, v2], [v2, v0]
    ];

    for (const [start, end] of edges) {
      const intersection = this.calculateEdgeIntersection(plane, start, end);
      if (intersection) {
        intersectionPoints.push(intersection);
      }
    }

    // 应该有2个交点形成一条线段
    if (intersectionPoints.length === 2) {
      return intersectionPoints;
    }

    return null;
  }

  /**
   * 计算边与平面的交点
   */
  private calculateEdgeIntersection(plane: Plane, start: Vector3, end: Vector3): Vector3 | null {
    const d1 = plane.distanceToPoint(start);
    const d2 = plane.distanceToPoint(end);

    // 如果两点在平面同侧，则无交点
    if (d1 * d2 > 0) {
      return null;
    }

    // 如果一点在平面上，直接返回该点
    if (Math.abs(d1) < 1e-10) {
      return start.clone();
    }
    if (Math.abs(d2) < 1e-10) {
      return end.clone();
    }

    // 计算交点
    const t = -d1 / (d2 - d1);
    return new Vector3(
      start.x + t * (end.x - start.x),
      start.y + t * (end.y - start.y),
      start.z + t * (end.z - start.z)
    );
  }

  /**
   * 生成缓存键
   * 使用更精确的键生成策略，考虑位置和方向的精度
   */
  private generateCacheKey(probePosition: Vector3, probeDirection: Vector3, heartModel: HeartModel): string {
    // 使用固定精度减少浮点数精度问题
    const precision = 4;
    const positionKey = `${probePosition.x.toFixed(precision)},${probePosition.y.toFixed(precision)},${probePosition.z.toFixed(precision)}`;
    const directionKey = `${probeDirection.x.toFixed(precision)},${probeDirection.y.toFixed(precision)},${probeDirection.z.toFixed(precision)}`;
    const modelKey = heartModel.triangles.length.toString();
    
    return `${positionKey}|${directionKey}|${modelKey}`;
  }

  /**
   * 验证向量有效性
   */
  private isValidVector(vector: Vector3): boolean {
    return (
      !isNaN(vector.x) && !isNaN(vector.y) && !isNaN(vector.z) &&
      isFinite(vector.x) && isFinite(vector.y) && isFinite(vector.z)
    );
  }

  /**
   * 优化三角形检查顺序
   * 基于上次结果，优先检查可能相交的三角形
   */
  private optimizeTriangleOrder(triangles: Vector3[][]): Vector3[][] {
    // 简单实现：返回原始顺序
    // 未来可以基于空间分区或上次相交结果进行优化
    return triangles;
  }

  /**
   * 清空缓存
   */
  clearCache(): void {
    this.cache.clear();
    this.lastResult = null;
    this.cacheHits = 0;
    this.cacheMisses = 0;
    this.totalCalculations = 0;
  }

  /**
   * 获取上次计算结果
   */
  getLastResult(): IntersectionResult | null {
    return this.lastResult;
  }

  /**
   * 获取性能统计
   */
  getPerformanceStats(): {
    cacheHitRate: number;
    totalCalculations: number;
    cacheHits: number;
    cacheMisses: number;
  } {
    const totalRequests = this.cacheHits + this.cacheMisses;
    const cacheHitRate = totalRequests > 0 ? this.cacheHits / totalRequests : 0;
    
    return {
      cacheHitRate,
      totalCalculations: this.totalCalculations,
      cacheHits: this.cacheHits,
      cacheMisses: this.cacheMisses
    };
  }

  /**
   * 设置缓存大小限制
   */
  setCacheSizeLimit(limit: number): void {
    if (this.cache.size > limit) {
      // 简单的LRU策略：清空缓存
      this.clearCache();
    }
  }
}
