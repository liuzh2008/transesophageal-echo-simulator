import { ModelStore } from '../../../src/data/models/ModelStore';
import { STLModel } from '../../../src/core/types/STLModel';

/**
 * ModelStore状态管理测试
 * 
 * @description 测试模型加载状态管理功能
 * @group unit
 * @group managers
 * @group model-store
 */
describe('ModelStore状态管理', () => {
  let modelStore: ModelStore;

  beforeEach(() => {
    modelStore = new ModelStore();
  });

  /**
   * 测试初始状态
   */
  it('应该具有正确的初始状态', () => {
    expect(modelStore.getState()).toEqual({
      isLoading: false,
      currentModel: null,
      error: null,
      progress: 0
    });
  });

  /**
   * 测试开始加载状态
   */
  it('应该能够开始加载状态', () => {
    modelStore.startLoading();
    
    expect(modelStore.getState()).toEqual({
      isLoading: true,
      currentModel: null,
      error: null,
      progress: 0
    });
  });

  /**
   * 测试加载成功状态
   */
  it('应该能够设置加载成功状态', () => {
    const mockModel: STLModel = {
      vertices: [0, 0, 0, 1, 0, 0, 0, 1, 0],
      normals: [0, 0, 1, 0, 0, 1, 0, 0, 1],
      faces: [0, 1, 2]
    };

    modelStore.setSuccess(mockModel);
    
    expect(modelStore.getState()).toEqual({
      isLoading: false,
      currentModel: mockModel,
      error: null,
      progress: 100
    });
  });

  /**
   * 测试加载失败状态
   */
  it('应该能够设置加载失败状态', () => {
    const errorMessage = '文件解析失败';
    
    modelStore.setError(errorMessage);
    
    expect(modelStore.getState()).toEqual({
      isLoading: false,
      currentModel: null,
      error: errorMessage,
      progress: 0
    });
  });

  /**
   * 测试更新进度状态
   */
  it('应该能够更新加载进度', () => {
    modelStore.startLoading();
    modelStore.updateProgress(50);
    
    expect(modelStore.getState()).toEqual({
      isLoading: true,
      currentModel: null,
      error: null,
      progress: 50
    });
  });

  /**
   * 测试重置状态
   */
  it('应该能够重置状态', () => {
    // 先设置一些状态
    modelStore.startLoading();
    modelStore.updateProgress(75);
    
    // 然后重置
    modelStore.reset();
    
    expect(modelStore.getState()).toEqual({
      isLoading: false,
      currentModel: null,
      error: null,
      progress: 0
    });
  });

  /**
   * 测试状态订阅机制
   */
  it('应该支持状态订阅和取消订阅', () => {
    const mockListener = jest.fn();
    
    // 订阅状态变化
    const unsubscribe = modelStore.subscribe(mockListener);
    
    // 触发状态变化
    modelStore.startLoading();
    
    // 验证监听器被调用（初始状态 + 状态变化）
    expect(mockListener).toHaveBeenCalledTimes(2);
    expect(mockListener).toHaveBeenLastCalledWith({
      isLoading: true,
      currentModel: null,
      error: null,
      progress: 0
    });
    
    // 取消订阅
    unsubscribe();
    
    // 再次触发状态变化
    modelStore.setError('test error');
    
    // 验证监听器没有被再次调用
    expect(mockListener).toHaveBeenCalledTimes(2);
  });

  /**
   * 测试状态变化历史记录
   */
  it('应该记录状态变化历史', () => {
    modelStore.startLoading();
    modelStore.updateProgress(25);
    modelStore.updateProgress(50);
    modelStore.setError('加载失败');
    
    const history = modelStore.getHistory();
    
    // 历史记录包括初始状态 + 4个状态变化
    expect(history).toHaveLength(5);
    expect(history[1].isLoading).toBe(true);
    expect(history[1].progress).toBe(0);
    expect(history[2].progress).toBe(25);
    expect(history[3].progress).toBe(50);
    expect(history[4].error).toBe('加载失败');
  });

  /**
   * 测试状态验证
   */
  it('应该验证状态数据的有效性', () => {
    // 测试进度值边界
    modelStore.updateProgress(-10); // 应该被限制为0
    expect(modelStore.getState().progress).toBe(0);
    
    modelStore.updateProgress(150); // 应该被限制为100
    expect(modelStore.getState().progress).toBe(100);
    
    modelStore.updateProgress(75); // 正常值
    expect(modelStore.getState().progress).toBe(75);
  });

  /**
   * 测试状态序列化
   */
  it('应该能够序列化和反序列化状态', () => {
    const mockModel: STLModel = {
      vertices: [0, 0, 0, 1, 0, 0, 0, 1, 0],
      normals: [0, 0, 1, 0, 0, 1, 0, 0, 1],
      faces: [0, 1, 2]
    };
    
    modelStore.setSuccess(mockModel);
    
    const serialized = modelStore.serialize();
    const newModelStore = new ModelStore();
    newModelStore.deserialize(serialized);
    
    expect(newModelStore.getState()).toEqual(modelStore.getState());
  });

  /**
   * 测试多个监听器同时工作
   */
  it('应该支持多个监听器同时工作', () => {
    const mockListener1 = jest.fn();
    const mockListener2 = jest.fn();
    
    // 订阅两个监听器
    const unsubscribe1 = modelStore.subscribe(mockListener1);
    const unsubscribe2 = modelStore.subscribe(mockListener2);
    
    // 触发状态变化
    modelStore.startLoading();
    
    // 验证两个监听器都被调用
    expect(mockListener1).toHaveBeenCalledTimes(2); // 初始状态 + 状态变化
    expect(mockListener2).toHaveBeenCalledTimes(2);
    
    // 取消一个监听器
    unsubscribe1();
    
    // 再次触发状态变化
    modelStore.updateProgress(50);
    
    // 验证只有第二个监听器被调用
    expect(mockListener1).toHaveBeenCalledTimes(2);
    expect(mockListener2).toHaveBeenCalledTimes(3);
    
    // 清理
    unsubscribe2();
  });

  /**
   * 测试无效序列化数据处理
   */
  it('应该正确处理无效的序列化数据', () => {
    const invalidData = 'invalid json data';
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    // 应该不会抛出错误，而是保持当前状态
    expect(() => {
      modelStore.deserialize(invalidData);
    }).not.toThrow();
    
    // 状态应该保持不变
    expect(modelStore.getState()).toEqual({
      isLoading: false,
      currentModel: null,
      error: null,
      progress: 0
    });
    
    // 恢复console.error
    consoleSpy.mockRestore();
  });

  /**
   * 测试状态隔离性
   */
  it('应该确保不同实例的状态隔离', () => {
    const store1 = new ModelStore();
    const store2 = new ModelStore();
    
    // 修改store1的状态
    store1.startLoading();
    store1.updateProgress(50);
    
    // store2的状态应该保持不变
    expect(store2.getState()).toEqual({
      isLoading: false,
      currentModel: null,
      error: null,
      progress: 0
    });
    
    // store1的状态应该正确更新
    expect(store1.getState()).toEqual({
      isLoading: true,
      currentModel: null,
      error: null,
      progress: 50
    });
  });

  /**
   * 测试状态深拷贝
   */
  it('应该确保状态返回的是深拷贝', () => {
    const mockModel: STLModel = {
      vertices: [0, 0, 0, 1, 0, 0, 0, 1, 0],
      normals: [0, 0, 1, 0, 0, 1, 0, 0, 1],
      faces: [0, 1, 2]
    };
    
    modelStore.setSuccess(mockModel);
    
    const state1 = modelStore.getState();
    const state2 = modelStore.getState();
    
    // 修改state1中的模型数据
    if (state1.currentModel) {
      state1.currentModel.vertices[0] = 999;
    }
    
    // state2中的模型数据应该保持不变
    expect(state2.currentModel?.vertices[0]).toBe(0);
  });
});
