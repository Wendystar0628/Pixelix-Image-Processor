import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget

# 设置中文字体支持
matplotlib.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

from app.core import ImageAnalysisEngine


class HueSaturationWidget(QWidget):
    """
    一个用于显示图像的色相和饱和度直方图的可嵌入控件。
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建一个 Matplotlib 图形画布
        self.canvas = FigureCanvas(Figure(figsize=(5, 6)))
        layout.addWidget(self.canvas)

        # 初始化两个子图，上面是色相（极坐标），下面是饱和度（直角坐标）
        self.ax_hue = self.canvas.figure.add_subplot(211, projection="polar")
        self.ax_saturation = self.canvas.figure.add_subplot(212)
        
        self._setup_axes()
        
        # 调整布局
        self.canvas.figure.tight_layout()
        self.canvas.draw()
        
        # 存储最新的分析数据
        self.latest_analysis_data = {}

    def _setup_axes(self):
        """
        设置坐标轴属性。
        """
        # 配置色相极坐标
        self.ax_hue.set_title("Hue Distribution", y=1.05)
        # 正确的方法隐藏半径轴刻度
        self.ax_hue.set_yticks([])  # 隐藏半径轴刻度
        self.ax_hue.set_xticks(
            [0, np.pi/3, 2*np.pi/3, np.pi, 4*np.pi/3, 5*np.pi/3]
        )  # 60度间隔的角度刻度
        self.ax_hue.set_xticklabels(["0°", "60°", "120°", "180°", "240°", "300°"])
        self.ax_hue.grid(True, linestyle=":", alpha=0.6)

        # 配置饱和度条形图
        self.ax_saturation.set_title("Saturation Distribution")
        self.ax_saturation.set_xlabel("Saturation (0-255)")
        self.ax_saturation.set_ylabel("Frequency")
        self.ax_saturation.grid(True, linestyle=":", alpha=0.6)

    def update_histograms(self, image: np.ndarray | None) -> None:
        """
        根据输入图像更新色相和饱和度直方图。
        
        注意: 此方法在主线程中计算直方图数据，可能会导致UI阻塞。
        推荐使用update_histograms_with_data方法，它接受预先计算好的直方图数据。

        Args:
            image: 输入的图像 (NumPy 数组) 或 None。
        """
        self.ax_hue.clear()
        self.ax_saturation.clear()
        self._setup_axes()

        if image is None:
            self.canvas.figure.suptitle("No image loaded", y=0.98)
            self.canvas.draw()
            return

        hue_hist, sat_hist = ImageAnalysisEngine.get_hue_saturation_histograms(image)
        self._plot_histograms(hue_hist, sat_hist)
        
    def update_histograms_with_data(self, results: dict):
        """
        使用预先计算好的色相和饱和度直方图数据更新显示，并存储原始数据。
        
        Args:
            results: 包含分析结果的字典
        """
        self.ax_hue.clear()
        self.ax_saturation.clear()
        self._setup_axes()
        
        # 存储完整的分析数据
        self.latest_analysis_data = results.copy()
        
        # 从结果字典中提取所需的数据
        if 'hue_histogram' in results and 'sat_histogram' in results:
            hue_hist = results['hue_histogram']
            sat_hist = results['sat_histogram']
            
            self._plot_histograms(hue_hist, sat_hist)
        else:
            self.canvas.figure.suptitle("No histogram data", y=0.98)
            self.canvas.draw()
        
    def _plot_histograms(self, hue_hist, sat_hist):
        """
        绘制色相和饱和度直方图。
        
        Args:
            hue_hist: 色相直方图数据
            sat_hist: 饱和度直方图数据
        """
        if hue_hist is not None and sat_hist is not None:
            self.canvas.figure.suptitle("")  # 清除旧标题

            # 绘制色相直方图 (极坐标)
            hue_bins = hue_hist.shape[0]
            # OpenCV的H范围是0-179，我们需要映射到0-358度 (因为np.pi是180度)
            theta = np.linspace(0, 2 * np.pi, hue_bins, endpoint=False)
            radii = hue_hist.flatten()
            width = (2 * np.pi) / hue_bins

            # 创建颜色映射，使每个条形都显示其对应的颜色
            colors = plt.get_cmap("hsv")(np.linspace(0, 1, hue_bins))

            # 只有当有数据时才绘制
            if np.sum(radii) > 0:
                self.ax_hue.bar(
                    theta, radii, width=width, bottom=0.0, color=colors, alpha=0.8
                )
                # 设置半径轴的范围，让数据更好地显示
                max_radius = np.max(radii)
                if max_radius > 0:
                    self.ax_hue.set_ylim(0, max_radius * 1.1)
            else:
                # 如果没有色相数据，显示提示信息
                self.ax_hue.text(
                    0, 0, "没有色相数据", ha="center", va="center", fontsize=12
                )

            # 绘制饱和度直方图
            sat_bins = sat_hist.shape[0]
            sat_values = sat_hist.flatten()
            x_axis = np.arange(sat_bins)
            
            # 创建颜色渐变，从灰色到蓝色
            sat_colors = plt.get_cmap("Blues")(np.linspace(0.3, 1.0, sat_bins))
            
            self.ax_saturation.bar(x_axis, sat_values, color=sat_colors, alpha=0.8)
            self.ax_saturation.set_xlim(-1, sat_bins)
            
            # 只有当 x 轴范围足够宽时才需要设置刻度
            if sat_bins > 10:
                # 设置 x 轴刻度，每隔一定间隔显示
                tick_interval = sat_bins // 5  # 大约显示5个刻度
                self.ax_saturation.set_xticks(np.arange(0, sat_bins, tick_interval))
                # 计算每个刻度对应的实际饱和度值
                tick_labels = [f"{int(i / sat_bins * 255)}" for i in np.arange(0, sat_bins, tick_interval)]
                self.ax_saturation.set_xticklabels(tick_labels)

        self.canvas.figure.tight_layout()
        self.canvas.draw()
