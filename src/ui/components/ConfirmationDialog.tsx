import React from 'react';

/**
 * 确认对话框组件属性接口
 */
interface ConfirmationDialogProps {
  /** 是否显示对话框 */
  isOpen: boolean;
  /** 对话框标题 */
  title: string;
  /** 对话框内容 */
  message: string;
  /** 确认按钮文本 */
  confirmText?: string;
  /** 取消按钮文本 */
  cancelText?: string;
  /** 确认回调函数 */
  onConfirm: () => void;
  /** 取消回调函数 */
  onCancel: () => void;
  /** 文件大小信息（可选） */
  fileSize?: string;
}

/**
 * 确认对话框组件
 * 
 * @component
 * @description 用于显示确认对话框，特别适用于大文件加载确认
 * @example
 * ```tsx
 * <ConfirmationDialog
 *   isOpen={true}
 *   title="大文件加载确认"
 *   message="您选择的文件较大，可能会影响应用性能。是否继续加载？"
 *   fileSize="247.06MB"
 *   onConfirm={() => console.log('确认加载')}
 *   onCancel={() => console.log('取消加载')}
 * />
 * ```
 * 
 * @returns {JSX.Element | null} 确认对话框组件
 */
const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  isOpen,
  title,
  message,
  confirmText = '确认',
  cancelText = '取消',
  onConfirm,
  onCancel,
  fileSize
}) => {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="confirmation-dialog-overlay" data-testid="confirmation-dialog">
      <div className="confirmation-dialog">
        <div className="confirmation-dialog-header">
          <h3 className="confirmation-dialog-title" data-testid="confirmation-dialog-title">
            {title}
          </h3>
        </div>
        
        <div className="confirmation-dialog-body">
          <p className="confirmation-dialog-message" data-testid="confirmation-dialog-message">
            {message}
          </p>
          
          {fileSize && (
            <div className="confirmation-dialog-file-info" data-testid="confirmation-dialog-file-info">
              <strong>文件大小:</strong> {fileSize}
            </div>
          )}
          
          <div className="confirmation-dialog-warning" data-testid="confirmation-dialog-warning">
            <strong>性能影响说明:</strong>
            <ul>
              <li>大文件加载可能需要较长时间</li>
              <li>可能会占用较多内存</li>
              <li>在低性能设备上可能影响应用响应速度</li>
            </ul>
          </div>
        </div>
        
        <div className="confirmation-dialog-footer">
          <button
            onClick={onCancel}
            className="confirmation-dialog-button confirmation-dialog-button-cancel"
            data-testid="confirmation-dialog-cancel"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className="confirmation-dialog-button confirmation-dialog-button-confirm"
            data-testid="confirmation-dialog-confirm"
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationDialog;
