"""
核心服务桥接适配器实现
提供核心层服务的统一访问点，复用UpperLayerServiceAdapter成功模式
"""

from typing import Any, Dict
from ..interfaces.core_service_interface import CoreServiceInterface


class CoreServiceAdapter(CoreServiceInterface):
    """核心服务桥接适配器 - 提供核心服务的统一访问接口"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
    
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """注册核心服务实例（由AppController调用）"""
        self._services[service_name] = service_instance
    
    def get_state_manager(self) -> Any:
        """获取状态管理器实例"""
        return self._services.get('state_manager')
    
    def get_config_accessor(self) -> Any:
        """获取配置访问器实例"""
        return self._services.get('config_accessor')
    
    def get_tool_manager(self) -> Any:
        """获取工具管理器实例"""
        return self._services.get('tool_manager')