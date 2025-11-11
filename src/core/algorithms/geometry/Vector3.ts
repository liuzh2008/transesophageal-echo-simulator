/**
 * 三维向量类
 * 用于表示三维空间中的向量和点
 * 提供向量基本运算和几何计算功能
 * 
 * @class Vector3
 * @param {number} x - X轴分量，默认为0
 * @param {number} y - Y轴分量，默认为0
 * @param {number} z - Z轴分量，默认为0
 */
export class Vector3 {
  /**
   * 创建三维向量实例
   * @param {number} x - X轴分量，默认为0
   * @param {number} y - Y轴分量，默认为0
   * @param {number} z - Z轴分量，默认为0
   */
  constructor(
    public x: number = 0,
    public y: number = 0,
    public z: number = 0
  ) {}

  /**
   * 计算向量长度（模长）
   * @returns {number} 向量的长度
   * @example
   * const v = new Vector3(3, 4, 0);
   * const len = v.length(); // 5
   */
  length(): number {
    return Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z);
  }

  /**
   * 向量归一化
   * 返回单位向量
   */
  normalize(): Vector3 {
    const len = this.length();
    if (len === 0) {
      return new Vector3(0, 0, 0);
    }
    return new Vector3(this.x / len, this.y / len, this.z / len);
  }

  /**
   * 向量点积
   */
  dot(v: Vector3): number {
    return this.x * v.x + this.y * v.y + this.z * v.z;
  }

  /**
   * 向量叉积
   */
  cross(v: Vector3): Vector3 {
    return new Vector3(
      this.y * v.z - this.z * v.y,
      this.z * v.x - this.x * v.z,
      this.x * v.y - this.y * v.x
    );
  }

  /**
   * 向量加法
   */
  add(v: Vector3): Vector3 {
    return new Vector3(this.x + v.x, this.y + v.y, this.z + v.z);
  }

  /**
   * 向量减法
   */
  subtract(v: Vector3): Vector3 {
    return new Vector3(this.x - v.x, this.y - v.y, this.z - v.z);
  }

  /**
   * 向量数乘
   */
  multiplyScalar(scalar: number): Vector3 {
    return new Vector3(this.x * scalar, this.y * scalar, this.z * scalar);
  }

  /**
   * 向量相等判断
   */
  equals(v: Vector3, tolerance: number = 1e-10): boolean {
    return (
      Math.abs(this.x - v.x) < tolerance &&
      Math.abs(this.y - v.y) < tolerance &&
      Math.abs(this.z - v.z) < tolerance
    );
  }

  /**
   * 克隆向量
   */
  clone(): Vector3 {
    return new Vector3(this.x, this.y, this.z);
  }

  /**
   * 转换为数组
   */
  toArray(): [number, number, number] {
    return [this.x, this.y, this.z];
  }

  /**
   * 从数组创建向量
   */
  static fromArray(array: [number, number, number]): Vector3 {
    return new Vector3(array[0], array[1], array[2]);
  }

  /**
   * 零向量
   */
  static zero(): Vector3 {
    return new Vector3(0, 0, 0);
  }

  /**
   * 单位向量
   */
  static unitX(): Vector3 {
    return new Vector3(1, 0, 0);
  }

  static unitY(): Vector3 {
    return new Vector3(0, 1, 0);
  }

  static unitZ(): Vector3 {
    return new Vector3(0, 0, 1);
  }
}
