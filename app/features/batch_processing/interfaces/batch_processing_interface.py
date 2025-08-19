"""
批处理服务接口

定义批处理功能的抽象接口，用于依赖注入和松耦合设计。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget


class QObjectABCMeta(type(QObject), type(ABC)):
    """解决QObject和ABC元类冲突的自定义元类"""
    pass


class BatchProcessingInterface(QObject, ABC, metaclass=QObjectABCMeta):
    """
    批处理服务接口
    
    定义批处理功能的核心接口，包括：
    - 作业管理（创建、删除、重命名）
    - 图像池管理（添加、删除、清空）
    - 作业-图像关联管理
    - 批处理执行控制
    - 预设应用功能
    """
    
    # 核心信号
    show_error_message = pyqtSignal(str)
    show_info_message = pyqtSignal(str)
    
    # 作业处理信号
    job_processing_started = pyqtSignal(str)
    job_processing_finished = pyqtSignal(str, bool, str)
    job_file_progress = pyqtSignal(str, str, int, int)
    
    # === 作业管理接口 ===
    
    @abstractmethod
    def add_job(self, name: str) -> Optional[object]:
        """
        创建新的批处理作业
        
        Args:
            name: 作业名称
            
        Returns:
            创建的作业对象，失败返回None
        """
        pass
    
    @abstractmethod
    def remove_job(self, job_id: str) -> bool:
        """
        删除指定作业
        
        Args:
            job_id: 作业ID
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    def rename_job(self, job_id: str, new_name: str) -> bool:
        """
        重命名作业
        
        Args:
            job_id: 作业ID
            new_name: 新名称
            
        Returns:
            是否重命名成功
        """
        pass
    
    @abstractmethod
    def get_all_jobs(self) -> List[object]:
        """
        获取所有作业
        
        Returns:
            作业列表
        """
        pass
    
    @abstractmethod
    def get_job_by_name(self, job_name: str) -> Optional[object]:
        """
        根据名称获取作业
        
        Args:
            job_name: 作业名称
            
        Returns:
            作业对象，不存在返回None
        """
        pass
    
    # === 图像池管理接口 ===
    
    @abstractmethod
    def add_images_to_pool(self, file_paths: List[str]) -> int:
        """
        添加图像到图像池
        
        Args:
            file_paths: 图像文件路径列表
            
        Returns:
            成功添加的图像数量
        """
        pass
    
    @abstractmethod
    def remove_from_pool(self, indices: List[int]) -> int:
        """
        从图像池移除图像
        
        Args:
            indices: 要移除的图像索引列表
            
        Returns:
            成功移除的图像数量
        """
        pass
    
    @abstractmethod
    def clear_image_pool(self) -> int:
        """
        清空图像池
        
        Returns:
            清除的图像数量
        """
        pass
    
    @abstractmethod
    def is_pool_empty(self) -> bool:
        """
        检查图像池是否为空
        
        Returns:
            是否为空
        """
        pass
    
    @abstractmethod
    def get_pool_images(self) -> List[str]:
        """
        获取图像池中的所有图像路径
        
        Returns:
            图像路径列表
        """
        pass
    
    # === 作业-图像关联管理接口 ===
    
    @abstractmethod
    def add_pool_items_to_job(self, job_id: str, item_indices: List[int]) -> int:
        """
        将图像池中的项目添加到作业
        
        Args:
            job_id: 作业ID
            item_indices: 图像池项目索引列表
            
        Returns:
            成功添加的项目数量
        """
        pass
    
    @abstractmethod
    def remove_items_from_job(self, job_id: str, item_indices: List[int]) -> int:
        """
        从作业中移除项目
        
        Args:
            job_id: 作业ID
            item_indices: 项目索引列表
            
        Returns:
            成功移除的项目数量
        """
        pass
    
    @abstractmethod
    def clear_job_items(self, job_id: str) -> int:
        """
        清空作业的所有项目
        
        Args:
            job_id: 作业ID
            
        Returns:
            清除的项目数量
        """
        pass
    
    # === 批处理执行接口 ===
    
    @abstractmethod
    def start_processing(self) -> bool:
        """
        开始批处理
        
        Returns:
            是否成功启动
        """
        pass
    
    @abstractmethod
    def cancel_processing(self, job_id: str) -> None:
        """
        取消指定作业的处理
        
        Args:
            job_id: 作业ID
        """
        pass
    
    @abstractmethod
    def cancel_all_processing(self) -> None:
        """取消所有处理"""
        pass
    
    @abstractmethod
    def is_processing_cancelled(self) -> bool:
        """
        检查处理是否被取消
        
        Returns:
            是否被取消
        """
        pass
    
    # === 预设应用接口 ===
    
    @abstractmethod
    def apply_preset_to_job(self, job_id: str, preset_operations: List[Dict]) -> bool:
        """
        将预设操作应用到指定作业
        
        Args:
            job_id: 作业ID
            preset_operations: 预设操作列表
            
        Returns:
            是否应用成功
        """
        pass
    
    @abstractmethod
    def apply_preset_to_jobs(self, job_ids: List[str], preset_operations: List[Dict]) -> Dict[str, bool]:
        """
        将预设操作应用到多个作业
        
        Args:
            job_ids: 作业ID列表
            preset_operations: 预设操作列表
            
        Returns:
            作业ID到成功状态的映射
        """
        pass
    
    # === 辅助接口 ===
    
    @abstractmethod
    def import_folder(self, folder_path: str, recursive: bool = False, 
                     file_types: Optional[List[str]] = None) -> int:
        """
        导入文件夹中的图像
        
        Args:
            folder_path: 文件夹路径
            recursive: 是否递归搜索
            file_types: 支持的文件类型列表
            
        Returns:
            导入的图像数量
        """
        pass
    
    @abstractmethod
    def show_import_folder_dialog(self, parent_widget: Optional[QWidget] = None) -> int:
        """
        显示导入文件夹对话框
        
        Args:
            parent_widget: 父窗口
            
        Returns:
            导入的图像数量
        """
        pass
    
    @abstractmethod
    def force_cleanup_all_jobs(self) -> None:
        """强制清理所有作业资源"""
        pass
    
    @abstractmethod
    def get_last_image_folder_path(self) -> Optional[str]:
        """
        获取上次使用的图像文件夹路径
        
        Returns:
            上次使用的路径，如果没有则返回None
        """
        pass
    
    @abstractmethod
    def save_last_image_folder_path(self, path: str) -> None:
        """
        保存图像文件夹路径
        
        Args:
            path: 要保存的路径
        """
        pass