#!/usr/bin/env python3
"""
经食管超声心动图模拟器 - 主应用程序入口

此应用程序提供交互式的3D可视化工具，帮助临床医生理解和模拟TEE检查过程。
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """应用程序主函数"""
    # 创建Qt应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("经食管超声心动图模拟器")
    app.setOrganizationName("医疗影像实验室")
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
