"""
集成测试脚本 - 测试主窗口和2D图像显示功能
"""
import sys
import os
sys.path.insert(0, 'src')

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def test_main_window():
    """测试主窗口创建"""
    app = QApplication(sys.argv)
    
    print("创建主窗口...")
    window = MainWindow()
    
    print(f"窗口标题: {window.windowTitle()}")
    print(f"窗口几何信息: {window.geometry()}")
    
    # 检查UI组件
    print(f"UI组件数量: {len(window.ui_components)}")
    
    # 检查是否有2D视图框架
    if 'view_2d_frame' in window.ui_components:
        print("[OK] 2D视图框架已创建")
    else:
        print("[ERROR] 2D视图框架未创建")
    
    if 'view_2d_label' in window.ui_components:
        print("[OK] 2D视图标签已创建")
    else:
        print("[ERROR] 2D视图标签未创建")
    
    # 检查布局结构
    print(f"UI组件总数: {len(window.ui_components)}")
    
    # 检查关键组件
    required_components = [
        'view_3d_frame',
        'patient_id_label',
        'patient_name_label',
        'cut_plane_button'
    ]
    
    for component in required_components:
        if component in window.ui_components:
            print(f"[OK] {component} 已创建")
        else:
            print(f"[WARNING] {component} 未找到")
    
    # 显示窗口
    window.show()
    
    print("测试完成。窗口已显示，请手动检查界面。")
    print("注意：需要加载DICOM数据后才能显示切割平面和2D图像。")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(test_main_window())
