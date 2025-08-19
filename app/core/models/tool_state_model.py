"""
工具状态模型模块

定义了工具状态的数据模型，用于保存和恢复工具的状态。
"""
from typing import Dict, Any, Optional


class ToolStateModel:
    """
    工具状态模型，表示一个工具的状态数据。
    
    工具状态包括工具的配置参数、当前状态等信息，
    可以被序列化和反序列化，用于保存和恢复工具状态。
    """
    
    def __init__(self, tool_name: str, parameters: Optional[Dict[str, Any]] = None):
        """
        初始化一个工具状态模型。
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数字典
        """
        self.tool_name = tool_name
        self.parameters = parameters or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        将工具状态转换为字典，用于序列化。
        
        Returns:
            Dict[str, Any]: 包含工具状态数据的字典
        """
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolStateModel':
        """
        从字典创建工具状态实例。
        
        Args:
            data: 包含工具状态数据的字典
            
        Returns:
            ToolStateModel: 创建的工具状态实例
        """
        return cls(
            tool_name=data.get("tool_name", ""),
            parameters=data.get("parameters", {})
        ) 