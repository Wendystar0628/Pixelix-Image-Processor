"""
直接服务初始化器
替代ServiceLocator模式，按层次直接创建服务
"""

import logging
from typing import Dict, Any

from app.models.app_config import AppConfig
from app.layers.infrastructure.configuration.config_service_interface import ConfigServiceInterface
from ..dependency_injection.simple_container import SimpleDependencyContainer
from ..dependency_injection.service_builder import ServiceBuilder
from ..dependency_injection.infrastructure_bridge import InfrastructureBridge
from ..adapters.upper_layer_service_adapter import UpperLayerServiceAdapter
from ..interfaces.upper_layer_service_interface import UpperLayerServiceInterface

logger = logging.getLogger(__name__)


class DirectServiceInitializer:
    """
    直接服务初始化器 - 替代ServiceLocator模式
    
    职责：按照core->business->handler的层次顺序创建服务
    """
    
    def __init__(self, config: AppConfig, config_service: ConfigServiceInterface):
        """初始化直接服务初始化器
        
        Args:
            config: 应用配置
            config_service: 配置服务接口
        """
        self.config = config
        self.config_service = config_service
        
        # 创建依赖注入容器和相关组件
        self.container = SimpleDependencyContainer()
        self.service_builder = ServiceBuilder(self.container)
        self.infrastructure_bridge = InfrastructureBridge(self.container)
        
        # 创建上层服务适配器
        self.upper_layer_adapter = UpperLayerServiceAdapter()
        
        # 配置基础设施服务绑定
        self._configure_infrastructure_services()
    
    def _configure_infrastructure_services(self) -> None:
        """配置基础设施服务到依赖注入容器的绑定"""
        logger.info("配置基础设施服务绑定...")
        
        # 通过基础设施桥接器注册配置服务
        self.infrastructure_bridge.register_config_services(self.config_service)
        
        # 注册上层服务适配器到基础设施桥接器
        self.infrastructure_bridge.register_service(UpperLayerServiceInterface, self.upper_layer_adapter)
        
        # 使用ServiceBuilder配置核心服务依赖
        self.service_builder.configure_core_services(self.config_service)
        
        logger.info("基础设施服务绑定配置完成")
        
    def initialize_all_services(self) -> Dict[str, Any]:
        """
        初始化所有服务并返回服务字典
        
        Returns:
            包含所有服务实例的字典
        """
        try:
            logger.info("开始直接服务初始化...")
            
            # 第1层：核心服务
            layer_1_services = self._create_layer_1_services()
            
            # 第2层：业务服务
            layer_2_services = self._create_layer_2_services(layer_1_services)
            
            # 第3层：处理器服务
            layer_3_services = self._create_layer_3_services(layer_1_services, layer_2_services)
            
            # 分析服务
            analysis_services = self._create_analysis_services()
            
            # 合并所有服务
            all_services = {
                **layer_1_services,
                **layer_2_services,
                **layer_3_services,
                **analysis_services
            }
            
            # 验证必需服务
            self._validate_required_services(all_services)
            
            logger.info(f"直接服务初始化完成，共创建 {len(all_services)} 个服务")
            return all_services
            
        except Exception as e:
            logger.error(f"直接服务初始化失败: {e}")
            raise ServiceCreationException("initialize_all_services", e)
    
    def _create_layer_1_services(self) -> Dict[str, Any]:
        """第1层：核心服务（无外部依赖）"""
        logger.info("创建第1层：核心服务...")
        
        services = {}
        
        try:
            # 配置数据访问器 - 保持现有实现
            from app.core.configuration.config_data_transfer import ConfigDataTransferObject
            from app.core.configuration.config_data_accessor import ConfigDataAccessor
            
            config_data = self.config_service.get_config()
            transfer_object = ConfigDataTransferObject.from_app_config(config_data)
            config_accessor = ConfigDataAccessor(transfer_object)
            
            services['config_accessor'] = config_accessor
            services['config_registry'] = config_accessor  # 向后兼容
            
            # 尝试从依赖注入容器获取服务（验证依赖注入系统）
            try:
                from ..abstractions.config_access_interface import ConfigAccessInterface
                config_access = self.container.resolve(ConfigAccessInterface)
                logger.info("✓ 依赖注入系统验证成功：ConfigAccessInterface")
                # 将依赖注入的配置访问服务也添加到服务字典
                services['config_access_di'] = config_access
            except Exception as e:
                logger.warning(f"依赖注入验证失败: {e}")
            
            # 图像处理器 - 尝试从依赖注入容器获取
            try:
                from ..interfaces import ImageProcessorInterface
                image_processor = self.container.resolve(ImageProcessorInterface)
                logger.info("✓ 从依赖注入容器获取ImageProcessor成功")
                services['image_processor'] = image_processor
            except Exception as e:
                # 回退到手工创建 - 使用新的业务层实现
                logger.info("从依赖注入容器获取ImageProcessor失败，回退到手工创建")
                from app.layers.business.processing.image_processor import ImageProcessor
                from app.layers.business.events.business_event_publisher import BusinessEventPublisher
                event_publisher = BusinessEventPublisher()
                image_processor = ImageProcessor(event_publisher)
                services['image_processor'] = image_processor
            
            logger.info("第1层核心服务创建完成")
            return services
            
        except Exception as e:
            logger.error(f"创建第1层服务失败: {e}")
            raise ServiceCreationException("layer_1_services", e)
    
    def _create_layer_2_services(self, layer_1_services: Dict[str, Any]) -> Dict[str, Any]:
        """第2层：业务服务（依赖第1层）"""
        logger.info("创建第2层：业务服务...")
        
        services = {}
        
        try:
            # 状态管理器 - 尝试从依赖注入容器获取
            try:
                from ..interfaces import StateManagerInterface
                state_manager = self.container.resolve(StateManagerInterface)
                logger.info("✓ 从依赖注入容器获取StateManager成功")
                services['state_manager'] = state_manager
            except Exception as e:
                # 回退到手工创建
                logger.info("从依赖注入容器获取StateManager失败，回退到手工创建")
                from app.core.managers.state_manager import StateManager
                image_processor = layer_1_services['image_processor']
                
                state_manager = StateManager(image_processor)
                services['state_manager'] = state_manager
            
            logger.info("第2层业务服务创建完成")
            return services
            
        except Exception as e:
            logger.error(f"创建第2层服务失败: {e}")
            raise ServiceCreationException("layer_2_services", e)
    
    def _create_layer_3_services(self, layer_1_services: Dict[str, Any], 
                                layer_2_services: Dict[str, Any]) -> Dict[str, Any]:
        """第3层：处理器服务（创建并注册到适配器）"""
        logger.info("创建第3层：处理器服务...")
        
        services = {}
        
        try:
            state_manager = layer_2_services['state_manager']
            image_processor = layer_1_services['image_processor']
            
            # 文件处理器
            from app.handlers.file_handler import FileHandler
            file_handler = FileHandler()
            services['file_handler'] = file_handler
            
            # 处理器
            from app.handlers.processing_handler import ProcessingHandler
            processing_handler = ProcessingHandler(state_manager)
            services['processing_handler'] = processing_handler
            
            # 批处理处理器
            batch_processing_handler = self._create_batch_processing_handler(
                state_manager, file_handler, image_processor)
            services['batch_processing_handler'] = batch_processing_handler
            
            # 预设处理器
            preset_handler = self._create_preset_handler(state_manager, batch_processing_handler)
            services['preset_handler'] = preset_handler
            
            # 应用控制器
            app_controller = self._create_app_controller(
                processing_handler, file_handler, batch_processing_handler, state_manager, preset_handler, layer_1_services)
            services['app_controller'] = app_controller
            
            # 注册到上层服务适配器
            self.upper_layer_adapter.register_service('file_handler', file_handler)
            self.upper_layer_adapter.register_service('processing_handler', processing_handler)
            self.upper_layer_adapter.register_service('batch_processing_handler', batch_processing_handler)
            self.upper_layer_adapter.register_service('preset_handler', preset_handler)
            self.upper_layer_adapter.register_service('app_controller', app_controller)
            
            logger.info("第3层处理器服务创建完成并注册到桥接适配器")
            return services
            
        except Exception as e:
            logger.error(f"创建第3层服务失败: {e}")
            raise ServiceCreationException("layer_3_services", e)
    
    def _create_batch_processing_handler(self, state_manager, file_handler, image_processor):
        """创建批处理处理器"""
        try:
            # 创建批处理作业管理器
            from app.features.batch_processing.managers.batch_job_manager import JobManager
            batch_job_manager = JobManager()
            
            # 创建批处理处理器
            from app.features.batch_processing.batch_coordinator import BatchProcessingHandler
            batch_processing_handler = BatchProcessingHandler(
                job_manager=batch_job_manager,
                state_manager=state_manager,
                file_handler=file_handler,
                image_processor=image_processor,
                config_service=self.config_service
            )
            
            return batch_processing_handler
            
        except Exception as e:
            logger.error(f"创建批处理处理器失败: {e}")
            raise ServiceCreationException("batch_processing_handler", e)
    
    def _create_preset_handler(self, state_manager, batch_processing_handler):
        """创建预设处理器"""
        try:
            from app.handlers.preset_handler import PresetHandler
            preset_handler = PresetHandler(state_manager, batch_processing_handler)
            return preset_handler
            
        except Exception as e:
            logger.error(f"创建预设处理器失败: {e}")
            raise ServiceCreationException("preset_handler", e)
    
    def _create_app_controller(self, processing_handler, file_handler, batch_processing_handler, state_manager, preset_handler, layer_1_services):
        """创建应用控制器"""
        try:
            from app.handlers.app_controller import AppController
            app_controller = AppController(
                state_manager=state_manager,
                file_handler=file_handler,
                preset_handler=preset_handler,
                processing_handler=processing_handler,
                batch_processor=batch_processing_handler
            )
            
            # 注册ConfigDataAccessor到桥接适配器
            config_accessor = layer_1_services.get('config_accessor')
            if config_accessor:
                app_controller.set_config_accessor(config_accessor)
            
            # 注册ConfigService到桥接适配器
            if self.config_service:
                app_controller.set_config_service(self.config_service)
            
            return app_controller
            
        except Exception as e:
            logger.error(f"创建应用控制器失败: {e}")
            raise ServiceCreationException("app_controller", e)
    
    def _create_analysis_services(self) -> Dict[str, Any]:
        """创建分析服务（独立初始化）"""
        logger.info("创建分析服务...")
        
        services = {}
        
        try:
            from PyQt6.QtCore import QThread
            from app.core import ImageAnalysisEngine
            
            # 创建分析线程和引擎
            analysis_thread = QThread()
            analysis_calculator = ImageAnalysisEngine()
            analysis_calculator.moveToThread(analysis_thread)
            analysis_thread.start()
            
            # 存储分析服务
            services['analysis_thread'] = analysis_thread
            services['analysis_calculator'] = analysis_calculator
            
            logger.info("分析服务创建完成")
            return services
            
        except Exception as e:
            logger.error(f"创建分析服务失败: {e}")
            raise ServiceCreationException("analysis_services", e)


    def _validate_required_services(self, services: Dict[str, Any]) -> None:
        """验证必需服务是否都已创建"""
        required_services = [
            'config_accessor', 'image_processor', 'state_manager',
            'file_handler', 'processing_handler', 'batch_processing_handler',
            'preset_handler', 'app_controller', 'analysis_calculator'
        ]
        
        missing_services = [name for name in required_services if name not in services or services[name] is None]
        if missing_services:
            error_msg = f"缺失必需服务: {missing_services}"
            logger.error(error_msg)
            raise ServiceValidationException(error_msg)
        
        logger.info("所有必需服务验证通过")


class ServiceCreationException(Exception):
    """服务创建异常"""
    
    def __init__(self, service_name: str, cause: Exception):
        self.service_name = service_name
        self.cause = cause
        super().__init__(f"创建服务 {service_name} 失败: {cause}")


class ServiceValidationException(Exception):
    """服务验证异常"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"服务验证失败: {message}")