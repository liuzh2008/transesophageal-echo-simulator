/**
 * 病人数据模型类
 * 
 * 按照TDD红-绿-重构流程实现的数据模型，负责病人数据的存储、验证和序列化
 * 
 * @class PatientData
 * @author 食道超声模拟软件开发团队
 * @version 1.0.0
 * @since 2025-11-08
 * 
 * @example
 * // 创建病人数据实例
 * const patient = new PatientData({
 *   name: '张三',
 *   age: 45,
 *   diagnosis: '心脏检查',
 *   gender: 'male'
 * });
 * 
 * // 验证数据
 * const validation = patient.isValid();
 * if (validation.isValid) {
 *   console.log('数据验证通过');
 * } else {
 *   console.log('验证错误:', validation.errors);
 * }
 * 
 * // 序列化为JSON
 * const json = patient.toJSON();
 */
export interface PatientDataProps {
  /** 病人姓名，必填字段，长度限制1-50个字符 */
  name: string;
  /** 病人年龄，必填字段，范围1-150岁 */
  age: number;
  /** 诊断信息，可选字段，长度限制200个字符 */
  diagnosis?: string;
  /** 性别，可选字段，支持'male'、'female'、'other' */
  gender?: 'male' | 'female' | 'other';
  /** 检查日期，可选字段 */
  examinationDate?: Date;
}

/**
 * 数据验证结果接口
 * 
 * @interface ValidationResult
 * @property {boolean} isValid - 验证是否通过
 * @property {string[]} errors - 错误信息列表
 */
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * 病人数据模型类
 * 
 * 提供病人数据的存储、验证和序列化功能
 * 
 * @class PatientData
 */
export default class PatientData {
  /** 病人姓名，自动进行trim处理 */
  readonly name: string;
  /** 病人年龄 */
  readonly age: number;
  /** 诊断信息，自动进行trim处理 */
  readonly diagnosis?: string;
  /** 性别 */
  readonly gender?: 'male' | 'female' | 'other';
  /** 检查日期 */
  readonly examinationDate?: Date;

  /**
   * 创建病人数据实例
   * 
   * @constructor
   * @param {PatientDataProps} props - 病人数据属性
   * 
   * @example
   * const patient = new PatientData({
   *   name: '张三',
   *   age: 45,
   *   diagnosis: '心脏检查'
   * });
   */
  constructor(props: PatientDataProps) {
    this.name = props.name.trim();
    this.age = props.age;
    this.diagnosis = props.diagnosis?.trim();
    this.gender = props.gender;
    this.examinationDate = props.examinationDate;
  }

  /**
   * 验证病人数据是否有效
   * 
   * 验证规则：
   * - 姓名不能为空且长度不超过50个字符
   * - 年龄必须在1-150岁之间
   * - 诊断信息长度不超过200个字符
   * 
   * @method isValid
   * @returns {ValidationResult} 验证结果，包含是否通过和错误信息列表
   * 
   * @example
   * const patient = new PatientData({ name: '', age: -5 });
   * const result = patient.isValid();
   * // 返回: { isValid: false, errors: ['姓名不能为空', '年龄必须大于0'] }
   */
  isValid(): ValidationResult {
    const errors: string[] = [];

    // 姓名验证
    if (this.name.length === 0) {
      errors.push('姓名不能为空');
    } else if (this.name.length > 50) {
      errors.push('姓名长度不能超过50个字符');
    }

    // 年龄验证
    if (this.age <= 0) {
      errors.push('年龄必须大于0');
    } else if (this.age > 150) {
      errors.push('年龄不能超过150岁');
    }

    // 诊断信息验证
    if (this.diagnosis && this.diagnosis.length > 200) {
      errors.push('诊断信息长度不能超过200个字符');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * 将病人数据转换为JSON对象
   * 
   * 用于数据序列化和存储，日期字段会自动转换为ISO字符串格式
   * 
   * @method toJSON
   * @returns {object} 序列化后的JSON对象
   * 
   * @example
   * const patient = new PatientData({ name: '张三', age: 45 });
   * const json = patient.toJSON();
   * // 返回: { name: '张三', age: 45, diagnosis: undefined, gender: undefined, examinationDate: undefined }
   */
  toJSON(): object {
    return {
      name: this.name,
      age: this.age,
      diagnosis: this.diagnosis,
      gender: this.gender,
      examinationDate: this.examinationDate?.toISOString()
    };
  }

  /**
   * 从JSON对象创建PatientData实例
   * 
   * 用于数据反序列化，日期字段会自动从ISO字符串转换为Date对象
   * 
   * @static
   * @method fromJSON
   * @param {any} data - JSON数据对象
   * @returns {PatientData} 创建的PatientData实例
   * 
   * @example
   * const jsonData = { name: '张三', age: 45, examinationDate: '2025-11-08T07:15:00.000Z' };
   * const patient = PatientData.fromJSON(jsonData);
   */
  static fromJSON(data: any): PatientData {
    return new PatientData({
      name: data.name,
      age: data.age,
      diagnosis: data.diagnosis,
      gender: data.gender,
      examinationDate: data.examinationDate ? new Date(data.examinationDate) : undefined
    });
  }
}
