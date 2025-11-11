import { Vector3 } from './Vector3';

/**
 * 4x4矩阵类
 * 用于表示三维空间中的变换矩阵
 */
export class Matrix4 {
  public elements: number[];

  constructor() {
    // 初始化为单位矩阵
    this.elements = [
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1
    ];
  }

  /**
   * 设置为单位矩阵
   */
  identity(): Matrix4 {
    this.elements = [
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1
    ];
    return this;
  }

  /**
   * 创建平移矩阵
   */
  makeTranslation(x: number, y: number, z: number): Matrix4 {
    this.identity();
    this.elements[12] = x;
    this.elements[13] = y;
    this.elements[14] = z;
    return this;
  }

  /**
   * 创建绕X轴旋转矩阵
   */
  makeRotationX(theta: number): Matrix4 {
    const c = Math.cos(theta);
    const s = Math.sin(theta);
    
    this.elements = [
      1, 0,  0, 0,
      0, c, -s, 0,
      0, s,  c, 0,
      0, 0,  0, 1
    ];
    return this;
  }

  /**
   * 创建绕Y轴旋转矩阵
   */
  makeRotationY(theta: number): Matrix4 {
    const c = Math.cos(theta);
    const s = Math.sin(theta);
    
    this.elements = [
      c, 0, s, 0,
      0, 1, 0, 0,
     -s, 0, c, 0,
      0, 0, 0, 1
    ];
    return this;
  }

  /**
   * 创建绕Z轴旋转矩阵
   */
  makeRotationZ(theta: number): Matrix4 {
    const c = Math.cos(theta);
    const s = Math.sin(theta);
    
    this.elements = [
      c, -s, 0, 0,
      s,  c, 0, 0,
      0,  0, 1, 0,
      0,  0, 0, 1
    ];
    return this;
  }

  /**
   * 创建缩放矩阵
   */
  makeScale(x: number, y: number, z: number): Matrix4 {
    this.elements = [
      x, 0, 0, 0,
      0, y, 0, 0,
      0, 0, z, 0,
      0, 0, 0, 1
    ];
    return this;
  }

  /**
   * 矩阵乘法
   */
  multiply(m: Matrix4): Matrix4 {
    const result = new Matrix4();
    const a = this.elements;
    const b = m.elements;
    const out = result.elements;

    for (let i = 0; i < 4; i++) {
      for (let j = 0; j < 4; j++) {
        out[i * 4 + j] = 0;
        for (let k = 0; k < 4; k++) {
          out[i * 4 + j] += a[i * 4 + k] * b[k * 4 + j];
        }
      }
    }

    this.elements = out;
    return this;
  }

  /**
   * 向量变换
   * 将向量与矩阵相乘（假设向量为齐次坐标，w=1）
   */
  transformVector(v: Vector3): Vector3 {
    const e = this.elements;
    const x = v.x;
    const y = v.y;
    const z = v.z;
    const w = 1;

    const resultX = e[0] * x + e[4] * y + e[8] * z + e[12] * w;
    const resultY = e[1] * x + e[5] * y + e[9] * z + e[13] * w;
    const resultZ = e[2] * x + e[6] * y + e[10] * z + e[14] * w;
    const resultW = e[3] * x + e[7] * y + e[11] * z + e[15] * w;

    // 透视除法
    if (resultW !== 1 && resultW !== 0) {
      return new Vector3(resultX / resultW, resultY / resultW, resultZ / resultW);
    }

    return new Vector3(resultX, resultY, resultZ);
  }

  /**
   * 获取矩阵的逆矩阵
   */
  invert(): Matrix4 | null {
    const result = new Matrix4();
    const success = this.invertTo(result);
    if (success) {
      this.elements = result.elements;
      return this;
    }
    return null;
  }

  /**
   * 计算逆矩阵到目标矩阵
   */
  private invertTo(target: Matrix4): boolean {
    const te = this.elements;
    const me = target.elements;

    const n11 = te[0], n12 = te[4], n13 = te[8], n14 = te[12];
    const n21 = te[1], n22 = te[5], n23 = te[9], n24 = te[13];
    const n31 = te[2], n32 = te[6], n33 = te[10], n34 = te[14];
    const n41 = te[3], n42 = te[7], n43 = te[11], n44 = te[15];

    const t11 = n23 * n34 * n42 - n24 * n33 * n42 + n24 * n32 * n43 - n22 * n34 * n43 - n23 * n32 * n44 + n22 * n33 * n44;
    const t12 = n14 * n33 * n42 - n13 * n34 * n42 - n14 * n32 * n43 + n12 * n34 * n43 + n13 * n32 * n44 - n12 * n33 * n44;
    const t13 = n13 * n24 * n42 - n14 * n23 * n42 + n14 * n22 * n43 - n12 * n24 * n43 - n13 * n22 * n44 + n12 * n23 * n44;
    const t14 = n14 * n23 * n32 - n13 * n24 * n32 - n14 * n22 * n33 + n12 * n24 * n33 + n13 * n22 * n34 - n12 * n23 * n34;

    const det = n11 * t11 + n21 * t12 + n31 * t13 + n41 * t14;

    if (det === 0) {
      return false;
    }

    const detInv = 1 / det;

    me[0] = t11 * detInv;
    me[1] = (n24 * n33 * n41 - n23 * n34 * n41 - n24 * n31 * n43 + n21 * n34 * n43 + n23 * n31 * n44 - n21 * n33 * n44) * detInv;
    me[2] = (n22 * n34 * n41 - n24 * n32 * n41 + n24 * n31 * n42 - n21 * n34 * n42 - n22 * n31 * n44 + n21 * n32 * n44) * detInv;
    me[3] = (n23 * n32 * n41 - n22 * n33 * n41 - n23 * n31 * n42 + n21 * n33 * n42 + n22 * n31 * n43 - n21 * n32 * n43) * detInv;

    me[4] = t12 * detInv;
    me[5] = (n13 * n34 * n41 - n14 * n33 * n41 + n14 * n31 * n43 - n11 * n34 * n43 - n13 * n31 * n44 + n11 * n33 * n44) * detInv;
    me[6] = (n14 * n32 * n41 - n12 * n34 * n41 - n14 * n31 * n42 + n11 * n34 * n42 + n12 * n31 * n44 - n11 * n32 * n44) * detInv;
    me[7] = (n12 * n33 * n41 - n13 * n32 * n41 + n13 * n31 * n42 - n11 * n33 * n42 - n12 * n31 * n43 + n11 * n32 * n43) * detInv;

    me[8] = t13 * detInv;
    me[9] = (n14 * n23 * n41 - n13 * n24 * n41 - n14 * n21 * n43 + n11 * n24 * n43 + n13 * n21 * n44 - n11 * n23 * n44) * detInv;
    me[10] = (n12 * n24 * n41 - n14 * n22 * n41 + n14 * n21 * n42 - n11 * n24 * n42 - n12 * n21 * n44 + n11 * n22 * n44) * detInv;
    me[11] = (n13 * n22 * n41 - n12 * n23 * n41 - n13 * n21 * n42 + n11 * n23 * n42 + n12 * n21 * n43 - n11 * n22 * n43) * detInv;

    me[12] = t14 * detInv;
    me[13] = (n13 * n24 * n31 - n14 * n23 * n31 + n14 * n21 * n33 - n11 * n24 * n33 - n13 * n21 * n34 + n11 * n23 * n34) * detInv;
    me[14] = (n14 * n22 * n31 - n12 * n24 * n31 - n14 * n21 * n32 + n11 * n24 * n32 + n12 * n21 * n34 - n11 * n22 * n34) * detInv;
    me[15] = (n12 * n23 * n31 - n13 * n22 * n31 + n13 * n21 * n32 - n11 * n23 * n32 - n12 * n21 * n33 + n11 * n22 * n33) * detInv;

    return true;
  }

  /**
   * 获取转置矩阵
   */
  transpose(): Matrix4 {
    const result = new Matrix4();
    const te = this.elements;
    const me = result.elements;

    for (let i = 0; i < 4; i++) {
      for (let j = 0; j < 4; j++) {
        me[i * 4 + j] = te[j * 4 + i];
      }
    }

    this.elements = me;
    return this;
  }

  /**
   * 克隆矩阵
   */
  clone(): Matrix4 {
    const result = new Matrix4();
    result.elements = [...this.elements];
    return result;
  }

  /**
   * 矩阵相等判断
   */
  equals(m: Matrix4, tolerance: number = 1e-10): boolean {
    for (let i = 0; i < 16; i++) {
      if (Math.abs(this.elements[i] - m.elements[i]) > tolerance) {
        return false;
      }
    }
    return true;
  }

  /**
   * 从数组创建矩阵
   */
  static fromArray(array: number[]): Matrix4 {
    const matrix = new Matrix4();
    matrix.elements = [...array];
    return matrix;
  }

  /**
   * 创建视图矩阵（相机矩阵）
   */
  static makeLookAt(eye: Vector3, target: Vector3, up: Vector3): Matrix4 {
    const z = eye.subtract(target).normalize();
    const x = up.cross(z).normalize();
    const y = z.cross(x).normalize();

    const matrix = new Matrix4();
    matrix.elements = [
      x.x, x.y, x.z, -x.dot(eye),
      y.x, y.y, y.z, -y.dot(eye),
      z.x, z.y, z.z, -z.dot(eye),
      0,   0,   0,   1
    ];

    return matrix;
  }

  /**
   * 创建透视投影矩阵
   */
  static makePerspective(fov: number, aspect: number, near: number, far: number): Matrix4 {
    const f = 1.0 / Math.tan(fov / 2);
    const nf = 1 / (near - far);

    const matrix = new Matrix4();
    matrix.elements = [
      f / aspect, 0, 0, 0,
      0, f, 0, 0,
      0, 0, (far + near) * nf, 2 * far * near * nf,
      0, 0, -1, 0
    ];

    return matrix;
  }
}
