import * as THREE from 'three';
import { STLLoader } from 'three-stdlib';

/**
 * STL文件加载服务
 * 职责：纯STL文件解析，不涉及UI或状态管理
 */
export class STLLoaderService {
  private stlLoader: STLLoader;
  private readonly maxFileSize = 250 * 1024 * 1024; // 250MB

  constructor() {
    this.stlLoader = new STLLoader();
  }

  /**
   * 解析STL二进制数据为Three.js网格
   * @param buffer STL文件的二进制数据
   * @returns Three.js网格对象
   * @throws 当STL数据无效时抛出错误
   */
  parseSTLBuffer(buffer: ArrayBuffer): THREE.Mesh {
    if (!buffer || buffer.byteLength === 0) {
      throw new Error('无效的STL文件格式：空数据');
    }

    if (buffer.byteLength < 84) {
      throw new Error('无效的STL文件格式：文件大小不足');
    }

    try {
      // 使用Three.js的STLLoader解析数据
      const geometry = this.stlLoader.parse(buffer);
      
      // 创建材质
      const material = new THREE.MeshPhongMaterial({
        color: 0x00ff00,
        specular: 0x111111,
        shininess: 200,
      });

      // 创建网格
      const mesh = new THREE.Mesh(geometry, material);
      
      // 计算几何体边界框和中心
      geometry.computeBoundingBox();
      geometry.computeBoundingSphere();
      
      return mesh;
    } catch (error) {
      throw new Error(`STL文件解析失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 验证STL文件是否有效
   * @param file 要验证的文件对象
   * @returns 文件是否有效
   */
  validateSTLFile(file: File): boolean {
    // 检查文件类型
    const validTypes = [
      'application/sla',
      'application/vnd.ms-pki.stl',
      'application/x-stl',
      'model/stl',
      '.stl'
    ];
    
    const fileExtension = file.name.toLowerCase().slice(-4);
    const isValidType = validTypes.some(type => 
      file.type.includes(type) || fileExtension === '.stl'
    );

    if (!isValidType) {
      return false;
    }

    // 检查文件大小
    if (file.size > this.maxFileSize) {
      return false;
    }

    // 检查文件是否为空
    if (file.size === 0) {
      return false;
    }

    return true;
  }

  /**
   * 从文件对象加载STL模型
   * @param file STL文件对象
   * @returns 解析后的Three.js网格
   */
  async loadFromFile(file: File): Promise<THREE.Mesh> {
    if (!this.validateSTLFile(file)) {
      throw new Error('无效的STL文件');
    }

    try {
      const arrayBuffer = await this.readFileAsArrayBuffer(file);
      return this.parseSTLBuffer(arrayBuffer);
    } catch (error) {
      throw new Error(`STL文件加载失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 将文件读取为ArrayBuffer
   * @param file 文件对象
   * @returns ArrayBuffer
   */
  private readFileAsArrayBuffer(file: File): Promise<ArrayBuffer> {
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
   * 释放Three.js资源
   * @param mesh 要释放的网格对象
   */
  dispose(mesh: THREE.Mesh): void {
    if (mesh.geometry) {
      mesh.geometry.dispose();
    }
    if (mesh.material) {
      if (Array.isArray(mesh.material)) {
        mesh.material.forEach(material => material.dispose());
      } else {
        mesh.material.dispose();
      }
    }
  }
}
