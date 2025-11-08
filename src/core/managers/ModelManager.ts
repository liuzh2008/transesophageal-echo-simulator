import * as THREE from 'three';
import { STLLoaderService } from '../services/STLLoaderService';
import { FileSystemService } from '../services/FileSystemService';

/**
 * 模型管理器
 * 职责：管理3D模型的生命周期，包括加载、缓存和释放
 */
export class ModelManager {
  private modelCache: Map<string, THREE.Mesh>;
  private stlLoaderService: STLLoaderService;
  private fileSystemService: FileSystemService;

  constructor(
    stlLoaderService?: STLLoaderService,
    fileSystemService?: FileSystemService
  ) {
    this.modelCache = new Map();
    this.stlLoaderService = stlLoaderService || new STLLoaderService();
    this.fileSystemService = fileSystemService || new FileSystemService();
  }

  /**
   * 加载STL模型文件
   * @param file STL文件对象
   * @returns 加载的Three.js网格
   * @throws 当文件无效或加载失败时抛出错误
   */
  async loadModel(file: File): Promise<THREE.Mesh> {
    // 验证文件
    if (!this.stlLoaderService.validateSTLFile(file)) {
      throw new Error('无效的STL文件');
    }

    // 检查缓存
    const cachedModel = this.modelCache.get(file.name);
    if (cachedModel) {
      return cachedModel;
    }

    try {
      // 加载模型
      const mesh = await this.stlLoaderService.loadFromFile(file);
      
      // 缓存模型
      this.modelCache.set(file.name, mesh);
      
      return mesh;
    } catch (error) {
      throw new Error(`模型加载失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 从文件路径加载模型
   * @param filePath 文件路径
   * @returns 加载的Three.js网格
   * @throws 当文件路径无效或加载失败时抛出错误
   */
  async loadModelFromPath(filePath: string): Promise<THREE.Mesh> {
    // 验证文件路径
    if (!this.fileSystemService.validateFilePath(filePath)) {
      throw new Error('无效的文件路径');
    }

    // 检查文件可访问性
    const isAccessible = await this.fileSystemService.isFileAccessible(filePath);
    if (!isAccessible) {
      throw new Error('文件不可访问');
    }

    // 检查缓存
    const fileName = this.extractFileName(filePath);
    const cachedModel = this.modelCache.get(fileName);
    if (cachedModel) {
      return cachedModel;
    }

    // 注意：在浏览器环境中，无法直接从路径加载文件
    // 这里抛出错误，提示使用文件选择器
    throw new Error('在浏览器环境中，请使用文件选择器加载模型');
  }

  /**
   * 释放模型资源
   * @param mesh 要释放的网格对象
   */
  disposeModel(mesh: THREE.Mesh | null): void {
    if (!mesh) {
      return;
    }

    try {
      // 从缓存中移除
      this.removeFromCache(mesh);
      
      // 释放Three.js资源
      this.stlLoaderService.dispose(mesh);
    } catch (error) {
      console.warn('模型释放失败:', error);
    }
  }

  /**
   * 从缓存中移除模型
   * @param mesh 要移除的网格对象
   */
  private removeFromCache(mesh: THREE.Mesh): void {
    for (const [fileName, cachedMesh] of this.modelCache.entries()) {
      if (cachedMesh === mesh) {
        this.modelCache.delete(fileName);
        break;
      }
    }
  }

  /**
   * 获取模型缓存
   * @returns 模型缓存Map
   */
  getModelCache(): Map<string, THREE.Mesh> {
    return new Map(this.modelCache);
  }

  /**
   * 清空模型缓存
   */
  clearCache(): void {
    // 释放所有缓存的模型资源
    for (const mesh of this.modelCache.values()) {
      this.stlLoaderService.dispose(mesh);
    }
    
    this.modelCache.clear();
  }

  /**
   * 获取缓存统计信息
   * @returns 缓存统计信息
   */
  getCacheStats(): CacheStats {
    return {
      totalModels: this.modelCache.size,
      memoryUsage: this.calculateMemoryUsage(),
      fileNames: Array.from(this.modelCache.keys())
    };
  }

  /**
   * 计算内存使用量（估算）
   * @returns 内存使用量（字节）
   */
  private calculateMemoryUsage(): number {
    let totalMemory = 0;
    
    for (const mesh of this.modelCache.values()) {
      if (mesh.geometry) {
        // 估算几何体内存使用
        const geometry = mesh.geometry;
        if (geometry.attributes.position) {
          totalMemory += geometry.attributes.position.array.byteLength;
        }
        if (geometry.attributes.normal) {
          totalMemory += geometry.attributes.normal.array.byteLength;
        }
        if (geometry.index) {
          totalMemory += geometry.index.array.byteLength;
        }
      }
    }
    
    return totalMemory;
  }

  /**
   * 从文件路径中提取文件名
   * @param filePath 文件路径
   * @returns 文件名
   */
  private extractFileName(filePath: string): string {
    const parts = filePath.split(/[\\/]/);
    return parts[parts.length - 1];
  }

  /**
   * 预加载多个模型文件
   * @param files 模型文件数组
   * @returns 加载进度和结果
   */
  async preloadModels(files: File[]): Promise<PreloadResult> {
    const results: PreloadResult = {
      total: files.length,
      loaded: 0,
      failed: 0,
      errors: []
    };

    const promises = files.map(async (file) => {
      try {
        await this.loadModel(file);
        results.loaded++;
      } catch (error) {
        results.failed++;
        results.errors.push({
          fileName: file.name,
          error: error instanceof Error ? error.message : '未知错误'
        });
      }
    });

    await Promise.all(promises);
    return results;
  }
}

/**
 * 缓存统计信息接口
 */
export interface CacheStats {
  totalModels: number;
  memoryUsage: number;
  fileNames: string[];
}

/**
 * 预加载结果接口
 */
export interface PreloadResult {
  total: number;
  loaded: number;
  failed: number;
  errors: Array<{
    fileName: string;
    error: string;
  }>;
}
