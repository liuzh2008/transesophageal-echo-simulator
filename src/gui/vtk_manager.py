"""
VTK管理器模块 - 负责VTK渲染相关逻辑

此模块按照关注点分享原则，将VTK渲染逻辑从主窗口中分离出来。
"""

import warnings

# 导入VTK组件
try:
    from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    import vtk
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False
    print("警告: VTK不可用，3D渲染功能将受限")


class VTKManager:
    """VTK渲染管理器"""
    
    def __init__(self, parent_widget=None):
        self.parent_widget = parent_widget
        self.vtk_widget = None
        self.renderer = None
        self.current_actor = None
        self._axes_actor = None  # 坐标轴Actor（只创建一次）
        
        if VTK_AVAILABLE:
            self._init_vtk()
    
    def _init_vtk(self):
        """初始化VTK组件"""
        if not VTK_AVAILABLE:
            return
        
        try:
            # 创建VTK渲染窗口
            self.vtk_widget = QVTKRenderWindowInteractor(self.parent_widget)
            
            # 创建渲染器
            self.renderer = vtk.vtkRenderer()
            self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
            
            # 设置背景颜色
            self.renderer.SetBackground(0.1, 0.2, 0.4)  # 深蓝色背景
            
            # 创建默认测试几何体
            self._create_test_geometry()
            
            # 添加坐标轴（只在此处添加一次）
            self._add_axes()
            
            # 开始交互
            self.vtk_widget.Initialize()
            self.vtk_widget.Start()
            
        except Exception as e:
            warnings.warn(f"初始化VTK失败: {e}")
            self.vtk_widget = None
            self.renderer = None
    
    def _add_axes(self, total_length=100):
        """添加坐标轴（只创建一次，避免重复添加导致OpenGL上下文冲突）"""
        if not VTK_AVAILABLE or self.renderer is None:
            return
        
        # 如果坐标轴已存在，先移除再重新添加
        if self._axes_actor is not None:
            self.renderer.RemoveActor(self._axes_actor)
        
        try:
            self._axes_actor = vtk.vtkAxesActor()
            self._axes_actor.SetTotalLength(total_length, total_length, total_length)
            self._axes_actor.SetShaftTypeToCylinder()
            self._axes_actor.SetCylinderRadius(0.02)
            self.renderer.AddActor(self._axes_actor)
        except Exception as e:
            warnings.warn(f"添加坐标轴失败: {e}")
    
    def _create_test_geometry(self):
        """创建测试几何体（一个球体）"""
        if not VTK_AVAILABLE or self.renderer is None:
            return
        
        try:
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
            self.current_actor = actor
            
            # 注意：坐标轴已在 _init_vtk 中通过 _add_axes() 统一添加，此处不再重复添加
            
            # 重置相机
            self.renderer.ResetCamera()
            
        except Exception as e:
            warnings.warn(f"创建测试几何体失败: {e}")
    
    def get_vtk_widget(self):
        """获取VTK小部件"""
        return self.vtk_widget
    
    def set_volume_data(self, image_data, spacing=None, origin=None):
        """设置体积数据"""
        if not VTK_AVAILABLE or self.renderer is None:
            return False
        
        try:
            from core.volume_render import get_volume_renderer
            
            # 获取体积渲染器
            volume_renderer = get_volume_renderer()
            
            # 设置体积数据
            if spacing is not None and origin is not None:
                volume_renderer.set_volume_data(image_data, spacing, origin)
            else:
                volume_renderer.set_volume_data(image_data)
            
            # 创建体积演员
            volume_actor = volume_renderer.create_volume_actor()
            
            if volume_actor is not None:
                # 清除现有演员
                self.renderer.RemoveAllViewProps()
                
                # 添加体积演员
                self.renderer.AddActor(volume_actor)
                self.current_actor = volume_actor
                
                # 重新添加坐标轴（使用统一方法，避免重复创建）
                self._add_axes()
                
                # 重置相机并重新渲染
                self.renderer.ResetCamera()
                self.vtk_widget.GetRenderWindow().Render()
                
                return True
            else:
                return False
                
        except Exception as e:
            warnings.warn(f"设置体积数据失败: {e}")
            return False
    
    def change_render_mode(self, mode):
        """更改渲染模式"""
        if not VTK_AVAILABLE or self.renderer is None:
            return
        
        try:
            from core.volume_render import get_volume_renderer
            
            volume_renderer = get_volume_renderer()
            
            # 清除现有演员
            self.renderer.RemoveAllViewProps()
            
            if mode == "体积渲染":
                # 创建体积演员
                volume_actor = volume_renderer.create_volume_actor()
                if volume_actor is not None:
                    self.renderer.AddActor(volume_actor)
                    self.current_actor = volume_actor
            
            elif mode == "表面渲染":
                # 创建表面演员
                surface_actor = volume_renderer.create_surface_actor(threshold=0.3)
                if surface_actor is not None:
                    self.renderer.AddActor(surface_actor)
                    self.current_actor = surface_actor
            
            elif mode == "线框渲染":
                # 创建表面演员并设置为线框模式
                surface_actor = volume_renderer.create_surface_actor(threshold=0.3)
                if surface_actor is not None:
                    surface_actor.GetProperty().SetRepresentationToWireframe()
                    surface_actor.GetProperty().SetColor(0.9, 0.3, 0.2)
                    self.renderer.AddActor(surface_actor)
                    self.current_actor = surface_actor
            
            # 重新添加坐标轴（使用统一方法，避免重复创建）
            self._add_axes()
            
            # 重置相机并重新渲染
            self.renderer.ResetCamera()
            self.vtk_widget.GetRenderWindow().Render()
            
        except Exception as e:
            warnings.warn(f"更改渲染模式失败: {e}")
    
    def change_opacity(self, opacity_value):
        """更改模型透明度"""
        if not VTK_AVAILABLE or self.renderer is None:
            return
        
        opacity = opacity_value / 100.0
        
        try:
            from core.volume_render import get_volume_renderer
            
            # 获取体积渲染器
            volume_renderer = get_volume_renderer()
            
            # 更新体积演员的透明度（如果存在）
            if volume_renderer.volume is not None:
                volume_renderer.update_opacity(opacity)
            
            # 更新所有普通演员的透明度
            actors = self.renderer.GetActors()
            actors.InitTraversal()
            actor = actors.GetNextItem()
            while actor:
                # 检查是否为普通演员（不是体积演员）
                if not isinstance(actor, vtk.vtkVolume):
                    actor.GetProperty().SetOpacity(opacity)
                actor = actors.GetNextItem()
            
            self.vtk_widget.GetRenderWindow().Render()
            
        except Exception as e:
            warnings.warn(f"更改透明度失败: {e}")
    
    def reset_camera(self):
        """重置相机"""
        if not VTK_AVAILABLE or self.renderer is None:
            return
        
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
    
    def show_cut_plane(self, position_percent=0.5, normal=(0, 0, 1), show_2d_window=False,
                       fan_apex_offset_x=0.0, fan_apex_offset_y=0.0, fan_apex_offset_z=0.0):
        """显示切割平面（红色线条+浅红色填充）
        
        参数:
            position_percent: 切割位置百分比 (0.0-1.0)，0.5表示50%位置
            normal: 平面法线向量，默认垂直于Z轴
            show_2d_window: 是否显示2D切片窗口（独立窗口），默认为False（在主窗口中显示）
            fan_apex_offset_x: 扇形顶点X轴偏移量
            fan_apex_offset_y: 扇形顶点Y轴偏移量
            fan_apex_offset_z: 扇形顶点Z轴偏移量
        """
        if not VTK_AVAILABLE or self.renderer is None:
            return False
        
        try:
            from core.volume_render import get_volume_renderer
            
            # 获取体积渲染器
            volume_renderer = get_volume_renderer()
            
            # 创建切割平面（获取切割数据和平面参数）
            result = volume_renderer.create_cut_plane(
                position_percent=position_percent, 
                normal=normal,
                return_data=True  # 获取切割数据和平面参数
            )
            
            # 从字典中提取数据
            cut_actor = result.get('cut_actor')
            fill_actor = result.get('fill_actor')
            plane_origin = result.get('plane_origin')
            plane_x_axis = result.get('plane_x_axis')
            plane_y_axis = result.get('plane_y_axis')
            
            if cut_actor is not None:
                # 添加红色线条切割Actor
                self.renderer.AddActor(cut_actor)
                
                # 如果存在填充Actor，也添加
                if fill_actor is not None:
                    self.renderer.AddActor(fill_actor)
                
                # 重新渲染
                self.vtk_widget.GetRenderWindow().Render()
                
                # 显示2D切片窗口（如果启用，显示为独立窗口）
                if show_2d_window:
                    self.show_cross_section_window(
                        position_percent, normal, embedded=False,
                        plane_origin=plane_origin,
                        plane_x_axis=plane_x_axis,
                        plane_y_axis=plane_y_axis,
                        fan_apex_offset_x=fan_apex_offset_x,
                        fan_apex_offset_y=fan_apex_offset_y,
                        fan_apex_offset_z=fan_apex_offset_z
                    )
                
                return True
            else:
                print("警告: 无法创建切割平面")
                return False
                
        except Exception as e:
            warnings.warn(f"显示切割平面失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_cross_section_window(self, cut_position, normal_vector=None, embedded=False, parent_widget=None,
                                   plane_origin=None, plane_x_axis=None, plane_y_axis=None,
                                   fan_apex_offset_x=0.0, fan_apex_offset_y=0.0, fan_apex_offset_z=0.0):
        """
        显示2D切片窗口（垂直于切割平面的2D切片图像）
        
        功能说明:
            创建并显示2D切片图像，可以选择显示为独立窗口或嵌入到主窗口中。
            此方法严格按照示例代码中的实现方式，使用vtkImageReslice提取2D切片。
        
        请求参数:
            cut_position: float - 切割位置（百分比），0.0-1.0之间，0.5表示50%位置
            normal_vector: tuple (可选) - 平面法线向量 (nx, ny, nz)，默认(0, 0, 1)垂直于Z轴
            embedded: bool (可选) - 是否嵌入到主窗口中显示，默认为False（独立窗口）
            parent_widget: QWidget (可选) - 父窗口部件（当embedded=True时需要）
            plane_origin: tuple (可选) - 平面原点 (x, y, z)，用于精确定位切割位置
            plane_x_axis: tuple (可选) - 平面X轴方向 (归一化向量)
            plane_y_axis: tuple (可选) - 平面Y轴方向 (归一化向量)
            fan_apex_offset_x: float (可选) - 扇形顶点X轴偏移量，默认为0.0
            fan_apex_offset_y: float (可选) - 扇形顶点Y轴偏移量，默认为0.0
            fan_apex_offset_z: float (可选) - 扇形顶点Z轴偏移量，默认为0.0
        
        响应格式:
            如果embedded=False: CrossSectionWindow - 创建的2D切片窗口实例
            如果embedded=True: QVTKRenderWindowInteractor - 包含2D切片渲染的VTK小部件
            如果创建失败则返回None
        
        逻辑:
            1. 检查VTK可用性
            2. 从volume_renderer获取VTK图像数据
            3. 根据embedded参数选择创建独立窗口或内嵌小部件
            4. 保存引用避免被垃圾回收
            5. 返回创建的窗口或小部件
        
        响应示例:
            >>> vtk_manager = VTKManager()
            >>> # 创建独立窗口
            >>> window = vtk_manager.show_cross_section_window(0.5, (0, 0, 1))
            >>> print(window.windowTitle())
            "2D切片视图 - 法线: (0, 0, 1)"
            
            >>> # 创建内嵌小部件
            >>> widget = vtk_manager.show_cross_section_window(0.5, (0, 0, 1), embedded=True, parent_widget=main_window)
        
        相关文件:
            src/gui/vtk_manager.py
            src/gui/cross_section_window.py
            src/core/volume_render.py
        
        注意事项:
            - 此方法依赖于VTK库和volume_renderer模块
            - 当embedded=True时，需要提供parent_widget参数
            - 使用正交投影相机，保持图像比例不变
            - 自动调整颜色窗口/级别以适应医学图像显示
        """
        if not VTK_AVAILABLE:
            print("警告: VTK不可用，无法显示2D切片窗口")
            return None
        
        try:
            # 从volume_renderer获取vtkImageData
            from core.volume_render import get_volume_renderer
            volume_renderer = get_volume_renderer()
            
            # 获取VTK图像数据
            vtk_image_data = volume_renderer.get_vtk_image_data()
            
            if vtk_image_data is None:
                print("警告: 无法获取VTK图像数据，2D切片窗口无法显示")
                return None
            
            # 导入2D切片窗口模块
            from .cross_section_window import create_cross_section_window, create_embedded_2d_view
            
            if embedded:
                # 创建内嵌的2D视图小部件
                if parent_widget is None:
                    print("警告: embedded=True时需要提供parent_widget参数")
                    return None
                
                widget = create_embedded_2d_view(
                    image_data=vtk_image_data,
                    normal_vector=normal_vector if normal_vector is not None else (0, 0, 1),
                    cut_position=cut_position,
                    parent_widget=parent_widget,
                    plane_origin=plane_origin,
                    plane_x_axis=plane_x_axis,
                    plane_y_axis=plane_y_axis,
                    fan_apex_offset_x=fan_apex_offset_x,
                    fan_apex_offset_y=fan_apex_offset_y,
                    fan_apex_offset_z=fan_apex_offset_z
                )
                
                # 保存小部件引用
                if not hasattr(self, '_embedded_2d_widgets'):
                    self._embedded_2d_widgets = []
                self._embedded_2d_widgets.append(widget)
                
                print(f"[DEBUG] 内嵌2D视图小部件已创建，小部件总数: {len(self._embedded_2d_widgets)}")
                return widget
            else:
                # 创建独立的2D切片窗口
                window = create_cross_section_window(
                    image_data=vtk_image_data,
                    normal_vector=normal_vector if normal_vector is not None else (0, 0, 1),
                    cut_position=cut_position,
                    parent=self.parent_widget,
                    plane_origin=plane_origin,
                    plane_x_axis=plane_x_axis,
                    plane_y_axis=plane_y_axis,
                    fan_apex_offset_x=fan_apex_offset_x,
                    fan_apex_offset_y=fan_apex_offset_y,
                    fan_apex_offset_z=fan_apex_offset_z
                )
                
                # 保存窗口引用，避免被垃圾回收
                if not hasattr(self, '_cross_section_windows'):
                    self._cross_section_windows = []
                self._cross_section_windows.append(window)
                
                print(f"[DEBUG] 2D切片窗口已创建并显示，窗口总数: {len(self._cross_section_windows)}")
                return window
            
        except ImportError as e:
            print(f"警告: 无法导入cross_section_window模块: {e}")
            return None
        except Exception as e:
            warnings.warn(f"显示2D切片窗口失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_available(self):
        """检查VTK是否可用"""
        return VTK_AVAILABLE
