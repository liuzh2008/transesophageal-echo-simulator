import React from 'react';

/**
 * 自适应控件组件
 * 根据屏幕尺寸自动调整大小的基础控件
 */
const AdaptiveControl: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  return (
    <div data-testid="adaptive-control" className="adaptive-control">
      {children}
    </div>
  );
};

export default AdaptiveControl;
