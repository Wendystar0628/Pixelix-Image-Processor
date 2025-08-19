"""
组合分析控件模块

将直方图和亮度波形组合在一个控件中，方便同时查看这两种分析数据。
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from .histogram_widget import HistogramWidget
from .luma_waveform_widget import LumaWaveformWidget


class CombinedAnalysisWidget(QWidget):
    """
    组合分析控件，包含直方图和亮度波形
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建直方图和亮度波形控件
        self.histogram_widget = HistogramWidget()
        self.luma_waveform_widget = LumaWaveformWidget()

        # 添加到布局中
        layout.addWidget(self.histogram_widget)
        layout.addWidget(self.luma_waveform_widget)
        
        # 存储最新的分析数据
        self.latest_analysis_data = {}

    def update_views(self, results: dict):
        """
        一次性更新直方图和亮度波形，并存储原始数据
        
        Args:
            results: 包含分析结果的字典
        """
        # 存储完整的分析数据
        self.latest_analysis_data = results.copy()
        
        # 从结果字典中提取所需的数据
        if 'histogram' in results and 'rgb_parade' in results:
            # 控件自己解析结果
            histogram_data = results['histogram']
            waveform_data = results['rgb_parade'][0]  # 使用第一个通道(B)作为亮度波形
            
            # 更新子控件
            self.histogram_widget.update_histogram_with_data(histogram_data)
            self.luma_waveform_widget.update_waveform_with_data(waveform_data)

    def clear_views(self):
        """清空所有视图和存储的数据"""
        self.histogram_widget.update_histogram(None)
        self.luma_waveform_widget.update_waveform(None)
        self.latest_analysis_data = {} 