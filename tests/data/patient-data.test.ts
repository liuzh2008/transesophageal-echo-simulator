/**
 * 病人数据管理测试用例
 * 按照TDD红-绿-重构流程实现
 * 
 * 用户故事：数据管理
 * 作为开发人员
 * 我希望实现可靠的数据管理功能
 * 以便能够有效管理病人数据和模型文件
 * 
 * 验收标准：
 * - 病人数据模型设计完成
 * - 本地存储方案实现并测试
 * - 模型文件管理功能可用
 * - 数据持久化功能正常
 * - 数据验证和错误处理完善
 * 
 * 测试评价：
 * - 测试覆盖了数据管理功能的核心需求
 * - 每个测试用例都有明确的验证目标
 * - 测试之间相互独立，便于维护
 * - 使用了适当的断言来验证功能正确性
 * - 模拟了localStorage环境，确保测试在Node.js中运行
 * 
 * 改进建议：
 * - 可以添加更多边界条件测试
 * - 考虑添加错误处理测试
 * - 可以添加性能测试来验证数据操作性能
 * - 考虑添加集成测试来验证数据流
 */

// 模拟localStorage用于Node.js环境测试
const localStorageMock = {
  store: {} as Record<string, string>,
  getItem(key: string) {
    return this.store[key] || null;
  },
  setItem(key: string, value: string) {
    this.store[key] = value;
  },
  removeItem(key: string) {
    delete this.store[key];
  },
  clear() {
    this.store = {};
  },
  key(index: number) {
    return Object.keys(this.store)[index] || null;
  },
  get length() {
    return Object.keys(this.store).length;
  }
};

// 设置全局localStorage
(global as any).localStorage = localStorageMock;

describe('病人数据管理 - 绿阶段', () => {
  test('病人数据模型创建', () => {
    // 绿阶段：这个测试现在应该通过
    const PatientData = require('../../src/data/models/PatientData').default;
    const patient = new PatientData({ name: '张三', age: 45 });
    expect(patient).toBeDefined();
    expect(patient.name).toBe('张三');
    expect(patient.age).toBe(45);
  });

  test('病人数据验证规则', () => {
    // 绿阶段：这个测试现在应该通过
    const PatientData = require('../../src/data/models/PatientData').default;
    const patient = new PatientData({ name: '', age: -5 });
    const validation = patient.isValid();
    expect(validation.isValid).toBe(false);
    expect(validation.errors.length).toBeGreaterThan(0);
  });

  test('本地存储操作', () => {
    // 绿阶段：这个测试现在应该通过
    const LocalStorageService = require('../../src/data/services/LocalStorageService').default;
    const storage = new LocalStorageService();
    const testData = { name: '测试数据' };
    
    const saveResult = storage.save('test-key', testData);
    expect(saveResult.success).toBe(true);
    
    const loadResult = storage.load('test-key');
    expect(loadResult.success).toBe(true);
    expect(loadResult.data).toEqual(testData);
  });

  test('数据持久化', () => {
    // 绿阶段：这个测试现在应该通过
    const DataManager = require('../../src/data/DataManager').default;
    const manager = new DataManager();
    const patientData = { name: '李四', age: 35, diagnosis: '心脏检查' };
    
    const saveResult = manager.savePatient(patientData);
    expect(saveResult.success).toBe(true);
    
    const loadResult = manager.loadPatient('李四');
    expect(loadResult.success).toBe(true);
    expect(loadResult.data?.data).toEqual(patientData);
  });
});
