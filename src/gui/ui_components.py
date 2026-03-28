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
        
        # 创建水平布局来放置按钮和计时标签
        cut_plane_layout = QHBoxLayout()
        cut_plane_layout.setSpacing(10)
        
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
        cut_plane_layout.addWidget(cut_plane_button)
        
        # 计时显示标签
        time_label = QLabel("用时: --")
        time_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 5px;
                background-color: #f5f5f5;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
        """)
        time_label.setMinimumWidth(100)
        cut_plane_layout.addWidget(time_label)
        
        # 添加弹性空间
        cut_plane_layout.addStretch()
        
        layout.addLayout(cut_plane_layout)
        
        # 添加分隔线
        layout.addWidget(UIComponents._create_separator())
        
        # Omniplane 角度控制 - 经食管超声(TEE)探头扫描平面旋转控制
        # Omniplane 技术允许在不移动探头的情况下，通过电子控制改变超声扫描平面的角度
        # 角度范围 0-180 度，模拟真实 TEE 探头的角度控制能力
        omniplane_label = QLabel("Omniplane 角度: 0°")
        omniplane_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(omniplane_label)
        
        # Omniplane 角度滑块 - 控制扫描平面的旋转角度
        # @ui_control {QSlider} omniplane_slider - 角度控制滑块，范围 0-180 度
        # @ui_control {int} tickInterval - 刻度间隔 15 度，对应临床常用的角度预设
        omniplane_slider = QSlider(Qt.Horizontal)
        omniplane_slider.setRange(0, 180)  # 标准 TEE 探头角度范围
        omniplane_slider.setValue(0)       # 默认 0 度（水平扫描平面）
        omniplane_slider.setTickInterval(15)
        omniplane_slider.setTickPosition(QSlider.TicksBelow)
        layout.addWidget(omniplane_slider)
        
        # 添加分隔线
        layout.addWidget(UIComponents._create_separator())
        
        # 扇形顶点偏移控制
        fan_apex_label = QLabel("扇形顶点偏移:")
        fan_apex_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(fan_apex_label)
        
        # X偏移
        fan_apex_x_label = QLabel("X偏移: 0.0")
        layout.addWidget(fan_apex_x_label)
        
        fan_apex_x_slider = QSlider(Qt.Horizontal)
        fan_apex_x_slider.setRange(-100, 100)
        fan_apex_x_slider.setValue(0)
        layout.addWidget(fan_apex_x_slider)
        
        # Y偏移
        fan_apex_y_label = QLabel("Y偏移: 0.0")
        layout.addWidget(fan_apex_y_label)
        
        fan_apex_y_slider = QSlider(Qt.Horizontal)
        fan_apex_y_slider.setRange(-100, 100)
        fan_apex_y_slider.setValue(0)
        layout.addWidget(fan_apex_y_slider)
        
        # Z偏移
        fan_apex_z_label = QLabel("Z偏移: 0.0")
        layout.addWidget(fan_apex_z_label)
        
        fan_apex_z_slider = QSlider(Qt.Horizontal)
        fan_apex_z_slider.setRange(-100, 100)
        fan_apex_z_slider.setValue(0)
        layout.addWidget(fan_apex_z_slider)
        
        return panel, {
            'view_3d_checkbox': view_3d_checkbox,
            'render_combo': render_combo,
            'opacity_slider': opacity_slider,
            'cut_plane_button': cut_plane_button,
            'cut_plane_time_label': time_label,  # 新增计时标签
            'omniplane_slider': omniplane_slider,
            'omniplane_label': omniplane_label,
            'fan_apex_x_slider': fan_apex_x_slider,
            'fan_apex_y_slider': fan_apex_y_slider,
            'fan_apex_z_slider': fan_apex_z_slider,
            'fan_apex_x_label': fan_apex_x_label,
            'fan_apex_y_label': fan_apex_y_label,
            'fan_apex_z_label': fan_apex_z_label
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
        
        @returns {tuple} (main_v_splitter, images_h_splitter, view_3d_widget, view_3d_layout, view_2d_widget, view_2d_layout, bottom_widget, bottom_layout)
        @returns {QSplitter} main_v_splitter - 主垂直分割器（上部：图像区域，下部：控制面板）
        @returns {QSplitter} images_h_splitter - 图像水平分割器（左侧：3D视图，右侧：2D图像）
        @returns {QWidget} view_3d_widget - 3D视图部件
        @returns {QVBoxLayout} view_3d_layout - 3D视图布局
        @returns {QWidget} view_2d_widget - 2D图像部件
        @returns {QVBoxLayout} view_2d_layout - 2D图像布局
        @returns {QWidget} bottom_widget - 底部控制面板部件
        @returns {QVBoxLayout} bottom_layout - 底部控制面板布局
        """
        # 创建主垂直分割器（上部：图像区域，下部：控制面板）
        main_v_splitter = QSplitter(Qt.Vertical)
        
        # 创建图像水平分割器（左侧：3D视图，右侧：2D图像）
        images_h_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：3D视图区域
        view_3d_widget = QWidget()
        view_3d_layout = QVBoxLayout(view_3d_widget)
        view_3d_layout.setContentsMargins(0, 0, 0, 0)
        
        # 右侧：2D图像区域
        view_2d_widget = QWidget()
        view_2d_layout = QVBoxLayout(view_2d_widget)
        view_2d_layout.setContentsMargins(0, 0, 0, 0)
        
        # 底部：控制面板区域（患者信息+视图选项）
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        
        # 将图像水平分割器添加到主垂直分割器的上部
        main_v_splitter.addWidget(images_h_splitter)
        # 将底部控制面板添加到主垂直分割器的下部
        main_v_splitter.addWidget(bottom_widget)
        
        return main_v_splitter, images_h_splitter, view_3d_widget, view_3d_layout, view_2d_widget, view_2d_layout, bottom_widget, bottom_layout
