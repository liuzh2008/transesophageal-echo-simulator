"""
主窗口模块 - 应用程序的主界面

此模块定义了应用程序的主窗口，包括菜单栏、工具栏、状态栏和主要视图布局。
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMenuBar, QMenu, QStatusBar,
                             QToolBar, QAction, QLabel, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

# 导入VTK组件
try:
    from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False
    print("警告: VTK不可用，3D渲染功能将受限")


class MainWindow(QMainWindow):
    """应用程序主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 窗口基本设置
        self.setWindowTitle("经食管超声心动图模拟器")
        self.setGeometry(100, 100, 1400, 900)  # x, y, width, height
        
        # 初始化UI组件
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
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 打开文件动作
        open_action = QAction("打开DICOM文件(&O)...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("打开DICOM影像文件")
        open_action.triggered.connect(self.open_dicom_file)
        file_menu.addAction(open_action)
        
        # 分隔线
        file_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出应用程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        # 3D视图动作
        view_3d_action = QAction("3D视图(&3)", self, checkable=True)
        view_3d_action.setChecked(True)
        view_3d_action.setStatusTip("显示/隐藏3D视图")
        view_3d_action.triggered.connect(self.toggle_3d_view)
        view_menu.addAction(view_3d_action)
        
        # 多平面视图动作
        view_mpr_action = QAction("多平面视图(&M)", self, checkable=True)
        view_mpr_action.setChecked(True)
        view_mpr_action.setStatusTip("显示/隐藏多平面视图")
        view_mpr_action.triggered.connect(self.toggle_mpr_view)
        view_menu.addAction(view_mpr_action)
        
        # 工具菜单
        tool_menu = menubar.addMenu("工具(&T)")
        
        # 测量工具
        measure_action = QAction("测量工具(&M)...", self)
        measure_action.setStatusTip("打开测量工具")
        tool_menu.addAction(measure_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 关于动作
        about_action = QAction("关于(&A)...", self)
        about_action.setStatusTip("显示关于信息")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 打开文件按钮
        open_action = QAction(QIcon(), "打开", self)
        open_action.setStatusTip("打开DICOM文件")
        open_action.triggered.connect(self.open_dicom_file)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # 3D视图按钮
        view_3d_action = QAction(QIcon(), "3D视图", self)
        view_3d_action.setStatusTip("切换3D视图")
        view_3d_action.triggered.connect(self.toggle_3d_view)
        toolbar.addAction(view_3d_action)
        
        # 多平面视图按钮
        view_mpr_action = QAction(QIcon(), "多平面视图", self)
        view_mpr_action.setStatusTip("切换多平面视图")
        view_mpr_action.triggered.connect(self.toggle_mpr_view)
        toolbar.addAction(view_mpr_action)
        
        toolbar.addSeparator()
        
        # 重置视图按钮
        reset_action = QAction(QIcon(), "重置视图", self)
        reset_action.setStatusTip("重置所有视图")
        reset_action.triggered.connect(self.reset_views)
        toolbar.addAction(reset_action)
    
    def create_main_content(self, main_layout):
        """创建主内容区域"""
        # 创建水平分割器（左侧3D视图，右侧控制面板）
        h_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：3D视图区域（70%）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 3D视图标签
        view_3d_label = QLabel("3D心脏视图")
        view_3d_label.setAlignment(Qt.AlignCenter)
        view_3d_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        left_layout.addWidget(view_3d_label)
        
        # 3D视图框架
        self.view_3d_frame = QFrame()
        self.view_3d_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.view_3d_frame.setLineWidth(2)
        self.view_3d_frame.setMinimumHeight(500)
        
        # 创建VTK渲染窗口（如果可用）
        if VTK_AVAILABLE:
            self.vtk_widget = QVTKRenderWindowInteractor(self.view_3d_frame)
            vtk_layout = QVBoxLayout(self.view_3d_frame)
            vtk_layout.addWidget(self.vtk_widget)
            vtk_layout.setContentsMargins(0, 0, 0, 0)
            
            # 初始化VTK渲染器
            self.init_vtk_renderer()
        else:
            # VTK不可用时显示占位符
            placeholder = QLabel("VTK 3D渲染引擎未安装\n请安装VTK以启用3D可视化功能")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder_layout = QVBoxLayout(self.view_3d_frame)
            placeholder_layout.addWidget(placeholder)
        
        left_layout.addWidget(self.view_3d_frame)
        
        # 右侧：控制面板区域（30%）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # 患者信息面板
        patient_panel = self.create_patient_panel()
        right_layout.addWidget(patient_panel)
        
        # 探头控制面板
        probe_panel = self.create_probe_control_panel()
        right_layout.addWidget(probe_panel)
        
        # 视图选项面板
        view_panel = self.create_view_options_panel()
        right_layout.addWidget(view_panel)
        
        # 添加弹性空间
        right_layout.addStretch()
        
        # 将左右部件添加到分割器
        h_splitter.addWidget(left_widget)
        h_splitter.addWidget(right_widget)
        
        # 设置分割比例（70%:30%）
        h_splitter.setSizes([980, 420])  # 总宽度1400px
        
        # 底部：多平面重建视图区域
        mpr_label = QLabel("多平面重建视图")
        mpr_label.setAlignment(Qt.AlignCenter)
        mpr_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        
        self.mpr_widget = QWidget()
        mpr_layout = QHBoxLayout(self.mpr_widget)
        mpr_layout.setContentsMargins(5, 5, 5, 5)
        mpr_layout.setSpacing(10)
        
        # 创建三个视图：轴向、冠状、矢状
        self.axial_view = self.create_mpr_view("轴向视图")
        self.coronal_view = self.create_mpr_view("冠状视图")
        self.sagittal_view = self.create_mpr_view("矢状视图")
        
        mpr_layout.addWidget(self.axial_view)
        mpr_layout.addWidget(self.coronal_view)
        mpr_layout.addWidget(self.sagittal_view)
        
        # 将组件添加到主布局
        main_layout.addWidget(h_splitter, 7)  # 70%高度
        main_layout.addWidget(mpr_label)
        main_layout.addWidget(self.mpr_widget, 3)  # 30%高度
    
    def create_patient_panel(self):
        """创建患者信息面板"""
        from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLineEdit
        
        panel = QGroupBox("患者信息")
        layout = QFormLayout(panel)
        
        # 患者ID
        self.patient_id_label = QLabel("未加载")
        layout.addRow("患者ID:", self.patient_id_label)
        
        # 患者姓名
        self.patient_name_label = QLabel("未加载")
        layout.addRow("患者姓名:", self.patient_name_label)
        
        # 检查日期
        self.study_date_label = QLabel("未加载")
        layout.addRow("检查日期:", self.study_date_label)
        
        # 模态
        self.modality_label = QLabel("未加载")
        layout.addRow("模态:", self.modality_label)
        
        return panel
    
    def create_probe_control_panel(self):
        """创建探头控制面板"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QSlider, QLabel
        
        panel = QGroupBox("探头控制")
        layout = QVBoxLayout(panel)
        
        # 位置控制
        pos_label = QLabel("探头位置:")
        pos_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(pos_label)
        
        # X轴位置
        x_layout = QHBoxLayout()
        x_label = QLabel("X:")
        self.x_slider = QSlider(Qt.Horizontal)
        self.x_slider.setRange(-100, 100)
        self.x_slider.setValue(0)
        self.x_slider.valueChanged.connect(self.update_probe_position)
        x_value = QLabel("0")
        self.x_slider.valueChanged.connect(lambda v: x_value.setText(str(v)))
        
        x_layout.addWidget(x_label)
        x_layout.addWidget(self.x_slider)
        x_layout.addWidget(x_value)
        layout.addLayout(x_layout)
        
        # Y轴位置
        y_layout = QHBoxLayout()
        y_label = QLabel("Y:")
        self.y_slider = QSlider(Qt.Horizontal)
        self.y_slider.setRange(-100, 100)
        self.y_slider.setValue(0)
        self.y_slider.valueChanged.connect(self.update_probe_position)
        y_value = QLabel("0")
        self.y_slider.valueChanged.connect(lambda v: y_value.setText(str(v)))
        
        y_layout.addWidget(y_label)
        y_layout.addWidget(self.y_slider)
        y_layout.addWidget(y_value)
        layout.addLayout(y_layout)
        
        # Z轴位置
        z_layout = QHBoxLayout()
        z_label = QLabel("Z:")
        self.z_slider = QSlider(Qt.Horizontal)
        self.z_slider.setRange(-100, 100)
        self.z_slider.setValue(0)
        self.z_slider.valueChanged.connect(self.update_probe_position)
        z_value = QLabel("0")
        self.z_slider.valueChanged.connect(lambda v: z_value.setText(str(v)))
        
        z_layout.addWidget(z_label)
        z_layout.addWidget(self.z_slider)
        z_layout.addWidget(z_value)
        layout.addLayout(z_layout)
        
        # 角度控制
        angle_label = QLabel("探头角度:")
        angle_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(angle_label)
        
        # RAO角度
        rao_layout = QHBoxLayout()
        rao_label = QLabel("RAO:")
        self.rao_slider = QSlider(Qt.Horizontal)
        self.rao_slider.setRange(0, 90)
        self.rao_slider.setValue(45)
        self.rao_slider.valueChanged.connect(self.update_probe_angle)
        rao_value = QLabel("45°")
        self.rao_slider.valueChanged.connect(lambda v: rao_value.setText(f"{v}°"))
        
        rao_layout.addWidget(rao_label)
        rao_layout.addWidget(self.rao_slider)
        rao_layout.addWidget(rao_value)
        layout.addLayout(rao_layout)
        
        # LAO角度
        lao_layout = QHBoxLayout()
        lao_label = QLabel("LAO:")
        self.lao_slider = QSlider(Qt.Horizontal)
        self.lao_slider.setRange(0, 90)
        self.lao_slider.setValue(45)
        self.lao_slider.valueChanged.connect(self.update_probe_angle)
        lao_value = QLabel("45°")
        self.lao_slider.valueChanged.connect(lambda v: lao_value.setText(f"{v}°"))
        
        lao_layout.addWidget(lao_label)
        lao_layout.addWidget(self.lao_slider)
        lao_layout.addWidget(lao_value)
        layout.addLayout(lao_layout)
        
        # 重置按钮
        from PyQt5.QtWidgets import QPushButton
        reset_button = QPushButton("重置探头位置")
        reset_button.clicked.connect(self.reset_probe_position)
        layout.addWidget(reset_button)
        
        return panel
    
    def create_view_options_panel(self):
        """创建视图选项面板"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QComboBox
        
        panel = QGroupBox("视图选项")
        layout = QVBoxLayout(panel)
        
        # 视图切换
        self.view_3d_checkbox = QCheckBox("显示3D视图")
        self.view_3d_checkbox.setChecked(True)
        self.view_3d_checkbox.stateChanged.connect(self.toggle_3d_view)
        layout.addWidget(self.view_3d_checkbox)
        
        self.view_mpr_checkbox = QCheckBox("显示多平面视图")
        self.view_mpr_checkbox.setChecked(True)
        self.view_mpr_checkbox.stateChanged.connect(self.toggle_mpr_view)
        layout.addWidget(self.view_mpr_checkbox)
        
        # 声窗显示
        self.show_fan_checkbox = QCheckBox("显示超声声窗")
        self.show_fan_checkbox.setChecked(True)
        self.show_fan_checkbox.stateChanged.connect(self.toggle_ultrasound_fan)
        layout.addWidget(self.show_fan_checkbox)
        
        # 渲染模式
        render_label = QLabel("渲染模式:")
        layout.addWidget(render_label)
        
        self.render_combo = QComboBox()
        self.render_combo.addItems(["体积渲染", "表面渲染", "线框渲染"])
        self.render_combo.currentTextChanged.connect(self.change_render_mode)
        layout.addWidget(self.render_combo)
        
        # 透明度控制
        opacity_label = QLabel("模型透明度:")
        layout.addWidget(opacity_label)
        
        from PyQt5.QtWidgets import QSlider
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(70)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        layout.addWidget(self.opacity_slider)
        
        return panel
    
    def create_mpr_view(self, title):
        """创建多平面重建视图"""
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        frame.setLineWidth(1)
        frame.setMinimumHeight(150)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(title_label)
        
        # 图像占位符
        image_label = QLabel("DICOM图像将在此显示")
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setMinimumSize(200, 150)
        image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        layout.addWidget(image_label)
        
        return frame
    
    def init_vtk_renderer(self):
        """初始化VTK渲染器"""
        if not VTK_AVAILABLE:
            return
        
        import vtk
        
        # 创建渲染器和渲染窗口
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        
        # 设置背景颜色
        self.renderer.SetBackground(0.1, 0.2, 0.4)  # 深蓝色背景
        
        # 创建测试几何体（一个球体）
        sphere_source = vtk.vtkSphereSource()
        sphere_source.SetRadius(50)
        sphere_source.SetThetaResolution(30)
        sphere_source.SetPhiResolution(30)
        
        # 创建映射器和演员
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere_source.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        # 设置演员属性
        actor.GetProperty().SetColor(0.9, 0.1, 0.1)  # 红色
        actor.GetProperty().SetOpacity(0.7)
        
        # 添加到渲染器
        self.renderer.AddActor(actor)
        
        # 添加坐标轴
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(60, 60, 60)
        axes.SetShaftTypeToCylinder()
        axes.SetCylinderRadius(0.02)
        self.renderer.AddActor(axes)
        
        # 重置相机
        self.renderer.ResetCamera()
        
        # 开始交互
        self.vtk_widget.Initialize()
        self.vtk_widget.Start()
    
    def create_status_bar(self):
        """创建状态栏"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # 添加永久部件
        self.status_label = QLabel("就绪")
        status_bar.addPermanentWidget(self.status_label)
    
    # 槽函数实现
    def open_dicom_file(self):
        """打开DICOM文件"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开DICOM文件",
            "",
            "DICOM文件 (*.dcm *.dicom);;所有文件 (*.*)"
        )
        
        if file_path:
            self.statusBar().showMessage(f"正在加载: {file_path}", 3000)
            # TODO: 实现DICOM加载逻辑
            print(f"打开文件: {file_path}")
    
    def toggle_3d_view(self, checked):
        """切换3D视图显示"""
        self.view_3d_frame.setVisible(checked)
        self.statusBar().showMessage(f"3D视图: {'显示' if checked else '隐藏'}", 2000)
    
    def toggle_mpr_view(self, checked):
        """切换多平面视图显示"""
        self.mpr_widget.setVisible(checked)
        self.statusBar().showMessage(f"多平面视图: {'显示' if checked else '隐藏'}", 2000)
    
    def toggle_ultrasound_fan(self, checked):
        """切换超声声窗显示"""
        self.statusBar().showMessage(f"超声声窗: {'显示' if checked else '隐藏'}", 2000)
        # TODO: 实现声窗显示/隐藏逻辑
    
    def update_probe_position(self):
        """更新探头位置"""
        x = self.x_slider.value()
        y = self.y_slider.value()
        z = self.z_slider.value()
        
        self.statusBar().showMessage(f"探头位置: X={x}, Y={y}, Z={z}", 1000)
        # TODO: 更新3D视图中的探头位置
    
    def update_probe_angle(self):
        """更新探头角度"""
        rao = self.rao_slider.value()
        lao = self.lao_slider.value()
        
        self.statusBar().showMessage(f"探头角度: RAO={rao}°, LAO={lao}°", 1000)
        # TODO: 更新3D视图中的探头角度
    
    def reset_probe_position(self):
        """重置探头位置"""
        self.x_slider.setValue(0)
        self.y_slider.setValue(0)
        self.z_slider.setValue(0)
        self.rao_slider.setValue(45)
        self.lao_slider.setValue(45)
        
        self.statusBar().showMessage("探头位置已重置", 2000)
    
    def reset_views(self):
        """重置所有视图"""
        if VTK_AVAILABLE:
            self.renderer.ResetCamera()
            self.vtk_widget.GetRenderWindow().Render()
        
        self.statusBar().showMessage("所有视图已重置", 2000)
    
    def change_render_mode(self, mode):
        """更改渲染模式"""
        self.statusBar().showMessage(f"渲染模式: {mode}", 2000)
        # TODO: 实现渲染模式切换逻辑
    
    def change_opacity(self, value):
        """更改模型透明度"""
        opacity = value / 100.0
        self.statusBar().showMessage(f"透明度: {value}%", 1000)
        
        if VTK_AVAILABLE:
            # 更新所有演员的透明度
            actors = self.renderer.GetActors()
            actors.InitTraversal()
            actor = actors.GetNextItem()
            while actor:
                actor.GetProperty().SetOpacity(opacity)
                actor = actors.GetNextItem()
            
            self.vtk_widget.GetRenderWindow().Render()
    
    def show_about(self):
        """显示关于对话框"""
        from PyQt5.QtWidgets import QMessageBox
        
        about_text = """
        <h3>经食管超声心动图模拟器</h3>
        <p>版本: 1.0.0 (DEMO)</p>
        <p>开发团队: 医疗影像实验室</p>
        <p>版权所有 © 2025</p>
        <hr>
        <p>此应用程序提供交互式的3D可视化工具，帮助临床医生理解和模拟TEE检查过程。</p>
        <p>技术支持: support@medical-imaging-lab.com</p>
        """
        
        QMessageBox.about(self, "关于", about_text)
