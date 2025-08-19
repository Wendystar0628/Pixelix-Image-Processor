from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np


class ImageOperation(ABC):
    """
    所有图像处理操作的抽象基类。

    每个操作都是一个无状态的配置对象，它定义了一个 `apply` 方法
    来将特定的图像处理算法应用于输入的图像上。
    """

    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        将此操作应用于给定的图像。

        Args:
            image (np.ndarray): 输入的图像，格式为NumPy数组。

        Returns:
            np.ndarray: 处理后的图像，格式为NumPy数组。
        """
        pass
        
    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        """
        获取此操作的参数。
        
        Returns:
            Dict[str, Any]: 包含操作参数的字典。
        """
        pass 
        
    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """
        将此操作序列化为字典，用于保存到预设中。
        
        Returns:
            Dict[str, Any]: 包含操作类型和参数的字典。
        """
        pass 