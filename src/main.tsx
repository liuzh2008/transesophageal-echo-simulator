import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './ui/AppWithZoom';
import './ui/styles.css';

/**
 * 应用主入口文件
 * 初始化React应用并挂载到DOM
 */
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
