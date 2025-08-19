"""
操作流水线管理器模块 - 兼容层

此模块现在是一个兼容层，将 StateManager 重新导出为 OperationPipelineManager，
以保持向后兼容性。所有操作流水线管理功能已经集成到 StateManager 中。

在新代码中，请直接使用 StateManager 的方法而不是这个模块。
"""

import warnings
from typing import Dict, List, Optional, Any

from ..operations.base_operation import ImageOperation
from .state_manager import StateManager
from ..services.persistence_service import PersistenceService
from .pipeline_manager import PipelineManager


# 发出废弃警告
warnings.warn(
    "OperationPipelineManager 已被集成到 StateManager 中，请直接使用 StateManager 的方法。",
    DeprecationWarning,
    stacklevel=2
)


class OperationPipelineManager:
    """
    操作流水线管理器类 - 兼容层
    
    此类现在是一个包装器，将所有方法委托给 StateManager。
    为了保持向后兼容性而保留。
    
    在新代码中，请直接使用 StateManager 的方法。
    """
    
    def __init__(self, persistence_service: Optional['PersistenceService'] = None):
        """初始化操作流水线管理器
        
        Args:
            persistence_service: 持久化服务实例
        """
        self.persistence_service = persistence_service or PersistenceService()
    
    def serialize_operation(self, operation: ImageOperation) -> Dict[str, Any]:
        """委托给 PersistenceService.serialize_operation"""
        return self.persistence_service.serialize_operation(operation)
        
    def deserialize_operation(self, serialized: Dict[str, Any]) -> Optional[ImageOperation]:
        """委托给 PersistenceService.deserialize_operation"""
        return self.persistence_service.deserialize_operation(serialized)
            
    def serialize_pipeline(self, pipeline: List[ImageOperation]) -> List[Dict[str, Any]]:
        """委托给 StateManager.serialize_operation"""
        return [self.serialize_operation(op) for op in pipeline]
        
    def deserialize_pipeline(self, serialized: List[Dict[str, Any]]) -> List[ImageOperation]:
        """委托给 StateManager.deserialize_pipeline"""
        return [self.deserialize_operation(item) for item in serialized if self.deserialize_operation(item)]
        
    def save_pipeline_to_file(self, pipeline: List[ImageOperation], file_path: str) -> bool:
        """委托给 StateManager.save_pipeline_to_file"""
        pipeline_manager = PipelineManager()
        pipeline_manager.set_pipeline(pipeline)
        return self.persistence_service.save_pipeline_to_file(pipeline_manager, file_path)
            
    def load_pipeline_from_file(self, file_path: str) -> Optional[List[ImageOperation]]:
        """委托给 StateManager.load_pipeline_from_file"""
        return self.persistence_service.load_pipeline_from_file(file_path)
            
    def clone_pipeline(self, pipeline: List[ImageOperation]) -> List[ImageOperation]:
        """委托给 StateManager.clone_pipeline"""
        return self.persistence_service.clone_pipeline(pipeline) 