import cv2
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from app.core import ImageAnalysisEngine


class LumaWaveformWidget(QWidget):
    """一个用于显示亮度波形图的可嵌入控件。"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建一个 Matplotlib 图形画布
        self.canvas = FigureCanvas(Figure(figsize=(5, 4)))
        layout.addWidget(self.canvas)

        # 初始化一个空的图形
        self.ax = self.canvas.figure.subplots()
        self._setup_axes()
        self.canvas.draw()

    def _setup_axes(self):
        """配置坐标轴的基本属性。"""
        self.ax.set_title("Luma Waveform")
        self.ax.set_ylabel("Luminance")
        self.ax.set_ylim(0, 255)
        self.ax.set_yticks([0, 64, 128, 192, 255])
        self.ax.grid(True, linestyle=":", alpha=0.6)

    def update_waveform(self, image: np.ndarray | None):
        """
        计算并绘制亮度波形图。
        
        注意: 此方法在主线程中计算波形图数据，可能会导致UI阻塞。
        推荐使用update_waveform_with_data方法，它接受预先计算好的波形数据。
        
        Args:
            image: 输入图像数据(NumPy数组)或None
        """
        self.ax.clear()
        self._setup_axes()

        if image is None:
            self.ax.set_title("No image loaded")
            self.canvas.draw()
            return

        if image.ndim == 3:
            # 使用 cv2 转换为灰度图
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image

        parade_data = ImageAnalysisEngine.get_rgb_parade_efficient(gray_image)
        self._plot_waveform_data(parade_data)
        
    def update_waveform_with_data(self, waveform_data):
        """
        使用预先计算好的波形数据绘制亮度波形图。
        
        Args:
            waveform_data: 预先计算好的亮度波形数据，通常是RGB波形数据的第一个通道
        """
        self.ax.clear()
        self._setup_axes()
        
        if waveform_data is None:
            self.ax.set_title("No waveform data")
            self.canvas.draw()
            return
            
        # 创建一个格式正确的parade_data，使其与_plot_waveform_data方法兼容
        parade_data = [waveform_data]
        self._plot_waveform_data(parade_data)

    def _plot_waveform_data(self, parade_data):
        """
        绘制亮度波形图数据。
        
        Args:
            parade_data: 波形图数据，格式与ImageAnalysisEngine.get_rgb_parade_efficient返回值相同
        """
        if parade_data:
            waveform = parade_data[0]
            log_data = np.log1p(waveform)
            self.ax.imshow(
                log_data,
                aspect="auto",
                cmap="viridis",
                origin="lower",
                extent=(0, waveform.shape[1], 0, 255),
            )
        else:
            self.ax.set_title("Could not generate waveform")

        self.canvas.figure.tight_layout()
        self.canvas.draw()
