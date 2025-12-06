"""
样式定义模块 - 应用程序的视觉样式

此模块定义了应用程序的颜色方案、字体和样式表。
"""

from PyQt5.QtGui import QColor, QFont


class AppStyles:
    """应用程序样式定义"""
    
    # 颜色方案
    COLORS = {
        'primary': '#1E88E5',      # 医疗蓝
        'primary_light': '#64B5F6',
        'primary_dark': '#0D47A1',
        'secondary': '#FF9800',    # 橙色
        'secondary_light': '#FFB74D',
        'secondary_dark': '#F57C00',
        'background': '#F5F5F5',   # 浅灰背景
        'surface': '#FFFFFF',      # 白色表面
        'text_primary': '#212121', # 主要文本
        'text_secondary': '#757575', # 次要文本
        'border': '#E0E0E0',       # 边框颜色
        'success': '#4CAF50',      # 成功绿色
        'warning': '#FFC107',      # 警告黄色
        'error': '#F44336',        # 错误红色
        'info': '#2196F3',         # 信息蓝色
    }
    
    # 字体
    FONTS = {
        'title': QFont('Arial', 16, QFont.Bold),
        'heading': QFont('Arial', 14, QFont.Bold),
        'subheading': QFont('Arial', 12, QFont.Bold),
        'body': QFont('Arial', 10),
        'caption': QFont('Arial', 9),
        'monospace': QFont('Courier New', 10),
    }
    
    @classmethod
    def get_stylesheet(cls):
        """获取应用程序样式表"""
        return f"""
        /* 主窗口样式 */
        QMainWindow {{
            background-color: {cls.COLORS['background']};
        }}
        
        /* 按钮样式 */
        QPushButton {{
            background-color: {cls.COLORS['primary']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {cls.COLORS['primary_light']};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.COLORS['primary_dark']};
        }}
        
        QPushButton:disabled {{
            background-color: {cls.COLORS['border']};
            color: {cls.COLORS['text_secondary']};
        }}
        
        /* 工具栏按钮 */
        QToolButton {{
            background-color: transparent;
            border: 1px solid transparent;
            padding: 4px;
            border-radius: 2px;
        }}
        
        QToolButton:hover {{
            background-color: rgba(30, 136, 229, 0.1);
            border: 1px solid {cls.COLORS['primary_light']};
        }}
        
        QToolButton:pressed {{
            background-color: rgba(30, 136, 229, 0.2);
        }}
        
        /* 滑块样式 */
        QSlider::groove:horizontal {{
            border: 1px solid {cls.COLORS['border']};
            height: 6px;
            background: {cls.COLORS['surface']};
            margin: 2px 0;
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: {cls.COLORS['primary']};
            border: 1px solid {cls.COLORS['primary_dark']};
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {cls.COLORS['primary_light']};
        }}
        
        /* 组合框样式 */
        QComboBox {{
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            padding: 4px 8px;
            background: {cls.COLORS['surface']};
            min-width: 6em;
        }}
        
        QComboBox:hover {{
            border: 1px solid {cls.COLORS['primary_light']};
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {cls.COLORS['text_primary']};
            width: 0;
            height: 0;
            margin-right: 8px;
        }}
        
        /* 复选框样式 */
        QCheckBox {{
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {cls.COLORS['border']};
            border-radius: 2px;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {cls.COLORS['primary']};
            border: 1px solid {cls.COLORS['primary_dark']};
        }}
        
        QCheckBox::indicator:checked:hover {{
            background-color: {cls.COLORS['primary_light']};
        }}
        
        /* 分组框样式 */
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: {cls.COLORS['surface']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
        }}
        
        /* 标签样式 */
        QLabel[important="true"] {{
            font-weight: bold;
            color: {cls.COLORS['primary_dark']};
        }}
        
        /* 状态栏样式 */
        QStatusBar {{
            background-color: {cls.COLORS['surface']};
            border-top: 1px solid {cls.COLORS['border']};
        }}
        
        QStatusBar QLabel {{
            padding: 2px 8px;
            border-left: 1px solid {cls.COLORS['border']};
        }}
        
        /* 菜单栏样式 */
        QMenuBar {{
            background-color: {cls.COLORS['surface']};
            border-bottom: 1px solid {cls.COLORS['border']};
        }}
        
        QMenuBar::item {{
            padding: 4px 8px;
            background-color: transparent;
        }}
        
        QMenuBar::item:selected {{
            background-color: rgba(30, 136, 229, 0.1);
        }}
        
        /* 工具栏样式 */
        QToolBar {{
            background-color: {cls.COLORS['surface']};
            border-bottom: 1px solid {cls.COLORS['border']};
            spacing: 4px;
            padding: 2px;
        }}
        
        /* 分割器样式 */
        QSplitter::handle {{
            background-color: {cls.COLORS['border']};
        }}
        
        QSplitter::handle:hover {{
            background-color: {cls.COLORS['primary_light']};
        }}
        
        /* 滚动条样式 */
        QScrollBar:vertical {{
            border: none;
            background-color: {cls.COLORS['background']};
            width: 10px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['primary']};
            border-radius: 5px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['primary_light']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        """
    
    @classmethod
    def apply_stylesheet(cls, widget):
        """应用样式表到部件"""
        widget.setStyleSheet(cls.get_stylesheet())
        
        # 设置字体
        widget.setFont(cls.FONTS['body'])
    
    @classmethod
    def get_color(cls, color_name):
        """获取颜色"""
        return QColor(cls.COLORS.get(color_name, '#000000'))
    
    @classmethod
    def get_font(cls, font_name):
        """获取字体"""
        return cls.FONTS.get(font_name, QFont('Arial', 10))
