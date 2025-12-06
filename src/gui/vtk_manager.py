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
            
            # 开始交互
            self.vtk_widget.Initialize()
            self.vtk_widget.Start()
            
        except Exception as e:
            warnings.warn(f"初始化VTK失败: {e}")
            self.vtk_widget = None
            self.renderer = None
    
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
            
            # 添加坐标轴
            axes = vtk.vtkAxesActor()
            axes.SetTotalLength(60, 60, 60)
            axes.SetShaftTypeToCylinder()
            axes.SetCylinderRadius(0.02)
            self.renderer.AddActor(axes)
            
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
                
                # 添加坐标轴
                axes = vtk.vtkAxesActor()
                axes.SetTotalLength(100, 100, 100)
                axes.SetShaftTypeToCylinder()
                axes.SetCylinderRadius(0.02)
                self.renderer.AddActor(axes)
                
                # 重置相机
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
            
            # 添加坐标轴
            axes = vtk.vtkAxesActor()
            axes.SetTotalLength(100, 100, 100)
            axes.SetShaftTypeToCylinder()
            axes.SetCylinderRadius(0.02)
            self.renderer.AddActor(axes)
            
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
    
    def is_available(self):
        """检查VTK是否可用"""
        return VTK_AVAILABLE
