"""
批处理文件导入管理器模块

负责管理批处理的文件导入功能，包括文件夹导入和文件类型过滤。
"""
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QFileDialog

from app.features.batch_processing.pools.pool_manager import PoolManager
from app.handlers.file_handler import FileHandler


class BatchImportManager(QObject):
    """
    批处理文件导入管理器
    
    职责：
    - 管理文件夹导入功能
    - 处理文件类型过滤
    - 提供导入对话框管理
    """
    
    # 定义信号
    show_error_message = pyqtSignal(str)
    
    def __init__(self, pool_manager: PoolManager, 
                 file_handler: FileHandler, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.pool_manager = pool_manager
        self.file_handler = file_handler
    
    def import_folder(self, folder_path: str, recursive: bool = False, 
                     file_types: Optional[List[str]] = None) -> int:
        """
        导入文件夹中的图像到图像池
        
        Args:
            folder_path: 文件夹路径
            recursive: 是否递归搜索子文件夹
            file_types: 要导入的文件类型列表，如 [".jpg", ".png"]
            
        Returns:
            int: 成功导入的图像数量
        """
        if not folder_path:
            self.show_error_message.emit("无效的文件夹路径")
            return 0
            
        return self.pool_manager.import_folder(folder_path, recursive, file_types)
    
    def show_import_folder_dialog(self, parent_widget: Optional[QWidget] = None) -> int:
        """
        显示文件夹选择对话框，并导入选中的文件夹中的图像到图像池
        
        Args:
            parent_widget: 父窗口部件
            
        Returns:
            int: 成功导入的图像数量
        """
        folder_path = QFileDialog.getExistingDirectory(
            parent_widget, 
            "选择文件夹导入图像", 
            self.file_handler.last_directory or ""
        )
        
        if folder_path:
            return self.import_folder(folder_path)
        return 0
    
    def get_supported_file_types(self) -> List[str]:
        """
        获取支持的文件类型列表
        
        Returns:
            List[str]: 支持的文件扩展名列表
        """
        return [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif"]
    
    def validate_file_path(self, file_path: str) -> bool:
        """
        验证文件路径是否为支持的图像文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为支持的图像文件
        """
        import os
        
        if not os.path.exists(file_path):
            return False
        
        if not os.path.isfile(file_path):
            return False
        
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in self.get_supported_file_types()
    
    def filter_image_files(self, file_paths: List[str]) -> List[str]:
        """
        从文件路径列表中过滤出图像文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            List[str]: 过滤后的图像文件路径列表
        """
        return [path for path in file_paths if self.validate_file_path(path)]