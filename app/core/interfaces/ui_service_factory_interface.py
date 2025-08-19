"""UI服务工厂接口"""

from abc import ABC, abstractmethod
from typing import Any


class UIServiceFactoryInterface(ABC):
    """UI服务工厂抽象接口
    
    定义UI服务创建的抽象接口，提供UI组件创建、依赖配置、服务组装等功能。
    核心层通过此接口创建所需的UI服务，避免直接依赖具体的UI工厂实现。
    """
    
    @abstractmethod
    def create_dialog_manager(self) -> 'DialogManagerInterface':
        """创建对话框管理器
        
        Returns:
            DialogManagerInterface: 对话框管理器接口实现
        """
        pass
    
    @abstractmethod
    def create_interactive_widget(self) -> 'InteractiveWidgetInterface':
        """创建交互组件
        
        Returns:
            InteractiveWidgetInterface: 交互组件接口实现
        """
        pass
    
    @abstractmethod
    def configure_ui_dependencies(self, main_window: Any) -> None:
        """配置UI依赖关系
        
        Args:
            main_window: 主窗口实例，用于获取UI组件引用
        """
        pass
    
    @abstractmethod
    def create_ui_services(self, main_window: Any, services: dict) -> None:
        """创建UI相关服务（向后兼容方法）
        
        Args:
            main_window: 主窗口实例
            services: 服务字典，用于存储创建的服务
        """
        pass