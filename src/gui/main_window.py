"""
主窗口模块 - 重构版本

此模块已按照关注点分享原则重构，作为应用程序的主控制器。
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStatusBar, QLabel
from PyQt5.QtCore import Qt

# 导入自定义模块
from .ui_components import UIComponents
from .vtk_manager import VTKManager
from .dicom_manager import DICOMManager
from .event_handlers import EventHandlers


class MainWindow(QMainWindow):
    """应用程序主窗口 - 重构版本"""
    
    # 版本号常量，格式：主版本.次版本.修订号
    VERSION = "0.1.001"
    
    def __init__(self):
        super().__init__()
        
        # 窗口基本设置
        self.setWindowTitle("DICOM影像查看器")
        self.setGeometry(100, 100, 1200, 800)  # x, y, width, height
        
        # 初始化管理器
        self.vtk_manager = VTKManager()
        self.dicom_manager = DICOMManager()
        self.event_handlers = EventHandlers(self, self.vtk_manager, self.dicom_manager)
        
        # 初始化UI组件
        self.ui_components = {}
        
        # 初始化用户界面
        self.init_ui()
        
        # 状态栏消息
        self.statusBar().showMessage("就绪", 3000)
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建主内容区域
        self.create_main_content(main_layout)
        
        # 创建状态栏
        self.create_status_bar()
        
        # 设置事件处理器
        self.setup_event_handlers()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar, menu_actions = UIComponents.create_menu_bar(self)
        self.setMenuBar(menubar)
        
        # 保存菜单动作引用
        self.ui_components.update(menu_actions)
    
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar, toolbar_actions = UIComponents.create_tool_bar(self)
        self.addToolBar(toolbar)
        
        # 保存工具栏动作引用
        self.ui_components.update(toolbar_actions)
    
    def create_main_content(self, main_layout):
        """创建主内容区域"""
        # 创建主布局结构（新的布局：上部图像区域，下部控制面板）
        main_v_splitter, images_h_splitter, view_3d_widget, view_3d_layout, view_2d_widget, view_2d_layout, bottom_widget, bottom_layout = \
            UIComponents.create_main_layout()
        
        # 创建3D视图框架
        view_3d_frame, view_3d_label = UIComponents.create_3d_view_frame()
        self.ui_components['view_3d_frame'] = view_3d_frame
        
        # 添加3D视图标签
        view_3d_layout.addWidget(view_3d_label)
        
        # 添加VTK小部件（如果可用）
        if self.vtk_manager.is_available():
            vtk_widget = self.vtk_manager.get_vtk_widget()
            if vtk_widget:
                vtk_layout = QVBoxLayout(view_3d_frame)
                vtk_layout.addWidget(vtk_widget)
                vtk_layout.setContentsMargins(0, 0, 0, 0)
        else:
            # VTK不可用时显示占位符
            placeholder = QLabel("VTK 3D渲染引擎未安装\n请安装VTK以启用3D可视化功能")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder_layout = QVBoxLayout(view_3d_frame)
            placeholder_layout.addWidget(placeholder)
        
        view_3d_layout.addWidget(view_3d_frame)
        
        # 创建2D视图框架（右侧区域）
        self._create_2d_view_area(view_2d_widget, view_2d_layout)
        
        # 将3D和2D部件添加到图像水平分割器
        images_h_splitter.addWidget(view_3d_widget)
        images_h_splitter.addWidget(view_2d_widget)
        
        # 设置图像水平分割比例（50%:50%）
        images_h_splitter.setSizes([600, 600])  # 总宽度1200px
        
        # 创建底部控制面板（患者信息+视图选项）
        self._create_bottom_panel(bottom_widget, bottom_layout)
        
        # 设置主垂直分割比例（70%:30%）
        main_v_splitter.setSizes([560, 240])  # 总高度800px
        
        # 将主垂直分割器添加到主布局
        main_layout.addWidget(main_v_splitter)
    
    def _create_2d_view_area(self, parent_widget, parent_layout):
        """创建2D视图区域（现在在右侧）"""
        from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout
        
        # 创建2D视图框架
        view_2d_frame = QFrame()
        view_2d_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        view_2d_frame.setLineWidth(2)
        view_2d_frame.setMinimumHeight(400)
        
        # 2D视图标签
        view_2d_label = QLabel("2D切片视图")
        view_2d_label.setAlignment(Qt.AlignCenter)
        view_2d_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        
        # 创建2D视图布局
        view_2d_frame_layout = QVBoxLayout(view_2d_frame)
        view_2d_frame_layout.addWidget(view_2d_label)
        
        # 创建占位符（稍后会被VTK小部件替换）
        self.view_2d_placeholder = QLabel("点击'显示50%位置横切面'按钮显示2D切片")
        self.view_2d_placeholder.setAlignment(Qt.AlignCenter)
        self.view_2d_placeholder.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
        view_2d_frame_layout.addWidget(self.view_2d_placeholder)
        
        # 保存2D视图框架引用
        self.ui_components['view_2d_frame'] = view_2d_frame
        self.ui_components['view_2d_label'] = view_2d_label
        
        # 将2D视图框架添加到父布局
        parent_layout.addWidget(view_2d_frame)
    
    def _create_bottom_panel(self, bottom_widget, bottom_layout):
        """创建底部控制面板（患者信息+视图选项）"""
        from PyQt5.QtWidgets import QHBoxLayout
        
        # 创建水平布局来并排显示患者信息和视图选项
        bottom_h_layout = QHBoxLayout()
        bottom_h_layout.setContentsMargins(0, 0, 0, 0)
        bottom_h_layout.setSpacing(20)
        
        # 创建患者信息面板
        patient_panel, patient_labels = UIComponents.create_patient_panel()
        self.ui_components.update(patient_labels)
        bottom_h_layout.addWidget(patient_panel)
        
        # 创建视图选项面板
        view_panel, view_controls = UIComponents.create_view_options_panel()
        self.ui_components.update(view_controls)
        bottom_h_layout.addWidget(view_panel)
        
        # 添加弹性空间
        bottom_h_layout.addStretch()
        
        # 将水平布局添加到底部部件
        bottom_layout.addLayout(bottom_h_layout)
    
    def create_status_bar(self):
        """创建状态栏"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # 添加永久部件
        self.status_label = QLabel("就绪")
        status_bar.addPermanentWidget(self.status_label)
    
    def setup_event_handlers(self):
        """设置事件处理器"""
        # 设置UI组件引用
        self.event_handlers.set_ui_components(self.ui_components)
        
        # 连接菜单动作
        if 'open_dir_action' in self.ui_components:
            self.ui_components['open_dir_action'].triggered.connect(
                self.event_handlers.handle_open_directory)
        
        if 'exit_action' in self.ui_components:
            self.ui_components['exit_action'].triggered.connect(
                self.event_handlers.handle_exit)
        
        if 'view_3d_action' in self.ui_components:
            self.ui_components['view_3d_action'].triggered.connect(
                self.event_handlers.handle_toggle_3d_view)
        
        if 'about_action' in self.ui_components:
            self.ui_components['about_action'].triggered.connect(
                self.event_handlers.handle_show_about)
        
        # 连接工具栏动作
        if 'view_3d_action' in self.ui_components:
            # 注意：这里可能和菜单动作是同一个对象，需要检查
            pass
        
        if 'reset_action' in self.ui_components:
            self.ui_components['reset_action'].triggered.connect(
                self.event_handlers.handle_reset_views)
        
        # 连接视图控制
        if 'view_3d_checkbox' in self.ui_components:
            self.ui_components['view_3d_checkbox'].stateChanged.connect(
                self.event_handlers.handle_toggle_3d_view)
        
        if 'render_combo' in self.ui_components:
            self.ui_components['render_combo'].currentTextChanged.connect(
                self.event_handlers.handle_change_render_mode)
        
        if 'opacity_slider' in self.ui_components:
            self.ui_components['opacity_slider'].valueChanged.connect(
                self.event_handlers.handle_change_opacity)
        
        # 连接切割平面按钮
        if 'cut_plane_button' in self.ui_components:
            self.ui_components['cut_plane_button'].clicked.connect(
                self.event_handlers.handle_show_cut_plane)
        
        # 连接 Omniplane 角度滑块 - 控制 TEE 探头扫描平面的旋转角度
        # 当滑块值改变时，触发 handle_omniplane_changed 方法更新 3D 切割平面和 2D 视图
        # @event_connection {QSlider.valueChanged} -> {EventHandlers.handle_omniplane_changed}
        # @param {int} value - 滑块当前值，范围 0-180 度
        if 'omniplane_slider' in self.ui_components:
            self.ui_components['omniplane_slider'].valueChanged.connect(
                self.event_handlers.handle_omniplane_changed)
        
        # 连接扇形顶点偏移滑动条
        for slider_key in ['fan_apex_x_slider', 'fan_apex_y_slider', 'fan_apex_z_slider']:
            if slider_key in self.ui_components:
                self.ui_components[slider_key].valueChanged.connect(
                    self.event_handlers.handle_fan_apex_offset_changed)
