from enum import Enum, auto

import numpy as np
from PyQt6.QtCore import QPoint, QPointF, QRect, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QPainter,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import QLabel, QScrollArea, QSizePolicy


class InteractionMode(Enum):
    NONE = auto()
    RECT_SELECTION = auto()
    LASSO_SELECTION = auto()


class InteractiveImageLabel(QLabel):
    """
    一个自定义的 QLabel，用于显示图像并处理复杂的鼠标交互。
    这是所有需要用户在图像上直接操作的功能（如选区）的基础。
    """

    selection_finished = pyqtSignal(QRect)
    lasso_finished = pyqtSignal(list)  # 套索完成信号，传递点列表
    request_load_image = pyqtSignal(str)  # 请求加载图像信号，传递文件路径

    def __init__(self, parent=None):
        """
        初始化交互式图像标签。
        """
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(1, 1)

        # *** 性能优化：设置大小策略 ***
        # 告诉QLabel，它的首选大小应该与它的内容（pixmap）一样大。
        # 这样，当pixmap改变时，它的sizeHint会随之改变，
        # 其父容器QScrollArea会自动检测到并调整滚动条，而无需我们手动resize。
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

        # 交互状态
        self.interaction_mode = InteractionMode.NONE
        self.interaction_in_progress = False
        self.interaction_rect = QRect()
        self.start_point = QPoint()
        self.end_point = QPoint()

        # 套索相关状态
        self.lasso_points = []  # 存储套索路径的点列表

        # 蚂蚁线动画
        self.ant_timer = QTimer(self)
        self.ant_timer.timeout.connect(self.update)  # 定时器触发重绘
        self.ant_offset = 0

        self.setMouseTracking(True)

        # 视图控制相关
        self.zoom_factor = 1.0  # 视图缩放因子
        self.pan_offset = QPointF(0, 0)  # 视图平移偏移量

        # 修饰键状态
        self.ctrl_pressed = False
        self.shift_pressed = False

        # 图像拖动状态
        self.is_panning = False
        self.pan_start_point = QPoint()
        self.scroll_area = None  # 将在父容器中设置

        # 启用键盘焦点
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_interaction_mode(self, mode: InteractionMode):
        """
        设置当前的交互模式。

        Args:
            mode: InteractionMode 枚举成员。
        """
        self.interaction_mode = mode

        # 清除旧的图形
        self.interaction_rect = QRect()
        self.lasso_points = []  # 清除套索路径

        self.update()

        if mode == InteractionMode.RECT_SELECTION:
            self.setCursor(Qt.CursorShape.CrossCursor)
            if not self.ant_timer.isActive():
                self.ant_timer.start(100)  # 每100ms更新一次
        elif mode == InteractionMode.LASSO_SELECTION:
            self.setCursor(Qt.CursorShape.CrossCursor)
            if not self.ant_timer.isActive():
                self.ant_timer.start(100)  # 每100ms更新一次
        else:  # InteractionMode.NONE
            self.unsetCursor()
            if self.ant_timer.isActive():
                self.ant_timer.stop()

    def set_image(self, image_qpixmap: QPixmap | None):
        """
        设置要显示的图像。

        Args:
            image_qpixmap: 要显示的 QPixmap 格式的图像，或 None 来清空。
        """
        if image_qpixmap is None:
            self.setText("")  # 清空文字，改用绘制方式显示提示
            self.setPixmap(QPixmap())  # 清除图像
            self.original_pixmap = None
            self.update()
        else:
            self.original_pixmap = image_qpixmap
            self.setPixmap(self.original_pixmap)
            # *** 性能优化：移除手动resize，让QScrollArea自动处理 ***
            # 下面的手动resize调用是导致UI卡顿的元凶，因为它会触发全局布局重计算。
            # 我们现在依赖于sizePolicy和sizeHint，让Qt自动、高效地处理。
            self.adjustSize()  # 使用 adjustSize() 来根据内容更新大小，这比resize()高效得多

            # 重置缩放因子为1.0（100%）
            self.zoom_factor = 1.0
            
            # 自动适应窗口大小
            self.fit_to_window()

            # 自动获取焦点，使键盘事件能被捕获
            self.setFocus()

    def fit_to_window(self):
        """
        调整缩放比例，使图像适应窗口大小。
        """
        if self.original_pixmap is None or self.original_pixmap.isNull():
            return
            
        # 获取控件的可见区域大小（考虑滚动区域）
        if self.scroll_area:
            view_width = self.scroll_area.width() - 20  # 减去滚动条宽度和边距
            view_height = self.scroll_area.height() - 20  # 减去滚动条高度和边距
        else:
            view_width = self.width()
            view_height = self.height()
            
        # 获取图像尺寸
        image_width = self.original_pixmap.width()
        image_height = self.original_pixmap.height()
        
        # 计算适应窗口的缩放比例
        width_ratio = view_width / image_width
        height_ratio = view_height / image_height
        
        # 选择较小的比例，确保图像完全可见
        new_zoom = min(width_ratio, height_ratio)
        
        # 设置新的缩放因子
        self.zoom_factor = new_zoom
        
        # 居中图像
        self.pan_offset = QPointF(
            (view_width - image_width * new_zoom) / 2,
            (view_height - image_height * new_zoom) / 2
        )
        
        # 更新显示
        self.update()
        
    def resizeEvent(self, event):
        """
        处理控件大小变化事件，自动调整图像以适应新大小。
        """
        super().resizeEvent(event)
        
        # 当控件大小改变时，如果有图像，则自动适应窗口
        if self.original_pixmap and not self.original_pixmap.isNull():
            self.fit_to_window()

    def set_scroll_area(self, scroll_area):
        """设置所在的滚动区域，用于平移操作"""
        self.scroll_area = scroll_area

    def wheelEvent(self, event):
        """处理鼠标滚轮事件，用于缩放图像"""
        if self.original_pixmap:
            # 检查是否按下Ctrl键
            if self.ctrl_pressed:
                # 计算缩放增量
                delta = event.angleDelta().y()
                factor = 1.0

                # 使用angleDelta来判断缩放方向和速度
                if delta > 0:  # 向上滚动，放大
                    factor = 1.1  # 放大10%
                else:  # 向下滚动，缩小
                    factor = 0.9  # 缩小10%

                # 获取鼠标相对于图像的位置
                pos = event.position()
                mouse_pos = QPointF(pos.x(), pos.y())  # 使用QPointF而不是QPoint

                # 计算新的缩放因子，但限制范围
                new_zoom = self.zoom_factor * factor
                new_zoom = max(0.1, min(5.0, new_zoom))  # 限制缩放范围在10%-500%之间

                # 计算鼠标位置相对于当前视图的偏移量
                mouse_scene_pos = (mouse_pos - self.pan_offset) / self.zoom_factor
                
                # 计算新的平移偏移量，保持鼠标指向的图像点不变
                new_pan_offset = mouse_pos - mouse_scene_pos * new_zoom
                
                # 更新视图状态
                self.zoom_factor = new_zoom
                self.pan_offset = new_pan_offset
                
                # 触发重绘
                self.update()
                event.accept()
            else:
                # 如果不是缩放操作，交给父类处理
                super().wheelEvent(event)
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        """处理键盘按下事件，主要用于检测修饰键"""
        if event.key() == Qt.Key.Key_Control:
            self.ctrl_pressed = True
        elif event.key() == Qt.Key.Key_Shift:
            self.shift_pressed = True
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """处理键盘释放事件，主要用于检测修饰键"""
        if event.key() == Qt.Key.Key_Control:
            self.ctrl_pressed = False
        elif event.key() == Qt.Key.Key_Shift:
            self.shift_pressed = False
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        """处理鼠标按下事件。"""
        # 处理图像拖动（平移）
        if event.button() == Qt.MouseButton.MiddleButton or (
            event.button() == Qt.MouseButton.LeftButton and self.ctrl_pressed
        ):
            # 中键拖动或Ctrl+左键拖动，用于平移视图
            self.is_panning = True
            self.pan_start_point = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        # 如果没有图像，让父类处理事件
        if (
            self.original_pixmap is None
            or self.original_pixmap.isNull()
        ):
            super().mousePressEvent(event)
            return

        # 处理左键不同交互模式的事件
        if event.button() == Qt.MouseButton.LeftButton:
            # 获取图像坐标系下的点击位置
            image_point = self._widget_to_image_point(event.pos())
            if image_point is None:
                # 点击在图像外部，忽略
                return

            if self.interaction_mode == InteractionMode.RECT_SELECTION:
                # 开始矩形选择
                self.interaction_in_progress = True
                self.start_point = event.pos()
                self.end_point = self.start_point
                self.update()
            elif self.interaction_mode == InteractionMode.LASSO_SELECTION:
                # 开始套索选择
                self.interaction_in_progress = True
                self.start_point = event.pos()
                self.end_point = self.start_point
                self.lasso_points = [event.pos()]  # 初始化套索点列表
                self.update()
            else:
                # 在没有特定交互模式时，调用父类的鼠标按下事件处理
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件。"""
        # 处理图像拖动（平移）
        if self.is_panning and self.original_pixmap:
            current_pos = event.position().toPoint()
            delta = current_pos - self.pan_start_point
            self.pan_offset += QPointF(delta)
            self.pan_start_point = current_pos
            self.update()
            event.accept()
            return

        # 如果没有图像，让父类处理事件
        if (
            self.original_pixmap is None
            or self.original_pixmap.isNull()
        ):
            super().mouseMoveEvent(event)
            return

        # 处理不同交互模式的鼠标移动
        if self.interaction_in_progress:
            if self.interaction_mode == InteractionMode.RECT_SELECTION:
                # 更新矩形选择
                self.end_point = event.pos()
                self.update()
            elif self.interaction_mode == InteractionMode.LASSO_SELECTION:
                # 更新套索路径
                self.end_point = event.pos()
                self.lasso_points.append(event.pos())
                self.update()
        else:
            # 没有进行交互时，调用父类的鼠标移动事件处理
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件。"""
        # 处理图像拖动（平移）释放
        if event.button() == Qt.MouseButton.MiddleButton or (
            event.button() == Qt.MouseButton.LeftButton and self.ctrl_pressed
        ):
            self.is_panning = False
            self.unsetCursor()
            event.accept()
            return

        # 如果没有图像，让父类处理事件
        if (
            self.original_pixmap is None
            or self.original_pixmap.isNull()
        ):
            super().mouseReleaseEvent(event)
            return

        # 处理不同交互模式的鼠标释放
        if event.button() == Qt.MouseButton.LeftButton and self.interaction_in_progress:
            self.interaction_in_progress = False

            if self.interaction_mode == InteractionMode.RECT_SELECTION:
                # 完成选区，保存矩形并发出信号
                current_rect = self._get_current_rect()
                if not current_rect.isNull() and current_rect.width() > 0 and current_rect.height() > 0:
                    # 转换为图像坐标系
                    image_rect = self._get_image_space_rect(current_rect)
                    # 保存交互矩形
                    self.interaction_rect = current_rect
                    # 发出选区完成信号
                    self.selection_finished.emit(image_rect)
                else:
                    # 如果矩形无效，清除它
                    self.interaction_rect = QRect()
                self.update()
            elif self.interaction_mode == InteractionMode.LASSO_SELECTION:
                # 完成套索选区，保存点列表并发出信号
                if len(self.lasso_points) > 2:  # 至少需要3个点才能形成有效区域
                    # 保存交互矩形（用于绘制边界框）
                    points = [self._widget_to_image_point(p) for p in self.lasso_points if self._widget_to_image_point(p) is not None]
                    # 发出套索选区完成信号
                    if points:
                        self.lasso_finished.emit(points)
                        # 保存交互矩形（用于绘制边界框）
                        left = min(p.x() for p in self.lasso_points)
                        top = min(p.y() for p in self.lasso_points)
                        right = max(p.x() for p in self.lasso_points)
                        bottom = max(p.y() for p in self.lasso_points)
                        self.interaction_rect = QRect(QPoint(left, top), QPoint(right, bottom))
                else:
                    # 如果点不足，清除套索路径
                    self.lasso_points = []
                    self.interaction_rect = QRect()
                self.update()
        else:
            # 其他按钮或没有交互时，调用父类的鼠标释放事件处理
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件。"""
        # 移除文件打开功能，主视图现在只作为图像显示和交互组件
        # 调用父类的双击事件处理
        super().mouseDoubleClickEvent(event)

    def paintEvent(self, event):
        """重写绘制事件以绘制交互图形。"""
        # 不调用super().paintEvent(event)，我们将完全控制绘制过程
        
        painter = QPainter(self)
        
        # 如果没有图像，绘制空状态提示
        if self.original_pixmap is None:
            self._draw_empty_state_hint()
            return

        # 应用视图变换
        painter.translate(self.pan_offset)
        painter.scale(self.zoom_factor, self.zoom_factor)
        
        # 绘制图像
        if self.original_pixmap:
            painter.drawPixmap(0, 0, self.original_pixmap)
        
        # 应用反向变换，以便后续绘制在正确的位置
        painter.scale(1/self.zoom_factor, 1/self.zoom_factor)
        painter.translate(-self.pan_offset)
        
        # 绘制交互元素
        current_rect = self._get_current_rect()
        if not current_rect.isNull():
            if self.interaction_mode == InteractionMode.RECT_SELECTION:
                self._draw_selection_ants(painter, current_rect)
            elif self.interaction_mode == InteractionMode.LASSO_SELECTION:
                self._draw_lasso_ants(painter, current_rect)

    def _get_current_rect(self) -> QRect:
        """获取当前应该绘制的矩形。"""
        if self.interaction_in_progress:
            return QRect(self.start_point, self.end_point).normalized()
        elif not self.interaction_rect.isNull():
            return self.interaction_rect
        return QRect()

    def _draw_selection_ants(self, painter: QPainter, rect: QRect):
        """绘制选区的"蚂蚁线"。"""
        pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine)
        pen.setDashPattern([5, 5])
        self.ant_offset = (self.ant_offset + 1) % 10
        pen.setDashOffset(self.ant_offset)
        painter.setPen(pen)
        painter.drawRect(rect)

        pen.setColor(Qt.GlobalColor.white)
        pen.setDashOffset(self.ant_offset + 5)
        painter.setPen(pen)
        painter.drawRect(rect)

    def _draw_lasso_ants(self, painter: QPainter, rect: QRect):
        """绘制套索的"蚂蚁线"。"""
        if not self.lasso_points or len(self.lasso_points) < 2:
            return

        # 绘制套索路径
        pen = QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine)
        pen.setDashPattern([5, 5])
        self.ant_offset = (self.ant_offset + 1) % 10
        pen.setDashOffset(self.ant_offset)
        painter.setPen(pen)

        # 绘制路径线段
        for i in range(len(self.lasso_points) - 1):
            painter.drawLine(self.lasso_points[i], self.lasso_points[i + 1])

        # 如果正在绘制中，绘制白色的对比线
        pen.setColor(Qt.GlobalColor.white)
        pen.setDashOffset(self.ant_offset + 5)
        painter.setPen(pen)
        for i in range(len(self.lasso_points) - 1):
            painter.drawLine(self.lasso_points[i], self.lasso_points[i + 1])

    def _widget_to_image_point(self, widget_point: QPoint) -> QPoint | None:
        """
        将 Widget 坐标系下的点转换为图像像素坐标系下的点。

        Args:
            widget_point: Widget 坐标系下的点

        Returns:
            图像坐标系下的点，如果点超出图像边界则返回 None
        """
        if (
            self.original_pixmap is None
            or self.original_pixmap.isNull()
        ):
            return None
            
        # 考虑视图变换
        # 将widget坐标转换为场景坐标
        widget_point_f = QPointF(widget_point)  # 转换为QPointF
        scene_point = (widget_point_f - self.pan_offset) / self.zoom_factor
        
        # 检查点是否在图像边界内
        if (0 <= scene_point.x() < self.original_pixmap.width() and 
            0 <= scene_point.y() < self.original_pixmap.height()):
            return QPoint(int(scene_point.x()), int(scene_point.y()))
            
        return None

    def _get_image_space_rect(self, widget_rect: QRect) -> QRect:
        """
        将 Widget 坐标系下的矩形转换为图像像素坐标系下的矩形。
        """
        if (
            self.pixmap() is None
            or self.pixmap().isNull()
            or self.original_pixmap is None
        ):
            return QRect()

        # 将矩形的角点转换为图像坐标系
        tl_point = self._widget_to_image_point(widget_rect.topLeft())
        br_point = self._widget_to_image_point(widget_rect.bottomRight())
        
        if tl_point is None or br_point is None:
            return QRect()
            
        # 创建图像空间中的矩形
        return QRect(tl_point, br_point)

    def _image_to_widget_point(self, image_point: QPoint) -> QPoint | None:
        """
        将图像坐标系下的点转换为Widget坐标系下的点。

        Args:
            image_point: 图像坐标系下的点

        Returns:
            Widget坐标系下的点，如果转换失败则返回None
        """
        if (
            self.original_pixmap is None
            or self.original_pixmap.isNull()
        ):
            return None

        # 检查点是否在图像边界内
        if (image_point.x() < 0 or image_point.x() >= self.original_pixmap.width() or
            image_point.y() < 0 or image_point.y() >= self.original_pixmap.height()):
            return None
        
        # 将场景坐标转换为widget坐标
        image_point_f = QPointF(image_point)
        
        # 将场景坐标转换为widget坐标
        widget_point = image_point_f * self.zoom_factor + self.pan_offset
        
        return QPoint(int(widget_point.x()), int(widget_point.y()))

    def reset_zoom(self):
        """重置缩放到100%"""
        self.zoom_factor = 1.0
        self.pan_offset = QPointF(0, 0)
        self.update()

    def zoom_in(self):
        """放大"""
        new_factor = min(self.zoom_factor * 1.25, 5.0)  # 最大5倍
        self.zoom_factor = new_factor
        self.update()

    def zoom_out(self):
        """缩小"""
        new_factor = max(self.zoom_factor / 1.25, 0.1)  # 最小0.1倍
        self.zoom_factor = new_factor
        self.update()

    def _draw_empty_state_hint(self):
        """绘制空状态提示"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 获取控件尺寸
        width = self.width()
        height = self.height()

        # 设置虚线边框
        pen = QPen(QColor(180, 180, 180))
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(2)
        painter.setPen(pen)

        # 绘制虚线边框，留出一定边距
        margin = 20
        painter.drawRect(margin, margin, width - 2 * margin, height - 2 * margin)

        # 绘制提示文本
        painter.setPen(QColor(120, 120, 120))

        # 设置字体
        font = painter.font()
        font.setPointSize(12)
        painter.setFont(font)

        # 计算文本位置
        text_rect = painter.fontMetrics().boundingRect("请打开一张图片")
        text_x = (width - text_rect.width()) / 2
        text_y = height / 2 - 30  # 稍微往上一点，为双击提示留出空间

        # 绘制主提示文本
        painter.drawText(int(text_x), int(text_y), "请打开一张图片")
        
        # 添加提示文本
        hint_text = "请从图像池选择图像加载到此处"
        hint_rect = painter.fontMetrics().boundingRect(hint_text)
        hint_x = (width - hint_rect.width()) / 2
        hint_y = text_y + 25  # 主文本下方
        painter.drawText(int(hint_x), int(hint_y), hint_text)

        # 设置较小的字体用于辅助提示
        font.setPointSize(9)
        painter.setFont(font)

        # 绘制支持的格式提示
        format_text = "支持格式: JPG, JPEG, PNG, BMP, TIF, TIFF"
        format_rect = painter.fontMetrics().boundingRect(format_text)
        format_x = (width - format_rect.width()) / 2
        format_y = hint_y + 25  # 提示文本下方
        painter.drawText(int(format_x), int(format_y), format_text)
