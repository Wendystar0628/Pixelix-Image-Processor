"""
批处理进度对话框模块

提供批处理任务的进度显示、取消和控制功能。
"""

from typing import Dict, Set, List
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QMessageBox
)


class BatchProgressDialog(QDialog):
    """
    批处理进度对话框类，显示批处理任务的进度并提供取消功能。
    """
    
    # 信号：请求取消批处理
    cancel_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        初始化批处理进度对话框
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setWindowTitle("批处理进度")
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinimizeButtonHint)
        
        # 状态变量
        self.is_processing = True
        self.is_cancelling = False
        
        # 作业进度跟踪
        self.job_progress: Dict[str, int] = {}  # job_id -> percentage
        self.completed_jobs: Set[str] = set()
        self.failed_jobs: Set[str] = set()
        self.current_file_info = ""
        
        # 错误信息跟踪
        self.job_error_messages: Dict[str, str] = {}  # job_id -> error_message
        self.processing_errors: List[str] = []  # 处理过程中的错误列表
        
        # 初始化UI
        self._init_ui()
        
    def _init_ui(self):
        """初始化对话框UI"""
        layout = QVBoxLayout(self)
        
        # 当前状态标签
        self.status_label = QLabel("准备处理...")
        layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 详细信息标签
        self.detail_label = QLabel("")
        layout.addWidget(self.detail_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        # 关闭按钮（初始禁用）
        self.close_button = QPushButton("关闭")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    @pyqtSlot(str, int)
    def update_job_progress(self, job_id: str, percentage: int):
        """
        更新单个作业的进度
        
        Args:
            job_id: 作业ID
            percentage: 进度百分比(0-100)
        """
        # 更新作业进度
        self.job_progress[job_id] = percentage
        
        # 计算整体进度
        self._update_overall_progress()
    
    @pyqtSlot(str, str, int, int)
    def update_file_progress(self, job_id: str, file_name: str, current: int, total: int):
        """
        更新单个文件的处理进度
        
        Args:
            job_id: 作业ID
            file_name: 当前处理的文件名
            current: 当前文件索引
            total: 总文件数
        """
        # 更新当前文件信息
        self.current_file_info = f"正在处理: {file_name} ({current}/{total})"
        self.detail_label.setText(self.current_file_info)
    
    def _update_overall_progress(self):
        """更新整体进度显示"""
        if not self.job_progress:
            return
        
        # 计算平均进度
        total_progress = sum(self.job_progress.values())
        average_progress = total_progress // len(self.job_progress)
        
        # 更新进度条
        self.progress_bar.setValue(average_progress)
        
        # 更新状态标签
        completed_count = len(self.completed_jobs)
        total_jobs = len(self.job_progress)
        self.status_label.setText(f"处理中... ({completed_count}/{total_jobs} 作业完成)")
    
    # 保持向后兼容的旧方法
    @pyqtSlot(int, int, str)
    def update_progress(self, current: int, total: int, message: str):
        """
        更新进度条和状态信息（向后兼容方法）
        
        Args:
            current: 当前进度
            total: 总任务数
            message: 状态消息
        """
        # 计算百分比
        percentage = int(current / total * 100) if total > 0 else 0
        
        # 更新UI
        self.progress_bar.setValue(percentage)
        self.status_label.setText(f"处理中... ({current}/{total})")
        self.detail_label.setText(message)
        
    @pyqtSlot(str, bool, str)
    def on_job_finished(self, job_id: str, success: bool, message: str):
        """
        单个作业完成时的处理
        
        Args:
            job_id: 作业ID
            success: 是否成功
            message: 结果消息
        """
        # 更新作业状态
        if success:
            self.completed_jobs.add(job_id)
        else:
            self.failed_jobs.add(job_id)
            # 记录错误信息
            self.job_error_messages[job_id] = message
            self.processing_errors.append(f"作业 {job_id}: {message}")
        
        # 设置作业进度为100%
        self.job_progress[job_id] = 100
        
        # 检查是否所有作业都已完成
        total_jobs = len(self.job_progress)
        finished_jobs = len(self.completed_jobs) + len(self.failed_jobs)
        
        if finished_jobs >= total_jobs:
            # 所有作业都已完成
            self._on_all_jobs_complete()
        else:
            # 更新整体进度
            self._update_overall_progress()
    
    def _on_all_jobs_complete(self):
        """所有作业完成时的处理"""
        self.is_processing = False
        
        # 统计结果
        success_count = len(self.completed_jobs)
        fail_count = len(self.failed_jobs)
        total_count = success_count + fail_count
        
        # 更新UI
        if self.is_cancelling:
            self.status_label.setText("批处理已取消")
        else:
            self.status_label.setText("批处理已完成")
            
        self.detail_label.setText(f"总计: {total_count} 作业, 成功: {success_count}, 失败: {fail_count}")
        
        # 设置进度条为100%
        self.progress_bar.setValue(100)
        
        # 启用关闭按钮，禁用取消按钮
        self.close_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        # 如果有失败的作业，显示详细错误信息
        if fail_count > 0 and not self.is_cancelling:
            self._show_detailed_error_dialog(fail_count)
    
    # 保持向后兼容的旧方法
    @pyqtSlot(dict)
    def on_batch_complete(self, results: dict):
        """
        批处理完成时的处理（向后兼容方法）
        
        Args:
            results: 包含处理结果的字典
        """
        self.is_processing = False
        
        # 统计成功和失败的数量
        success_count = sum(1 for success in results.values() if success)
        fail_count = sum(1 for success in results.values() if not success)
        total_count = len(results)
        
        # 更新UI
        if self.is_cancelling:
            self.status_label.setText("批处理已取消")
        else:
            self.status_label.setText("批处理已完成")
            
        self.detail_label.setText(f"总计: {total_count}, 成功: {success_count}, 失败: {fail_count}")
        
        # 启用关闭按钮，禁用取消按钮
        self.close_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        # 如果有失败项，显示详细信息
        if fail_count > 0 and not self.is_cancelling:
            failed_files = [path for path, success in results.items() if not success]
            failed_message = "\n".join(failed_files[:10])
            if len(failed_files) > 10:
                failed_message += f"\n... 以及其他 {len(failed_files) - 10} 个文件"
            
            QMessageBox.warning(
                self,
                "批处理警告",
                f"有 {fail_count} 个文件处理失败:\n{failed_message}"
            )
    
    def closeEvent(self, event: QCloseEvent):
        """
        处理窗口关闭事件
        
        Args:
            event: 关闭事件
        """
        if self.is_processing and not self.is_cancelling:
            # 如果正在处理，询问是否取消
            reply = QMessageBox.question(
                self,
                "确认取消",
                "批处理任务正在进行中，确定要取消吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 发出取消信号
                self.is_cancelling = True
                self.cancel_requested.emit()
                self.status_label.setText("正在取消...")
                self.cancel_button.setEnabled(False)
                event.ignore()  # 不关闭窗口，等待取消完成
            else:
                event.ignore()  # 不关闭窗口
        else:
            # 如果已完成或已经在取消中，接受关闭
            event.accept()
            
    def _on_cancel_clicked(self):
        """处理取消按钮点击事件"""
        if not self.is_processing:
            return
            
        # 发出取消信号
        self.is_cancelling = True
        self.cancel_requested.emit()
        
        # 更新UI
        self.status_label.setText("正在取消...")
        self.cancel_button.setEnabled(False)
    
    def _show_detailed_error_dialog(self, fail_count: int) -> None:
        """
        显示详细的错误信息对话框
        
        Args:
            fail_count: 失败的作业数量
        """
        # 构建错误消息
        error_title = f"批处理完成 - {fail_count} 个作业失败"
        
        # 构建详细错误信息
        error_details = []
        for job_id in self.failed_jobs:
            error_msg = self.job_error_messages.get(job_id, "未知错误")
            error_details.append(f"• 作业 {job_id}: {error_msg}")
        
        # 限制显示的错误数量
        max_errors_to_show = 10
        if len(error_details) > max_errors_to_show:
            shown_errors = error_details[:max_errors_to_show]
            remaining_count = len(error_details) - max_errors_to_show
            error_message = "\n".join(shown_errors)
            error_message += f"\n\n... 以及其他 {remaining_count} 个失败的作业"
        else:
            error_message = "\n".join(error_details)
        
        # 添加建议
        suggestions = [
            "\n建议检查以下项目：",
            "• 源文件是否存在且可读",
            "• 输出目录是否有写入权限",
            "• 作业配置是否正确",
            "• 磁盘空间是否充足"
        ]
        error_message += "\n".join(suggestions)
        
        # 创建详细错误对话框
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Warning)
        error_dialog.setWindowTitle(error_title)
        error_dialog.setText(f"有 {fail_count} 个作业处理失败。")
        error_dialog.setDetailedText(error_message)
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # 设置对话框大小
        error_dialog.setMinimumWidth(500)
        
        # 显示对话框
        error_dialog.exec()
    
    def add_processing_error(self, error_message: str) -> None:
        """
        添加处理过程中的错误信息
        
        Args:
            error_message: 错误消息
        """
        self.processing_errors.append(error_message)
        
        # 在详细信息标签中显示最新错误
        if len(self.processing_errors) <= 3:
            # 如果错误不多，显示所有错误
            error_text = "; ".join(self.processing_errors[-3:])
        else:
            # 如果错误很多，只显示最新的几个
            error_text = f"...{len(self.processing_errors)-2} 个错误; " + "; ".join(self.processing_errors[-2:])
        
        self.detail_label.setText(f"错误: {error_text}")
    
    def get_processing_summary(self) -> Dict[str, any]:
        """
        获取处理结果摘要
        
        Returns:
            Dict[str, any]: 包含处理结果的字典
        """
        return {
            'total_jobs': len(self.job_progress),
            'completed_jobs': len(self.completed_jobs),
            'failed_jobs': len(self.failed_jobs),
            'error_messages': self.job_error_messages.copy(),
            'processing_errors': self.processing_errors.copy(),
            'is_cancelled': self.is_cancelling
        } 