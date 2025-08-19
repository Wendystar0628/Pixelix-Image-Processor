"""
渲染引擎管理器模块

负责管理渲染引擎的切换、资源清理和错误处理
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import QWidget, QTabWidget
from PyQt6.QtCore import QObject

# 移除核心层直接导入，通过桥接适配器访问
# from app.core.managers.state_manager import StateManager  # 已移除
from app.layers.business.processing.image_processor import ImageProcessor
from app.core import ImageAnalysisEngine
# from app.core.configuration.config_data_accessor import ConfigDataAccessor  # 已移除
from app.ui.managers.analysis_components_manager import AnalysisComponentsManager
from .analysis_widget_factory import AnalysisWidgetFactory

# 设置日志记录器
logger = logging.getLogger(__name__)


class RenderingEngineManager(QObject):
    """
    渲染引擎管理器
    
    负责管理渲染引擎的切换、资源生命周期管理、错误处理和回退机制。
    将复杂的引擎管理逻辑从UI层分离出来，提高代码的可维护性。
    """
    
    def __init__(self, app_controller, image_processor: ImageProcessor, 
                 analysis_calculator: ImageAnalysisEngine, 
                 parent: QObject = None):
        """
        初始化渲染引擎管理器
        
        Args:
            app_controller: 应用控制器（用于获取核心服务）
            image_processor: 图像处理器
            analysis_calculator: 分析计算器
            parent: 父对象
        """
        super().__init__(parent)
        
        self.app_controller = app_controller
        self.image_processor = image_processor
        self.analysis_calculator = analysis_calculator
        
        # 通过桥接适配器获取核心服务
        core_adapter = self.app_controller.get_core_service_adapter()
        self.state_manager = core_adapter.get_state_manager() if core_adapter else None
        self.config_registry = core_adapter.get_config_accessor() if core_adapter else None
        
        # 从配置提供者获取默认渲染引擎
        default_engine = self.config_registry.get_rendering_mode()
        
        # 当前状态
        self.current_engine = default_engine  # 使用配置中的渲染模式
        self.last_working_engine = default_engine  # 用于错误回退
        
        # 当前的分析组件管理器
        self.analysis_manager: Optional[AnalysisComponentsManager] = None
        
        # 当前的UI组件引用
        self.current_widgets = {}
        
        logger.debug("渲染引擎管理器初始化完成")
    
    def _disconnect_manager_signals(self, tabs_widget: QTabWidget):
        """
        安全地断开分析组件管理器的信号连接
        
        Args:
            tabs_widget: 标签页控件
        """
        if not self.analysis_manager:
            return
            
        try:
            # 断开标签页切换信号
            if hasattr(tabs_widget, 'currentChanged'):
                tabs_widget.currentChanged.disconnect()
                logger.debug("已断开标签页切换信号")
        except (TypeError, RuntimeError) as e:
            logger.warning(f"断开标签页信号时出现警告: {e}")
            
        try:
            # 断开分析计算器完成信号 - 新架构中信号连接在AnalysisDataProcessor中
            if hasattr(self.analysis_calculator, 'analysis_finished') and self.analysis_manager:
                # 获取数据处理器并断开其信号连接
                if hasattr(self.analysis_manager, 'data_processor'):
                    self.analysis_calculator.analysis_finished.disconnect(
                        self.analysis_manager.data_processor.on_analysis_finished
                    )
                    logger.debug("已断开分析完成信号（通过数据处理器）")
                else:
                    logger.debug("跳过分析完成信号断开：数据处理器不存在")
        except (TypeError, RuntimeError) as e:
            logger.warning(f"断开分析完成信号时出现警告: {e}")
    
    def _cleanup_current_engine(self, tabs_widget: QTabWidget, info_widget: QWidget):
        """
        清理当前引擎的所有资源
        
        Args:
            tabs_widget: 标签页控件
            info_widget: 信息控件（共享的，不会被销毁）
        """
        logger.debug(f"开始清理当前引擎资源: {self.current_engine}")
        
        try:
            # 断开信号连接
            self._disconnect_manager_signals(tabs_widget)
            
            # 清空标签页（除了信息页，它会被重新添加）
            while tabs_widget.count() > 0:
                widget = tabs_widget.widget(0)
                tabs_widget.removeTab(0)
                
                # 如果不是共享的信息控件，则销毁它
                if widget and widget != info_widget:
                    logger.debug(f"销毁UI组件: {type(widget).__name__}")
                    widget.deleteLater()
            
            # 销毁分析管理器
            if self.analysis_manager:
                logger.debug("销毁分析组件管理器")
                self.analysis_manager.deleteLater()
                self.analysis_manager = None
            
            # 清空组件引用
            self.current_widgets.clear()
                
            logger.debug("资源清理完成")
            
        except Exception as e:
            logger.error(f"清理资源时发生错误: {e}")
            # 即使清理失败，也要确保管理器被重置
            self.analysis_manager = None
            self.current_widgets.clear()
    
    def _handle_switch_error(self, error: Exception, target_engine: str, 
                           tabs_widget: QTabWidget, info_widget: QWidget):
        """
        处理切换过程中的错误
        
        Args:
            error: 发生的异常
            target_engine: 目标渲染引擎名称
            tabs_widget: 标签页控件
            info_widget: 信息控件
        """
        logger.error(f"切换到 {target_engine} 引擎时发生错误: {error}")
        
        # 尝试回退到上一个工作的引擎
        if self.last_working_engine != target_engine:
            logger.info(f"尝试回退到上一个工作的引擎: {self.last_working_engine}")
            try:
                # 尝试切换回上一个工作的引擎
                success = self.switch_engine(self.last_working_engine, tabs_widget, info_widget)
                
                if success:
                    logger.info(f"成功回退到 {self.last_working_engine} 引擎")
                    logger.warning(f"渲染引擎切换失败，已回退到 {self.last_working_engine}")
                    return True
                else:
                    raise RuntimeError("回退切换失败")
                
            except Exception as rollback_error:
                logger.error(f"回退到 {self.last_working_engine} 引擎也失败: {rollback_error}")
                logger.critical("渲染引擎切换和回退都失败，界面可能处于不稳定状态")
        else:
            logger.error("无法回退：目标引擎与上一个工作引擎相同")
            logger.critical("渲染引擎切换失败且无法回退，界面可能处于不稳定状态")
        
        return False
    
    def switch_engine(self, engine_name: str, tabs_widget: QTabWidget, 
                     info_widget: QWidget) -> bool:
        """
        切换到指定的渲染引擎
        
        Args:
            engine_name: 目标渲染引擎名称
            tabs_widget: 标签页控件
            info_widget: 信息控件（共享的）
            
        Returns:
            bool: 切换成功返回True，失败返回False
        """
        logger.info(f"开始切换到渲染引擎: {engine_name}")
        
        # 检查引擎是否支持
        if not AnalysisWidgetFactory.is_engine_supported(engine_name):
            logger.error(f"不支持的渲染引擎: {engine_name}")
            return False
        
        try:
            # 首先清理当前引擎的资源
            self._cleanup_current_engine(tabs_widget, info_widget)
            
            # 创建新引擎的UI组件
            widgets = AnalysisWidgetFactory.create_widgets(engine_name)
            if widgets is None:
                raise RuntimeError(f"创建 {engine_name} 引擎的UI组件失败")
            
            # 保存组件引用
            self.current_widgets = widgets
            
            # 添加信息标签页（始终存在）
            tabs_widget.addTab(info_widget, "信息")
            
            # 添加分析标签页
            tabs_widget.addTab(widgets['combined'], "直方图与波形")
            tabs_widget.addTab(widgets['rgb_parade'], "RGB Parade")
            tabs_widget.addTab(widgets['hue_saturation'], "色相/饱和度")
            tabs_widget.addTab(widgets['lab_analysis'], "Lab色度")
            
            # 创建新的增强分析组件管理器（直接集成智能更新）
            self.analysis_manager = AnalysisComponentsManager(
                state_manager=self.state_manager,
                image_processor=self.image_processor,
                analysis_calculator=self.analysis_calculator,
                analysis_tabs=tabs_widget,
                image_info_widget=info_widget,
                combined_analysis_widget=widgets['combined'],
                rgb_parade_widget=widgets['rgb_parade'],
                hue_saturation_widget=widgets['hue_saturation'],
                lab_analysis_widget=widgets['lab_analysis'],
                config_registry=self.config_registry,
                parent=self
            )
            
            if self.analysis_manager is None:
                raise RuntimeError("创建分析组件管理器失败")
            
            # 更新当前引擎状态
            self.current_engine = engine_name
            
            # 成功切换后，更新上一个工作引擎
            self.last_working_engine = engine_name
            
            logger.info(f"成功切换到渲染引擎: {engine_name}")
            return True
            
        except Exception as e:
            # 处理切换错误
            success = self._handle_switch_error(e, engine_name, tabs_widget, info_widget)
            return success
    
    def get_current_engine(self) -> str:
        """
        获取当前渲染引擎名称
        
        Returns:
            str: 当前引擎名称
        """
        return self.current_engine
    
    def get_analysis_manager(self) -> Optional[AnalysisComponentsManager]:
        """
        获取当前的分析组件管理器
        
        Returns:
            Optional[AnalysisComponentsManager]: 分析组件管理器，如果不存在返回None
        """
        return self.analysis_manager
    
    def request_analysis_update(self, tab_index: Optional[int] = None):
        """
        请求更新分析数据
        
        Args:
            tab_index: 要更新的标签页索引，如果为None，则更新当前可见的标签页
        """
        if self.analysis_manager:
            try:
                self.analysis_manager.request_analysis_update(tab_index)
                logger.debug(f"已请求分析更新，标签页索引: {tab_index}")
            except Exception as e:
                logger.error(f"请求分析更新时发生错误: {e}")
        else:
            logger.warning("分析管理器不存在，无法请求分析更新")
    
    def clear_all_analyses(self):
        """
        清除所有分析数据
        """
        if self.analysis_manager:
            try:
                self.analysis_manager.clear_all_analyses()
                logger.debug("已清除所有分析数据")
            except Exception as e:
                logger.error(f"清除分析数据时发生错误: {e}")
        else:
            logger.warning("分析管理器不存在，无法清除分析数据")
    
    def get_supported_engines(self) -> list:
        """
        获取支持的渲染引擎列表
        
        Returns:
            list: 支持的引擎名称列表
        """
        return AnalysisWidgetFactory.get_supported_engines()
    
    def handle_image_data_changed(self):
        """
        处理图像数据变化事件
        
        当图像处理完成或图像数据发生变化时调用此方法，
        触发智能更新机制。
        """
        if self.analysis_manager:
            try:
                self.analysis_manager.handle_image_data_changed()
                logger.debug("已通知分析管理器处理图像数据变化")
            except Exception as e:
                logger.error(f"通知分析管理器处理图像数据变化时发生错误: {e}")
        else:
            logger.warning("分析管理器不存在，无法处理图像数据变化")
    
