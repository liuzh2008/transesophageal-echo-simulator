"""
UI组件模块 - 负责创建应用程序的UI组件

此模块按照关注点分享原则，将UI创建逻辑从主窗口中分离出来。
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGroupBox, QFormLayout, QCheckBox,
                             QComboBox, QSlider, QPushButton, QToolBar,
                             QAction, QMenuBar, QMenu, QSplitter)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont


class UIComponents:
    """
    UI组件创建器
    
    按照关注点分享原则，负责创建应用程序的所有UI组件。
    将UI创建逻辑从业务逻辑中分离出来，提高代码的可维护性和可测试性。
    """
    
    @staticmethod
    def create_menu_bar(parent):
        """
        创建应用程序的菜单栏
        
        @param {QWidget} parent - 父窗口部件
        @returns {tuple} (menubar, actions_dict) - 菜单栏和动作字典
        @returns {QMenuBar} menubar - 创建的菜单栏
        @returns {dict} actions_dict - 包含所有菜单动作的字典
            - open_dir_action: 打开文件夹动作
            - exit_action: 退出动作
            - view_3d_action: 3D视图切换动作
            - about_action: 关于动作
        """
        menubar = QMenuBar(parent)
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 打开文件夹动作（仅保留文件夹导入功能）
        open_dir_action = QAction("打开DICOM文件夹(&D)...", parent)
        open_dir_action.setShortcut("Ctrl+D")
        open_dir_action.setStatusTip("打开包含DICOM文件的文件夹")
        file_menu.addAction(open_dir_action)
        
        # 分隔线
        file_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction("退出(&X)", parent)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出应用程序")
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        # 3D视图动作
        view_3d_action = QAction("3D视图(&3)", parent, checkable=True)
        view_3d_action.setChecked(True)
        view_3d_action.setStatusTip("显示/隐藏3D视图")
        view_menu.addAction(view_3d_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 关于动作
        about_action = QAction("关于(&A)...", parent)
        about_action.setStatusTip("显示关于信息")
        help_menu.addAction(about_action)
        
        return menubar, {
            'open_dir_action': open_dir_action,
            'exit_action': exit_action,
            'view_3d_action': view_3d_action,
            'about_action': about_action
        }
    
    @staticmethod
    def create_tool_bar(parent):
        """
        创建应用程序的工具栏
        
        @param {QWidget} parent - 父窗口部件
        @returns {tuple} (toolbar, actions_dict) - 工具栏和动作字典
        @returns {QToolBar} toolbar - 创建的工具栏
        @returns {dict} actions_dict - 包含所有工具栏动作的字典
            - view_3d_action: 3D视图切换动作
            - reset_action: 重置视图动作
        """
        toolbar = QToolBar("主工具栏", parent)
        toolbar.setIconSize(QSize(24, 24))
        
        # 3D视图按钮
        view_3d_action = QAction(QIcon(), "3D视图", parent)
        view_3d_action.setStatusTip("切换3D视图")
        toolbar.addAction(view_3d_action)
        
        toolbar.addSeparator()
        
        # 重置视图按钮
        reset_action = QAction(QIcon(), "重置视图", parent)
        reset_action.setStatusTip("重置所有视图")
        toolbar.addAction(reset_action)
        
        return toolbar, {
            'view_3d_action': view_3d_action,
            'reset_action': reset_action
        }
    
    @staticmethod
    def create_patient_panel():
        """
        创建患者信息面板
        
        @returns {tuple} (panel, labels_dict) - 面板和标签字典
        @returns {QGroupBox} panel - 患者信息面板
        @returns {dict} labels_dict - 包含所有标签控件的字典
            - patient_id_label: 患者ID标签
            - patient_name_label: 患者姓名标签
            - study_date_label: 检查日期标签
            - modality_label: 模态标签
        """
        panel = QGroupBox("患者信息")
        layout = QFormLayout(panel)
        
        # 患者ID
        patient_id_label = QLabel("未加载")
        layout.addRow("患者ID:", patient_id_label)
        
        # 患者姓名
        patient_name_label = QLabel("未加载")
        layout.addRow("患者姓名:", patient_name_label)
        
        # 检查日期
        study_date_label = QLabel("未加载")
        layout.addRow("检查日期:", study_date_label)
        
        # 模态
        modality_label = QLabel("未加载")
        layout.addRow("模态:", modality_label)
        
        return panel, {
            'patient_id_label': patient_id_label,
            'patient_name_label': patient_name_label,
            'study_date_label': study_date_label,
            'modality_label': modality_label
        }
    
    @staticmethod
    def create_view_options_panel():
        """
        创建视图选项面板
        
        @returns {tuple} (panel, controls_dict) - 面板和控制字典
        @returns {QGroupBox} panel - 视图选项面板
        @returns {dict} controls_dict - 包含所有控制控件的字典
            - view_3d_checkbox: 3D视图显示复选框
            - render_combo: 渲染模式下拉框
            - opacity_slider: 透明度滑块
            - cut_plane_button: 切割平面按钮
        """
        panel = QGroupBox("视图选项")
        layout = QVBoxLayout(panel)
        
        # 视图切换
        view_3d_checkbox = QCheckBox("显示3D视图")
        view_3d_checkbox.setChecked(True)
        layout.addWidget(view_3d_checkbox)
        
        # 渲染模式
        render_label = QLabel("渲染模式:")
        layout.addWidget(render_label)
        
        render_combo = QComboBox()
        render_combo.addItems(["体积渲染", "表面渲染", "线框渲染"])
        layout.addWidget(render_combo)
        
        # 透明度控制
        opacity_label = QLabel("模型透明度:")
        layout.addWidget(opacity_label)
        
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(10, 100)
        opacity_slider.setValue(70)
        layout.addWidget(opacity_slider)
        
        # 添加分隔线
        layout.addWidget(UIComponents._create_separator())
        
        # 切割平面控制
        cut_plane_label = QLabel("切割平面:")
        cut_plane_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(cut_plane_label)
        
        # 切割平面按钮
        cut_plane_button = QPushButton("显示50%位置横切面")
        cut_plane_button.setToolTip("在3D模型中显示50%位置的横切面（红色线条+浅红色填充）")
        cut_plane_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        layout.addWidget(cut_plane_button)
        
        return panel, {
            'view_3d_checkbox': view_3d_checkbox,
            'render_combo': render_combo,
            'opacity_slider': opacity_slider,
            'cut_plane_button': cut_plane_button
        }
    
    @staticmethod
    def _create_separator():
        """创建分隔线"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #cccccc;")
        return separator
    
    @staticmethod
    def create_3d_view_frame():
        """
        创建3D视图框架
        
        @returns {tuple} (frame, label) - 框架和标签
        @returns {QFrame} frame - 3D视图框架
        @returns {QLabel} label - 3D视图标签
        """
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        frame.setLineWidth(2)
        frame.setMinimumHeight(500)
        
        # 3D视图标签
        view_3d_label = QLabel("3D DICOM视图")
        view_3d_label.setAlignment(Qt.AlignCenter)
        view_3d_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        
        return frame, view_3d_label
    
    @staticmethod
    def create_main_layout():
        """
        创建主布局结构
        
        @returns {tuple} (v_splitter, h_splitter, left_widget, left_layout, right_widget, right_layout)
        @returns {QSplitter} v_splitter - 垂直分割器（主分割器）
        @returns {QSplitter} h_splitter - 水平分割器（上部分割器）
        @returns {QWidget} left_widget - 左侧部件（3D视图区域）
        @returns {QVBoxLayout} left_layout - 左侧布局
        @returns {QWidget} right_widget - 右侧部件（信息面板区域）
        @returns {QVBoxLayout} right_layout - 右侧布局
        """
        # 创建垂直分割器（上部：3D视图+控制面板，下部：2D图像）
        v_splitter = QSplitter(Qt.Vertical)
        
        # 创建上部水平分割器（左侧3D视图，右侧信息面板）
        h_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：3D视图区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 右侧：信息面板区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # 将水平分割器添加到垂直分割器的上部
        v_splitter.addWidget(h_splitter)
        
        return v_splitter, h_splitter, left_widget, left_layout, right_widget, right_layout
