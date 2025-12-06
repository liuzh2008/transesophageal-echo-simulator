#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DICOM截面切割模块
包含平面切割、截面显示等功能
"""

import math
from dicom_renderer import calculate_plane_normal

def create_cut_plane(image_data, nx, ny, nz):
    """创建切割平面"""
    try:
        import vtk
        
        # 获取体积的边界框和中心点
        bounds = image_data.GetBounds()
        center = [
            (bounds[0] + bounds[1]) / 2,
            (bounds[2] + bounds[3]) / 2,
            (bounds[4] + bounds[5]) / 2
        ]
        
        print(f"体积中心点: ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})")
        print(f"X轴范围: [{bounds[0]:.1f}, {bounds[1]:.1f}]")
        print(f"Y轴范围: [{bounds[2]:.1f}, {bounds[3]:.1f}]")
        print(f"Z轴范围: [{bounds[4]:.1f}, {bounds[5]:.1f}]")
        
        # 创建切割平面
        plane = vtk.vtkPlane()
        plane.SetOrigin(center[0], center[1], center[2])
        plane.SetNormal(nx, ny, nz)
        
        return plane, center
        
    except Exception as e:
        print(f"创建切割平面失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def create_cut_surface(image_data, nx, ny, nz):
    """创建切割表面（显示为3D中的线条和平面）"""
    try:
        import vtk
        
        print(f"\n创建切割表面...")
        print(f"平面法线: ({nx:.3f}, {ny:.3f}, {nz:.3f})")
        
        # 创建切割平面
        plane, center = create_cut_plane(image_data, nx, ny, nz)
        if not plane:
            return None, None
        
        # 创建切割器
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputData(image_data)
        cutter.Update()
        
        # 获取切割结果
        cut_polydata = cutter.GetOutput()
        
        print(f"横截面信息:")
        print(f"  点数: {cut_polydata.GetNumberOfPoints():,}")
        print(f"  多边形数: {cut_polydata.GetNumberOfCells():,}")
        
        # 创建横截面映射器
        cut_mapper = vtk.vtkPolyDataMapper()
        cut_mapper.SetInputData(cut_polydata)
        
        # 创建横截面Actor（线条）
        cut_actor = vtk.vtkActor()
        cut_actor.SetMapper(cut_mapper)
        cut_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # 红色横截面
        cut_actor.GetProperty().SetLineWidth(2.0)
        cut_actor.GetProperty().SetOpacity(0.7)
        
        # 创建横截面填充（显示为平面）
        fill_actor = None
        if cut_polydata.GetNumberOfPoints() > 0:
            # 创建轮廓三角化器
            triangulator = vtk.vtkContourTriangulator()
            triangulator.SetInputData(cut_polydata)
            triangulator.Update()
            
            filled_polydata = triangulator.GetOutput()
            
            if filled_polydata.GetNumberOfPolys() > 0:
                # 创建填充平面映射器
                fill_mapper = vtk.vtkPolyDataMapper()
                fill_mapper.SetInputData(filled_polydata)
                
                # 创建填充平面Actor
                fill_actor = vtk.vtkActor()
                fill_actor.SetMapper(fill_mapper)
                fill_actor.GetProperty().SetColor(0.8, 0.2, 0.2)  # 浅红色
                fill_actor.GetProperty().SetOpacity(0.3)
                fill_actor.GetProperty().SetRepresentationToSurface()
                
                print(f"  横截面填充平面创建成功")
            else:
                print(f"  注意: 无法创建横截面填充平面")
        else:
            print(f"  注意: 横截面数据为空")
        
        print("切割表面创建完成")
        
        return cut_actor, fill_actor
        
    except Exception as e:
        print(f"创建切割表面失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def create_horizontal_cut(image_data, cut_percent=50):
    """创建水平切割（Z轴方向）"""
    try:
        import vtk
        
        print(f"\n创建水平切割（{cut_percent}%高度）...")
        
        # 获取体积的边界框
        bounds = image_data.GetBounds()
        z_min, z_max = bounds[4], bounds[5]
        
        # 计算切割位置
        cut_z = z_min + (z_max - z_min) * (cut_percent / 100.0)
        print(f"切割位置: Z = {cut_z:.1f} (高度{cut_percent}%)")
        print(f"Z轴范围: [{z_min:.1f}, {z_max:.1f}]")
        
        # 创建水平切割平面
        plane = vtk.vtkPlane()
        plane.SetOrigin(0, 0, cut_z)
        plane.SetNormal(0, 0, 1)  # 水平切割
        
        # 创建切割器
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputData(image_data)
        cutter.Update()
        
        # 获取切割结果
        cut_polydata = cutter.GetOutput()
        
        print(f"水平横截面信息:")
        print(f"  点数: {cut_polydata.GetNumberOfPoints():,}")
        print(f"  多边形数: {cut_polydata.GetNumberOfCells():,}")
        
        # 创建横截面映射器
        cut_mapper = vtk.vtkPolyDataMapper()
        cut_mapper.SetInputData(cut_polydata)
        
        # 创建横截面Actor
        cut_actor = vtk.vtkActor()
        cut_actor.SetMapper(cut_mapper)
        cut_actor.GetProperty().SetColor(0.0, 1.0, 0.0)  # 绿色横截面
        cut_actor.GetProperty().SetLineWidth(2.0)
        cut_actor.GetProperty().SetOpacity(0.7)
        
        return cut_actor, cut_z
        
    except Exception as e:
        print(f"创建水平切割失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def create_rao_lao_cut(image_data, rao_angle=30, lao_angle=20):
    """创建RAO+LAO角度切割"""
    try:
        import vtk
        
        print(f"\n创建RAO {rao_angle}° + LAO {lao_angle}°角度切割...")
        
        # 计算平面法线向量
        nx, ny, nz = calculate_plane_normal(rao_angle, lao_angle)
        
        # 创建切割表面
        cut_actor, fill_actor = create_cut_surface(image_data, nx, ny, nz)
        
        return cut_actor, fill_actor, (nx, ny, nz)
        
    except Exception as e:
        print(f"创建RAO+LAO角度切割失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None
