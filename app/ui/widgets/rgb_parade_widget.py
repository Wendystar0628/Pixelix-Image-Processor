import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from app.core import ImageAnalysisEngine


class RGBParadeWidget(QWidget):
    """
    一个用于显示图像RGB分量波形图的可嵌入控件。
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建一个 Matplotlib 图形画布，包含3个子图
        self.canvas = FigureCanvas(Figure(figsize=(5, 6)))
        layout.addWidget(self.canvas)

        # 初始化三个垂直排列的子图
        (self.ax_r, self.ax_g, self.ax_b) = self.canvas.figure.subplots(
            3, 1, sharex=True
        )

        self.canvas.figure.suptitle("RGB Parade")
        self._setup_axes(self.ax_r, "Red", "Reds")
        self._setup_axes(self.ax_g, "Green", "Greens")
        self._setup_axes(self.ax_b, "Blue", "Blues")

        # 调整布局以避免标题重叠
        self.canvas.figure.tight_layout(rect=(0, 0.03, 1, 0.95))
        self.canvas.draw()

        # 存储最新的分析数据
        self.latest_analysis_data = {}

    def _setup_axes(self, ax, title: str, cmap: str):
        """配置子图的基本属性。"""
        ax.set_ylabel(title)
        ax.set_ylim(0, 255)
        ax.set_yticks([0, 64, 128, 192, 255])
        ax.grid(True, linestyle=":", alpha=0.6)

    def update_parade(self, analysis_results: dict):
        """
        使用预先计算好的分析结果更新RGB波形图。
        此方法遵循高内聚原则，仅负责展示数据。

        Args:
            analysis_results: 包含分析结果的字典。
                              预期键: 'rgb_parade'
        """
        # 存储最新的完整分析数据，以备将来使用（如导出）
        self.latest_analysis_data = analysis_results.copy()
        
        # 从结果字典中提取所需的数据
        parade_data = analysis_results.get('rgb_parade')

        # 清除旧的图形
        self._clear_axes()

        if parade_data is None or len(parade_data) == 0:
            self.canvas.figure.suptitle("No Parade Data")
            self.canvas.draw()
            return
            
        self._plot_parade_data(parade_data)
        
    def clear_view(self):
        """
        清空视图并显示无图像状态。
        """
        self._clear_axes()
        self.canvas.figure.suptitle("No Image Loaded")
        self.canvas.draw()
        self.latest_analysis_data = {}  # 清空存储的数据

    def _clear_axes(self):
        """
        一个辅助方法，用于清除和重置所有绘图轴。
        """
        # 清除旧的图形
        self.ax_r.clear()
        self.ax_g.clear()
        self.ax_b.clear()

        # 重新应用基本配置
        self._setup_axes(self.ax_r, "Red", "Reds")
        self._setup_axes(self.ax_g, "Green", "Greens")
        self._setup_axes(self.ax_b, "Blue", "Blues")

        # 确保所有轴都可见（每次更新时重置）
        self.ax_r.set_visible(True)
        self.ax_g.set_visible(True)
        self.ax_b.set_visible(True)

    def _plot_parade_data(self, parade_data):
        """
        绘制波形图数据。
        
        Args:
            parade_data: 波形图数据，格式与ImageAnalysisEngine.get_rgb_parade_efficient返回值相同
        """
        if len(parade_data) == 3:  # 彩色图
            self.canvas.figure.suptitle("RGB Parade")
            # OpenCV的split返回的是B, G, R，我们需要正确映射到R, G, B显示
            cmaps = ["Reds", "Greens", "Blues"]
            axes = [self.ax_r, self.ax_g, self.ax_b]
            # OpenCV's split is B, G, R. We want to display R, G, B.
            data_to_plot = [parade_data[2], parade_data[1], parade_data[0]]  # R, G, B

            # 确保所有轴都可见
            self.ax_r.set_visible(True)
            self.ax_g.set_visible(True)
            self.ax_b.set_visible(True)

            for ax, data, cmap in zip(axes, data_to_plot, cmaps):
                # 对数据进行对数缩放以增强低强度值的可见性
                log_data = np.log1p(data)
                ax.imshow(
                    log_data,
                    aspect="auto",
                    cmap=cmap,
                    origin="lower",
                    extent=[0, data.shape[1], 0, 255],
                )

        elif len(parade_data) == 1:  # 灰度图
            self.canvas.figure.suptitle("Luma Waveform")
            log_data = np.log1p(parade_data[0])
            # 隐藏红色和蓝色轴，只显示绿色轴用于灰度图
            self.ax_r.set_visible(False)
            self.ax_b.set_visible(False)
            self.ax_g.set_visible(True)
            self.ax_g.imshow(
                log_data,
                aspect="auto",
                cmap="viridis",
                origin="lower",
                extent=[0, parade_data[0].shape[1], 0, 255],
            )

        else:
            self.canvas.figure.suptitle("Unsupported Format")

        self.canvas.figure.tight_layout(rect=(0, 0.03, 1, 0.95))
        self.canvas.draw()
