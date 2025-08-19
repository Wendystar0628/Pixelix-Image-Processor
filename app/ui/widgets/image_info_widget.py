import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QFrame,
    QHBoxLayout,
    QGridLayout,
    QSizePolicy,
)
from PyQt6.QtGui import QColor, QPalette

from app.core import ImageAnalysisEngine
from app.core.operations.base_operation import ImageOperation
from typing import List, Optional


class ImageInfoWidget(QWidget):
    """
    一个用于显示图像详细元数据信息的可嵌入控件。
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # 创建一个可滚动的区域，以防信息过多
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        main_layout.addWidget(scroll_area)

        # 用于放置所有信息行的容器控件
        container_widget = QWidget()
        scroll_area.setWidget(container_widget)

        # 使用 QFormLayout 来展示键值对信息
        self.form_layout = QFormLayout(container_widget)
        self.form_layout.setSpacing(10)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 保存应用的操作区域
        self.operations_frame = None

        self.update_info(None, None)  # 初始为空状态

    def update_info(self, image: np.ndarray | None, file_path: str | None, operations: Optional[List[ImageOperation]] = None) -> None:
        """
        根据输入图像、文件路径和应用的操作更新显示的信息。

        Args:
            image: 输入的图像 (NumPy 数组) 或 None。
            file_path: 图像的文件路径或 None。
            operations: 应用于图像的操作列表或 None。
        """
        # 清除旧的信息
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)

        if image is None:
            self.form_layout.addRow(QLabel("没有图像信息"))
            return

        try:
            # 首先添加应用的操作信息（放在最上方）
            if operations:
                self.update_applied_operations(operations)
                
                # 添加一个分隔线，与下面的信息分开
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setFrameShadow(QFrame.Shadow.Sunken)
                self.form_layout.addRow(separator)
            
            properties = ImageAnalysisEngine.get_image_properties(image, file_path)
            
            # 对属性进行分组以获得更好的可读性
            groups = {
                "文件信息": [
                    "文件名称",
                    "文件路径",
                    "文件大小",
                    "格式",
                    "创建时间",
                    "修改时间",
                ],
                "尺寸信息": ["分辨率", "宽高比", "总像素数"],
                "色彩信息": [
                    "色彩空间",
                    "通道数",
                    "透明通道",
                    "数据类型",
                    "位深度",
                ],
                "内存与数据": ["内存占用", "数值范围"],
                "相机信息": [key for key in properties if key.startswith("相机")],
                "拍摄参数": [key for key in properties if key.startswith("拍摄")],
                "EXIF时间信息": [
                    key
                    for key in properties
                    if key.startswith("EXIF ") and ("Time" in key or "Date" in key)
                ],
                "GPS信息": [key for key in properties if key.startswith("GPS ")],
                "其他EXIF信息": [
                    key
                    for key in properties
                    if key.startswith("EXIF ")
                    and not any(x in key for x in ["Time", "Date"])
                ],
            }

            # 仅显示非空组
            for group_title, prop_keys in groups.items():
                # 检查是否有此组的有效属性
                valid_keys = [key for key in prop_keys if key in properties]
                if not valid_keys:
                    continue

                # 为每个组添加一个标题
                group_label = QLabel(f"<b>{group_title}</b>")
                self.form_layout.addRow(group_label)

                for key in valid_keys:
                    value = str(properties[key])
                    # 创建并添加标签和值
                    label_widget = QLabel(f"{key}:")
                    value_widget = QLabel(value)
                    value_widget.setWordWrap(True)  # 允许长文本（如文件路径）换行
                    value_widget.setTextInteractionFlags(
                        Qt.TextInteractionFlag.TextSelectableByMouse
                    )  # 允许用鼠标选择和复制文本
                    self.form_layout.addRow(label_widget, value_widget)
                    
        except Exception as e:
            import traceback
            error_msg = f"获取图像信息时出错: {str(e)}\n{traceback.format_exc()}"
            error_label = QLabel(error_msg)
            error_label.setWordWrap(True)
            self.form_layout.addRow(error_label)
            print(error_msg)
    
    def update_applied_operations(self, operations: List[ImageOperation]) -> None:
        """
        更新并显示应用于图像的处理效果。

        Args:
            operations: 应用于图像的操作列表。
        """
        # 如果没有操作，不显示此部分
        if not operations:
            return
            
        # 添加处理效果标题，使用不同的样式
        effects_title = QLabel("<b>已应用的处理效果</b>")
        effects_title.setStyleSheet("color: #2c5aa0; font-size: 14px;")  # 使用蓝色和稍大的字体
        self.form_layout.addRow(effects_title)
        
        # 创建一个框架来包含所有处理效果
        self.operations_frame = QFrame()
        self.operations_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.operations_frame.setStyleSheet("background-color: #f0f7ff; border-radius: 5px; padding: 8px;")  # 淡蓝色背景
        
        # 根据效果数量选择合适的布局方式
        if len(operations) == 1:
            # 只有一个效果时使用垂直布局
            operations_layout = QVBoxLayout(self.operations_frame)
            operations_layout.setSpacing(5)
            
            for i, op in enumerate(operations):
                op_name = self._format_operation_name(op)
                op_label = QLabel(f"{i+1}. {op_name}")
                op_label.setStyleSheet("font-weight: bold; padding: 2px;")
                operations_layout.addWidget(op_label)
        else:
            # 效果达到2个及以上时使用网格布局，每行显示2个效果
            operations_layout = QGridLayout(self.operations_frame)
            operations_layout.setSpacing(8)
            operations_layout.setHorizontalSpacing(15)
            
            for i, op in enumerate(operations):
                op_name = self._format_operation_name(op)
                op_label = QLabel(f"{i+1}. {op_name}")
                op_label.setStyleSheet("font-weight: bold; padding: 3px; border-radius: 3px; background-color: rgba(44, 90, 160, 0.1);")
                op_label.setWordWrap(True)  # 允许文本换行
                op_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
                
                # 计算网格位置（每行2列）
                row = i // 2
                col = i % 2
                operations_layout.addWidget(op_label, row, col)
        
        # 添加处理效果框架到主布局
        self.form_layout.addRow(self.operations_frame)
    
    def _format_operation_name(self, op: ImageOperation) -> str:
        """
        格式化操作名称为更友好的显示。
        
        Args:
            op: 图像操作对象
            
        Returns:
            str: 格式化后的操作名称
        """
        op_name = op.__class__.__name__
        if op_name.endswith("Op"):
            op_name = op_name[:-2]  # 移除 "Op" 后缀
            
        # 格式化操作名称为更友好的显示
        op_name = op_name.replace("_", " ").title()
        return op_name
