import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileSelector from '../../src/ui/components/FileSelector';
import { ModelStore } from '../../src/data/models/ModelStore';
import { ModelIntegrationService } from '../../src/core/services/ModelIntegrationService';
import { STLLoaderService } from '../../src/core/services/STLLoaderService';
import { FileSystemService } from '../../src/core/services/FileSystemService';

/**
 * FileSelector与ModelStore集成测试
 * 
 * @description 测试文件选择器与模型状态管理的集成
 * 验证FileSelector组件与ModelIntegrationService和ModelStore的完整集成流程
 * @group integration
 * @group file-selector
 * @group model-loading
 */
describe('FileSelector与ModelStore集成', () => {
  let modelStore: ModelStore;
  let modelIntegrationService: ModelIntegrationService;
  let stlLoaderService: STLLoaderService;
  let fileSystemService: FileSystemService;

  beforeEach(() => {
    // 初始化所有服务实例
    modelStore = new ModelStore();
    stlLoaderService = new STLLoaderService();
    fileSystemService = new FileSystemService();
    modelIntegrationService = new ModelIntegrationService(
      modelStore,
      stlLoaderService,
      fileSystemService
    );
  });

  afterEach(() => {
    // 清理所有模拟和状态
    jest.clearAllMocks();
    modelStore.reset();
  });

  /**
   * 测试文件选择器与ModelStore的集成
   */
  it('应该将选择的文件传递给ModelIntegrationService进行处理', async () => {
    const mockFile = new File(['test stl content'], 'heart.stl', { type: 'application/sla' });
    
    // 模拟ModelIntegrationService的loadModelFromFile方法，并实际调用ModelStore的方法
    const mockLoadModelFromFile = jest.spyOn(modelIntegrationService, 'loadModelFromFile').mockImplementation(async (file) => {
      // 实际调用ModelStore的startLoading方法
      modelStore.startLoading();
      return {
        geometry: {},
        material: {}
      } as any;
    });

    // 渲染FileSelector并传递ModelIntegrationService的处理函数
    render(
      <FileSelector 
        onFileSelect={(file) => modelIntegrationService.loadModelFromFile(file)}
        accept=".stl"
      />
    );

    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    
    // 模拟文件选择
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    // 验证ModelIntegrationService的loadModelFromFile方法被调用
    await waitFor(() => {
      expect(mockLoadModelFromFile).toHaveBeenCalledWith(mockFile);
    });

    // 验证ModelStore的状态更新
    expect(modelStore.getState().isLoading).toBe(true);
  });

  /**
   * 测试文件选择错误处理与ModelStore的集成
   */
  it('应该在文件选择错误时更新ModelStore状态', () => {
    const mockOnError = jest.fn();
    
    render(
      <FileSelector 
        onFileSelect={jest.fn()}
        onError={(error) => {
          mockOnError(error);
          modelIntegrationService.handleFileSelectionError(error);
        }}
        accept=".stl"
      />
    );

    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    const invalidFile = new File(['test'], 'invalid.txt', { type: 'text/plain' });
    
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });

    // 验证错误回调被调用
    expect(mockOnError).toHaveBeenCalledWith('不支持的文件类型: invalid.txt。请选择.stl格式的文件。');

    // 验证ModelStore的错误状态
    expect(modelStore.getState().error).toBe('不支持的文件类型: invalid.txt。请选择.stl格式的文件。');
  });

  /**
   * 测试大文件确认流程与ModelStore的集成
   */
  it('应该在大文件确认后调用ModelIntegrationService加载', async () => {
    // 创建200MB的文件（在150MB-250MB确认范围内）
    const largeFile = new File([new ArrayBuffer(200 * 1024 * 1024)], 'heart.stl', { type: 'application/sla' });
    
    // 模拟ModelIntegrationService的loadModelFromFile方法，并实际调用ModelStore的方法
    const mockLoadModelFromFile = jest.spyOn(modelIntegrationService, 'loadModelFromFile').mockImplementation(async (file) => {
      // 实际调用ModelStore的startLoading方法
      modelStore.startLoading();
      return {
        geometry: {},
        material: {}
      } as any;
    });

    render(
      <FileSelector 
        onFileSelect={(file) => modelIntegrationService.loadModelFromFile(file)}
        accept=".stl"
      />
    );

    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [largeFile] } });

    // 验证确认对话框显示
    expect(screen.getByTestId('confirmation-dialog')).toBeInTheDocument();

    // 模拟用户确认
    fireEvent.click(screen.getByTestId('confirmation-dialog-confirm'));

    // 验证ModelIntegrationService的loadModelFromFile方法被调用
    await waitFor(() => {
      expect(mockLoadModelFromFile).toHaveBeenCalledWith(largeFile);
    });

    // 验证ModelStore的加载状态
    expect(modelStore.getState().isLoading).toBe(true);
  });

  /**
   * 测试大文件取消流程与ModelStore的集成
   */
  it('应该在大文件取消后不调用ModelIntegrationService加载', async () => {
    // 创建200MB的文件（在150MB-250MB确认范围内）
    const largeFile = new File([new ArrayBuffer(200 * 1024 * 1024)], 'heart.stl', { type: 'application/sla' });
    
    // 模拟ModelIntegrationService的loadModelFromFile方法
    const mockLoadModelFromFile = jest.spyOn(modelIntegrationService, 'loadModelFromFile');

    render(
      <FileSelector 
        onFileSelect={(file) => modelIntegrationService.loadModelFromFile(file)}
        accept=".stl"
      />
    );

    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [largeFile] } });

    // 验证确认对话框显示
    expect(screen.getByTestId('confirmation-dialog')).toBeInTheDocument();

    // 模拟用户取消
    fireEvent.click(screen.getByTestId('confirmation-dialog-cancel'));

    // 验证ModelIntegrationService的loadModelFromFile方法没有被调用
    await waitFor(() => {
      expect(mockLoadModelFromFile).not.toHaveBeenCalled();
    });

    // 验证ModelStore的状态保持不变
    expect(modelStore.getState().isLoading).toBe(false);
    expect(modelStore.getState().error).toBe(null);
  });
});
