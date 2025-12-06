#!/usr/bin/env python3
"""
经食管超声心动图模拟器 - 主应用程序入口

此应用程序提供交互式的3D可视化工具，帮助临床医生理解和模拟TEE检查过程。
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """应用程序主函数"""
    # 创建Qt应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("经食管超声心动图模拟器")
    app.setOrganizationName("医疗影像实验室")
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 自动加载DICOM文件夹（如果存在）
    auto_load_dicom_folder(window)
    
    # 运行应用程序
    sys.exit(app.exec_())


def auto_load_dicom_folder(window):
    """自动加载DICOM文件夹（如果存在）"""
    dicom_folder = r"D:\patients\SE7"
    
    if os.path.exists(dicom_folder):
        print(f"检测到DICOM文件夹: {dicom_folder}")
        print("正在自动加载...")
        
        # 延迟加载，确保窗口完全初始化
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, lambda: load_dicom_folder(window, dicom_folder))
    else:
        print(f"DICOM文件夹不存在: {dicom_folder}")
        print("应用程序将以空状态启动")


def load_dicom_folder(window, folder_path):
    """加载DICOM文件夹"""
    try:
        # 使用窗口的DICOM管理器
        dicom_manager = window.dicom_manager
        vtk_manager = window.vtk_manager
        
        # 加载DICOM文件夹
        success = dicom_manager.load_directory(folder_path)
        
        if success:
            # 更新患者信息显示
            patient_info = dicom_manager.get_patient_info()
            
            # 通过事件处理器更新UI
            if hasattr(window, 'event_handlers'):
                window.event_handlers._update_patient_info(patient_info)
            
            # 获取体积数据
            volume_data = dicom_manager.get_volume_data()
            
            if volume_data is not None:
                # 获取间距和原点
                spacing = dicom_manager.get_spacing()
                origin = dicom_manager.get_origin()
                
                # 更新3D视图
                vtk_manager.set_volume_data(volume_data, spacing, origin)
                
                window.statusBar().showMessage(f"自动加载成功: {os.path.basename(folder_path)} ({volume_data.shape[2]}个切片)", 5000)
                print(f"自动加载成功: {folder_path} ({volume_data.shape[2]}个切片)")
            else:
                window.statusBar().showMessage("自动加载失败: 无体积数据", 5000)
                print("自动加载失败: 无体积数据")
        else:
            window.statusBar().showMessage("自动加载DICOM文件夹失败", 5000)
            print("自动加载DICOM文件夹失败")
            
    except Exception as e:
        window.statusBar().showMessage(f"自动加载时出错: {str(e)}", 5000)
        print(f"自动加载时出错: {e}")


if __name__ == "__main__":
    main()
