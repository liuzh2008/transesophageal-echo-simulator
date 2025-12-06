"""
测试2D截面窗口功能
"""
import sys
import os
sys.path.insert(0, 'src')

from PyQt5.QtWidgets import QApplication
import vtk

# 创建Qt应用程序
app = QApplication(sys.argv)

# 创建测试的切割平面数据
sphere_source = vtk.vtkSphereSource()
sphere_source.SetRadius(50)
sphere_source.SetThetaResolution(30)
sphere_source.SetPhiResolution(30)
sphere_source.Update()

cut_polydata = sphere_source.GetOutput()

# 导入并创建2D截面窗口
from gui.cross_section_window import create_cross_section_window

print("创建2D截面窗口...")
window = create_cross_section_window(
    cut_polydata=cut_polydata,
    cut_position=0.5,
    normal_vector=(0, 0, 1)
)

print(f"窗口标题: {window.windowTitle()}")
print(f"窗口是否可见: {window.isVisible()}")
print(f"窗口几何信息: {window.geometry()}")

# 运行应用程序
print("运行应用程序...")
sys.exit(app.exec_())
