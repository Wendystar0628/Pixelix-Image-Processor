"""
MainWindow事件处理器

负责处理主窗口的键盘、拖放、关闭等事件，
实现事件处理职责的分离。
"""

import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QDragEnterEvent, QDropEvent, QKeyEvent


class MainWindowEventHandler:
    """主窗口事件处理器"""
    
    def __init__(self, main_window):
        """
        初始化事件处理器
        
        Args:
            main_window: MainWindow实例
        """
        self.main_window = main_window
        
    def handle_key_press_event(self, event: QKeyEvent) -> bool:
        """
        处理键盘事件
        
        Args:
            event: 键盘事件
            
        Returns:
            bool: 是否处理了该事件
        """
        # 处理Ctrl+S快捷键 (保存)
        if event.key() == Qt.Key.Key_S and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if self.main_window.app_controller:
                self.main_window.app_controller.save_image(self.main_window)
                return True
        
        # 处理工具相关的键盘事件
        if (self.main_window.tool_manager and 
            self.main_window.tool_manager.handle_key_press(event.key(), event.modifiers().value)):
            return True
            
        return False
        
    def handle_drag_enter_event(self, event: QDragEnterEvent) -> None:
        """处理拖动进入事件"""
        mime_data = event.mimeData()
        if mime_data is not None and mime_data.hasUrls():
            # 检查是否有任何文件是支持的图像格式
            valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if any(file_path.lower().endswith(ext) for ext in valid_extensions):
                    event.acceptProposedAction()
                    return
        event.ignore()
        
    def handle_drop_event(self, event: QDropEvent) -> None:
        """处理文件放下事件"""
        mime_data = event.mimeData()
        if mime_data is not None and mime_data.hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            
            file_paths = []
            valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
            
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    if any(file_path.lower().endswith(ext) for ext in valid_extensions):
                        file_paths.append(file_path)
            
            if file_paths and self.main_window.app_controller:
                # 使用应用控制器将文件添加到图像池
                self.main_window.app_controller.add_images_to_pool(file_paths)
        else:
            event.ignore()
            
    def handle_close_event(self, event: QCloseEvent) -> None:
        """处理窗口关闭事件"""
        # 确保tool_manager不为None
        if self.main_window.tool_manager:
            # 保存所有工具状态
            self.main_window.tool_manager.save_all_tool_states()
        
        # 接受关闭事件
        event.accept()
    
    def handle_close(self, event: QCloseEvent) -> None:
        """处理窗口关闭事件（向后兼容方法）"""
        self.handle_close_event(event)