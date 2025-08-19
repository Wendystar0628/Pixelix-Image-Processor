"""
文件处理器模块

负责处理所有与文件I/O相关的操作，包括打开、保存图像文件，
以及处理文件对话框和文件格式选择等。
"""

import os
from typing import Optional, Tuple, Dict, Any, List, Callable

import cv2
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox

from app.utils.image_utils import load_image_safely, save_image_safely
from app.core.models.export_config import ExportConfig
from app.core.utils.proxy_utils import create_proxy_image
from app.core.interfaces.file_handler_interface import FileHandlerInterface


class FileHandler(FileHandlerInterface):
    """
    文件处理器类，负责处理所有与文件I/O相关的操作。
    
    这个类封装了文件打开、保存的逻辑，包括文件对话框的显示、
    文件格式的选择和处理，以及错误处理等。
    """
    
    # 当最近的文件列表更改时发出信号
    recent_files_changed = pyqtSignal(list)
    
    def __init__(self):
        """初始化文件处理器。"""
        super().__init__()
        self._last_directory = ""  # 记住上次打开/保存的目录
        self._max_recent_files = 10  # 最多记住10个最近文件
        self._recent_files: List[str] = []
        
    @property
    def last_directory(self) -> str:
        """获取上次使用的目录路径。"""
        return self._last_directory
        
    @property
    def recent_files(self) -> List[str]:
        """获取最近文件列表的副本。"""
        return self._recent_files.copy()
    
    def show_open_dialog(self, parent: QWidget) -> Optional[str]:
        """
        显示打开文件对话框
        
        Args:
            parent: 父窗口部件
            
        Returns:
            选择的文件路径，如果用户取消则返回None
        """
        return self._select_image_file(parent)
    
    def show_save_dialog(self, parent: QWidget) -> Optional[str]:
        """
        显示保存文件对话框
        
        Args:
            parent: 父窗口部件
            
        Returns:
            选择的保存路径，如果用户取消则返回None
        """
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "保存图像",
            self._last_directory,
            "PNG图像 (*.png);;JPEG图像 (*.jpg);;BMP图像 (*.bmp);;TIFF图像 (*.tiff)"
        )
        
        if file_path:
            self._last_directory = os.path.dirname(file_path)
            
        return file_path if file_path else None

    def _select_image_file(self, parent_widget: QWidget) -> Optional[str]:
        """
        显示文件选择对话框让用户选择图像文件
        
        Args:
            parent_widget: 父窗口部件，用于显示文件对话框
            
        Returns:
            选择的文件路径，如果用户取消则返回None
        """
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget, 
            "打开图像", 
            self._last_directory,
            "图像文件 (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if not file_path:
            # 用户取消了操作
            return None
        
        # 记住这个目录，下次打开时使用
        self._last_directory = os.path.dirname(file_path)
        return file_path

    def load_image_proxy(self, parent_widget: QWidget) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        快速加载图像代理
        
        通过文件对话框选择图像，但只返回低分辨率代理
        
        Args:
            parent_widget: 父窗口部件，用于显示文件对话框
            
        Returns:
            tuple: (代理图像, 文件路径) 或 (None, None)
        """
        file_path = self._select_image_file(parent_widget)
        if not file_path:
            return None, None
            
        try:
            # 加载原始图像但创建低分辨率代理
            image = cv2.imread(file_path)
            if image is None:
                QMessageBox.critical(parent_widget, "错误", "无法加载图像文件。")
                return None, None
                
            # 对于非RGB图像，确保转换为RGB
            if len(image.shape) == 2:  # 灰度图像
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                
            # 使用默认质量因子创建代理
            quality_factor = 0.75  # 默认代理质量因子
            
            proxy_image, _ = create_proxy_image(image, quality_factor)
            
            # 添加到最近文件列表
            self._add_to_recent_files(file_path)
            
            return proxy_image, file_path
            
        except Exception as e:
            # 显示错误消息
            QMessageBox.critical(parent_widget, "错误", f"打开文件时出错: {e}")
            return None, None
        
    def load_image(self, parent_widget: QWidget) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        打开图像文件并加载到内存中。
        
        Args:
            parent_widget: 父窗口部件，用于显示文件对话框。
            
        Returns:
            Tuple[Optional[np.ndarray], Optional[str]]: 
                - 如果成功，返回 (图像数据, 文件路径)
                - 如果用户取消或发生错误，返回 (None, None)
        """
        # 显示文件对话框
        file_path = self._select_image_file(parent_widget)
        
        if not file_path:
            # 用户取消了操作
            return None, None
            
        try:
            # 加载图像
            image = load_image_safely(file_path)
            if image is None:
                raise IOError("无法加载图像文件。")
                
            # 添加到最近文件列表
            self._add_to_recent_files(file_path)
                
            return image, file_path
            
        except Exception as e:
            # 显示错误消息
            QMessageBox.critical(parent_widget, "错误", f"打开文件时出错: {e}")
            return None, None

    def save_image(self, parent_widget: QWidget, image_data: np.ndarray, 
                  file_path: Optional[str] = None, force_dialog: bool = False) -> Optional[str]:
        """
        保存图像到文件，支持普通保存和弹出保存对话框功能。
        
        Args:
            parent_widget: 父窗口部件，用于显示文件对话框。
            image_data: 要保存的图像数据。
            file_path: 保存路径。如果为None或force_dialog为True，将显示保存对话框。
            force_dialog: 是否强制显示保存对话框，即使有file_path。
            
        Returns:
            Optional[str]: 如果成功保存，返回文件路径；否则返回None。
        """
        # 确定是否需要显示保存对话框
        show_dialog = file_path is None or force_dialog
        
        if show_dialog:
            # 显示保存对话框
            try:
                file_path, selected_filter = QFileDialog.getSaveFileName(
                    parent_widget,
                    "保存图像",
                    self._last_directory,
                    "PNG图像 (*.png);;JPEG图像 (*.jpg);;BMP图像 (*.bmp);;TIFF图像 (*.tiff)"
                )
                
                if not file_path:
                    # 用户取消了操作
                    return None
                    
                # 确保文件有正确的扩展名
                if selected_filter == "PNG图像 (*.png)" and not file_path.lower().endswith(".png"):
                    file_path += ".png"
                elif selected_filter == "JPEG图像 (*.jpg)" and not file_path.lower().endswith((".jpg", ".jpeg")):
                    file_path += ".jpg"
                elif selected_filter == "BMP图像 (*.bmp)" and not file_path.lower().endswith(".bmp"):
                    file_path += ".bmp"
                elif selected_filter == "TIFF图像 (*.tiff)" and not file_path.lower().endswith((".tiff", ".tif")):
                    file_path += ".tiff"
            except Exception as e:
                QMessageBox.critical(parent_widget, "错误", f"显示保存对话框时出错: {str(e)}")
                return None
        
        try:
            # 记住这个目录，下次保存时使用
            self._last_directory = os.path.dirname(file_path)
            
            # 根据文件扩展名确定保存参数
            params = self._get_format_params(file_path)
                
            # 保存图像
            from ..utils.image_utils import save_image_safely
            try:
                save_result = save_image_safely(image_data, file_path, params)
                
                if save_result:
                    # 添加到最近文件列表
                    self._add_to_recent_files(file_path)
                    return file_path
                else:
                    QMessageBox.critical(parent_widget, "错误", "保存失败，未知错误")
                    return None
                    
            except ValueError as ve:
                QMessageBox.critical(parent_widget, "错误", f"保存图像失败: {str(ve)}")
                return None
            
        except Exception as e:
            # 显示错误消息
            QMessageBox.critical(parent_widget, "错误", f"保存文件时出错: {str(e)}")
            return None

    def save_image_headless(self, image_data: np.ndarray, file_path: str, export_config: Optional[ExportConfig] = None) -> bool:
        """
        无UI交互的图像保存方法，适用于批处理。
        
        Args:
            image_data: 要保存的图像数据
            file_path: 保存路径
            export_config: (可选) 导出配置，用于获取格式化参数
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 根据文件扩展名确定保存参数
            params = None
            if export_config:
                # 使用传入的导出配置获取参数
                params = export_config.get_format_params(file_path)
            else:
                # 兼容旧逻辑，使用默认参数
                params = self._get_format_params(file_path)
                
            # 保存图像
            save_image_safely(image_data, file_path, params)
            
            # 添加到最近文件列表（可选，取决于是否需要将批处理的文件添加到最近文件列表）
            # self._add_to_recent_files(file_path)
            
            return True
            
        except Exception as e:
            # 记录错误但不显示UI
            print(f"保存文件时出错: {e}")
            return False
    
    def _get_format_params(self, file_path: str) -> Optional[List]:
        """
        根据文件扩展名获取格式特定的保存参数。
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[List]: 格式特定的参数列表，如果没有特定参数则返回None
        """
        params = None
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".jpg" or ext == ".jpeg":
            # JPEG质量设置为90%
            params = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        elif ext == ".png":
            # PNG压缩级别设置为9（最高压缩）
            params = [int(cv2.IMWRITE_PNG_COMPRESSION), 9]
        return params
            
    def _add_to_recent_files(self, file_path: str) -> None:
        """
        将文件添加到最近文件列表。
        
        Args:
            file_path: 要添加的文件路径。
        """
        # 如果文件已经在列表中，先移除它
        if file_path in self._recent_files:
            self._recent_files.remove(file_path)
            
        # 将文件添加到列表开头
        self._recent_files.insert(0, file_path)
        
        # 如果列表太长，移除最旧的文件
        if len(self._recent_files) > self._max_recent_files:
            self._recent_files = self._recent_files[:self._max_recent_files]
            
        # 发出信号通知最近文件列表已更改
        self.recent_files_changed.emit(self._recent_files) 

    def find_images_in_folder(self, folder_path: str, recursive: bool = False, file_types: Optional[List[str]] = None) -> List[str]:
        """
        在指定文件夹中查找图像文件。
        
        Args:
            folder_path: 要搜索的文件夹路径
            recursive: 是否递归搜索子文件夹
            file_types: 要查找的文件类型列表，如 [".jpg", ".png"]。如果为None，使用默认类型。
            
        Returns:
            List[str]: 找到的图像文件路径列表
        """
        if not folder_path or not os.path.isdir(folder_path):
            return []
            
        # 如果未指定文件类型，使用默认图像类型
        if not file_types:
            file_types = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
            
        # 收集所有符合条件的文件路径
        file_paths = []
        
        # 定义一个辅助函数来检查文件扩展名
        def is_valid_image_file(filename):
            return any(filename.lower().endswith(ext) for ext in file_types)
            
        # 遍历文件夹
        if recursive:
            # 递归搜索
            for root, _, files in os.walk(folder_path):
                for filename in files:
                    if is_valid_image_file(filename):
                        file_paths.append(os.path.join(root, filename))
        else:
            # 只搜索当前文件夹
            for filename in os.listdir(folder_path):
                if os.path.isfile(os.path.join(folder_path, filename)) and is_valid_image_file(filename):
                    file_paths.append(os.path.join(folder_path, filename))
                    
        return file_paths

    def is_supported_image_file(self, file_path: str) -> bool:
        """
        检查文件是否为支持的图像文件类型。
        
        Args:
            file_path: 要检查的文件路径
            
        Returns:
            bool: 如果是支持的图像文件则返回True
        """
        if not file_path or not os.path.isfile(file_path):
            return False
        
        # 支持的图像文件扩展名
        supported_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"]
        
        # 获取文件扩展名并转换为小写
        _, ext = os.path.splitext(file_path)
        return ext.lower() in supported_extensions

    def load_image_from_path(self, file_path: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        直接从文件路径加载图像，不显示文件对话框。
        
        Args:
            file_path: 图像文件的路径。
            
        Returns:
            Tuple[Optional[np.ndarray], Optional[str]]: 
                - 如果成功，返回 (图像数据, 文件路径)
                - 如果发生错误，返回 (None, file_path)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return None, file_path
                
            # 记住这个目录，下次打开时使用
            self._last_directory = os.path.dirname(file_path)
            
            # 加载图像
            image = load_image_safely(file_path)
            if image is None:
                print(f"无法加载图像文件: {file_path}")
                return None, file_path
                
            # 添加到最近文件列表
            self._add_to_recent_files(file_path)
                
            return image, file_path
            
        except Exception as e:
            # 记录错误但不显示UI
            print(f"加载文件时出错: {e}")
            return None, file_path
    
    def save_image(self, image: np.ndarray, file_path: str) -> None:
        """
        保存图像到文件（接口方法）
        
        Args:
            image: 图像数据
            file_path: 保存路径
        """
        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 根据文件扩展名确定保存参数
            params = self._get_format_params(file_path)
            
            # 保存图像
            save_image_safely(image, file_path, params)
            
            # 记住这个目录
            self._last_directory = os.path.dirname(file_path)
            
            # 添加到最近文件列表
            self._add_to_recent_files(file_path)
            
        except Exception as e:
            print(f"保存文件时出错: {e}")
            raise