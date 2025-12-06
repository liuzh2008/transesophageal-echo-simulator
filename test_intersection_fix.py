#!/usr/bin/env python3
"""
测试截面交线修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_intersection_creation():
    """测试截面交线创建"""
    print("=== 测试截面交线创建 ===")
    
    try:
        # 导入模块
        from src.core.tee_simulator import get_tee_simulator
        print("[OK] TEESimulator 导入成功")
        
        # 创建模拟器实例
        simulator = get_tee_simulator()
        print("[OK] TEESimulator 实例创建成功")
        
        # 设置探头参数
        simulator.set_probe_position((0, 0, 0))
        simulator.set_probe_direction((0, 0, 1))
        simulator.set_heart_model((0, 0, 0), 50.0)
        
        print("[OK] 探头参数设置成功")
        
