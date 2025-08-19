"""
命令模型模块

定义了命令的数据模型，用于表示命令的配置和参数。
"""
from typing import Dict, Any, Optional


class CommandModel:
    """
    命令模型，表示一个命令的配置和参数。
    
    命令模型可以被序列化和反序列化，用于保存和恢复命令历史。
    """
    
    def __init__(self, command_type: str, parameters: Optional[Dict[str, Any]] = None):
        """
        初始化一个命令模型。
        
        Args:
            command_type: 命令类型，如"add_operation", "remove_operation"等
            parameters: 命令参数字典
        """
        self.command_type = command_type
        self.parameters = parameters or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        将命令模型转换为字典，用于序列化。
        
        Returns:
            Dict[str, Any]: 包含命令模型数据的字典
        """
        return {
            "type": self.command_type,
            "params": self.parameters
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandModel':
        """
        从字典创建命令模型实例。
        
        Args:
            data: 包含命令模型数据的字典
            
        Returns:
            CommandModel: 创建的命令模型实例
        """
        return cls(
            command_type=data.get("type", ""),
            parameters=data.get("params", {})
        ) 