/**
 * 缩放功能集成测试
 * 测试缩放管理器、上下文和3D场景的集成
 */

import { createZoomManager, zoomValueToCameraDistance, cameraDistanceToZoomValue } from '../../src/core/zoom/ZoomManager';

describe('缩放功能集成测试', () => {
  describe('缩放管理器', () => {
    test('创建缩放管理器', () => {
      const zoomManager = createZoomManager();
      const state = zoomManager.getState();
      
      expect(state.value).toBe(50);
      expect(state.min).toBe(0);
      expect(state.max).toBe(100);
      expect(state.step).toBe(1);
    });

    test('设置有效缩放值', () => {
      const zoomManager = createZoomManager();
      zoomManager.setZoom(75);
      
      const state = zoomManager.getState();
      expect(state.value).toBe(75);
    });

    test('拒绝无效缩放值', () => {
      const zoomManager = createZoomManager();
      const originalState = zoomManager.getState();
      
      // 尝试设置超出范围的缩放值
      zoomManager.setZoom(150);
      
      const state = zoomManager.getState();
      expect(state.value).toBe(originalState.value); // 值应该保持不变
    });

    test('重置缩放值', () => {
      const zoomManager = createZoomManager();
      zoomManager.setZoom(80);
      zoomManager.reset();
      
      const state = zoomManager.getState();
      expect(state.value).toBe(50); // 重置到默认值
    });
  });

  describe('缩放值转换工具', () => {
    test('缩放值转相机距离', () => {
      // 缩放值0对应最远距离10
      expect(zoomValueToCameraDistance(0)).toBeCloseTo(10);
      
      // 缩放值50对应中间距离6
      expect(zoomValueToCameraDistance(50)).toBeCloseTo(6);
      
      // 缩放值100对应最近距离2
      expect(zoomValueToCameraDistance(100)).toBeCloseTo(2);
    });

    test('相机距离转缩放值', () => {
      // 距离10对应缩放值0
      expect(cameraDistanceToZoomValue(10)).toBeCloseTo(0);
      
      // 距离6对应缩放值50
      expect(cameraDistanceToZoomValue(6)).toBeCloseTo(50);
      
      // 距离2对应缩放值100
      expect(cameraDistanceToZoomValue(2)).toBeCloseTo(100);
    });

    test('转换函数互为逆运算', () => {
      const testValues = [0, 25, 50, 75, 100];
      
      testValues.forEach(zoomValue => {
        const distance = zoomValueToCameraDistance(zoomValue);
        const convertedZoomValue = cameraDistanceToZoomValue(distance);
        expect(convertedZoomValue).toBeCloseTo(zoomValue);
      });
    });
  });

  describe('缩放状态验证', () => {
    test('缩放值范围验证', () => {
      const zoomManager = createZoomManager();
      
      expect(zoomManager.isValidZoom(0)).toBe(true);
      expect(zoomManager.isValidZoom(50)).toBe(true);
      expect(zoomManager.isValidZoom(100)).toBe(true);
      expect(zoomManager.isValidZoom(-10)).toBe(false);
      expect(zoomManager.isValidZoom(150)).toBe(false);
    });

    test('自定义缩放范围', () => {
      const zoomManager = createZoomManager({ min: 10, max: 90 });
      
      expect(zoomManager.isValidZoom(10)).toBe(true);
      expect(zoomManager.isValidZoom(90)).toBe(true);
      expect(zoomManager.isValidZoom(5)).toBe(false);
      expect(zoomManager.isValidZoom(95)).toBe(false);
    });
  });
});
