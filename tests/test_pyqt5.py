#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyQt5 测试程序
一个简单的窗口应用程序，用于验证PyQt5安装是否成功
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('PyQt5 安装测试')
        self.setGeometry(100, 100, 400, 300)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 添加标签
        label = QLabel('PyQt5 安装成功！')
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold; color: green; margin: 20px;")
        layout.addWidget(label)
        
        # 添加信息标签
        info_label = QLabel(f'PyQt5 版本: 5.15.11\nPython 版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(info_label)
        
        # 添加按钮
        button = QPushButton('点击测试')
        button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")
        button.clicked.connect(self.on_button_click)
        layout.addWidget(button)
        
        # 添加状态标签
        self.status_label = QLabel('等待点击...')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # 设置布局
        central_widget.setLayout(layout)
    
    def on_button_click(self):
        self.status_label.setText('按钮已点击！PyQt5 工作正常。')
        self.status_label.setStyleSheet("font-size: 14px; color: blue; font-weight: bold; margin: 10px;")

def main():
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
