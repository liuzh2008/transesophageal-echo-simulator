import React from 'react';

/**
 * 响应式布局组件
 * 提供自适应屏幕尺寸的布局容器
 */
const ResponsiveLayout: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  return (
    <div data-testid="responsive-layout" className="responsive-layout">
      {children}
    </div>
  );
};

export default ResponsiveLayout;
