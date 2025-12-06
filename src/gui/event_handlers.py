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
