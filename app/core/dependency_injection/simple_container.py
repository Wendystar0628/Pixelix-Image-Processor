"""
简化的依赖注入容器
只管理实例注册和获取，不进行自动依赖解析
"""

import logging
from typing import Dict, Type, Any, TypeVar, Callable, Optional
from threading import RLock

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DependencyNotRegisteredException(Exception):
    """依赖未注册异常"""
    pass


class SimpleDependencyContainer:
    """
    简化的依赖注入容器
    
    只管理实例注册和获取，避免自动依赖解析导致的循环依赖问题
    """
    
    def __init__(self):
        self._instances: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._lock = RLock()
        
    def register_instance(self, interface_type: Type[T], instance: T) -> None:
        """
        注册已创建的实例
        
        Args:
            interface_type: 接口类型
            instance: 服务实例
        """
        with self._lock:
            self._instances[interface_type] = instance
            logger.debug(f"注册实例: {interface_type.__name__}")
    
    def register_factory(self, interface_type: Type[T], factory: Callable[[], T]) -> None:
        """
        注册工厂函数
        
        Args:
            interface_type: 接口类型
            factory: 创建实例的工厂函数
        """
        with self._lock:
            self._factories[interface_type] = factory
            logger.debug(f"注册工厂: {interface_type.__name__}")
    
    def get_instance(self, interface_type: Type[T]) -> T:
        """
        获取实例（不进行自动依赖解析）
        
        Args:
            interface_type: 要获取的接口类型
            
        Returns:
            服务实例
            
        Raises:
            DependencyNotRegisteredException: 依赖未注册
        """
        with self._lock:
            # 优先返回已注册的实例
            if interface_type in self._instances:
                return self._instances[interface_type]
            
            # 使用工厂创建实例
            if interface_type in self._factories:
                try:
                    instance = self._factories[interface_type]()
                    # 缓存工厂创建的实例
                    self._instances[interface_type] = instance
                    logger.debug(f"工厂创建实例: {interface_type.__name__}")
                    return instance
                except Exception as e:
                    logger.error(f"工厂创建实例失败 {interface_type.__name__}: {e}")
                    raise
            
            # 未找到注册的依赖
            raise DependencyNotRegisteredException(
                f"未注册的依赖: {interface_type.__name__}")
    
    def register_interface(self, interface_type: Type[T], implementation_type: Type[T], singleton: bool = True, dependencies: list = None) -> None:
        """
        注册接口到实现类的映射
        
        Args:
            interface_type: 接口类型
            implementation_type: 实现类类型
            singleton: 是否单例模式（目前总是True，因为resolve方法会缓存实例）
            dependencies: 构造函数依赖的接口类型列表
        """
        def factory() -> T:
            try:
                if dependencies:
                    # 解析构造函数依赖
                    resolved_deps = []
                    for dep_type in dependencies:
                        dep_instance = self.get_instance(dep_type)
                        resolved_deps.append(dep_instance)
                    return implementation_type(*resolved_deps)
                else:
                    return implementation_type()
            except Exception as e:
                logger.error(f"创建{implementation_type.__name__}实例失败: {e}")
                raise
        
        self.register_factory(interface_type, factory)
        logger.debug(f"注册接口映射: {interface_type.__name__} -> {implementation_type.__name__}, 依赖: {dependencies or '无'}")
    
    def resolve(self, interface_type: Type[T]) -> T:
        """
        解析依赖（get_instance的别名，兼容常见依赖注入容器API）
        
        Args:
            interface_type: 要解析的接口类型
            
        Returns:
            服务实例
        """
        return self.get_instance(interface_type)
    
    def has_instance(self, interface_type: Type) -> bool:
        """
        检查是否已注册实例或工厂
        
        Args:
            interface_type: 接口类型
            
        Returns:
            是否已注册
        """
        with self._lock:
            return (interface_type in self._instances or 
                    interface_type in self._factories)
    
    def clear(self) -> None:
        """清空所有注册的实例和工厂"""
        with self._lock:
            self._instances.clear()
            self._factories.clear()
            logger.debug("清空简化依赖容器")
    
    def list_registrations(self) -> Dict[str, str]:
        """获取所有注册的字符串表示"""
        with self._lock:
            result = {}
            for interface_type in self._instances:
                result[interface_type.__name__] = "实例"
            for interface_type in self._factories:
                result[interface_type.__name__] = "工厂"
            return result
    
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """获取诊断信息"""
        with self._lock:
            return {
                "registered_instances": len(self._instances),
                "registered_factories": len(self._factories),
                "total_registrations": len(self._instances) + len(self._factories),
                "instance_types": [t.__name__ for t in self._instances.keys()],
                "factory_types": [t.__name__ for t in self._factories.keys()]
            }