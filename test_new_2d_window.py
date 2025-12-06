"""
测试新的2D切片窗口功能
"""
import sys
import os
sys.path.insert(0, 'src')

from PyQt5.QtWidgets import QApplication
import numpy as np

# 创建Qt应用程序
app = QApplication(sys.argv)

# 创建测试的VTK图像数据
import vtk

# 创建一个简单的3D体积数据
shape = (100, 100, 100)
test_data = np.random.rand(*shape).astype(np.float32)

# 转换为VTK图像数据
from vtk.util import numpy_support
vtk_array = numpy_support.numpy_to_vtk(test_data.ravel(order='F'), deep=True, array_type=vtk.VTK_FLOAT)

vtk_image = vtk.vtkImageData()
vtk_image.SetDimensions(shape[1], shape[0], shape[2])  # VTK使用 (X, Y, Z)
vtk_image.AllocateScalars(vtk.VTK_FLOAT, 1)
vtk_image.GetPointData().SetScalars(vtk_array)
vtk_image.SetSpacing(1.0, 1.0, 1.0)
vtk_image.SetOrigin(0.0, 0.0, 0.0)

# 导入并创建2D切片窗口
from gui.cross_section_window import create_cross_section_window

print("创建新的2D切片窗口...")
window = create_cross_section_window(
    image_data=vtk_image,
    normal_vector=(0, 0, 1),
    cut_position=0.5
)

print(f"窗口标题: {window.windowTitle()}")
print(f"窗口是否可见: {window.isVisible()}")
print(f"窗口几何信息: {window.geometry()}")

# 运行应用程序
print("运行应用程序...")
sys.exit(app.exec_())
