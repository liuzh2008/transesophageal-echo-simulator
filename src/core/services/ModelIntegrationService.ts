import { ModelStore } from '../../data/models/ModelStore';
import { STLLoaderService } from './STLLoaderService';
import { FileSystemService } from './FileSystemService';
import { STLModel } from '../types/STLModel';
import * as THREE from 'three';

/**
 * 模型集成服务
 * 
 * @description 负责连接文件选择器与模型状态管理，处理完整的文件加载流程
 */
export class ModelIntegrationService {
  private modelStore: ModelStore;
  private stlLoaderService: STLLoaderService;
  private fileSystemService: FileSystemService;

  constructor(
    modelStore: ModelStore,
    stlLoaderService: STLLoaderService,
    fileSystemService: FileSystemService
  ) {
    this.modelStore = modelStore;
    this.stlLoaderService = stlLoaderService;
    this.fileSystemService = fileSystemService;
  }

  /**
   * 处理文件选择并加载模型
   * 
   * @param file 选择的文件
   * @returns Promise<THREE.Mesh> 加载的模型网格
   */
  async loadModelFromFile(file: File): Promise<THREE.Mesh> {
    try {
      // 开始加载状态
      this.modelStore.startLoading();

      // 使用STLLoaderService加载模型
      const mesh = await this.stlLoaderService.loadFromFile(file);
      
      // 更新加载进度
      this.modelStore.updateProgress(100);

      // 将THREE.Mesh转换为STLModel并设置成功状态
      const stlModel = this.convertMeshToSTLModel(mesh);
      this.modelStore.setSuccess(stlModel);

      return mesh;
    } catch (error) {
      // 设置错误状态
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      this.modelStore.setError(`文件加载失败: ${errorMessage}`);
      throw error;
    }
  }

  /**
   * 将THREE.Mesh转换为STLModel
   * 
   * @param mesh THREE.js网格对象
   * @returns STLModel 转换后的STL模型数据
   */
  private convertMeshToSTLModel(mesh: THREE.Mesh): STLModel {
    const geometry = mesh.geometry;
    
    // 获取顶点数据
    const vertices: number[] = [];
    if (geometry.attributes.position) {
      const positions = geometry.attributes.position.array;
      for (let i = 0; i < positions.length; i++) {
        vertices.push(positions[i]);
      }
    }

    // 获取法线数据
    const normals: number[] = [];
    if (geometry.attributes.normal) {
      const normalsArray = geometry.attributes.normal.array;
      for (let i = 0; i < normalsArray.length; i++) {
        normals.push(normalsArray[i]);
      }
    }

    // 获取面数据
    const faces: number[] = [];
    if (geometry.index) {
      const indices = geometry.index.array;
      for (let i = 0; i < indices.length; i++) {
        faces.push(indices[i]);
      }
    } else {
      // 如果没有索引，则使用顺序索引
      for (let i = 0; i < vertices.length / 3; i++) {
        faces.push(i);
      }
    }

    return {
      vertices,
      normals,
      faces
    };
  }

  /**
   * 处理文件选择错误
   * 
   * @param error 错误信息
   */
  handleFileSelectionError(error: string): void {
    this.modelStore.setError(error);
  }

  /**
   * 重置模型状态
   */
  resetModelState(): void {
    this.modelStore.reset();
  }

  /**
   * 获取当前模型状态
   */
  getCurrentState() {
    return this.modelStore.getState();
  }
}
