"""
2D截面窗口模块 - 显示垂直于切割平面的2D切片图像

严格按照doc/sample code/transesophageal-echo-simulator/dicom_rao_lao_cut_analysis.md
中的create_slice_renderer函数实现方式。
"""

import warnings
import math
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

try:
    from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    import vtk
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False
    warnings.warn("VTK不可用，2D截面显示功能将受限")

try:
    from scipy.ndimage import map_coordinates as scipy_map_coordinates
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


# DEBUG 开关
_DEBUG = False


class CrossSectionWindow(QMainWindow):
    """
    2D截面窗口 - 显示垂直于切割平面的2D切片图像
    
    支持 Omniplane 角度旋转功能，可以模拟 TEE 探头在不同角度下的扫描平面显示。
    使用 Rodrigues 旋转公式实现扫描平面坐标系的旋转。
    """
    
    def __init__(self, image_data, normal_vector, cut_position, parent=None,
                 plane_origin=None, plane_x_axis=None, plane_y_axis=None,
                 fan_apex_offset_x=0.0, fan_apex_offset_y=0.0, fan_apex_offset_z=0.0,
                 omniplane_angle=0):
        """
        初始化2D截面窗口
        
        参数:
            image_data (vtk.vtkImageData): 3D体积数据
            normal_vector (tuple): 切割平面法线向量 (nx, ny, nz)
            cut_position (float): 切割位置（百分比或实际坐标）
            parent (QWidget, 可选): 父窗口
            plane_origin (tuple, 可选): 平面原点 (x, y, z)，用于精确定位切割位置
            plane_x_axis (tuple, 可选): 平面X轴方向（归一化向量），定义切片局部坐标系的X方向
            plane_y_axis (tuple, 可选): 平面Y轴方向（归一化向量），定义切片局部坐标系的Y方向
            fan_apex_offset_x (float, 可选): 扇形顶点X方向物理偏移量，基于切片局部坐标系，默认为0.0
            fan_apex_offset_y (float, 可选): 扇形顶点Y方向物理偏移量，基于切片局部坐标系，默认为0.0
            fan_apex_offset_z (float, 可选): 扇形顶点Z方向物理偏移量，沿法线方向，默认为0.0
            omniplane_angle (int, 可选): Omniplane旋转角度（0-180度），控制扫描平面绕法线旋转，默认为0
        
        属性:
            omniplane_angle (int): 存储当前的 Omniplane 角度值，用于渲染器创建扇形视图
        """
        super().__init__(parent)
        
        self.image_data = image_data
        self.normal_vector = normal_vector
        self.cut_position = cut_position
        
        # 存储平面参数（用于精确定位切割位置）
        self.plane_origin = plane_origin
        self.plane_x_axis = plane_x_axis
        self.plane_y_axis = plane_y_axis
        
        # 存储扇形顶点偏移参数
        self.fan_apex_offset_x = fan_apex_offset_x
        self.fan_apex_offset_y = fan_apex_offset_y
        self.fan_apex_offset_z = fan_apex_offset_z
        
        # 存储Omniplane角度
        self.omniplane_angle = omniplane_angle
        
        # 窗口设置
        self.setWindowTitle(f"2D切片视图 - 法线: {normal_vector}")
        self.setGeometry(200, 200, 600, 600)
        
        # 初始化UI
        self.init_ui()
        
        # 状态栏
        self.statusBar().showMessage("2D切片视图已就绪", 3000)
    
    def init_ui(self):
        """初始化用户界面"""
        if not VTK_AVAILABLE:
            self._show_vtk_unavailable_message()
            return
        
        try:
            # 创建中央部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # 主布局
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # 创建VTK小部件
            self.vtk_widget = QVTKRenderWindowInteractor(central_widget)
            
            # 创建2D切片渲染器
            self.renderer_2d = self.create_slice_renderer()
            
            if self.renderer_2d is not None:
                # 添加渲染器到VTK窗口
                self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer_2d)
                
                # 将VTK小部件添加到布局
                main_layout.addWidget(self.vtk_widget)
                
                # 开始交互
                self.vtk_widget.Initialize()
                self.vtk_widget.Start()
                
                # 渲染窗口
                self.vtk_widget.GetRenderWindow().Render()
            else:
                self._show_renderer_error_message()
                
        except Exception as e:
            warnings.warn(f"初始化2D切片窗口失败: {e}")
            self._show_error_message(str(e))
    
    def create_slice_renderer(self):
        """
        创建2D切片渲染器
        
        直接从3D体积数据进行扇形采样，避免双重插值
        返回: vtkRenderer对象或None
        """
        return _create_slice_renderer_internal(
            self.image_data, self.normal_vector, self.cut_position,
            plane_origin=self.plane_origin,
            plane_x_axis=self.plane_x_axis,
            plane_y_axis=self.plane_y_axis,
            fan_apex_offset_x=self.fan_apex_offset_x,
            fan_apex_offset_y=self.fan_apex_offset_y,
            fan_apex_offset_z=self.fan_apex_offset_z,
            omniplane_angle=self.omniplane_angle
        )
    
    def _show_vtk_unavailable_message(self):
        """显示VTK不可用消息"""
        from PyQt5.QtWidgets import QLabel
        from PyQt5.QtCore import Qt
        
        label = QLabel("VTK 3D渲染引擎未安装\n请安装VTK以启用2D切片显示功能")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 14px; color: red; padding: 20px;")
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(label)
        self.setCentralWidget(central_widget)
    
    def _show_renderer_error_message(self):
        """显示渲染器错误消息"""
        from PyQt5.QtWidgets import QLabel
        from PyQt5.QtCore import Qt
        
        label = QLabel("无法创建2D切片渲染器\n体积数据可能为空或无效")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 14px; color: red; padding: 20px;")
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(label)
        self.setCentralWidget(central_widget)
    
    def _show_error_message(self, error_text):
        """显示错误消息"""
        from PyQt5.QtWidgets import QLabel
        from PyQt5.QtCore import Qt
        
        label = QLabel(f"初始化2D切片窗口时出错:\n{error_text}")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 12px; color: red; padding: 20px;")
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(label)
        self.setCentralWidget(central_widget)
    
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        if hasattr(self, 'vtk_widget') and self.vtk_widget:
            self.vtk_widget.Finalize()
        event.accept()


def create_cross_section_window(image_data, normal_vector, cut_position, parent=None,
                                plane_origin=None, plane_x_axis=None, plane_y_axis=None,
                                fan_apex_offset_x=0.0, fan_apex_offset_y=0.0, fan_apex_offset_z=0.0,
                                omniplane_angle=0):
    """
    创建并显示2D切片窗口的便捷函数
    
    支持 Omniplane 角度旋转功能，可以创建具有特定角度旋转的 2D 切片窗口。
    使用 Rodrigues 旋转公式实现扫描平面坐标系的旋转，模拟真实 TEE 探头的角度扫描。
    
    参数:
        image_data (vtk.vtkImageData): 3D体积数据，包含DICOM图像信息
        normal_vector (tuple): 切割平面法线向量 (nx, ny, nz)，定义切片方向
        cut_position (float): 切割位置（百分比），0.0-1.0之间，0.5表示50%位置
        parent (QWidget, 可选): 父窗口部件，用于窗口层次结构
        plane_origin (tuple, 可选): 平面原点 (x, y, z)，用于精确定位切割位置
        plane_x_axis (tuple, 可选): 平面X轴方向（归一化向量），定义切片局部坐标系的X方向
        plane_y_axis (tuple, 可选): 平面Y轴方向（归一化向量），定义切片局部坐标系的Y方向
        fan_apex_offset_x (float, 可选): 扇形顶点X方向物理偏移量，基于切片局部坐标系，默认为0.0
        fan_apex_offset_y (float, 可选): 扇形顶点Y方向物理偏移量，基于切片局部坐标系，默认为0.0
        fan_apex_offset_z (float, 可选): 扇形顶点Z方向物理偏移量，沿法线方向，默认为0.0
        omniplane_angle (int, 可选): Omniplane旋转角度（0-180度），控制扫描平面绕法线旋转，默认为0
        
    返回:
        CrossSectionWindow: 创建的2D切片窗口实例，包含指定的Omniplane角度设置
        
    逻辑:
        1. 创建 CrossSectionWindow 实例，传入所有参数包括 omniplane_angle
        2. 设置窗口标志确保作为独立窗口显示
        3. 显示窗口并激活
        4. 返回窗口实例
        
    示例:
        >>> # 创建标准 0 度切片窗口
        >>> window = create_cross_section_window(vtk_image, (0, 0, 1), 0.5)
        >>> print(window.windowTitle())
        "2D切片视图 - 法线: (0, 0, 1)"
        
        >>> # 创建 45 度 Omniplane 角度的切片窗口
        >>> window = create_cross_section_window(
        ...     vtk_image, (0, 0, 1), 0.5, omniplane_angle=45
        ... )
        
    相关文件:
        src/gui/cross_section_window.py
        src/gui/vtk_manager.py
        src/core/volume_render.py
    """
    window = CrossSectionWindow(
        image_data, normal_vector, cut_position, parent,
        plane_origin=plane_origin,
        plane_x_axis=plane_x_axis,
        plane_y_axis=plane_y_axis,
        fan_apex_offset_x=fan_apex_offset_x,
        fan_apex_offset_y=fan_apex_offset_y,
        fan_apex_offset_z=fan_apex_offset_z,
        omniplane_angle=omniplane_angle
    )
    
    # 确保窗口作为独立窗口显示
    window.setWindowFlags(window.windowFlags() | Qt.Window)
    
    # 显示窗口
    window.show()
    window.raise_()  # 将窗口提到最前面
    window.activateWindow()  # 激活窗口
    
    if _DEBUG:
        print(f"[DEBUG] 2D切片窗口已显示，标题: {window.windowTitle()}")
    return window


def create_embedded_2d_view(image_data, normal_vector, cut_position, parent_widget,
                            plane_origin=None, plane_x_axis=None, plane_y_axis=None,
                            fan_apex_offset_x=0.0, fan_apex_offset_y=0.0, fan_apex_offset_z=0.0,
                            omniplane_angle=0):
    """
    创建内嵌的2D视图小部件（用于在主窗口中显示）
    
    支持 Omniplane 角度旋转功能，可以在主窗口中显示具有特定角度旋转的 2D 切片。
    使用 Rodrigues 旋转公式实现扫描平面坐标系的旋转，模拟真实 TEE 探头的角度扫描。
    
    参数:
        image_data (vtk.vtkImageData): 3D体积数据
        normal_vector (tuple): 切割平面法线向量 (nx, ny, nz)
        cut_position (float): 切割位置（百分比），0.0-1.0之间
        parent_widget (QWidget): 父窗口部件
        plane_origin (tuple, 可选): 平面原点 (x, y, z)，用于精确定位切割位置
        plane_x_axis (tuple, 可选): 平面X轴方向（归一化向量），定义切片局部坐标系的X方向
        plane_y_axis (tuple, 可选): 平面Y轴方向（归一化向量），定义切片局部坐标系的Y方向
        fan_apex_offset_x (float, 可选): 扇形顶点X方向物理偏移量，基于切片局部坐标系，默认为0.0
        fan_apex_offset_y (float, 可选): 扇形顶点Y方向物理偏移量，基于切片局部坐标系，默认为0.0
        fan_apex_offset_z (float, 可选): 扇形顶点Z方向物理偏移量，沿法线方向，默认为0.0
        omniplane_angle (int, 可选): Omniplane旋转角度（0-180度），控制扫描平面绕法线旋转，默认为0
        
    返回:
        QVTKRenderWindowInteractor: 包含2D切片渲染的VTK小部件，如果创建失败则返回None
        
    示例:
        >>> # 创建标准 0 度内嵌视图
        >>> widget = create_embedded_2d_view(
        ...     image_data, (0, 0, 1), 0.5, parent_widget=main_window
        ... )
        >>>
        >>> # 创建 90 度 Omniplane 角度的内嵌视图
        >>> widget = create_embedded_2d_view(
        ...     image_data, (0, 0, 1), 0.5, parent_widget=main_window,
        ...     omniplane_angle=90
        ... )
    """
    if not VTK_AVAILABLE or image_data is None:
        return None
    
    try:
        # 创建VTK小部件
        vtk_widget = QVTKRenderWindowInteractor(parent_widget)
        
        # 创建2D切片渲染器（使用CrossSectionWindow的相同逻辑）
        renderer = _create_slice_renderer_internal(
            image_data, normal_vector, cut_position,
            plane_origin=plane_origin,
            plane_x_axis=plane_x_axis,
            plane_y_axis=plane_y_axis,
            fan_apex_offset_x=fan_apex_offset_x,
            fan_apex_offset_y=fan_apex_offset_y,
            fan_apex_offset_z=fan_apex_offset_z,
            omniplane_angle=omniplane_angle
        )
        
        if renderer is not None:
            # 添加渲染器到VTK窗口
            vtk_widget.GetRenderWindow().AddRenderer(renderer)
            
            # 开始交互
            vtk_widget.Initialize()
            vtk_widget.Start()
            
            # 渲染窗口
            vtk_widget.GetRenderWindow().Render()
            
            return vtk_widget
        else:
            return None
            
    except Exception as e:
        warnings.warn(f"创建内嵌2D视图失败: {e}")
        return None


# 扇形采样预计算缓存
_fan_cache = {}


def _get_fan_geometry_cache(fan_angle, output_size, fan_apex_x, fan_apex_y, pixel_to_physical, near_depth, far_depth):
    """获取或创建缓存的扇形几何数据（极坐标网格、掩码等）"""
    import numpy as np
    cache_key = (fan_angle, output_size, fan_apex_x, fan_apex_y, pixel_to_physical, near_depth, far_depth)
    if cache_key in _fan_cache:
        return _fan_cache[cache_key]
    
    half_angle_rad = math.radians(fan_angle / 2.0)
    y_indices, x_indices = np.mgrid[0:output_size, 0:output_size]
    dx = (x_indices - fan_apex_x).astype(np.float64)
    dy = (y_indices - fan_apex_y).astype(np.float64)
    r_pixels = np.sqrt(dx**2 + dy**2)
    theta = np.arctan2(dx, dy)
    r_physical = r_pixels * pixel_to_physical
    
    mask = (np.abs(theta) <= half_angle_rad) & \
           (r_physical >= near_depth) & \
           (r_physical <= far_depth)
    
    theta_masked = theta[mask]
    r_physical_masked = r_physical[mask]
    
    # 预计算 sin/cos
    sin_theta = np.sin(theta_masked)
    cos_theta = np.cos(theta_masked)
    plane_x_offset = r_physical_masked * sin_theta
    plane_y_offset = r_physical_masked * cos_theta
    
    fan_coords = np.where(mask)
    
    result = {
        'mask': mask,
        'plane_x_offset': plane_x_offset,
        'plane_y_offset': plane_y_offset,
        'fan_coords': fan_coords,
    }
    _fan_cache[cache_key] = result
    return result


def _create_slice_renderer_internal(image_data, normal_vector, cut_position,
                                     plane_origin=None, plane_x_axis=None, plane_y_axis=None,
                                     fan_apex_offset_x=0.0, fan_apex_offset_y=0.0, fan_apex_offset_z=0.0,
                                     omniplane_angle=0):
    """
    内部函数：创建2D切片渲染器 - 直接从3D体积数据扇形采样
    
    核心渲染函数，支持 Omniplane 角度旋转功能。使用 Rodrigues 旋转公式实现
    扫描平面坐标系绕法线向量的旋转，模拟真实 TEE 探头的角度扫描能力。
    
    参数:
        image_data (vtk.vtkImageData): 3D体积数据
        normal_vector (tuple): 切割平面法线向量 (nx, ny, nz)
        cut_position (float): 切割位置（百分比），0.0-1.0之间
        plane_origin (tuple, 可选): 平面原点 (x, y, z)，用于精确定位切割位置
        plane_x_axis (tuple, 可选): 平面X轴方向（归一化向量），定义切片局部坐标系的X方向
        plane_y_axis (tuple, 可选): 平面Y轴方向（归一化向量），定义切片局部坐标系的Y方向
        fan_apex_offset_x (float, 可选): 扇形顶点X方向物理偏移量，基于切片局部坐标系，默认为0.0
        fan_apex_offset_y (float, 可选): 扇形顶点Y方向物理偏移量，基于切片局部坐标系，默认为0.0
        fan_apex_offset_z (float, 可选): 扇形顶点Z方向物理偏移量，沿法线方向，默认为0.0
        omniplane_angle (int, 可选): Omniplane旋转角度（0-180度），控制扫描平面绕法线旋转，默认为0
        
    返回:
        vtk.vtkRenderer: 配置好的2D切片渲染器对象，如果创建失败则返回None
        
    技术细节:
        Omniplane 旋转处理:
            1. 当传入 plane_x_axis 和 plane_y_axis 时，直接使用这些坐标轴（已在外部计算旋转）
            2. 当需要回退计算坐标系时，根据 omniplane_angle 应用 Rodrigues 旋转公式：
               v_rot = v * cos(θ) + (k × v) * sin(θ) + k * (k · v) * (1 - cos(θ))
            3. 旋转轴 k 为法线向量，旋转角度 θ 为 omniplane_angle 转换为弧度
        
        TEE 扇形采样:
            - 使用极坐标网格进行扇形采样
            - 通过矩阵乘法将扇形坐标转换为世界坐标
            - 使用 scipy.ndimage.map_coordinates 进行三线性插值
    """
    if not VTK_AVAILABLE or image_data is None:
        return None
    
    try:
        nx, ny, nz = normal_vector
        
        # 判断是否使用传入的平面参数
        if plane_origin is not None:
            # 使用传入的精确平面原点
            center = list(plane_origin)
            if _DEBUG:
                print(f"[DEBUG] _create_slice_renderer_internal 使用传入的平面原点: ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})")
        else:
            # 回退到体积中心（后向兼容）
            bounds = image_data.GetBounds()
            center = [
                (bounds[0] + bounds[1]) / 2,
                (bounds[2] + bounds[3]) / 2,
                (bounds[4] + bounds[5]) / 2
            ]
            if _DEBUG:
                print(f"[DEBUG] _create_slice_renderer_internal 使用体积中心: ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})")
        
        # 判断是否使用传入的平面坐标系
        if plane_x_axis is not None and plane_y_axis is not None:
            # 使用传入的精确平面坐标系
            x_axis = plane_x_axis
            y_axis = plane_y_axis
            if _DEBUG:
                print(f"[DEBUG] _create_slice_renderer_internal 使用传入的平面X轴: ({x_axis[0]:.3f}, {x_axis[1]:.3f}, {x_axis[2]:.3f})")
                print(f"[DEBUG] _create_slice_renderer_internal 使用传入的平面Y轴: ({y_axis[0]:.3f}, {y_axis[1]:.3f}, {y_axis[2]:.3f})")
        else:
            # 回退到计算坐标系（后向兼容）
            # 设置切片方向（垂直于法线向量）
            if abs(nx) < 0.5:
                ref_vector = (1, 0, 0)
            else:
                ref_vector = (0, 1, 0)
            
            # 计算X轴（与法线向量正交）
            ref_x, ref_y, ref_z = ref_vector
            x_axis = (
                ref_y * nz - ref_z * ny,
                ref_z * nx - ref_x * nz,
                ref_x * ny - ref_y * nx
            )
            
            # 计算向量长度
            x_length = math.sqrt(x_axis[0]**2 + x_axis[1]**2 + x_axis[2]**2)
            
            if x_length < 0.001:
                # 如果叉积太小，尝试另一个参考向量
                ref_vector = (0, 0, 1)
                ref_x, ref_y, ref_z = ref_vector
                x_axis = (
                    ref_y * nz - ref_z * ny,
                    ref_z * nx - ref_x * nz,
                    ref_x * ny - ref_y * nx
                )
                x_length = math.sqrt(x_axis[0]**2 + x_axis[1]**2 + x_axis[2]**2)
            
            # 归一化X轴
            if x_length > 0:
                x_axis = (x_axis[0]/x_length, x_axis[1]/x_length, x_axis[2]/x_length)
            
            # 计算Y轴
            y_axis = (
                ny * x_axis[2] - nz * x_axis[1],
                nz * x_axis[0] - nx * x_axis[2],
                nx * x_axis[1] - ny * x_axis[0]
            )
            
            y_length = math.sqrt(y_axis[0]**2 + y_axis[1]**2 + y_axis[2]**2)
            if y_length > 0:
                y_axis = (y_axis[0]/y_length, y_axis[1]/y_length, y_axis[2]/y_length)
            
            if _DEBUG:
                print(f"[DEBUG] _create_slice_renderer_internal 计算的X轴: ({x_axis[0]:.3f}, {x_axis[1]:.3f}, {x_axis[2]:.3f})")
                print(f"[DEBUG] _create_slice_renderer_internal 计算的Y轴: ({y_axis[0]:.3f}, {y_axis[1]:.3f}, {y_axis[2]:.3f})")
            
            # =====================================================
            # Omniplane 旋转（仅在回退计算坐标系时应用）
            # =====================================================
            # 当没有传入预计算的 plane_x_axis 和 plane_y_axis 时，
            # 需要在这里根据 omniplane_angle 计算旋转后的坐标系。
            #
            # Rodrigues 旋转公式：
            #   v_rot = v * cos(θ) + (k × v) * sin(θ) + k * (k · v) * (1 - cos(θ))
            #
            # 其中：
            #   - v: 待旋转的向量（x_axis 或 y_axis）
            #   - k: 旋转轴单位向量（归一化的法线向量）
            #   - θ: 旋转角度（omniplane_angle 转换为弧度）
            #   - ×: 向量叉积
            #   - ·: 向量点积
            #
            # 此旋转模拟 TEE 探头的 Omniplane 功能，在不移动探头的情况下
            # 通过电子控制改变超声扫描平面的角度。
            # =====================================================
            if omniplane_angle != 0:
                import numpy as np
                import math as _math
                
                # 将角度从度转换为弧度
                theta = _math.radians(omniplane_angle)
                # 预计算三角函数值
                cos_t = _math.cos(theta)
                sin_t = _math.sin(theta)
                
                # 构建归一化的法线向量作为旋转轴 k
                normal_array = np.array([nx, ny, nz], dtype=np.float64)
                normal_length = np.linalg.norm(normal_array)
                if normal_length > 0:
                    k = normal_array / normal_length  # 归一化旋转轴
                else:
                    k = normal_array
                
                def rodrigues_rotate(v, k, cos_t, sin_t):
                    """
                    Rodrigues 旋转公式实现
                    
                    参数:
                        v (np.array): 待旋转的向量
                        k (np.array): 旋转轴单位向量
                        cos_t (float): cos(θ) 预计算值
                        sin_t (float): sin(θ) 预计算值
                    
                    返回:
                        np.array: 旋转后的向量
                    
                    数学公式:
                        v_rot = v*cos(θ) + (k×v)*sin(θ) + k*(k·v)*(1-cos(θ))
                    """
                    # 计算 k × v（旋转轴与向量的叉积）
                    kxv = np.cross(k, v)
                    # 计算 k · v（旋转轴与向量的点积）
                    kdv = np.dot(k, v)
                    # 组合三项得到旋转后的向量
                    return v * cos_t + kxv * sin_t + k * kdv * (1 - cos_t)
                
                # 应用旋转到平面坐标系的 X 轴和 Y 轴
                px = rodrigues_rotate(np.array(x_axis), k, cos_t, sin_t)
                py = rodrigues_rotate(np.array(y_axis), k, cos_t, sin_t)
                x_axis = tuple(px.tolist())
                y_axis = tuple(py.tolist())
        
        # 应用扇形顶点偏移（基于切片局部坐标系）
        center[0] += fan_apex_offset_x * x_axis[0] + fan_apex_offset_y * y_axis[0] + fan_apex_offset_z * nx
        center[1] += fan_apex_offset_x * x_axis[1] + fan_apex_offset_y * y_axis[1] + fan_apex_offset_z * ny
        center[2] += fan_apex_offset_x * x_axis[2] + fan_apex_offset_y * y_axis[2] + fan_apex_offset_z * nz
        if _DEBUG:
            print(f"[DEBUG] _create_slice_renderer_internal 应用偏移后的中心: ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})")
        
        # =====================================================
        # TEE扇形视图处理 - 直接从3D体积采样
        # =====================================================
        import numpy as np
        from vtkmodules.util import numpy_support
        
        # TEE扇形视图参数
        fan_angle = 60.0  # 扇形角度（度）
        output_size = 256  # 输出图像尺寸（优化：从512降至256提升4倍性能）
        
        # 计算扇形顶点位置（顶部中心）
        fan_apex_x = output_size / 2.0
        fan_apex_y = output_size * 0.05
        
        # 直接从3D体积数据创建扇形图像
        fan_image, far_field_depth = _create_tee_fan_image_internal(
            image_data, center, x_axis, y_axis,
            fan_angle=fan_angle, output_size=output_size,
            fan_apex_x=fan_apex_x, fan_apex_y=fan_apex_y
        )
        
        # 将扇形图像转换回VTK
        vtk_array_type = image_data.GetPointData().GetScalars().GetDataType()
        fan_vtk_array = numpy_support.numpy_to_vtk(
            fan_image.ravel(),
            deep=True,
            array_type=vtk_array_type
        )
        
        # 设置输出图像参数
        spacing = (1.0, 1.0, 1.0)
        origin = (0.0, 0.0, 0.0)
        
        fan_vtk_image = vtk.vtkImageData()
        fan_vtk_image.SetDimensions(output_size, output_size, 1)
        fan_vtk_image.SetSpacing(spacing)
        fan_vtk_image.SetOrigin(origin)
        fan_vtk_image.GetPointData().SetScalars(fan_vtk_array)
        
        # 使用vtkImageSliceMapper显示
        image_slice_mapper = vtk.vtkImageSliceMapper()
        image_slice_mapper.SetInputData(fan_vtk_image)
        image_slice_mapper.SliceAtFocalPointOn()
        image_slice_mapper.SliceFacesCameraOn()
        
        # 创建图像属性
        scalar_range = fan_vtk_image.GetScalarRange()
        min_val, max_val = scalar_range
        if _DEBUG:
            print(f"[DEBUG] _create_slice_renderer_internal 数据范围: {min_val:.1f} 到 {max_val:.1f}")
        
        image_property = vtk.vtkImageProperty()
        if max_val - min_val > 0:
            if max_val <= 1.0 and min_val >= 0.0:
                image_property.SetColorWindow(1.0)
                image_property.SetColorLevel(0.5)
            else:
                image_property.SetColorWindow(max_val - min_val)
                image_property.SetColorLevel((max_val + min_val) / 2)
        else:
            image_property.SetColorWindow(400)
            image_property.SetColorLevel(40)
        
        image_slice = vtk.vtkImageSlice()
        image_slice.SetMapper(image_slice_mapper)
        image_slice.SetProperty(image_property)
        
        # 创建渲染器
        renderer = vtk.vtkRenderer()
        renderer.AddViewProp(image_slice)
        renderer.SetBackground(0.05, 0.05, 0.1)  # 深色背景
        
        # 计算扇形在像素坐标中的半径
        fan_radius_pixels = output_size * 0.85
        
        # 创建扇形边界线Actor
        fan_outline = _create_fan_outline_actor_internal(
            output_size, output_size, fan_apex_x, fan_apex_y, fan_angle, 
            fan_radius_pixels, spacing, origin)
        if fan_outline is not None:
            renderer.AddActor(fan_outline)
        
        # 添加TEE文本标注
        text_actor = vtk.vtkTextActor()
        text_actor.SetInput(
            f"TEE扇形视图（直接3D采样）\n法线: ({nx:.2f}, {ny:.2f}, {nz:.2f})\n扇角: {fan_angle}° 深度: {far_field_depth:.1f}mm")
        text_actor.GetTextProperty().SetFontSize(12)
        text_actor.GetTextProperty().SetColor(1, 1, 1)
        text_actor.GetTextProperty().SetBackgroundColor(0, 0, 0)
        text_actor.GetTextProperty().SetBackgroundOpacity(0.7)
        text_actor.SetPosition(10, 10)
        renderer.AddActor2D(text_actor)
        
        # 设置相机
        renderer.ResetCamera()
        camera = renderer.GetActiveCamera()
        camera.ParallelProjectionOn()
        
        if _DEBUG:
            print(f"[DEBUG] _create_slice_renderer_internal TEE扇形切片渲染器创建完成（直接3D采样）")
        return renderer
        
    except Exception as e:
        import traceback
        print(f"[ERROR] 创建2D切片渲染器失败: {e}")
        traceback.print_exc()
        return None


def _create_tee_fan_image_internal(vtk_image_data, plane_origin, plane_x_axis, plane_y_axis,
                                   fan_angle=60.0, output_size=256,
                                   fan_apex_x=None, fan_apex_y=None):
    """
    内部函数：真实TEE扇形切割 - 直接从3D体积数据采样（性能优化版）
    """
    import numpy as np
    from vtk.util import numpy_support
    
    # 获取体积参数
    dims = vtk_image_data.GetDimensions()
    spacing = vtk_image_data.GetSpacing()
    origin = vtk_image_data.GetOrigin()
    
    # 获取体积numpy数据
    scalars = vtk_image_data.GetPointData().GetScalars()
    volume_np = numpy_support.vtk_to_numpy(scalars)
    volume_np = volume_np.reshape(dims[2], dims[1], dims[0])
    
    # 计算扇形物理范围
    physical_extent_x = (dims[0] - 1) * spacing[0]
    physical_extent_y = (dims[1] - 1) * spacing[1]
    physical_extent_z = (dims[2] - 1) * spacing[2]
    max_physical_extent = max(physical_extent_x, physical_extent_y, physical_extent_z)
    
    near_depth = 0.0
    far_depth = max_physical_extent * 0.5
    
    if fan_apex_x is None:
        fan_apex_x = output_size / 2.0
    if fan_apex_y is None:
        fan_apex_y = output_size * 0.05
    
    pixel_to_physical = far_depth / (output_size * 0.85)
    
    # 使用预计算的扇形几何缓存
    geo = _get_fan_geometry_cache(fan_angle, output_size, fan_apex_x, fan_apex_y,
                                  pixel_to_physical, near_depth, far_depth)
    
    plane_x_offset = geo['plane_x_offset']
    plane_y_offset = geo['plane_y_offset']
    mask = geo['mask']
    fan_coords = geo['fan_coords']
    
    # 使用矩阵乘法计算世界坐标
    transform_matrix = np.array([
        [plane_x_axis[0], plane_y_axis[0]],
        [plane_x_axis[1], plane_y_axis[1]],
        [plane_x_axis[2], plane_y_axis[2]]
    ])  # 3x2
    
    offsets = np.column_stack([plane_x_offset, plane_y_offset])  # Nx2
    world_coords = np.array(plane_origin)[:, None] + transform_matrix @ offsets.T  # 3xN
    
    world_x = world_coords[0]
    world_y = world_coords[1]
    world_z = world_coords[2]
    
    # 转换为体素索引
    vox_x = (world_x - origin[0]) / spacing[0]
    vox_y = (world_y - origin[1]) / spacing[1]
    vox_z = (world_z - origin[2]) / spacing[2]
    
    # 边界检查
    valid = (vox_x >= 0) & (vox_x < dims[0] - 1) & \
            (vox_y >= 0) & (vox_y < dims[1] - 1) & \
            (vox_z >= 0) & (vox_z < dims[2] - 1)
    
    # 初始化输出图像
    fan_image = np.zeros((output_size, output_size), dtype=np.float32)
    
    if np.any(valid):
        vox_x_valid = vox_x[valid]
        vox_y_valid = vox_y[valid]
        vox_z_valid = vox_z[valid]
        
        # 使用 scipy.ndimage.map_coordinates 进行三线性插值（C优化实现）
        if SCIPY_AVAILABLE:
            coords = np.array([vox_z_valid, vox_y_valid, vox_x_valid])
            sampled_values = scipy_map_coordinates(volume_np, coords, order=1, mode='constant', cval=0.0)
        else:
            # 回退到手写三线性插值
            x0 = np.floor(vox_x_valid).astype(np.int32)
            y0 = np.floor(vox_y_valid).astype(np.int32)
            z0 = np.floor(vox_z_valid).astype(np.int32)
            x1 = x0 + 1
            y1 = y0 + 1
            z1 = z0 + 1
            
            xd = vox_x_valid - x0
            yd = vox_y_valid - y0
            zd = vox_z_valid - z0
            
            c000 = volume_np[z0, y0, x0]
            c001 = volume_np[z0, y0, x1]
            c010 = volume_np[z0, y1, x0]
            c011 = volume_np[z0, y1, x1]
            c100 = volume_np[z1, y0, x0]
            c101 = volume_np[z1, y0, x1]
            c110 = volume_np[z1, y1, x0]
            c111 = volume_np[z1, y1, x1]
            
            c00 = c000 * (1 - xd) + c001 * xd
            c01 = c010 * (1 - xd) + c011 * xd
            c10 = c100 * (1 - xd) + c101 * xd
            c11 = c110 * (1 - xd) + c111 * xd
            
            c0 = c00 * (1 - yd) + c01 * yd
            c1 = c10 * (1 - yd) + c11 * yd
            
            sampled_values = c0 * (1 - zd) + c1 * zd
        
        # 写入输出图像
        valid_fan_coords = (fan_coords[0][valid], fan_coords[1][valid])
        fan_image[valid_fan_coords] = sampled_values
    
    return fan_image, far_depth


def _create_fan_outline_actor_internal(width, height, apex_x, apex_y, fan_angle, fan_radius, spacing, origin):
    """
    内部函数：创建扇形边界线Actor
    """
    try:
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()
        
        half_angle = fan_angle / 2.0
        num_arc_points = 60
        
        # 转换到世界坐标
        def to_world(px, py):
            wx = origin[0] + px * spacing[0]
            wy = origin[1] + py * spacing[1]
            return wx, wy
        
        # 添加扇形顶点
        apex_wx, apex_wy = to_world(apex_x, apex_y)
        apex_id = points.InsertNextPoint(apex_wx, apex_wy, 0)
        
        # 添加弧线点
        arc_ids = []
        for i in range(num_arc_points + 1):
            # 角度从 -half_angle 到 +half_angle，以向上(90度)为中心
            angle = -half_angle + (fan_angle * i / num_arc_points)
            angle_rad = math.radians(90 - angle)  # 转换：向上为90度
            px = apex_x + fan_radius * math.cos(angle_rad)
            py = apex_y + fan_radius * math.sin(angle_rad)
            wx, wy = to_world(px, py)
            arc_ids.append(points.InsertNextPoint(wx, wy, 0))
        
        # 创建左边界线
        left_line = vtk.vtkLine()
        left_line.GetPointIds().SetId(0, apex_id)
        left_line.GetPointIds().SetId(1, arc_ids[0])
        lines.InsertNextCell(left_line)
        
        # 创建弧线
        for i in range(len(arc_ids) - 1):
            arc_line = vtk.vtkLine()
            arc_line.GetPointIds().SetId(0, arc_ids[i])
            arc_line.GetPointIds().SetId(1, arc_ids[i + 1])
            lines.InsertNextCell(arc_line)
        
        # 创建右边界线
        right_line = vtk.vtkLine()
        right_line.GetPointIds().SetId(0, arc_ids[-1])
        right_line.GetPointIds().SetId(1, apex_id)
        lines.InsertNextCell(right_line)
        
        # 创建PolyData
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(lines)
        
        # 创建Mapper和Actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.0, 1.0, 0.0)  # 绿色边框
        actor.GetProperty().SetLineWidth(2.0)
        
        return actor
        
    except Exception as e:
        print(f"[DEBUG] 创建扇形边界线失败: {e}")
        return None
