"""
预设模型模块

定义了预设（Preset）数据模型，用于保存和加载一系列图像处理操作。
"""
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime


class PresetModel:
    """
    预设模型，表示一系列可以应用于图像的操作及其参数。
    
    预设可以被保存为JSON文件，并在以后加载和应用到图像上。
    """
    
    def __init__(self, name: str, operations: Optional[List[Dict[str, Any]]] = None, 
                 description: str = "", created_at: Optional[str] = None):
        """
        初始化一个预设。
        
        Args:
            name: 预设名称
            operations: 操作列表，每个操作是一个字典，包含操作名称和参数
            description: 预设描述
            created_at: 创建时间，如果为None则使用当前时间
        """
        self.name = name
        self.operations = operations or []
        self.description = description
        self.created_at = created_at or datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        将预设转换为字典，用于序列化。
        
        Returns:
            Dict[str, Any]: 包含预设数据的字典
        """
        return {
            "name": self.name,
            "operations": self.operations,
            "description": self.description,
            "created_at": self.created_at
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PresetModel':
        """
        从字典创建预设实例。
        
        Args:
            data: 包含预设数据的字典
            
        Returns:
            PresetModel: 创建的预设实例
        """
        return cls(
            name=data.get("name", "未命名预设"),
            operations=data.get("operations", []),
            description=data.get("description", ""),
            created_at=data.get("created_at")
        ) 