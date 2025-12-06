"""
DICOM管理器模块 - 负责DICOM文件加载和处理

此模块按照关注点分享原则，将DICOM相关逻辑从主窗口中分离出来。
"""

import os


class DICOMManager:
    """DICOM文件管理器"""
    
    def __init__(self):
        self.dicom_loader = None
        self.current_file_path = None
        self.current_dir_path = None
    
    def load_file(self, file_path):
        """加载DICOM文件"""
        try:
            from core.dicom_loader import get_dicom_loader
            
            # 获取DICOM加载器
            self.dicom_loader = get_dicom_loader()
            
            # 加载文件
            success = self.dicom_loader.load_file(file_path)
            
            if success:
                self.current_file_path = file_path
                return True
            else:
                return False
                
        except Exception as e:
            print(f"加载DICOM文件失败: {e}")
            return False
    
    def load_directory(self, dir_path):
        """加载DICOM文件夹"""
        try:
            from core.dicom_loader import get_dicom_loader
            
            # 获取DICOM加载器
            self.dicom_loader = get_dicom_loader()
            
            # 加载文件夹
            success = self.dicom_loader.load_directory(dir_path)
            
            if success:
                self.current_dir_path = dir_path
                return True
            else:
                return False
                
        except Exception as e:
            print(f"加载DICOM文件夹失败: {e}")
            return False
    
    def get_patient_info(self):
        """获取患者信息"""
        if self.dicom_loader is None:
            return {
                'patient_id': '未加载',
                'patient_name': '未加载',
                'study_date': '未加载',
                'modality': '未加载'
            }
        
        try:
            return self.dicom_loader.get_patient_info()
        except Exception as e:
            print(f"获取患者信息失败: {e}")
            return {
                'patient_id': '错误',
                'patient_name': '错误',
                'study_date': '错误',
                'modality': '错误'
            }
    
    def get_image_data(self):
        """获取图像数据"""
        if self.dicom_loader is None:
            return None
        
        try:
            return self.dicom_loader.get_image_data()
        except Exception as e:
            print(f"获取图像数据失败: {e}")
            return None
    
    def get_volume_data(self):
        """获取体积数据"""
        if self.dicom_loader is None:
            return None
        
        try:
            return self.dicom_loader.get_volume_data()
        except Exception as e:
            print(f"获取体积数据失败: {e}")
            return None
    
    def get_spacing(self):
        """获取间距信息"""
        if self.dicom_loader is None:
            return None
        
        try:
            return self.dicom_loader.get_spacing()
        except Exception as e:
            print(f"获取间距信息失败: {e}")
            return None
    
    def get_origin(self):
        """获取原点信息"""
        if self.dicom_loader is None:
            return None
        
        try:
            return self.dicom_loader.get_origin()
        except Exception as e:
            print(f"获取原点信息失败: {e}")
            return None
    
    def get_current_file_info(self):
        """获取当前文件信息"""
        if self.current_file_path:
            return {
                'type': 'file',
                'path': self.current_file_path,
                'name': os.path.basename(self.current_file_path)
            }
        elif self.current_dir_path:
            return {
                'type': 'directory',
                'path': self.current_dir_path,
                'name': os.path.basename(self.current_dir_path)
            }
        else:
            return {
                'type': 'none',
                'path': None,
                'name': '未加载'
            }
    
    def is_loaded(self):
        """检查是否已加载DICOM数据"""
        return self.dicom_loader is not None
