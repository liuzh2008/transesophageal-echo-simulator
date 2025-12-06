#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL文件查看器 - 使用VTK显示，带横截面功能
支持大文件加载、进度显示和横截面分析
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

def create_cross_section(polydata, cut_position_percent=50):
    """创建横截面"""
    try:
        import vtk
        
        # 获取模型的边界框
        bounds = polydata.GetBounds()
        z_min, z_max = bounds[4], bounds[5]
        
        # 计算切割位置（模型高度的50%）
        cut_z = z_min + (z_max - z_min) * (cut_position_percent / 100.0)
        
        print(f"\n创建横截面:")
        print(f"  模型Z范围: [{z_min:.1f}, {z_max:.1f}]")
        print(f"  切割位置 (高度{cut_position_percent}%): Z = {cut_z:.1f}")
        
        # 创建切割平面
        plane = vtk.vtkPlane()
        plane.SetOrigin(0, 0, cut_z)
        plane.SetNormal(0, 0, 1)  # 沿Z轴切割
        
        # 创建切割器
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputData(polydata)
        cutter.Update()
        
        # 获取切割结果
        cut_polydata = cutter.GetOutput()
        
        if cut_polydata.GetNumberOfPoints() == 0:
            print("  警告: 横截面为空，可能切割位置不在模型范围内")
            return None
        
        print(f"  横截面点数: {cut_polydata.GetNumberOfPoints():,}")
        print(f"  横截面线数: {cut_polydata.GetNumberOfLines():,}")
        
        return cut_polydata, cut_z
        
    except Exception as e:
        print(f"创建横截面失败: {e}")
        return None

def create_cross_section_renderer(cut_polydata, cut_z):
    """创建2D横截面渲染器（带填充）"""
    try:
        import vtk
        
        print(f"  正在创建2D横截面渲染器（带填充）...")
        
        # 创建2D渲染器
        renderer_2d = vtk.vtkRenderer()
        renderer_2d.SetBackground(1.0, 1.0, 1.0)  # 白色背景
        
        # 检查横截面数据
        if cut_polydata.GetNumberOfPoints() == 0:
            print("  警告: 横截面数据为空")
            return None
        
        print(f"  原始横截面数据: 点数={cut_polydata.GetNumberOfPoints()}, 线数={cut_polydata.GetNumberOfLines()}")
        
        # 创建填充的横截面（使用轮廓三角化）
        filled_polydata = None
        
        # 尝试使用vtkContourTriangulator填充轮廓
        try:
            if cut_polydata.GetNumberOfLines() > 0:
                print(f"  正在使用轮廓三角化填充横截面...")
                
                # 创建轮廓三角化器
                triangulator = vtk.vtkContourTriangulator()
                triangulator.SetInputData(cut_polydata)
                triangulator.Update()
                
                filled_polydata = triangulator.GetOutput()
                
                if filled_polydata.GetNumberOfPolys() > 0:
                    print(f"  轮廓三角化成功: 生成{filled_polydata.GetNumberOfPolys()}个多边形")
                else:
                    print(f"  轮廓三角化未生成多边形，使用原始数据")
                    filled_polydata = cut_polydata
            else:
                print(f"  横截面无线数据，使用原始数据")
                filled_polydata = cut_polydata
                
        except Exception as tri_error:
            print(f"  轮廓三角化失败: {tri_error}")
            filled_polydata = cut_polydata
        
        # 创建填充区域的Mapper和Actor
        if filled_polydata and filled_polydata.GetNumberOfPolys() > 0:
            # 创建填充区域的Mapper
            fill_mapper = vtk.vtkPolyDataMapper()
            fill_mapper.SetInputData(filled_polydata)
            
            # 创建填充区域的Actor
            fill_actor = vtk.vtkActor()
            fill_actor.SetMapper(fill_mapper)
            fill_actor.GetProperty().SetColor(0.9, 0.6, 0.6)  # 浅红色填充
            fill_actor.GetProperty().SetOpacity(0.7)  # 半透明
            fill_actor.GetProperty().SetRepresentationToSurface()
            fill_actor.GetProperty().SetEdgeVisibility(False)  # 隐藏边缘
            
            renderer_2d.AddActor(fill_actor)
            print(f"  已添加填充区域")
        
        # 创建轮廓线的Mapper和Actor（显示在填充区域上方）
        # 创建轮廓线Mapper
        contour_mapper = vtk.vtkPolyDataMapper()
        contour_mapper.SetInputData(cut_polydata)
        
        # 创建轮廓线Actor
        contour_actor = vtk.vtkActor()
        contour_actor.SetMapper(contour_mapper)
        contour_actor.GetProperty().SetColor(0.8, 0.2, 0.2)  # 红色轮廓
        contour_actor.GetProperty().SetLineWidth(3.0)
        contour_actor.GetProperty().SetRepresentationToWireframe()
        
        renderer_2d.AddActor(contour_actor)
        print(f"  已添加轮廓线")
        
        # 添加文本标注
        text_actor = vtk.vtkTextActor()
        text_actor.SetInput(f"横截面 (Z = {cut_z:.1f}) - 已填充")
        text_actor.GetTextProperty().SetFontSize(18)
        text_actor.GetTextProperty().SetColor(0, 0, 0)  # 黑色文字
        text_actor.GetTextProperty().SetBackgroundColor(1, 1, 1)  # 白色背景
        text_actor.GetTextProperty().SetBackgroundOpacity(0.7)
        text_actor.SetPosition(20, 20)
        
        # 使用AddViewProp添加2D文本
        renderer_2d.AddViewProp(text_actor)
        
        # 重置相机（2D视图）
        renderer_2d.ResetCamera()
        
        # 设置相机为正交投影，确保2D视图
        camera_2d = renderer_2d.GetActiveCamera()
        camera_2d.ParallelProjectionOn()
        
        # 调整相机位置以更好地显示横截面
        bounds = cut_polydata.GetBounds()
        center_x = (bounds[0] + bounds[1]) / 2
        center_y = (bounds[2] + bounds[3]) / 2
        
        # 设置相机位置，从Z轴正方向看
        camera_2d.SetPosition(center_x, center_y, 1000)  # 从上方看
        camera_2d.SetFocalPoint(center_x, center_y, 0)
        camera_2d.SetViewUp(0, 1, 0)  # Y轴向上
        
        # 调整平行投影比例
        width = max(bounds[1] - bounds[0], bounds[3] - bounds[2]) * 1.2
        if width > 0:
            camera_2d.SetParallelScale(width / 2)
        
        print(f"  2D横截面渲染器创建完成（带填充）")
        print(f"  横截面边界框: X[{bounds[0]:.1f}, {bounds[1]:.1f}], Y[{bounds[2]:.1f}, {bounds[3]:.1f}]")
        
        return renderer_2d
        
    except Exception as e:
        print(f"创建2D横截面渲染器失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_stl_with_vtk(file_path, show_cross_section=True):
    """使用VTK加载和显示STL文件，可选显示横截面"""
    try:
        import vtk
        
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
        
        # 创建3D渲染器
        renderer_3d = vtk.vtkRenderer()
        renderer_3d.AddActor(actor)
        renderer_3d.SetBackground(0.85, 0.85, 0.9)  # 浅灰蓝色背景，比纯白色柔和
        
        # 改进模型材质属性 - 提高表面亮度
        actor.GetProperty().SetAmbient(0.7)      # 大幅增加环境光系数
        actor.GetProperty().SetDiffuse(1.0)      # 最大漫反射系数
        actor.GetProperty().SetSpecular(0.8)     # 增加镜面反射系数
        actor.GetProperty().SetSpecularPower(60) # 提高光泽度
        actor.GetProperty().SetColor(0.25, 0.5, 1.0)  # 更亮的蓝色
        
        # 添加更强的光源 - 显著提高亮度
        # 主光源（前方）- 大幅增强
        light1 = vtk.vtkLight()
        light1.SetPosition(2, 2, 2)  # 右上前方，更远的位置
        light1.SetFocalPoint(0, 0, 0)
        light1.SetColor(1.0, 1.0, 1.0)  # 白色光
        light1.SetIntensity(1.8)  # 大幅增加强度
        renderer_3d.AddLight(light1)
        
        # 填充光源（左侧）- 大幅增强
        light2 = vtk.vtkLight()
        light2.SetPosition(-2, 1, 1)  # 左前方，更远的位置
        light2.SetFocalPoint(0, 0, 0)
        light2.SetColor(1.0, 1.0, 1.0)  # 白色光
        light2.SetIntensity(1.2)  # 大幅增加强度
        renderer_3d.AddLight(light2)
        
        # 背光（后方）- 增强
        light3 = vtk.vtkLight()
        light3.SetPosition(0, -2, -1)  # 后下方，更远的位置
        light3.SetFocalPoint(0, 0, 0)
        light3.SetColor(1.0, 1.0, 1.0)  # 白色光
        light3.SetIntensity(0.9)  # 增加强度
        renderer_3d.AddLight(light3)
        
        # 添加顶部光源 - 大幅增强
        light4 = vtk.vtkLight()
        light4.SetPosition(0, 2, 1)  # 正上方，更远的位置
        light4.SetFocalPoint(0, 0, 0)
        light4.SetColor(1.0, 1.0, 1.0)  # 白色光
        light4.SetIntensity(1.1)
        renderer_3d.AddLight(light4)
        
        # 添加前方填充光 - 额外增强
        light5 = vtk.vtkLight()
        light5.SetPosition(0, 0, 3)  # 正前方
        light5.SetFocalPoint(0, 0, 0)
        light5.SetColor(1.0, 1.0, 1.0)  # 白色光
        light5.SetIntensity(1.0)
        renderer_3d.AddLight(light5)
        
        # 启用阴影（可选）
        renderer_3d.SetUseShadows(False)  # 关闭阴影，可能使模型更亮
        
        # 设置渲染器全局环境光 - 显著提高整体亮度
        renderer_3d.SetAmbient(0.6, 0.6, 0.6)
        
        # 创建渲染窗口
        render_window = vtk.vtkRenderWindow()
        render_window.SetSize(1600, 800)  # 更宽的窗口以容纳两个视图
        render_window.SetWindowName("STL文件查看器 - 3D视图 + 横截面")
        
        # 设置视口布局
        # 左侧：3D视图 (60%)
        # 右侧：2D横截面视图 (40%)
        renderer_3d.SetViewport(0.0, 0.0, 0.6, 1.0)
        render_window.AddRenderer(renderer_3d)
        
        # 创建2D横截面渲染器（如果需要）
        renderer_2d = None
        if show_cross_section:
            # 创建横截面
            cross_section_result = create_cross_section(polydata, cut_position_percent=50)
            
            if cross_section_result:
                cut_polydata, cut_z = cross_section_result
                
                # 创建2D横截面渲染器
                renderer_2d = create_cross_section_renderer(cut_polydata, cut_z)
                
                if renderer_2d:
                    # 设置2D视图的视口（右侧40%）
                    renderer_2d.SetViewport(0.6, 0.0, 1.0, 1.0)
                    render_window.AddRenderer(renderer_2d)
        
        # 创建交互器
        render_window_interactor = vtk.vtkRenderWindowInteractor()
        render_window_interactor.SetRenderWindow(render_window)
        
        # 添加交互样式
        interactor_style = vtk.vtkInteractorStyleTrackballCamera()
        render_window_interactor.SetInteractorStyle(interactor_style)
        
        # 为3D视图添加坐标轴
        axes = vtk.vtkAxesActor()
        axes_widget = vtk.vtkOrientationMarkerWidget()
        axes_widget.SetOrientationMarker(axes)
        axes_widget.SetInteractor(render_window_interactor)
        axes_widget.SetEnabled(1)
        axes_widget.InteractiveOn()
        
        # 重置相机
        renderer_3d.ResetCamera()
        
        # 显示窗口
        print("\n正在打开显示窗口...")
        print("窗口布局:")
        print("  左侧 (60%): 3D视图")
        if renderer_2d:
            print("  右侧 (40%): 2D横截面视图")
        print("\n交互提示:")
        print("  鼠标左键拖拽: 旋转3D视图")
        print("  鼠标右键拖拽: 平移视图")
        print("  滚轮: 缩放")
        print("  按'R'键: 重置3D视图")
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
    
    # 使用VTK显示（带横截面）
    print("\n=== 使用VTK显示STL文件（带横截面） ===")
    if load_stl_with_vtk(stl_file_path, show_cross_section=True):
        print("\nSTL文件显示完成")
    else:
        print("\nSTL文件显示失败")

if __name__ == "__main__":
    main()
