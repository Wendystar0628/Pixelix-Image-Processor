"""
服务管理器 - 替代ApplicationBootstrap中的services字典
"""

import logging
from typing import Dict, Any


class ServiceManager:
    """服务管理器 - 专门管理服务实例的存储和获取"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)
    
    def register_service(self, name: str, service: Any) -> None:
        """注册服务实例"""
        if name in self._services:
            self._logger.warning(f"服务 {name} 已存在，将被覆盖")
        self._services[name] = service
        self._logger.debug(f"注册服务: {name}")
    
    def get_service(self, name: str) -> Any:
        """获取单个服务实例"""
        if name not in self._services:
            raise KeyError(f"服务 {name} 未找到")
        return self._services[name]
    
    def get_all_services(self) -> Dict[str, Any]:
        """获取所有服务，与现有bootstrap.services用法兼容"""
        return self._services.copy()
    
    def clear_all(self) -> None:
        """清空所有服务"""
        self._services.clear()
        self._logger.debug("已清空所有服务")