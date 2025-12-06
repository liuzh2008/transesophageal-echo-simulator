# PyQt5 安装和配置指南

## 已完成步骤

### 1. Python环境检查
- 已安装Python 3.10.11
- 使用`py --version`验证
- pip版本: 23.0.1

### 2. 虚拟环境创建
- 创建虚拟环境: `py -m venv venv`
- 虚拟环境目录: `venv/`

### 3. PyQt5安装
- 激活虚拟环境: `venv\Scripts\activate` (Windows)
- 安装PyQt5: `pip install PyQt5`
- 安装版本: PyQt5 5.15.11

### 4. 验证安装
```bash
# 激活虚拟环境
venv\Scripts\activate

# 验证PyQt5版本
python -c "from PyQt5 import QtCore; print(f'PyQt5 version: {QtCore.PYQT_VERSION_STR}')"
```

### 5. 测试程序
已创建测试程序 `tests/test_pyqt5.py`，包含：
- 简单窗口界面
- 版本信息显示
- 交互按钮测试

## 快速开始

### 激活虚拟环境
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 运行测试程序
```bash
python tests/test_pyqt5.py
```

### 安装依赖（在新环境中）
```bash
pip install -r requirements.txt
```

## 项目结构
```
d:/transesophageal-echo-simulator/
├── venv/                    # 虚拟环境目录
├── tests/                   # 测试目录
│   └── test_pyqt5.py       # PyQt5测试程序
├── requirements.txt        # 项目依赖
├── doc/
│   └── Demo/
│       └── 配置/
│           └── PYQT5_INSTALL_GUIDE.md # 本指南
└── .git/                   # Git版本控制
```

## 常见问题

### 1. 虚拟环境激活失败
- Windows: 确保使用`venv\Scripts\activate`
- 检查虚拟环境是否已创建

### 2. PyQt5导入错误
- 确保已激活虚拟环境
- 检查安装: `pip list | findstr PyQt5` (Windows)

### 3. 程序无法运行
- 检查Python路径: `where python` (Windows)
- 确保使用虚拟环境中的Python

## 下一步建议

1. **学习PyQt5基础**
   - 官方文档: https://www.riverbankcomputing.com/static/Docs/PyQt5/
   - 中文教程: https://maicss.gitbook.io/pyqt5/

2. **开发GUI应用**
   - 使用Qt Designer设计界面
   - 学习信号与槽机制
   - 掌握布局管理

3. **项目集成**
   - 将PyQt5集成到现有项目中
   - 创建专业的用户界面
   - 打包为可执行文件

## 依赖管理

### 导出当前环境依赖
```bash
pip freeze > requirements.txt
```

### 从requirements.txt安装
```bash
pip install -r requirements.txt
```

## 技术支持
- PyQt5官方文档: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- Python官方: https://www.python.org/
- 虚拟环境文档: https://docs.python.org/3/library/venv.html
