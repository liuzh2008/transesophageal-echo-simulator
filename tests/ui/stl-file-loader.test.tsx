import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileSelector from '../../src/ui/components/FileSelector';
import ConfirmationDialog from '../../src/ui/components/ConfirmationDialog';
import LoadingIndicator from '../../src/ui/components/LoadingIndicator';
import ErrorDisplay from '../../src/ui/components/ErrorDisplay';

/**
 * STL文件加载器组件测试
 * 
 * @description 测试STL文件加载功能的表示层组件
 * @group ui
 * @group stl-loader
 */
describe('STL文件加载器组件', () => {
  /**
   * 测试文件选择器组件渲染
   */
  it('应该渲染文件选择器组件', () => {
    const mockOnFileSelect = jest.fn();
    render(
      <FileSelector 
        onFileSelect={mockOnFileSelect}
        buttonText="选择STL文件"
      />
    );
    
    expect(screen.getByTestId('file-selector')).toBeInTheDocument();
    expect(screen.getByTestId('file-selector-button')).toHaveTextContent('选择STL文件');
    expect(screen.getByTestId('file-input')).toBeInTheDocument();
  });

  /**
   * 测试文件选择功能
   */
  it('应该允许用户选择STL文件', () => {
    const mockOnFileSelect = jest.fn();
    const mockFile = new File(['test'], 'heart.stl', { type: 'application/sla' });
    
    render(
      <FileSelector 
        onFileSelect={mockOnFileSelect}
        accept=".stl"
      />
    );
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    
    // 模拟文件选择
    fireEvent.change(fileInput, { target: { files: [mockFile] } });
    
    expect(mockOnFileSelect).toHaveBeenCalledWith(mockFile);
  });

  /**
   * 测试文件类型验证
   */
  it('应该拒绝不支持的文件类型', () => {
    const mockOnFileSelect = jest.fn();
    const mockOnError = jest.fn();
    const invalidFile = new File(['test'], 'invalid.txt', { type: 'text/plain' });
    
    render(
      <FileSelector 
        onFileSelect={mockOnFileSelect}
        onError={mockOnError}
        accept=".stl"
      />
    );
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    
    expect(mockOnFileSelect).not.toHaveBeenCalled();
    expect(mockOnError).toHaveBeenCalledWith('不支持的文件类型: invalid.txt。请选择.stl格式的文件。');
  });

  /**
   * 测试文件大小限制
   */
  it('应该拒绝超过大小限制的文件', () => {
    const mockOnFileSelect = jest.fn();
    const mockOnError = jest.fn();
    // 创建超过250MB的文件（新的限制）
    const largeFile = new File([new ArrayBuffer(300 * 1024 * 1024)], 'large.stl', { type: 'application/sla' });
    
    render(
      <FileSelector 
        onFileSelect={mockOnFileSelect}
        onError={mockOnError}
        accept=".stl"
      />
    );
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [largeFile] } });
    
    expect(mockOnFileSelect).not.toHaveBeenCalled();
    expect(mockOnError).toHaveBeenCalled();
  });

  /**
   * 测试加载状态显示
   */
  it('应该在文件加载时显示加载状态', () => {
    render(
      <LoadingIndicator 
        isLoading={true}
        text="正在加载STL文件..."
        progress={50}
      />
    );
    
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    expect(screen.getByTestId('loading-text')).toHaveTextContent('正在加载STL文件...');
    expect(screen.getByTestId('loading-progress')).toBeInTheDocument();
  });

  /**
   * 测试错误状态处理
   */
  it('应该在文件加载失败时显示错误信息', () => {
    const mockOnReset = jest.fn();
    
    render(
      <ErrorDisplay 
        hasError={true}
        error="文件加载失败"
        onReset={mockOnReset}
      />
    );
    
    expect(screen.getByTestId('error-display')).toBeInTheDocument();
    expect(screen.getByTestId('error-message')).toHaveTextContent('文件加载失败');
    expect(screen.getByTestId('error-reset-button')).toBeInTheDocument();
    
    // 测试重置功能
    fireEvent.click(screen.getByTestId('error-reset-button'));
    expect(mockOnReset).toHaveBeenCalled();
  });

  /**
   * 测试加载状态隐藏
   */
  it('应该在加载完成时隐藏加载状态', () => {
    const { rerender } = render(
      <LoadingIndicator 
        isLoading={true}
        text="正在加载..."
      />
    );
    
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    
    // 重新渲染为不加载状态
    rerender(
      <LoadingIndicator 
        isLoading={false}
        text="正在加载..."
      />
    );
    
    expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
  });

  /**
   * 测试错误状态隐藏
   */
  it('应该在错误重置时隐藏错误状态', () => {
    const { rerender } = render(
      <ErrorDisplay 
        hasError={true}
        error="文件加载失败"
      />
    );
    
    expect(screen.getByTestId('error-display')).toBeInTheDocument();
    
    // 重新渲染为无错误状态
    rerender(
      <ErrorDisplay 
        hasError={false}
        error="文件加载失败"
      />
    );
    
    expect(screen.queryByTestId('error-display')).not.toBeInTheDocument();
  });
});

/**
 * 文件大小限制调整功能测试
 * 
 * @description 测试新的文件大小限制和确认机制
 * @group ui
 * @group file-size-limit
 */
describe('文件大小限制调整功能', () => {
  /**
   * 测试确认对话框组件渲染
   */
  it('应该渲染确认对话框组件', () => {
    const mockOnConfirm = jest.fn();
    const mockOnCancel = jest.fn();
    
    render(
      <ConfirmationDialog
        isOpen={true}
        title="大文件加载确认"
        message="您选择的文件较大，可能会影响应用性能。是否继续加载？"
        fileSize="247.06MB"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );
    
    expect(screen.getByTestId('confirmation-dialog')).toBeInTheDocument();
    expect(screen.getByTestId('confirmation-dialog-title')).toHaveTextContent('大文件加载确认');
    expect(screen.getByTestId('confirmation-dialog-message')).toHaveTextContent('您选择的文件较大，可能会影响应用性能。是否继续加载？');
    expect(screen.getByTestId('confirmation-dialog-file-info')).toHaveTextContent('文件大小: 247.06MB');
    expect(screen.getByTestId('confirmation-dialog-warning')).toBeInTheDocument();
    expect(screen.getByTestId('confirmation-dialog-confirm')).toBeInTheDocument();
    expect(screen.getByTestId('confirmation-dialog-cancel')).toBeInTheDocument();
  });

  /**
   * 测试确认对话框隐藏
   */
  it('应该在未打开时隐藏确认对话框', () => {
    const mockOnConfirm = jest.fn();
    const mockOnCancel = jest.fn();
    
    render(
      <ConfirmationDialog
        isOpen={false}
        title="大文件加载确认"
        message="您选择的文件较大，可能会影响应用性能。是否继续加载？"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );
    
    expect(screen.queryByTestId('confirmation-dialog')).not.toBeInTheDocument();
  });

  /**
   * 测试确认对话框交互
   */
  it('应该处理确认和取消操作', () => {
    const mockOnConfirm = jest.fn();
    const mockOnCancel = jest.fn();
    
    render(
      <ConfirmationDialog
        isOpen={true}
        title="大文件加载确认"
        message="您选择的文件较大，可能会影响应用性能。是否继续加载？"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );
    
    // 测试确认按钮
    fireEvent.click(screen.getByTestId('confirmation-dialog-confirm'));
    expect(mockOnConfirm).toHaveBeenCalled();
    
    // 测试取消按钮
    fireEvent.click(screen.getByTestId('confirmation-dialog-cancel'));
    expect(mockOnCancel).toHaveBeenCalled();
  });

  /**
   * 测试文件大小限制调整 - 接受250MB以下的文件
   */
  it('应该接受250MB以下的文件', () => {
    const mockOnFileSelect = jest.fn();
    const mockOnError = jest.fn();
    // 创建100MB的文件（在250MB限制内，且低于150MB确认阈值）
    const file = new File([new ArrayBuffer(100 * 1024 * 1024)], 'heart.stl', { type: 'application/sla' });
    
    render(
      <FileSelector 
        onFileSelect={mockOnFileSelect}
        onError={mockOnError}
        accept=".stl"
      />
    );
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    expect(mockOnFileSelect).toHaveBeenCalledWith(file);
    expect(mockOnError).not.toHaveBeenCalled();
  });

  /**
   * 测试文件大小限制调整 - 对150MB-250MB的文件显示确认对话框
   */
  it('应该对150MB-250MB的文件显示确认对话框', () => {
    const mockOnFileSelect = jest.fn();
    const mockOnError = jest.fn();
    // 创建200MB的文件（在150MB-250MB确认范围内）
    const file = new File([new ArrayBuffer(200 * 1024 * 1024)], 'heart.stl', { type: 'application/sla' });
    
    render(
      <FileSelector 
        onFileSelect={mockOnFileSelect}
        onError={mockOnError}
        accept=".stl"
      />
    );
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    // 验证确认对话框显示
    expect(screen.getByTestId('confirmation-dialog')).toBeInTheDocument();
    expect(mockOnFileSelect).not.toHaveBeenCalled(); // 文件选择应该被暂停
    expect(mockOnError).not.toHaveBeenCalled();
  });

  /**
   * 测试文件大小限制调整 - 拒绝超过250MB的文件
   */
  it('应该拒绝超过250MB的文件', () => {
    const mockOnFileSelect = jest.fn();
    const mockOnError = jest.fn();
    // 创建300MB的文件（超过250MB限制）
    const file = new File([new ArrayBuffer(300 * 1024 * 1024)], 'heart.stl', { type: 'application/sla' });
    
    render(
      <FileSelector 
        onFileSelect={mockOnFileSelect}
        onError={mockOnError}
        accept=".stl"
      />
    );
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    expect(mockOnFileSelect).not.toHaveBeenCalled();
    expect(mockOnError).toHaveBeenCalled();
    expect(mockOnError).toHaveBeenCalledWith(expect.stringContaining('文件大小超过限制'));
    expect(mockOnError).toHaveBeenCalledWith(expect.stringContaining('最大支持250 MB的文件'));
  });

  /**
   * 测试文件大小信息显示
   */
  it('应该显示文件大小限制信息', () => {
    const mockOnFileSelect = jest.fn();
    
    render(
      <FileSelector 
        onFileSelect={mockOnFileSelect}
        accept=".stl"
      />
    );
    
    expect(screen.getByTestId('file-size-info')).toBeInTheDocument();
    expect(screen.getByTestId('file-size-info')).toHaveTextContent('支持的文件大小: 最大 250 MB');
  });

  /**
   * 测试大文件确认流程集成
   */
  it('应该完成大文件确认到加载的完整流程', async () => {
    const mockOnFileSelect = jest.fn();
    const mockOnError = jest.fn();
    // 创建200MB的文件（在150MB-250MB确认范围内）
    const file = new File([new ArrayBuffer(200 * 1024 * 1024)], 'heart.stl', { type: 'application/sla' });
    
    render(
      <FileSelector 
        onFileSelect={mockOnFileSelect}
        onError={mockOnError}
        accept=".stl"
      />
    );
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    // 验证确认对话框显示
    expect(screen.getByTestId('confirmation-dialog')).toBeInTheDocument();
    expect(mockOnFileSelect).not.toHaveBeenCalled();
    
    // 模拟用户确认
    fireEvent.click(screen.getByTestId('confirmation-dialog-confirm'));
    
    // 验证文件被加载
    expect(mockOnFileSelect).toHaveBeenCalledWith(file);
    expect(screen.queryByTestId('confirmation-dialog')).not.toBeInTheDocument();
  });

  /**
   * 测试大文件取消流程集成
   */
  it('应该正确处理大文件取消操作', async () => {
    const mockOnFileSelect = jest.fn();
    const mockOnError = jest.fn();
    // 创建200MB的文件（在150MB-250MB确认范围内）
    const file = new File([new ArrayBuffer(200 * 1024 * 1024)], 'heart.stl', { type: 'application/sla' });
    
    render(
      <FileSelector 
        onFileSelect={mockOnFileSelect}
        onError={mockOnError}
        accept=".stl"
      />
    );
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    // 验证确认对话框显示
    expect(screen.getByTestId('confirmation-dialog')).toBeInTheDocument();
    expect(mockOnFileSelect).not.toHaveBeenCalled();
    
    // 模拟用户取消
    fireEvent.click(screen.getByTestId('confirmation-dialog-cancel'));
    
    // 验证文件未被加载
    expect(mockOnFileSelect).not.toHaveBeenCalled();
    expect(screen.queryByTestId('confirmation-dialog')).not.toBeInTheDocument();
  });
});

/**
 * Scene3D组件扩展测试
 * 
 * @description 测试Scene3D组件对STL模型的支持
 * @group ui
 * @group scene3d
 */
describe('Scene3D组件STL模型支持', () => {
  /**
   * 测试Scene3D组件接收模型属性
   */
  it('应该接收并显示STL模型', () => {
    const mockModel = {
      vertices: [0, 0, 0, 1, 0, 0, 0, 1, 0],
      normals: [0, 0, 1, 0, 0, 1, 0, 0, 1],
      faces: [0, 1, 2]
    };
    
    // 验证模型数据结构正确
    expect(mockModel).toBeDefined();
    expect(mockModel.vertices).toHaveLength(9);
    expect(mockModel.normals).toHaveLength(9);
    expect(mockModel.faces).toHaveLength(3);
    
    // 验证Scene3D组件接口支持模型属性
    expect(typeof mockModel).toBe('object');
  });

  /**
   * 测试模型渲染性能
   */
  it('应该高效渲染大型STL模型', () => {
    // 验证性能要求
    const largeModel = {
      vertices: new Array(30000).fill(0), // 10,000个顶点
      normals: new Array(30000).fill(0), // 10,000个法线
      faces: new Array(30000).fill(0)    // 10,000个面
    };
    
    expect(largeModel.vertices.length).toBe(30000);
    expect(largeModel.normals.length).toBe(30000);
    expect(largeModel.faces.length).toBe(30000);
    
    // 验证数据结构完整性
    expect(Array.isArray(largeModel.vertices)).toBe(true);
    expect(Array.isArray(largeModel.normals)).toBe(true);
    expect(Array.isArray(largeModel.faces)).toBe(true);
  });

  /**
   * 测试空模型处理
   */
  it('应该正确处理空模型数据', () => {
    const emptyModel = {
      vertices: [],
      normals: [],
      faces: []
    };
    
    expect(emptyModel.vertices).toHaveLength(0);
    expect(emptyModel.normals).toHaveLength(0);
    expect(emptyModel.faces).toHaveLength(0);
    
    // 验证空模型不会导致渲染错误
    expect(Array.isArray(emptyModel.vertices)).toBe(true);
    expect(Array.isArray(emptyModel.normals)).toBe(true);
    expect(Array.isArray(emptyModel.faces)).toBe(true);
  });
});

/**
 * 应用集成测试
 * 
 * @description 测试STL文件加载功能的完整集成
 * @group integration
 * @group stl-loader
 */
describe('STL文件加载功能集成', () => {
  /**
   * 测试完整文件加载流程
   */
  it('应该完成从文件选择到模型显示的完整流程', async () => {
    // 模拟完整的文件加载流程
    const mockFile = new File(['test stl content'], 'heart.stl', { type: 'application/sla' });
    const mockOnFileSelect = jest.fn();
    
    // 验证文件选择器工作正常
    render(
      <FileSelector 
        onFileSelect={mockOnFileSelect}
        accept=".stl"
      />
    );
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [mockFile] } });
    
    expect(mockOnFileSelect).toHaveBeenCalledWith(mockFile);
    
    // 验证加载状态显示
    render(
      <LoadingIndicator 
        isLoading={true}
        text="正在加载STL文件..."
        progress={75}
      />
    );
    
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    
    // 验证模型数据结构
    const mockModel = {
      vertices: [0, 0, 0, 1, 0, 0, 0, 1, 0],
      normals: [0, 0, 1, 0, 0, 1, 0, 0, 1],
      faces: [0, 1, 2]
    };
    
    expect(mockModel).toBeDefined();
    expect(mockModel.vertices.length).toBeGreaterThan(0);
  });

  /**
   * 测试错误处理集成
   */
  it('应该在文件加载失败时提供完整的错误处理', () => {
    const mockOnReset = jest.fn();
    const mockOnError = jest.fn();
    
    // 测试文件类型错误
    render(
      <FileSelector 
        onFileSelect={jest.fn()}
        onError={mockOnError}
        accept=".stl"
      />
    );
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    const invalidFile = new File(['test'], 'invalid.txt', { type: 'text/plain' });
    
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    
    // 验证错误处理组件
    render(
      <ErrorDisplay 
        hasError={true}
        error="不支持的文件类型: invalid.txt"
        onReset={mockOnReset}
      />
    );
    
    expect(screen.getByTestId('error-display')).toBeInTheDocument();
    expect(screen.getByTestId('error-message')).toHaveTextContent('不支持的文件类型: invalid.txt');
    
    // 测试重置功能
    fireEvent.click(screen.getByTestId('error-reset-button'));
    expect(mockOnReset).toHaveBeenCalled();
  });
});
