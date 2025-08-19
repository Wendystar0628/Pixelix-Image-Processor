"""
曲线编辑控件模块
提供交互式曲线编辑功能
"""

import math
from typing import List, Tuple, Optional

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QCursor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class CurveEditWidget(QWidget):
    """
    曲线编辑控件，支持添加、移动、删除控制点。
    提供直观的曲线编辑界面。
    """

    # 定义信号
    curve_changed = pyqtSignal(list)  # 发出曲线控制点变化信号
    drag_started = pyqtSignal()      # 拖动开始信号，用于触发代理模式
    drag_finished = pyqtSignal()     # 拖动结束信号，用于结束代理模式

    def __init__(self, parent=None):
        """
        初始化曲线编辑控件。
        
        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.setMouseTracking(True)

        # 曲线控制点 [(x, y), ...] 范围 0-255
        self._control_points = [(0, 0), (255, 255)]

        # 鼠标交互状态
        self._dragging_point = -1  # 正在拖拽的点索引，-1表示无
        self._hover_point = -1  # 鼠标悬停的点索引

        # 绘制参数
        self._margin = 20
        self._grid_color = QColor(200, 200, 200)
        self._curve_color = QColor(50, 50, 50)
        self._point_color = QColor(100, 150, 255)
        self._point_hover_color = QColor(150, 200, 255)

    def set_curve_points(self, points: List[Tuple[int, int]]):
        """
        设置曲线控制点。
        
        Args:
            points: 控制点列表，每个点是(x,y)坐标元组
        """
        if not points:
            return
            
        self._control_points = points.copy()
        self.update()
        self.curve_changed.emit(self._control_points)

    def get_curve_points(self) -> List[Tuple[int, int]]:
        """
        获取当前曲线控制点。
        
        Returns:
            控制点列表的副本
        """
        return self._control_points.copy()

    def _coord_to_pixel(self, coord_x: int, coord_y: int) -> Tuple[int, int]:
        """
        将0-255坐标转换为像素坐标。
        
        Args:
            coord_x: X坐标(0-255)
            coord_y: Y坐标(0-255)
            
        Returns:
            (pixel_x, pixel_y) 像素坐标
        """
        width = self.width() - 2 * self._margin
        height = self.height() - 2 * self._margin

        pixel_x = self._margin + int(coord_x * width / 255)
        pixel_y = self.height() - self._margin - int(coord_y * height / 255)

        return pixel_x, pixel_y

    def _pixel_to_coord(self, pixel_x: int, pixel_y: int) -> Tuple[int, int]:
        """
        将像素坐标转换为0-255坐标。
        
        Args:
            pixel_x: 像素X坐标
            pixel_y: 像素Y坐标
            
        Returns:
            (coord_x, coord_y) 0-255范围内的坐标
        """
        width = self.width() - 2 * self._margin
        height = self.height() - 2 * self._margin

        coord_x = int((pixel_x - self._margin) * 255 / width)
        coord_y = int((self.height() - self._margin - pixel_y) * 255 / height)

        # 限制在有效范围内
        coord_x = max(0, min(255, coord_x))
        coord_y = max(0, min(255, coord_y))

        return coord_x, coord_y

    def _find_point_at_pixel(
        self, pixel_x: int, pixel_y: int, tolerance: int = 8
    ) -> int:
        """
        在指定像素位置查找控制点，返回点索引或-1。
        
        Args:
            pixel_x: 像素X坐标
            pixel_y: 像素Y坐标
            tolerance: 匹配的容差范围(像素)
            
        Returns:
            点索引，如果未找到则返回-1
        """
        for i, (coord_x, coord_y) in enumerate(self._control_points):
            px, py = self._coord_to_pixel(coord_x, coord_y)
            distance = math.sqrt((px - pixel_x) ** 2 + (py - pixel_y) ** 2)
            if distance <= tolerance:
                return i
        return -1

    def paintEvent(self, event):
        """绘制曲线编辑器。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制背景
        painter.fillRect(self.rect(), QColor(250, 250, 250))

        # 绘制网格
        self._draw_grid(painter)

        # 绘制曲线
        self._draw_curve(painter)

        # 绘制控制点
        self._draw_control_points(painter)

        # 绘制坐标轴标签
        self._draw_labels(painter)

    def _draw_grid(self, painter: QPainter):
        """
        绘制网格。
        
        Args:
            painter: QPainter实例
        """
        painter.setPen(QPen(self._grid_color, 1))

        # 垂直网格线
        for i in range(5):
            coord_x = i * 64  # 0, 64, 128, 192, 255
            pixel_x, _ = self._coord_to_pixel(coord_x, 0)
            painter.drawLine(pixel_x, self._margin, pixel_x, self.height() - self._margin)

        # 水平网格线
        for i in range(5):
            coord_y = i * 64
            _, pixel_y = self._coord_to_pixel(0, coord_y)
            painter.drawLine(self._margin, pixel_y, self.width() - self._margin, pixel_y)

        # 对角线参考线
        painter.setPen(QPen(self._grid_color, 1, Qt.PenStyle.DashLine))
        start_x, start_y = self._coord_to_pixel(0, 0)
        end_x, end_y = self._coord_to_pixel(255, 255)
        painter.drawLine(start_x, start_y, end_x, end_y)

    def _draw_curve(self, painter: QPainter):
        """
        绘制曲线。
        
        Args:
            painter: QPainter实例
        """
        if len(self._control_points) < 2:
            return

        painter.setPen(QPen(self._curve_color, 2))

        # 使用插值绘制平滑曲线
        prev_pixel = None
        for coord_x in range(256):
            # 计算当前x对应的y值
            coord_y = self._interpolate_y(coord_x)
            pixel_x, pixel_y = self._coord_to_pixel(coord_x, coord_y)

            if prev_pixel is not None:
                painter.drawLine(prev_pixel[0], prev_pixel[1], pixel_x, pixel_y)
            prev_pixel = (pixel_x, pixel_y)

    def _interpolate_y(self, x: int) -> int:
        """
        插值计算指定x坐标对应的y值。
        
        Args:
            x: X坐标(0-255)
            
        Returns:
            对应的Y坐标值(0-255)
        """
        # 排序控制点
        sorted_points = sorted(self._control_points, key=lambda p: p[0])

        # 如果x在端点外，返回端点值
        if x <= sorted_points[0][0]:
            return sorted_points[0][1]
        if x >= sorted_points[-1][0]:
            return sorted_points[-1][1]

        # 找到x所在的区间
        for i in range(len(sorted_points) - 1):
            x1, y1 = sorted_points[i]
            x2, y2 = sorted_points[i + 1]

            if x1 <= x <= x2:
                # 线性插值
                if x2 == x1:
                    return y1
                t = (x - x1) / (x2 - x1)
                return int(y1 + t * (y2 - y1))

        return 128  # 默认值

    def _draw_control_points(self, painter: QPainter):
        """
        绘制控制点。
        
        Args:
            painter: QPainter实例
        """
        for i, (coord_x, coord_y) in enumerate(self._control_points):
            pixel_x, pixel_y = self._coord_to_pixel(coord_x, coord_y)

            # 选择颜色
            if i == self._hover_point:
                color = self._point_hover_color
                radius = 6
            else:
                color = self._point_color
                radius = 5

            painter.setPen(QPen(color.darker(), 2))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(
                pixel_x - radius, pixel_y - radius, radius * 2, radius * 2
            )

    def _draw_labels(self, painter: QPainter):
        """
        绘制坐标轴标签。
        
        Args:
            painter: QPainter实例
        """
        painter.setPen(QPen(QColor(100, 100, 100)))
        painter.setFont(QFont("Arial", 8))

        # X轴标签
        for i in range(5):
            coord_x = i * 64
            pixel_x, _ = self._coord_to_pixel(coord_x, 0)
            painter.drawText(pixel_x - 10, self.height() - 5, str(coord_x))

        # Y轴标签
        for i in range(5):
            coord_y = i * 64
            _, pixel_y = self._coord_to_pixel(0, coord_y)
            painter.drawText(5, pixel_y + 5, str(coord_y))

    def mousePressEvent(self, event):
        """
        鼠标按下事件。
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # 查找点击的控制点
            point_index = self._find_point_at_pixel(event.pos().x(), event.pos().y())

            if point_index >= 0:
                # 开始拖拽现有点
                self._dragging_point = point_index
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                self.drag_started.emit() # 发出拖动开始信号
            else:
                # 添加新控制点（除非是端点）
                coord_x, coord_y = self._pixel_to_coord(
                    event.pos().x(), event.pos().y()
                )
                if coord_x > 0 and coord_x < 255:  # 不能在端点添加
                    self._control_points.append((coord_x, coord_y))
                    self._control_points.sort(key=lambda p: p[0])
                    self._dragging_point = self._control_points.index((coord_x, coord_y))
                    self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                    self.drag_started.emit() # 发出拖动开始信号
                    self.update()
                    self.curve_changed.emit(self._control_points)

        elif event.button() == Qt.MouseButton.RightButton:
            # 右键删除控制点（除了端点）
            point_index = self._find_point_at_pixel(event.pos().x(), event.pos().y())
            if (
                point_index > 0
                and point_index < len(self._control_points) - 1
                and len(self._control_points) > 2
            ):
                del self._control_points[point_index]
                self.update()
                self.curve_changed.emit(self._control_points)

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件。
        
        Args:
            event: 鼠标事件
        """
        # 更新悬停点
        point_index = self._find_point_at_pixel(event.pos().x(), event.pos().y())
        if self._dragging_point < 0 and point_index != self._hover_point:
            self._hover_point = point_index
            self.update()

        # 拖拽控制点
        if self._dragging_point >= 0:
            coord_x, coord_y = self._pixel_to_coord(event.pos().x(), event.pos().y())

            # 确保端点只在垂直方向移动
            if self._dragging_point == 0:
                coord_x = 0
            elif self._dragging_point == len(self._control_points) - 1:
                coord_x = 255

            # 更新点的位置
            self._control_points[self._dragging_point] = (coord_x, coord_y)

            # 排序以防拖拽越过其他点
            self._control_points.sort(key=lambda p: p[0])
            self._dragging_point = self._control_points.index((coord_x, coord_y))

            self.update()
            self.curve_changed.emit(self._control_points)
        else:
            # 更新鼠标光标
            if self._hover_point >= 0:
                self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件。
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging_point = -1
            self.drag_finished.emit() # 发出拖动结束信号
            if self._hover_point >= 0:
                self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor)) 