"""
操作模型模块

定义了图像处理操作的数据模型，用于表示操作的配置和参数。
"""
from typing import Dict, Any, Optional


class OperationModel:
    """
    操作模型，表示一个图像处理操作的配置和参数。
    
    操作模型可以被序列化和反序列化，用于保存和恢复操作配置。
    """
    
    def __init__(self, operation_type: str, parameters: Optional[Dict[str, Any]] = None):
        """
        初始化一个操作模型。
        
        Args:
            operation_type: 操作类型，如"brightness_contrast", "grayscale"等
            parameters: 操作参数字典
        """
        self.operation_type = operation_type
        self.parameters = parameters or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        将操作模型转换为字典，用于序列化。
        
        Returns:
            Dict[str, Any]: 包含操作模型数据的字典
        """
        return {
            "type": self.operation_type,
            "params": self.parameters
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OperationModel':
        """
        从字典创建操作模型实例。
        
        Args:
            data: 包含操作模型数据的字典
            
        Returns:
            OperationModel: 创建的操作模型实例
        """
        return cls(
            operation_type=data.get("type", ""),
            parameters=data.get("params", {})
        ) 