"""
代理工作流管理器模块

该模块定义了ProxyWorkflowManager类，负责协调预览降采样的工作流。
"""

from typing import Optional, Tuple
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

from ..processing_context import ProcessingContext
from app.layers.business.processing.image_processor import ImageProcessor
from ..repositories.image_repository import ImageRepository
from .pipeline_manager import PipelineManager
from .preview_manager import PreviewManager
from ..utils.proxy_utils import create_proxy_image


class ProxyWorkflowManager(QObject):
    """
    代理工作流管理器。
    
    负责所有代理图像的创建、管理和协调，包括：
    1. 创建和管理交互式预览代理
    2. 创建和管理主视图代理
    3. 管理代理质量设置
    4. 协调代理的使用时机
    
    这个类是代理相关所有业务逻辑的唯一来源。
    """
    
    # 定义信号
    processing_started = pyqtSignal()  # 处理开始信号
    processing_finished = pyqtSignal(np.ndarray)  # 处理完成信号，传递处理后的图像
    interaction_started = pyqtSignal()  # 交互开始信号
    interaction_ended = pyqtSignal()  # 交互结束信号
    proxy_quality_changed = pyqtSignal(float)  # 代理质量变更信号
    
    def __init__(
        self, 
        image_processor: ImageProcessor, 
        image_repository: ImageRepository,
        pipeline_manager: PipelineManager,
        preview_manager: PreviewManager
    ):
        """
        初始化代理工作流管理器
        
        Args:
            image_processor: 图像处理器实例
            image_repository: 图像仓库实例
            pipeline_manager: 流水线管理器实例
            preview_manager: 预览管理器实例
        """
        super().__init__()
        self._image_processor = image_processor
        self._image_repository = image_repository
        self._pipeline_manager = pipeline_manager
        self._preview_manager = preview_manager
        
        # 创建处理上下文对象
        self._context = ProcessingContext()
        
        # 交互模式状态
        self._is_interactive_mode = False
        
        # 内部维护的代理图像和缩放因子
        self._interaction_proxy_image: Optional[np.ndarray] = None
        self._interaction_scale_factor: float = 1.0
    
    # ----- 代理质量管理方法 -----
    
    def set_proxy_quality(self, quality_factor: float) -> None:
        """
        设置代理图像的质量因子
        
        Args:
            quality_factor: 质量因子，范围0.1-1.0
                           0.1: 极低质量（最快）
                           0.25: 低质量
                           0.5: 中等质量
                           0.75: 高质量
                           1.0: 原始质量（最慢）
        """
        # 确保质量因子在有效范围内
        quality_factor = max(0.1, min(1.0, quality_factor))
        
        # 更新内部质量因子
        self._context.proxy_quality_factor = quality_factor
        
        # 更新当前代理图像(如果有)
        self._update_all_proxies()
        
        # 发出质量变更信号
        self.proxy_quality_changed.emit(quality_factor)
    
    def get_proxy_quality(self) -> float:
        """
        获取代理图像的质量因子
        
        Returns:
            代理图像的质量因子(0.1-1.0)
        """
        # 返回内部存储的质量因子
        return self._context.proxy_quality_factor
    
    def _update_all_proxies(self) -> None:
        """
        当代理质量变更时，更新所有代理图像
        """
        # 只在有图像加载时更新
        if not self._image_repository.is_image_loaded():
            return
            
        # 获取原始图像
        original_image = self._image_repository.get_image_for_processing()
        if original_image is None:
            return
        
        # 更新主视图代理
        main_view_proxy = self.create_proxy_for_main_view(original_image)
        self._image_repository.set_proxy_image(main_view_proxy)
        
        # 如果处于交互模式，也更新交互代理
        if self._is_interactive_mode:
            self._interaction_proxy_image, self._interaction_scale_factor = self._create_proxy(original_image)
            
            # 触发重新渲染
            result = self.update_interaction()
            self.processing_finished.emit(result)
    
    # ----- 主视图代理方法 -----
    
    def create_proxy_for_main_view(self, original_image: np.ndarray) -> np.ndarray:
        """
        为主视图创建代理图像
        
        Args:
            original_image: 原始高分辨率图像
            
        Returns:
            代理图像
        """
        proxy_image, _ = self._create_proxy(original_image)
        return proxy_image
    
    def update_main_view_proxy(self) -> Optional[np.ndarray]:
        """
        更新主视图的代理图像
        
        Returns:
            Optional[np.ndarray]: 新的代理图像或None
        """
        if not self._image_repository.is_image_loaded():
            return None
            
        # 获取原始图像
        original_image = self._image_repository.get_image_for_processing()
        if original_image is None:
            return None
            
        # 创建新的代理
        proxy_image = self.create_proxy_for_main_view(original_image)
        
        # 更新到图像仓库
        self._image_repository.set_proxy_image(proxy_image)
        
        return proxy_image
    
    # ----- 交互模式代理方法 -----
    
    def start_interaction(self) -> None:
        """
        开始交互模式
        
        在用户按下滑块时调用，创建代理图像，并设置交互状态。
        """
        if not self._image_repository.is_image_loaded():
            return
            
        # 获取原始图像
        original_image = self._image_repository.get_image_for_processing()
        if original_image is None:
            return
            
        # 设置交互模式标志
        self._is_interactive_mode = True
        
        # 创建交互用的代理图像
        self._interaction_proxy_image, self._interaction_scale_factor = self._create_proxy(original_image)
        
        # 发出信号
        self.interaction_started.emit()
    
    def update_interaction(self) -> np.ndarray:
        """
        更新交互式预览
        
        在滑块移动时调用，使用代理图像快速渲染当前操作。
        
        Returns:
            处理后的代理图像
        """
        if not self._is_interactive_mode or self._interaction_proxy_image is None:
            return self._render_with_original()
            
        # 获取当前操作流水线和预览参数
        pipeline = self._pipeline_manager.operation_pipeline
        preview_params = self._preview_manager.get_preview_params()
        
        # 使用交互代理图像和缩放因子渲染
        result = self._image_processor.render_pipeline(
            self._interaction_proxy_image,
            pipeline,
            preview_params,
            self._interaction_scale_factor
        )
        
        return result
    
    def end_interaction(self) -> None:
        """
        结束交互模式
        
        在用户松开滑块时调用，触发对原始图像的最终渲染。
        """
        if not self._is_interactive_mode:
            return
            
        # 重置交互模式状态
        self._is_interactive_mode = False
        self._interaction_proxy_image = None
        
        # 发出信号
        self.interaction_ended.emit()
        
        # 触发对原始图像的最终渲染
        self.render_final()
    
    # ----- 渲染和工具方法 -----
    
    def render_final(self) -> None:
        """
        渲染最终结果
        
        在交互结束后，对原始图像进行完整的渲染。
        """
        # 发出处理开始的信号
        self.processing_started.emit()
        
        # 使用原始图像进行最终渲染
        result = self._render_with_original()
        
        # 发出处理完成的信号
        self.processing_finished.emit(result)
    
    def _render_with_original(self) -> np.ndarray:
        """
        使用原始图像进行渲染
        
        Returns:
            渲染后的图像
        """
        original_image = self._image_repository.get_image_for_processing()
        if original_image is None:
            return np.zeros((100, 100, 3), dtype=np.uint8)
            
        pipeline = self._pipeline_manager.operation_pipeline
        preview_params = self._preview_manager.get_preview_params()
        
        # 使用原始图像和默认缩放因子渲染
        return self._image_processor.render_pipeline(
            original_image,
            pipeline,
            preview_params,
            scale_factor=1.0
        )
    
    def get_final_render(self) -> np.ndarray:
        """
        获取最终渲染结果（非交互模式）
        
        在非交互模式下，如果存在预览参数，会将预览效果应用到全分辨率图像上。
        这确保了用户在松开滑块后能看到全分辨率的预览效果。
        
        Returns:
            最终渲染的图像
        """
        # 获取原始图像
        original_image = self._image_repository.get_image_for_processing()
        if original_image is None:
            # 如果没有原始图像，尝试获取显示图像
            display_image = self._image_repository.get_image_for_display()
            if display_image is None:
                return np.zeros((100, 100, 3), dtype=np.uint8)
            original_image = display_image
            
        pipeline = self._pipeline_manager.operation_pipeline
        preview_params = self._preview_manager.get_preview_params()
        
        # 如果有预览参数，应用到全分辨率图像（实现用户需求：松开滑块后看到全分辨率预览效果）
        if preview_params:
            return self._image_processor.render_pipeline(
                original_image,
                pipeline,
                preview_params,
                scale_factor=1.0
            )
        
        # 没有预览参数时，只应用处理管道
        processed_image = original_image
        for operation in pipeline:
            processed_image = operation.apply(processed_image)
        
        return processed_image
    
    def reset(self) -> None:
        """
        重置代理工作流状态
        
        在加载新图像时调用，清除所有代理状态。
        """
        self._is_interactive_mode = False
        self._interaction_proxy_image = None
        self._interaction_scale_factor = 1.0
        
    def _create_proxy(self, original_image: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        创建代理图像的核心方法
        
        Args:
            original_image: 原始高分辨率图像
            
        Returns:
            (代理图像, 缩放因子) 元组
        """
        quality_factor = self.get_proxy_quality()
        return create_proxy_image(original_image, quality_factor)
        
    def get_display_image(self) -> Optional[np.ndarray]:
        """
        获取用于显示的图像
        
        这个方法用于委托给ImageRepository，让它知道该返回什么图像
        
        Returns:
            应该显示的图像
        """
        return self._image_repository.get_image_for_display() 