"""
3D体积渲染模块 - 使用VTK进行医学图像3D可视化

此模块负责创建和管理3D体积渲染，包括体积渲染、表面渲染和多平面重建。
"""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import warnings

try:
    import vtk
    from vtk.util import numpy_support
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
            self.probe_direction = tuple(d / norm for d in direction)
    
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
                transform.RotateWXYZ(rotation_angle, rotation_axis)
        
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
