import React from 'react';

/**
 * 加载状态指示器组件属性接口
 */
interface LoadingIndicatorProps {
  /** 是否显示加载状态 */
  isLoading: boolean;
  /** 加载文本 */
  text?: string;
  /** 加载进度 (0-100) */
  progress?: number;
  /** 自定义样式类名 */
  className?: string;
}

/**
 * 加载状态指示器组件
 * 
 * @component
 * @description 显示文件加载进度和状态的UI组件
 * @example
 * ```tsx
 * <LoadingIndicator 
 *   isLoading={true}
 *   text="正在加载STL文件..."
 *   progress={75}
 * />
 * ```
 * 
 * @returns {JSX.Element} 加载状态指示器组件
 */
const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  isLoading,
  text = '正在加载...',
  progress,
  className = ''
}) => {
  if (!isLoading) {
    return null;
  }

  return (
    <div 
      className={`loading-indicator ${className}`}
      data-testid="loading-indicator"
      role="status"
      aria-live="polite"
    >
      <div className="loading-content">
        <div className="loading-spinner" data-testid="loading-spinner">
          <div className="spinner"></div>
        </div>
        <div className="loading-text" data-testid="loading-text">
          {text}
        </div>
        {progress !== undefined && (
          <div className="loading-progress" data-testid="loading-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <span className="progress-text">{progress}%</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoadingIndicator;
