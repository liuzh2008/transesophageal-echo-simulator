"""
事件处理器模块 - 负责处理用户事件

此模块按照关注点分享原则，将事件处理逻辑从主窗口中分离出来。
"""

from PyQt5.QtWidgets import QFileDialog, QMessageBox


class EventHandlers:
    """事件处理器"""
    
    def __init__(self, main_window, vtk_manager, dicom_manager):
        self.main_window = main_window
        self.vtk_manager = vtk_manager
        self.dicom_manager = dicom_manager
        
        # UI组件引用
        self.ui_components = {}
    
    def set_ui_components(self, ui_components):
        """设置UI组件引用"""
        self.ui_components = ui_components
    
    
    def handle_open_directory(self):
        """处理打开文件夹事件"""
        dir_path = QFileDialog.getExistingDirectory(
            self.main_window,
            "选择DICOM文件夹",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if dir_path:
            self.main_window.statusBar().showMessage(f"正在加载文件夹: {dir_path}", 3000)
            
            # 加载DICOM文件夹
            success = self.dicom_manager.load_directory(dir_path)
            
            if success:
                # 更新患者信息显示
                patient_info = self.dicom_manager.get_patient_info()
                self._update_patient_info(patient_info)
                
                # 获取体积数据
                volume_data = self.dicom_manager.get_volume_data()
                
                if volume_data is not None:
                    # 获取间距和原点
                    spacing = self.dicom_manager.get_spacing()
                    origin = self.dicom_manager.get_origin()
                    
                    # 更新3D视图
                    self.vtk_manager.set_volume_data(volume_data, spacing, origin)
                    
                    self.main_window.statusBar().showMessage(
                        f"成功加载DICOM文件夹: {dir_path.split('/')[-1]} "
                        f"({volume_data.shape[2] if hasattr(volume_data, 'shape') else '未知'}个切片)", 
                        5000)
                else:
                    self.main_window.statusBar().showMessage(
                        "加载DICOM文件夹失败: 无体积数据", 5000)
            else:
                self.main_window.statusBar().showMessage("加载DICOM文件夹失败", 5000)
    
    def handle_toggle_3d_view(self, checked):
        """处理切换3D视图事件"""
        if 'view_3d_frame' in self.ui_components:
            self.ui_components['view_3d_frame'].setVisible(checked)
        
        self.main_window.statusBar().showMessage(
            f"3D视图: {'显示' if checked else '隐藏'}", 2000)
    
    def handle_reset_views(self):
        """处理重置视图事件"""
        self.vtk_manager.reset_camera()
        self.main_window.statusBar().showMessage("所有视图已重置", 2000)
    
    def handle_change_render_mode(self, mode):
        """处理更改渲染模式事件"""
        self.main_window.statusBar().showMessage(f"渲染模式: {mode}", 2000)
        self.vtk_manager.change_render_mode(mode)
    
    def handle_change_opacity(self, value):
        """处理更改透明度事件"""
        opacity = value / 100.0
        self.main_window.statusBar().showMessage(f"透明度: {value}%", 1000)
        self.vtk_manager.change_opacity(value)
    
    def handle_show_about(self):
        """处理显示关于信息事件"""
        about_text = """
        <h3>DICOM影像查看器</h3>
        <p>版本: 1.0.0</p>
        <p>开发团队: 医疗影像实验室</p>
        <p>版权所有 © 2025</p>
        <hr>
        <p>此应用程序提供3D DICOM影像查看功能。</p>
        <p>技术支持: support@medical-imaging-lab.com</p>
        """
        
        QMessageBox.about(self.main_window, "关于", about_text)
    
    def handle_fan_apex_offset_changed(self):
        """
        处理扇形顶点偏移滑动条变化事件
        
        当扇形顶点偏移滑块值改变时调用此方法。计算物理偏移量并更新 3D 切割平面显示，
        同时会读取当前的 Omniplane 角度值，将角度信息传递给切割平面渲染。
        
        处理流程:
            1. 从 UI 读取 X/Y/Z 三个方向的滑块值（范围 -100 ~ 100）
            2. 将滑块值归一化到 -1.0 ~ 1.0 范围
            3. 根据体积数据边界计算物理偏移量
            4. 更新 UI 标签显示当前偏移值
            5. 获取当前 Omniplane 角度值
            6. 调用 vtk_manager.show_cut_plane() 更新 3D 视图
            7. 刷新主窗口中的 2D 视图显示
        
        @function handle_fan_apex_offset_changed
        @memberof EventHandlers
        @instance
        @returns {void}
        @triggers {vtk_manager.show_cut_plane} 更新 3D 切割平面
        @triggers {_show_2d_image_in_main_window} 刷新 2D 视图
        @example
        // 当扇形顶点偏移滑块值改变时自动触发
        fan_apex_x_slider.valueChanged.connect(event_handlers.handle_fan_apex_offset_changed)
        """
        # 从UI读取滑动条值
        offset_x_val = 0
        offset_y_val = 0
        offset_z_val = 0
        
        if 'fan_apex_x_slider' in self.main_window.ui_components:
            offset_x_val = self.main_window.ui_components['fan_apex_x_slider'].value()
        if 'fan_apex_y_slider' in self.main_window.ui_components:
            offset_y_val = self.main_window.ui_components['fan_apex_y_slider'].value()
        if 'fan_apex_z_slider' in self.main_window.ui_components:
            offset_z_val = self.main_window.ui_components['fan_apex_z_slider'].value()
        
        # 转换为 -1.0 ~ 1.0
        offset_x = offset_x_val / 100.0
        offset_y = offset_y_val / 100.0
        offset_z = offset_z_val / 100.0
        
        # 更新标签
        if 'fan_apex_x_label' in self.main_window.ui_components:
            self.main_window.ui_components['fan_apex_x_label'].setText(f"X偏移: {offset_x:.2f}")
        if 'fan_apex_y_label' in self.main_window.ui_components:
            self.main_window.ui_components['fan_apex_y_label'].setText(f"Y偏移: {offset_y:.2f}")
        if 'fan_apex_z_label' in self.main_window.ui_components:
            self.main_window.ui_components['fan_apex_z_label'].setText(f"Z偏移: {offset_z:.2f}")
        
        # 计算物理偏移量（基于体积尺寸）
        physical_offset_x = 0.0
        physical_offset_y = 0.0
        physical_offset_z = 0.0
        
        # 通过 volume_renderer 获取图像数据
        image_data = None
        if hasattr(self.vtk_manager, 'volume_renderer') and self.vtk_manager.volume_renderer is not None:
            image_data = self.vtk_manager.volume_renderer.get_vtk_image_data()
        if image_data is None:
            # 尝试通过单例获取
            from core.volume_render import get_volume_renderer
            vr = get_volume_renderer()
            image_data = vr.get_vtk_image_data()
        
        if image_data is not None:
            bounds = image_data.GetBounds()
            extent_x = (bounds[1] - bounds[0]) / 2.0
            extent_y = (bounds[3] - bounds[2]) / 2.0
            extent_z = (bounds[5] - bounds[4]) / 2.0
            physical_offset_x = offset_x * extent_x
            physical_offset_y = offset_y * extent_y
            physical_offset_z = offset_z * extent_z
            print(f"[DEBUG] 物理偏移量: x={physical_offset_x:.1f}, y={physical_offset_y:.1f}, z={physical_offset_z:.1f}")
        
        # 更新状态栏
        self.main_window.statusBar().showMessage(
            f"扇形顶点偏移: X={offset_x:.2f}, Y={offset_y:.2f}, Z={offset_z:.2f}", 2000)
        
        # 获取 omniplane 角度
        omniplane_angle = 0
        if 'omniplane_slider' in self.main_window.ui_components:
            omniplane_angle = self.main_window.ui_components['omniplane_slider'].value()
        
        # 更新 3D 切割平面
        self.vtk_manager.show_cut_plane(
            position_percent=0.5,
            normal=(0, 0, 1),
            show_2d_window=False,
            fan_apex_offset_x=physical_offset_x,
            fan_apex_offset_y=physical_offset_y,
            fan_apex_offset_z=physical_offset_z,
            omniplane_angle=omniplane_angle
        )
        
        # 刷新2D视图（如果已显示）
        self._show_2d_image_in_main_window()
    
    def handle_omniplane_changed(self):
        """
        处理 Omniplane 角度滑块变化事件
        
        当 Omniplane 角度滑块值改变时调用此方法。更新 UI 显示并同步更新 3D 切割平面和 2D 视图，
        实现 TEE 探头扫描平面的实时旋转效果。使用 Rodrigues 旋转公式计算旋转后的平面坐标系。
        
        处理流程:
            1. 从 UI 读取 Omniplane 角度滑块值（范围 0-180 度）
            2. 更新角度标签显示当前角度值
            3. 在状态栏显示当前角度信息
            4. 获取当前扇形顶点偏移值（X/Y/Z 三个方向）
            5. 将偏移值转换为物理偏移量（基于体积数据边界）
            6. 调用 vtk_manager.show_cut_plane() 更新 3D 切割平面（包含 omniplane 旋转参数）
            7. 调用 _show_2d_image_in_main_window() 刷新 2D 扇形视图
        
        @function handle_omniplane_changed
        @memberof EventHandlers
        @instance
        @returns {void}
        @triggers {vtk_manager.show_cut_plane} 更新 3D 切割平面，传递 omniplane_angle 参数
        @triggers {_show_2d_image_in_main_window} 刷新 2D 扇形视图
        @uses {RodriguesRotation} 在 volume_render.py 中计算旋转后的平面坐标系
        @example
        // 当 Omniplane 角度滑块值改变时自动触发
        omniplane_slider.valueChanged.connect(event_handlers.handle_omniplane_changed)
        """
        # 从 UI 读取当前角度值
        angle = 0
        if 'omniplane_slider' in self.main_window.ui_components:
            angle = self.main_window.ui_components['omniplane_slider'].value()
        
        # 更新角度标签显示
        if 'omniplane_label' in self.main_window.ui_components:
            self.main_window.ui_components['omniplane_label'].setText(f"Omniplane 角度: {angle}°")
        
        # 在状态栏显示角度信息
        self.main_window.statusBar().showMessage(f"Omniplane 角度: {angle}°", 2000)
        
        # 获取扇形顶点偏移
        fan_apex_offset_x = 0.0
        fan_apex_offset_y = 0.0
        fan_apex_offset_z = 0.0
        
        from core.volume_render import get_volume_renderer
        volume_renderer = get_volume_renderer()
        vtk_image_data = volume_renderer.get_vtk_image_data()
        
        if vtk_image_data is not None and 'fan_apex_x_slider' in self.main_window.ui_components:
            offset_x = self.main_window.ui_components['fan_apex_x_slider'].value() / 100.0
            offset_y = self.main_window.ui_components['fan_apex_y_slider'].value() / 100.0
            offset_z = self.main_window.ui_components['fan_apex_z_slider'].value() / 100.0
            bounds = vtk_image_data.GetBounds()
            fan_apex_offset_x = offset_x * (bounds[1] - bounds[0]) / 2.0
            fan_apex_offset_y = offset_y * (bounds[3] - bounds[2]) / 2.0
            fan_apex_offset_z = offset_z * (bounds[5] - bounds[4]) / 2.0
        
        # 更新 3D 切割平面（包含 omniplane 旋转）
        self.vtk_manager.show_cut_plane(
            position_percent=0.5,
            normal=(0, 0, 1),
            show_2d_window=False,
            fan_apex_offset_x=fan_apex_offset_x,
            fan_apex_offset_y=fan_apex_offset_y,
            fan_apex_offset_z=fan_apex_offset_z,
            omniplane_angle=angle
        )
        
        # 刷新2D视图
        self._show_2d_image_in_main_window(vtk_image_data=vtk_image_data)
    
    def handle_show_cut_plane(self):
        """
        处理显示切割平面事件（在主窗口中显示2D图像）
        
        此方法处理切割平面按钮点击事件，包括：
        1. 记录开始时间
        2. 更新计时标签状态
        3. 检查VTK可用性和数据存在性
        4. 调用VTK管理器显示切割平面
        5. 在主窗口中显示2D图像
        6. 更新计时标签显示用时
        
        @function handle_show_cut_plane
        @memberof EventHandlers
        @instance
        @returns {void}
        @throws {Exception} 如果VTK不可用或数据不存在
        @example
        // 在事件连接中使用
        cut_plane_button.clicked.connect(event_handlers.handle_show_cut_plane)
        """
        import time
        
        # 记录开始时间
        start_time = time.time()
        
        # 更新计时标签为"计算中..."
        if 'cut_plane_time_label' in self.ui_components:
            self.ui_components['cut_plane_time_label'].setText("用时: 计算中...")
            self.ui_components['cut_plane_time_label'].setStyleSheet("""
                QLabel {
                    color: #e67e22;
                    font-weight: bold;
                    font-style: italic;
                    padding: 5px;
                    background-color: #fff9e6;
                    border-radius: 4px;
                    border: 1px solid #f39c12;
                }
            """)
        
        if not self.vtk_manager.is_available():
            self.main_window.statusBar().showMessage("VTK不可用，无法显示切割平面", 3000)
            QMessageBox.warning(self.main_window, "警告", "VTK 3D渲染引擎未安装，无法显示切割平面")
            self._update_time_label(start_time, False)
            return
        
        # 检查是否有体积数据
        from core.volume_render import get_volume_renderer
        volume_renderer = get_volume_renderer()
        
        # 一次性获取 VTK 图像数据（利用缓存）
        vtk_image_data = volume_renderer.get_vtk_image_data()
        
        if volume_renderer.volume_data is None:
            self.main_window.statusBar().showMessage("请先加载DICOM数据", 3000)
            QMessageBox.warning(self.main_window, "警告", "请先加载DICOM数据以显示切割平面")
            self._update_time_label(start_time, False)
            return
        
        # 获取扇形顶点偏移
        fan_apex_offset_x = 0.0
        fan_apex_offset_y = 0.0
        fan_apex_offset_z = 0.0
        if 'fan_apex_x_slider' in self.main_window.ui_components:
            offset_x = self.main_window.ui_components['fan_apex_x_slider'].value() / 100.0
            offset_y = self.main_window.ui_components['fan_apex_y_slider'].value() / 100.0
            offset_z = self.main_window.ui_components['fan_apex_z_slider'].value() / 100.0
            
            if vtk_image_data is not None:
                bounds = vtk_image_data.GetBounds()
                fan_apex_offset_x = offset_x * (bounds[1] - bounds[0]) / 2.0
                fan_apex_offset_y = offset_y * (bounds[3] - bounds[2]) / 2.0
                fan_apex_offset_z = offset_z * (bounds[5] - bounds[4]) / 2.0
                print(f"[DEBUG] handle_show_cut_plane 物理偏移量: x={fan_apex_offset_x:.1f}, y={fan_apex_offset_y:.1f}, z={fan_apex_offset_z:.1f}")
        
        # 获取 Omniplane 角度 - 用于控制 TEE 探头扫描平面的旋转
        # 从 UI 滑块读取当前角度值（范围 0-180 度），默认为 0 度
        omniplane_angle = 0
        if 'omniplane_slider' in self.main_window.ui_components:
            omniplane_angle = self.main_window.ui_components['omniplane_slider'].value()
        
        # 显示切割平面 - 传递所有参数包括扇形顶点偏移和 Omniplane 角度
        # @param {float} position_percent - 切割位置百分比（0.5 = 50%位置）
        # @param {tuple} normal - 平面法线向量，默认 (0, 0, 1) 垂直于 Z 轴
        # @param {bool} show_2d_window - 是否在新窗口显示 2D 图像，False 表示在主窗口显示
        # @param {float} fan_apex_offset_x - 扇形顶点 X 方向物理偏移量
        # @param {float} fan_apex_offset_y - 扇形顶点 Y 方向物理偏移量
        # @param {float} fan_apex_offset_z - 扇形顶点 Z 方向物理偏移量
        # @param {int} omniplane_angle - Omniplane 旋转角度（0-180 度），控制扫描平面旋转
        success = self.vtk_manager.show_cut_plane(
            position_percent=0.5,  # 50%位置
            normal=(0, 0, 1),      # 垂直于Z轴
            show_2d_window=False,  # 不在新窗口中显示2D图像，而是在主窗口中显示
            fan_apex_offset_x=fan_apex_offset_x,
            fan_apex_offset_y=fan_apex_offset_y,
            fan_apex_offset_z=fan_apex_offset_z,
            omniplane_angle=omniplane_angle
        )
        
        if success:
            # 在主窗口中显示2D图像
            self._show_2d_image_in_main_window(vtk_image_data=vtk_image_data)
            
            # 更新计时标签
            self._update_time_label(start_time, True)
            
            self.main_window.statusBar().showMessage("切割平面显示成功（50%位置，红色线条+浅红色填充），2D图像已显示在主窗口中", 5000)
        else:
            self.main_window.statusBar().showMessage("切割平面显示失败", 3000)
            QMessageBox.warning(self.main_window, "警告", "切割平面显示失败，请检查数据")
            self._update_time_label(start_time, False)
    
    def _update_time_label(self, start_time, success):
        """
        更新计时标签
        
        此方法计算从开始时间到当前时间的用时，并更新计时标签的显示。
        根据操作成功与否，显示不同的颜色和文本。
        
        @function _update_time_label
        @memberof EventHandlers
        @instance
        @param {float} start_time - 开始时间（time.time()返回的时间戳）
        @param {bool} success - 操作是否成功
        @returns {void}
        @example
        // 在handle_show_cut_plane方法中调用
        self._update_time_label(start_time, True)
        """
        import time
        
        # 计算用时
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if 'cut_plane_time_label' in self.ui_components:
            if success:
                # 格式化时间显示（毫秒）
                if elapsed_time < 0.001:
                    time_str = "<1ms"
                elif elapsed_time < 1.0:
                    time_str = f"{elapsed_time*1000:.1f}ms"
                else:
                    time_str = f"{elapsed_time:.2f}s"
                
                self.ui_components['cut_plane_time_label'].setText(f"用时: {time_str}")
                self.ui_components['cut_plane_time_label'].setStyleSheet("""
                    QLabel {
                        color: #27ae60;
                        font-weight: bold;
                        padding: 5px;
                        background-color: #eafaf1;
                        border-radius: 4px;
                        border: 1px solid #2ecc71;
                    }
                """)
            else:
                self.ui_components['cut_plane_time_label'].setText("用时: 失败")
                self.ui_components['cut_plane_time_label'].setStyleSheet("""
                    QLabel {
                        color: #c0392b;
                        font-weight: bold;
                        padding: 5px;
                        background-color: #fdedec;
                        border-radius: 4px;
                        border: 1px solid #e74c3c;
                    }
                """)
    
    def _show_2d_image_in_main_window(self, vtk_image_data=None):
        """在主窗口中显示2D图像"""
        try:
            # 获取2D视图框架
            if 'view_2d_frame' not in self.ui_components:
                print("警告: 找不到2D视图框架")
                return
            
            view_2d_frame = self.ui_components['view_2d_frame']
            
            # 清除现有的占位符
            if hasattr(self.main_window, 'view_2d_placeholder'):
                layout = view_2d_frame.layout()
                if layout:
                    # 移除占位符
                    self.main_window.view_2d_placeholder.setParent(None)
            
            # 创建内嵌的2D视图
            from .cross_section_window import create_embedded_2d_view
            from core.volume_render import get_volume_renderer
            
            if vtk_image_data is None:
                volume_renderer = get_volume_renderer()
                vtk_image_data = volume_renderer.get_vtk_image_data()
            
            if vtk_image_data is None:
                print("警告: 无法获取VTK图像数据")
                return
            
            # 获取扇形顶点偏移
            fan_apex_offset_x = 0.0
            fan_apex_offset_y = 0.0
            fan_apex_offset_z = 0.0
            if 'fan_apex_x_slider' in self.main_window.ui_components:
                offset_x = self.main_window.ui_components['fan_apex_x_slider'].value() / 100.0
                offset_y = self.main_window.ui_components['fan_apex_y_slider'].value() / 100.0
                offset_z = self.main_window.ui_components['fan_apex_z_slider'].value() / 100.0
                
                if vtk_image_data is not None:
                    bounds = vtk_image_data.GetBounds()
                    fan_apex_offset_x = offset_x * (bounds[1] - bounds[0]) / 2.0
                    fan_apex_offset_y = offset_y * (bounds[3] - bounds[2]) / 2.0
                    fan_apex_offset_z = offset_z * (bounds[5] - bounds[4]) / 2.0
                    print(f"[DEBUG] _show_2d_image_in_main_window 物理偏移量: x={fan_apex_offset_x:.1f}, y={fan_apex_offset_y:.1f}, z={fan_apex_offset_z:.1f}")
            
            # 获取 Omniplane 角度
            omniplane_angle = 0
            if 'omniplane_slider' in self.main_window.ui_components:
                omniplane_angle = self.main_window.ui_components['omniplane_slider'].value()
            
            # 创建2D视图小部件
            vtk_widget = create_embedded_2d_view(
                image_data=vtk_image_data,
                normal_vector=(0, 0, 1),  # 垂直于Z轴
                cut_position=0.5,         # 50%位置
                parent_widget=view_2d_frame,
                fan_apex_offset_x=fan_apex_offset_x,
                fan_apex_offset_y=fan_apex_offset_y,
                fan_apex_offset_z=fan_apex_offset_z,
                omniplane_angle=omniplane_angle
            )
            
            if vtk_widget is not None:
                # 添加到2D视图框架
                layout = view_2d_frame.layout()
                if layout:
                    # 移除所有现有部件（除了标签）
                    for i in reversed(range(layout.count())):
                        widget = layout.itemAt(i).widget()
                        if widget and widget != self.ui_components.get('view_2d_label'):
                            widget.setParent(None)
                    
                    # 添加VTK小部件
                    layout.addWidget(vtk_widget)
                    
                    # 保存引用
                    self.ui_components['view_2d_vtk_widget'] = vtk_widget
                    print("[DEBUG] 2D图像已成功显示在主窗口中")
                else:
                    print("警告: 2D视图框架没有布局")
            else:
                print("警告: 无法创建2D视图小部件")
                
        except Exception as e:
            print(f"在主窗口中显示2D图像时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_exit(self):
        """处理退出事件"""
        self.main_window.close()
    
    def _update_patient_info(self, patient_info):
        """更新患者信息显示"""
        if 'patient_id_label' in self.ui_components:
            self.ui_components['patient_id_label'].setText(
                str(patient_info.get('patient_id', '未知')))
        
        if 'patient_name_label' in self.ui_components:
            self.ui_components['patient_name_label'].setText(
                str(patient_info.get('patient_name', '未知')))
        
        if 'study_date_label' in self.ui_components:
            self.ui_components['study_date_label'].setText(
                str(patient_info.get('study_date', '未知')))
        
        if 'modality_label' in self.ui_components:
            self.ui_components['modality_label'].setText(
                str(patient_info.get('modality', '未知')))
