"""
经食管超声模拟模块 - 简化版本

此模块已移除超声探头相关功能，只保留基本的DICOM查看功能。
"""

import numpy as np
from typing import Tuple, Optional, List, Dict, Any
import warnings

try:
    import vtk
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False
    warnings.warn("VTK库未安装，3D渲染功能将受限")


class TEESimulator:
    """经食管超声模拟器 - 简化版本（已移除探头功能）"""
    
    def __init__(self):
        # 心脏模型参数（保留用于参考）
        self.heart_center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.heart_radius: float = 50.0  # 心脏半径 (mm)
        
        # 超声参数（保留用于参考）
        self.ultrasound_angle: float = 60.0  # 扇形角度 (度)
        self.ultrasound_radius: float = 100.0  # 扇形半径 (mm)
    
    def set_heart_model(self, center: Tuple[float, float, float], radius: float = 50.0):
        """设置心脏模型参数"""
        self.heart_center = center
        self.heart_radius = max(10.0, radius)
    
    def set_ultrasound_parameters(self, angle: float = 60.0, radius: float = 100.0):
        """设置超声参数（保留用于参考）"""
        self.ultrasound_angle = max(10.0, min(120.0, angle))  # 限制在10-120度
        self.ultrasound_radius = max(10.0, min(200.0, radius))  # 限制在10-200mm
    
    def calculate_plane_normal_from_angles(self, rao_angle: float, lao_angle: float) -> Tuple[float, float, float]:
        """根据RAO和LAO角度计算平面法线向量
        
        参数:
            rao_angle: RAO角度 (度)
            lao_angle: LAO角度 (度)
            
        返回:
            平面法线向量 (nx, ny, nz)
        """
        import math
        
        # 将角度转换为弧度
        rao_rad = math.radians(rao_angle)
        lao_rad = math.radians(lao_angle)
        
        # 计算法线向量
        # RAO主要影响X-Z平面，LAO主要影响Y-Z平面
        nx = math.sin(rao_rad)
        ny = math.sin(lao_rad)
        nz = math.cos(rao_rad) * math.cos(lao_rad)
        
        # 归一化
        length = math.sqrt(nx*nx + ny*ny + nz*nz)
        if length > 0:
            nx /= length
            ny /= length
            nz /= length
        
        return (nx, ny, nz)
    
    def get_info(self) -> Dict[str, Any]:
        """获取模拟器信息"""
        return {
            'heart_center': self.heart_center,
            'heart_radius': self.heart_radius,
            'ultrasound_angle': self.ultrasound_angle,
            'ultrasound_radius': self.ultrasound_radius
        }
    
    def clear(self):
        """清除所有数据"""
        # 此版本没有需要清除的VTK对象
        pass


# 单例实例
_tee_simulator_instance: Optional[TEESimulator] = None

def get_tee_simulator() -> TEESimulator:
    """获取TEE模拟器单例实例"""
    global _tee_simulator_instance
    if _tee_simulator_instance is None:
        _tee_simulator_instance = TEESimulator()
    return _tee_simulator_instance
