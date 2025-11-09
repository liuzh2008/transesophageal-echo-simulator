import React, { useState } from 'react';
import Scene3D from '../core/Scene3D';
import ResponsiveLayout from './components/ResponsiveLayout';
import Panel from './components/Panel';
import Button from './components/Button';
import Slider from './components/Slider';
import ThemeProvider from './components/ThemeProvider';
import STLFileLoader, { STLModel } from './components/STLFileLoader';

/**
 * 食道超声模拟软件主应用组件
 * 
 * @component
 * @description 提供完整的食道超声模拟软件界面，集成3D场景、UI控件和主题配置
 * @example
 * ```tsx
 * // 在main.tsx中使用
 * ReactDOM.createRoot(document.getElementById('root')!).render(
 *   <React.StrictMode>
 *     <App />
 *   </React.StrictMode>
 * );
 * ```
 * 
 * @returns {JSX.Element} 渲染完整的应用界面
 */
const App: React.FC = () => {
  const [currentModel, setCurrentModel] = useState<STLModel | null>(null);
  const [showDefaultCube, setShowDefaultCube] = useState(true);

  // 调试信息
  console.log('App组件渲染 - STLFileLoader组件应该显示');

  /**
   * 处理STL模型加载
   * @function
   * @description 处理STL文件加载完成后的模型数据
   * @param {STLModel} model - 加载的STL模型数据
   * @example
   * ```tsx
   * <STLFileLoader onModelLoad={handleModelLoad} />
   * ```
   */
  const handleModelLoad = (model: STLModel) => {
    console.log('STL模型加载完成:', model);
    setCurrentModel(model);
    setShowDefaultCube(false);
  };

  /**
   * 处理加载错误
   * @function
   * @description 处理STL文件加载过程中的错误
   * @param {string} error - 错误信息
   * @example
   * ```tsx
   * <STLFileLoader onError={handleLoadError} />
   * ```
   */
  const handleLoadError = (error: string) => {
    console.error('STL文件加载错误:', error);
  };

  /**
   * 重置场景处理函数
   * @function
   * @description 重置3D场景到初始状态
   * @example
   * ```tsx
   * <Button onClick={handleReset}>重置场景</Button>
   * ```
   */
  const handleReset = () => {
    console.log('重置场景');
    setCurrentModel(null);
    setShowDefaultCube(true);
  };

  /**
   * 缩放控制处理函数
   * @function
   * @description 处理滑块缩放值变化
   * @param {number} value - 缩放级别，范围0-100
   * @example
   * ```tsx
   * <Slider onChange={handleZoomChange} />
   * ```
   */
  const handleZoomChange = (value: number) => {
    console.log('缩放级别:', value);
  };

  return (
    <ThemeProvider>
      <ResponsiveLayout>
        <div className="app">
          <header className="app-header">
            <h1>食道超声模拟软件</h1>
            <p>基于React + TypeScript + Three.js的3D模拟应用</p>
          </header>
          <main className="app-main">
            <div className="app-content">
              <div className="scene-section">
                <Panel title="3D场景视图" className="scene-panel">
                  <div className="scene-container">
                    <Scene3D 
                      model={currentModel}
                      showDefaultCube={showDefaultCube}
                    />
                  </div>
                </Panel>
              </div>
              <div className="controls-section">
                <Panel title="STL文件加载" className="controls-panel">
                  <STLFileLoader 
                    onModelLoad={handleModelLoad}
                    onError={handleLoadError}
                  />
                </Panel>
                
                <Panel title="场景控制" className="controls-panel">
                  <div className="control-group">
                    <Button onClick={handleReset} variant="secondary">
                      重置场景
                    </Button>
                  </div>
                  <div className="control-group">
                    <label>缩放控制</label>
                    <Slider 
                      value={50} 
                      min={0} 
                      max={100} 
                      onChange={handleZoomChange}
                    />
                  </div>
                </Panel>
              </div>
            </div>
          </main>
        </div>
      </ResponsiveLayout>
    </ThemeProvider>
  );
};

export default App;
