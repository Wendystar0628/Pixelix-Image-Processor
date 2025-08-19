"""
图像仓库模块

负责管理图像资源，包括原始图像和代理图像。
"""

from typing import Optional
import numpy as np


class ImageRepository:
    """
    负责管理图像资源，包括原始图像和代理图像。
    
    主要职责:
    1. 存储和管理原始高分辨率图像
    2. 存储和管理低分辨率代理图像
    3. 控制显示模式（原始/代理）
    4. 提供图像访问接口
    """

    def __init__(self):
        # 图像数据
        self._original_image: Optional[np.ndarray] = None  # 原始高分辨率图像
        self._proxy_image: Optional[np.ndarray] = None     # 代理低分辨率图像
        
        # 显示模式
        self._use_proxy_mode: bool = True  # 默认使用代理模式
        
        # 图像元数据
        self.canvas_width: int = 0
        self.canvas_height: int = 0
        self.current_file_path: Optional[str] = None  # 当前文件路径
    
    # ----- 向后兼容属性 -----
    
    @property
    def original_image(self) -> Optional[np.ndarray]:
        """
        向后兼容属性访问器 - 获取原始图像
        
        Returns:
            Optional[np.ndarray]: 原始图像或None
        """
        return self._original_image
        
    # ----- 图像访问方法 -----
        
    def get_image_for_processing(self) -> Optional[np.ndarray]:
        """
        获取用于处理的原始图像。
        
        此方法始终返回原始高分辨率图像的副本，无论当前的显示模式是什么。
        如果原始图像未加载，则返回None。
        
        Returns:
            Optional[np.ndarray]: 原始图像的副本，或None
        """
        return self._original_image.copy() if self._original_image is not None else None
        
    def get_image_for_display(self) -> Optional[np.ndarray]:
        """
        获取用于显示的图像（根据当前模式返回原始图像或代理图像）。
        
        根据当前设置的显示模式，返回:
        - 代理模式: 返回低分辨率代理图像的副本（如果存在）
        - 原始模式: 返回高分辨率原始图像的副本
        - 无图像: 返回None
        
        Returns:
            Optional[np.ndarray]: 当前模式下应该显示的图像的副本，或None
        """
        if self._use_proxy_mode and self._proxy_image is not None:
            return self._proxy_image.copy()
        elif self._original_image is not None:
            return self._original_image.copy()
        return None
        
    def is_image_loaded(self) -> bool:
        """检查当前是否有任何图像被加载（无论是原始图像还是代理图像）。"""
        return self._original_image is not None or self._proxy_image is not None
        
    # ----- 图像加载方法 -----
        
    def load_image(self, image: np.ndarray, file_path: Optional[str] = None) -> None:
        """
        加载一个新原始图像。
        
        Args:
            image (np.ndarray): 要加载的图像数据
            file_path (Optional[str]): 图像文件路径
        """
        if image is not None:
            self.canvas_height, self.canvas_width = image.shape[:2]
            self._original_image = image
            self.current_file_path = file_path
            # 清除旧的代理图像
            self._proxy_image = None
            
    def set_proxy_image(self, proxy_image: np.ndarray) -> None:
        """
        设置代理图像。
        
        Args:
            proxy_image (np.ndarray): 代理图像数据
        """
        if proxy_image is not None:
            self._proxy_image = proxy_image
            
    def has_proxy_image(self) -> bool:
        """检查当前是否有代理图像。"""
        return self._proxy_image is not None
            
    # ----- 显示模式控制 -----
    
    def use_proxy_mode(self) -> bool:
        """
        检查当前是否处于代理图像显示模式。
        
        Returns:
            bool: 如果当前处于代理模式则返回True，否则返回False
        """
        return self._use_proxy_mode
        
    def switch_to_proxy_mode(self) -> None:
        """
        切换到代理图像显示模式。
        
        在此模式下，get_image_for_display将返回低分辨率代理图像。
        """
        self._use_proxy_mode = True
        
    def switch_to_original_mode(self) -> None:
        """
        切换到原始图像显示模式。
        
        在此模式下，get_image_for_display将返回完整分辨率的原始图像。
        """
        self._use_proxy_mode = False
        
    # ----- 文件路径管理 -----
        
    def get_current_file_path(self) -> Optional[str]:
        """
        获取当前打开的文件路径。

        Returns:
            Optional[str]: 当前文件路径，如果没有打开文件则返回None
        """
        return self.current_file_path
        
    def set_current_file_path(self, file_path: str) -> None:
        """
        设置当前文件路径。
        
        Args:
            file_path: 新的文件路径
        """
        self.current_file_path = file_path 