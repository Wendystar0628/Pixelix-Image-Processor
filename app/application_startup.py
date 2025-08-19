"""应用启动协调器"""
import sys
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QApplication

from app.layers.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from app.core.container.application_bootstrap import ApplicationBootstrap
from app.ui.main_window import MainWindow


class ApplicationStartup:
    """应用启动协调器"""
    
    def __init__(self, app: QApplication):
        self._app = app
        self._infrastructure_factory = InfrastructureFactory()
        self._bootstrap: Optional[ApplicationBootstrap] = None
        self._main_window: Optional[MainWindow] = None
        self._services: Dict[str, Any] = {}
    
    def start_application(self) -> int:
        """启动应用的完整流程"""
        try:
            print("="*50)
            print("数字图像处理工坊")
            print("="*50)
            
            # 1. 创建基础设施服务
            self._setup_infrastructure()
            
            # 2. 配置应用引导器
            self._setup_bootstrap()
            
            # 3. 初始化所有服务
            self._initialize_services()
            
            # 4. 创建和配置主窗口
            self._create_main_window()
            
            # 5. 创建UI服务
            self._create_ui_services()
            
            # 6. 设置UI接口实现
            self._setup_ui_interfaces()
            
            # 7. 配置可选依赖
            self._setup_optional_dependencies()
            
            # 8. 完成UI初始化
            self._complete_ui_initialization()
            
            # 9. 设置信号连接
            self._setup_signal_connections()
            
            # 10. 显示主窗口
            self._main_window.showMaximized()
            
            # 11. 注册清理回调
            self._app.aboutToQuit.connect(self._cleanup_services)
            
            return self._app.exec()
            
        except Exception as e:
            return self._handle_startup_error(e)
    
    def _setup_infrastructure(self) -> None:
        """设置基础设施服务"""
        print("开始设置基础设施服务...")
        # 基础设施服务已通过工厂创建
        print("基础设施服务设置完成")
    
    def _setup_bootstrap(self) -> None:
        """配置应用引导器"""
        print("开始配置应用引导器...")
        
        # 创建配置服务
        config_service = self._infrastructure_factory.create_config_service()
        config = config_service.get_config()
        
        # 初始化应用引导器
        self._bootstrap = ApplicationBootstrap(config, config_service)
        
        if not self._bootstrap.bootstrap_application():
            raise RuntimeError("应用引导失败")
            
        print("应用引导器配置完成")
    
    def _initialize_services(self) -> None:
        """初始化所有服务"""
        print("开始初始化所有服务...")
        
        self._services = self._bootstrap.initialize_all_services()
        
        # 验证核心服务
        required_core_services = ['image_processor', 'state_manager', 'analysis_calculator', 'config_registry', 'app_controller']
        for service_name in required_core_services:
            if service_name not in self._services or self._services[service_name] is None:
                raise RuntimeError(f"核心服务 {service_name} 初始化失败")
        
        print("所有服务初始化完成")
    
    def _create_main_window(self) -> None:
        """创建主窗口"""
        print("开始创建MainWindow...")
        
        # 验证AppController可用性
        app_controller = self._services.get('app_controller')
        if not app_controller:
            raise RuntimeError("AppController未创建或未正确配置")
        
        # 验证桥接适配器配置
        if not hasattr(app_controller, 'get_core_service_adapter'):
            raise RuntimeError("AppController桥接适配器未配置")
        
        core_adapter = app_controller.get_core_service_adapter()
        if not core_adapter:
            raise RuntimeError("核心服务桥接适配器未初始化")
        
        # 验证核心服务注册
        if not core_adapter.get_state_manager():
            raise RuntimeError("StateManager未注册到桥接适配器")
        
        print("开始创建MainWindow...")
        
        # 验证AppController的桥接适配器配置
        if hasattr(app_controller, 'verify_bridge_adapter_configuration'):
            app_controller.verify_bridge_adapter_configuration()
        
        self._main_window = MainWindow(
            image_processor=self._services['image_processor'],
            state_manager=self._services['state_manager'],
            analysis_calculator=self._services['analysis_calculator'],
            config_registry=self._services['config_registry'],
            app_controller=app_controller,  # 传递AppController
            batch_processing_handler=self._services.get('batch_processing_handler')
        )
        
        print("MainWindow创建完成")
    
    def _create_ui_services(self) -> None:
        """创建UI服务"""
        print("开始创建UI服务...")
        self._bootstrap.create_ui_services(self._main_window)
        print("UI服务创建完成")
    
    def _setup_ui_interfaces(self) -> None:
        """设置UI接口实现"""
        print("开始创建UI接口实现...")
        
        from app.ui.integration import InterfaceIntegrationManager
        integration_manager = InterfaceIntegrationManager()
        
        if integration_manager.setup_ui_interfaces(self._bootstrap, self._main_window, self._services):
            print("UI接口实现创建完成")
        else:
            print("警告：部分UI接口实现设置失败")
    
    def _setup_optional_dependencies(self) -> None:
        """设置可选依赖"""
        print("开始设置可选依赖...")
        
        # 获取可选服务
        app_controller = self._services.get('app_controller')
        batch_processing_handler = self._services.get('batch_processing_handler')
        file_handler = self._services.get('file_handler')
        
        # 验证可选服务并设置
        if app_controller:
            self._main_window.app_controller = app_controller
            print("应用控制器设置完成")
        else:
            print("警告：应用控制器未创建")
            
        if batch_processing_handler:
            self._main_window.batch_processing_handler = batch_processing_handler
            print("批处理处理器设置完成")
        else:
            print("警告：批处理处理器未创建")
            
        if file_handler:
            self._main_window.file_handler = file_handler
            print("文件处理器设置完成")
        else:
            print("警告：文件处理器未创建")
    
    def _complete_ui_initialization(self) -> None:
        """完成UI初始化"""
        print("开始完成UI初始化...")
        self._main_window.complete_ui_initialization()
        print("UI初始化完成")
    
    def _setup_signal_connections(self) -> None:
        """设置信号连接"""
        print("开始设置信号连接...")
        
        # 获取服务
        batch_processing_handler = self._services.get('batch_processing_handler')
        processing_handler = self._services.get('processing_handler')
        app_controller = self._services.get('app_controller')
        
        # 连接错误信号
        if hasattr(self._main_window, '_show_error_message'):
            if batch_processing_handler:
                batch_processing_handler.show_error_message.connect(self._main_window._show_error_message)
            if processing_handler:
                processing_handler.show_error_message.connect(self._main_window._show_error_message)
            if app_controller:
                app_controller.show_error_message.connect(self._main_window._show_error_message)
        
        # 连接信息信号
        if hasattr(self._main_window, '_show_info_message'):
            if batch_processing_handler:
                batch_processing_handler.show_info_message.connect(self._main_window._show_info_message)
            if app_controller:
                app_controller.show_info_message.connect(self._main_window._show_info_message)
        
        # 连接图像信号
        if hasattr(self._main_window, '_on_image_loaded') and app_controller:
            app_controller.image_loaded.connect(self._main_window._on_image_loaded)
        if hasattr(self._main_window, '_on_image_saved') and app_controller:
            app_controller.image_saved.connect(self._main_window._on_image_saved)
        
        print("信号连接设置完成")
    
    def _cleanup_services(self) -> None:
        """清理服务"""
        print("开始清理服务...")
        if self._bootstrap:
            try:
                self._bootstrap.shutdown()
                print("服务清理完成")
            except Exception as e:
                print(f"服务清理过程中出现警告: {e}")
                print("继续关闭应用...")
    
    def _handle_startup_error(self, error: Exception) -> int:
        """处理启动错误"""
        import traceback
        print(f"应用启动失败: {error}")
        print("详细错误信息:")
        traceback.print_exc()
        
        # 尝试清理资源
        try:
            if self._bootstrap:
                self._bootstrap.cleanup_services()
                print("资源清理完成")
        except Exception as cleanup_error:
            print(f"资源清理失败: {cleanup_error}")
        
        return 1