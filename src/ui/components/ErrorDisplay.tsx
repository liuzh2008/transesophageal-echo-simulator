import React from 'react';

/**
 * 错误状态显示组件属性接口
 */
interface ErrorDisplayProps {
  /** 错误消息 */
  error?: string;
  /** 是否显示错误状态 */
  hasError: boolean;
  /** 错误重置回调函数 */
  onReset?: () => void;
  /** 自定义样式类名 */
  className?: string;
}

/**
 * 错误状态显示组件
 * 
 * @component
 * @description 显示错误信息和提供重置功能的UI组件
 * @example
 * ```tsx
 * <ErrorDisplay 
 *   hasError={true}
 *   error="文件加载失败"
 *   onReset={() => console.log('重置错误状态')}
 * />
 * ```
 * 
 * @returns {JSX.Element} 错误状态显示组件
 */
const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  hasError,
  onReset,
  className = ''
}) => {
  if (!hasError || !error) {
    return null;
  }

  return (
    <div 
      className={`error-display ${className}`}
      data-testid="error-display"
      role="alert"
      aria-live="assertive"
    >
      <div className="error-content">
        <div className="error-icon" data-testid="error-icon">
          ⚠️
        </div>
        <div className="error-message" data-testid="error-message">
          {error}
        </div>
        {onReset && (
          <button
            onClick={onReset}
            className="error-reset-button"
            data-testid="error-reset-button"
          >
            重试
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorDisplay;
