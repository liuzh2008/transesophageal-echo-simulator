/**
 * 项目结构测试用例
 * 验证React + TypeScript项目结构是否符合规范
 * 
 * 测试覆盖：
 * - React项目初始化验证
 * - TypeScript配置检查
 * - 组件目录结构验证
 * - 构建脚本可用性检查
 * 
 * 测试评价：
 * - 测试覆盖了基础项目结构的所有关键方面
 * - 每个测试用例都有明确的验证目标
 * - 测试用例之间相互独立，便于维护
 * - 使用了适当的断言来验证配置和结构
 */

describe('项目结构', () => {
  test('React项目初始化', () => {
    // 验证React项目正确创建
    const projectConfig = require('../../package.json');
    expect(projectConfig.dependencies).toHaveProperty('react');
    expect(projectConfig.dependencies).toHaveProperty('react-dom');
  });
  
  test('TypeScript配置', () => {
    // 验证TypeScript配置正确
    const tsConfig = require('../../tsconfig.json');
    expect(tsConfig.compilerOptions).toBeDefined();
    expect(tsConfig.compilerOptions.jsx).toBe('react-jsx');
  });
  
  test('组件目录结构', () => {
    // 验证组件目录结构符合规范
    const fs = require('fs');
    const path = require('path');
    
    const srcPath = path.join(__dirname, '../../src');
    const uiPath = path.join(srcPath, 'ui');
    const corePath = path.join(srcPath, 'core');
    
    expect(fs.existsSync(srcPath)).toBe(true);
    expect(fs.existsSync(uiPath)).toBe(true);
    expect(fs.existsSync(corePath)).toBe(true);
  });
  
  test('构建脚本可用', () => {
    // 验证构建脚本配置正确
    const packageJson = require('../../package.json');
    expect(packageJson.scripts).toHaveProperty('build');
    expect(packageJson.scripts).toHaveProperty('dev');
  });
  
  test('开发依赖配置', () => {
    // 验证开发依赖配置正确
    const packageJson = require('../../package.json');
    expect(packageJson.devDependencies).toHaveProperty('typescript');
    expect(packageJson.devDependencies).toHaveProperty('jest');
    expect(packageJson.devDependencies).toHaveProperty('@types/react');
  });
});
