"""
图像压缩参数对话框
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QComboBox, QGroupBox, QLabel

from ..base_dialog import BaseOperationDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.compression_params import CompressionParams


class CompressionDialog(BaseOperationDialog):
    """
    图像压缩参数调整对话框
    
    允许用户调整压缩质量、格式和算法选择
    """
    
    # 参数变化信号
    params_changed = pyqtSignal(object)
    # 应用操作信号
    apply_operation = pyqtSignal(object)
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化图像压缩对话框"""
        super().__init__(parent, initial_params)
        
        self.processing_handler = processing_handler
        self._slider_events_connected = False
        
        self.setWindowTitle("图像压缩")
        self.setMinimumWidth(350)
        
        self._setup_ui()
        self._connect_signals()
        self.set_initial_parameters(self.initial_params)
        # 压缩对话框不需要滑块预览事件
    
    def _setup_ui(self):
        """创建UI布局"""
        main_layout = QVBoxLayout()
        
        # 质量控制组
        quality_group, self.quality_slider, self.quality_label = self._create_slider_group(
            "压缩质量", 10, 100, 85  # 10%到100%，默认85%
        )
        main_layout.addWidget(quality_group)
        
        # 算法选择控制组
        algorithm_group = self._create_algorithm_group()
        main_layout.addWidget(algorithm_group)
        
        # 预估大小显示
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
        
        label = QLabel(f"{default_val}%")
        label.setMinimumWidth(40)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        slider_layout.addWidget(slider)
        slider_layout.addWidget(label)
        
        layout.addLayout(slider_layout)
        group.setLayout(layout)
        
        return group, slider, label
    
    def _create_algorithm_group(self) -> QGroupBox:
        """创建算法选择控制组"""
        group = QGroupBox("压缩算法")
        layout = QVBoxLayout()
        
        self.algorithm_combo = QComboBox()
        algorithms = [
            ("JPEG压缩 (通用)", "jpeg"),
            ("PNG压缩 (无损)", "png"),
            ("WebP压缩 (现代)", "webp"),
            ("颜色量化 (减色)", "color_quantization"),
            ("智能优化 (目标大小)", "lossy_optimization")
        ]
        
        for name, value in algorithms:
            self.algorithm_combo.addItem(name, value)
        
        self.algorithm_combo.setCurrentIndex(0)  # 默认JPEG
        
        layout.addWidget(self.algorithm_combo)
        group.setLayout(layout)
        
        return group
    
    def _create_size_info_group(self) -> QGroupBox:
        """创建大小信息显示组"""
        group = QGroupBox("压缩信息")
        layout = QVBoxLayout()
        
        self.size_info_label = QLabel("预估压缩后大小: 计算中...")
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
        self.quality_slider.valueChanged.connect(self._update_quality_label)
        self.quality_slider.valueChanged.connect(self._emit_params_changed)
        self.algorithm_combo.currentIndexChanged.connect(self._emit_params_changed)
        self.algorithm_combo.currentIndexChanged.connect(self._update_size_info)
        
        self.reset_button.clicked.connect(self._reset_values)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self._apply_and_close)
    

    
    @pyqtSlot()
    def _update_quality_label(self):
        """更新质量标签"""
        value = self.quality_slider.value()
        self.quality_label.setText(f"{value}%")
        self._update_size_info()
    
    def _update_size_info(self):
        """更新大小信息"""
        quality = self.quality_slider.value()
        algorithm = self.algorithm_combo.currentData()
        
        # 获取当前图像信息
        estimated_size_text = "计算中..."
        
        if self.processing_handler and hasattr(self.processing_handler, 'get_current_image_info'):
            image_info = self.processing_handler.get_current_image_info()
            if image_info:
                width, height, channels = image_info
                total_pixels = width * height
                
                # 根据算法和质量估算压缩比
                if algorithm == "jpeg":
                    # JPEG压缩比随质量变化
                    compression_ratio = 0.05 + (quality / 100.0) * 0.25  # 5%-30%
                elif algorithm == "png":
                    # PNG无损压缩，比率相对固定
                    compression_ratio = 0.6  # 约60%
                elif algorithm == "webp":
                    # WebP更高效
                    compression_ratio = 0.03 + (quality / 100.0) * 0.20  # 3%-23%
                elif algorithm == "color_quantization":
                    # 颜色量化压缩
                    compression_ratio = 0.3  # 约30%
                else:  # lossy_optimization
                    # 智能优化压缩
                    compression_ratio = 0.15  # 约15%
                
                # 估算文件大小
                bytes_per_pixel = 3 if channels >= 3 else 1
                uncompressed_bytes = total_pixels * bytes_per_pixel
                estimated_bytes = int(uncompressed_bytes * compression_ratio)
                
                # 转换为合适的单位
                if estimated_bytes < 1024:
                    estimated_size_text = f"{estimated_bytes} B"
                elif estimated_bytes < 1024 * 1024:
                    estimated_size_text = f"{estimated_bytes / 1024:.1f} KB"
                else:
                    estimated_size_text = f"{estimated_bytes / (1024 * 1024):.1f} MB"
        
        self.size_info_label.setText(
            f"预估压缩后大小: {estimated_size_text}\n"
            f"压缩比: 约 {quality}% 质量\n"
            f"算法: {self.algorithm_combo.currentText().split(' ')[0]}"
        )
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """发出参数变化信号"""
        params = CompressionParams(
            quality=self.quality_slider.value(),
            algorithm=self.algorithm_combo.currentData()
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.quality_slider.setValue(85)
        self.algorithm_combo.setCurrentIndex(0)  # JPEG
    
    @pyqtSlot()
    def _apply_and_close(self):
        """应用参数并关闭对话框"""
        params = self.get_final_parameters()
        self.apply_operation.emit(params)
        self.accept()
    
    def get_final_parameters(self) -> CompressionParams:
        """获取最终参数设置"""
        return CompressionParams(
            quality=self.quality_slider.value(),
            algorithm=self.algorithm_combo.currentData()
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置质量
        quality = params.get('quality', 85)
        self.quality_slider.setValue(quality)
        
        # 设置算法
        algorithm = params.get('algorithm', 'jpeg')
        for i in range(self.algorithm_combo.count()):
            if self.algorithm_combo.itemData(i) == algorithm:
                self.algorithm_combo.setCurrentIndex(i)
                break