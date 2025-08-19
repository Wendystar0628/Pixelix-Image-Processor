from typing import Dict, List, Optional, Any

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

from ..commands.base_command import BaseCommand
from ..operations.base_operation import ImageOperation
from ..interfaces import StateManagerInterface

# 导入各个子模块
from ..repositories.image_repository import ImageRepository
from .pipeline_manager import PipelineManager
from .preview_manager import PreviewManager
from ..services.persistence_service import PersistenceService
from app.layers.business.processing.image_processor import ImageProcessor
from .proxy_workflow_manager import ProxyWorkflowManager
from ..tools.tool_manager import ToolManager


class StateManager(StateManagerInterface):
    """
    中央状态管理器 - 应用运行时状态的统一门面
    
    聚合子模块：ImageRepository, PipelineManager, PreviewManager, 
    ToolManager, ProxyWorkflowManager, PersistenceService
    
    职责：状态访问接口、信号转发、向后兼容的门面
    """

    # 核心信号
    state_changed = pyqtSignal()
    image_state_changed = pyqtSignal(bool)
    tool_changed = pyqtSignal(str)
    processing_started = pyqtSignal()
    processing_finished = pyqtSignal()

    def __init__(self, image_processor):
        super().__init__()
        
        # 通过构造函数注入图像处理器
        self.image_processor = image_processor
        
        # 创建子模块实例
        self.image_repository = ImageRepository()
        self.pipeline_manager = PipelineManager()
        self.preview_manager = PreviewManager()
        self.persistence_service = PersistenceService()
        
        # 直接在构造函数中创建代理工作流管理器
        self.proxy_workflow_manager = ProxyWorkflowManager(
            self.image_processor,
            self.image_repository,
            self.pipeline_manager,
            self.preview_manager
        )
        
        # 聚合重构后的工具管理器（完全独立，不依赖StateManager）
        self.tool_manager = ToolManager()
        
        # 连接信号
        self._setup_signal_connections()
        
    def _setup_signal_connections(self):
        """设置信号连接"""
        # 连接代理工作流的信号
        self.proxy_workflow_manager.processing_started.connect(self._on_processing_started)
        self.proxy_workflow_manager.processing_finished.connect(self._on_processing_finished)
        
        # 连接所有子模块的信号到 notify 方法
        self.pipeline_manager.pipeline_changed.connect(self.notify)
        self.preview_manager.preview_changed.connect(self.notify)
        
        # 连接ToolManager的信号并转发
        self.tool_manager.tool_changed.connect(self.tool_changed)
        self.tool_manager.tool_changed.connect(lambda: self.notify())
        
        # 监听工具操作完成信号，并将操作提交给PipelineManager
        self.tool_manager.operation_created.connect(
            lambda operation: self.pipeline_manager.add_operation(operation)
        )
        
        # 发射初始图像状态信号
        self.image_state_changed.emit(False)
        
    def _on_processing_started(self):
        self.processing_started.emit()
        
    def _on_processing_finished(self, image):
        self.processing_finished.emit()
        self.notify()
        
    def _on_tool_changed(self, tool_name: str):
        self.tool_changed.emit(tool_name)
        self.notify()

    def notify(self):
        """发出状态变化信号，触发UI更新"""
        print("State changed, notifying observers...")  # for debugging
        self.state_changed.emit()
    
    def _reset_processing_state(self):
        """重置所有图像处理相关状态"""
        self.pipeline_manager.reset()
        self.preview_manager.clear_preview_params()
        self.proxy_workflow_manager.reset()
        
    def load_image(self, image, file_path=None):
        """向后兼容接口"""
        # 注意：已重构为不依赖全局ProcessingHandler，改为直接处理
        self.image_repository.load_image(image, file_path)
        self.notify()
        self.image_state_changed.emit(True)
        
    def load_image_proxy(self, proxy_image, file_path=None):
        """向后兼容接口"""
        # 注意：已重构为不依赖全局ProcessingHandler，改为直接处理
        self.image_repository.set_proxy_image(proxy_image)
        if file_path:
            self.image_repository.current_file_path = file_path
        self.notify()
        self.image_state_changed.emit(True)

    def update_with_full_image(self, full_image, file_path=None):
        """用完整图像更新显示状态"""
        self.image_repository.load_image(full_image, file_path)
        proxy = self.proxy_workflow_manager.create_proxy_for_main_view(full_image)
        self.image_repository.set_proxy_image(proxy)
        self.image_repository.switch_to_original_mode()
        self.notify()
        self.image_state_changed.emit(True)

    def is_image_loaded(self) -> bool:
        return self.image_repository.is_image_loaded()
    
    def clear_image(self):
        """向后兼容接口"""
        # 注意：已重构为不依赖全局ProcessingHandler，改为直接处理
        self.image_repository.clear_image()
        self.operation_pipeline_manager.clear_pipeline()
        self.notify()
        self.image_state_changed.emit(False)

    def get_image_for_display(self) -> Optional[np.ndarray]:
        """获取当前显示图像（根据交互模式和代理状态）"""
        if not self.is_image_loaded():
            return None
        
        # 检查代理工作流管理器是否可用
        if (self.proxy_workflow_manager and 
            hasattr(self.proxy_workflow_manager, '_is_interactive_mode') and
            self.proxy_workflow_manager._is_interactive_mode):
            return self.proxy_workflow_manager.update_interaction()
        
        # 非交互模式：使用代理工作流管理器进行渲染
        if self.proxy_workflow_manager:
            return self.proxy_workflow_manager.get_final_render()
        
        # 回退：获取基础图像并应用处理管道效果
        base_image = self.image_repository.get_image_for_display()
        if base_image is None:
            return None
            
        # 应用处理管道效果
        if self.pipeline_manager and hasattr(self.pipeline_manager, 'apply_pipeline'):
            try:
                processed_image = self.pipeline_manager.apply_pipeline(base_image)
                return processed_image
            except Exception as e:
                print(f"应用处理管道失败: {e}")
                return base_image
        
        return base_image
        
    def get_current_image(self) -> Optional[np.ndarray]:
        """[已弃用] 向后兼容接口，使用get_image_for_display"""
        return self.get_image_for_display()
        
    def get_original_image(self) -> Optional[np.ndarray]:
        """获取原始图像（完整分辨率，不考虑代理模式）"""
        if not self.image_repository.is_image_loaded():
            return None
        return self.image_repository.get_image_for_processing()
            
    def get_current_file_path(self) -> Optional[str]:
        return self.image_repository.get_current_file_path()

    def set_current_file_path(self, path: str):
        self.image_repository.set_current_file_path(path)

    def get_pipeline(self) -> List[ImageOperation]:
        return self.pipeline_manager.operation_pipeline

    def get_preview_params(self) -> Optional[Dict]:
        return self.preview_manager.get_preview_params()
        
    def cancel_preview(self):
        self.preview_manager.clear_preview_params()

    def execute_command(self, command: BaseCommand):
        self.pipeline_manager.execute_command(command)
        
    def start_interaction(self):
        """开始交互模式，用于快速预览"""
        if self.proxy_workflow_manager:
            self.proxy_workflow_manager.start_interaction()
        
    def end_interaction(self):
        """结束交互模式，恢复完整质量渲染并保留预览效果"""
        if self.proxy_workflow_manager:
            self.proxy_workflow_manager.end_interaction()
            # 重要：触发UI更新以显示完整质量渲染结果（保留预览效果）
            self.notify()
        
    def set_proxy_quality(self, quality_factor: float):
        """设置代理质量等级"""
        if self.proxy_workflow_manager:
            self.proxy_workflow_manager.set_proxy_quality(quality_factor)
            # 立即触发UI更新以反映质量变化
            self.notify()
        
    def get_proxy_quality(self) -> float:
        return self.proxy_workflow_manager.get_proxy_quality()
        
    def set_image_data(self, image, file_path=None):
        """原子操作：设置图像数据"""
        self.image_repository.load_image(image, file_path)
        self.image_state_changed.emit(True)
    
    def set_proxy_image_data(self, proxy_image, file_path=None):
        """原子操作：设置代理图像数据"""
        self.image_repository.set_current_file_path(file_path)
        self.image_repository.set_proxy_image(proxy_image)
        self.image_repository.switch_to_proxy_mode()
        self.image_state_changed.emit(True)
    
    def reset_all_processing_state(self):
        """原子操作：重置所有处理状态"""
        self._reset_processing_state()
    
    def clear_image_data(self):
        """原子操作：清除图像数据"""
        self.image_repository._original_image = None
        self.image_repository._proxy_image = None
        self.image_repository.current_file_path = None
        self.image_state_changed.emit(False)
        
    @property
    def active_tool_name(self) -> Optional[str]:
        """门面接口：获取当前活动工具名称"""
        return self.tool_manager.active_tool_name
        
    def set_active_tool(self, name: str) -> bool:
        """门面接口：设置活动工具"""
        return self.tool_manager.set_active_tool(name)
            
    def register_tool(self, name: str, tool_type: str):
        """向后兼容接口：注册工具类型"""
        pass
        
    def save_tool_state(self, tool_name: str, state: Dict[str, Any]):
        """门面接口：保存工具状态"""
        self.tool_manager.save_tool_state(tool_name, state)
        
    def get_tool_state(self, tool_name: str) -> Dict[str, Any]:
        """门面接口：获取工具状态"""
        return self.tool_manager.get_tool_state(tool_name)
    
    def get_all_jobs_with_images(self) -> Dict[str, List[str]]:
        """
        获取所有作业及其图像列表
        
        Returns:
            Dict[str, List[str]]: 作业名称到图像路径列表的映射
        """
        jobs_data = {}
        
        # 如果当前有加载的图像，创建一个默认作业
        if self.is_image_loaded():
            current_path = self.get_current_file_path()
            if current_path:
                jobs_data["当前作业"] = [current_path]
        
        # TODO: 这里可以扩展为从批处理系统获取实际的作业数据
        # 如果有批处理管理器，可以从那里获取更完整的作业信息
        
        return jobs_data


# 单例模式已移除，使用依赖注入模式

# 全局访问器函数已删除
# 使用依赖注入方式获取StateManager实例
