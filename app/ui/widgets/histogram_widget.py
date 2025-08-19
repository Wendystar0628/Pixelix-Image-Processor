import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from app.core import ImageAnalysisEngine


class HistogramWidget(QWidget):
    """
    一个用于显示图像直方图的可嵌入控件。
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建一个 Matplotlib 图形画布
        self.canvas = FigureCanvas(Figure(figsize=(5, 4)))
        layout.addWidget(self.canvas)

        # 初始化一个空的图形
        self.ax = self.canvas.figure.subplots()
        self.ax.set_title("Histogram")
        self.ax.set_xlabel("Pixel Value")
        self.ax.set_ylabel("Frequency")
        self.ax.grid(True)
        self.canvas.draw()

    def update_histogram(self, image: np.ndarray | None):
        """
        计算并绘制直方图。
        
        注意: 此方法在主线程中计算直方图，可能会导致UI阻塞。
        推荐使用update_histogram_with_data方法，它接受预先计算好的直方图数据。
        """
        # 清除旧的图形
        self.ax.clear()

        if image is None:
            self.ax.set_title("No image loaded")
            self.canvas.draw()
            return

        hist_data = ImageAnalysisEngine.calculate_histogram(image)
        self._plot_histogram(hist_data)

    def update_histogram_with_data(self, hist_data):
        """
        使用预先计算好的直方图数据绘制直方图。
        
        Args:
            hist_data: 预先计算好的直方图数据，格式与ImageAnalysisEngine.calculate_histogram返回值相同
        """
        # 清除旧的图形
        self.ax.clear()
        
        if hist_data is None or len(hist_data) == 0:
            self.ax.set_title("No histogram data")
            self.canvas.draw()
            return
            
        self._plot_histogram(hist_data)
        
    def _plot_histogram(self, hist_data):
        """
        绘制直方图数据。
        
        Args:
            hist_data: 直方图数据，格式与ImageAnalysisEngine.calculate_histogram返回值相同
        """
        if len(hist_data) == 1:  # 灰度图
            self.ax.plot(hist_data[0], color="gray")
            self.ax.set_title("Grayscale Histogram")
        elif len(hist_data) == 3:  # 彩色图
            colors = ("b", "g", "r")
            for i, hist in enumerate(hist_data):
                self.ax.plot(hist, color=colors[i])
            self.ax.set_title("Color Histogram")

        self.ax.set_xlim((0, 256))
        self.ax.set_xlabel("Pixel Value")
        self.ax.set_ylabel("Frequency")
        self.ax.grid(True)
        self.canvas.draw()


