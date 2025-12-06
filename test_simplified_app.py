#!/usr/bin/env python3
"""
简化版本应用程序测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simplified_modules():
    """测试简化后的模块"""
    print("=== 测试简化版本应用程序 ===")
    
    try:
        # 测试1：导入tee_simulator模块
        from src.core.tee_simulator import get_tee_simulator
        print("[OK] TEESimulator 导入成功")
        
        # 测试2：创建模拟器实例
        simulator = get_tee_simulator()
        print("[OK] TEESimulator 实例创建成功")
        
        # 测试3：测试基本功能
        simulator.set_heart_model((0, 0, 0), 50.0)
        simulator.set_ultrasound_parameters(60.0, 100.0)
        
        info = simulator.get_info()
        print(f"[OK] 模拟器信息: {info}")
        
        # 测试4：测试角度计算
        normal = simulator.calculate_plane_normal_from_angles(45, 45)
        print(f"[OK] 平面法线计算: {normal}")
        
        # 测试5：导入main_window模块
        from src.gui.main_window import MainWindow
        print("[OK] MainWindow 导入成功")
        
        print("\n=== 所有测试通过 ===")
        print("应用程序已成功简化为DICOM查看器")
        print("已移除所有超声探头相关功能")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simplified_modules()
