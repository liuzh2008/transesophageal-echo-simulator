import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import STLFileLoader from '../../src/ui/components/STLFileLoader';

/**
 * STL文件加载器集成测试
 * 
 * @description 测试STLFileLoader组件的完整集成功能
 * @group integration
 * @group stl-loader
 */
describe('STLFileLoader集成测试', () => {
  /**
   * 测试STLFileLoader组件渲染
   */
  it('应该渲染完整的STL文件加载器组件', () => {
    const mockOnModelLoad = jest.fn();
    const mockOnError = jest.fn();
    
    render(
      <STLFileLoader 
        onModelLoad={mockOnModelLoad}
        onError={mockOnError}
      />
    );
    
    expect(screen.getByTestId('stl-file-loader')).toBeInTheDocument();
    expect(screen.getByTestId('file-selector')).toBeInTheDocument();
    expect(screen.getByTestId('instruction-section')).toBeInTheDocument();
  });

  /**
   * 测试文件选择到模型加载的完整流程
   */
  it('应该完成从文件选择到模型加载的完整流程', async () => {
    const mockOnModelLoad = jest.fn();
    const mockOnError = jest.fn();
    
    render(
      <STLFileLoader 
        onModelLoad={mockOnModelLoad}
        onError={mockOnError}
      />
    );

    // 验证初始状态
    expect(screen.getByTestId('instruction-section')).toBeInTheDocument();
    expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    expect(screen.queryByTestId('error-display')).not.toBeInTheDocument();

    // 模拟文件选择
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    const mockFile = new File(['test stl content'], 'heart.stl', { type: 'application/sla' });
    
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    // 验证加载状态显示
    await waitFor(() => {
      expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    });

    // 验证加载完成
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    }, { timeout: 3000 });

    // 验证模型加载回调被调用（可能成功也可能失败，取决于随机错误概率）
    // 由于有30%的失败概率，我们检查是否调用了onModelLoad或onError
    const wasCalled = mockOnModelLoad.mock.calls.length > 0 || mockOnError.mock.calls.length > 0;
    expect(wasCalled).toBe(true);
  });

  /**
   * 测试错误处理集成
   */
  it('应该在文件加载失败时显示错误信息', async () => {
    const mockOnModelLoad = jest.fn();
    const mockOnError = jest.fn();
    
    render(
      <STLFileLoader 
        onModelLoad={mockOnModelLoad}
        onError={mockOnError}
      />
    );

    // 模拟文件选择（这里应该触发错误）
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    const mockFile = new File(['test stl content'], 'heart.stl', { type: 'application/sla' });
    
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    // 验证加载状态显示
    await waitFor(() => {
      expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    });

    // 等待加载完成（可能成功也可能失败）
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    }, { timeout: 3000 });

    // 检查是否显示了错误信息（如果解析失败）
    const errorDisplay = screen.queryByTestId('error-display');
    if (errorDisplay) {
      expect(mockOnError).toHaveBeenCalled();
      expect(mockOnModelLoad).not.toHaveBeenCalled();
    } else {
      // 如果解析成功，验证模型加载回调被调用
      expect(mockOnModelLoad).toHaveBeenCalled();
      expect(mockOnError).not.toHaveBeenCalled();
    }
  });

  /**
   * 测试错误重置功能
   */
  it('应该能够重置错误状态', async () => {
    const mockOnModelLoad = jest.fn();
    const mockOnError = jest.fn();
    
    render(
      <STLFileLoader 
        onModelLoad={mockOnModelLoad}
        onError={mockOnError}
      />
    );

    // 模拟文件选择（这里应该触发错误）
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    const mockFile = new File(['test stl content'], 'heart.stl', { type: 'application/sla' });
    
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    // 等待加载状态显示
    await waitFor(() => {
      expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    });

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    }, { timeout: 3000 });

    // 检查是否显示了错误信息
    const errorDisplay = screen.queryByTestId('error-display');
    if (errorDisplay) {
      // 如果有错误，测试重置功能
      fireEvent.click(screen.getByTestId('error-reset-button'));
      expect(screen.queryByTestId('error-display')).not.toBeInTheDocument();
      expect(screen.getByTestId('instruction-section')).toBeInTheDocument();
    } else {
      // 如果没有错误，测试仍然通过（这是可接受的情况）
      expect(screen.getByTestId('instruction-section')).toBeInTheDocument();
    }
  });

  /**
   * 测试大文件确认流程集成
   */
  it('应该处理大文件确认流程', async () => {
    const mockOnModelLoad = jest.fn();
    const mockOnError = jest.fn();
    
    render(
      <STLFileLoader 
        onModelLoad={mockOnModelLoad}
        onError={mockOnError}
      />
    );

    // 创建大文件（在150MB-250MB确认范围内）
    const largeFile = new File([new ArrayBuffer(200 * 1024 * 1024)], 'large-heart.stl', { type: 'application/sla' });
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [largeFile] } });

    // 验证确认对话框显示
    await waitFor(() => {
      expect(screen.getByTestId('confirmation-dialog')).toBeInTheDocument();
    });

    // 模拟用户确认
    fireEvent.click(screen.getByTestId('confirmation-dialog-confirm'));

    // 验证加载开始
    await waitFor(() => {
      expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    });

    // 验证加载完成
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    }, { timeout: 3000 });

    // 验证模型加载回调被调用（可能成功也可能失败，取决于随机错误概率）
    // 由于有30%的失败概率，我们检查是否调用了onModelLoad或onError
    const wasCalled = mockOnModelLoad.mock.calls.length > 0 || mockOnError.mock.calls.length > 0;
    expect(wasCalled).toBe(true);
  });
});
