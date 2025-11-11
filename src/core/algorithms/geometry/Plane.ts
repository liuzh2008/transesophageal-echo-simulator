import { Vector3 } from './Vector3';

/**
 * 平面类
 * 表示三维空间中的平面，使用法向量和常数项定义
 * 平面方程: normal.x * x + normal.y * y + normal.z * z + constant = 0
 */
export class Plane {
  public normal: Vector3;
  public constant: number;

  constructor(
    normal: Vector3,
    constant: number = 0
  ) {
    // 验证法向量不能为零向量
    if (normal.length() === 0) {
      throw new Error('法向量不能为零向量');
    }
    
    // 确保法向量是单位向量
    this.normal = normal.normalize();
    this.constant = constant;
  }

  /**
   * 通过点和法向量创建平面
   */
  static fromPointAndNormal(point: Vector3, normal: Vector3): Plane {
    const normalizedNormal = normal.normalize();
    const constant = -normalizedNormal.dot(point);
    return new Plane(normalizedNormal, constant);
  }

  /**
   * 通过三个点创建平面
   */
  static fromPoints(point1: Vector3, point2: Vector3, point3: Vector3): Plane {
    const v1 = point2.subtract(point1);
    const v2 = point3.subtract(point1);
    const normal = v1.cross(v2).normalize();
    return Plane.fromPointAndNormal(point1, normal);
  }

  /**
   * 计算点到平面的距离
   * 有符号距离，正负表示点在法向量的哪一侧
   */
  distanceToPoint(point: Vector3): number {
    return this.normal.dot(point) + this.constant;
  }

  /**
   * 计算点在平面上的投影
   */
  projectPoint(point: Vector3): Vector3 {
    const distance = this.distanceToPoint(point);
    return point.subtract(this.normal.multiplyScalar(distance));
  }

  /**
   * 判断点是否在平面上（考虑浮点数精度）
   */
  containsPoint(point: Vector3, tolerance: number = 1e-10): boolean {
    return Math.abs(this.distanceToPoint(point)) < tolerance;
  }

  /**
   * 获取平面上的任意一点
   */
  getAnyPoint(): Vector3 {
    if (Math.abs(this.normal.x) > 1e-10) {
      return new Vector3(-this.constant / this.normal.x, 0, 0);
    } else if (Math.abs(this.normal.y) > 1e-10) {
      return new Vector3(0, -this.constant / this.normal.y, 0);
    } else {
      return new Vector3(0, 0, -this.constant / this.normal.z);
    }
  }

  /**
   * 平面相交计算
   * 计算两个平面的交线
   */
  intersectPlane(other: Plane): { point: Vector3; direction: Vector3 } | null {
    const direction = this.normal.cross(other.normal);
    
    // 如果法向量平行，则平面平行或重合
    if (direction.length() < 1e-10) {
      return null;
    }
    
    // 计算交线上的一个点
    // 使用三个平面的交点：当前平面、另一个平面、以及一个辅助平面
    const tempNormal = this.normal.cross(direction).normalize();
    const tempPlane = new Plane(tempNormal, 0);
    
    // 解线性方程组
    const A = [
      [this.normal.x, this.normal.y, this.normal.z],
      [other.normal.x, other.normal.y, other.normal.z],
      [tempNormal.x, tempNormal.y, tempNormal.z]
    ];
    
    const b = [-this.constant, -other.constant, 0];
    
    // 使用克莱姆法则求解
    const detA = this.determinant3x3(A);
    if (Math.abs(detA) < 1e-10) {
      return null;
    }
    
    const point = new Vector3(
      this.determinant3x3([
        [b[0], A[0][1], A[0][2]],
        [b[1], A[1][1], A[1][2]],
        [b[2], A[2][1], A[2][2]]
      ]) / detA,
      this.determinant3x3([
        [A[0][0], b[0], A[0][2]],
        [A[1][0], b[1], A[1][2]],
        [A[2][0], b[2], A[2][2]]
      ]) / detA,
      this.determinant3x3([
        [A[0][0], A[0][1], b[0]],
        [A[1][0], A[1][1], b[1]],
        [A[2][0], A[2][1], b[2]]
      ]) / detA
    );
    
    return {
      point,
      direction: direction.normalize()
    };
  }

  /**
   * 计算3x3矩阵的行列式
   */
  private determinant3x3(matrix: number[][]): number {
    return matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) -
           matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0]) +
           matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]);
  }

  /**
   * 克隆平面
   */
  clone(): Plane {
    return new Plane(this.normal.clone(), this.constant);
  }

  /**
   * 平面相等判断
   */
  equals(other: Plane, tolerance: number = 1e-10): boolean {
    return (
      this.normal.equals(other.normal, tolerance) &&
      Math.abs(this.constant - other.constant) < tolerance
    );
  }
}
