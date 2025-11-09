import React, { useRef, useState, ChangeEvent } from 'react';
import ConfirmationDialog from './ConfirmationDialog';
import './confirmation-dialog.css';
import './file-selector.css';

/**
 * 文件选择器组件属性接口
 */
interface FileSelectorProps {
  /** 接受的文件类型 */
  accept?: string;
  /** 文件选择回调函数 */
  onFileSelect: (file: File) => void;
  /** 文件选择错误回调函数 */
  onError?: (error: string) => void;
  /** 是否禁用 */
  disabled?: boolean;
  /** 按钮文本 */
  buttonText?: string;
}

/**
 * 文件选择器组件
 * 
 * @component
 * @description 提供STL文件选择功能的UI组件，支持文件大小限制和确认机制
 * @example
 * ```tsx
 * <FileSelector 
 *   accept=".stl"
 *   onFileSelect={(file) => console.log('选择的文件:', file)}
 *   onError={(error) => console.error('文件选择错误:', error)}
 *   buttonText="选择STL文件"
 * />
 * ```
 * 
 * @returns {JSX.Element} 文件选择器组件
 */
const FileSelector: React.FC<FileSelectorProps> = ({
  accept = '.stl',
  onFileSelect,
  onError,
  disabled = false,
  buttonText = '选择文件'
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);

  // 文件大小限制配置
  const maxSize = 250 * 1024 * 1024; // 250MB
  const confirmationThreshold = 150 * 1024 * 1024; // 150MB

  /**
   * 格式化文件大小为可读格式
   */
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  /**
   * 处理文件选择
   */
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) {
      return;
    }

    const file = files[0];
    
    // 验证文件类型
    if (accept && !file.name.toLowerCase().endsWith(accept.toLowerCase())) {
      onError?.(`不支持的文件类型: ${file.name}。请选择${accept}格式的文件。`);
      return;
    }

    // 验证文件大小
    if (file.size > maxSize) {
      onError?.(`文件大小超过限制 (${formatFileSize(file.size)})。最大支持${formatFileSize(maxSize)}的文件。`);
      return;
    }

    // 检查是否需要确认
    if (file.size > confirmationThreshold) {
      setPendingFile(file);
      setShowConfirmation(true);
      return;
    }

    // 直接加载小文件
    processFileSelection(file);
    
    // 重置input值，允许选择同一个文件
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /**
   * 处理文件选择确认
   */
  const handleConfirmation = () => {
    if (pendingFile) {
      processFileSelection(pendingFile);
    }
    setShowConfirmation(false);
    setPendingFile(null);
    
    // 重置input值，允许选择同一个文件
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /**
   * 处理文件选择取消
   */
  const handleCancel = () => {
    setShowConfirmation(false);
    setPendingFile(null);
    
    // 重置input值，允许选择同一个文件
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /**
   * 处理文件选择流程
   */
  const processFileSelection = (file: File) => {
    onFileSelect(file);
  };

  /**
   * 触发文件选择对话框
   */
  const handleButtonClick = () => {
    if (fileInputRef.current && !disabled) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="file-selector" data-testid="file-selector">
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        data-testid="file-input"
      />
      <button
        onClick={handleButtonClick}
        disabled={disabled}
        className="file-selector-button"
        data-testid="file-selector-button"
      >
        {buttonText}
      </button>

      {/* 文件大小限制提示 */}
      <div className="file-size-info" data-testid="file-size-info">
        <small>支持的文件大小: 最大 {formatFileSize(maxSize)}</small>
      </div>

      {/* 确认对话框 */}
      <ConfirmationDialog
        isOpen={showConfirmation}
        title="大文件加载确认"
        message="您选择的文件较大，可能会影响应用性能。是否继续加载？"
        fileSize={pendingFile ? formatFileSize(pendingFile.size) : undefined}
        confirmText="继续加载"
        cancelText="取消"
        onConfirm={handleConfirmation}
        onCancel={handleCancel}
      />
    </div>
  );
};

export default FileSelector;
