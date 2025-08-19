"""
分析面板模块
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import pyqtSignal

# 移除核心层直接导入，通过桥接适配器访问
# from app.core.managers.state_manager import StateManager  # 已移除
from app.layers.business.processing.image_processor import ImageProcessor
from app.core import ImageAnalysisEngine
# from app.core.configuration.config_data_accessor import ConfigDataAccessor  # 已移除
from app.ui.widgets.image_info_widget import ImageInfoWidget
from .managers.rendering_engine_manager import RenderingEngineManager


# 设置日志记录器
logger = logging.getLogger(__name__)


class AnalysisPanel(QWidget):
    """
    分析面板类，负责显示和管理图像分析工具。
    支持在PyQtGraph和Matplotlib渲染引擎之间切换。
    """
    
    # 渲染引擎切换信号
    rendering_engine_changed = pyqtSignal(str)
    
    def __init__(
        self, 
        app_controller,  # 通过AppController获取核心服务
        image_processor: ImageProcessor, 
        analysis_calculator: ImageAnalysisEngine,
        parent=None
    ):
        """
        初始化分析面板
        
        Args:
            app_controller: 应用控制器（用于获取核心服务）
            image_processor: 图像处理器
            analysis_calculator: 分析计算器
            parent: 父级部件
        """
        super().__init__(parent)
        
        # 保存核心组件引用
        self.app_controller = app_controller
        self.image_processor = image_processor
        self.analysis_calculator = analysis_calculator
        
        # 通过桥接适配器获取核心服务
        core_adapter = self.app_controller.get_core_service_adapter()
        self.state_manager = core_adapter.get_state_manager() if core_adapter else None
        self.config_registry = core_adapter.get_config_accessor() if core_adapter else None
        
        # 创建渲染引擎管理器
        self.engine_manager = RenderingEngineManager(
            self.app_controller, self.image_processor, self.analysis_calculator,
            parent=self
        )
        
        # 共享的信息控件
        self.image_info_widget = ImageInfoWidget()
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI组件"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建渲染引擎选择控件
        self._create_engine_selector(layout)
        
        # 创建分析标签页
        self.analysis_tabs = QTabWidget()
        
        # 设置默认引擎
        self._switch_to_engine(self.engine_manager.get_current_engine())
        
        # 将标签页添加到布局
        layout.addWidget(self.analysis_tabs)
        
    def _create_engine_selector(self, layout):
        """创建渲染引擎选择器"""
        engine_layout = QHBoxLayout()
        
        # 标签
        engine_label = QLabel("渲染引擎:")
        engine_layout.addWidget(engine_label)
        
        # 下拉选择框
        self.engine_combo = QComboBox()
        
        # 添加渲染引擎选项
        self.engine_combo.addItem("PyQtGraph", "pyqtgraph")
        self.engine_combo.addItem("Matplotlib", "matplotlib")
        
        # 设置当前选择
        current_engine = self.engine_manager.get_current_engine()
        if current_engine == "pyqtgraph":
            self.engine_combo.setCurrentIndex(0)
        else:
            self.engine_combo.setCurrentIndex(1)

            
        self.engine_combo.currentTextChanged.connect(self._on_engine_changed)
        engine_layout.addWidget(self.engine_combo)
        
        # 应用按钮
        apply_button = QPushButton("应用")
        apply_button.clicked.connect(self._apply_engine_change)
        engine_layout.addWidget(apply_button)
        
        # 导出数据分析按钮
        export_button = QPushButton("导出数据分析")
        export_button.clicked.connect(self._on_export_analysis_clicked)
        engine_layout.addWidget(export_button)
        
        # 添加弹性空间
        engine_layout.addStretch()
        
        layout.addLayout(engine_layout)

    def _switch_to_engine(self, engine_name):
        """
        切换到指定的渲染引擎
        
        Args:
            engine_name: 目标渲染引擎名称
        """
        success = self.engine_manager.switch_engine(
            engine_name, self.analysis_tabs, self.image_info_widget
        )
        
        if not success:
            # 如果切换失败，更新UI选择器以反映实际状态
            self.engine_combo.setCurrentText(self.engine_manager.get_current_engine())
        
    def _on_engine_changed(self, engine_name):
        """引擎选择改变时的处理"""
        # 这里只是更新选择，不立即切换
        pass
        
    def _apply_engine_change(self):
        """
        应用引擎切换
        """
        # 获取选中项的数据（实际的引擎名称）
        new_engine = self.engine_combo.currentData()
        if new_engine is None:
            # 如果没有数据，回退到文本解析
            current_text = self.engine_combo.currentText()
            if "PyQt" in current_text:
                new_engine = "pyqtgraph"
            else:
                new_engine = "matplotlib"
        
        current_engine = self.engine_manager.get_current_engine()
        
        if new_engine == current_engine:
            logger.debug(f"引擎未改变，无需切换: {new_engine}")
            return
            
        logger.info(f"用户请求切换引擎: {current_engine} -> {new_engine}")
        
        # 执行引擎切换
        self._switch_to_engine(new_engine)
        
        # 发出引擎切换信号
        self.rendering_engine_changed.emit(self.engine_manager.get_current_engine())
        
        # 请求重新分析当前图像
        self.request_analysis_update()
        
        logger.info(f"引擎切换处理完成")
        
    def _on_export_analysis_clicked(self):
        """导出数据分析按钮点击处理"""
        try:
            from app.ui.dialogs.analysis_export_dialog import AnalysisExportDialog
            from app.ui.dialogs.analysis_export_progress_dialog import AnalysisExportProgressDialog
            from app.core.services.analysis_export_service import AnalysisExportService
            from PyQt6.QtWidgets import QMessageBox
            
            # 获取批处理协调器
            batch_coordinator = None
            if hasattr(self.app_controller, 'get_batch_processor'):
                batch_coordinator = self.app_controller.get_batch_processor()
            
            # 检查是否有可用的作业
            if not batch_coordinator:
                QMessageBox.warning(self, "警告", "批处理功能未初始化，无法导出数据分析。")
                return
            
            try:
                jobs = batch_coordinator.get_all_jobs()
                if not jobs:
                    QMessageBox.information(self, "提示", "当前没有可用的作业，请先创建作业后再进行数据分析导出。")
                    return
            except Exception as e:
                logger.error(f"获取作业列表失败: {e}")
                QMessageBox.warning(self, "警告", "无法获取作业列表，请检查批处理功能是否正常。")
                return
            
            # 获取配置服务
            config_accessor = None
            if hasattr(self.app_controller, 'get_config_accessor'):
                config_accessor = self.app_controller.get_config_accessor()
            
            # 显示导出配置对话框
            export_dialog = AnalysisExportDialog(self, batch_coordinator, config_accessor, self.app_controller)
            if export_dialog.exec() == export_dialog.DialogCode.Accepted:
                config = export_dialog.get_config()
                
                # 创建导出服务
                export_service = AnalysisExportService(
                    self.state_manager, 
                    self.image_processor, 
                    self.analysis_calculator,
                    batch_coordinator
                )
                
                # 显示进度对话框并开始导出
                progress_dialog = AnalysisExportProgressDialog(export_service, config, self)
                progress_dialog.exec()
                
        except Exception as e:
            logger.error(f"导出数据分析失败: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
        
    def request_analysis_update(self, tab_index: Optional[int] = None):
        """
        请求更新分析数据
        
        Args:
            tab_index: 要更新的标签页索引，如果为None，则更新当前可见的标签页
        """
        self.engine_manager.request_analysis_update(tab_index)
    
    def clear_all_analyses(self):
        """清除所有分析数据"""
        self.engine_manager.clear_all_analyses()
        
    def get_smart_update_status(self) -> dict:
        """
        获取智能更新状态信息
        
        Returns:
            dict: 包含智能更新状态的字典
        """
        analysis_manager = self.engine_manager.get_analysis_manager()
        if analysis_manager and hasattr(analysis_manager, 'get_update_status'):
            try:
                status = analysis_manager.get_update_status()
                status['current_engine'] = self.engine_manager.get_current_engine()
                return status
            except Exception as e:
                logger.error(f"获取智能更新状态时发生错误: {e}")
                return {'error': str(e), 'current_engine': self.engine_manager.get_current_engine()}
        else:
            return {'error': '分析管理器不支持智能更新', 'current_engine': self.engine_manager.get_current_engine()}
        
    def get_error_statistics(self) -> dict:
        """
        获取错误统计信息
        
        Returns:
            dict: 包含错误统计信息的字典
        """
        analysis_manager = self.engine_manager.get_analysis_manager()
        if analysis_manager and hasattr(analysis_manager, 'get_error_statistics'):
            return analysis_manager.get_error_statistics()
        else:
            return {'error': '分析管理器不支持错误统计'}
            
    def clear_error_history(self):
        """清除错误历史记录"""
        analysis_manager = self.engine_manager.get_analysis_manager()
        if analysis_manager and hasattr(analysis_manager, 'clear_error_history'):
            analysis_manager.clear_error_history()
            logger.info("已清除错误历史记录")
        else:
            logger.warning("分析管理器不支持清除错误历史记录")
    
    def update_display(self):
        """更新显示内容"""
        # 触发分析面板的刷新逻辑
        try:
            # 通知渲染引擎管理器图像数据已变化，触发智能更新机制
            self.engine_manager.handle_image_data_changed()
            logger.debug("分析面板显示已更新")
        except Exception as e:
            logger.error(f"更新分析面板显示失败: {e}")