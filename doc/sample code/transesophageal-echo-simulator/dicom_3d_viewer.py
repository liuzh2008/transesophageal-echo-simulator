#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DICOM序列3D体积渲染器
支持加载DICOM序列并显示为3D体积
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
        
        # 检查目录中是否有DICOM文件（支持无扩展名或常见DICOM扩展名）
        dicom_files = []
        for f in os.listdir(dicom_dir):
            # 检查常见DICOM扩展名或无扩展名但看起来像DICOM文件
            if (f.lower().endswith(('.dcm', '.dicom')) or 
                f.startswith('IM') or  # 以IM开头的文件
                f.isdigit() or  # 纯数字文件名
                '.' not in f):  # 无扩展名文件
                dicom_files.append(f)
        
        if not dicom_files:
            print(f"错误: 目录中没有DICOM文件")
            # 显示目录内容以便调试
            print(f"目录内容 (前10个):")
            for f in os.listdir(dicom_dir)[:10]:
                print(f"  {f}")
            return None
        
        print(f"找到 {len(dicom_files)} 个可能的DICOM文件")
        print(f"前10个文件: {dicom_files[:10]}")
        
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

def create_volume_renderer(image_data):
    """创建3D体积渲染器"""
    try:
        import vtk
        
        print("\n创建3D体积渲染...")
        
        # 创建进度观察器
        progress_observer = ProgressObserver("创建体积渲染")
        
        # 创建体积映射器
        volume_mapper = vtk.vtkFixedPointVolumeRayCastMapper()
        volume_mapper.SetInputData(image_data)
        
        # 添加进度观察器
        volume_mapper.AddObserver("ProgressEvent", progress_observer)
        
        # 设置采样距离（影响渲染质量和速度）
        volume_mapper.SetSampleDistance(0.5)
        volume_mapper.SetAutoAdjustSampleDistances(1)
        
        # 创建体积属性
        volume_property = vtk.vtkVolumeProperty()
        volume_property.ShadeOn()  # 启用阴影
        volume_property.SetInterpolationTypeToLinear()  # 线性插值
        
        # 设置传输函数（颜色和透明度）
        color_transfer_function = vtk.vtkColorTransferFunction()
        opacity_transfer_function = vtk.vtkPiecewiseFunction()
        
        # 获取标量范围
        scalar_range = image_data.GetScalarRange()
        min_val, max_val = scalar_range
        
        # 医学影像典型的传输函数设置
        # 对于CT数据：空气~-1000，水~0，骨骼>400
        # 对于MRI数据：范围不同，这里使用通用设置
        
        # 设置颜色传输函数
        if max_val - min_val > 2000:  # 可能是CT数据
            # CT颜色映射
            color_transfer_function.AddRGBPoint(min_val, 0.0, 0.0, 0.0)  # 黑色
            color_transfer_function.AddRGBPoint(min_val + (max_val - min_val) * 0.3, 0.5, 0.5, 0.5)  # 灰色
            color_transfer_function.AddRGBPoint(min_val + (max_val - min_val) * 0.6, 1.0, 0.7, 0.5)  # 肉色
            color_transfer_function.AddRGBPoint(max_val, 1.0, 1.0, 0.9)  # 亮黄色
        else:  # 可能是MRI或其他数据
            # 通用颜色映射
            color_transfer_function.AddRGBPoint(min_val, 0.0, 0.0, 0.0)  # 黑色
            color_transfer_function.AddRGBPoint(min_val + (max_val - min_val) * 0.3, 0.0, 0.0, 1.0)  # 蓝色
            color_transfer_function.AddRGBPoint(min_val + (max_val - min_val) * 0.6, 0.0, 1.0, 0.0)  # 绿色
            color_transfer_function.AddRGBPoint(max_val, 1.0, 0.0, 0.0)  # 红色
        
        # 设置透明度传输函数
        opacity_transfer_function.AddPoint(min_val, 0.0)  # 完全透明
        opacity_transfer_function.AddPoint(min_val + (max_val - min_val) * 0.1, 0.0)
        opacity_transfer_function.AddPoint(min_val + (max_val - min_val) * 0.3, 0.1)
        opacity_transfer_function.AddPoint(min_val + (max_val - min_val) * 0.6, 0.3)
        opacity_transfer_function.AddPoint(max_val, 0.6)  # 半透明
        
        volume_property.SetColor(color_transfer_function)
        volume_property.SetScalarOpacity(opacity_transfer_function)
        
        # 设置梯度不透明度（增强边缘）
        gradient_opacity = vtk.vtkPiecewiseFunction()
        gradient_opacity.AddPoint(0.0, 0.0)
        gradient_opacity.AddPoint(10.0, 0.1)
        gradient_opacity.AddPoint(50.0, 0.5)
        gradient_opacity.AddPoint(100.0, 1.0)
        volume_property.SetGradientOpacity(gradient_opacity)
        
        # 创建体积
        volume = vtk.vtkVolume()
        volume.SetMapper(volume_mapper)
        volume.SetProperty(volume_property)
        
        print("体积渲染创建完成")
        
        return volume, volume_mapper, volume_property
        
    except Exception as e:
        print(f"创建体积渲染失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_slice_viewers(image_data):
    """创建三个正交切片视图（轴向、冠状、矢状）"""
    try:
        import vtk
        
        print("\n创建切片视图...")
        
        # 获取图像维度
        dimensions = image_data.GetDimensions()
        center = [
            dimensions[0] // 2,
            dimensions[1] // 2,
            dimensions[2] // 2
        ]
        
        # 创建三个切片提取器
        axial_reslice = vtk.vtkImageReslice()
        axial_reslice.SetInputData(image_data)
        axial_reslice.SetOutputDimensionality(2)
        axial_reslice.SetResliceAxesDirectionCosines([1, 0, 0, 0, 1, 0, 0, 0, 1])
        axial_reslice.SetResliceAxesOrigin([0, 0, center[2]])
        
        coronal_reslice = vtk.vtkImageReslice()
        coronal_reslice.SetInputData(image_data)
        coronal_reslice.SetOutputDimensionality(2)
        coronal_reslice.SetResliceAxesDirectionCosines([1, 0, 0, 0, 0, 1, 0, -1, 0])
        coronal_reslice.SetResliceAxesOrigin([0, center[1], 0])
        
        sagittal_reslice = vtk.vtkImageReslice()
        sagittal_reslice.SetInputData(image_data)
        sagittal_reslice.SetOutputDimensionality(2)
        sagittal_reslice.SetResliceAxesDirectionCosines([0, 0, -1, 0, 1, 0, 1, 0, 0])
        sagittal_reslice.SetResliceAxesOrigin([center[0], 0, 0])
        
        # 创建切片映射器
        axial_mapper = vtk.vtkImageMapper()
        axial_mapper.SetInputConnection(axial_reslice.GetOutputPort())
        axial_mapper.SetColorWindow(255)
        axial_mapper.SetColorLevel(128)
        
        coronal_mapper = vtk.vtkImageMapper()
        coronal_mapper.SetInputConnection(coronal_reslice.GetOutputPort())
        coronal_mapper.SetColorWindow(255)
        coronal_mapper.SetColorLevel(128)
        
        sagittal_mapper = vtk.vtkImageMapper()
        sagittal_mapper.SetInputConnection(sagittal_reslice.GetOutputPort())
        sagittal_mapper.SetColorWindow(255)
        sagittal_mapper.SetColorLevel(128)
        
        # 创建切片Actor
        axial_actor = vtk.vtkActor2D()
        axial_actor.SetMapper(axial_mapper)
        
        coronal_actor = vtk.vtkActor2D()
        coronal_actor.SetMapper(coronal_mapper)
        
        sagittal_actor = vtk.vtkActor2D()
        sagittal_actor.SetMapper(sagittal_mapper)
        
        print(f"切片视图创建完成 (轴向: 切片 {center[2]}, 冠状: 切片 {center[1]}, 矢状: 切片 {center[0]})")
        
        return {
            'axial': (axial_actor, axial_reslice, center[2]),
            'coronal': (coronal_actor, coronal_reslice, center[1]),
            'sagittal': (sagittal_actor, sagittal_reslice, center[0])
        }
        
    except Exception as e:
        print(f"创建切片视图失败: {e}")
        return None

def setup_render_window(volume, slice_actors=None):
    """设置渲染窗口"""
    try:
        import vtk
        
        # 创建渲染器
        renderer = vtk.vtkRenderer()
        renderer.AddVolume(volume)
        renderer.SetBackground(0.1, 0.1, 0.2)  # 深蓝色背景
        
        # 添加光源
        light = vtk.vtkLight()
        light.SetPosition(1, 1, 1)
        light.SetFocalPoint(0, 0, 0)
        light.SetColor(1, 1, 1)
        light.SetIntensity(1.0)
        renderer.AddLight(light)
        
        # 添加切片视图（如果提供）
        if slice_actors:
            # 设置切片视图的位置
            viewport_height = 0.25  # 每个切片视图占25%的高度
            
            slice_renderers = {}
            for i, (plane, (actor, reslice, slice_pos)) in enumerate(slice_actors.items()):
                slice_renderer = vtk.vtkRenderer()
                slice_renderer.AddActor2D(actor)
                slice_renderer.SetBackground(0.2, 0.2, 0.3)
                
                # 设置视口位置（顶部，从上到下）
                y_start = 1.0 - (i + 1) * viewport_height
                y_end = 1.0 - i * viewport_height
                slice_renderer.SetViewport(0.7, y_start, 1.0, y_end)
                
                # 添加文本标注
                text_actor = vtk.vtkTextActor()
                text_actor.SetInput(f"{plane} - 切片 {slice_pos}")
                text_actor.GetTextProperty().SetFontSize(14)
                text_actor.GetTextProperty().SetColor(1, 1, 1)
                text_actor.SetPosition(10, 10)
                slice_renderer.AddActor2D(text_actor)
                
                slice_renderers[plane] = slice_renderer
        
        # 创建渲染窗口
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        
        # 设置主渲染器的视口（左侧70%）
        renderer.SetViewport(0.0, 0.0, 0.7, 1.0)
        
        # 添加切片渲染器
        if slice_actors:
            for plane, slice_renderer in slice_renderers.items():
                render_window.AddRenderer(slice_renderer)
        
        render_window.SetSize(1400, 900)
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
        renderer.ResetCamera()
        
        return render_window, render_window_interactor
        
    except Exception as e:
        print(f"设置渲染窗口失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def view_dicom_sequence_3d(dicom_dir, show_slices=True):
    """查看DICOM序列的3D体积"""
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
        
        # 创建3D体积渲染
        volume_result = create_volume_renderer(image_data)
        if not volume_result:
            return False
        
        volume, volume_mapper, volume_property = volume_result
        
        # 创建切片视图（可选）
        slice_actors = None
        if show_slices:
            slice_actors = create_slice_viewers(image_data)
        
        # 设置渲染窗口
        window_result = setup_render_window(volume, slice_actors)
        if not window_result:
            return False
        
        render_window, render_window_interactor = window_result
        
        # 显示窗口
        print("\n正在打开3D体积渲染窗口...")
        print("窗口布局:")
        print("  左侧 (70%): 3D体积渲染")
        if show_slices:
            print("  右侧顶部 (25%): 轴向切片")
            print("  右侧中部 (25%): 冠状切片")
            print("  右侧底部 (25%): 矢状切片")
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

def find_dicom_directories(base_dir):
    """查找包含DICOM文件的目录"""
    dicom_dirs = []
    if os.path.exists(base_dir):
        for root, dirs, files in os.walk(base_dir):
            # 检查当前目录是否有DICOM文件
            dicom_files = [f for f in files if f.lower().endswith(('.dcm', '.dicom'))]
            if dicom_files:
                dicom_dirs.append(root)
                print(f"找到DICOM目录: {root} ({len(dicom_files)} 个文件)")
    
    return dicom_dirs

def main():
    """主函数"""
    print("=== DICOM序列3D体积渲染器 ===")
    print("功能: 加载DICOM序列并显示为3D体积")
    
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
        # 显示目录内容
        print(f"目录内容:")
        for f in os.listdir(dicom_dir)[:10]:  # 只显示前10个文件
            print(f"  {f}")
        return
    
    print(f"找到 {len(dicom_files)} 个DICOM文件")
    print(f"前5个文件: {dicom_files[:5]}")
    
    print(f"\n正在处理DICOM目录: {repr(dicom_dir)}")
    
    # 确保VTK已安装
    if not install_required_packages():
        print("无法安装VTK，请手动安装: pip install vtk")
        return
    
    # 查看DICOM序列的3D体积
    print("\n=== 开始3D体积渲染 ===")
    if view_dicom_sequence_3d(dicom_dir, show_slices=True):
        print("\nDICOM序列3D显示完成")
    else:
        print("\nDICOM序列3D显示失败")

if __name__ == "__main__":
    main()
