import { ModelManager } from '../../../src/core/managers/ModelManager';
import { STLLoaderService } from '../../../src/core/services/STLLoaderService';
import { FileSystemService } from '../../../src/core/services/FileSystemService';
import * as THREE from 'three';

// Mock the services
jest.mock('../../../src/core/services/STLLoaderService');
jest.mock('../../../src/core/services/FileSystemService');

describe('ModelManager', () => {
  let modelManager: ModelManager;
  let mockSTLLoaderService: jest.Mocked<STLLoaderService>;
  let mockFileSystemService: jest.Mocked<FileSystemService>;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Create mock instances
    mockSTLLoaderService = new STLLoaderService() as jest.Mocked<STLLoaderService>;
    mockFileSystemService = new FileSystemService() as jest.Mocked<FileSystemService>;
    
    // Create ModelManager with mocked dependencies
    modelManager = new ModelManager(mockSTLLoaderService, mockFileSystemService);
  });

  describe('loadModel', () => {
    it('应该成功加载有效的STL文件', async () => {
      // 红：测试模型加载
      const testFile = new File([''], 'test.stl', { type: 'application/sla' });
      const mockMesh = new THREE.Mesh(
        new THREE.BoxGeometry(1, 1, 1),
        new THREE.MeshBasicMaterial()
      );

      // 设置mock行为
      mockSTLLoaderService.validateSTLFile.mockReturnValue(true);
      mockSTLLoaderService.loadFromFile.mockResolvedValue(mockMesh);

      // 绿：调用加载方法
      const result = await modelManager.loadModel(testFile);

      // 验证结果
      expect(result).toBe(mockMesh);
      expect(mockSTLLoaderService.validateSTLFile).toHaveBeenCalledWith(testFile);
      expect(mockSTLLoaderService.loadFromFile).toHaveBeenCalledWith(testFile);
    });

    it('应该拒绝无效的STL文件', async () => {
      // 红：测试无效文件处理
      const invalidFile = new File([''], 'test.txt', { type: 'text/plain' });

      // 设置mock行为
      mockSTLLoaderService.validateSTLFile.mockReturnValue(false);

      // 验证抛出错误
      await expect(modelManager.loadModel(invalidFile)).rejects.toThrow('无效的STL文件');
      expect(mockSTLLoaderService.validateSTLFile).toHaveBeenCalledWith(invalidFile);
      expect(mockSTLLoaderService.loadFromFile).not.toHaveBeenCalled();
    });

    it('应该处理加载过程中的错误', async () => {
      // 红：测试错误处理
      const testFile = new File([''], 'test.stl', { type: 'application/sla' });

      // 设置mock行为
      mockSTLLoaderService.validateSTLFile.mockReturnValue(true);
      mockSTLLoaderService.loadFromFile.mockRejectedValue(new Error('加载失败'));

      // 验证抛出错误
      await expect(modelManager.loadModel(testFile)).rejects.toThrow('模型加载失败');
    });
  });

  describe('disposeModel', () => {
    it('应该正确释放模型资源', () => {
      // 红：测试资源释放
      const mockMesh = new THREE.Mesh(
        new THREE.BoxGeometry(1, 1, 1),
        new THREE.MeshBasicMaterial()
      );

      // 设置mock行为
      mockSTLLoaderService.dispose.mockImplementation(() => {});

      // 绿：调用释放方法
      modelManager.disposeModel(mockMesh);

      // 验证结果
      expect(mockSTLLoaderService.dispose).toHaveBeenCalledWith(mockMesh);
    });

    it('应该处理空模型释放', () => {
      // 红：测试边界情况
      expect(() => {
        modelManager.disposeModel(null as any);
      }).not.toThrow();
    });
  });

  describe('getModelCache', () => {
    it('应该返回模型缓存', () => {
      // 红：测试缓存获取
      const cache = modelManager.getModelCache();

      // 验证结果
      expect(cache).toBeInstanceOf(Map);
    });

    it('应该缓存已加载的模型', async () => {
      // 红：测试缓存功能
      const testFile = new File([''], 'test.stl', { type: 'application/sla' });
      const mockMesh = new THREE.Mesh(
        new THREE.BoxGeometry(1, 1, 1),
        new THREE.MeshBasicMaterial()
      );

      // 设置mock行为
      mockSTLLoaderService.validateSTLFile.mockReturnValue(true);
      mockSTLLoaderService.loadFromFile.mockResolvedValue(mockMesh);

      // 加载模型
      await modelManager.loadModel(testFile);

      // 验证缓存
      const cache = modelManager.getModelCache();
      expect(cache.size).toBe(1);
      expect(cache.get(testFile.name)).toBe(mockMesh);
    });
  });

  describe('clearCache', () => {
    it('应该清空模型缓存', async () => {
      // 红：测试缓存清理
      const testFile = new File([''], 'test.stl', { type: 'application/sla' });
      const mockMesh = new THREE.Mesh(
        new THREE.BoxGeometry(1, 1, 1),
        new THREE.MeshBasicMaterial()
      );

      // 设置mock行为
      mockSTLLoaderService.validateSTLFile.mockReturnValue(true);
      mockSTLLoaderService.loadFromFile.mockResolvedValue(mockMesh);

      // 加载模型并填充缓存
      await modelManager.loadModel(testFile);
      expect(modelManager.getModelCache().size).toBe(1);

      // 清空缓存
      modelManager.clearCache();

      // 验证缓存已清空
      expect(modelManager.getModelCache().size).toBe(0);
    });
  });
});
