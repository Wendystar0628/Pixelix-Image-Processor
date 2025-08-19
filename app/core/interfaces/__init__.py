"""
核心服务接口模块

定义了应用中主要服务的抽象接口，实现依赖注入和控制反转。
"""

from .image_processor_interface import ImageProcessorInterface
from .state_manager_interface import StateManagerInterface
from .app_controller_interface import AppControllerInterface
from .handler_interface_base import BaseHandlerInterface, HandlerInterfaceMeta
from .file_handler_interface import FileHandlerInterface
from .processing_handler_interface import ProcessingHandlerInterface
from .preset_handler_interface import PresetHandlerInterface

# UI抽象接口
from .interactive_widget_interface import InteractiveWidgetInterface
from .dialog_manager_interface import DialogManagerInterface
from .ui_service_factory_interface import UIServiceFactoryInterface

# 桥接接口
from .core_service_interface import CoreServiceInterface


__all__ = [
    'ImageProcessorInterface',
    'StateManagerInterface', 
    'AppControllerInterface',
    'BaseHandlerInterface',
    'HandlerInterfaceMeta',
    'FileHandlerInterface',
    'ProcessingHandlerInterface',
    'PresetHandlerInterface',
    
    # UI抽象接口
    'InteractiveWidgetInterface',
    'DialogManagerInterface',
    'UIServiceFactoryInterface',
    
    # 桥接接口
    'CoreServiceInterface',
]