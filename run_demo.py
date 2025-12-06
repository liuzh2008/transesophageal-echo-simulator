#!/usr/bin/env python3
"""
经食管超声心动图模拟器 - DEMO启动脚本

此脚本用于启动和测试基础框架。
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试所有模块导入"""
    print("正在测试模块导入...")
    
    modules_to_test = [
        ('PyQt5', 'PyQt5'),
        ('vtk', 'vtk'),
        ('numpy', 'numpy'),
        ('pydicom', 'pydicom'),
        ('应用程序模块', 'gui.main_window'),
        ('DICOM加载器', 'core.dicom_loader'),
        ('体积渲染器', 'core.volume_render'),
        ('TEE模拟器', 'core.tee_simulator'),
        ('进度工具', 'utils.progress'),
    ]
    
    all_passed = True
    
    for module_name, import_path in modules_to_test:
        try:
            if '.' in import_path:
                # 对于我们的模块，使用动态导入
                module_parts = import_path.split('.')
                import_statement = f"from {'.'.join(module_parts[:-1])} import {module_parts[-1]}"
                exec(import_statement)
            else:
                __import__(import_path)
            print(f"  [OK] {module_name} 导入成功")
        except ImportError as e:
            print(f"  [FAIL] {module_name} 导入失败: {e}")
            all_passed = False
        except Exception as e:
            print(f"  [ERROR] {module_name} 导入时出错: {e}")
            all_passed = False
    
    return all_passed

def test_vtk_availability():
    """测试VTK可用性"""
    print("\n测试VTK可用性...")
    try:
        import vtk
        from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
        print("  [OK] VTK 和 QVTKRenderWindowInteractor 可用")
        return True
    except ImportError as e:
        print(f"  [FAIL] VTK 不可用: {e}")
        print("  注意: 3D渲染功能将受限，但应用程序仍可运行")
        return False

def test_pydicom_availability():
    """测试pydicom可用性"""
    print("\n测试pydicom可用性...")
    try:
        import pydicom
        print(f"  [OK] pydicom 版本 {pydicom.__version__} 可用")
        return True
    except ImportError as e:
        print(f"  [FAIL] pydicom 不可用: {e}")
        print("  注意: DICOM文件加载功能将受限")
        return False

def create_test_data_directory():
    """创建测试数据目录"""
    print("\n检查数据目录...")
    data_dir = os.path.join(os.path.dirname(__file__), 'data', 'samples')
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        print(f"  [OK] 创建测试数据目录: {data_dir}")
        
        # 创建README文件
        readme_path = os.path.join(data_dir, 'README.txt')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("测试数据目录\n")
            f.write("============\n\n")
            f.write("请将DICOM测试文件放在此目录中。\n")
            f.write("支持的格式: .dcm, .dicom\n\n")
            f.write("示例数据可以从以下来源获取:\n")
            f.write("1. Osirix DICOM样本: https://www.osirix-viewer.com/resources/dicom-image-library/\n")
            f.write("2. DICOM库: https://www.dicomlibrary.com/\n")
        print(f"  [OK] 创建README文件")
    else:
        print(f"  [OK] 测试数据目录已存在: {data_dir}")
    
    return data_dir

def print_system_info():
    """打印系统信息"""
    print("\n系统信息:")
    print(f"  操作系统: {sys.platform}")
    print(f"  Python版本: {sys.version}")
    
    try:
        import PyQt5
        from PyQt5.QtCore import QT_VERSION_STR
        print(f"  Qt版本: {QT_VERSION_STR}")
    except:
        print("  Qt版本: 未知")

def main():
    """主函数"""
    print("=" * 60)
    print("经食管超声心动图模拟器 - 基础框架测试")
    print("=" * 60)
    
    # 打印系统信息
    print_system_info()
    
    # 测试导入
    if not test_imports():
        print("\n[WARNING] 部分模块导入失败，应用程序可能无法正常运行")
        response = input("\n是否继续? (y/n): ")
        if response.lower() != 'y':
            print("测试中止")
            return
    
    # 测试VTK
    vtk_available = test_vtk_availability()
    
    # 测试pydicom
    dicom_available = test_pydicom_availability()
    
    # 创建数据目录
    create_test_data_directory()
    
    print("\n" + "=" * 60)
    print("基础框架测试完成!")
    
    if vtk_available and dicom_available:
        print("[OK] 所有核心依赖可用")
        print("[OK] 应用程序可以正常运行")
    else:
        print("[WARNING] 部分依赖不可用:")
        if not vtk_available:
            print("  - VTK: 3D渲染功能将受限")
        if not dicom_available:
            print("  - pydicom: DICOM文件加载功能将受限")
        print("\n应用程序仍可启动，但部分功能可能无法使用")
    
    # 询问是否启动应用程序
    print("\n" + "=" * 60)
    response = input("是否启动应用程序? (y/n): ")
    
    if response.lower() == 'y':
        print("启动应用程序...")
        try:
            # 导入并启动应用程序
            from main import main as app_main
            app_main()
        except Exception as e:
            print(f"启动应用程序时出错: {e}")
            print("\n故障排除建议:")
            print("1. 确保所有依赖已安装: pip install -r requirements.txt")
            print("2. 检查Python路径配置")
            print("3. 查看具体错误信息以确定问题")
    else:
        print("\n测试完成。")
        print("要手动启动应用程序，请运行: python src/main.py")
        print("或: py src/main.py (Windows)")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
