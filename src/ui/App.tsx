import React from 'react';
import Scene3D from '../core/Scene3D';
import ResponsiveLayout from './components/ResponsiveLayout';
import Panel from './components/Panel';
import Button from './components/Button';
import Slider from './components/Slider';
import ThemeProvider from './components/ThemeProvider';

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
                    <Scene3D />
                  </div>
                </Panel>
              </div>
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
