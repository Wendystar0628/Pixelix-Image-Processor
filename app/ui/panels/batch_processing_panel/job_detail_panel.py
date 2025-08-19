"""
作业详情面板模块
"""
import os
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QListWidget, QListWidgetItem, QPushButton, 
    QMessageBox, QLabel, QGridLayout
)

from app.core.models.batch_models import BatchJob
from app.features.batch_processing.batch_coordinator import BatchProcessingHandler


class JobDetailPanel(QWidget):
    """
    显示作业详情的面板
    
    职责：
    1. 显示作业内的图像列表
    2. 显示作业的操作列表
    3. 处理作业内图像的管理操作
    """
    
    def __init__(self, handler: BatchProcessingHandler, parent=None):
        super().__init__(parent)
        self.handler = handler
        self.current_job_id = None
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """初始化UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 作业详情组
        job_details_group = QGroupBox("作业详情")
        job_details_layout = QVBoxLayout(job_details_group)
        
        # 操作列表
        job_details_layout.addWidget(QLabel("当前作业效果:"))
        self.job_operations_list = QListWidget()
        self.job_operations_list.setFixedHeight(100)  # 限制高度
        job_details_layout.addWidget(self.job_operations_list)
        
        # 当前作业效果区域的按钮布局
        effects_buttons_layout = QHBoxLayout()
        self.apply_operations_button = QPushButton("应用当前效果")
        self.clear_effects_button = QPushButton("清除当前作业效果")
        effects_buttons_layout.addWidget(self.apply_operations_button)
        effects_buttons_layout.addWidget(self.clear_effects_button)
        job_details_layout.addLayout(effects_buttons_layout)
        
        # 图像列表
        job_details_layout.addWidget(QLabel("作业内图像列表:"))
        self.job_items_list = QListWidget()
        self.job_items_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        job_details_layout.addWidget(self.job_items_list)
        
        # 图像管理按钮布局
        buttons_layout = QGridLayout()
        self.remove_from_job_button = QPushButton("从作业移除")
        self.remove_all_from_job_button = QPushButton("移除所有")
        
        buttons_layout.addWidget(self.remove_from_job_button, 0, 0)
        buttons_layout.addWidget(self.remove_all_from_job_button, 0, 1)
        
        job_details_layout.addLayout(buttons_layout)
        layout.addWidget(job_details_group)
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接按钮点击信号
        self.remove_from_job_button.clicked.connect(self._on_remove_from_job_clicked)
        self.remove_all_from_job_button.clicked.connect(self._on_remove_all_from_job_clicked)
        self.apply_operations_button.clicked.connect(self._on_apply_operations_clicked)
        self.clear_effects_button.clicked.connect(self._on_clear_effects_clicked)
        
        # 连接作业更新信号
        self.handler.job_manager.job_updated.connect(self._on_job_updated)
        
    def set_job(self, job_id: Optional[str]):
        """设置当前显示的作业"""
        self.current_job_id = job_id
        self.update_display()
        
    def clear_display(self):
        """清空显示内容"""
        self.current_job_id = None
        self.job_items_list.clear()
        self.job_operations_list.clear()
        
    def update_display(self):
        """更新作业详情显示"""
        self.job_items_list.clear()
        self.job_operations_list.clear()
        
        if not self.current_job_id:
            # 没有选中作业时，显示为空
            return
            
        # 获取作业
        job = self.handler.job_manager.get_job(self.current_job_id)
        if not job:
            # 作业不存在时，清空显示
            self.current_job_id = None
            return
            
        # 更新图像列表
        for file_path in job.source_paths:
            file_name = os.path.basename(file_path)
            list_item = QListWidgetItem(file_name)
            list_item.setToolTip(file_path)
            self.job_items_list.addItem(list_item)
        
        # 更新操作列表
        op_name_map = {
            "BrightnessContrastOp": "亮度/对比度",
            "ColorBalanceOp": "色彩平衡",
            "CurvesOp": "曲线",
            "GrayscaleOp": "灰度化",
            "HistogramEqualizationOp": "直方图均衡化",
            "HueSaturationOp": "色相/饱和度",
            "InvertOp": "反相",
            "LevelsOp": "色阶",
            "OtsuThresholdOp": "大津阈值",
            "ThresholdOp": "阈值",
        }
        
        for op in job.operations:
            op_class_name = op.__class__.__name__
            friendly_name = op_name_map.get(op_class_name, op_class_name)
            self.job_operations_list.addItem(friendly_name)
    
    # --- 槽函数 ---
    
    @pyqtSlot(str)
    def _on_job_updated(self, job_id: str):
        """处理作业更新事件"""
        if job_id == self.current_job_id:
            self.update_display()
    
    @pyqtSlot()
    def _on_remove_from_job_clicked(self):
        """从作业中移除选中的图像"""
        if not self.current_job_id:
            return
            
        selected_rows = [item.row() for item in self.job_items_list.selectedIndexes()]
        if not selected_rows:
            return
            
        self.handler.remove_items_from_job(self.current_job_id, selected_rows)
    
    @pyqtSlot()
    def _on_remove_all_from_job_clicked(self):
        """从作业中移除所有图像"""
        if not self.current_job_id:
            return
            
        job = self.handler.job_manager.get_job(self.current_job_id)
        if not job:
            return
            
        # 添加确认对话框
        reply = QMessageBox.question(
            self, 
            "确认移除", 
            f"确定要移除作业 '{job.name}' 中的所有图像吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.handler.clear_job_items(self.current_job_id)
    
    @pyqtSlot()
    def _on_apply_operations_clicked(self):
        """将当前主窗口的操作应用到选中的作业"""
        if not self.current_job_id:
            return
            
        self.handler.apply_main_pipeline_to_job(self.current_job_id)
    
    @pyqtSlot()
    def _on_clear_effects_clicked(self):
        """清除当前作业的效果"""
        if not self.current_job_id:
            return
            
        if self.handler.clear_job_effects(self.current_job_id):
            pass
        else:
            self.handler.show_error_message.emit("清除作业效果失败")