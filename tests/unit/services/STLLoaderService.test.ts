import { STLLoaderService } from '../../../src/core/services/STLLoaderService';
import * as THREE from 'three';

describe('STLLoaderService', () => {
  let stlLoaderService: STLLoaderService;

  beforeEach(() => {
    stlLoaderService = new STLLoaderService();
  });

  describe('parseSTLBuffer', () => {
    it('应该正确解析有效的STL二进制数据', () => {
      // 红：编写测试用例
      // 这里我们创建一个简单的STL文件头来测试
      const mockSTLBuffer = createMockSTLBuffer();
      
      // 绿：调用解析方法
      const mesh = stlLoaderService.parseSTLBuffer(mockSTLBuffer);
      
      // 验证结果
      expect(mesh).toBeInstanceOf(THREE.Mesh);
      expect(mesh.geometry).toBeInstanceOf(THREE.BufferGeometry);
      expect(mesh.material).toBeInstanceOf(THREE.Material);
    });

    it('应该对无效的STL数据抛出错误', () => {
      // 红：测试错误处理
      const invalidBuffer = new ArrayBuffer(0);
      
      // 验证抛出错误
      expect(() => {
        stlLoaderService.parseSTLBuffer(invalidBuffer);
      }).toThrow('无效的STL文件格式');
    });

    it('应该处理空的STL文件', () => {
      // 红：测试边界情况
      const emptyBuffer = new ArrayBuffer(84); // STL文件头大小
      
      // 空的STL文件应该能够被解析，但会创建空的几何体
      const mesh = stlLoaderService.parseSTLBuffer(emptyBuffer);
      
      expect(mesh).toBeInstanceOf(THREE.Mesh);
      expect(mesh.geometry).toBeInstanceOf(THREE.BufferGeometry);
    });
  });

  describe('validateSTLFile', () => {
    it('应该验证有效的STL文件', () => {
      // 红：测试文件验证
      const validFile = new File(['test data'], 'test.stl', { type: 'application/sla' });
      
      const isValid = stlLoaderService.validateSTLFile(validFile);
      
      expect(isValid).toBe(true);
    });

    it('应该拒绝非STL文件类型', () => {
      // 红：测试无效文件类型
      const invalidFile = new File([''], 'test.txt', { type: 'text/plain' });
      
      const isValid = stlLoaderService.validateSTLFile(invalidFile);
      
      expect(isValid).toBe(false);
    });

    it('应该拒绝过大的文件', () => {
      // 红：测试文件大小限制
      const largeFile = new File([new ArrayBuffer(1024 * 1024 * 101)], 'large.stl', { 
        type: 'application/sla' 
      });
      
      const isValid = stlLoaderService.validateSTLFile(largeFile);
      
      expect(isValid).toBe(false);
    });
  });
});

/**
 * 创建模拟的STL二进制数据用于测试
 */
function createMockSTLBuffer(): ArrayBuffer {
  // 创建一个简单的STL文件结构
  // STL文件头：80字节 + 三角形数量：4字节
  const buffer = new ArrayBuffer(84);
  const view = new DataView(buffer);
  
  // 写入文件头（80字节的空数据）
  for (let i = 0; i < 80; i++) {
    view.setUint8(i, 0);
  }
  
  // 写入三角形数量为0
  view.setUint32(80, 0, true);
  
  return buffer;
}
