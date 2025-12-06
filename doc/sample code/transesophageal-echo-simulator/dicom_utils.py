#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DICOM工具模块
包含安装包检测、目录检测等通用功能
"""

import os
import sys
import time

class ProgressObserver:
    """VTK进度观察器"""
    def __init__(self, task_name="处理"):
        self.progress = 0.0
        self.start_time = time.time()
        self.task_name = task_name
        
    def __call__(self, obj, event):
        if event == "ProgressEvent":
            try:
                self.progress = obj.GetProgress()
                elapsed = time.time() - self.start_time
                bar_length = 50
                filled_length = int(bar_length * self.progress)
                bar = '=' * filled_length + ' ' * (bar_length - filled_length)
                percent = self.progress * 100
                sys.stdout.write(f'\r{self.task_name}: [{bar}] {percent:.1f}% - 耗时: {elapsed:.1f}秒')
                sys.stdout.flush()
            except:
                pass

def install_required_packages():
    """安装必要的包"""
    try:
        import vtk
        print("VTK已安装")
        return True
    except ImportError:
        print("正在安装VTK...")
        os.system("pip install vtk")
        try:
            import vtk
            print("VTK安装成功")
            return True
        except ImportError:
            print("VTK安装失败")
            return False

def check_dicom_directory(dicom_dir):
    """检查DICOM目录是否存在并包含DICOM文件"""
    if not os.path.exists(dicom_dir):
        print(f"错误: 目录不存在 {repr(dicom_dir)}")
        return False
    
    # 检查目录中是否有DICOM文件
    dicom_files = []
    for f in os.listdir(dicom_dir):
        if (f.lower().endswith(('.dcm', '.dicom')) or 
            f.startswith('IM') or
            f.isdigit() or
            '.' not in f):
            dicom_files.append(f)
    
    if not dicom_files:
        print(f"错误: 目录中没有DICOM文件")
        return False
    
    print(f"找到 {len(dicom_files)} 个DICOM文件")
    return True

def load_dicom_sequence(dicom_dir):
    """加载DICOM序列"""
    try:
        import vtk
        
        print(f"正在加载DICOM序列: {repr(dicom_dir)}")
        
        if not check_dicom_directory(dicom_dir):
            return None
        
        # 创建进度观察器
        progress_observer = ProgressObserver("加载DICOM序列")
        
        # 创建DICOM读取器
        reader = vtk.vtkDICOMImageReader()
        reader.SetDirectoryName(dicom_dir)
        
        # 添加进度观察器
        reader.AddObserver("ProgressEvent", progress_observer)
        
        # 读取数据
        print("\n开始读取DICOM序列...")
        start_time = time.time()
        reader.Update()
        load_time = time.time() - start_time
        
        print(f"\nDICOM序列加载完成，耗时: {load_time:.2f}秒")
        
        # 获取图像数据
        image_data = reader.GetOutput()
        
        if image_data.GetNumberOfPoints() == 0:
            print("错误: 无法加载DICOM序列或数据为空")
            return None
        
        # 获取数据信息
        dimensions = image_data.GetDimensions()
        spacing = image_data.GetSpacing()
        origin = image_data.GetOrigin()
        
        print(f"DICOM序列信息:")
        print(f"  维度: {dimensions[0]} × {dimensions[1]} × {dimensions[2]}")
        print(f"  间距: {spacing[0]:.3f} × {spacing[1]:.3f} × {spacing[2]:.3f} mm")
        print(f"  原点: {origin[0]:.1f}, {origin[1]:.1f}, {origin[2]:.1f}")
        
        # 获取标量范围
        scalar_range = image_data.GetScalarRange()
        print(f"  像素值范围: [{scalar_range[0]:.1f}, {scalar_range[1]:.1f}]")
        
        return image_data, reader
        
    except Exception as e:
        print(f"加载DICOM序列失败: {e}")
        import traceback
        traceback.print_exc()
        return None
