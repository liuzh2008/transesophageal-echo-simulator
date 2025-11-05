import React from 'react';
import Scene3D from '../core/Scene3D';

/**
 * 主应用组件
 * 食道超声模拟软件的主界面
 */
const App: React.FC = () => {
  return (
    <div className="app">
      <header className="app-header">
        <h1>食道超声模拟软件</h1>
        <p>基于React + TypeScript + Three.js的3D模拟应用</p>
      </header>
      <main className="app-main">
        <div className="scene-container">
          <Scene3D />
        </div>
      </main>
    </div>
  );
};

export default App;
