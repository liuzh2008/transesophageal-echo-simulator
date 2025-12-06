#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DICOM序列3D体积渲染器 - RAO+LAO角度切割（重构版）
模块化设计：安装包检测、目录检测、3D渲染、截面分开
"""

import os
import sys

# 导入模块
from dicom_utils import install_required_packages, load_dicom_sequence
from dicom_renderer import create_volume_renderer, setup_render_window, create_slice_renderer, setup_render_window_with_sliders, calculate_plane_normal
from dicom_cutter import create_rao_lao_cut

def view_dicom_with_rao_lao_cut(dicom_dir, rao_angle=30, lao_angle=20):
    """查看DICOM序列的3D体积和RAO+LAO角度切割"""
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
        
        # 创建3D体积渲染器
        volume_result = create_volume_renderer(image_data)
        if not volume_result:
            return False
        
        volume, volume_mapper, volume_property = volume_result
        
        # 创建RAO+LAO角度切割
        cut_result = create_rao_lao_cut(image_data, rao_angle, lao_angle)
        if not cut_result:
            return False
        
        cut_actor, fill_actor, normal_vector = cut_result
        nx, ny, nz = normal_vector
        
        # 创建RAO+LAO角度切片视图
        slice_renderer = create_slice_renderer(
            image_data, nx, ny, nz, 
            title=f"RAO {rao_angle}°+LAO {lao_angle}°角度切片"
        )
        
        # 设置渲染窗口
        window_result = setup_render_window(volume, slice_renderer)
        if not window_result:
            return False
        
        render_window, render_window_interactor = window_result
        
        # 添加切割Actor到3D渲染器
        renderer_3d = render_window.GetRenderers().GetFirstRenderer()
        if cut_actor:
            renderer_3d.AddActor(cut_actor)
        if fill_actor:
            renderer_3d.AddActor(fill_actor)
        
        # 显示窗口
        print("\n正在打开3D体积渲染窗口（RAO+LAO角度切割）...")
        print("窗口布局:")
        print("  左侧 (60%): 3D体积渲染 + RAO+LAO角度切割线")
        print("  右侧 (40%): RAO+LAO角度切片视图")
        print(f"  切割角度: RAO {rao_angle}° + LAO {lao_angle}°")
        print(f"  平面法线: ({nx:.3f}, {ny:.3f}, {nz:.3f})")
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

def view_dicom_with_interactive_sliders(dicom_dir, initial_rao_angle=30, initial_lao_angle=20):
    """查看DICOM序列的3D体积，使用滑块交互式调整RAO和LAO角度"""
    try:
        import vtk
        import math
        
        # 确保VTK已安装
        if not install_required_packages():
            print("无法安装VTK，请手动安装: pip install vtk")
            return False
        
        # 加载DICOM序列
        result = load_dicom_sequence(dicom_dir)
        if not result:
            return False
        
        image_data, reader = result
        
        # 创建3D体积渲染器
        volume_result = create_volume_renderer(image_data)
        if not volume_result:
            return False
        
        volume, volume_mapper, volume_property = volume_result
        
        # 创建初始RAO+LAO角度切割
        cut_result = create_rao_lao_cut(image_data, initial_rao_angle, initial_lao_angle)
        if not cut_result:
            return False
        
        cut_actor, fill_actor, normal_vector = cut_result
        nx, ny, nz = normal_vector
        
        # 创建初始RAO+LAO角度切片视图
        slice_renderer = create_slice_renderer(
            image_data, nx, ny, nz, 
            title=f"RAO {initial_rao_angle}°+LAO {initial_lao_angle}°角度切片"
        )
        
        # 设置带滑块的渲染窗口
        window_result = setup_render_window_with_sliders(
            volume, slice_renderer, initial_rao_angle, initial_lao_angle
        )
        if not window_result:
            return False
        
        render_window, render_window_interactor, rao_slider, lao_slider = window_result
        
        # 添加切割Actor到3D渲染器
        renderer_3d = render_window.GetRenderers().GetFirstRenderer()
        if cut_actor:
            renderer_3d.AddActor(cut_actor)
        if fill_actor:
            renderer_3d.AddActor(fill_actor)
        
        # 存储需要更新的组件
        class SliderCallbackData:
            def __init__(self):
                self.image_data = image_data
                self.renderer_3d = renderer_3d
                self.cut_actor = cut_actor
                self.fill_actor = fill_actor
                self.slice_renderer = slice_renderer
                self.render_window = render_window
                self.rao_slider = rao_slider
                self.lao_slider = lao_slider
                self.text_actor = None
        
        callback_data = SliderCallbackData()
        
        # 在切片渲染器中查找文本Actor
        slice_renderer_collection = slice_renderer.GetActors2D()
        slice_renderer_collection.InitTraversal()
        for i in range(slice_renderer_collection.GetNumberOfItems()):
            actor = slice_renderer_collection.GetNextItem()
            if isinstance(actor, vtk.vtkTextActor):
                callback_data.text_actor = actor
                break
        
        def update_cut_plane():
            """更新切割平面和切片视图"""
            try:
                # 获取当前滑块值
                rao_angle = rao_slider.GetRepresentation().GetValue()
                lao_angle = lao_slider.GetRepresentation().GetValue()
                
                print(f"\n更新切割平面: RAO {rao_angle:.1f}°, LAO {lao_angle:.1f}°")
                
                # 计算新的平面法线
                nx, ny, nz = calculate_plane_normal(rao_angle, lao_angle)
                
                # 移除旧的切割Actor
                if callback_data.cut_actor:
                    callback_data.renderer_3d.RemoveActor(callback_data.cut_actor)
                if callback_data.fill_actor:
                    callback_data.renderer_3d.RemoveActor(callback_data.fill_actor)
                
                # 创建新的切割
                new_cut_result = create_rao_lao_cut(image_data, rao_angle, lao_angle)
                if new_cut_result:
                    new_cut_actor, new_fill_actor, _ = new_cut_result
                    
                    # 更新存储的Actor
                    callback_data.cut_actor = new_cut_actor
                    callback_data.fill_actor = new_fill_actor
                    
                    # 添加新的切割Actor
                    callback_data.renderer_3d.AddActor(new_cut_actor)
                    if new_fill_actor:
                        callback_data.renderer_3d.AddActor(new_fill_actor)
                
                # 更新切片视图
                if callback_data.slice_renderer:
                    # 清除旧的2D Actor
                    actors = callback_data.slice_renderer.GetActors2D()
                    actors.InitTraversal()
                    actors_to_remove = []
                    for i in range(actors.GetNumberOfItems()):
                        actor = actors.GetNextItem()
                        if not isinstance(actor, vtk.vtkTextActor):
                            actors_to_remove.append(actor)
                    
                    for actor in actors_to_remove:
                        callback_data.slice_renderer.RemoveActor2D(actor)
                    
                    # 创建新的切片
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
                    
                    # 设置切片方向
                    if abs(nx) < 0.5:
                        ref_vector = (1, 0, 0)
                    else:
                        ref_vector = (0, 1, 0)
                    
                    ref_x, ref_y, ref_z = ref_vector
                    x_axis = (
                        ref_y * nz - ref_z * ny,
                        ref_z * nx - ref_x * nz,
                        ref_x * ny - ref_y * nx
                    )
                    
                    x_length = math.sqrt(x_axis[0]**2 + x_axis[1]**2 + x_axis[2]**2)
                    if x_length < 0.001:
                        ref_vector = (0, 0, 1)
                        ref_x, ref_y, ref_z = ref_vector
                        x_axis = (
                            ref_y * nz - ref_z * ny,
                            ref_z * nx - ref_x * nz,
                            ref_x * ny - ref_y * nx
                        )
                        x_length = math.sqrt(x_axis[0]**2 + x_axis[1]**2 + x_axis[2]**2)
                    
                    if x_length > 0:
                        x_axis = (x_axis[0]/x_length, x_axis[1]/x_length, x_axis[2]/x_length)
                    
                    y_axis = (
                        ny * x_axis[2] - nz * x_axis[1],
                        nz * x_axis[0] - nx * x_axis[2],
                        nx * x_axis[1] - ny * x_axis[0]
                    )
                    
                    y_length = math.sqrt(y_axis[0]**2 + y_axis[1]**2 + y_axis[2]**2)
                    if y_length > 0:
                        y_axis = (y_axis[0]/y_length, y_axis[1]/y_length, y_axis[2]/y_length)
                    
                    reslice.SetResliceAxesDirectionCosines(
                        x_axis[0], x_axis[1], x_axis[2],
                        y_axis[0], y_axis[1], y_axis[2],
                        nx, ny, nz
                    )
                    
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
                    callback_data.slice_renderer.AddActor2D(image_actor)
                
                # 更新文本标注
                if callback_data.text_actor:
                    callback_data.text_actor.SetInput(
                        f"RAO {rao_angle:.0f}°+LAO {lao_angle:.0f}°角度切片\n"
                        f"法线: ({nx:.2f}, {ny:.2f}, {nz:.2f})"
                    )
                
                # 重新渲染
                callback_data.render_window.Render()
                
            except Exception as e:
                print(f"更新切割平面失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 设置滑块回调函数
        def rao_slider_callback(obj, event):
            update_cut_plane()
        
        def lao_slider_callback(obj, event):
            update_cut_plane()
        
        rao_slider.AddObserver("InteractionEvent", rao_slider_callback)
        lao_slider.AddObserver("InteractionEvent", lao_slider_callback)
        
        # 显示窗口
        print("\n正在打开3D体积渲染窗口（带交互式角度滑块）...")
        print("窗口布局:")
        print("  左侧 (60%): 3D体积渲染 + RAO+LAO角度切割线")
        print("  右侧 (40%): RAO+LAO角度切片视图")
        print("  顶部左侧: RAO角度滑块 (-90° 到 90°)")
        print("  顶部左侧下方: LAO角度滑块 (-90° 到 90°)")
        print(f"  初始角度: RAO {initial_rao_angle}° + LAO {initial_lao_angle}°")
        print(f"  初始平面法线: ({nx:.3f}, {ny:.3f}, {nz:.3f})")
        print("\n交互提示:")
        print("  鼠标左键拖拽: 旋转3D视图")
        print("  鼠标右键拖拽: 平移视图")
        print("  滚轮: 缩放")
        print("  拖动滑块: 实时调整RAO和LAO角度")
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
    print("=== DICOM序列3D体积渲染器 - RAO+LAO角度切割（重构版） ===")
    print("功能: 加载DICOM序列，显示3D体积，并进行RAO+LAO角度切割")
    print("模块化设计: 安装包检测、目录检测、3D渲染、截面分开")
    
    # 使用用户提供的DICOM目录
    dicom_dir = r"D:\patients\SE7"
    
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
    
    # 询问用户选择哪种模式
    print("\n请选择显示模式:")
    print("  1. 固定角度模式 (RAO 30° + LAO 20°)")
    print("  2. 交互式滑块模式 (可调整RAO和LAO角度)")
    
    try:
        choice = input("请输入选择 (1 或 2, 默认 2): ").strip()
        if choice == "" or choice == "2":
            print("\n=== 开始3D体积渲染（交互式滑块模式） ===")
            print("功能: 使用滑块实时调整RAO和LAO角度")
            print("滑块1: RAO90-LAO90 (-90° 到 90°)")
            print("滑块2: CRA90-CAU90 (-90° 到 90°)")
            
            if view_dicom_with_interactive_sliders(dicom_dir, initial_rao_angle=30, initial_lao_angle=20):
                print("\nDICOM序列3D显示完成（交互式滑块模式）")
            else:
                print("\nDICOM序列3D显示失败")
        else:
            print("\n=== 开始3D体积渲染（固定角度模式） ===")
            if view_dicom_with_rao_lao_cut(dicom_dir, rao_angle=30, lao_angle=20):
                print("\nDICOM序列3D显示完成（固定角度模式）")
            else:
                print("\nDICOM序列3D显示失败")
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n选择模式时发生错误: {e}")
        print("使用默认的交互式滑块模式...")
        if view_dicom_with_interactive_sliders(dicom_dir, initial_rao_angle=30, initial_lao_angle=20):
            print("\nDICOM序列3D显示完成（交互式滑块模式）")
        else:
            print("\nDICOM序列3D显示失败")

if __name__ == "__main__":
    main()
