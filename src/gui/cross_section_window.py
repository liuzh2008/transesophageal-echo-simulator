"""
2D截面窗口模块 - 显示垂直于切割平面的2D切片图像

严格按照doc\sample code\transesophageal-echo-simulator\dicom_rao_lao_cut_analysis.md
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


class CrossSectionWindow(QMainWindow):
    """2D截面窗口 - 显示垂直于切割平面的2D切片图像"""
    
    def __init__(self, image_data, normal_vector, cut_position, parent=None):
        """
        初始化2D截面窗口
        
        参数:
            image_data: vtkImageData对象，3D体积数据
            normal_vector: 切割平面法线向量 (nx, ny, nz)
            cut_position: 切割位置（百分比或实际坐标）
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.image_data = image_data
        self.normal_vector = normal_vector
        self.cut_position = cut_position
        
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
        
        严格按照示例代码中的create_slice_renderer函数实现
        返回: vtkRenderer对象或None
        """
        if not VTK_AVAILABLE or self.image_data is None:
            return None
        
        try:
            print(f"[DEBUG] 创建2D切片渲染器...")
            nx, ny, nz = self.normal_vector
            print(f"[DEBUG] 平面法线: ({nx:.3f}, {ny:.3f}, {nz:.3f})")
            
            # 获取体积的边界框和中心点
            bounds = self.image_data.GetBounds()
            center = [
                (bounds[0] + bounds[1]) / 2,
                (bounds[2] + bounds[3]) / 2,
                (bounds[4] + bounds[5]) / 2
            ]
            
            print(f"[DEBUG] 体积中心: ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})")
            
            # 创建切片提取器
            reslice = vtk.vtkImageReslice()
            reslice.SetInputData(self.image_data)
            reslice.SetOutputDimensionality(2)
            
            # 设置切片方向（垂直于法线向量）
            # 我们需要创建两个正交向量作为切片的X和Y轴
            
            # 创建切片的坐标系
            # Z轴：法线向量（切片平面的法线）
            # X轴：任意与Z轴正交的向量
            # Y轴：Z轴 × X轴
            
            # 选择一个参考向量（通常使用[1, 0, 0]或[0, 1, 0]）
            if abs(nx) < 0.5:
                ref_vector = (1, 0, 0)
            else:
                ref_vector = (0, 1, 0)
            
            # 计算X轴（与法线向量正交）
            # 叉积计算
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
            
            print(f"[DEBUG] 切片X轴: ({x_axis[0]:.3f}, {x_axis[1]:.3f}, {x_axis[2]:.3f})")
            print(f"[DEBUG] 切片Y轴: ({y_axis[0]:.3f}, {y_axis[1]:.3f}, {y_axis[2]:.3f})")
            
            # 设置方向余弦矩阵
            reslice.SetResliceAxesDirectionCosines(
                x_axis[0], x_axis[1], x_axis[2],
                y_axis[0], y_axis[1], y_axis[2],
                nx, ny, nz
            )
            
            # 设置切片原点为中心点
            reslice.SetResliceAxesOrigin(center[0], center[1], center[2])
            reslice.SetInterpolationModeToLinear()
            
            # 创建图像映射器
            image_mapper = vtk.vtkImageMapper()
            image_mapper.SetInputConnection(reslice.GetOutputPort())
            
            # 获取图像数据范围以设置合适的颜色窗口和级别
            reslice.Update()
            output = reslice.GetOutput()
            if output:
                scalar_range = output.GetScalarRange()
                min_val, max_val = scalar_range
                print(f"[DEBUG] 2D切片数据范围: {min_val:.1f} 到 {max_val:.1f}")
                
                # 根据数据范围设置颜色窗口和级别
                if max_val - min_val > 0:
                    # 对于医学图像，如果数据范围很小，可能需要调整窗口/级别
                    # 检查数据是否已经归一化（范围在0-1之间）
                    if max_val <= 1.0 and min_val >= 0.0:
                        # 数据已经归一化，使用适合归一化数据的设置
                        window = 1.0  # 全范围
                        level = 0.5   # 中间值
                        print(f"[DEBUG] 数据已归一化，使用窗口: {window}, 级别: {level}")
                    else:
                        # 使用数据实际范围
                        window = max_val - min_val
                        level = (max_val + min_val) / 2
                        print(f"[DEBUG] 使用实际数据范围，窗口: {window:.1f}, 级别: {level:.1f}")
                    
                    image_mapper.SetColorWindow(window)
                    image_mapper.SetColorLevel(level)
                else:
                    # 默认值 - 适合医学图像的典型设置
                    image_mapper.SetColorWindow(400)  # 典型CT窗口
                    image_mapper.SetColorLevel(40)    # 典型CT级别
                    print(f"[DEBUG] 使用默认医学图像设置，窗口: 400, 级别: 40")
            else:
                # 默认值 - 适合医学图像的典型设置
                image_mapper.SetColorWindow(400)  # 典型CT窗口
                image_mapper.SetColorLevel(40)    # 典型CT级别
                print(f"[DEBUG] 无输出数据，使用默认设置，窗口: 400, 级别: 40")
            
            # 创建2D Actor
            image_actor = vtk.vtkActor2D()
            image_actor.SetMapper(image_mapper)
            
            # 创建渲染器
            renderer = vtk.vtkRenderer()
            renderer.AddActor2D(image_actor)
            renderer.SetBackground(0.2, 0.2, 0.3)  # 深蓝色背景
            
            # 添加文本标注
            text_actor = vtk.vtkTextActor()
            text_actor.SetInput(f"2D切片视图\n法线: ({nx:.2f}, {ny:.2f}, {nz:.2f})\n位置: {self.cut_position}")
            text_actor.GetTextProperty().SetFontSize(14)
            text_actor.GetTextProperty().SetColor(1, 1, 1)  # 白色文字
            text_actor.GetTextProperty().SetBackgroundColor(0, 0, 0)  # 黑色背景
            text_actor.GetTextProperty().SetBackgroundOpacity(0.7)
            text_actor.SetPosition(20, 20)
            renderer.AddActor2D(text_actor)
            
            # 设置相机为正交投影
            camera = renderer.GetActiveCamera()
            camera.ParallelProjectionOn()
            
            # 获取图像边界
            reslice.Update()
            output = reslice.GetOutput()
            if output:
                bounds = output.GetBounds()
                width = max(bounds[1] - bounds[0], bounds[3] - bounds[2]) * 1.2
                if width > 0:
                    camera.SetParallelScale(width / 2)
            
            # 设置相机位置
            camera.SetPosition(0, 0, 1000)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 1, 0)
            
            print(f"[DEBUG] 2D切片渲染器创建完成")
            return renderer
            
        except Exception as e:
            print(f"[DEBUG] 创建2D切片渲染器失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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


def create_cross_section_window(image_data, normal_vector, cut_position, parent=None):
    """
    创建并显示2D切片窗口的便捷函数
    
    参数:
        image_data: vtk.vtkImageData - 3D体积数据，包含DICOM图像信息
        normal_vector: tuple - 切割平面法线向量 (nx, ny, nz)，定义切片方向
        cut_position: float - 切割位置（百分比），0.0-1.0之间，0.5表示50%位置
        parent: QWidget (可选) - 父窗口部件，用于窗口层次结构
        
    返回:
        CrossSectionWindow - 创建的2D切片窗口实例
        
    逻辑:
        1. 创建CrossSectionWindow实例
        2. 设置窗口标志确保作为独立窗口显示
        3. 显示窗口并激活
        4. 返回窗口实例
        
    响应示例:
        >>> window = create_cross_section_window(vtk_image, (0, 0, 1), 0.5)
        >>> print(window.windowTitle())
        "2D切片视图 - 法线: (0, 0, 1)"
        
    相关文件:
        src/gui/cross_section_window.py
        src/gui/vtk_manager.py
        src/core/volume_render.py
    """
    window = CrossSectionWindow(image_data, normal_vector, cut_position, parent)
    
    # 确保窗口作为独立窗口显示
    window.setWindowFlags(window.windowFlags() | Qt.Window)
    
    # 显示窗口
    window.show()
    window.raise_()  # 将窗口提到最前面
    window.activateWindow()  # 激活窗口
    
    print(f"[DEBUG] 2D切片窗口已显示，标题: {window.windowTitle()}")
    return window


def create_embedded_2d_view(image_data, normal_vector, cut_position, parent_widget):
    """
    创建内嵌的2D视图小部件（用于在主窗口中显示）
    
    参数:
        image_data: vtk.vtkImageData - 3D体积数据
        normal_vector: tuple - 切割平面法线向量 (nx, ny, nz)
        cut_position: float - 切割位置（百分比）
        parent_widget: QWidget - 父窗口部件
        
    返回:
        QVTKRenderWindowInteractor - 包含2D切片渲染的VTK小部件，或None（如果创建失败）
    """
    if not VTK_AVAILABLE or image_data is None:
        return None
    
    try:
        # 创建VTK小部件
        vtk_widget = QVTKRenderWindowInteractor(parent_widget)
        
        # 创建2D切片渲染器（使用CrossSectionWindow的相同逻辑）
        renderer = _create_slice_renderer_internal(image_data, normal_vector, cut_position)
        
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


def _create_slice_renderer_internal(image_data, normal_vector, cut_position):
    """
    内部函数：创建2D切片渲染器（从CrossSectionWindow类中提取的逻辑）
    
    参数:
        image_data: vtk.vtkImageData - 3D体积数据
        normal_vector: tuple - 切割平面法线向量
        cut_position: float - 切割位置
        
    返回:
        vtkRenderer对象或None
    """
    if not VTK_AVAILABLE or image_data is None:
        return None
    
    try:
        nx, ny, nz = normal_vector
        
        # 获取体积的边界框和中心点
        bounds = image_data.GetBounds()
        center = [
            (bounds[0] + bounds[1]) / 2,
            (bounds[2] + bounds[3]) / 2,
            (bounds[4] + bounds[5]) / 2
        ]
        
        # 创建切片提取器
        reslice = vtk.vtkImageReslice()
        reslice.SetInputData(image_data)
        reslice.SetOutputDimensionality(2)
        
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
        
        # 设置方向余弦矩阵
        reslice.SetResliceAxesDirectionCosines(
            x_axis[0], x_axis[1], x_axis[2],
            y_axis[0], y_axis[1], y_axis[2],
            nx, ny, nz
        )
        
        # 设置切片原点为中心点
        reslice.SetResliceAxesOrigin(center[0], center[1], center[2])
        reslice.SetInterpolationModeToLinear()
        
        # 创建图像映射器
        image_mapper = vtk.vtkImageMapper()
        image_mapper.SetInputConnection(reslice.GetOutputPort())
        
        # 获取图像数据范围以设置合适的颜色窗口和级别
        reslice.Update()
        output = reslice.GetOutput()
        if output:
            scalar_range = output.GetScalarRange()
            min_val, max_val = scalar_range
            
            # 根据数据范围设置颜色窗口和级别
            if max_val - min_val > 0:
                if max_val <= 1.0 and min_val >= 0.0:
                    # 数据已经归一化
                    window = 1.0
                    level = 0.5
                else:
                    # 使用数据实际范围
                    window = max_val - min_val
                    level = (max_val + min_val) / 2
                
                image_mapper.SetColorWindow(window)
                image_mapper.SetColorLevel(level)
            else:
                # 默认值 - 适合医学图像的典型设置
                image_mapper.SetColorWindow(400)
                image_mapper.SetColorLevel(40)
        else:
            # 默认值 - 适合医学图像的典型设置
            image_mapper.SetColorWindow(400)
            image_mapper.SetColorLevel(40)
        
        # 创建2D Actor
        image_actor = vtk.vtkActor2D()
        image_actor.SetMapper(image_mapper)
        
        # 创建渲染器
        renderer = vtk.vtkRenderer()
        renderer.AddActor2D(image_actor)
        renderer.SetBackground(0.2, 0.2, 0.3)  # 深蓝色背景
        
        # 添加文本标注
        text_actor = vtk.vtkTextActor()
        text_actor.SetInput(f"2D切片视图\n法线: ({nx:.2f}, {ny:.2f}, {nz:.2f})\n位置: {cut_position}")
        text_actor.GetTextProperty().SetFontSize(14)
        text_actor.GetTextProperty().SetColor(1, 1, 1)  # 白色文字
        text_actor.GetTextProperty().SetBackgroundColor(0, 0, 0)  # 黑色背景
        text_actor.GetTextProperty().SetBackgroundOpacity(0.7)
        text_actor.SetPosition(20, 20)
        renderer.AddActor2D(text_actor)
        
        # 设置相机为正交投影
        camera = renderer.GetActiveCamera()
        camera.ParallelProjectionOn()
        
        # 获取图像边界
        reslice.Update()
        output = reslice.GetOutput()
        if output:
            bounds = output.GetBounds()
            width = max(bounds[1] - bounds[0], bounds[3] - bounds[2]) * 1.2
            if width > 0:
                camera.SetParallelScale(width / 2)
        
        # 设置相机位置
        camera.SetPosition(0, 0, 1000)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 1, 0)
        
        return renderer
        
    except Exception as e:
        print(f"[DEBUG] 创建2D切片渲染器失败: {e}")
        import traceback
        traceback.print_exc()
        return None
