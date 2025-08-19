"""
MainWindow连接管理器

负责管理主窗口相关的所有信号连接，包括菜单、工具栏、状态管理等信号的连接。
"""

from app.ui.managers.ui_state_manager import UIStateManager


class MainWindowConnectionManager:
    """主窗口连接管理器"""
    
    def __init__(self, main_window):
        """
        初始化连接管理器
        
        Args:
            main_window: MainWindow实例
        """
        self.main_window = main_window
        self.ui_state_manager = None
        
    def connect_all_signals(self):
        """连接所有可用的信号"""
        if not self.main_window.app_controller:
            print("警告：app_controller不可用，跳过信号连接")
            return
            
        # 连接基础信号
        self._connect_basic_signals()
        
        # 连接菜单信号
        self._connect_menu_signals()
        
        # 连接工具栏信号
        self._connect_toolbar_signals()
        
        # 连接批处理信号
        self._connect_batch_processing_signals()
        
        # 设置UI状态管理器
        self._setup_ui_state_manager()
        
    def _connect_basic_signals(self):
        """连接基础信号"""
        # 连接图像视图面板信号
        if hasattr(self.main_window, 'image_view_panel'):
            self.main_window.image_view_panel.request_load_image.connect(
                self.main_window.app_controller.open_recent_file
            )
            
        # 连接图像加载信号
        if hasattr(self.main_window.app_controller, 'loading_started'):
            self.main_window.app_controller.loading_started.connect(
                self.main_window._on_loading_started
            )
        if hasattr(self.main_window.app_controller, 'loading_complete'):
            self.main_window.app_controller.loading_complete.connect(
                self.main_window._on_loading_complete
            )
            
        # 连接状态栏消息信号
        if (self.main_window.app_controller and 
            hasattr(self.main_window.app_controller, 'image_loader') and
            self.main_window.app_controller.image_loader):
            self.main_window.app_controller.image_loader.status_message.connect(
                self.main_window.statusBar().showMessage
            )
            self.main_window.app_controller.image_loader.show_error_message.connect(
                self.main_window._show_error_message
            )
            
    def _get_common_signal_mappings(self):
        """获取通用信号映射"""
        return {
            'save_file_triggered': lambda: self.main_window.app_controller.save_image(self.main_window),
            'clear_effects_triggered': self.main_window.app_controller.clear_all_effects,
            'import_folder_triggered': lambda: self.main_window.app_controller.show_import_folder_dialog(self.main_window),
        }
        
    def _connect_menu_signals(self):
        """连接菜单信号到相应的处理函数"""
        if not hasattr(self.main_window, 'menu_manager'):
            return
            
        # 通用信号连接
        common_mappings = self._get_common_signal_mappings()
        for signal_name, handler in common_mappings.items():
            if hasattr(self.main_window.menu_manager, signal_name):
                getattr(self.main_window.menu_manager, signal_name).connect(handler)
                
        # 菜单特有的信号
        menu_specific_mappings = self._get_menu_specific_mappings()
        for signal_name, handler in menu_specific_mappings.items():
            if hasattr(self.main_window.menu_manager, signal_name):
                getattr(self.main_window.menu_manager, signal_name).connect(handler)
                
    def _get_menu_specific_mappings(self):
        """获取菜单特有的信号映射"""
        mappings = {
            'open_recent_file_triggered': self.main_window.app_controller.open_recent_file,
            'exit_app_triggered': self.main_window.close,
            'undo_triggered': self.main_window.app_controller.undo,
            'redo_triggered': self.main_window.app_controller.redo,
            'show_dialog_triggered': self.main_window.app_controller.show_dialog,
            'apply_simple_operation_triggered': self.main_window.app_controller.apply_simple_operation,
            'set_proxy_quality_triggered': self.set_proxy_quality,
            'apply_preset_triggered': self.main_window.app_controller.show_apply_preset_dialog,
            'save_as_preset_triggered': lambda: self.main_window.app_controller.save_current_as_preset(self.main_window),
            'delete_preset_triggered': lambda: self.main_window.app_controller.delete_preset(self.main_window),
            'help_triggered': self.main_window.app_controller.show_help_dialog,
        }
        
        # 注意：添加图像菜单项已被删除，不再需要连接open_file_triggered信号
            
        return mappings
        
    def _connect_toolbar_signals(self):
        """连接工具栏管理器的所有信号到相应的处理函数"""
        if not hasattr(self.main_window, 'toolbar_manager'):
            return
            
        # 通用信号连接
        common_mappings = self._get_common_signal_mappings()
        for signal_name, handler in common_mappings.items():
            if hasattr(self.main_window.toolbar_manager, signal_name):
                getattr(self.main_window.toolbar_manager, signal_name).connect(handler)
                
        # 工具栏特有的信号
        # 注意：添加图像按钮已被删除，不再需要连接open_file_triggered信号
    
    def _connect_batch_processing_signals(self):
        """连接批处理相关信号"""
        # 检查批处理面板是否存在
        if not hasattr(self.main_window, 'batch_processing_panel') or not self.main_window.batch_processing_panel:
            return
            
        batch_panel = self.main_window.batch_processing_panel
        
        # 连接批处理面板的错误和信息信号到主窗口状态栏
        if hasattr(batch_panel, 'handler') and batch_panel.handler:
            batch_panel.handler.show_error_message.connect(
                lambda msg: self.main_window.statusBar().showMessage(f"批处理错误: {msg}", 5000)
            )
            batch_panel.handler.show_info_message.connect(
                lambda msg: self.main_window.statusBar().showMessage(msg, 3000)
            )
            
        # 连接批处理作业处理信号
        if hasattr(batch_panel, 'handler') and batch_panel.handler:
            if hasattr(batch_panel.handler, 'job_processing_started'):
                batch_panel.handler.job_processing_started.connect(
                    lambda job_id: self.main_window.statusBar().showMessage(f"开始处理作业: {job_id}")
                )
            if hasattr(batch_panel.handler, 'job_processing_finished'):
                batch_panel.handler.job_processing_finished.connect(
                    self._on_batch_job_finished
                )
        
        # 连接图像池双击信号到主视图加载
        if hasattr(batch_panel, 'image_pool_panel') and batch_panel.image_pool_panel:
            if hasattr(batch_panel.image_pool_panel, 'image_double_clicked'):
                batch_panel.image_pool_panel.image_double_clicked.connect(
                    self.main_window.app_controller.load_image_from_path
                )
    
    def _on_batch_job_finished(self, job_id: str, success: bool, message: str):
        """处理批处理作业完成信号"""
        if success:
            self.main_window.statusBar().showMessage(f"作业 {job_id} 完成: {message}", 3000)
        else:
            self.main_window.statusBar().showMessage(f"作业 {job_id} 失败: {message}", 5000)
                    
    def _setup_ui_state_manager(self):
        """设置UI状态管理器"""
        # 创建UI状态管理器
        self.ui_state_manager = UIStateManager(self.main_window)
        
        # 注册UI组件
        self._register_ui_components()
        
        # 连接状态管理信号
        self._connect_state_management()
        
    def _register_ui_components(self):
        """注册需要状态管理的UI组件"""
        if not self.ui_state_manager:
            return
            
        # 注册菜单actions
        if hasattr(self.main_window, 'menu_manager'):
            menu_actions = self.main_window.menu_manager.get_image_dependent_actions()
            for action in menu_actions:
                self.ui_state_manager.register_image_dependent_action(action)
                
        # 注册工具栏actions
        if hasattr(self.main_window, 'toolbar_manager'):
            toolbar_actions = self.main_window.toolbar_manager.get_image_dependent_actions()
            for action in toolbar_actions:
                self.ui_state_manager.register_image_dependent_action(action)
                
    def _connect_state_management(self):
        """连接状态管理信号"""
        if not self.ui_state_manager:
            return
            
        # 连接状态管理信号
        self.main_window.state_manager.image_state_changed.connect(
            self.ui_state_manager.update_actions_state
        )
        
        # 连接StateController的按钮状态信号
        if (self.main_window.app_controller and 
            hasattr(self.main_window.app_controller, 'state') and
            self.main_window.app_controller.state):
            
            self.main_window.app_controller.state.undo_state_changed.connect(
                lambda enabled: self.update_action_state('undo', enabled)
            )
            self.main_window.app_controller.state.redo_state_changed.connect(
                lambda enabled: self.update_action_state('redo', enabled)
            )
            self.main_window.app_controller.state.effects_state_changed.connect(
                lambda enabled: self.update_action_state('clear_effects', enabled, True)
            )
            
    def handle_service_availability(self, service_name, available):
        """处理服务可用性变化"""
        if service_name == 'app_controller' and available:
            # 当app_controller可用时，重新连接所有信号
            self.connect_all_signals()

        
    def update_action_state(self, action_name: str, enabled: bool, include_toolbar: bool = False):
        """通用的action状态更新方法"""
        # 更新菜单action状态
        menu_action = getattr(self.main_window.menu_manager, f"{action_name}_action", None)
        if menu_action:
            menu_action.setEnabled(enabled)
            
        # 更新工具栏action状态
        if include_toolbar:
            toolbar_action = getattr(self.main_window.toolbar_manager, f"{action_name}_action", None)
            if toolbar_action:
                toolbar_action.setEnabled(enabled)
                
    def set_proxy_quality(self, quality_factor: float):
        """
        设置代理图像质量
        
        Args:
            quality_factor: 质量因子，范围0.1-1.0
        """
        # 直接访问注入的依赖
        state_manager = self.main_window.state_manager
            
        if state_manager and hasattr(state_manager, 'set_proxy_quality'):
                state_manager.set_proxy_quality(quality_factor)
                
                # 更新菜单选中状态
                if hasattr(self.main_window, 'menu_manager') and self.main_window.menu_manager:
                    self.main_window.menu_manager.update_proxy_quality_menu()