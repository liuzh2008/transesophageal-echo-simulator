"""
DICOM加载器模块 - 处理DICOM文件的加载和解析

此模块负责读取DICOM文件，提取患者信息和影像数据。
"""

import os
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import warnings

try:
    import pydicom
    from pydicom.dataset import Dataset
    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False
    warnings.warn("pydicom库未安装，DICOM功能将受限")


class DICOMLoader:
    """DICOM文件加载器"""
    
    def __init__(self):
        self.datasets: List[Dataset] = []
        self.patient_info: Dict[str, Any] = {}
        self.image_data: Optional[np.ndarray] = None
        self.spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
        self.origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    def load_file(self, file_path: str) -> bool:
        """加载单个DICOM文件
        
        参数:
            file_path: DICOM文件路径
            
        返回:
            bool: 加载是否成功
        """
        if not PYDICOM_AVAILABLE:
            warnings.warn("pydicom不可用，无法加载DICOM文件")
            return False
        
        try:
            dataset = pydicom.dcmread(file_path)
            self.datasets = [dataset]
            self._extract_patient_info(dataset)
            self._extract_image_data(dataset)
            return True
        except Exception as e:
            warnings.warn(f"加载DICOM文件失败: {e}")
            return False
    
    def load_directory(self, dir_path: str) -> bool:
        """加载目录中的所有DICOM文件
        
        参数:
            dir_path: 包含DICOM文件的目录路径
            
        返回:
            bool: 加载是否成功
        """
        if not PYDICOM_AVAILABLE:
            warnings.warn("pydicom不可用，无法加载DICOM文件")
            return False
        
        try:
            dicom_files = []
            for root, _, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 尝试所有文件，不仅仅是特定扩展名
                    # 首先检查常见DICOM扩展名
                    if file.lower().endswith(('.dcm', '.dicom', '.ima')):
                        dicom_files.append(file_path)
                    else:
                        # 对于无扩展名文件，尝试读取前几个字节来判断是否为DICOM
                        try:
                            with open(file_path, 'rb') as f:
                                # DICOM文件通常以"DICM"魔术字节开头
                                f.seek(128)
                                magic = f.read(4)
                                if magic == b'DICM':
                                    dicom_files.append(file_path)
                        except:
                            pass
            
            if not dicom_files:
                warnings.warn(f"在目录中未找到DICOM文件: {dir_path}")
                return False
            
            # 加载所有文件
            self.datasets = []
            successful_files = 0
            for file_path in dicom_files:
                try:
                    dataset = pydicom.dcmread(file_path)
                    self.datasets.append(dataset)
                    successful_files += 1
                except Exception as e:
                    warnings.warn(f"加载文件失败 {file_path}: {e}")
            
            if not self.datasets:
                warnings.warn("所有DICOM文件加载失败")
                return False
            
            print(f"成功加载 {successful_files} 个DICOM文件")
            
            # 按位置排序（如果可能）
            self._sort_datasets()
            
            # 提取信息（使用第一个数据集）
            self._extract_patient_info(self.datasets[0])
            
            # 提取图像数据（3D体积）
            self._extract_volume_data()
            
            return True
        except Exception as e:
            warnings.warn(f"加载DICOM目录失败: {e}")
            return False
    
    def _extract_patient_info(self, dataset: Dataset):
        """从DICOM数据集中提取患者信息"""
        self.patient_info = {
            'patient_id': getattr(dataset, 'PatientID', '未知'),
            'patient_name': str(getattr(dataset, 'PatientName', '未知')),
            'patient_birth_date': getattr(dataset, 'PatientBirthDate', '未知'),
            'patient_sex': getattr(dataset, 'PatientSex', '未知'),
            'study_date': getattr(dataset, 'StudyDate', '未知'),
            'study_time': getattr(dataset, 'StudyTime', '未知'),
            'study_description': getattr(dataset, 'StudyDescription', '未知'),
            'modality': getattr(dataset, 'Modality', '未知'),
            'institution_name': getattr(dataset, 'InstitutionName', '未知'),
            'series_description': getattr(dataset, 'SeriesDescription', '未知'),
            'slice_thickness': getattr(dataset, 'SliceThickness', 1.0),
            'rows': getattr(dataset, 'Rows', 0),
            'columns': getattr(dataset, 'Columns', 0),
            'pixel_spacing': getattr(dataset, 'PixelSpacing', [1.0, 1.0]),
        }
    
    def _extract_image_data(self, dataset: Dataset):
        """从单个DICOM数据集中提取图像数据"""
        try:
            # 获取像素数组
            pixel_array = dataset.pixel_array
            
            # 转换为numpy数组
            self.image_data = pixel_array.astype(np.float32)
            
            # 应用窗宽窗位（如果存在）
            if hasattr(dataset, 'WindowCenter') and hasattr(dataset, 'WindowWidth'):
                window_center = float(dataset.WindowCenter)
                window_width = float(dataset.WindowWidth)
                self._apply_window_level(window_center, window_width)
            
            # 归一化到0-1范围
            if self.image_data is not None:
                min_val = np.min(self.image_data)
                max_val = np.max(self.image_data)
                if max_val > min_val:
                    self.image_data = (self.image_data - min_val) / (max_val - min_val)
            
        except Exception as e:
            warnings.warn(f"提取图像数据失败: {e}")
            self.image_data = None
    
    def _extract_volume_data(self):
        """从多个DICOM切片中提取3D体积数据"""
        if len(self.datasets) < 2:
            # 只有一个切片，使用单个图像数据
            self._extract_image_data(self.datasets[0])
            self.image_data = np.expand_dims(self.image_data, axis=2) if self.image_data is not None else None
            return
        
        try:
            # 获取所有切片的像素数据
            slices = []
            spacings = []
            positions = []
            
            for dataset in self.datasets:
                # 提取图像数据
                pixel_array = dataset.pixel_array.astype(np.float32)
                slices.append(pixel_array)
                
                # 提取间距信息
                pixel_spacing = getattr(dataset, 'PixelSpacing', [1.0, 1.0])
                slice_thickness = getattr(dataset, 'SliceThickness', 1.0)
                spacings.append((float(pixel_spacing[0]), float(pixel_spacing[1]), float(slice_thickness)))
                
                # 提取切片位置
                if hasattr(dataset, 'ImagePositionPatient'):
                    position = [float(x) for x in dataset.ImagePositionPatient]
                    positions.append(position)
            
            # 创建3D体积
            if slices:
                # 假设所有切片尺寸相同
                slice_shape = slices[0].shape
                volume_shape = (slice_shape[0], slice_shape[1], len(slices))
                self.image_data = np.zeros(volume_shape, dtype=np.float32)
                
                for i, slice_data in enumerate(slices):
                    if slice_data.shape == slice_shape:
                        self.image_data[:, :, i] = slice_data
                
                # 计算平均间距
                if spacings:
                    avg_spacing = np.mean(spacings, axis=0)
                    self.spacing = tuple(avg_spacing)
                
                # 计算原点
                if positions:
                    self.origin = tuple(np.min(positions, axis=0))
                
                # 归一化
                min_val = np.min(self.image_data)
                max_val = np.max(self.image_data)
                if max_val > min_val:
                    self.image_data = (self.image_data - min_val) / (max_val - min_val)
            
        except Exception as e:
            warnings.warn(f"提取体积数据失败: {e}")
            self.image_data = None
    
    def _sort_datasets(self):
        """按切片位置对数据集进行排序"""
        if len(self.datasets) < 2:
            return
        
        try:
            # 尝试按ImagePositionPatient排序
            positions = []
            for dataset in self.datasets:
                if hasattr(dataset, 'ImagePositionPatient'):
                    position = [float(x) for x in dataset.ImagePositionPatient]
                    positions.append(position)
                else:
                    positions.append([0, 0, 0])
            
            # 按Z坐标排序
            z_coords = [pos[2] for pos in positions]
            sorted_indices = np.argsort(z_coords)
            self.datasets = [self.datasets[i] for i in sorted_indices]
            
        except Exception as e:
            warnings.warn(f"排序数据集失败: {e}")
    
    def _apply_window_level(self, window_center: float, window_width: float):
        """应用窗宽窗位到图像数据"""
        if self.image_data is None:
            return
        
        # 计算窗范围
        window_min = window_center - window_width / 2
        window_max = window_center + window_width / 2
        
        # 应用窗
        self.image_data = np.clip(self.image_data, window_min, window_max)
        self.image_data = (self.image_data - window_min) / window_width
        self.image_data = np.clip(self.image_data, 0, 1)
    
    def get_patient_info(self) -> Dict[str, Any]:
        """获取患者信息"""
        return self.patient_info.copy()
    
    def get_image_data(self) -> Optional[np.ndarray]:
        """获取图像数据"""
        return self.image_data
    
    def get_volume_data(self) -> Optional[np.ndarray]:
        """获取3D体积数据"""
        return self.image_data
    
    def get_spacing(self) -> Tuple[float, float, float]:
        """获取体素间距"""
        return self.spacing
    
    def get_origin(self) -> Tuple[float, float, float]:
        """获取体积原点"""
        return self.origin
    
    def clear(self):
        """清除加载的数据"""
        self.datasets.clear()
        self.patient_info.clear()
        self.image_data = None
        self.spacing = (1.0, 1.0, 1.0)
        self.origin = (0.0, 0.0, 0.0)


# 单例实例
_dicom_loader_instance: Optional[DICOMLoader] = None

def get_dicom_loader() -> DICOMLoader:
    """获取DICOM加载器单例实例"""
    global _dicom_loader_instance
    if _dicom_loader_instance is None:
        _dicom_loader_instance = DICOMLoader()
    return _dicom_loader_instance
