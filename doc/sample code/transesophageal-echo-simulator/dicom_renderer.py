#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DICOM 3D渲染模块
包含3D体积渲染、窗口设置等功能
"""

import math
from dicom_utils import ProgressObserver

def calculate_plane_normal(rao_angle=30, lao_angle=20):
    """计算RAO和LAO角度对应的平面法线向量"""
    # 将角度转换为弧度
    rao_rad = math.radians(rao_angle)
    lao_rad = math.radians(lao_angle)
    
    # 在心脏影像学中：
    # RAO (右前斜位): 从右前方向观察
    # LAO (左前斜位): 从左前方向观察
    
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

def create_volume_renderer(image_data):
    """创建3D体积渲染器"""
    try:
        import vtk
        
        print("\n创建3D体积渲染器...")
        
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
        
        print("3D体积渲染器创建完成")
        
        return volume, volume_mapper, volume_property
        
    except Exception as e:
        print(f"创建3D体积渲染器失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def setup_render_window(volume, slice_renderer=None):
    """设置渲染窗口"""
    try:
        import vtk
        
        # 创建主渲染器（3D视图）
        renderer_3d = vtk.vtkRenderer()
        renderer_3d.AddVolume(volume)
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
        if slice_renderer:
            # 左侧：3D视图 (60%)
            # 右侧：2D切片视图 (40%)
            renderer_3d.SetViewport(0.0, 0.0, 0.6, 1.0)
            slice_renderer.SetViewport(0.6, 0.0, 1.0, 1.0)
            
            render_window.AddRenderer(renderer_3d)
            render_window.AddRenderer(slice_renderer)
        else:
            # 全屏3D视图
            renderer_3d.SetViewport(0.0, 0.0, 1.0, 1.0)
            render_window.AddRenderer(renderer_3d)
        
        render_window.SetSize(1400, 800)
        render_window.SetWindowName("DICOM序列3D体积渲染器")
        
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

def create_slice_renderer(image_data, nx, ny, nz, title="切片"):
    """创建2D切片渲染器"""
    try:
        import vtk
        import math
        
        print(f"\n创建{title}视图...")
        print(f"平面法线: ({nx:.3f}, {ny:.3f}, {nz:.3f})")
        
        # 获取体积的边界框和中心点
        bounds = image_data.GetBounds()
        center = [
            (bounds[0] + bounds[1]) / 2,
            (bounds[2] + bounds[3]) / 2,
            (bounds[4] + bounds[5]) / 2
        ]
        
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
            ref_vector = (1, 0, 0)
        else:
            ref_vector = (0, 1, 0)
        
        # 计算X轴（与法线向量正交）
        # 叉积计算
        ref_x, ref_y, ref_z = ref_vector
        x_axis = (
            ref_y * nz - ref_z * ny,
            ref_z * nx - ref_x * nz,
            ref_x * ny - ref_y * nx
        )
        
        # 计算向量长度
        x_length = math.sqrt(x_axis[0]**2 + x_axis[1]**2 + x_axis[2]**2)
        
        if x_length < 0.001:
            # 如果叉积太小，尝试另一个参考向量
            ref_vector = (0, 0, 1)
            ref_x, ref_y, ref_z = ref_vector
            x_axis = (
                ref_y * nz - ref_z * ny,
                ref_z * nx - ref_x * nz,
                ref_x * ny - ref_y * nx
            )
            x_length = math.sqrt(x_axis[0]**2 + x_axis[1]**2 + x_axis[2]**2)
        
        # 归一化X轴
        if x_length > 0:
            x_axis = (x_axis[0]/x_length, x_axis[1]/x_length, x_axis[2]/x_length)
        
        # 计算Y轴
        y_axis = (
            ny * x_axis[2] - nz * x_axis[1],
            nz * x_axis[0] - nx * x_axis[2],
            nx * x_axis[1] - ny * x_axis[0]
        )
        
        y_length = math.sqrt(y_axis[0]**2 + y_axis[1]**2 + y_axis[2]**2)
        if y_length > 0:
            y_axis = (y_axis[0]/y_length, y_axis[1]/y_length, y_axis[2]/y_length)
        
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
        text_actor.SetInput(f"{title}\n法线: ({nx:.2f}, {ny:.2f}, {nz:.2f})")
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
        
        print(f"{title}视图创建完成")
        
        return renderer
        
    except Exception as e:
        print(f"创建{title}视图失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def add_slider_widgets(render_window_interactor, initial_rao_angle=30, initial_lao_angle=20):
    """添加RAO和LAO角度滑块控件"""
    try:
        import vtk
        
        print("\n添加角度滑块控件...")
        
        # 创建RAO角度滑块（RAO90-LAO90）
        rao_slider = vtk.vtkSliderWidget()
        rao_slider_rep = vtk.vtkSliderRepresentation2D()
        
        # 设置RAO滑块属性
        rao_slider_rep.SetMinimumValue(-90)  # RAO90-LAO90范围
        rao_slider_rep.SetMaximumValue(90)
        rao_slider_rep.SetValue(initial_rao_angle)
        rao_slider_rep.SetTitleText("RAO90-LAO90")
        
        # 设置RAO滑块位置（控制面板左侧）
        # 控制面板在顶部10%区域，滑块放在控制面板的中部
        rao_slider_rep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
        rao_slider_rep.GetPoint1Coordinate().SetValue(0.05, 0.95)  # Y坐标在0.9-1.0范围内
        rao_slider_rep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
        rao_slider_rep.GetPoint2Coordinate().SetValue(0.25, 0.95)
        
        # 设置RAO滑块样式
        rao_slider_rep.SetSliderLength(0.02)
        rao_slider_rep.SetSliderWidth(0.03)
        rao_slider_rep.SetEndCapLength(0.01)
        rao_slider_rep.SetEndCapWidth(0.03)
        rao_slider_rep.SetTubeWidth(0.005)
        rao_slider_rep.SetLabelFormat("%.0f°")
        rao_slider_rep.GetTitleProperty().SetColor(1, 1, 1)
        rao_slider_rep.GetLabelProperty().SetColor(1, 1, 1)
        rao_slider_rep.GetSliderProperty().SetColor(0.8, 0.3, 0.3)  # 红色
        rao_slider_rep.GetTubeProperty().SetColor(0.5, 0.5, 0.5)
        rao_slider_rep.GetCapProperty().SetColor(0.7, 0.7, 0.7)
        
        rao_slider.SetInteractor(render_window_interactor)
        rao_slider.SetRepresentation(rao_slider_rep)
        rao_slider.SetAnimationModeToAnimate()
        rao_slider.EnabledOn()
        
        # 创建LAO角度滑块（CRA90-CAU90）
        lao_slider = vtk.vtkSliderWidget()
        lao_slider_rep = vtk.vtkSliderRepresentation2D()
        
        # 设置LAO滑块属性
        lao_slider_rep.SetMinimumValue(-90)  # CRA90-CAU90范围
        lao_slider_rep.SetMaximumValue(90)
        lao_slider_rep.SetValue(initial_lao_angle)
        lao_slider_rep.SetTitleText("CRA90-CAU90")
        
        # 设置LAO滑块位置（控制面板左侧，在RAO滑块下方）
        lao_slider_rep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
        lao_slider_rep.GetPoint1Coordinate().SetValue(0.05, 0.90)  # Y坐标在0.9-1.0范围内
        lao_slider_rep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
        lao_slider_rep.GetPoint2Coordinate().SetValue(0.25, 0.90)
        
        # 设置LAO滑块样式
        lao_slider_rep.SetSliderLength(0.02)
        lao_slider_rep.SetSliderWidth(0.03)
        lao_slider_rep.SetEndCapLength(0.01)
        lao_slider_rep.SetEndCapWidth(0.03)
        lao_slider_rep.SetTubeWidth(0.005)
        lao_slider_rep.SetLabelFormat("%.0f°")
        lao_slider_rep.GetTitleProperty().SetColor(1, 1, 1)
        lao_slider_rep.GetLabelProperty().SetColor(1, 1, 1)
        lao_slider_rep.GetSliderProperty().SetColor(0.3, 0.8, 0.3)  # 绿色
        lao_slider_rep.GetTubeProperty().SetColor(0.5, 0.5, 0.5)
        lao_slider_rep.GetCapProperty().SetColor(0.7, 0.7, 0.7)
        
        lao_slider.SetInteractor(render_window_interactor)
        lao_slider.SetRepresentation(lao_slider_rep)
        lao_slider.SetAnimationModeToAnimate()
        lao_slider.EnabledOn()
        
        print("角度滑块控件添加完成")
        print("  RAO90-LAO90滑块: -90° 到 90° (红色)")
        print("  CRA90-CAU90滑块: -90° 到 90° (绿色)")
        print("  滑块位置: 窗口顶部控制面板区域")
        
        return rao_slider, lao_slider
        
    except Exception as e:
        print(f"添加滑块控件失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def setup_render_window_with_sliders(volume, slice_renderer=None, initial_rao_angle=30, initial_lao_angle=20):
    """设置带滑块的渲染窗口"""
    try:
        import vtk
        
        # 创建控制面板渲染器（用于显示滑块）
        control_renderer = vtk.vtkRenderer()
        control_renderer.SetBackground(0.3, 0.3, 0.4)
        control_renderer.SetViewport(0.0, 0.9, 1.0, 1.0)  # 顶部10%区域
        
        # 创建主渲染器（3D视图）
        renderer_3d = vtk.vtkRenderer()
        renderer_3d.AddVolume(volume)
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
        if slice_renderer:
            # 顶部：控制面板 (10%)
            # 左侧：3D视图 (60% of 90% = 54% of total)
            # 右侧：2D切片视图 (40% of 90% = 36% of total)
            control_renderer.SetViewport(0.0, 0.9, 1.0, 1.0)
            renderer_3d.SetViewport(0.0, 0.0, 0.6, 0.9)
            slice_renderer.SetViewport(0.6, 0.0, 1.0, 0.9)
            
            render_window.AddRenderer(control_renderer)
            render_window.AddRenderer(renderer_3d)
            render_window.AddRenderer(slice_renderer)
        else:
            # 顶部：控制面板 (10%)
            # 底部：全屏3D视图 (90%)
            control_renderer.SetViewport(0.0, 0.9, 1.0, 1.0)
            renderer_3d.SetViewport(0.0, 0.0, 1.0, 0.9)
            
            render_window.AddRenderer(control_renderer)
            render_window.AddRenderer(renderer_3d)
        
        render_window.SetSize(1400, 800)
        render_window.SetWindowName("DICOM序列3D体积渲染器 - 带角度滑块")
        
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
        
        # 添加滑块控件
        rao_slider, lao_slider = add_slider_widgets(
            render_window_interactor, 
            initial_rao_angle, 
            initial_lao_angle
        )
        
        # 在控制面板中添加文本说明
        text_actor = vtk.vtkTextActor()
        text_actor.SetInput("角度控制滑块: 拖动滑块调整RAO和LAO角度")
        text_actor.GetTextProperty().SetFontSize(16)
        text_actor.GetTextProperty().SetColor(1, 1, 1)
        text_actor.GetTextProperty().SetBackgroundColor(0.2, 0.2, 0.3)
        text_actor.GetTextProperty().SetBackgroundOpacity(0.7)
        text_actor.SetPosition(20, 20)
        control_renderer.AddActor2D(text_actor)
        
        # 重置相机
        renderer_3d.ResetCamera()
        
        return render_window, render_window_interactor, rao_slider, lao_slider
        
    except Exception as e:
        print(f"设置带滑块的渲染窗口失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None
