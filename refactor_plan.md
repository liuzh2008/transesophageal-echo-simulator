# 重构main_window.py计划

## 当前问题分析
当前`main_window.py`文件包含：
- UI创建逻辑
- 事件处理逻辑
- 业务逻辑
- VTK渲染逻辑
- DICOM加载逻辑

所有逻辑都混合在一个类中，违反了单一职责原则。

## 重构目标
按关注点分享原则重构，创建以下模块：

### 1. ui_components.py
- 负责创建UI组件
- 包含各种面板的创建方法
- 返回创建好的UI组件

### 2. event_handlers.py
- 负责处理用户事件
- 包含按钮点击、滑块变化等事件处理
- 与业务逻辑解耦

### 3. vtk_manager.py
- 负责VTK渲染相关逻辑
- 管理渲染器、演员、相机等
- 提供渲染模式切换功能

### 4. dicom_manager.py
- 负责DICOM文件加载和处理
- 与core模块的dicom_loader交互
- 管理患者信息显示

### 5. main_window.py (重构后)
- 作为主控制器
- 协调各个模块
- 初始化应用程序
- 最小化业务逻辑

## 重构步骤
1. [ ] 分析当前代码，识别关注点
2. [ ] 创建ui_components模块
3. [ ] 创建event_handlers模块
4. [ ] 创建vtk_manager模块
5. [ ] 创建dicom_manager模块
6. [ ] 重构main_window.py
7. [ ] 测试重构后的应用程序

## 预期收益
- 代码更易于维护
- 模块职责清晰
- 便于单元测试
- 提高代码复用性
