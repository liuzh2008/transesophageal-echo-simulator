"""
经食管超声模拟模块 - 模拟TEE探头和超声声窗

此模块负责模拟经食管超声探头的位置、方向和超声声窗。
"""

import numpy as np
from typing import Tuple, Optional, List, Dict, Any
import warnings

try:
    import vtk
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False
    warnings.warn("VTK库未安装，超声模拟功能将受限")


class TEESimulator:
    """经食管超声模拟器"""
    
    def __init__(self):
        # 探头参数
        self.probe_position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.probe_direction: Tuple[float, float, float] = (0.0, 0.0, 1.0)
        self.probe_rotation: float = 0.0  # 绕自身轴旋转角度
        
        # 超声参数
        self.ultrasound_angle: float = 60.0  # 扇形角度 (度)
        self.ultrasound_radius: float = 100.0  # 扇形半径 (mm)
        self.frequency: float = 5.0  # 频率 (MHz)
        
        # 心脏模型参数
        self.heart_center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.heart_radius: float = 50.0  # 心脏半径 (mm)
        
        # VTK对象
        self.probe_actor: Optional[vtk.vtkActor] = None
        self.ultrasound_fan_actor: Optional[vtk.vtkActor] = None
        self.intersection_actor: Optional[vtk.vtkActor] = None
        
        # 截面数据
        self.cross_section_data: Optional[np.ndarray] = None
    
    def set_probe_position(self, position: Tuple[float, float, float]):
        """设置探头位置"""
        self.probe_position = position
        self._update_probe_visualization()
    
    def set_probe_direction(self, direction: Tuple[float, float, float]):
        """设置探头方向"""
        # 归一化方向向量
        norm = np.linalg.norm(direction)
        if norm > 0:
            self.probe_direction = tuple(d / norm for d in direction)
        else:
            self.probe_direction = (0.0, 0.0, 1.0)
        
        self._update_probe_visualization()
    
    def set_probe_rotation(self, rotation: float):
        """设置探头旋转角度 (度)"""
        self.probe_rotation = rotation % 360
        self._update_probe_visualization()
    
    def set_ultrasound_parameters(self, angle: float = 60.0, radius: float = 100.0):
        """设置超声参数"""
        self.ultrasound_angle = max(10.0, min(120.0, angle))  # 限制在10-120度
        self.ultrasound_radius = max(10.0, min(200.0, radius))  # 限制在10-200mm
        self._update_ultrasound_fan()
    
    def set_heart_model(self, center: Tuple[float, float, float], radius: float = 50.0):
        """设置心脏模型参数"""
        self.heart_center = center
        self.heart_radius = max(10.0, radius)
    
    def create_probe_actor(self) -> Optional[vtk.vtkActor]:
        """创建探头可视化演员"""
        if not VTK_AVAILABLE:
            return None
        
        try:
            # 创建圆柱体作为探头
            cylinder_source = vtk.vtkCylinderSource()
            cylinder_source.SetRadius(3.0)  # 探头半径 3mm
            cylinder_source.SetHeight(20.0)  # 探头长度 20mm
            cylinder_source.SetResolution(20)
            
            # 创建映射器
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(cylinder_source.GetOutputPort())
            
            # 创建演员
            self.probe_actor = vtk.vtkActor()
            self.probe_actor.SetMapper(mapper)
            
            # 设置探头颜色 (银色)
            self.probe_actor.GetProperty().SetColor(0.8, 0.8, 0.8)
            self.probe_actor.GetProperty().SetSpecular(0.5)
            self.probe_actor.GetProperty().SetSpecularPower(30)
            self.probe_actor.GetProperty().SetAmbient(0.2)
            self.probe_actor.GetProperty().SetDiffuse(0.8)
            
            # 应用初始位置和方向
            self._update_probe_visualization()
            
            return self.probe_actor
            
        except Exception as e:
            warnings.warn(f"创建探头演员失败: {e}")
            return None
    
    def create_ultrasound_fan_actor(self) -> Optional[vtk.vtkActor]:
        """创建超声扇形声窗演员"""
        if not VTK_AVAILABLE:
            return None
        
        try:
            # 计算扇形参数
            half_angle = np.radians(self.ultrasound_angle / 2)
            arc_radius = self.ultrasound_radius * np.tan(half_angle)
            
            # 创建扇形源
            arc_source = vtk.vtkArcSource()
            arc_source.SetPoint1(0, -arc_radius, 0)
            arc_source.SetPoint2(0, arc_radius, 0)
            arc_source.SetCenter(0, 0, 0)
            arc_source.SetResolution(30)
            arc_source.SetNegative(False)
            
            # 创建扇形多边形
            points = vtk.vtkPoints()
            triangles = vtk.vtkCellArray()
            
            # 添加原点 (探头位置)
            points.InsertNextPoint(0, 0, 0)
            
            # 添加弧上的点
            arc_source.Update()
            arc_poly = arc_source.GetOutput()
            arc_points = []
            for i in range(arc_poly.GetNumberOfPoints()):
                point = arc_poly.GetPoint(i)
                # 将2D弧点转换为3D (添加Z坐标)
                points.InsertNextPoint(point[0], point[1], -self.ultrasound_radius)
                arc_points.append(i + 1)  # 点索引 (0是原点)
            
            # 创建三角形扇
            num_arc_points = len(arc_points)
            for i in range(num_arc_points - 1):
                triangle = vtk.vtkTriangle()
                triangle.GetPointIds().SetId(0, 0)  # 原点
                triangle.GetPointIds().SetId(1, arc_points[i])
                triangle.GetPointIds().SetId(2, arc_points[i + 1])
                triangles.InsertNextCell(triangle)
            
            # 创建多边形数据
            poly_data = vtk.vtkPolyData()
            poly_data.SetPoints(points)
            poly_data.SetPolys(triangles)
            
            # 创建映射器
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(poly_data)
            
            # 创建演员
            self.ultrasound_fan_actor = vtk.vtkActor()
            self.ultrasound_fan_actor.SetMapper(mapper)
            
            # 设置扇形属性 (半透明黄色)
            self.ultrasound_fan_actor.GetProperty().SetColor(1.0, 1.0, 0.0)  # 黄色
            self.ultrasound_fan_actor.GetProperty().SetOpacity(0.3)
            self.ultrasound_fan_actor.GetProperty().SetAmbient(0.5)
            self.ultrasound_fan_actor.GetProperty().SetDiffuse(0.5)
            self.ultrasound_fan_actor.GetProperty().SetSpecular(0.5)
            self.ultrasound_fan_actor.GetProperty().SetSpecularPower(10)
            
            # 应用探头位置和方向
            self._update_ultrasound_fan()
            
            return self.ultrasound_fan_actor
            
        except Exception as e:
            warnings.warn(f"创建超声扇形演员失败: {e}")
            return None
    
    def calculate_cross_section(self, volume_data: Optional[np.ndarray] = None,
                               spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0),
                               origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> Optional[np.ndarray]:
        """计算超声平面与体积数据的截面
        
        参数:
            volume_data: 3D体积数据
            spacing: 体素间距
            origin: 体积原点
            
        返回:
            2D截面图像，如果无法计算则返回None
        """
        if volume_data is None:
            # 如果没有体积数据，创建模拟截面
            return self._create_simulated_cross_section()
        
        try:
            # 计算截面平面
            plane_normal = self.probe_direction
            plane_point = self.probe_position
            
            # 这里需要实现实际的体积数据截面计算
            # 这是一个简化版本，返回一个模拟图像
            return self._create_simulated_cross_section()
            
        except Exception as e:
            warnings.warn(f"计算截面失败: {e}")
            return None
    
    def _create_simulated_cross_section(self) -> np.ndarray:
        """创建模拟截面图像"""
        # 创建一个256x256的模拟超声图像
        size = 256
        image = np.zeros((size, size), dtype=np.float32)
        
        # 计算图像中心
        center_x, center_y = size // 2, size // 2
        
        # 添加心脏轮廓 (椭圆)
        heart_radius_x = int(self.heart_radius * 0.8)
        heart_radius_y = int(self.heart_radius * 0.6)
        
        for i in range(size):
            for j in range(size):
                # 计算到中心的距离
                dx = (i - center_x) / heart_radius_x
                dy = (j - center_y) / heart_radius_y
                distance = np.sqrt(dx*dx + dy*dy)
                
                if distance < 1.0:
                    # 心脏内部
                    value = 0.7 - distance * 0.3
                    image[i, j] = value
                
                # 添加一些纹理
                if np.random.random() < 0.01:
                    image[i, j] += np.random.random() * 0.2 - 0.1
        
        # 添加探头位置标记
        probe_marker_size = 5
        for i in range(-probe_marker_size, probe_marker_size + 1):
            for j in range(-probe_marker_size, probe_marker_size + 1):
                x = center_x + i
                y = center_y + j
                if 0 <= x < size and 0 <= y < size:
                    if abs(i) <= 1 and abs(j) <= 1:
                        image[x, y] = 1.0  # 中心亮点
                    else:
                        image[x, y] = min(1.0, image[x, y] + 0.3)
        
        # 归一化到0-1范围
        image = np.clip(image, 0, 1)
        
        self.cross_section_data = image
        return image
    
    def _update_probe_visualization(self):
        """更新探头可视化"""
        if self.probe_actor is None:
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
        
        # 应用绕自身轴的旋转
        if self.probe_rotation != 0:
            transform.RotateZ(self.probe_rotation)
        
        self.probe_actor.SetUserTransform(transform)
    
    def _update_ultrasound_fan(self):
        """更新超声扇形"""
        if self.ultrasound_fan_actor is None:
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
        
        # 应用绕自身轴的旋转
        if self.probe_rotation != 0:
            transform.RotateZ(self.probe_rotation)
        
        self.ultrasound_fan_actor.SetUserTransform(transform)
    
    def get_probe_info(self) -> Dict[str, Any]:
        """获取探头信息"""
        return {
            'position': self.probe_position,
            'direction': self.probe_direction,
            'rotation': self.probe_rotation,
            'ultrasound_angle': self.ultrasound_angle,
            'ultrasound_radius': self.ultrasound_radius,
            'frequency': self.frequency
        }
    
    def get_cross_section_data(self) -> Optional[np.ndarray]:
        """获取截面数据"""
        return self.cross_section_data
    
    def clear(self):
        """清除所有VTK对象"""
        self.probe_actor = None
        self.ultrasound_fan_actor = None
        self.intersection_actor = None
        self.cross_section_data = None


# 单例实例
_tee_simulator_instance: Optional[TEESimulator] = None

def get_tee_simulator() -> TEESimulator:
    """获取TEE模拟器单例实例"""
    global _tee_simulator_instance
    if _tee_simulator_instance is None:
        _tee_simulator_instance = TEESimulator()
    return _tee_simulator_instance
