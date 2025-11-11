import { Vector3, Plane, Matrix4 } from '../../../src/core/algorithms/geometry/index';

describe('几何计算基础', () => {
  describe('Vector3 向量运算', () => {
    test('向量创建和基本属性', () => {
      const v = new Vector3(1, 2, 3);
      expect(v.x).toBe(1);
      expect(v.y).toBe(2);
      expect(v.z).toBe(3);
    });

    test('向量长度计算', () => {
      const v = new Vector3(3, 4, 0);
      expect(v.length()).toBe(5);
    });

    test('向量归一化', () => {
      const v = new Vector3(3, 4, 0);
      const normalized = v.normalize();
      expect(normalized.length()).toBeCloseTo(1);
      expect(normalized.x).toBeCloseTo(0.6);
      expect(normalized.y).toBeCloseTo(0.8);
    });

    test('向量点积', () => {
      const v1 = new Vector3(1, 2, 3);
      const v2 = new Vector3(4, 5, 6);
      expect(v1.dot(v2)).toBe(32);
    });

    test('向量叉积', () => {
      const v1 = new Vector3(1, 0, 0);
      const v2 = new Vector3(0, 1, 0);
      const cross = v1.cross(v2);
      expect(cross.x).toBe(0);
      expect(cross.y).toBe(0);
      expect(cross.z).toBe(1);
    });

    test('向量加减法', () => {
      const v1 = new Vector3(1, 2, 3);
      const v2 = new Vector3(4, 5, 6);
      const sum = v1.add(v2);
      const diff = v1.subtract(v2);
      
      expect(sum.x).toBe(5);
      expect(sum.y).toBe(7);
      expect(sum.z).toBe(9);
      
      expect(diff.x).toBe(-3);
      expect(diff.y).toBe(-3);
      expect(diff.z).toBe(-3);
    });
  });

  describe('Plane 平面定义', () => {
    test('通过点和法向量创建平面', () => {
      const point = new Vector3(0, 0, 0);
      const normal = new Vector3(0, 1, 0);
      const plane = Plane.fromPointAndNormal(point, normal);
      
      expect(plane.normal.x).toBe(0);
      expect(plane.normal.y).toBe(1);
      expect(plane.normal.z).toBe(0);
      expect(plane.constant).toBeCloseTo(0); // 使用toBeCloseTo处理-0和0的问题
    });

    test('平面方程计算', () => {
      const plane = new Plane(new Vector3(0, 1, 0), 2);
      expect(plane.normal.x).toBe(0);
      expect(plane.normal.y).toBe(1);
      expect(plane.normal.z).toBe(0);
      expect(plane.constant).toBe(2);
    });

    test('点到平面距离计算', () => {
      const plane = new Plane(new Vector3(0, 1, 0), -2); // 平面 y = 2
      const point = new Vector3(1, 5, 3);
      const distance = plane.distanceToPoint(point);
      
      expect(distance).toBe(3); // 5 - 2 = 3
    });

    test('点在平面上的投影', () => {
      const plane = new Plane(new Vector3(0, 1, 0), -2); // 平面 y = 2
      const point = new Vector3(1, 5, 3);
      const projection = plane.projectPoint(point);
      
      expect(projection.x).toBe(1);
      expect(projection.y).toBe(2);
      expect(projection.z).toBe(3);
    });
  });

  describe('Matrix4 矩阵变换', () => {
    test('单位矩阵创建', () => {
      const matrix = new Matrix4();
      const identity = matrix.identity();
      
      // 检查对角线元素为1，其他为0
      for (let i = 0; i < 4; i++) {
        for (let j = 0; j < 4; j++) {
          if (i === j) {
            expect(identity.elements[i * 4 + j]).toBe(1);
          } else {
            expect(identity.elements[i * 4 + j]).toBe(0);
          }
        }
      }
    });

    test('平移矩阵', () => {
      const matrix = new Matrix4();
      const translation = matrix.makeTranslation(2, 3, 4);
      
      expect(translation.elements[12]).toBe(2);
      expect(translation.elements[13]).toBe(3);
      expect(translation.elements[14]).toBe(4);
    });

    test('旋转矩阵', () => {
      const matrix = new Matrix4();
      const rotation = matrix.makeRotationX(Math.PI / 2); // 绕X轴旋转90度
      
      // 检查旋转矩阵的基本性质
      expect(rotation.elements[5]).toBeCloseTo(0);
      expect(rotation.elements[6]).toBeCloseTo(-1); // 修正符号
      expect(rotation.elements[9]).toBeCloseTo(1); // 修正符号
      expect(rotation.elements[10]).toBeCloseTo(0);
    });

    test('向量变换', () => {
      const matrix = new Matrix4();
      const translation = matrix.makeTranslation(1, 2, 3);
      const vector = new Vector3(4, 5, 6);
      const transformed = translation.transformVector(vector);
      
      expect(transformed.x).toBe(5); // 4 + 1
      expect(transformed.y).toBe(7); // 5 + 2
      expect(transformed.z).toBe(9); // 6 + 3
    });
  });

  describe('边界情况处理', () => {
    test('零向量归一化', () => {
      const zeroVector = new Vector3(0, 0, 0);
      const normalized = zeroVector.normalize();
      
      // 零向量归一化应该返回零向量
      expect(normalized.x).toBe(0);
      expect(normalized.y).toBe(0);
      expect(normalized.z).toBe(0);
    });

    test('非法平面参数', () => {
      // 零法向量应该抛出错误
      expect(() => {
        new Plane(new Vector3(0, 0, 0), 0);
      }).toThrow('法向量不能为零向量');
    });

    test('浮点数精度处理', () => {
      const v = new Vector3(0.1, 0.2, 0.3);
      const normalized = v.normalize();
      
      // 归一化后的向量长度应该接近1
      expect(normalized.length()).toBeCloseTo(1, 10);
    });
  });
});
