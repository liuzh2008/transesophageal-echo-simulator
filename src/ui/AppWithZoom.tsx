import React, { useState } from 'react';
import Scene3D from '../core/Scene3D';
import ResponsiveLayout from './components/ResponsiveLayout';
import Panel from './components/Panel';
import Button from './components/Button';
import Slider from './components/Slider';
import ThemeProvider from './components/ThemeProvider';
import STLFileLoader, { STLModel } from './components/STLFileLoader';
import { ZoomProvider, useZoomControls, useZoomState } from '../core/zoom/ZoomContext';

/**
 * STL文件加载组件
 * 负责STL模型文件的加载和管理
 */
interface STLFileLoaderComponentProps {
  onModelLoad: (model: STLModel) => void;
}

const STLFileLoaderComponent: React.FC<STLFileLoaderComponentProps> = ({ onModelLoad }) => {
  const [showDefaultCube, setShowDefaultCube] = useState(true);

  // 调试信息
  console.log('STLFileLoaderComponent渲染');

  /**
   * 处理STL模型加载
   */
  const handleModelLoad = (model: STLModel) => {
    console.log('STL模型加载完成:', model);
    onModelLoad(model);
    setShowDefaultCube(false);
  };

  /**
   * 处理加载错误
   */
  const handleLoadError = (error: string) => {
    console.error('STL文件加载错误:', error);
  };

  return (
    <div className="controls-section">
      <Panel title="STL文件加载" className="controls-panel">
        <STLFileLoader 
          onModelLoad={handleModelLoad}
          onError={handleLoadError}
        />
      </Panel>
    </div>
  );
};

/**
 * 缩放控制组件
 * 负责缩放UI控制，不包含业务逻辑
 */
const ZoomControls: React.FC = () => {
  const { setZoom, resetZoom } = useZoomControls();
  const zoomState = useZoomState();

  /**
   * 处理缩放值变化
   */
  const handleZoomChange = (value: number) => {
    console.log('ZoomControls: 设置缩放值:', value);
    setZoom(value);
  };

  /**
   * 处理重置场景
   */
  const handleReset = () => {
    resetZoom();
  };

  return (
    <div className="controls-section">
      <Panel title="场景控制" className="controls-panel">
        <div className="control-group">
          <Button onClick={handleReset} variant="secondary">
            重置场景
          </Button>
        </div>
        <div className="control-group">
          <label>缩放控制</label>
          <Slider 
            value={zoomState.value} 
            min={zoomState.min} 
            max={zoomState.max} 
            step={zoomState.step}
            onChange={handleZoomChange}
          />
        </div>
      </Panel>
    </div>
  );
};

/**
 * 3D场景组件
 * 负责3D场景渲染，接收缩放参数和模型数据
 */
interface SceneWithZoomProps {
  model?: STLModel | null;
}

const SceneWithZoom: React.FC<SceneWithZoomProps> = ({ model }) => {
  const { getCameraDistance } = useZoomControls();
  const zoomState = useZoomState();

  // 使用useMemo缓存相机距离，只在缩放值变化时重新计算
  const cameraDistance = React.useMemo(() => {
    const distance = getCameraDistance();
    console.log('SceneWithZoom: 计算相机距离, 缩放值:', zoomState.value, '相机距离:', distance);
    return distance;
  }, [getCameraDistance, zoomState.value]);

  return (
    <div className="scene-section">
      <Panel title="3D场景视图" className="scene-panel">
        <div className="scene-container">
          <Scene3D 
            cameraDistance={cameraDistance} 
            model={model}
            showDefaultCube={!model} // 有模型时不显示默认立方体
          />
        </div>
      </Panel>
    </div>
  );
};

/**
 * 食道超声模拟软件主应用组件（带缩放功能）
 * 
 * @component
 * @description 提供完整的食道超声模拟软件界面，集成3D场景、UI控件和主题配置
 * 使用关注点分离原则，状态管理由ZoomProvider负责
 * 
 * @returns {JSX.Element} 渲染完整的应用界面
 */
const AppWithZoom: React.FC = () => {
  const [currentModel, setCurrentModel] = useState<STLModel | null>(null);

  /**
   * 处理STL模型加载
   */
  const handleModelLoad = (model: STLModel) => {
    console.log('AppWithZoom: STL模型加载完成:', model);
    setCurrentModel(model);
  };

  return (
    <ZoomProvider>
      <ThemeProvider>
        <ResponsiveLayout>
          <div className="app">
            <header className="app-header">
              <h1>食道超声模拟软件</h1>
              <p>基于React + TypeScript + Three.js的3D模拟应用</p>
            </header>
            <main className="app-main">
              <div className="app-content">
                <SceneWithZoom model={currentModel} />
                <div className="controls-container">
                  <STLFileLoaderComponent onModelLoad={handleModelLoad} />
                  <ZoomControls />
                </div>
              </div>
            </main>
          </div>
        </ResponsiveLayout>
      </ThemeProvider>
    </ZoomProvider>
  );
};

export default AppWithZoom;
