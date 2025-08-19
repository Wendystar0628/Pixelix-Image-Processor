"""作业选择组件"""

from typing import List, Dict, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QPushButton,
    QCheckBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal


class JobSelectionWidget(QWidget):
    """作业选择组件"""
    
    # 信号：选择状态改变
    selection_changed = pyqtSignal(list)  # 选中的作业ID列表
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.jobs_data = {}  # {job_id: {"name": str, "image_count": int}}
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 全选按钮
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setMaximumWidth(60)
        self.select_all_btn.clicked.connect(self._toggle_select_all)
        header_layout.addWidget(self.select_all_btn)
        
        layout.addLayout(header_layout)
        
        # 作业列表
        self.job_list = QListWidget()
        self.job_list.setMinimumHeight(100)
        self.job_list.setMaximumHeight(200)
        self.job_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
                min-height: 100px;
                outline: none;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #f0f0f0;
                min-height: 25px;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            QListWidget::item:selected {
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.job_list)
        
        # 选择状态标签
        self.status_label = QLabel("未选择任何作业")
        self.status_label.setStyleSheet("color: #666666; font-size: 12px;")
        layout.addWidget(self.status_label)
        
    def set_jobs_data(self, jobs_data: Dict[str, Dict]):
        """设置作业数据"""
        self.jobs_data = jobs_data
        self._refresh_job_list()
        
    def _refresh_job_list(self):
        """刷新作业列表"""
        self.job_list.clear()
        
        if not self.jobs_data:
            return
            
        for job_id, job_info in self.jobs_data.items():
            item = QListWidgetItem()
            
            # 创建自定义widget
            widget = QWidget()
            widget.setMinimumHeight(30)
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(6, 2, 6, 2)
            layout.setSpacing(6)
            
            # 复选框
            checkbox = QCheckBox()
            checkbox.setProperty("job_id", job_id)
            checkbox.stateChanged.connect(self._on_selection_changed)
            layout.addWidget(checkbox)
            
            # 作业信息
            info_label = QLabel(f"{job_info['name']} ({job_info['image_count']} 张图像)")
            info_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # 垂直居中
            layout.addWidget(info_label)
            layout.addStretch()
            
            # 设置item
            from PyQt6.QtCore import QSize
            item.setSizeHint(QSize(widget.sizeHint().width(), 30))
            self.job_list.addItem(item)
            self.job_list.setItemWidget(item, widget)
            
        self._update_status()
        
    def _on_selection_changed(self):
        """选择状态改变处理"""
        selected_ids = self.get_selected_job_ids()
        self.selection_changed.emit(selected_ids)
        self._update_status()
        self._update_select_all_button()
        
    def _update_status(self):
        """更新状态标签"""
        selected_count = len(self.get_selected_job_ids())
        total_count = len(self.jobs_data)
        
        if selected_count == 0:
            self.status_label.setText("未选择任何作业")
        else:
            total_images = sum(
                self.jobs_data[job_id]['image_count'] 
                for job_id in self.get_selected_job_ids()
            )
            self.status_label.setText(
                f"已选择 {selected_count}/{total_count} 个作业，共 {total_images} 张图像"
            )
            
    def _update_select_all_button(self):
        """更新全选按钮状态"""
        selected_count = len(self.get_selected_job_ids())
        total_count = len(self.jobs_data)
        
        if selected_count == 0:
            self.select_all_btn.setText("全选")
        elif selected_count == total_count:
            self.select_all_btn.setText("取消全选")
        else:
            self.select_all_btn.setText("全选")
            
    def _toggle_select_all(self):
        """切换全选状态"""
        selected_count = len(self.get_selected_job_ids())
        total_count = len(self.jobs_data)
        
        # 如果全部选中，则取消全选；否则全选
        select_all = selected_count != total_count
        
        for i in range(self.job_list.count()):
            item = self.job_list.item(i)
            widget = self.job_list.itemWidget(item)
            checkbox = widget.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(select_all)
                
    def get_selected_job_ids(self) -> List[str]:
        """获取选中的作业ID列表"""
        selected_ids = []
        
        for i in range(self.job_list.count()):
            item = self.job_list.item(i)
            widget = self.job_list.itemWidget(item)
            checkbox = widget.findChild(QCheckBox)
            
            if checkbox and checkbox.isChecked():
                job_id = checkbox.property("job_id")
                if job_id:
                    selected_ids.append(job_id)
                    
        return selected_ids
        
    def set_selected_job_ids(self, job_ids: List[str]):
        """设置选中的作业ID列表"""
        for i in range(self.job_list.count()):
            item = self.job_list.item(i)
            widget = self.job_list.itemWidget(item)
            checkbox = widget.findChild(QCheckBox)
            
            if checkbox:
                job_id = checkbox.property("job_id")
                checkbox.setChecked(job_id in job_ids)
                
        self._update_status()
        self._update_select_all_button()
        
    def clear_selection(self):
        """清除所有选择"""
        self.set_selected_job_ids([])