"""
应用总控制器模块 - 重构版本

使用内部组件模式整合所有子控制器功能，采用依赖注入架构。
"""

from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.core.interfaces import (
    StateManagerInterface, 
    ImageProcessorInterface,
    FileHandlerInterface,
    ProcessingHandlerInterface,
    PresetHandlerInterface
)
from app.core.adapters.core_service_adapter import CoreServiceAdapter
from app.ui.managers.dialog_manager import DialogManager
from app.features.batch_processing.interfaces import BatchProcessingInterface


class AppController(QObject):
    """
    应用总控制器 - 重构版本
    
    使用内部组件模式整合原控制器层功能，采用依赖注入架构。
    每个内部组件负责特定的业务领域。
    """
    
    # 主要信号（从原AppController继承）
    show_error_message = pyqtSignal(str)
    show_info_message = pyqtSignal(str)
    image_loaded = pyqtSignal(str)
    image_saved = pyqtSignal(str)
    
    def __init__(self, 
                 state_manager: StateManagerInterface,
                 file_handler: FileHandlerInterface,
                 preset_handler: PresetHandlerInterface,
                 processing_handler: ProcessingHandlerInterface,
                 batch_processor: Optional[BatchProcessingInterface] = None):
        """
        初始化应用总控制器
        
        Args:
            state_manager: 状态管理器
            file_handler: 文件处理器
            preset_handler: 预设处理器
            processing_handler: 图像处理器
            batch_processor: 批处理处理器（可选）
        """
        super().__init__()
        
        # 核心依赖
        self.state_manager = state_manager
        
        # 内部组件（原独立控制器整合）
        self.file_ops = self.FileOperationsComponent(state_manager, file_handler)
        self.image_ops = self.ImageOperationsComponent(state_manager, processing_handler)
        self.batch_ops = self.BatchOperationsComponent(state_manager, batch_processor)
        self.preset_ops = self.PresetOperationsComponent(preset_handler)
        
        # 对话框管理器（延迟设置）
        self.dialog_manager: Optional[DialogManager] = None
        
        # 创建并配置核心服务适配器
        self.core_service_adapter = CoreServiceAdapter()
        self._register_core_services()
        
        # 连接组件信号到主控制器
        self._connect_component_signals()
    
    def verify_bridge_adapter_configuration(self) -> bool:
        """验证桥接适配器配置完整性"""
        if not self.core_service_adapter:
            return False
        
        state_manager = self.core_service_adapter.get_state_manager()
        
        return state_manager is not None
    
    def _connect_component_signals(self):
        """连接内部组件信号到主控制器信号"""
        # 文件操作信号
        self.file_ops.image_loaded.connect(self.image_loaded)
        self.file_ops.image_saved.connect(self.image_saved)
        self.file_ops.show_error_message.connect(self.show_error_message)
        self.file_ops.show_info_message.connect(self.show_info_message)
        
        # 图像操作信号
        self.image_ops.show_error_message.connect(self.show_error_message)
        self.image_ops.show_info_message.connect(self.show_info_message)
        
        # 预设操作信号
        self.preset_ops.show_error_message.connect(self.show_error_message)
        self.preset_ops.show_info_message.connect(self.show_info_message)
        
        # 批处理操作信号
        self.batch_ops.show_error_message.connect(self.show_error_message)
        self.batch_ops.show_info_message.connect(self.show_info_message)
    
    def _register_core_services(self):
        """注册核心服务到桥接适配器"""
        # 注册状态管理器
        if self.state_manager:
            self.core_service_adapter.register_service('state_manager', self.state_manager)
            
            # 注册工具管理器（通过StateManager访问）
            if hasattr(self.state_manager, 'tool_manager'):
                self.core_service_adapter.register_service('tool_manager', self.state_manager.tool_manager)
    
    def set_config_accessor(self, config_accessor) -> None:
        """设置配置访问器（由应用初始化时调用）"""
        if config_accessor:
            self.core_service_adapter.register_service('config_accessor', config_accessor)
    
    def set_config_service(self, config_service) -> None:
        """设置配置服务（由应用初始化时调用）"""
        if config_service:
            self.core_service_adapter.register_service('config_service', config_service)
    
    def get_config_service(self):
        """获取配置服务"""
        return self.core_service_adapter._services.get('config_service')
    
    def get_config_accessor(self):
        """获取配置访问器"""
        return self.core_service_adapter._services.get('config_accessor')
    
    def get_core_service_adapter(self) -> CoreServiceAdapter:
        """为UI层提供核心服务适配器"""
        return self.core_service_adapter
    
    def set_dialog_manager(self, dialog_manager: DialogManager) -> None:
        """设置对话框管理器"""
        self.dialog_manager = dialog_manager
        self.image_ops.set_dialog_manager(dialog_manager)
    
    # === 文件操作相关公共接口 ===
    
    def open_image(self, parent_widget: QWidget) -> None:
        """打开图像"""
        self.file_ops.open_image(parent_widget)
    
    def open_recent_file(self, file_path: str) -> None:
        """打开最近文件"""
        self.file_ops.open_recent_file(file_path)
    
    def load_image_from_path(self, file_path: str) -> None:
        """从路径加载图像"""
        self.file_ops.load_image_from_path(file_path)
    
    def save_image(self, parent_widget: QWidget) -> None:
        """保存图像"""
        self.file_ops.save_image(parent_widget)
    
    # === 图像操作相关公共接口 ===
    
    def apply_simple_operation(self, op_id: str) -> None:
        """应用简单操作"""
        self.image_ops.apply_simple_operation(op_id)
    
    def undo_last_operation(self) -> None:
        """撤销最后操作"""
        self.image_ops.undo_last_operation()
    
    def redo_last_operation(self) -> None:
        """重做最后操作"""
        self.image_ops.redo_last_operation()
    
    def clear_all_effects(self) -> None:
        """清除所有效果"""
        self.image_ops.clear_all_effects()
    
    def undo(self) -> None:
        """撤销"""
        self.image_ops.undo()
    
    def redo(self) -> None:
        """重做"""
        self.image_ops.redo()
    
    def can_undo(self) -> bool:
        """是否可以撤销"""
        return self.image_ops.can_undo()
    
    def can_redo(self) -> bool:
        """是否可以重做"""
        return self.image_ops.can_redo()
    
    # === 预设操作相关公共接口 ===
    
    def show_apply_preset_dialog(self) -> None:
        """显示应用预设对话框"""
        if self.dialog_manager:
            self.dialog_manager.show_dialog("apply_preset")
        else:
            self.show_error_message.emit("对话框管理器未初始化")
    
    def save_current_as_preset(self, parent_widget: QWidget) -> None:
        """保存当前为预设"""
        self.preset_ops.save_current_as_preset(parent_widget)
    
    def delete_preset(self, parent_widget: QWidget) -> None:
        """删除预设"""
        self.preset_ops.delete_preset(parent_widget)
    
    # === 批处理操作相关公共接口 ===
    
    def add_current_image_to_pool(self) -> None:
        """添加当前图像到池"""
        self.batch_ops.add_current_image_to_pool()
    
    def add_images_to_pool(self, file_paths: list) -> None:
        """添加图像到池"""
        self.batch_ops.add_images_to_pool(file_paths)
    
    def show_import_folder_dialog(self, parent_widget: QWidget) -> None:
        """显示导入文件夹对话框"""
        self.batch_ops.show_import_folder_dialog(parent_widget)
    
    # === 对话框相关公共接口 ===
    
    def show_dialog(self, dialog_id: str) -> None:
        """显示对话框"""
        if self.dialog_manager:
            self.dialog_manager.show_dialog(dialog_id)
    
    def show_help_dialog(self) -> None:
        """显示帮助对话框"""
        if self.dialog_manager:
            self.dialog_manager.show_help_dialog()
    
    def get_batch_processor(self) -> Optional[BatchProcessingInterface]:
        """获取批处理器"""
        return self.batch_ops.batch_processor
    
    # === 内部组件类定义 ===
    
    class FileOperationsComponent(QObject):
        """文件操作组件（整合FileIOController + ImageLoaderController）"""
        
        image_loaded = pyqtSignal(str)
        image_saved = pyqtSignal(str)
        show_error_message = pyqtSignal(str)
        show_info_message = pyqtSignal(str)
        
        def __init__(self, state_manager: StateManagerInterface, file_handler: FileHandlerInterface):
            super().__init__()
            self.state_manager = state_manager
            self.file_handler = file_handler
        
        def open_image(self, parent_widget: QWidget) -> None:
            """打开图像"""
            try:
                file_path = self.file_handler.show_open_dialog(parent_widget)
                if file_path:
                    self.load_image_from_path(file_path)
            except Exception as e:
                self.show_error_message.emit(f"打开图像失败: {str(e)}")
        
        def open_recent_file(self, file_path: str) -> None:
            """打开最近文件"""
            self.load_image_from_path(file_path)
        
        def load_image_from_path(self, file_path: str) -> None:
            """从路径加载图像"""
            try:
                # 1. 使用FileHandler加载图像数据
                image_data, actual_path = self.file_handler.load_image_from_path(file_path)
                
                # 2. 检查加载是否成功
                if image_data is None:
                    self.show_error_message.emit(f"无法加载图像: {file_path}")
                    return
                    
                # 3. 将图像数据传递给StateManager
                self.state_manager.load_image(image_data, actual_path)
                
                # 4. 发射信号
                self.image_loaded.emit(actual_path)
                self.show_info_message.emit(f"图像加载成功: {actual_path}")
            except Exception as e:
                self.show_error_message.emit(f"加载图像失败: {str(e)}")
        
        def save_image(self, parent_widget: QWidget) -> None:
            """保存图像"""
            try:
                if not self.state_manager.is_image_loaded():
                    self.show_error_message.emit("没有可保存的图像")
                    return
                
                file_path = self.file_handler.show_save_dialog(parent_widget)
                if file_path:
                    # 获取处理后的图像并保存
                    processed_image = self.state_manager.get_image_for_display()
                    if processed_image is not None:
                        self.file_handler.save_image(processed_image, file_path)
                        self.image_saved.emit(file_path)
                        self.show_info_message.emit(f"图像保存成功: {file_path}")
            except Exception as e:
                self.show_error_message.emit(f"保存图像失败: {str(e)}")
    
    class ImageOperationsComponent(QObject):
        """图像操作组件（整合ImageOperationController + StateController）"""
        
        show_error_message = pyqtSignal(str)
        show_info_message = pyqtSignal(str)
        
        def __init__(self, state_manager: StateManagerInterface, processing_handler: ProcessingHandlerInterface):
            super().__init__()
            self.state_manager = state_manager
            self.processing_handler = processing_handler
            self.dialog_manager: Optional[DialogManager] = None
        
        def set_dialog_manager(self, dialog_manager: DialogManager) -> None:
            """设置对话框管理器"""
            self.dialog_manager = dialog_manager
        
        def apply_simple_operation(self, op_id: str) -> None:
            """应用简单操作"""
            try:
                if not self.state_manager.is_image_loaded():
                    self.show_error_message.emit("请先加载图像")
                    return
                
                if hasattr(self.processing_handler, 'apply_simple_operation'):
                    self.processing_handler.apply_simple_operation(op_id)
                    self.show_info_message.emit(f"操作应用成功: {op_id}")
            except Exception as e:
                self.show_error_message.emit(f"应用操作失败: {str(e)}")
        
        def undo_last_operation(self) -> None:
            """撤销最后操作"""
            self.undo()
        
        def redo_last_operation(self) -> None:
            """重做最后操作"""
            self.redo()
        
        def clear_all_effects(self) -> None:
            """清除所有效果"""
            try:
                if hasattr(self.processing_handler, 'clear_all_effects'):
                    self.processing_handler.clear_all_effects()
                    self.show_info_message.emit("所有效果已清除")
            except Exception as e:
                self.show_error_message.emit(f"清除效果失败: {str(e)}")
        
        def undo(self) -> None:
            """撤销"""
            try:
                if self.can_undo():
                    pipeline_manager = self.state_manager.pipeline_manager
                    if pipeline_manager and hasattr(pipeline_manager, 'undo'):
                        pipeline_manager.undo()
                        self.show_info_message.emit("撤销操作成功")
                else:
                    self.show_info_message.emit("没有可撤销的操作")
            except Exception as e:
                self.show_error_message.emit(f"撤销失败: {str(e)}")
        
        def redo(self) -> None:
            """重做"""
            try:
                if self.can_redo():
                    pipeline_manager = self.state_manager.pipeline_manager
                    if pipeline_manager and hasattr(pipeline_manager, 'redo'):
                        pipeline_manager.redo()
                        self.show_info_message.emit("重做操作成功")
                else:
                    self.show_info_message.emit("没有可重做的操作")
            except Exception as e:
                self.show_error_message.emit(f"重做失败: {str(e)}")
        
        def can_undo(self) -> bool:
            """是否可以撤销"""
            pipeline_manager = self.state_manager.pipeline_manager
            return pipeline_manager and hasattr(pipeline_manager, 'can_undo') and pipeline_manager.can_undo()
        
        def can_redo(self) -> bool:
            """是否可以重做"""
            pipeline_manager = self.state_manager.pipeline_manager
            return pipeline_manager and hasattr(pipeline_manager, 'can_redo') and pipeline_manager.can_redo()
    
    class BatchOperationsComponent(QObject):
        """批处理操作组件（整合BatchProcessingController）"""
        
        show_error_message = pyqtSignal(str)
        show_info_message = pyqtSignal(str)
        
        def __init__(self, state_manager: StateManagerInterface, 
                     batch_processor: Optional[BatchProcessingInterface] = None):
            super().__init__()
            self.state_manager = state_manager
            self.batch_processor = batch_processor
            
            # 连接批处理器信号（如果可用）
            if self.batch_processor:
                self.batch_processor.show_error_message.connect(self.show_error_message)
                self.batch_processor.show_info_message.connect(self.show_info_message)
        
        def add_current_image_to_pool(self) -> None:
            """添加当前图像到池"""
            if not self.batch_processor:
                self.show_error_message.emit("批处理功能不可用")
                return
                
            try:
                if not self.state_manager.is_image_loaded():
                    self.show_error_message.emit("没有可添加的图像")
                    return
                
                # 获取当前图像路径
                current_path = self.state_manager.get_current_file_path()
                if current_path:
                    # 使用批处理接口添加图像
                    added_count = self.batch_processor.add_images_to_pool([current_path])
                    if added_count > 0:
                        self.show_info_message.emit(f"图像已添加到处理池: {current_path}")
                    else:
                        self.show_error_message.emit("添加图像到处理池失败")
                else:
                    self.show_error_message.emit("无法获取当前图像路径")
            except Exception as e:
                self.show_error_message.emit(f"添加图像失败: {str(e)}")
        
        def add_images_to_pool(self, file_paths: list) -> None:
            """添加图像到池"""
            if not self.batch_processor:
                self.show_error_message.emit("批处理功能不可用")
                return
                
            try:
                if not file_paths:
                    self.show_error_message.emit("没有选择图像文件")
                    return
                
                # 使用批处理接口批量添加图像
                added_count = self.batch_processor.add_images_to_pool(file_paths)
                if added_count > 0:
                    self.show_info_message.emit(f"已添加 {added_count} 个图像到处理池")
                else:
                    self.show_error_message.emit("没有图像被添加到处理池")
            except Exception as e:
                self.show_error_message.emit(f"批量添加失败: {str(e)}")
        
        def show_import_folder_dialog(self, parent_widget: QWidget) -> None:
            """显示导入文件夹对话框"""
            if not self.batch_processor:
                self.show_error_message.emit("批处理功能不可用")
                return
                
            try:
                # 使用批处理接口显示导入对话框
                imported_count = self.batch_processor.show_import_folder_dialog(parent_widget)
                if imported_count > 0:
                    self.show_info_message.emit(f"成功导入 {imported_count} 个图像文件")
                else:
                    self.show_info_message.emit("没有导入任何图像文件")
            except Exception as e:
                self.show_error_message.emit(f"显示导入对话框失败: {str(e)}")
        
        # === 新增批处理功能方法 ===
        
        def get_pool_images_count(self) -> int:
            """获取图像池中的图像数量"""
            if not self.batch_processor:
                return 0
            return len(self.batch_processor.get_pool_images())
        
        def is_pool_empty(self) -> bool:
            """检查图像池是否为空"""
            if not self.batch_processor:
                return True
            return self.batch_processor.is_pool_empty()
        
        def clear_image_pool(self) -> None:
            """清空图像池"""
            if not self.batch_processor:
                self.show_error_message.emit("批处理功能不可用")
                return
                
            try:
                cleared_count = self.batch_processor.clear_image_pool()
                if cleared_count > 0:
                    self.show_info_message.emit(f"已清空图像池，移除了 {cleared_count} 个图像")
                else:
                    self.show_info_message.emit("图像池已经是空的")
            except Exception as e:
                self.show_error_message.emit(f"清空图像池失败: {str(e)}")
        
        def get_all_jobs_count(self) -> int:
            """获取所有作业数量"""
            if not self.batch_processor:
                return 0
            return len(self.batch_processor.get_all_jobs())
        
        def create_new_job(self, job_name: str) -> bool:
            """创建新作业"""
            if not self.batch_processor:
                self.show_error_message.emit("批处理功能不可用")
                return False
                
            try:
                job = self.batch_processor.add_job(job_name)
                if job:
                    self.show_info_message.emit(f"成功创建作业: {job_name}")
                    return True
                else:
                    self.show_error_message.emit(f"创建作业失败: {job_name}")
                    return False
            except Exception as e:
                self.show_error_message.emit(f"创建作业失败: {str(e)}")
                return False
    
    class PresetOperationsComponent(QObject):
        """预设操作组件（整合PresetController + DialogController）"""
        
        show_error_message = pyqtSignal(str)
        show_info_message = pyqtSignal(str)
        
        def __init__(self, preset_handler: PresetHandlerInterface):
            super().__init__()
            self.preset_handler = preset_handler
            
            # 连接预设处理器信号
            self.preset_handler.show_error_message.connect(self.show_error_message)
            self.preset_handler.show_info_message.connect(self.show_info_message)
        

        
        def save_current_as_preset(self, parent_widget: QWidget) -> None:
            """保存当前为预设"""
            self.preset_handler.save_current_as_preset(parent_widget)
        
        def delete_preset(self, parent_widget: QWidget) -> None:
            """删除预设"""
            self.preset_handler.delete_preset(parent_widget)