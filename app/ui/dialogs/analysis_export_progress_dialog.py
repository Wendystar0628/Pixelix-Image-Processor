"""
数据分析导出进度对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from app.core.models.analysis_export_config import AnalysisExportConfig
from app.core.services.analysis_export_service import AnalysisExportService


class ExportWorkerThread(QThread):
    """导出工作线程"""
    
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    export_finished = pyqtSignal(bool)  # success
    
    def __init__(self, export_service: AnalysisExportService, config: AnalysisExportConfig):
        super().__init__()
        self.export_service = export_service
        self.config = config
        self.cancelled = False
    
    def run(self):
        """执行导出任务"""
        try:
            success = self.export_service.export_analysis_data(
                self.config, 
                progress_callback=self._on_progress
            )
            self.export_finished.emit(success)
        except Exception as e:
            self.export_finished.emit(False)
    
    def _on_progress(self, current: int, total: int, message: str):
        """进度回调"""
        if not self.cancelled:
            self.progress_updated.emit(current, total, message)
    
    def cancel(self):
        """取消导出"""
        self.cancelled = True


class AnalysisExportProgressDialog(QDialog):
    """数据分析导出进度对话框"""
    
    def __init__(self, export_service: AnalysisExportService, 
                 config: AnalysisExportConfig, parent=None):
        super().__init__(parent)
        self.export_service = export_service
        self.config = config
        self.worker_thread = None
        
        self.setWindowTitle("导出进度")
        self.setModal(True)
        self.resize(500, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        self._init_ui()
        self._start_export()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("正在导出数据分析...")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备开始...")
        layout.addWidget(self.status_label)
        
        # 详细信息文本框
        self.detail_text = QTextEdit()
        self.detail_text.setMaximumHeight(200)
        self.detail_text.setReadOnly(True)
        layout.addWidget(self.detail_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setEnabled(False)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def _start_export(self):
        """开始导出"""
        self.worker_thread = ExportWorkerThread(self.export_service, self.config)
        self.worker_thread.progress_updated.connect(self._on_progress_updated)
        self.worker_thread.export_finished.connect(self._on_export_finished)
        self.worker_thread.start()
        
    def _on_progress_updated(self, current: int, total: int, message: str):
        """更新进度"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"进度: {current}/{total} - {message}")
        else:
            self.status_label.setText(message)
        
        # 添加到详细信息
        self.detail_text.append(f"[{current}/{total}] {message}")
        
        # 滚动到底部
        cursor = self.detail_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.detail_text.setTextCursor(cursor)
        
    def _on_export_finished(self, success: bool):
        """导出完成"""
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
        
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("导出完成！")
            self.detail_text.append("\n✓ 导出成功完成")
        else:
            self.status_label.setText("导出失败")
            self.detail_text.append("\n✗ 导出过程中发生错误")
            
    def _on_cancel_clicked(self):
        """取消按钮点击"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.worker_thread.wait(3000)  # 等待3秒
            
        self.reject()
        
    def closeEvent(self, event):
        """关闭事件"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.worker_thread.wait(3000)
        event.accept()