"""
图像池管理器模块

此模块定义了PoolManager类，负责协调图像池存储和作业系统的交互，
不再创建或管理"图像池"作业，使用独立的ImagePoolStorage组件。
"""
import os
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QFileDialog

from .image_pool_storage import ImagePoolStorage
from ..managers.batch_job_manager import JobManager
from ..managers.job_selection_manager import JobSelectionManager
from ..batch_job_models import BatchJob
from app.handlers.file_handler import FileHandler


class PoolManager(QObject):
    """
    图像池管理器
    
    职责：
    - 协调图像池存储和作业系统的交互
    - 处理"一键添加到作业"的逻辑
    - 不再创建或管理"图像池"作业
    - 提供文件夹导入功能
    """
    
    # 信号：当图像池内容发生变化时发出
    pool_changed = pyqtSignal()
    
    # 信号：当图像添加到作业时发出
    images_added_to_job = pyqtSignal(str, int)  # job_id, count
    
    def __init__(self, job_manager: JobManager, 
                 job_selection_manager: JobSelectionManager,
                 file_handler: FileHandler):
        """
        初始化重构的图像池管理器
        
        Args:
            job_manager: 作业管理器实例
            job_selection_manager: 作业选择管理器实例
            file_handler: 文件处理器实例
        """
        super().__init__()
        self.job_manager = job_manager
        self.job_selection_manager = job_selection_manager
        self.file_handler = file_handler
        
        # 创建独立的图像池存储组件
        self.storage = ImagePoolStorage(file_handler)
        
        # 连接存储组件的信号
        self.storage.pool_changed.connect(self.pool_changed)
    
    def add_images_to_pool(self, file_paths: List[str]) -> int:
        """
        向图像池添加图像
        
        Args:
            file_paths: 图像文件路径列表
            
        Returns:
            int: 成功添加的图像数量
        """
        return self.storage.add_images(file_paths)
    
    def remove_from_pool(self, indices: List[int]) -> int:
        """
        从图像池中移除图像
        
        Args:
            indices: 要移除的索引列表
            
        Returns:
            int: 成功移除的图像数量
        """
        return self.storage.remove_images(indices)
    
    def clear_image_pool(self) -> int:
        """
        清空图像池
        
        Returns:
            int: 清除的图像数量
        """
        return self.storage.clear_images()
    
    def is_pool_empty(self) -> bool:
        """
        检查图像池是否为空
        
        Returns:
            bool: 如果图像池为空则返回True，否则返回False
        """
        return self.storage.is_empty()
    
    def get_pool_images(self) -> List[str]:
        """
        获取图像池中的所有图像路径
        
        Returns:
            List[str]: 图像路径列表
        """
        return self.storage.get_all_images()
    
    def get_pool_image_count(self) -> int:
        """
        获取图像池中的图像数量
        
        Returns:
            int: 图像数量
        """
        return self.storage.get_image_count()
    
    def get_pool_thumbnails(self):
        """
        获取图像池中的所有缩略图
        
        Returns:
            Dict[str, np.ndarray]: 文件路径到缩略图的映射
        """
        return self.storage.get_all_thumbnails()
    
    def add_pool_items_to_job(self, job_id: str, item_indices: List[int]) -> int:
        """
        将图像池中的项添加到指定作业
        
        Args:
            job_id: 目标作业ID
            item_indices: 图像池中项的索引列表
            
        Returns:
            int: 成功添加的项数量
        """
        # 验证作业是否存在
        job = self.job_manager.get_job(job_id)
        if job is None:
            return 0
        
        # 获取图像池中的所有图像
        pool_images = self.storage.get_all_images()
        if not pool_images or not item_indices:
            return 0
        
        # 获取要添加的文件路径
        file_paths = []
        for idx in item_indices:
            if 0 <= idx < len(pool_images):
                file_paths.append(pool_images[idx])
        
        if not file_paths:
            return 0
        
        # 添加到目标作业
        added_count = self.job_manager.add_sources_to_job(job_id, file_paths)
        
        if added_count > 0:
            self.images_added_to_job.emit(job_id, added_count)
        
        return added_count
    
    def add_all_pool_items_to_selected_job(self) -> Optional[BatchJob]:
        """
        将图像池中的所有图像添加到当前选中的作业
        
        Returns:
            Optional[BatchJob]: 成功操作的作业对象，如果没有选中作业或图像池为空则返回None
        """
        # 检查图像池是否为空
        if self.storage.is_empty():
            return None
        
        # 获取当前选中的作业
        selected_job = self.job_selection_manager.get_selected_job()
        if selected_job is None:
            return None
        
        # 获取所有图像池项目的索引
        pool_images = self.storage.get_all_images()
        all_indices = list(range(len(pool_images)))
        
        # 添加到选中的作业
        added_count = self.add_pool_items_to_job(selected_job.job_id, all_indices)
        
        if added_count > 0:
            return selected_job
        
        return None
    
    def can_add_to_job(self) -> bool:
        """
        检查是否可以添加图像到作业
        
        Returns:
            bool: 如果图像池不为空且有选中的作业则返回True
        """
        return (not self.storage.is_empty() and 
                self.job_selection_manager.has_selection())
    
    def import_folder(self, folder_path: str, recursive: bool = False, 
                     file_types: Optional[List[str]] = None) -> int:
        """
        从文件夹导入图像到图像池
        
        Args:
            folder_path: 文件夹路径
            recursive: 是否递归搜索子文件夹
            file_types: 要导入的文件类型列表，如 [".jpg", ".png"]
            
        Returns:
            int: 成功导入的图像数量
        """
        return self.storage.import_folder(folder_path, recursive, file_types)
    
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
            "选择要导入的文件夹",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path:
            return self.import_folder(folder_path, recursive=True)
        
        return 0
    
    def get_storage_component(self) -> ImagePoolStorage:
        """
        获取图像池存储组件（用于直接访问存储功能）
        
        Returns:
            ImagePoolStorage: 图像池存储组件实例
        """
        return self.storage