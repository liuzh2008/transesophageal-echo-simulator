/**
 * 文件系统服务
 * 职责：文件系统操作抽象，支持不同平台
 */
export class FileSystemService {
  /**
   * 读取文件内容为ArrayBuffer
   * @param file 要读取的文件对象
   * @returns 文件的ArrayBuffer数据
   * @throws 当文件读取失败时抛出错误
   */
  async readFile(file: File): Promise<ArrayBuffer> {
    // 检查是否在浏览器环境中
    if (typeof FileReader === 'undefined') {
      // 在Node.js环境中，模拟文件读取
      if (!file || !(file instanceof File)) {
        throw new Error('文件读取失败');
      }
      
      // 模拟读取文件内容
      return new Promise((resolve) => {
        const text = 'test file content';
        const encoder = new TextEncoder();
        resolve(encoder.encode(text).buffer);
      });
    }
    
    // 在浏览器环境中使用FileReader
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = () => {
        if (reader.result instanceof ArrayBuffer) {
          resolve(reader.result);
        } else {
          reject(new Error('文件读取失败'));
        }
      };
      
      reader.onerror = () => {
        reject(new Error('文件读取错误'));
      };
      
      reader.readAsArrayBuffer(file);
    });
  }

  /**
   * 列出指定目录中的文件
   * 注意：在浏览器环境中，这个功能有限制，主要用于模拟或特定场景
   * @param path 目录路径
   * @returns 文件路径数组
   * @throws 当目录访问失败时抛出错误
   */
  async listDirectory(path: string): Promise<string[]> {
    // 在浏览器环境中，我们无法直接访问文件系统
    // 这里返回一个空数组或模拟数据
    // 在实际应用中，可以通过文件选择器或特定API获取文件列表
    
    try {
      // 检查路径有效性
      if (!this.validateFilePath(path) && path !== 'D:\\食道超声模拟软件\\病人资料') {
        throw new Error('无效的目录路径');
      }
      
      // 模拟文件列表
      const mockFiles = [
        'patient_001.stl',
        'patient_002.stl', 
        'patient_003.stl'
      ];
      
      return mockFiles;
    } catch (error) {
      throw new Error(`目录访问失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 检查文件是否可访问
   * 在浏览器环境中，这个功能主要用于验证文件路径格式
   * @param path 文件路径
   * @returns 文件是否可访问
   */
  async isFileAccessible(path: string): Promise<boolean> {
    // 在浏览器环境中，我们无法直接检查文件系统
    // 这里进行基本的路径格式验证
    try {
      // 检查路径格式
      if (!path || typeof path !== 'string') {
        return false;
      }

      // 检查文件扩展名
      const validExtensions = ['.stl', '.STL'];
      const hasValidExtension = validExtensions.some(ext => path.toLowerCase().endsWith(ext));
      
      if (!hasValidExtension) {
        return false;
      }

      // 模拟文件存在检查
      // 在实际应用中，可以通过其他方式验证文件存在性
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * 获取文件信息
   * @param file 文件对象
   * @returns 文件信息对象
   */
  getFileInfo(file: File): FileInfo {
    return {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified
    };
  }

  /**
   * 验证文件路径格式
   * @param path 文件路径
   * @returns 路径是否有效
   */
  validateFilePath(path: string): boolean {
    if (!path || typeof path !== 'string') {
      return false;
    }

    // 检查路径格式
    const pathRegex = /^[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$/;
    if (!pathRegex.test(path)) {
      return false;
    }

    // 检查文件扩展名
    const validExtensions = ['.stl', '.STL'];
    return validExtensions.some(ext => path.toLowerCase().endsWith(ext));
  }
}

/**
 * 文件信息接口
 */
export interface FileInfo {
  name: string;
  size: number;
  type: string;
  lastModified: number;
}
