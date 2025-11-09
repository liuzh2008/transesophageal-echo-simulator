import '@testing-library/jest-dom';

// 全局测试配置
beforeEach(() => {
  // 重置所有模拟
  jest.clearAllMocks();
});

// 全局测试后清理
afterEach(() => {
  // 清理DOM
  document.body.innerHTML = '';
});

// 全局测试超时设置
jest.setTimeout(10000);

// 模拟window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // 已废弃
    removeListener: jest.fn(), // 已废弃
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// 模拟ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// 模拟IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// 模拟URL.createObjectURL
global.URL.createObjectURL = jest.fn();

// 模拟FileReader
global.FileReader = jest.fn().mockImplementation(() => ({
  readAsArrayBuffer: jest.fn(),
  readAsText: jest.fn(),
  readAsDataURL: jest.fn(),
  abort: jest.fn(),
  onload: null,
  onerror: null,
  onabort: null,
}));
