/**
 * 本地存储服务类
 * 
 * 提供浏览器localStorage的封装，包含完整的错误处理和类型安全
 * 
 * @class LocalStorageService
 * @author 食道超声模拟软件开发团队
 * @version 1.0.0
 * @since 2025-11-08
 * 
 * @example
 * // 创建存储服务实例
 * const storage = new LocalStorageService();
 * 
 * // 保存数据
 * const saveResult = storage.save('user-data', { name: '张三', age: 45 });
 * if (saveResult.success) {
 *   console.log('数据保存成功');
 * }
 * 
 * // 加载数据
 * const loadResult = storage.load<{ name: string, age: number }>('user-data');
 * if (loadResult.success) {
 *   console.log('加载的数据:', loadResult.data);
 * }
 */

/**
 * 存储操作结果接口
 * 
 * @interface StorageResult
 * @template T - 数据类型
 * @property {boolean} success - 操作是否成功
 * @property {T} [data] - 返回的数据（仅load方法）
 * @property {string} [error] - 错误信息
 */
export interface StorageResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * 本地存储服务类
 * 
 * 提供localStorage的封装，包含错误处理、类型安全和数据验证
 * 
 * @class LocalStorageService
 */
export default class LocalStorageService {
  /**
   * 保存数据到本地存储
   * 
   * 自动进行JSON序列化，包含完整的错误处理和键验证
   * 
   * @method save
   * @template T - 数据类型
   * @param {string} key - 存储键，必须是有效的字符串
   * @param {T} data - 要存储的数据，会自动进行JSON序列化
   * @returns {StorageResult<void>} 保存操作结果
   * 
   * @example
   * const result = storage.save('test-key', { name: '测试数据' });
   * if (result.success) {
   *   console.log('保存成功');
   * } else {
   *   console.error('保存失败:', result.error);
   * }
   */
  save<T>(key: string, data: T): StorageResult<void> {
    try {
      if (!key || typeof key !== 'string') {
        throw new Error('存储键必须是有效的字符串');
      }
      
      const serializedData = JSON.stringify(data);
      localStorage.setItem(key, serializedData);
      
      return { success: true };
    } catch (error) {
      console.error(`保存数据失败 (key: ${key}):`, error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : '未知错误' 
      };
    }
  }

  /**
   * 从本地存储加载数据
   * 
   * 自动进行JSON反序列化，包含完整的错误处理和类型安全
   * 
   * @method load
   * @template T - 期望的数据类型
   * @param {string} key - 存储键，必须是有效的字符串
   * @returns {StorageResult<T>} 加载操作结果，包含数据或错误信息
   * 
   * @example
   * const result = storage.load<{ name: string }>('test-key');
   * if (result.success) {
   *   console.log('加载的数据:', result.data);
   * } else {
   *   console.error('加载失败:', result.error);
   * }
   */
  load<T>(key: string): StorageResult<T> {
    try {
      if (!key || typeof key !== 'string') {
        throw new Error('存储键必须是有效的字符串');
      }

      const data = localStorage.getItem(key);
      if (data === null) {
        return { success: false, error: '数据不存在' };
      }

      const parsedData = JSON.parse(data) as T;
      return { success: true, data: parsedData };
    } catch (error) {
      console.error(`加载数据失败 (key: ${key}):`, error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : '数据解析失败' 
      };
    }
  }

  /**
   * 从本地存储删除数据
   * 
   * 删除指定键的数据，包含错误处理
   * 
   * @method remove
   * @param {string} key - 要删除的存储键
   * @returns {StorageResult<void>} 删除操作结果
   * 
   * @example
   * const result = storage.remove('test-key');
   * if (result.success) {
   *   console.log('删除成功');
   * }
   */
  remove(key: string): StorageResult<void> {
    try {
      if (!key || typeof key !== 'string') {
        throw new Error('存储键必须是有效的字符串');
      }

      localStorage.removeItem(key);
      return { success: true };
    } catch (error) {
      console.error(`删除数据失败 (key: ${key}):`, error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : '未知错误' 
      };
    }
  }

  /**
   * 检查数据是否存在
   * 
   * 检查指定键的数据是否存在于本地存储中
   * 
   * @method exists
   * @param {string} key - 要检查的存储键
   * @returns {boolean} 数据是否存在
   * 
   * @example
   * const exists = storage.exists('test-key');
   * console.log('数据是否存在:', exists);
   */
  exists(key: string): boolean {
    try {
      return localStorage.getItem(key) !== null;
    } catch (error) {
      console.error(`检查数据存在性失败 (key: ${key}):`, error);
      return false;
    }
  }

  /**
   * 获取所有存储键
   * 
   * 返回本地存储中所有的键列表
   * 
   * @method getAllKeys
   * @returns {string[]} 存储键列表
   * 
   * @example
   * const keys = storage.getAllKeys();
   * console.log('所有存储键:', keys);
   */
  getAllKeys(): string[] {
    try {
      const keys: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key) keys.push(key);
      }
      return keys;
    } catch (error) {
      console.error('获取存储键列表失败:', error);
      return [];
    }
  }

  /**
   * 清空本地存储
   * 
   * 清空所有存储在localStorage中的数据
   * 
   * @method clear
   * @returns {StorageResult<void>} 清空操作结果
   * 
   * @example
   * const result = storage.clear();
   * if (result.success) {
   *   console.log('存储已清空');
   * }
   */
  clear(): StorageResult<void> {
    try {
      localStorage.clear();
      return { success: true };
    } catch (error) {
      console.error('清空存储失败:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : '未知错误' 
      };
    }
  }
}
