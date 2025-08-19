"""依赖注入桥接管理器"""
from typing import Any, Type
from .simple_container import SimpleDependencyContainer
from ..abstractions.config_access_interface import ConfigAccessInterface
from ..adapters.config_access_adapter import ConfigAccessAdapter
from app.layers.infrastructure.configuration.config_service_interface import ConfigServiceInterface


class InfrastructureBridge:
    """依赖注入桥接管理器"""
    
    def __init__(self, container: SimpleDependencyContainer):
        self._container = container
    
    def register_config_services(self, config_service: ConfigServiceInterface) -> None:
        """注册配置服务到依赖注入容器"""
        # 创建配置访问适配器
        config_adapter = ConfigAccessAdapter(config_service)
        
        # 注册抽象接口实现
        self._container.register_instance(ConfigAccessInterface, config_adapter)
        
        # 保留对基础设施服务的引用（如果需要直接访问）
        self._container.register_instance(ConfigServiceInterface, config_service)
    
    def register_service(self, interface_type: Type, service_instance: Any) -> None:
        """注册服务实例到容器"""
        self._container.register_instance(interface_type, service_instance)
    
    def get_service(self, interface_type: Type) -> Any:
        """从容器获取服务实例"""
        return self._container.get(interface_type)
    
    def has_service(self, interface_type: Type) -> bool:
        """检查容器中是否有指定服务"""
        try:
            self._container.get(interface_type)
            return True
        except Exception:
            return False