#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DICOM序列3D体积渲染器 - 带横截面功能
支持加载DICOM序列，显示3D体积，并在50%高度进行水平横切
"""

import os
import sys
import time

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

def load_dicom_sequence(dicom_dir):
    """加载DICOM序列"""
    try:
        import vtk
        
        print(f"正在加载DICOM序列: {repr(dicom_dir)}")
        
        if not os.path.exists(dicom_dir):
            print(f"错误: 目录不存在 {repr(dicom_dir)}")
            return None
        
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
            return None
        
        print(f"找到 {len(dicom_files)} 个DICOM文件")
        
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

def calculate_plane_normal(rao_angle=30, lao_angle=20):
    """计算RAO和LAO角度对应的平面法线向量"""
    import math
    
    # 将角度转换为弧度
    rao_rad = math.radians(rao_angle)
    lao_rad = math.radians(lao_angle)
    
    # 在心脏影像学中：
    # RAO (右前斜位): 从右前方向观察
    # LAO (左前斜位): 从左前方向观察
    # 通常这些角度用于定义观察方向，而不是平面法线
    
    # 对于切割平面，我们需要一个法线向量
    # 一个常见的方法是创建一个复合角度的平面
    
    # 方法1：创建一个倾斜平面，结合RAO和LAO角度
    # X轴：左右方向（右为正）
    # Y轴：前后方向（前为正）
    # Z轴：头脚方向（头为正）
    
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
    
    print(f"平面法线向量: ({nx:.3f}, {ny:.3f}, {nz:.3f})")
    print(f"RAO角度: {rao_angle}°, LAO角度: {lao_angle}°")
    
    return (nx, ny, nz)

def create_volume_with_rao_lao_cut(image_data, rao_angle=30, lao_angle=20):
    """创建带RAO+LAO角度切割的3D体积渲染"""
    try:
        import vtk
        import math
        
        print(f"\n创建3D体积渲染（带RAO {rao_angle}° + LAO {lao_angle}°切割）...")
        
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
        
        # 计算平面法线向量
        nx, ny, nz = calculate_plane_normal(rao_angle, lao_angle)
        
        # 创建进度观察器
        progress_observer = ProgressObserver("创建体积渲染")
        
        # 创建体积映射器
        volume_mapper = vtk.vtkFixedPointVolumeRayCastMapper()
        volume_mapper.SetInputData(image_data)
        
        # 添加进度观察器
        volume_mapper.AddObserver("ProgressEvent", progress_observer)
        
        # 设置采样距离
        volume_mapper.SetSampleDistance(0.5)
        volume_mapper.SetAutoAdjustSampleDistances(1)
        
        # 创建体积属性
        volume_property = vtk.vtkVolumeProperty()
        volume_property.ShadeOn()
        volume_property.SetInterpolationTypeToLinear()
        
        # 设置传输函数
        color_transfer_function = vtk.vtkColorTransferFunction()
        opacity_transfer_function = vtk.vtkPiecewiseFunction()
        
        scalar_range = image_data.GetScalarRange()
        min_val, max_val = scalar_range
        
        # CT数据颜色映射
        if max_val - min_val > 2000:
            color_transfer_function.AddRGBPoint(min_val, 0.0, 0.0, 0.0)
            color_transfer_function.AddRGBPoint(min_val + (max_val - min_val) * 0.3, 0.5, 0.5, 0.5)
            color_transfer_function.AddRGBPoint(min_val + (max_val - min_val) * 0.6, 1.0, 0.7, 0.5)
            color_transfer_function.AddRGBPoint(max_val, 1.0, 1.0, 0.9)
        else:
            color_transfer_function.AddRGBPoint(min_val, 0.0, 0.0, 0.0)
            color_transfer_function.AddRGBPoint(min_val + (max_val - min_val) * 0.3, 0.0, 0.0, 1.0)
            color_transfer_function.AddRGBPoint(min_val + (max_val - min_val) * 0.6, 0.0, 1.0, 0.0)
            color_transfer_function.AddRGBPoint(max_val, 1.0, 0.0, 0.0)
        
        opacity_transfer_function.AddPoint(min_val, 0.0)
        opacity_transfer_function.AddPoint(min_val + (max_val - min_val) * 0.1, 0.0)
        opacity_transfer_function.AddPoint(min_val + (max_val - min_val) * 0.3, 0.1)
        opacity_transfer_function.AddPoint(min_val + (max_val - min_val) * 0.6, 0.3)
        opacity_transfer_function.AddPoint(max_val, 0.6)
        
        volume_property.SetColor(color_transfer_function)
        volume_property.SetScalarOpacity(opacity_transfer_function)
        
        # 创建体积
        volume = vtk.vtkVolume()
        volume.SetMapper(volume_mapper)
        volume.SetProperty(volume_property)
        
        # 创建切割平面（RAO+LAO角度）
        plane = vtk.vtkPlane()
        plane.SetOrigin(center[0], center[1], center[2])
        plane.SetNormal(nx, ny, nz)
        
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
        
        # 创建横截面Actor
        cut_actor = vtk.vtkActor()
        cut_actor.SetMapper(cut_mapper)
        cut_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # 红色横截面
        cut_actor.GetProperty().SetLineWidth(2.0)
        cut_actor.GetProperty().SetOpacity(0.7)
        
        # 创建横截面填充（显示为平面）
        # 提取横截面轮廓并创建填充平面
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
                fill_actor = None
                print(f"  注意: 无法创建横截面填充平面")
        else:
            fill_actor = None
            print(f"  注意: 横截面数据为空")
        
        print("体积渲染创建完成")
        
        return volume, cut_actor, fill_actor, (nx, ny, nz)
        
    except Exception as e:
        print(f"创建体积渲染失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_rao_lao_slice_view(image_data, nx, ny, nz):
    """创建RAO+LAO角度的2D切片视图"""
    try:
        import vtk
        import math
        
        print(f"\n创建RAO+LAO角度切片视图...")
        print(f"平面法线: ({nx:.3f}, {ny:.3f}, {nz:.3f})")
        
        # 获取体积的边界框和中心点
        bounds = image_data.GetBounds()
        center = [
            (bounds[0] + bounds[1]) / 2,
            (bounds[2] + bounds[3]) / 2,
            (bounds[4] + bounds[5]) / 2
        ]
        
        # 创建垂直于法线向量的切片
        # 我们需要创建一个坐标系，其中Z轴与法线向量对齐
        
        # 计算法线向量的角度
        # 计算与Z轴的夹角
        angle_with_z = math.degrees(math.acos(abs(nz)))
        
        # 创建旋转矩阵
        # 首先计算旋转轴（法线向量与Z轴的叉积）
        import numpy as np
        
        # 目标Z轴（法线向量）
        target_z = np.array([nx, ny, nz])
        
        # 源Z轴（原始Z轴）
        source_z = np.array([0, 0, 1])
        
        # 计算旋转轴
        rotation_axis = np.cross(source_z, target_z)
        axis_length = np.linalg.norm(rotation_axis)
        
        if axis_length > 0:
            rotation_axis = rotation_axis / axis_length
            # 计算旋转角度
            rotation_angle = math.acos(np.dot(source_z, target_z))
        else:
            # 向量平行，不需要旋转
            rotation_axis = np.array([1, 0, 0])
            rotation_angle = 0
        
        print(f"旋转角度: {math.degrees(rotation_angle):.1f}°")
        print(f"旋转轴: ({rotation_axis[0]:.3f}, {rotation_axis[1]:.3f}, {rotation_axis[2]:.3f})")
        
        # 创建切片提取器
        reslice = vtk.vtkImageReslice()
        reslice.SetInputData(image_data)
        reslice.SetOutputDimensionality(2)
        
        # 设置切片方向（垂直于法线向量）
        # 我们需要创建两个正交向量作为切片的X和Y轴
        
        # 创建切片的坐标系
        # Z轴：法线向量（切片平面的法线）
        # X轴：任意与Z轴正交的向量
        # Y轴：Z轴 × X轴
        
        # 选择一个参考向量（通常使用[1, 0, 0]或[0, 1, 0]）
        if abs(nx) < 0.5:
            ref_vector = np.array([1, 0, 0])
        else:
            ref_vector = np.array([0, 1, 0])
        
        # 计算X轴（与法线向量正交）
        x_axis = np.cross(ref_vector, target_z)
        if np.linalg.norm(x_axis) < 0.001:
            # 如果叉积太小，尝试另一个参考向量
            ref_vector = np.array([0, 0, 1])
            x_axis = np.cross(ref_vector, target_z)
        
        x_axis = x_axis / np.linalg.norm(x_axis)
        
        # 计算Y轴
        y_axis = np.cross(target_z, x_axis)
        y_axis = y_axis / np.linalg.norm(y_axis)
        
        print(f"切片X轴: ({x_axis[0]:.3f}, {x_axis[1]:.3f}, {x_axis[2]:.3f})")
        print(f"切片Y轴: ({y_axis[0]:.3f}, {y_axis[1]:.3f}, {y_axis[2]:.3f})")
        
        # 设置方向余弦矩阵
        reslice.SetResliceAxesDirectionCosines(
            x_axis[0], x_axis[1], x_axis[2],
            y_axis[0], y_axis[1], y_axis[2],
            nx, ny, nz
        )
        
        # 设置切片原点为中心点
        reslice.SetResliceAxesOrigin(center[0], center[1], center[2])
        reslice.SetInterpolationModeToLinear()
        
        # 创建图像映射器
        image_mapper = vtk.vtkImageMapper()
        image_mapper.SetInputConnection(reslice.GetOutputPort())
        image_mapper.SetColorWindow(255)
        image_mapper.SetColorLevel(128)
        
        # 创建2D Actor
        image_actor = vtk.vtkActor2D()
        image_actor.SetMapper(image_mapper)
        
        # 创建渲染器
        renderer = vtk.vtkRenderer()
        renderer.AddActor2D(image_actor)
        renderer.SetBackground(0.2, 0.2, 0.3)
        
        # 添加文本标注
        text_actor = vtk.vtkTextActor()
        text_actor.SetInput(f"RAO+LAO角度切片\n法线: ({nx:.2f}, {ny:.2f}, {nz:.2f})")
        text_actor.GetTextProperty().SetFontSize(14)
        text_actor.GetTextProperty().SetColor(1, 1, 1)
        text_actor.GetTextProperty().SetBackgroundColor(0, 0, 0)
        text_actor.GetTextProperty().SetBackgroundOpacity(0.7)
        text_actor.SetPosition(20, 20)
        renderer.AddActor2D(text_actor)
        
        # 设置相机为正交投影
        camera = renderer.GetActiveCamera()
        camera.ParallelProjectionOn()
        
        # 获取图像边界
        reslice.Update()
        output = reslice.GetOutput()
        if output:
            bounds = output.GetBounds()
            width = max(bounds[1] - bounds[0], bounds[3] - bounds[2]) * 1.2
            if width > 0:
                camera.SetParallelScale(width / 2)
        
        # 设置相机位置
        camera.SetPosition(0, 0, 1000)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 1, 0)
        
        print("RAO+LAO角度切片视图创建完成")
        
        return renderer
        
    except Exception as e:
        print(f"创建RAO+LAO角度切片视图失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_cross_section_view(image_data, cut_z):
    """创建2D横截面视图"""
    try:
        import vtk
        
        print(f"\n创建2D横截面视图 (Z = {cut_z:.1f})...")
        
        # 创建切片提取器（在cut_z位置提取轴向切片）
        reslice = vtk.vtkImageReslice()
        reslice.SetInputData(image_data)
        reslice.SetOutputDimensionality(2)
        reslice.SetResliceAxesDirectionCosines([1, 0, 0, 0, 1, 0, 0, 0, 1])
        reslice.SetResliceAxesOrigin([0, 0, cut_z])
        reslice.SetInterpolationModeToLinear()
        
        # 创建图像映射器
        image_mapper = vtk.vtkImageMapper()
        image_mapper.SetInputConnection(reslice.GetOutputPort())
        image_mapper.SetColorWindow(255)
        image_mapper.SetColorLevel(128)
        
        # 创建2D Actor
        image_actor = vtk.vtkActor2D()
        image_actor.SetMapper(image_mapper)
        
        # 创建渲染器
        renderer = vtk.vtkRenderer()
        renderer.AddActor2D(image_actor)
        renderer.SetBackground(0.2, 0.2, 0.3)
        
        # 添加文本标注
        text_actor = vtk.vtkTextActor()
        text_actor.SetInput(f"横截面 (Z = {cut_z:.1f} mm)")
        text_actor.GetTextProperty().SetFontSize(16)
        text_actor.GetTextProperty().SetColor(1, 1, 1)
        text_actor.GetTextProperty().SetBackgroundColor(0, 0, 0)
        text_actor.GetTextProperty().SetBackgroundOpacity(0.7)
        text_actor.SetPosition(20, 20)
        renderer.AddActor2D(text_actor)
        
        # 设置相机为正交投影
        camera = renderer.GetActiveCamera()
        camera.ParallelProjectionOn()
        
        # 获取图像边界
        reslice.Update()
        output = reslice.GetOutput()
        if output:
            bounds = output.GetBounds()
            width = max(bounds[1] - bounds[0], bounds[3] - bounds[2]) * 1.2
            if width > 0:
                camera.SetParallelScale(width / 2)
        
        # 设置相机位置
        camera.SetPosition(0, 0, 1000)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 1, 0)
        
        print("2D横截面视图创建完成")
        
        return renderer
        
    except Exception as e:
        print(f"创建2D横截面视图失败: {e}")
        return None

def setup_render_window(volume, cut_actor, fill_actor, cross_section_renderer=None):
    """设置渲染窗口"""
    try:
        import vtk
        
        # 创建主渲染器（3D视图）
        renderer_3d = vtk.vtkRenderer()
        renderer_3d.AddVolume(volume)
        
        # 添加横截面Actor
        if cut_actor:
            renderer_3d.AddActor(cut_actor)
        
        if fill_actor:
            renderer_3d.AddActor(fill_actor)
        
        renderer_3d.SetBackground(0.1, 0.1, 0.2)
        
        # 添加光源
        light = vtk.vtkLight()
        light.SetPosition(1, 1, 1)
        light.SetFocalPoint(0, 0, 0)
        light.SetColor(1, 1, 1)
        light.SetIntensity(1.0)
        renderer_3d.AddLight(light)
        
        # 创建渲染窗口
        render_window = vtk.vtkRenderWindow()
        
        # 设置视口布局
        if cross_section_renderer:
            # 左侧：3D视图 (60%)
            # 右侧：2D横截面视图 (40%)
            renderer_3d.SetViewport(0.0, 0.0, 0.6, 1.0)
            cross_section_renderer.SetViewport(0.6, 0.0, 1.0, 1.0)
            
            render_window.AddRenderer(renderer_3d)
            render_window.AddRenderer(cross_section_renderer)
        else:
            # 全屏3D视图
            renderer_3d.SetViewport(0.0, 0.0, 1.0, 1.0)
            render_window.AddRenderer(renderer_3d)
        
        render_window.SetSize(1400, 800)
        render_window.SetWindowName("DICOM序列3D体积渲染器 - 带横截面")
        
        # 创建交互器
        render_window_interactor = vtk.vtkRenderWindowInteractor()
        render_window_interactor.SetRenderWindow(render_window)
        
        # 添加交互样式
        interactor_style = vtk.vtkInteractorStyleTrackballCamera()
        render_window_interactor.SetInteractorStyle(interactor_style)
        
        # 添加坐标轴
        axes = vtk.vtkAxesActor()
        axes_widget = vtk.vtkOrientationMarkerWidget()
        axes_widget.SetOrientationMarker(axes)
        axes_widget.SetInteractor(render_window_interactor)
        axes_widget.SetEnabled(1)
        axes_widget.InteractiveOn()
        
        # 重置相机
        renderer_3d.ResetCamera()
        
        return render_window, render_window_interactor
        
    except Exception as e:
        print(f"设置渲染窗口失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def view_dicom_with_cross_section(dicom_dir, cut_percent=50):
    """查看DICOM序列的3D体积和横截面"""
    try:
        import vtk
        
        # 确保VTK已安装
        if not install_required_packages():
            print("无法安装VTK，请手动安装: pip install vtk")
            return False
        
        # 加载DICOM序列
        result = load_dicom_sequence(dicom_dir)
        if not result:
            return False
        
        image_data, reader = result
        
        # 创建带横截面的3D体积渲染
        volume_result = create_volume_with_cross_section(image_data, cut_percent)
        if not volume_result:
            return False
        
        volume, cut_actor, fill_actor, cut_z = volume_result
        
        # 创建2D横截面视图
        cross_section_renderer = create_cross_section_view(image_data, cut_z)
        
        # 设置渲染窗口
        window_result = setup_render_window(volume, cut_actor, fill_actor, cross_section_renderer)
        if not window_result:
            return False
        
        render_window, render_window_interactor = window_result
        
        # 显示窗口
        print("\n正在打开3D体积渲染窗口（带横截面）...")
        print("窗口布局:")
        print("  左侧 (60%): 3D体积渲染 + 横截面线")
        print("  右侧 (40%): 2D横截面视图")
        print(f"  横截面位置: 高度{cut_percent}% (Z = {cut_z:.1f} mm)")
        print("\n交互提示:")
        print("  鼠标左键拖拽: 旋转3D视图")
        print("  鼠标右键拖拽: 平移视图")
        print("  滚轮: 缩放")
        print("  按'R'键: 重置视图")
        print("  按'Q'键或关闭窗口: 退出")
        
        # 开始交互
        render_window.Render()
        render_window_interactor.Start()
        
        return True
        
    except Exception as e:
        print(f"查看DICOM序列失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=== DICOM序列3D体积渲染器 - 带横截面功能 ===")
    print("功能: 加载DICOM序列，显示3D体积，并在50%高度进行水平横切")
    
    # 使用用户提供的DICOM目录
    dicom_dir = r"D:\transesophageal-echo-simulator\patients\SE7"
    
    print(f"使用指定的DICOM目录: {repr(dicom_dir)}")
    
    # 检查目录是否存在
    if not os.path.exists(dicom_dir):
        print(f"错误: DICOM目录不存在 {repr(dicom_dir)}")
        return
    
    # 检查目录中是否有DICOM文件
    dicom_files = [f for f in os.listdir(dicom_dir) if f.lower().endswith(('.dcm', '.dicom')) or 'IM' in f]
    if not dicom_files:
        print(f"错误: 目录中没有DICOM文件")
        return
    
    print(f"找到 {len(dicom_files)} 个DICOM文件")
    
    print(f"\n正在处理DICOM目录: {repr(dicom_dir)}")
    
    # 确保VTK已安装
    if not install_required_packages():
        print("无法安装VTK，请手动安装: pip install vtk")
        return
    
    # 查看DICOM序列的3D体积和横截面
    print("\n=== 开始3D体积渲染（带50%高度横截面） ===")
    if view_dicom_with_cross_section(dicom_dir, cut_percent=50):
        print("\nDICOM序列3D显示完成（带横截面）")
    else:
        print("\nDICOM序列3D显示失败")

if __name__ == "__main__":
    main()
