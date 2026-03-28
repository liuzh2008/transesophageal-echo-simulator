"""
3D体积渲染模块 - 使用VTK进行医学图像3D可视化

此模块负责创建和管理3D体积渲染，包括体积渲染、表面渲染和多平面重建。
"""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any, Union, TYPE_CHECKING
import warnings

try:
    import vtk
    from vtkmodules.util import numpy_support

    VTK_AVAILABLE = True
    
except ImportError:
    VTK_AVAILABLE = False
    warnings.warn("VTK库未安装，3D渲染功能将受限")


class VolumeRenderer:
    """3D体积渲染器"""
    
    def __init__(self):
        self.volume_data: Optional[np.ndarray] = None
        self.spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
        self.origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        
        # VTK对象
        self.renderer: Optional[vtk.vtkRenderer] = None
        self.volume_mapper: Optional[vtk.vtkGPUVolumeRayCastMapper] = None
        self.volume_property: Optional[vtk.vtkVolumeProperty] = None
        self.volume: Optional[vtk.vtkVolume] = None
        
        # 多平面重建
        self.mpr_planes: Dict[str, vtk.vtkImagePlaneWidget] = {}
        
        # 探头位置
        self.probe_position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.probe_direction: Tuple[float, float, float] = (0.0, 0.0, 1.0)
        
        # 超声声窗
        self.ultrasound_fan: Optional[vtk.vtkActor] = None
    
    def set_volume_data(self, volume_data: np.ndarray, 
                        spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0),
                        origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """设置3D体积数据
        
        参数:
            volume_data: 3D numpy数组 (Z, Y, X) 或 (Y, X, Z)
            spacing: 体素间距 (X, Y, Z)
            origin: 体积原点 (X, Y, Z)
        """
        if not VTK_AVAILABLE:
            warnings.warn("VTK不可用，无法设置体积数据")
            return
        
        self.volume_data = volume_data
        self.spacing = spacing
        self.origin = origin
        
        # 确保数据是3D的
        if volume_data.ndim == 2:
            # 2D图像，添加第三维
            self.volume_data = np.expand_dims(volume_data, axis=2)
        elif volume_data.ndim != 3:
            raise ValueError(f"体积数据必须是2D或3D，但得到 {volume_data.ndim}D")
    
    def create_volume_actor(self) -> Optional[vtk.vtkVolume]:
        """创建体积渲染演员
        
        返回:
            vtkVolume对象，如果VTK不可用则返回None
        """
        if not VTK_AVAILABLE or self.volume_data is None:
            return None
        
        try:
            # 将numpy数组转换为VTK图像数据
            vtk_image = self._numpy_to_vtk_image(self.volume_data)
            
            # 设置间距和原点
            vtk_image.SetSpacing(self.spacing)
            vtk_image.SetOrigin(self.origin)
            
            # 创建体积映射器
            self.volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
            self.volume_mapper.SetInputData(vtk_image)
            self.volume_mapper.SetBlendModeToComposite()
            
            # 创建体积属性
            self.volume_property = vtk.vtkVolumeProperty()
            self.volume_property.ShadeOn()
            self.volume_property.SetInterpolationTypeToLinear()
            
            # 创建颜色传输函数
            color_func = vtk.vtkColorTransferFunction()
            color_func.AddRGBPoint(0.0, 0.0, 0.0, 0.0)      # 黑色
            color_func.AddRGBPoint(0.3, 0.5, 0.2, 0.1)      # 棕色
            color_func.AddRGBPoint(0.6, 0.9, 0.6, 0.3)      # 浅棕色
            color_func.AddRGBPoint(1.0, 1.0, 1.0, 0.9)      # 浅黄色
            
            # 创建不透明度传输函数
            opacity_func = vtk.vtkPiecewiseFunction()
            opacity_func.AddPoint(0.0, 0.0)
            opacity_func.AddPoint(0.1, 0.0)
            opacity_func.AddPoint(0.3, 0.3)
            opacity_func.AddPoint(0.6, 0.6)
            opacity_func.AddPoint(1.0, 0.8)
            
            self.volume_property.SetColor(color_func)
            self.volume_property.SetScalarOpacity(opacity_func)
            
            # 创建体积
            self.volume = vtk.vtkVolume()
            self.volume.SetMapper(self.volume_mapper)
            self.volume.SetProperty(self.volume_property)
            
            return self.volume
            
        except Exception as e:
            warnings.warn(f"创建体积演员失败: {e}")
            return None
    
    def create_surface_actor(self, threshold: float = 0.3) -> Optional[vtk.vtkActor]:
        """创建表面渲染演员
        
        参数:
            threshold: 等值面阈值 (0-1)
            
        返回:
            vtkActor对象，如果VTK不可用则返回None
        """
        if not VTK_AVAILABLE or self.volume_data is None:
            return None
        
        try:
            # 将numpy数组转换为VTK图像数据
            vtk_image = self._numpy_to_vtk_image(self.volume_data)
            vtk_image.SetSpacing(self.spacing)
            vtk_image.SetOrigin(self.origin)
            
            # 创建Marching Cubes算法
            marching_cubes = vtk.vtkMarchingCubes()
            marching_cubes.SetInputData(vtk_image)
            marching_cubes.SetValue(0, threshold)
            marching_cubes.ComputeNormalsOn()
            
            # 创建映射器
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(marching_cubes.GetOutputPort())
            mapper.ScalarVisibilityOff()
            
            # 创建演员
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            
            # 设置表面属性
            actor.GetProperty().SetColor(0.9, 0.3, 0.2)  # 红色
            actor.GetProperty().SetOpacity(0.7)
            actor.GetProperty().SetAmbient(0.1)
            actor.GetProperty().SetDiffuse(0.7)
            actor.GetProperty().SetSpecular(0.5)
            actor.GetProperty().SetSpecularPower(50)
            
            return actor
            
        except Exception as e:
            warnings.warn(f"创建表面演员失败: {e}")
            return None
    
    def create_mpr_planes(self, renderer: vtk.vtkRenderer) -> Dict[str, vtk.vtkImagePlaneWidget]:
        """创建多平面重建平面
        
        参数:
            renderer: VTK渲染器
            
        返回:
            包含三个平面（轴向、冠状、矢状）的字典
        """
        if not VTK_AVAILABLE or self.volume_data is None:
            return {}
        
        try:
            # 将numpy数组转换为VTK图像数据
            vtk_image = self._numpy_to_vtk_image(self.volume_data)
            vtk_image.SetSpacing(self.spacing)
            vtk_image.SetOrigin(self.origin)
            
            # 计算体积中心
            dims = vtk_image.GetDimensions()
            center = [
                self.origin[0] + dims[0] * self.spacing[0] / 2,
                self.origin[1] + dims[1] * self.spacing[1] / 2,
                self.origin[2] + dims[2] * self.spacing[2] / 2
            ]
            
            # 创建三个平面
            planes = {}
            
            # 轴向平面 (XY平面)
            axial_plane = vtk.vtkImagePlaneWidget()
            axial_plane.SetInputData(vtk_image)
            axial_plane.SetPlaneOrientationToZAxes()
            axial_plane.SetSliceIndex(dims[2] // 2)
            axial_plane.SetInteractor(renderer.GetRenderWindow().GetInteractor())
            axial_plane.DisplayTextOn()
            axial_plane.SetDefaultRenderer(renderer)
            axial_plane.On()
            axial_plane.SetWindowLevel(1.0, 0.5)
            axial_plane.GetPlaneProperty().SetColor(0.0, 1.0, 0.0)  # 绿色
            axial_plane.GetPlaneProperty().SetOpacity(0.3)
            planes['axial'] = axial_plane
            
            # 冠状平面 (XZ平面)
            coronal_plane = vtk.vtkImagePlaneWidget()
            coronal_plane.SetInputData(vtk_image)
            coronal_plane.SetPlaneOrientationToYAxes()
            coronal_plane.SetSliceIndex(dims[1] // 2)
            coronal_plane.SetInteractor(renderer.GetRenderWindow().GetInteractor())
            coronal_plane.DisplayTextOn()
            coronal_plane.SetDefaultRenderer(renderer)
            coronal_plane.On()
            coronal_plane.SetWindowLevel(1.0, 0.5)
            coronal_plane.GetPlaneProperty().SetColor(1.0, 0.0, 0.0)  # 红色
            coronal_plane.GetPlaneProperty().SetOpacity(0.3)
            planes['coronal'] = coronal_plane
            
            # 矢状平面 (YZ平面)
            sagittal_plane = vtk.vtkImagePlaneWidget()
            sagittal_plane.SetInputData(vtk_image)
            sagittal_plane.SetPlaneOrientationToXAxes()
            sagittal_plane.SetSliceIndex(dims[0] // 2)
            sagittal_plane.SetInteractor(renderer.GetRenderWindow().GetInteractor())
            sagittal_plane.DisplayTextOn()
            sagittal_plane.SetDefaultRenderer(renderer)
            sagittal_plane.On()
            sagittal_plane.SetWindowLevel(1.0, 0.5)
            sagittal_plane.GetPlaneProperty().SetColor(0.0, 0.0, 1.0)  # 蓝色
            sagittal_plane.GetPlaneProperty().SetOpacity(0.3)
            planes['sagittal'] = sagittal_plane
            
            self.mpr_planes = planes
            return planes
            
        except Exception as e:
            warnings.warn(f"创建MPR平面失败: {e}")
            return {}
    
    def set_probe_position(self, position: Tuple[float, float, float], 
                          direction: Tuple[float, float, float] = (0.0, 0.0, 1.0)):
        """设置探头位置和方向
        
        参数:
            position: 探头位置 (X, Y, Z)
            direction: 探头方向向量
        """
        self.probe_position = position
        self.probe_direction = direction
        
        # 归一化方向向量
        norm = np.linalg.norm(direction)
        if norm > 0:
            # 显式创建3元组以避免类型检查器错误
            normalized = (float(direction[0] / norm), 
                         float(direction[1] / norm), 
                         float(direction[2] / norm))
            self.probe_direction = normalized
    
    def create_ultrasound_fan(self, angle: float = 60.0, radius: float = 100.0) -> Optional[vtk.vtkActor]:
        """创建超声扇形声窗
        
        参数:
            angle: 扇形角度 (度)
            radius: 扇形半径 (mm)
            
        返回:
            vtkActor对象，如果VTK不可用则返回None
        """
        if not VTK_AVAILABLE:
            return None
        
        try:
            # 创建扇形源
            arc_source = vtk.vtkArcSource()
            arc_source.SetPoint1(0, -radius * np.tan(np.radians(angle/2)), 0)
            arc_source.SetPoint2(0, radius * np.tan(np.radians(angle/2)), 0)
            arc_source.SetCenter(0, 0, 0)
            arc_source.SetResolution(30)
            arc_source.SetNegative(False)
            
            # 创建扇形多边形
            points = vtk.vtkPoints()
            lines = vtk.vtkCellArray()
            
            # 添加原点
            points.InsertNextPoint(0, 0, 0)
            
            # 添加弧上的点
            arc_source.Update()
            arc_poly = arc_source.GetOutput()
            for i in range(arc_poly.GetNumberOfPoints()):
                point = arc_poly.GetPoint(i)
                points.InsertNextPoint(point[0], point[1], point[2])
            
            # 创建三角形扇
            num_arc_points = arc_poly.GetNumberOfPoints()
            for i in range(num_arc_points - 1):
                triangle = vtk.vtkTriangle()
                triangle.GetPointIds().SetId(0, 0)  # 原点
                triangle.GetPointIds().SetId(1, i + 1)
                triangle.GetPointIds().SetId(2, i + 2)
                lines.InsertNextCell(triangle)
            
            # 创建多边形数据
            poly_data = vtk.vtkPolyData()
            poly_data.SetPoints(points)
            poly_data.SetPolys(lines)
            
            # 创建映射器
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(poly_data)
            
            # 创建演员
            self.ultrasound_fan = vtk.vtkActor()
            self.ultrasound_fan.SetMapper(mapper)
            
            # 设置属性
            self.ultrasound_fan.GetProperty().SetColor(1.0, 1.0, 0.0)  # 黄色
            self.ultrasound_fan.GetProperty().SetOpacity(0.3)
            self.ultrasound_fan.GetProperty().SetAmbient(0.5)
            self.ultrasound_fan.GetProperty().SetDiffuse(0.5)
            self.ultrasound_fan.GetProperty().SetSpecular(0.5)
            
            # 应用探头位置和方向
            self._transform_ultrasound_fan()
            
            return self.ultrasound_fan
            
        except Exception as e:
            warnings.warn(f"创建超声扇形失败: {e}")
            return None
    
    def _transform_ultrasound_fan(self):
        """根据探头位置和方向变换超声扇形"""
        if self.ultrasound_fan is None:
            return
        
        # 创建变换
        transform = vtk.vtkTransform()
        
        # 平移
        transform.Translate(self.probe_position)
        
        # 旋转到方向向量
        if self.probe_direction != (0.0, 0.0, 1.0):
            # 计算从Z轴到目标方向的旋转
            z_axis = (0.0, 0.0, 1.0)
            rotation_axis = np.cross(z_axis, self.probe_direction)
            rotation_angle = np.degrees(np.arccos(np.dot(z_axis, self.probe_direction)))
            
            if np.linalg.norm(rotation_axis) > 0:
                # 将numpy数组转换为列表
                axis_list = rotation_axis.tolist()
                transform.RotateWXYZ(rotation_angle, axis_list[0], axis_list[1], axis_list[2])
        
        self.ultrasound_fan.SetUserTransform(transform)
    
    def update_ultrasound_fan(self, angle: Optional[float] = None, radius: Optional[float] = None):
        """更新超声扇形参数"""
        if angle is not None or radius is not None:
            # 需要重新创建扇形
            current_angle = angle if angle is not None else 60.0
            current_radius = radius if radius is not None else 100.0
            self.create_ultrasound_fan(current_angle, current_radius)
        else:
            # 只更新变换
            self._transform_ultrasound_fan()
    
    def _numpy_to_vtk_image(self, numpy_array: np.ndarray) -> vtk.vtkImageData:
        """将numpy数组转换为VTK图像数据"""
        # 确保数组是C连续的
        numpy_array = np.ascontiguousarray(numpy_array)
        
        # 获取数组维度
        dims = numpy_array.shape
        
        # 创建VTK图像数据
        vtk_image = vtk.vtkImageData()
        vtk_image.SetDimensions(dims[1], dims[0], dims[2])  # VTK使用 (X, Y, Z)
        vtk_image.AllocateScalars(vtk.VTK_FLOAT, 1)
        
        # 将数据复制到VTK
        vtk_array = numpy_support.numpy_to_vtk(
            numpy_array.ravel(order='F'),  # VTK使用Fortran顺序
            deep=True,
            array_type=vtk.VTK_FLOAT
        )
        
        vtk_image.GetPointData().SetScalars(vtk_array)
        return vtk_image
    
    def get_volume_center(self) -> Tuple[float, float, float]:
        """获取体积中心"""
        if self.volume_data is None:
            return (0.0, 0.0, 0.0)
        
        dims = self.volume_data.shape
        center = (
            self.origin[0] + dims[2] * self.spacing[0] / 2,
            self.origin[1] + dims[1] * self.spacing[1] / 2,
            self.origin[2] + dims[0] * self.spacing[2] / 2
        )
        return center
    
    def get_vtk_image_data(self) -> Optional[vtk.vtkImageData]:
        """
        获取VTK图像数据
        
        功能说明:
            将内部的numpy体积数据转换为VTK图像数据格式，用于2D切片显示和其他VTK操作。
            此方法提供了从numpy数组到VTK图像数据的桥梁，支持2D截面显示功能。
        
        请求参数:
            无
        
        响应格式:
            vtk.vtkImageData 或 None - 转换后的VTK图像数据，如果转换失败则返回None
        
        逻辑:
            1. 检查VTK可用性和体积数据是否存在
            2. 调用内部方法_numpy_to_vtk_image进行数据转换
            3. 设置图像的间距和原点信息
            4. 返回转换后的VTK图像数据
        
        响应示例:
            >>> renderer = VolumeRenderer()
            >>> renderer.set_volume_data(np.random.rand(256, 256, 256))
            >>> vtk_image = renderer.get_vtk_image_data()
            >>> print(vtk_image.GetDimensions())
            (256, 256, 256)
        
        相关文件:
            src/core/volume_render.py
            src/gui/cross_section_window.py
            src/gui/vtk_manager.py
        
        注意事项:
            - 此方法依赖于VTK库，如果VTK不可用则返回None
            - 返回的图像数据包含原始体积数据的完整信息，包括间距和原点
            - 主要用于2D切片显示功能，也可用于其他需要VTK图像数据的操作
        """
        if not VTK_AVAILABLE or self.volume_data is None:
            return None
        
        try:
            # 将numpy数组转换为VTK图像数据
            vtk_image = self._numpy_to_vtk_image(self.volume_data)
            vtk_image.SetSpacing(self.spacing)
            vtk_image.SetOrigin(self.origin)
            return vtk_image
        except Exception as e:
            warnings.warn(f"获取VTK图像数据失败: {e}")
            return None
    
    def update_opacity(self, opacity_value: float):
        """更新体积透明度
        
        参数:
            opacity_value: 透明度值 (0.0-1.0)，0.0为完全透明，1.0为完全不透明
            注意：对于体积渲染，完全透明(0.0)并不意味着完全不可见，
            而是表示最低的不透明度水平
        """
        if not VTK_AVAILABLE or self.volume_property is None:
            return
        
        try:
            # 获取当前的不透明度传输函数
            opacity_func = self.volume_property.GetScalarOpacity()
            
            # 确保opacity_value在合理范围内，避免完全不可见
            # 设置最小不透明度为0.1，最大为1.0
            adjusted_opacity = max(0.1, min(1.0, opacity_value))
            
            if opacity_func is None:
                # 创建新的不透明度传输函数
                opacity_func = vtk.vtkPiecewiseFunction()
                # 基础不透明度函数 - 低密度区域透明，高密度区域不透明
                # 使用非线性映射，确保即使透明度值低，高密度区域仍然可见
                opacity_func.AddPoint(0.0, 0.0)
                opacity_func.AddPoint(0.1, 0.0)
                opacity_func.AddPoint(0.3, 0.3 * adjusted_opacity)
                opacity_func.AddPoint(0.6, 0.6 * adjusted_opacity)
                opacity_func.AddPoint(1.0, 1.0 * adjusted_opacity)
                self.volume_property.SetScalarOpacity(opacity_func)
            else:
                # 对于体积渲染，使用更温和的缩放方式
                # 获取当前函数的所有点
                old_points = []
                range_val = opacity_func.GetRange()
                if range_val[0] == range_val[1]:
                    range_val = (0.0, 1.0)
                
                # 采样关键点而不是所有点
                sample_points = [0.0, 0.1, 0.3, 0.6, 1.0]
                old_points = []
                for x in sample_points:
                    # 将采样点映射到实际范围
                    mapped_x = range_val[0] + (range_val[1] - range_val[0]) * x
                    y = opacity_func.GetValue(mapped_x)
                    old_points.append((mapped_x, y))
                
                # 清除现有点并添加调整后的点
                opacity_func.RemoveAllPoints()
                for x, y in old_points:
                    # 使用更温和的缩放：保留一定的基础不透明度
                    # 当adjusted_opacity=0.1时，new_y = y * 0.3 + 0.05
                    # 当adjusted_opacity=1.0时，new_y = y * 0.8 + 0.2
                    scale_factor = 0.3 + 0.5 * adjusted_opacity  # 0.3到0.8之间
                    base_opacity = 0.05 + 0.15 * adjusted_opacity  # 0.05到0.2之间
                    new_y = y * scale_factor + base_opacity
                    # 确保不透明度在0-1范围内
                    new_y = max(0.0, min(1.0, new_y))
                    opacity_func.AddPoint(x, new_y)
            
            # 设置整体不透明度乘数
            self.volume_property.SetScalarOpacityUnitDistance(1.0)
            
            # 如果体积存在，触发重新渲染
            if self.volume is not None:
                self.volume.Modified()
                # 强制重新渲染
                self.volume.Update()
                
        except Exception as e:
            warnings.warn(f"更新透明度失败: {e}")
    
    def create_cut_plane(self, position_percent: float = 0.5, 
                        normal: Tuple[float, float, float] = (0, 0, 1),
                        return_data: bool = False) -> Union[
                            Tuple[Optional[vtk.vtkActor], Optional[vtk.vtkActor]], 
                            Dict[str, Any]
                        ]:
        """创建切割平面（红色线条+浅红色填充）
        
        参数:
            position_percent: 切割位置百分比 (0.0-1.0)，0.5表示50%位置
            normal: 平面法线向量，默认垂直于Z轴
            return_data: 是否返回切割数据（vtkPolyData）及平面参数
            
        返回:
            如果return_data为False: (cut_actor, fill_actor) - 红色线条Actor和浅红色填充Actor
            如果return_data为True: dict包含：
                - cut_actor: 红色线条Actor
                - fill_actor: 浅红色填充Actor
                - cut_polydata: 切割数据
                - plane_origin: 平面原点 (x, y, z)
                - plane_x_axis: 平面X轴方向 (归一化向量)
                - plane_y_axis: 平面Y轴方向 (归一化向量)
        """
        print(f"\n[DEBUG] 开始创建切割平面...")
        print(f"[DEBUG] VTK_AVAILABLE: {VTK_AVAILABLE}")
        print(f"[DEBUG] volume_data is None: {self.volume_data is None}")
        print(f"[DEBUG] return_data: {return_data}")
        
        if not VTK_AVAILABLE:
            print("[DEBUG] VTK不可用")
            if return_data:
                return {'cut_actor': None, 'fill_actor': None, 'cut_polydata': None, 
                        'plane_origin': None, 'plane_x_axis': None, 'plane_y_axis': None}
            return (None, None)
        
        if self.volume_data is None:
            print("[DEBUG] 体积数据为空")
            if return_data:
                return {'cut_actor': None, 'fill_actor': None, 'cut_polydata': None,
                        'plane_origin': None, 'plane_x_axis': None, 'plane_y_axis': None}
            return (None, None)
        
        try:
            # 将numpy数组转换为VTK图像数据
            print(f"[DEBUG] 转换numpy数组到VTK图像...")
            vtk_image = self._numpy_to_vtk_image(self.volume_data)
            vtk_image.SetSpacing(self.spacing)
            vtk_image.SetOrigin(self.origin)
            
            # 获取体积边界
            bounds = vtk_image.GetBounds()
            print(f"[DEBUG] 体积边界: {bounds}")
            print(f"[DEBUG] 体积维度: {vtk_image.GetDimensions()}")
            print(f"[DEBUG] 体积间距: {self.spacing}")
            print(f"[DEBUG] 体积原点: {self.origin}")
            
            # 计算切割位置（50%位置）
            # 根据法线方向确定切割轴
            print(f"[DEBUG] 法线向量: {normal}")
            if abs(normal[2]) > abs(normal[0]) and abs(normal[2]) > abs(normal[1]):
                # 主要垂直于Z轴
                cut_position = bounds[4] + (bounds[5] - bounds[4]) * position_percent
                plane_origin = [(bounds[0] + bounds[1]) / 2, 
                               (bounds[2] + bounds[3]) / 2, 
                               cut_position]
                print(f"[DEBUG] 垂直于Z轴切割，位置: {cut_position}")
            elif abs(normal[1]) > abs(normal[0]) and abs(normal[1]) > abs(normal[2]):
                # 主要垂直于Y轴
                cut_position = bounds[2] + (bounds[3] - bounds[2]) * position_percent
                plane_origin = [(bounds[0] + bounds[1]) / 2, 
                               cut_position,
                               (bounds[4] + bounds[5]) / 2]
                print(f"[DEBUG] 垂直于Y轴切割，位置: {cut_position}")
            else:
                # 主要垂直于X轴
                cut_position = bounds[0] + (bounds[1] - bounds[0]) * position_percent
                plane_origin = [cut_position,
                               (bounds[2] + bounds[3]) / 2,
                               (bounds[4] + bounds[5]) / 2]
                print(f"[DEBUG] 垂直于X轴切割，位置: {cut_position}")
            
            print(f"[DEBUG] 平面原点: {plane_origin}")
            
            # 计算平面坐标系（X轴和Y轴）
            # 归一化法线向量
            normal_vec = np.array([normal[0], normal[1], normal[2]], dtype=np.float64)
            normal_length = np.linalg.norm(normal_vec)
            if normal_length > 0:
                normal_vec = normal_vec / normal_length
            
            # 选择参考向量（与法线不平行）
            if abs(normal_vec[0]) < 0.9:
                ref = np.array([1.0, 0.0, 0.0])
            else:
                ref = np.array([0.0, 1.0, 0.0])
            
            # 叉积计算正交坐标系
            plane_x_axis = np.cross(ref, normal_vec)
            x_length = np.linalg.norm(plane_x_axis)
            if x_length > 0:
                plane_x_axis = plane_x_axis / x_length
            
            plane_y_axis = np.cross(normal_vec, plane_x_axis)
            y_length = np.linalg.norm(plane_y_axis)
            if y_length > 0:
                plane_y_axis = plane_y_axis / y_length
            
            # 转换为元组
            plane_x_axis = tuple(plane_x_axis.tolist())
            plane_y_axis = tuple(plane_y_axis.tolist())
            
            print(f"[DEBUG] 平面X轴: {plane_x_axis}")
            print(f"[DEBUG] 平面Y轴: {plane_y_axis}")
            
            # 创建切割平面
            plane = vtk.vtkPlane()
            plane.SetOrigin(plane_origin[0], plane_origin[1], plane_origin[2])
            plane.SetNormal(normal[0], normal[1], normal[2])
            
            # 执行切割操作
            cutter = vtk.vtkCutter()
            cutter.SetCutFunction(plane)
            cutter.SetInputData(vtk_image)
            cutter.Update()
            
            cut_polydata = cutter.GetOutput()
            
            # 检查是否有切割结果
            num_points = cut_polydata.GetNumberOfPoints()
            num_cells = cut_polydata.GetNumberOfCells()
            print(f"[DEBUG] 切割结果 - 点数: {num_points}, 单元数: {num_cells}")
            
            if num_points == 0:
                print("[DEBUG] 警告: 切割平面未产生任何几何体")
                print("[DEBUG] 可能原因: 平面位置在体积外部，或体积数据为空")
                if return_data:
                    return {'cut_actor': None, 'fill_actor': None, 'cut_polydata': None,
                            'plane_origin': None, 'plane_x_axis': None, 'plane_y_axis': None}
                return (None, None)
            
            # 创建红色线条切割Actor（轮廓线）
            cut_mapper = vtk.vtkPolyDataMapper()
            cut_mapper.SetInputData(cut_polydata)
            
            cut_actor = vtk.vtkActor()
            cut_actor.SetMapper(cut_mapper)
            cut_actor.GetProperty().SetColor(0.8, 0.2, 0.2)  # 红色轮廓 (RGB: 0.8,0.2,0.2) - 与参考文件一致
            cut_actor.GetProperty().SetLineWidth(3.0)        # 线宽3.0 - 与参考文件一致
            cut_actor.GetProperty().SetOpacity(0.7)          # 透明度0.7 - 与参考文件一致
            cut_actor.GetProperty().SetRepresentationToWireframe()  # 线框模式 - 与参考文件一致
            
            print(f"[DEBUG] 创建红色轮廓线Actor成功")
            
            # 创建浅红色填充平面Actor - 使用vtkContourTriangulator
            fill_actor = None
            try:
                print(f"[DEBUG] 创建填充平面（使用vtkContourTriangulator）...")
                
                # 使用vtkFeatureEdges提取轮廓线
                feature_edges = vtk.vtkFeatureEdges()
                feature_edges.SetInputData(cut_polydata)
                feature_edges.BoundaryEdgesOn()
                feature_edges.FeatureEdgesOff()
                feature_edges.ManifoldEdgesOff()
                feature_edges.NonManifoldEdgesOff()
                feature_edges.Update()
                
                contour_polydata = feature_edges.GetOutput()
                
                if contour_polydata.GetNumberOfLines() > 0:
                    # 使用vtkContourTriangulator创建填充平面
                    triangulator = vtk.vtkContourTriangulator()
                    triangulator.SetInputData(contour_polydata)
                    triangulator.Update()
                    
                    filled_polydata = triangulator.GetOutput()
                    
                    if filled_polydata.GetNumberOfPolys() > 0:
                        fill_mapper = vtk.vtkPolyDataMapper()
                        fill_mapper.SetInputData(filled_polydata)
                        
                        fill_actor = vtk.vtkActor()
                        fill_actor.SetMapper(fill_mapper)
                        fill_actor.GetProperty().SetColor(0.9, 0.6, 0.6)  # 浅红色填充
                        fill_actor.GetProperty().SetOpacity(0.7)
                        fill_actor.GetProperty().SetRepresentationToSurface()
                        fill_actor.GetProperty().SetEdgeVisibility(False)
                        print(f"[DEBUG] 使用ContourTriangulator创建填充平面成功")
                    else:
                        print(f"[DEBUG] ContourTriangulator没有生成多边形")
                else:
                    print(f"[DEBUG] 无法提取轮廓线")
                    
            except Exception as e:
                print(f"[DEBUG] 创建填充平面时出错: {e}")
                # 如果创建填充平面失败，只返回线条Actor
            
            print(f"[DEBUG] 切割平面创建完成")
            
            if return_data:
                # 返回扩展数据：包含平面原点和坐标轴
                return {
                    'cut_actor': cut_actor,
                    'fill_actor': fill_actor,
                    'cut_polydata': cut_polydata,
                    'plane_origin': tuple(plane_origin),
                    'plane_x_axis': plane_x_axis,
                    'plane_y_axis': plane_y_axis
                }
            else:
                return cut_actor, fill_actor
            
        except Exception as e:
            print(f"[DEBUG] 创建切割平面失败: {e}")
            import traceback
            traceback.print_exc()
            if return_data:
                return {'cut_actor': None, 'fill_actor': None, 'cut_polydata': None,
                        'plane_origin': None, 'plane_x_axis': None, 'plane_y_axis': None}
            return (None, None)
    
    def clear(self):
        """清除所有VTK对象"""
        self.volume_data = None
        self.volume = None
        self.volume_mapper = None
        self.volume_property = None
        self.mpr_planes.clear()
        self.ultrasound_fan = None


# 单例实例
_volume_renderer_instance: Optional[VolumeRenderer] = None

def get_volume_renderer() -> VolumeRenderer:
    """获取体积渲染器单例实例"""
    global _volume_renderer_instance
    if _volume_renderer_instance is None:
        _volume_renderer_instance = VolumeRenderer()
    return _volume_renderer_instance
