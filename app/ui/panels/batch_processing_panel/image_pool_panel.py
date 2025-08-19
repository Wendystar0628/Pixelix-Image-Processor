"""
图像池面板模块
"""
import os
from typing import Optional, List, Dict, Any

import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QRect
from PyQt6.QtGui import QAction, QPixmap, QIcon, QImage, QPainter
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QListWidget, QListWidgetItem, QPushButton, 
    QLabel, QMenu, QFileDialog, QStackedLayout,
    QStyledItemDelegate, QStyle
)

from app.features.batch_processing.batch_coordinator import BatchProcessingHandler


class ImagePoolItemDelegate(QStyledItemDelegate):
    """
    为图像池中的项目提供自定义的渲染和大小。
    确保每个项目都有固定的大小，并且内容（缩略图和文本）居中对齐。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_size = QSize(120, 120)
        self._thumb_area_height = 80
        self._padding = 5

    def sizeHint(self, option, index):
        """返回所有项目的固定大小。"""
        return self._item_size

    def paint(self, painter: QPainter | None, option, index):
        """自定义绘制逻辑。"""
        if painter is None:
            return

        painter.save()

        # 从模型索引中获取数据
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        text = index.data(Qt.ItemDataRole.DisplayRole)

        # 从图标中获取像素图
        pixmap = QPixmap()
        if isinstance(icon, QIcon):
            pixmap = icon.pixmap(self._item_size.width(), self._thumb_area_height)

        # 如果项目被选中，绘制背景
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        # --- 1. 绘制缩略图 ---
        if not pixmap.isNull():
            # 按比例缩放像素图以适应缩略图区域
            scaled_pixmap = pixmap.scaled(
                self._item_size.width() - 2 * self._padding,
                self._thumb_area_height - self._padding,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # 计算缩略图的居中位置
            thumb_rect = QRect(0, 0, scaled_pixmap.width(), scaled_pixmap.height())
            thumb_area_rect = QRect(option.rect.x(), option.rect.y(), option.rect.width(), self._thumb_area_height)
            thumb_rect.moveCenter(thumb_area_rect.center())
            
            painter.drawPixmap(thumb_rect, scaled_pixmap)

        # --- 2. 绘制文本 ---
        if text:
            # 根据选择状态设置文本颜色
            if option.state & QStyle.StateFlag.State_Selected:
                painter.setPen(option.palette.highlightedText().color())
            else:
                painter.setPen(option.palette.text().color())

            # 定义文本的矩形区域
            text_rect = QRect(
                option.rect.x() + self._padding,
                option.rect.y() + self._thumb_area_height,
                option.rect.width() - 2 * self._padding,
                option.rect.height() - self._thumb_area_height
            )

            # 绘制文本，水平居中、顶部对齐，并自动换行/省略
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap, text)

        painter.restore()


class ImagePoolPanel(QWidget):
    """
    管理图像池的面板
    
    职责：
    1. 显示图像池中的图像
    2. 处理图像池的添加、移除等操作
    3. 提供图像的上下文菜单和双击操作
    """
    
    # 定义信号
    image_double_clicked = pyqtSignal(str)  # 图像路径
    
    def __init__(self, handler: BatchProcessingHandler, parent=None):
        super().__init__(parent)
        self.handler = handler
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """初始化UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 图像池组
        image_pool_group = QGroupBox("图像池 (等待分配)")
        image_pool_layout = QVBoxLayout(image_pool_group)
        
        # 使用QStackedLayout来切换图像池和占位符
        self.image_pool_container = QWidget()
        self.image_pool_stack = QStackedLayout(self.image_pool_container)
        self.image_pool_stack.setContentsMargins(0, 0, 0, 0)
        
        # 图像池列表
        self.image_pool_list = QListWidget()
        self.image_pool_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        # 启用网格视图
        self.image_pool_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.image_pool_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.image_pool_list.setMovement(QListWidget.Movement.Static)
        self.image_pool_list.setWrapping(True)
        self.image_pool_list.setSpacing(10)
        
        # 设置自定义委托以实现一致的项目渲染
        self.image_pool_list.setItemDelegate(ImagePoolItemDelegate(self))
        
        # 设置上下文菜单
        self.image_pool_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_pool_list.customContextMenuRequested.connect(self._show_context_menu)
        
        self.image_pool_stack.addWidget(self.image_pool_list)
        
        # 为空图像池创建占位符
        self.image_pool_placeholder = QLabel("图像池为空\n\n双击图像可加载到主视图")
        self.image_pool_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_pool_placeholder.setStyleSheet("color: gray; font-style: italic;")
        self.image_pool_stack.addWidget(self.image_pool_placeholder)
        
        image_pool_layout.addWidget(self.image_pool_container)
        
        # 按钮布局
        buttons_layout = QHBoxLayout()
        self.add_images_button = QPushButton("添加图像")
        self.add_to_job_button = QPushButton("添加到作业")
        self.add_all_to_job_button = QPushButton("一键添加到作业")
        self.remove_from_pool_button = QPushButton("移出图像")
        self.clear_pool_button = QPushButton("清空图像池")
        
        buttons_layout.addWidget(self.add_images_button)
        buttons_layout.addWidget(self.add_to_job_button)
        buttons_layout.addWidget(self.add_all_to_job_button)
        buttons_layout.addWidget(self.remove_from_pool_button)
        buttons_layout.addWidget(self.clear_pool_button)
        
        image_pool_layout.addLayout(buttons_layout)
        layout.addWidget(image_pool_group)
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接按钮点击信号
        self.add_images_button.clicked.connect(self._on_add_images_clicked)
        self.add_to_job_button.clicked.connect(self._on_add_to_job_clicked)
        self.add_all_to_job_button.clicked.connect(self._on_add_all_to_job_clicked)
        self.remove_from_pool_button.clicked.connect(self._on_remove_from_pool_clicked)
        self.clear_pool_button.clicked.connect(self._on_clear_pool_clicked)
        
        # 连接列表项双击信号
        self.image_pool_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # 连接图像池变化信号
        self.handler.pool_manager.pool_changed.connect(self.update_display)
        
    def update_display(self):
        """更新图像池显示"""
        self.image_pool_list.clear()
        
        # 获取图像池中的图像
        pool_images = self.handler.get_pool_images()
        
        if not pool_images:
            self.image_pool_stack.setCurrentWidget(self.image_pool_placeholder)
            return
            
        self.image_pool_stack.setCurrentWidget(self.image_pool_list)
        
        # 获取缩略图
        thumbnails = self.handler.get_pool_thumbnails()
        
        # 添加池中的所有图像
        for file_path in pool_images:
            file_name = os.path.basename(file_path)
            list_item = QListWidgetItem(file_name)
            
            # 检查是否有缩略图
            thumbnail = thumbnails.get(file_path)
            if thumbnail is not None:
                height, width, channel = thumbnail.shape
                bytes_per_line = 3 * width
                
                # 直接创建RGB格式的QImage，不需要调用rgbSwapped()
                # 因为thumbnail已经是RGB格式
                if not thumbnail.flags['C_CONTIGUOUS']:
                    thumbnail_copy = np.ascontiguousarray(thumbnail)
                    q_image = QImage(thumbnail_copy.data.tobytes(), width, height, bytes_per_line, QImage.Format.Format_RGB888)
                else:
                    q_image = QImage(thumbnail.data.tobytes(), width, height, bytes_per_line, QImage.Format.Format_RGB888)
                
                pixmap = QPixmap.fromImage(q_image)
                list_item.setIcon(QIcon(pixmap))
            
            # 存储文件路径作为用户数据
            list_item.setData(Qt.ItemDataRole.UserRole, file_path)
            list_item.setToolTip(f"{file_path}\n双击加载到主视图")
            self.image_pool_list.addItem(list_item)
    
    def get_selected_indices(self) -> List[int]:
        """获取当前选中的项目索引"""
        return [item.row() for item in self.image_pool_list.selectedIndexes()]
    
    # --- 槽函数 ---
    

    
    @pyqtSlot()
    def _on_add_images_clicked(self):
        """添加图像到图像池"""
        # 获取上次使用的路径
        start_dir = ""
        if hasattr(self.handler, 'get_last_image_folder_path'):
            last_path = self.handler.get_last_image_folder_path()
            if last_path and os.path.exists(last_path):
                start_dir = last_path
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "添加图像", start_dir, "图像文件 (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if file_paths:
            # 保存当前选择的文件夹路径
            if hasattr(self.handler, 'save_last_image_folder_path'):
                folder_path = os.path.dirname(file_paths[0])
                self.handler.save_last_image_folder_path(folder_path)
            
            self.handler.add_images_to_pool(file_paths)
    
    @pyqtSlot()
    def _on_add_to_job_clicked(self):
        """将选中的图像添加到当前作业"""
        # 这个信号需要由外部连接到相应的槽函数
        selected_indices = self.get_selected_indices()
        if selected_indices:
            # 发出自定义信号，由父组件处理
            self.add_to_job_requested.emit(selected_indices)
    
    @pyqtSlot()
    def _on_add_all_to_job_clicked(self):
        """将所有图像添加到作业"""
        # 发出信号，让主面板处理
        self.add_all_to_job_requested.emit()
    
    @pyqtSlot()
    def _on_remove_from_pool_clicked(self):
        """从图像池移除选中的图像"""
        selected_indices = self.get_selected_indices()
        if selected_indices:
            count = self.handler.remove_from_pool(selected_indices)
    
    @pyqtSlot()
    def _on_clear_pool_clicked(self):
        """清空图像池"""
        if not self.handler.is_pool_empty():
            count = self.handler.clear_image_pool()
    
    @pyqtSlot(QListWidgetItem)
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """处理列表项双击事件"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            self.image_double_clicked.emit(file_path)
        else:
            print(f"警告: 文件路径无效或不存在: {file_path}")
    
    def _show_context_menu(self, position):
        """显示上下文菜单"""
        item = self.image_pool_list.itemAt(position)
        if not item:
            return
            
        context_menu = QMenu(self)
        
        # 添加"加载到主视图"菜单项
        load_action = QAction("加载到主视图", self)
        load_action.triggered.connect(lambda: self._on_item_double_clicked(item))
        context_menu.addAction(load_action)
        
        # 添加"从图像池移除"菜单项
        remove_action = QAction("从图像池移除", self)
        remove_action.triggered.connect(lambda: self._remove_item(item))
        context_menu.addAction(remove_action)
        
        # 显示菜单
        context_menu.exec(self.image_pool_list.mapToGlobal(position))
    
    def _remove_item(self, item: QListWidgetItem):
        """移除指定项目"""
        row = self.image_pool_list.row(item)
        if row >= 0:
            count = self.handler.remove_from_pool([row])

# 添加自定义信号
ImagePoolPanel.add_to_job_requested = pyqtSignal(list)  # 选中的索引列表
ImagePoolPanel.add_all_to_job_requested = pyqtSignal()