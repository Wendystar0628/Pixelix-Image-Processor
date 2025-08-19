"""
主窗口模块 - 依赖注入版本

重构后的MainWindow使用构造函数注入所有依赖，移除对AppContext的依赖。
将布局组装和信号连接职责委托给专门的管理器。
"""

import os
from typing import cast, Optional

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QDragEnterEvent, QDropEvent, QKeyEvent, QIcon
from PyQt6.QtWidgets import QMainWindow, QMessageBox

# --- 核心接口 ---
from app.core.interfaces import (
    ImageProcessorInterface,
    StateManagerInterface,
    AppControllerInterface
)

# --- 核心组件 ---
from app.core import ImageAnalysisEngine
# 移除核心层直接导入，通过桥接适配器访问
# from app.core.tools.tool_manager import ToolManager  # 已移除
# from app.core.configuration.config_data_accessor import ConfigDataAccessor  # 已移除
from app.features.batch_processing.batch_coordinator import BatchProcessingHandler

# --- UI组件 ---
from app.ui.managers.menu_manager import MenuManager
from app.ui.managers.toolbar_manager import ToolbarManager
from app.ui.managers.main_window_layout_manager import MainWindowLayoutManager
from app.ui.managers.main_window_connection_manager import MainWindowConnectionManager
from app.ui.managers.main_window_event_handler import MainWindowEventHandler
from app.ui.panels.batch_processing_panel import BatchProcessingPanel


class MainWindow(QMainWindow):
    """
    主应用程序窗口容器 - 依赖注入版本
    
    通过构造函数注入所有依赖，专注于窗口容器职责和管理器协调
    """

    def __init__(self, 
                 image_processor: ImageProcessorInterface,
                 state_manager: StateManagerInterface,
                 analysis_calculator: ImageAnalysisEngine,
                 config_registry,  # 通过桥接适配器获取
                 app_controller: Optional[AppControllerInterface] = None,
                 batch_processing_handler: Optional[BatchProcessingHandler] = None):
        super().__init__()
        self.setWindowTitle("Pixelix - 数字图像处理工坊")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置窗口图标
        self._set_window_icon()

        # 核心服务（依赖注入）
        self.image_processor = image_processor
        self.state_manager = state_manager
        self.analysis_calculator = analysis_calculator
        self.config_registry = config_registry
        self.tool_manager = self.state_manager.tool_manager  # 通过桥接适配器获取
        
        # 可选UI服务
        self.app_controller = app_controller
        self.batch_processing_handler = batch_processing_handler
        
        # 批处理面板（延迟创建）
        self.batch_processing_panel = None
        
        # 可选管理器（延迟创建，依赖可选服务）
        self.menu_manager = None
        self.toolbar_manager = None
        
        # 创建UI面板
        self._create_ui_panels()
        
        # 创建基础管理器（不依赖可选服务）
        self._create_basic_managers()
        
        # 基础UI初始化
        self._init_basic_ui()
        
        # 连接基础信号
        self.state_manager.state_changed.connect(self._render_and_update_display)
        
        # 初始化工具和拖放
        self._setup_tools()
        self.setAcceptDrops(True)



    def _create_ui_panels(self):
        """创建UI面板"""
        from app.ui.panels.image_view_panel import ImageViewPanel
        from app.ui.panels.analysis_panel import AnalysisPanel
        
        self.image_view_panel = ImageViewPanel(self.state_manager, self.image_processor)
        self.analysis_panel = AnalysisPanel(self.app_controller, self.image_processor, self.analysis_calculator, parent=self)
        
    def _create_basic_managers(self):
        """创建基础管理器（不依赖可选服务）"""
        self.layout_manager = MainWindowLayoutManager(self)
        self.connection_manager = MainWindowConnectionManager(self)
        self.event_handler = MainWindowEventHandler(self)
        
    def _create_optional_managers(self):
        """创建可选管理器（依赖可选服务，如file_handler）"""
        self.menu_manager = MenuManager(self)
        self.toolbar_manager = ToolbarManager(self)
        
    def _init_basic_ui(self):
        """初始化基础UI（布局结构）"""
        # 创建中央部件和布局
        central_widget = self.layout_manager.create_central_widget()
        self.setCentralWidget(central_widget)
        
    def _complete_ui_assembly(self):
        """完成完整UI组装（菜单、工具栏等）"""
        if self.menu_manager:
            self.menu_manager.create_menus(self.menuBar())
        
        if self.toolbar_manager:
            # 创建工具栏并添加到主窗口
            toolbar = self.toolbar_manager.create_toolbar()
            self.addToolBar(toolbar)
        
    def complete_ui_initialization(self):
        """完成UI初始化，在可选依赖设置后调用"""
        # 创建依赖可选服务的管理器
        self._create_optional_managers()
        
        # 完成完整UI组装
        self._complete_ui_assembly()
        
        # 连接所有信号
        if self.app_controller:
            self.connection_manager.connect_all_signals()
        
        # 初始化批处理面板
        self._initialize_batch_processing_panel()
        
    def _initialize_batch_processing_panel(self):
        """初始化批处理面板"""
        if self.batch_processing_handler:
            self.batch_processing_panel = BatchProcessingPanel(self.batch_processing_handler, self.app_controller, self)
            self.layout_manager.add_batch_processing_panel(self.batch_processing_panel)
            
            # 批处理面板创建后，立即连接相关信号
            if hasattr(self, 'connection_manager'):
                self.connection_manager._connect_batch_processing_signals()
        else:
            self.batch_processing_panel = None
    
    def _setup_tools(self):
        """设置工具"""
        # 工具初始化逻辑
        pass
        
    def _render_and_update_display(self):
        """渲染并更新显示"""
        if hasattr(self, 'image_view_panel'):
            self.image_view_panel.update_display()
        if hasattr(self, 'analysis_panel'):
            self.analysis_panel.update_display()
    
    def closeEvent(self, event: QCloseEvent):
        """处理窗口关闭事件"""
        self.event_handler.handle_close_event(event)
        
    def keyPressEvent(self, event: QKeyEvent):
        """处理按键事件"""
        if self.event_handler.handle_key_press_event(event):
            return
        super().keyPressEvent(event)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖拽进入事件"""
        self.event_handler.handle_drag_enter_event(event)
        
    def dropEvent(self, event: QDropEvent):
        """处理拖拽放下事件"""  
        self.event_handler.handle_drop_event(event)

    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        # 确保窗口显示后再进行初始渲染
        if hasattr(self, 'image_view_panel'):
            self.image_view_panel.initial_render()
    
    # === 信号处理方法 ===
    
    def _show_error_message(self, message: str):
        """显示错误消息"""
        QMessageBox.critical(self, "错误", message)
    
    def _on_loading_started(self):
        """图像加载开始处理"""
        self.statusBar().showMessage("正在加载图像...")
    
    def _on_loading_complete(self):
        """图像加载完成处理"""
        self.statusBar().showMessage("图像加载完成", 2000)
    
    def _set_window_icon(self):
        """设置窗口图标"""
        try:
            # 获取图标文件路径
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'icons', 'LOGO.ico')
            
            # 检查图标文件是否存在
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                self.setWindowIcon(icon)
                print(f"窗口图标设置成功: {icon_path}")
            else:
                print(f"警告: 图标文件不存在: {icon_path}")
        except Exception as e:
            print(f"设置窗口图标时出错: {e}")
    
