/**
 * 数据管理器类
 * 
 * 负责病人数据的持久化管理和业务逻辑，按照TDD红-绿-重构流程实现
 * 
 * @class DataManager
 * @author 食道超声模拟软件开发团队
 * @version 1.0.0
 * @since 2025-11-08
 * 
 * @example
 * // 创建数据管理器实例
 * const manager = new DataManager();
 * 
 * // 保存病人数据
 * const saveResult = manager.savePatient({
 *   name: '张三',
 *   age: 45,
 *   diagnosis: '心脏检查'
 * });
 * 
 * // 加载病人数据
 * const loadResult = manager.loadPatient('张三');
 * if (loadResult.success) {
 *   console.log('病人数据:', loadResult.data);
 * }
 */

import PatientData, { PatientDataProps, ValidationResult } from './models/PatientData';
import LocalStorageService, { StorageResult } from './services/LocalStorageService';

/**
 * 病人记录接口
 * 
 * @interface PatientRecord
 * @property {string} id - 病人记录的唯一标识符
 * @property {PatientDataProps} data - 病人数据
 * @property {Date} createdAt - 创建时间
 * @property {Date} updatedAt - 更新时间
 */
export interface PatientRecord {
  id: string;
  data: PatientDataProps;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 数据管理操作结果接口
 * 
 * @interface DataManagerResult
 * @template T - 数据类型
 * @property {boolean} success - 操作是否成功
 * @property {T} [data] - 返回的数据
 * @property {string} [error] - 错误信息
 */
export interface DataManagerResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * 数据管理器类
 * 
 * 提供病人数据的完整生命周期管理，包括保存、加载、更新、删除和查询
 * 
 * @class DataManager
 */
export default class DataManager {
  /** 本地存储服务实例 */
  private storage: LocalStorageService;
  /** 病人数据存储键前缀 */
  private readonly PATIENT_KEY_PREFIX = 'patient_';

  /**
   * 创建数据管理器实例
   * 
   * @constructor
   */
  constructor() {
    this.storage = new LocalStorageService();
  }

  /**
   * 保存病人数据
   * 
   * 在保存前会自动验证病人数据，验证通过后创建病人记录并保存到本地存储
   * 
   * @method savePatient
   * @param {PatientDataProps} patientData - 病人数据
   * @returns {DataManagerResult<string>} 保存操作结果，包含病人ID或错误信息
   * 
   * @example
   * const result = manager.savePatient({
   *   name: '李四',
   *   age: 35,
   *   diagnosis: '心脏检查'
   * });
   * if (result.success) {
   *   console.log('保存成功，病人ID:', result.data);
   * } else {
   *   console.error('保存失败:', result.error);
   * }
   */
  savePatient(patientData: PatientDataProps): DataManagerResult<string> {
    try {
      // 验证病人数据
      const patient = new PatientData(patientData);
      const validation = patient.isValid();
      
      if (!validation.isValid) {
        return {
          success: false,
          error: `数据验证失败: ${validation.errors.join(', ')}`
        };
      }

      // 创建病人记录
      const patientId = this.generatePatientId(patientData.name);
      const patientRecord: PatientRecord = {
        id: patientId,
        data: patientData,
        createdAt: new Date(),
        updatedAt: new Date()
      };

      // 保存到存储
      const saveResult = this.storage.save(patientId, patientRecord);
      if (!saveResult.success) {
        return {
          success: false,
          error: `保存失败: ${saveResult.error}`
        };
      }

      return {
        success: true,
        data: patientId
      };
    } catch (error) {
      console.error('保存病人数据失败:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : '未知错误'
      };
    }
  }

  /**
   * 加载病人数据
   * 
   * 根据病人姓名加载对应的病人记录
   * 
   * @method loadPatient
   * @param {string} name - 病人姓名
   * @returns {DataManagerResult<PatientRecord>} 加载操作结果，包含病人记录或错误信息
   * 
   * @example
   * const result = manager.loadPatient('李四');
   * if (result.success) {
   *   console.log('病人记录:', result.data);
   * } else {
   *   console.error('加载失败:', result.error);
   * }
   */
  loadPatient(name: string): DataManagerResult<PatientRecord> {
    try {
      const patientId = this.generatePatientId(name);
      const loadResult = this.storage.load<PatientRecord>(patientId);
      
      if (!loadResult.success) {
        return {
          success: false,
          error: loadResult.error
        };
      }

      return {
        success: true,
        data: loadResult.data
      };
    } catch (error) {
      console.error(`加载病人数据失败 (name: ${name}):`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : '未知错误'
      };
    }
  }

  /**
   * 删除病人数据
   * 
   * 根据病人姓名删除对应的病人记录
   * 
   * @method deletePatient
   * @param {string} name - 病人姓名
   * @returns {DataManagerResult<void>} 删除操作结果
   * 
   * @example
   * const result = manager.deletePatient('李四');
   * if (result.success) {
   *   console.log('删除成功');
   * }
   */
  deletePatient(name: string): DataManagerResult<void> {
    try {
      const patientId = this.generatePatientId(name);
      const removeResult = this.storage.remove(patientId);
      
      if (!removeResult.success) {
        return {
          success: false,
          error: removeResult.error
        };
      }

      return { success: true };
    } catch (error) {
      console.error(`删除病人数据失败 (name: ${name}):`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : '未知错误'
      };
    }
  }

  /**
   * 获取所有病人列表
   * 
   * 返回所有已保存的病人记录，按创建时间倒序排列
   * 
   * @method getAllPatients
   * @returns {DataManagerResult<PatientRecord[]>} 病人列表操作结果
   * 
   * @example
   * const result = manager.getAllPatients();
   * if (result.success) {
   *   console.log('病人列表:', result.data);
   * }
   */
  getAllPatients(): DataManagerResult<PatientRecord[]> {
    try {
      const allKeys = this.storage.getAllKeys();
      const patientKeys = allKeys.filter(key => key.startsWith(this.PATIENT_KEY_PREFIX));
      
      const patients: PatientRecord[] = [];
      
      for (const key of patientKeys) {
        const loadResult = this.storage.load<PatientRecord>(key);
        if (loadResult.success && loadResult.data) {
          patients.push(loadResult.data);
        }
      }

      // 按创建时间排序
      patients.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

      return {
        success: true,
        data: patients
      };
    } catch (error) {
      console.error('获取病人列表失败:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : '未知错误'
      };
    }
  }

  /**
   * 更新病人数据
   * 
   * 更新指定病人的数据，会保留原有数据并合并更新字段
   * 
   * @method updatePatient
   * @param {string} name - 病人姓名
   * @param {Partial<PatientDataProps>} updatedData - 要更新的数据字段
   * @returns {DataManagerResult<string>} 更新操作结果，包含新的病人ID或错误信息
   * 
   * @example
   * const result = manager.updatePatient('李四', { age: 36 });
   * if (result.success) {
   *   console.log('更新成功');
   * }
   */
  updatePatient(name: string, updatedData: Partial<PatientDataProps>): DataManagerResult<string> {
    try {
      // 先加载现有数据
      const loadResult = this.loadPatient(name);
      if (!loadResult.success || !loadResult.data) {
        return {
          success: false,
          error: `病人数据不存在: ${name}`
        };
      }

      // 合并数据
      const existingData = loadResult.data.data;
      const mergedData = { ...existingData, ...updatedData, name }; // 确保姓名不变

      // 保存更新后的数据
      return this.savePatient(mergedData);
    } catch (error) {
      console.error(`更新病人数据失败 (name: ${name}):`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : '未知错误'
      };
    }
  }

  /**
   * 生成病人ID
   * 
   * 根据病人姓名生成唯一的存储键
   * 
   * @private
   * @method generatePatientId
   * @param {string} name - 病人姓名
   * @returns {string} 生成的病人ID
   */
  private generatePatientId(name: string): string {
    return `${this.PATIENT_KEY_PREFIX}${name.toLowerCase().replace(/\s+/g, '_')}`;
  }

  /**
   * 获取存储统计信息
   * 
   * 返回存储中的病人数量和总存储键数量
   * 
   * @method getStorageStats
   * @returns {{ totalPatients: number; storageKeys: number }} 存储统计信息
   * 
   * @example
   * const stats = manager.getStorageStats();
   * console.log(`病人数量: ${stats.totalPatients}, 存储键数量: ${stats.storageKeys}`);
   */
  getStorageStats(): { totalPatients: number; storageKeys: number } {
    const allKeys = this.storage.getAllKeys();
    const patientKeys = allKeys.filter(key => key.startsWith(this.PATIENT_KEY_PREFIX));
    
    return {
      totalPatients: patientKeys.length,
      storageKeys: allKeys.length
    };
  }
}
