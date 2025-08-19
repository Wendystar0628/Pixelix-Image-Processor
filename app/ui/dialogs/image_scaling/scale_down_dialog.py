"""
图像缩小参数对话框
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QComboBox, QGroupBox, QLabel

from ..base_dialog import BaseOperationDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.scale_down_params import ScaleDownParams


class ScaleDownDialog(BaseOperationDialog):
    """
    图像缩小参数调整对话框
    
    允许用户调整缩小倍数和算法选择
    """
    
    # 参数变化信号
    params_changed = pyqtSignal(object)
    # 应用操作信号
    apply_operation = pyqtSignal(object)
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化图像缩小对话框"""
        super().__init__(parent, initial_params)
        
        self.processing_handler = processing_handler
        self._slider_events_connected = False
        
        self.setWindowTitle("图像缩小")
        self.setMinimumWidth(350)
        
        self._setup_ui()
        self._connect_signals()
        self.set_initial_parameters(self.initial_params)
        # 缩放对话框不需要滑块预览事件
    
    def _setup_ui(self):
        """创建UI布局"""
        main_layout = QVBoxLayout()
        
        # 缩放因子控制组
        scale_group, self.scale_slider, self.scale_label = self._create_slider_group(
            "缩小倍数", 10, 90, 50  # 0.1x到0.9x，默认0.5x
        )
        main_layout.addWidget(scale_group)
        
        # 算法选择控制组
        algorithm_group = self._create_algorithm_group()
        main_layout.addWidget(algorithm_group)
        
        # 大小信息显示
        size_group = self._create_size_info_group()
        main_layout.addWidget(size_group)
        
        # 创建按钮布局
        button_layout = self._create_button_layout()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def _create_slider_group(self, title: str, min_val: int, max_val: int, default_val: int):
        """创建滑块控制组"""
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QSlider, QLabel, QHBoxLayout
        
        group = QGroupBox(title)
        layout = QVBoxLayout()
        
        slider_layout = QHBoxLayout()
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTracking(True)
        
        label = QLabel(f"{default_val/100:.1f}x")
        label.setMinimumWidth(50)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        slider_layout.addWidget(slider)
        slider_layout.addWidget(label)
        
        layout.addLayout(slider_layout)
        group.setLayout(layout)
        
        return group, slider, label
    
    def _create_algorithm_group(self) -> QGroupBox:
        """创建算法选择控制组"""
        group = QGroupBox("缩小算法")
        layout = QVBoxLayout()
        
        self.algorithm_combo = QComboBox()
        algorithms = [
            ("最近邻下采样 (最快)", "nearest"),
            ("双线性下采样 (平衡)", "bilinear"),
            ("区域平均下采样 (保细节)", "area_average"),
            ("高斯下采样 (抗锯齿)", "gaussian"),
            ("抗锯齿下采样 (最佳质量)", "anti_alias")
        ]
        
        for name, value in algorithms:
            self.algorithm_combo.addItem(name, value)
        
        self.algorithm_combo.setCurrentIndex(2)  # 默认区域平均
        
        layout.addWidget(self.algorithm_combo)
        group.setLayout(layout)
        
        return group
    
    def _create_size_info_group(self) -> QGroupBox:
        """创建大小信息显示组"""
        group = QGroupBox("缩放信息")
        layout = QVBoxLayout()
        
        self.size_info_label = QLabel("预估缩小后大小: 计算中...")
        self.size_info_label.setWordWrap(True)
        
        layout.addWidget(self.size_info_label)
        group.setLayout(layout)
        
        return group
    
    def _create_button_layout(self):
        """创建按钮布局"""
        from PyQt6.QtWidgets import QHBoxLayout, QPushButton
        
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("重置")
        self.cancel_button = QPushButton("取消")
        self.ok_button = QPushButton("确定")
        self.ok_button.setDefault(True)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        return button_layout
    
    def _connect_signals(self):
        """连接信号和槽"""
        self.scale_slider.valueChanged.connect(self._update_scale_label)
        self.scale_slider.valueChanged.connect(self._emit_params_changed)
        self.algorithm_combo.currentIndexChanged.connect(self._emit_params_changed)
        self.algorithm_combo.currentIndexChanged.connect(self._update_size_info)
        
        self.reset_button.clicked.connect(self._reset_values)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self._apply_and_close)
    

    
    @pyqtSlot()
    def _update_scale_label(self):
        """更新缩放倍数标签"""
        value = self.scale_slider.value() / 100.0
        self.scale_label.setText(f"{value:.1f}x")
        self._update_size_info()
    
    def _update_size_info(self):
        """更新大小信息"""
        scale_factor = self.scale_slider.value() / 100.0
        algorithm = self.algorithm_combo.currentData()
        
        # 获取当前图像信息
        current_size_text = "未知"
        estimated_size_text = "计算中..."
        
        if self.processing_handler and hasattr(self.processing_handler, 'get_current_image_info'):
            image_info = self.processing_handler.get_current_image_info()
            if image_info:
                width, height, channels = image_info
                
                # 计算缩小后的像素数量
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                new_pixels = new_width * new_height
                
                # 估算文件大小 (假设每像素3字节用于RGB)
                bytes_per_pixel = 3 if channels >= 3 else 1
                estimated_bytes = new_pixels * bytes_per_pixel
                
                # 转换为合适的单位
                if estimated_bytes < 1024:
                    estimated_size_text = f"{estimated_bytes} B"
                elif estimated_bytes < 1024 * 1024:
                    estimated_size_text = f"{estimated_bytes / 1024:.1f} KB"
                else:
                    estimated_size_text = f"{estimated_bytes / (1024 * 1024):.1f} MB"
                
                current_size_text = f"{new_width} × {new_height} 像素"
        
        self.size_info_label.setText(
            f"预估缩小后尺寸: {current_size_text}\n"
            f"预估文件大小: {estimated_size_text}\n"
            f"算法: {self.algorithm_combo.currentText().split(' ')[0]}"
        )
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """发出参数变化信号"""
        params = ScaleDownParams(
            scale_factor=self.scale_slider.value() / 100.0,
            algorithm=self.algorithm_combo.currentData()
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.scale_slider.setValue(50)  # 0.5x
        self.algorithm_combo.setCurrentIndex(2)  # 区域平均
    
    @pyqtSlot()
    def _apply_and_close(self):
        """应用参数并关闭对话框"""
        params = self.get_final_parameters()
        self.apply_operation.emit(params)
        self.accept()
    
    def get_final_parameters(self) -> ScaleDownParams:
        """获取最终参数设置"""
        return ScaleDownParams(
            scale_factor=self.scale_slider.value() / 100.0,
            algorithm=self.algorithm_combo.currentData()
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置缩放因子
        scale_factor = params.get('scale_factor', 0.5)
        self.scale_slider.setValue(int(scale_factor * 100))
        
        # 设置算法
        algorithm = params.get('algorithm', 'area_average')
        for i in range(self.algorithm_combo.count()):
            if self.algorithm_combo.itemData(i) == algorithm:
                self.algorithm_combo.setCurrentIndex(i)
                break