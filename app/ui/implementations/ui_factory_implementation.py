"""UI服务工厂接口实现"""

import logging
from typing import Any

from app.core.interfaces import UIServiceFactoryInterface, DialogManagerInterface, InteractiveWidgetInterface
from .dialog_implementation import DialogImplementation
from .widget_implementation import WidgetImplementation

logger = logging.getLogger(__name__)


class UIFactoryImplementation(UIServiceFactoryInterface):
    """UI服务工厂接口实现
    
    将UIServiceFactory适配为UIServiceFactoryInterface，
    为核心层提供UI服务创建能力的接口实现。
    """
    
    def __init__(self, ui_service_factory=None):
        """初始化UI服务工厂实现
        
        Args:
            ui_service_factory: UIServiceFactory实例，如果为None则创建新实例
        """
        self._ui_service_factory = ui_service_factory
        if self._ui_service_factory is None:
            # 创建默认的UI服务工厂
            from app.core.container.ui_service_factory import UIServiceFactory
            self._ui_service_factory = UIServiceFactory()
        
        # 缓存创建的接口实例
        self._dialog_manager_impl: DialogManagerInterface = None
        self._interactive_widget_impl: InteractiveWidgetInterface = None
        self._main_window = None
    
    def create_dialog_manager(self) -> DialogManagerInterface:
        """创建对话框管理器
        
        Returns:
            DialogManagerInterface: 对话框管理器接口实现
        """
        try:
            if self._dialog_manager_impl is None:
                # 获取原始的DialogManager
                dialog_manager = self._ui_service_factory.get_dialog_manager()
                if dialog_manager is None:
                    # 如果还没有创建，先创建UI服务
                    logger.warning("DialogManager尚未创建，可能需要先调用create_ui_services")
                    return None
                
                # 创建接口实现
                self._dialog_manager_impl = DialogImplementation(dialog_manager)
                logger.info("已创建DialogManagerInterface实现")
            
            return self._dialog_manager_impl
            
        except Exception as e:
            logger.error(f"创建对话框管理器失败: {e}")
            return None
    
    def create_interactive_widget(self) -> InteractiveWidgetInterface:
        """创建交互组件
        
        Returns:
            InteractiveWidgetInterface: 交互组件接口实现
        """
        try:
            if self._interactive_widget_impl is None:
                # 从主窗口获取交互组件
                if self._main_window is None:
                    logger.warning("主窗口未设置，无法创建交互组件")
                    return None
                
                # 尝试获取交互式图像标签
                interactive_widget = None
                if hasattr(self._main_window, 'get_interactive_image_label'):
                    interactive_widget = self._main_window.get_interactive_image_label()
                elif hasattr(self._main_window, 'interactive_image_label'):
                    interactive_widget = self._main_window.interactive_image_label
                elif hasattr(self._main_window, 'image_view_panel'):
                    # 从图像视图面板获取
                    image_view_panel = self._main_window.image_view_panel
                    if hasattr(image_view_panel, 'interactive_image_label'):
                        interactive_widget = image_view_panel.interactive_image_label
                
                if interactive_widget is None:
                    logger.warning("无法找到交互式图像组件")
                    return None
                
                # 创建接口实现
                self._interactive_widget_impl = WidgetImplementation(interactive_widget)
                logger.info("已创建InteractiveWidgetInterface实现")
            
            return self._interactive_widget_impl
            
        except Exception as e:
            logger.error(f"创建交互组件失败: {e}")
            return None
    
    def configure_ui_dependencies(self, main_window: Any) -> None:
        """配置UI依赖关系
        
        Args:
            main_window: 主窗口实例，用于获取UI组件引用
        """
        try:
            self._main_window = main_window
            
            # 调用原始工厂的配置方法
            if hasattr(self._ui_service_factory, 'configure_ui_dependencies'):
                self._ui_service_factory.configure_ui_dependencies(main_window)
            
            logger.info("UI依赖关系配置完成")
            
        except Exception as e:
            logger.error(f"配置UI依赖关系失败: {e}")
    
    def create_ui_services(self, main_window: Any, services: dict) -> None:
        """创建UI相关服务（向后兼容方法）
        
        Args:
            main_window: 主窗口实例
            services: 服务字典，用于存储创建的服务
        """
        try:
            # 存储主窗口引用
            self._main_window = main_window
            
            # 调用原始工厂的创建方法
            if hasattr(self._ui_service_factory, 'create_ui_services'):
                self._ui_service_factory.create_ui_services(main_window, services)
            
            # 创建接口实现并添加到服务字典
            dialog_manager_impl = self.create_dialog_manager()
            if dialog_manager_impl:
                services['dialog_manager_interface'] = dialog_manager_impl
            
            interactive_widget_impl = self.create_interactive_widget()
            if interactive_widget_impl:
                services['interactive_widget_interface'] = interactive_widget_impl
            
            logger.info("UI服务创建完成（通过接口实现）")
            
        except Exception as e:
            logger.error(f"创建UI服务失败: {e}")
    
    # 额外的便利方法
    def get_ui_service_factory(self):
        """获取原始UIServiceFactory实例
        
        Returns:
            原始的UIServiceFactory实例
        """
        return self._ui_service_factory
    
    def set_main_window(self, main_window: Any) -> None:
        """设置主窗口引用
        
        Args:
            main_window: 主窗口实例
        """
        self._main_window = main_window
    
    def get_main_window(self) -> Any:
        """获取主窗口引用
        
        Returns:
            主窗口实例
        """
        return self._main_window
    
    def reset_cache(self) -> None:
        """重置缓存的接口实例
        
        用于在UI组件重新创建时清理缓存
        """
        self._dialog_manager_impl = None
        self._interactive_widget_impl = None
        logger.info("UI接口实现缓存已重置")