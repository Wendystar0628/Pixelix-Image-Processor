"""UI接口实现集成管理器

负责创建、配置和注册所有UI接口实现到依赖注入容器中
确保Core层通过接口与UI层解耦
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class InterfaceIntegrationManager:
    """UI接口实现集成管理器
    
    职责：
    1. 创建所有UI接口实现（DialogImplementation, WidgetImplementation等）
    2. 将接口实现注册到依赖注入容器
    3. 管理UI接口实现的生命周期
    4. 提供统一的UI接口集成入口点
    
    设计原则：
    - UI接口实现的创建由UI层负责，符合分层架构
    - Core层只依赖接口，不直接导入UI实现类
    - 通过依赖注入容器实现松耦合
    """
    
    def __init__(self):
        """初始化集成管理器"""
        self._ui_implementations = {}
        self._logger = logger
    
    def setup_ui_interfaces(self, bootstrap, main_window, services: Dict[str, Any]) -> bool:
        """设置所有UI接口实现
        
        Args:
            bootstrap: ApplicationBootstrap实例
            main_window: 主窗口实例
            services: 服务字典
            
        Returns:
            bool: 是否成功设置所有UI接口
        """
        try:
            self._logger.info("开始设置UI接口实现...")
            
            # 导入UI实现类（仅在UI层导入）
            if not self._import_ui_implementations():
                return False
            
            # 创建并注册各种UI接口实现（直接注册到services字典）
            success = True
            success &= self._setup_ui_factory_implementation(bootstrap, services)
            success &= self._setup_dialog_manager_implementation(services)
            success &= self._setup_interactive_widget_implementation(main_window, services)
            
            if success:
                self._logger.info("所有UI接口实现设置完成")
            else:
                self._logger.warning("部分UI接口实现设置失败，应用将继续运行")
            
            return success
            
        except Exception as e:
            self._logger.error(f"设置UI接口实现时发生异常: {e}")
            return False
    
    def _import_ui_implementations(self) -> bool:
        """导入所有UI实现类
        
        Returns:
            bool: 是否成功导入所有实现类
        """
        try:
            self._logger.debug("导入UI实现类...")
            from ..implementations import (
                UIFactoryImplementation,
                DialogImplementation,
                WidgetImplementation
            )
            
            # 存储类引用，避免重复导入
            self._ui_implementations = {
                'UIFactoryImplementation': UIFactoryImplementation,
                'DialogImplementation': DialogImplementation,
                'WidgetImplementation': WidgetImplementation
            }
            
            self._logger.debug("UI实现类导入完成")
            return True
            
        except ImportError as e:
            self._logger.error(f"无法导入UI实现类: {e}")
            return False
    
    def _setup_ui_factory_implementation(self, bootstrap, services: Dict[str, Any]) -> bool:
        """设置UI工厂接口实现
        
        Args:
            bootstrap: ApplicationBootstrap实例
            services: 服务字典
            
        Returns:
            bool: 是否成功设置
        """
        try:
            self._logger.debug("创建UI工厂实现...")
            
            UIFactoryImplementation = self._ui_implementations.get('UIFactoryImplementation')
            if not UIFactoryImplementation:
                self._logger.error("UIFactoryImplementation类未找到")
                return False
            
            # 获取core层的UI服务工厂
            ui_service_factory = bootstrap.ui_service_factory
            ui_factory_impl = UIFactoryImplementation(ui_service_factory)
            
            # 直接注册到服务字典
            services['ui_factory_interface'] = ui_factory_impl
            
            self._logger.debug("UIServiceFactoryInterface实现已注册")
            return True
            
        except Exception as e:
            self._logger.error(f"设置UI工厂实现失败: {e}")
            return False
    
    def _setup_dialog_manager_implementation(self, services: Dict[str, Any]) -> bool:
        """设置对话框管理器接口实现
        
        Args:
            services: 服务字典
            
        Returns:
            bool: 是否成功设置
        """
        try:
            self._logger.debug("创建对话框管理器实现...")
            
            DialogImplementation = self._ui_implementations.get('DialogImplementation')
            if not DialogImplementation:
                self._logger.error("DialogImplementation类未找到")
                return False
            
            # 由于UIServiceFactory不再创建DialogManager，我们需要在这里创建
            dialog_manager = self._create_dialog_manager(services)
            if not dialog_manager:
                self._logger.error("无法创建DialogManager")
                return False
            
            # 将DialogManager添加到services中（向后兼容）
            services['dialog_manager'] = dialog_manager
            
            # 设置AppController的DialogManager（保持向后兼容）
            app_controller = services.get('app_controller')
            if app_controller and hasattr(app_controller, 'set_dialog_manager'):
                app_controller.set_dialog_manager(dialog_manager)
                self._logger.debug("已设置AppController的DialogManager")
            
            # 创建接口实现（适配器模式）
            dialog_manager_impl = DialogImplementation(dialog_manager)
            
            # 直接注册到服务字典
            services['dialog_manager_interface'] = dialog_manager_impl
            
            self._logger.debug("DialogManagerInterface实现已注册")
            return True
            
        except Exception as e:
            self._logger.error(f"设置对话框管理器实现失败: {e}")
            return False
    
    def _setup_interactive_widget_implementation(self, main_window, services: Dict[str, Any]) -> bool:
        """设置交互组件接口实现
        
        Args:
            main_window: 主窗口实例
            services: 服务字典
            
        Returns:
            bool: 是否成功设置
        """
        try:
            self._logger.debug("创建交互组件实现...")
            
            WidgetImplementation = self._ui_implementations.get('WidgetImplementation')
            if not WidgetImplementation:
                self._logger.error("WidgetImplementation类未找到")
                return False
            
            # 从主窗口获取交互式图像标签
            interactive_image_label = self._get_interactive_image_label(main_window)
            if not interactive_image_label:
                self._logger.warning("无法获取interactive_image_label，交互功能可能不可用")
                return False
            
            # 创建接口实现（适配器模式）
            interactive_widget_impl = WidgetImplementation(interactive_image_label)
            
            # 直接注册到服务字典
            services['interactive_widget_interface'] = interactive_widget_impl
            
            self._logger.debug("InteractiveWidgetInterface实现已注册")
            return True
            
        except Exception as e:
            self._logger.error(f"设置交互组件实现失败: {e}")
            return False
    
    def _get_interactive_image_label(self, main_window):
        """从主窗口获取交互式图像标签
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            交互式图像标签实例或None
        """
        try:
            # 检查主窗口结构
            if not hasattr(main_window, 'image_view_panel'):
                self._logger.warning("主窗口没有image_view_panel属性")
                return None
            
            image_view_panel = main_window.image_view_panel
            if not hasattr(image_view_panel, 'image_label'):
                self._logger.warning("image_view_panel没有image_label属性")
                return None
            
            interactive_image_label = image_view_panel.image_label
            self._logger.debug("成功获取interactive_image_label")
            return interactive_image_label
            
        except Exception as e:
            self._logger.error(f"获取interactive_image_label失败: {e}")
            return None
    
    def get_ui_implementation(self, interface_name: str):
        """获取指定的UI接口实现
        
        Args:
            interface_name: 接口名称
            
        Returns:
            对应的UI接口实现实例或None
        """
        return self._ui_implementations.get(interface_name)
    
    def _create_dialog_manager(self, services: Dict[str, Any]):
        """创建DialogManager实例
        
        Args:
            services: 服务字典，包含所需的依赖服务
            
        Returns:
            DialogManager实例或None
        """
        try:
            # 导入DialogManager类（在UI层导入是合适的）
            from ..managers.dialog_manager import DialogManager
            
            # 获取必要的服务
            state_manager = services.get('state_manager')
            processing_handler = services.get('processing_handler')
            preset_handler = services.get('preset_handler')  # 可能为None
            
            if not state_manager:
                self._logger.error("创建DialogManager失败：缺少state_manager")
                return None
                
            if not processing_handler:
                self._logger.error("创建DialogManager失败：缺少processing_handler")
                return None
            
            # 获取app_controller
            app_controller = services.get('app_controller')
            if not app_controller:
                self._logger.error("创建DialogManager失败：缺少app_controller")
                return None
            
            # 创建DialogManager实例
            # parent参数暂时设为None，可以后续通过set_parent设置
            dialog_manager = DialogManager(
                app_controller=app_controller,
                processing_handler=processing_handler,
                preset_handler=preset_handler,
                parent=None  # 主窗口引用在需要时设置
            )
            
            self._logger.debug("DialogManager创建成功")
            return dialog_manager
            
        except ImportError as e:
            self._logger.error(f"无法导入DialogManager: {e}")
            return None
        except Exception as e:
            self._logger.error(f"创建DialogManager失败: {e}")
            return None
    
    def cleanup(self):
        """清理资源"""
        self._logger.debug("清理UI接口集成管理器资源")
        self._ui_implementations.clear()