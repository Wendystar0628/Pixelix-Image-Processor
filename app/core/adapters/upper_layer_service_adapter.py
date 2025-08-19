"""
上层服务桥接适配器实现
提供handlers和features层服务的统一访问点，复用ConfigAccessAdapter成功模式
"""

from typing import Any, Dict
from ..interfaces.upper_layer_service_interface import UpperLayerServiceInterface


class UpperLayerServiceAdapter(UpperLayerServiceInterface):
    """上层服务桥接适配器 - 提供上层服务的统一访问接口"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
    
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """注册服务实例（由DirectServiceInitializer调用）"""
        self._services[service_name] = service_instance
    
    def get_app_controller(self) -> Any:
        """获取应用控制器实例"""
        return self._services.get('app_controller')
    
    def get_file_handler(self) -> Any:
        """获取文件处理器实例"""
        return self._services.get('file_handler')
    
    def get_processing_handler(self) -> Any:
        """获取处理器实例"""
        return self._services.get('processing_handler')
    
    def get_preset_handler(self) -> Any:
        """获取预设处理器实例"""
        return self._services.get('preset_handler')
    
    def get_batch_processing_handler(self) -> Any:
        """获取批处理处理器实例"""
        return self._services.get('batch_processing_handler')