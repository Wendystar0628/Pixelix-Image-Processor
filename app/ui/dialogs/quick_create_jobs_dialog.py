"""
快速创建批处理作业对话框模块

提供一次性创建多个批处理作业的功能。
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QSpinBox
)


class QuickCreateJobsDialog(QDialog):
    """
    快速创建批处理作业对话框类，允许用户一次性创建多个作业。
    """
    
    def __init__(self, parent=None):
        """
        初始化快速创建作业对话框
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setWindowTitle("快速创建作业")
        self.setMinimumWidth(300)
        
        # 作业数量
        self.job_count = 1
        
        # 初始化UI
        self._init_ui()
        
    def _init_ui(self):
        """初始化对话框UI"""
        layout = QVBoxLayout(self)
        
        # 作业数量选择
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("创建作业数量:"))
        
        # 添加滑块
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(10)
        self.slider.setValue(1)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(1)
        count_layout.addWidget(self.slider)
        
        # 添加数字输入框
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(1)
        self.spinbox.setMaximum(10)
        self.spinbox.setValue(1)
        self.spinbox.setMinimumWidth(60)  # 设置最小宽度确保数字显示
        count_layout.addWidget(self.spinbox)
        
        # 连接滑块和数字输入框
        self.slider.valueChanged.connect(self.spinbox.setValue)
        self.spinbox.valueChanged.connect(self.slider.setValue)
        self.spinbox.valueChanged.connect(self._update_job_count)
        
        layout.addLayout(count_layout)
        
        # 添加提示标签
        self.info_label = QLabel('将创建 1 个名为"新建作业1"的作业')
        layout.addWidget(self.info_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        self.create_button = QPushButton("创建")
        self.create_button.clicked.connect(self.accept)
        self.create_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
    
    def _update_job_count(self, value):
        """
        更新作业数量和提示信息
        
        Args:
            value: 新的作业数量
        """
        self.job_count = value
        if value == 1:
            self.info_label.setText(f'将创建 {value} 个名为"新建作业1"的作业')
        else:
            self.info_label.setText(f'将创建 {value} 个名为"新建作业1"到"新建作业{value}"的作业')
    
    def get_job_count(self) -> int:
        """
        获取用户选择的作业数量
        
        Returns:
            int: 作业数量
        """
        return self.job_count