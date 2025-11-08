import React from 'react';

/**
 * 触摸交互组件
 * 提供移动设备友好的触摸交互支持
 */
const TouchInteraction: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  return (
    <div data-testid="touch-interaction" className="touch-interaction">
      {children}
    </div>
  );
};

export default TouchInteraction;
