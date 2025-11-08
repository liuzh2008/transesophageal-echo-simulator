import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { createZoomManager, ZoomState, zoomValueToCameraDistance } from './ZoomManager';

/**
 * 缩放上下文接口
 */
interface ZoomContextType {
  zoomState: ZoomState;
  setZoom: (value: number) => void;
  resetZoom: () => void;
  getCameraDistance: () => number;
}

/**
 * 创建缩放上下文
 */
const ZoomContext = createContext<ZoomContextType | undefined>(undefined);

/**
 * 缩放上下文提供者组件
 * 负责管理缩放状态并在组件树中共享
 */
interface ZoomProviderProps {
  children: ReactNode;
  initialState?: Partial<ZoomState>;
}

export const ZoomProvider: React.FC<ZoomProviderProps> = ({ 
  children, 
  initialState 
}) => {
  // 创建缩放管理器实例
  const [zoomManager] = useState(() => createZoomManager(initialState));
  
  // 状态用于触发重新渲染
  const [zoomState, setZoomState] = useState<ZoomState>(zoomManager.getState());

  /**
   * 设置缩放值
   */
  const setZoom = useCallback((value: number) => {
    zoomManager.setZoom(value);
    setZoomState(zoomManager.getState());
  }, [zoomManager]);

  /**
   * 重置缩放
   */
  const resetZoom = useCallback(() => {
    zoomManager.reset();
    setZoomState(zoomManager.getState());
  }, [zoomManager]);

  /**
   * 获取相机距离（用于3D场景）
   */
  const getCameraDistance = useCallback(() => {
    return zoomValueToCameraDistance(zoomState.value);
  }, [zoomState.value]);

  const contextValue: ZoomContextType = {
    zoomState,
    setZoom,
    resetZoom,
    getCameraDistance,
  };

  return (
    <ZoomContext.Provider value={contextValue}>
      {children}
    </ZoomContext.Provider>
  );
};

/**
 * 使用缩放上下文的Hook
 */
export const useZoom = (): ZoomContextType => {
  const context = useContext(ZoomContext);
  if (context === undefined) {
    throw new Error('useZoom必须在ZoomProvider内部使用');
  }
  return context;
};

/**
 * 缩放上下文Hook，提供只读访问
 */
export const useZoomState = (): ZoomState => {
  const { zoomState } = useZoom();
  return zoomState;
};

/**
 * 缩放控制Hook，提供操作方法
 */
export const useZoomControls = () => {
  const { setZoom, resetZoom, getCameraDistance } = useZoom();
  return { setZoom, resetZoom, getCameraDistance };
};
