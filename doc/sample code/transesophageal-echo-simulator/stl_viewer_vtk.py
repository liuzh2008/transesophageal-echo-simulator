#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL文件查看器 - 使用VTK显示
支持大文件加载和进度显示
"""

import os
import sys
import time

def install_vtk():
    """自动安装VTK"""
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
    def __init__(self):
        self.progress = 0.0
        self.start_time = time.time()
        
    def __call__(self, obj, event):
        if event == "ProgressEvent":
            # 获取进度值
            try:
                self.progress = obj.GetProgress()
                elapsed = time.time() - self.start_time
                bar_length = 50
                filled_length = int(bar_length * self.progress)
                bar = '=' * filled_length + ' ' * (bar_length - filled_length)
                percent = self.progress * 100
                sys.stdout.write(f'\r[{bar}] {percent:.1f}% - 耗时: {elapsed:.1f}秒')
                sys.stdout.flush()
            except:
                pass

def load_stl_with_vtk(file_path):
    """使用VTK加载和显示STL文件"""
    try:
        import vtk
        from vtk.util.colors import tomato
        
        print(f"正在使用VTK加载文件: {repr(file_path)}")
        
        # 显示加载进度
        print("开始加载STL文件...")
        start_time = time.time()
        
        # 创建进度观察器
        progress_observer = ProgressObserver()
        
        # 创建STL读取器
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_path)
        
        # 添加进度观察器
        reader.AddObserver("ProgressEvent", progress_observer)
        
        # 更新读取器以触发进度事件
        reader.Update()
        
        load_time = time.time() - start_time
        print(f"\n文件加载完成，耗时: {load_time:.2f}秒")
        
        # 获取输出数据
        polydata = reader.GetOutput()
        
        if polydata.GetNumberOfPoints() == 0:
            print("错误: 无法加载STL文件或文件为空")
            return False
            
        print(f"成功加载STL文件:")
        print(f"  顶点数: {polydata.GetNumberOfPoints():,}")
        print(f"  多边形数: {polydata.GetNumberOfCells():,}")
        
        # 计算边界框
        bounds = polydata.GetBounds()
        print(f"  边界框: X[{bounds[0]:.1f}, {bounds[1]:.1f}], "
              f"Y[{bounds[2]:.1f}, {bounds[3]:.1f}], "
              f"Z[{bounds[4]:.1f}, {bounds[5]:.1f}]")
        
        # 计算体积和表面积
        mass_properties = vtk.vtkMassProperties()
        mass_properties.SetInputData(polydata)
        
        try:
            volume = mass_properties.GetVolume()
            surface_area = mass_properties.GetSurfaceArea()
            print(f"  体积: {volume:.2f} 立方单位")
            print(f"  表面积: {surface_area:.2f} 平方单位")
        except:
            print("  注意: 无法计算体积和表面积（网格可能不是封闭的）")
        
        # 创建Mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        
        # 创建Actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.2, 0.4, 0.8)  # 蓝色，在白色背景下更清晰
        
        # 设置材质属性 - 提高亮度
        actor.GetProperty().SetAmbient(0.5)      # 增加环境光系数
        actor.GetProperty().SetDiffuse(0.9)      # 增加漫反射系数
        actor.GetProperty().SetSpecular(0.6)     # 增加镜面反射系数
        actor.GetProperty().SetSpecularPower(40) # 提高光泽度
        
        # 边缘设置 - 可选显示，减少干扰
        actor.GetProperty().SetEdgeColor(0.1, 0.1, 0.3)  # 深蓝色边缘
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetLineWidth(0.5)  # 进一步减小边缘线宽
        actor.GetProperty().SetOpacity(1.0)    # 完全不透明
        
        # 创建渲染器
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(1.0, 1.0, 1.0)  # 白色背景
        
        # 添加更强的光源 - 提高亮度
        # 主光源（前方45度）- 增强
        light1 = vtk.vtkLight()
        light1.SetPosition(1, 1, 1)  # 右上前方
        light1.SetFocalPoint(0, 0, 0)
        light1.SetColor(1.0, 1.0, 1.0)  # 白色光
        light1.SetIntensity(1.2)  # 增加强度
        renderer.AddLight(light1)
        
        # 填充光源（左侧）- 增强
        light2 = vtk.vtkLight()
        light2.SetPosition(-1, 0.5, 0.5)  # 左前方
        light2.SetFocalPoint(0, 0, 0)
        light2.SetColor(1.0, 1.0, 1.0)  # 改为纯白色光
        light2.SetIntensity(0.8)  # 增加强度
        renderer.AddLight(light2)
        
        # 背光（后方）- 增强
        light3 = vtk.vtkLight()
        light3.SetPosition(0, -1, -0.5)  # 后下方
        light3.SetFocalPoint(0, 0, 0)
        light3.SetColor(1.0, 1.0, 1.0)  # 改为纯白色光
        light3.SetIntensity(0.6)  # 增加强度
        renderer.AddLight(light3)
        
        # 添加顶部光源 - 额外增强
        light4 = vtk.vtkLight()
        light4.SetPosition(0, 1, 0.5)  # 正上方
        light4.SetFocalPoint(0, 0, 0)
        light4.SetColor(1.0, 1.0, 1.0)  # 白色光
        light4.SetIntensity(0.7)
        renderer.AddLight(light4)
        
        # 启用阴影（可选）
        renderer.SetUseShadows(True)
        
        # 设置渲染器全局环境光 - 进一步提高整体亮度
        renderer.SetAmbient(0.4, 0.4, 0.4)
        
        # 创建渲染窗口
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.SetSize(1024, 768)
        render_window.SetWindowName("STL文件查看器 - VTK")
        
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
        
        # 显示3D网格
        print("\n正在打开3D显示窗口...")
        print("提示:")
        print("  鼠标左键拖拽: 旋转视图")
        print("  鼠标右键拖拽: 平移视图")
        print("  滚轮: 缩放")
        print("  按'R'键: 重置视图")
        print("  按'Q'键或关闭窗口: 退出")
        
        # 开始交互
        render_window.Render()
        render_window_interactor.Start()
        
        return True
        
    except ImportError:
        print("VTK未安装，请运行: pip install vtk")
        return False
    except Exception as e:
        print(f"VTK加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def find_stl_files(directory):
    """在目录中查找STL文件"""
    stl_files = []
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.lower().endswith('.stl'):
                stl_files.append(file)
    return stl_files

def main():
    """主函数"""
    # STL文件路径 - 使用重命名后的文件
    stl_file_path = r"D:\transesophageal-echo-simulator\patients\CHEN ZHI MING 3D-object.stl"
    
    # 检查文件是否存在
    if not os.path.exists(stl_file_path):
        print(f"错误: 文件不存在 {repr(stl_file_path)}")
        
        # 尝试查找实际文件
        patients_dir = os.path.dirname(stl_file_path)
        if os.path.exists(patients_dir):
            print(f"检查目录: {patients_dir}")
            files = find_stl_files(patients_dir)
            if files:
                print(f"找到STL文件: {files}")
                # 使用第一个找到的STL文件
                stl_file_path = os.path.join(patients_dir, files[0])
                print(f"将使用文件: {repr(stl_file_path)}")
            else:
                print("未找到任何STL文件")
                return
        else:
            print("patients目录不存在")
            return
    
    print(f"正在处理STL文件: {repr(stl_file_path)}")
    print(f"文件大小: {os.path.getsize(stl_file_path) / (1024*1024):.1f} MB")
    
    # 确保VTK已安装
    if not install_vtk():
        print("无法安装VTK，请手动安装: pip install vtk")
        return
    
    # 使用VTK显示
    print("\n=== 使用VTK显示STL文件 ===")
    if load_stl_with_vtk(stl_file_path):
        print("\nSTL文件显示完成")
    else:
        print("\nSTL文件显示失败")

if __name__ == "__main__":
    main()
