"""
进度观察器模块 - 提供任务进度反馈

此模块提供进度条和状态更新功能，用于长时间运行的任务。
"""

from PyQt5.QtWidgets import (QProgressDialog, QProgressBar, QLabel, 
                             QVBoxLayout, QWidget, QDialog, QPushButton)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from typing import Optional, Callable, Any
import time


class ProgressObserver(QObject):
    """进度观察器"""
    
    progress_updated = pyqtSignal(int, str)  # 进度百分比, 状态消息
    task_completed = pyqtSignal(bool, str)   # 是否成功, 完成消息
    task_cancelled = pyqtSignal()           # 任务取消
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0
        self._status = "就绪"
        self._is_cancelled = False
        self._start_time = None
        self._total_steps = 100
    
    def start(self, total_steps: int = 100, initial_status: str = "开始处理..."):
        """开始进度跟踪"""
        self._progress = 0
        self._status = initial_status
        self._is_cancelled = False
        self._start_time = time.time()
        self._total_steps = total_steps
        self.progress_updated.emit(0, initial_status)
    
    def update(self, step: int, status: str = None):
        """更新进度"""
        if self._is_cancelled:
            return
        
        self._progress = min(step, self._total_steps)
        
        if status:
            self._status = status
        
        # 计算预计剩余时间
        elapsed = time.time() - self._start_time
        if self._progress > 0:
            estimated_total = elapsed * self._total_steps / self._progress
            remaining = estimated_total - elapsed
            time_str = self._format_time(remaining)
            status_with_time = f"{self._status} (剩余时间: {time_str})"
        else:
            status_with_time = self._status
        
        self.progress_updated.emit(self._progress, status_with_time)
    
    def increment(self, increment: int = 1, status: str = None):
        """增加进度"""
        self.update(self._progress + increment, status)
    
    def complete(self, success: bool = True, message: str = "完成"):
        """完成任务"""
        elapsed = time.time() - self._start_time if self._start_time else 0
        time_str = self._format_time(elapsed)
        final_message = f"{message} (用时: {time_str})"
        
        self._progress = self._total_steps
        self._status = final_message
        
        self.progress_updated.emit(self._total_steps, final_message)
        self.task_completed.emit(success, final_message)
    
    def cancel(self):
        """取消任务"""
        self._is_cancelled = True
        self._status = "已取消"
        self.task_cancelled.emit()
    
    def is_cancelled(self) -> bool:
        """检查任务是否已取消"""
        return self._is_cancelled
    
    def get_progress(self) -> int:
        """获取当前进度"""
        return self._progress
    
    def get_status(self) -> str:
        """获取当前状态"""
        return self._status
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小时"


class ProgressDialog(QDialog):
    """进度对话框"""
    
    def __init__(self, title: str = "处理中...", parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # 设置对话框大小
        self.setFixedSize(400, 150)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_button, 0, Qt.AlignCenter)
        
        # 进度观察器
        self.observer = ProgressObserver()
        self.observer.progress_updated.connect(self._on_progress_updated)
        self.observer.task_completed.connect(self._on_task_completed)
        self.observer.task_cancelled.connect(self._on_task_cancelled)
        
        # 自动关闭计时器
        self.auto_close_timer = QTimer()
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.accept)
    
    def get_observer(self) -> ProgressObserver:
        """获取进度观察器"""
        return self.observer
    
    def start_task(self, total_steps: int = 100, initial_status: str = "开始处理..."):
        """开始任务"""
        self.observer.start(total_steps, initial_status)
        self.show()
    
    def _on_progress_updated(self, progress: int, status: str):
        """处理进度更新"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
        
        # 更新窗口标题显示进度
        self.setWindowTitle(f"处理中... {progress}%")
    
    def _on_task_completed(self, success: bool, message: str):
        """处理任务完成"""
        if success:
            self.status_label.setText(f"✓ {message}")
            self.progress_bar.setValue(100)
            self.cancel_button.setText("关闭")
            self.cancel_button.clicked.disconnect()
            self.cancel_button.clicked.connect(self.accept)
            
            # 2秒后自动关闭
            self.auto_close_timer.start(2000)
        else:
            self.status_label.setText(f"✗ {message}")
            self.cancel_button.setText("确定")
            self.cancel_button.clicked.disconnect()
            self.cancel_button.clicked.connect(self.accept)
    
    def _on_task_cancelled(self):
        """处理任务取消"""
        self.status_label.setText("任务已取消")
        self.cancel_button.setText("关闭")
        self.cancel_button.clicked.disconnect()
        self.cancel_button.clicked.connect(self.accept)
    
    def _on_cancel(self):
        """取消按钮点击"""
        self.observer.cancel()


def run_with_progress(parent_widget, task_func: Callable, 
                     task_name: str = "处理", 
                     total_steps: int = 100) -> Any:
    """使用进度对话框运行任务
    
    参数:
        parent_widget: 父窗口部件
        task_func: 任务函数，接受一个ProgressObserver参数
        task_name: 任务名称
        total_steps: 总步骤数
        
    返回:
        任务函数的返回值
    """
    dialog = ProgressDialog(f"{task_name}...", parent_widget)
    result = None
    completed = False
    
    def execute_task():
        nonlocal result, completed
        try:
            result = task_func(dialog.get_observer())
            completed = True
            dialog.get_observer().complete(True, f"{task_name}完成")
        except Exception as e:
            completed = False
            dialog.get_observer().complete(False, f"{task_name}失败: {str(e)}")
    
    # 启动任务（在实际应用中可能需要使用线程）
    # 这里简化处理，直接在主线程执行
    dialog.start_task(total_steps, f"开始{task_name}...")
    
    # 在实际应用中，应该使用QThread来执行任务
    # 这里为了简化，直接调用（注意：这会阻塞UI）
    execute_task()
    
    # 显示对话框
    dialog.exec_()
    
    return result if completed else None
