import React from 'react';

/**
 * 面板组件
 * 提供内容容器和布局功能
 */
interface PanelProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
}

const Panel: React.FC<PanelProps> = ({ children, title, className = '' }) => {
  return (
    <div data-testid="panel" className={`panel ${className}`}>
      {title && (
        <div className="panel__header">
          <h3 className="panel__title">{title}</h3>
        </div>
      )}
      <div className="panel__content">
        {children}
      </div>
    </div>
  );
};

export default Panel;
