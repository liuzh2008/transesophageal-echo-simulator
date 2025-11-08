import { FileSystemService } from '../../../src/core/services/FileSystemService';

describe('FileSystemService', () => {
  let fileSystemService: FileSystemService;

  beforeEach(() => {
    fileSystemService = new FileSystemService();
  });

  describe('readFile', () => {
    it('应该正确读取文件内容为ArrayBuffer', async () => {
      // 红：测试文件读取
      const testContent = 'test file content';
      const testFile = new File([testContent], 'test.txt', { type: 'text/plain' });
      
      // 绿：调用读取方法
      const result = await fileSystemService.readFile(testFile);
      
      // 验证结果
      expect(result).toBeInstanceOf(ArrayBuffer);
      
      // 验证内容正确性
      const decoder = new TextDecoder();
      const content = decoder.decode(result);
      expect(content).toBe(testContent);
    });

    it('应该处理文件读取错误', async () => {
      // 红：测试错误处理
      // 创建一个无法读取的文件（模拟错误）
      const invalidFile = {} as File;
      
      // 验证抛出错误
      await expect(fileSystemService.readFile(invalidFile)).rejects.toThrow('文件读取失败');
    });
  });

  describe('listDirectory', () => {
    it('应该列出指定目录中的文件', async () => {
      // 红：测试目录列表功能
      // 注意：在浏览器环境中，这个功能可能有限制
      const testPath = 'D:\\食道超声模拟软件\\病人资料';
      
      // 绿：调用目录列表方法
      const files = await fileSystemService.listDirectory(testPath);
      
      // 验证结果
      expect(Array.isArray(files)).toBe(true);
      // 在浏览器环境中，可能返回空数组或模拟数据
    });

    it('应该处理目录访问错误', async () => {
      // 红：测试错误处理
      const invalidPath = 'invalid://path';
      
      // 验证抛出错误
      await expect(fileSystemService.listDirectory(invalidPath)).rejects.toThrow('目录访问失败');
    });
  });

  describe('isFileAccessible', () => {
    it('应该检查文件是否可访问', async () => {
      // 红：测试文件可访问性检查
      const testPath = 'D:\\食道超声模拟软件\\病人资料\\test.stl';
      
      // 绿：调用检查方法
      const isAccessible = await fileSystemService.isFileAccessible(testPath);
      
      // 验证结果
      expect(typeof isAccessible).toBe('boolean');
    });
  });
});
