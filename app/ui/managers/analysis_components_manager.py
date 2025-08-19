"""
分析组件管理器模块 - 重构为协调器

采用门面模式，协调各个专门的子管理器：
- AnalysisUpdateManager: 智能更新逻辑
- AnalysisWidgetManager: UI组件管理  
- AnalysisDataProcessor: 数据处理协调

职责：作为统一的入口点，保持向后兼容的接口，协调各子管理器工作。
"""
import logging
from typing import Set, Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSlot
# 移除核心层直接导入，通过桥接适配器访问
# from app.core.configuration.config_data_accessor import ConfigDataAccessor  # 已移除

# 通用服务已移除，使用简化的错误处理
from app.ui.managers.analysis_update_manager import AnalysisUpdateManager
from app.ui.managers.analysis_widget_manager import AnalysisWidgetManager
from app.ui.managers.analysis_data_processor import AnalysisDataProcessor


logger = logging.getLogger(__name__)

class AnalysisComponentsManager(QObject):
    """
    分析组件协调器 - 重构版本
    
    采用门面模式，协调各个专门的子管理器，保持向后兼容的接口。
    职责：统一入口点、信号协调、生命周期管理。
    """
    def __init__(self, state_manager, image_processor, analysis_calculator, 
                 analysis_tabs, image_info_widget, combined_analysis_widget, 
                 rgb_parade_widget, hue_saturation_widget, 
                 config_registry,  # 通过桥接适配器获取
                 lab_analysis_widget=None,
                 parent=None):
        super().__init__(parent)
        
        # 保持对核心组件的引用（用于向后兼容和错误处理）
        self.state_manager = state_manager
        self.analysis_tabs = analysis_tabs
        self.config_registry = config_registry
        
        # 通用服务已移除，使用默认配置
        self.config = None  # 将在需要时通过其他方式获取配置
        
        # 创建专门的子管理器
        self.update_manager = AnalysisUpdateManager(
            analysis_tabs=analysis_tabs,
            config_registry=config_registry,
            parent=self
        )
        
        self.widget_manager = AnalysisWidgetManager(
            analysis_tabs=analysis_tabs,
            image_info_widget=image_info_widget,
            combined_analysis_widget=combined_analysis_widget,
            rgb_parade_widget=rgb_parade_widget,
            hue_saturation_widget=hue_saturation_widget,
            lab_analysis_widget=lab_analysis_widget,
            parent=self
        )
        
        self.data_processor = AnalysisDataProcessor(
            state_manager=state_manager,
            image_processor=image_processor,
            analysis_calculator=analysis_calculator,
            parent=self
        )
        
        # 错误恢复策略已移除
        
        # 连接信号
        self._connect_signals()
        
        logger.debug("分析组件协调器初始化完成（职责分离版本）")

    def _register_error_recovery_strategies(self):
        """错误恢复策略已移除"""
        pass

    def _connect_signals(self):
        """连接所有相关的信号和槽（协调器模式）"""
        # 连接标签页切换信号到更新管理器
        self.analysis_tabs.currentChanged.connect(self.update_manager.handle_tab_changed)
        
        # 连接子管理器之间的信号
        # 更新管理器 -> 数据处理器
        self.update_manager.immediate_update_requested.connect(
            self.data_processor.process_immediate_update
        )
        self.update_manager.current_tab_update_requested.connect(
            self._handle_current_tab_update
        )
        
        # 数据处理器 -> widget管理器
        self.data_processor.analysis_completed.connect(
            self.widget_manager.update_widgets_with_results
        )
        self.data_processor.image_info_updated.connect(
            self.widget_manager.update_image_info
        )
        
        logger.debug("所有子管理器信号已连接")
    
    def _handle_current_tab_update(self):
        """处理当前标签页更新请求"""
        current_tab = self.analysis_tabs.currentIndex()
        self.data_processor.process_immediate_update(current_tab)
    
    # ==================== 向后兼容的公共接口 ====================
    
    @pyqtSlot(int)
    def on_analysis_tab_changed(self, index):
        """
        处理分析标签页切换事件（委托给更新管理器）
        
        Args:
            index: 新选中的标签页索引
        """
        # 委托给更新管理器处理
        self.update_manager.handle_tab_changed(index)

    def request_analysis_update(self, tab_index=None):
        """
        请求更新分析数据（委托给更新管理器）
        
        Args:
            tab_index: 要更新的标签页索引。如果为None，则使用当前选中的标签页。
        """
        # 委托给更新管理器处理
        self.update_manager.request_analysis_update(tab_index)

    @pyqtSlot(dict)
    def on_analysis_finished(self, results):
        """
        处理来自分析计算器的结果（委托给数据处理器）
        这个方法保留用于向后兼容，但实际处理已在信号连接中完成。
        """
        # 此方法保留用于向后兼容，实际处理在信号连接中完成
        pass

    def clear_all_analyses(self):
        """清空所有分析组件的内容（委托给widget管理器）"""
        self.widget_manager.clear_all_analyses()
    
    # ==================== 委托接口方法 ====================
    
    # 智能更新相关方法委托给 update_manager
    def handle_image_data_changed(self):
        """处理图像数据变化事件（委托给更新管理器）"""
        self.update_manager.handle_image_data_changed()
    
    def get_stale_tabs(self) -> Set[int]:
        """获取stale标签页集合（委托给更新管理器）"""
        return self.update_manager.get_stale_tabs()
    
    def clear_stale_tabs(self):
        """清除所有stale标签页标记（委托给更新管理器）"""
        self.update_manager.clear_stale_tabs()
    
    def is_tab_stale(self, tab_index: int) -> bool:
        """检查标签页是否为stale状态（委托给更新管理器）"""
        return self.update_manager.is_tab_stale(tab_index)
    
    def get_update_status(self) -> Dict[str, Any]:
        """获取更新状态信息（委托给更新管理器）"""
        return self.update_manager.get_update_status()
    
    def configure_update_behavior(self):
        """配置更新行为（委托给更新管理器）"""
        self.update_manager.configure_update_behavior()
    
    # 数据处理相关方法委托给 data_processor  
    def get_processing_status(self) -> Dict[str, Any]:
        """获取处理状态信息（委托给数据处理器）"""
        return self.data_processor.get_processing_status()
    
    def reset_calculating_state(self):
        """重置计算状态（委托给数据处理器）"""
        self.data_processor.reset_calculating_state()
    
    # Widget管理相关方法委托给 widget_manager
    def get_widget_status(self) -> Dict[str, Any]:
        """获取widget状态信息（委托给widget管理器）"""
        return self.widget_manager.get_widget_status()
    
    def refresh_all_widgets(self):
        """刷新所有widget显示（委托给widget管理器）"""
        self.widget_manager.refresh_all_widgets()
    
    # ==================== 向后兼容属性 ====================
    
    @property
    def is_calculating(self) -> bool:
        """获取计算状态（委托给数据处理器）"""
        return self.data_processor.is_calculating
    
    @is_calculating.setter  
    def is_calculating(self, value: bool):
        """设置计算状态（委托给数据处理器）"""
        self.data_processor.is_calculating = value
    
    # ==================== 错误恢复 ====================
    
    def _unified_error_recovery(self, error_record):
        """错误恢复方法已移除"""
        pass