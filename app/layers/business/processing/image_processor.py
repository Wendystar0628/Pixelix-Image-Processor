"""
业务层图像处理器 - 纯业务组件
"""
import time
from typing import Dict, List, Optional

import numpy as np

from app.core.operations.base_operation import ImageOperation
from app.core.services.persistence_service import OPERATION_CLASS_MAP
from ..interfaces.image_processor_interface import BusinessImageProcessorInterface
from ..events.business_event_publisher import BusinessEventPublisher

# 使用从 persistence_service.py 导入的 OPERATION_CLASS_MAP
OPERATION_MAP = OPERATION_CLASS_MAP


class ImageProcessor(BusinessImageProcessorInterface):
    """
    业务层图像处理器 - 完全无状态的纯业务组件
    
    职责：
    - 执行图像处理算法
    - 渲染操作流水线
    - 发布处理完成事件
    - 不依赖任何上层组件（控制器、UI等）
    """

    def __init__(self, event_publisher: Optional[BusinessEventPublisher] = None):
        """
        初始化图像处理器
        
        Args:
            event_publisher: 事件发布器，用于发布处理完成事件
        """
        self._event_publisher = event_publisher or BusinessEventPublisher()

    def render_pipeline(
        self,
        base_image: Optional[np.ndarray],
        pipeline: List[ImageOperation],
        preview_op_params: Optional[Dict] = None,
        scale_factor: float = 1.0,
    ) -> np.ndarray:
        """
        渲染一个完整的操作流水线
        
        该方法会获取基础图像，并按顺序应用流水线中的所有操作。
        如果提供了预览参数，它将在所有已提交的操作之上应用一个临时的预览操作。

        Args:
            base_image: 要处理的基础图像。如果为None，返回占位符图像。
            pipeline: 要应用的操作流水线。
            preview_op_params: 一个包含预览操作及其参数的字典。
                              例如: {'op': 'hue_saturation', 'hue': 50, ...}
            scale_factor: 图像的缩放因子，用于代理图像处理。

        Returns:
            应用了所有操作（包括预览）后的最终图像。
        """
        render_start_time = time.time()
        
        try:
            if base_image is None:
                # 如果没有基础图像，则返回一个黑色小方块作为占位符
                return np.zeros((100, 100, 3), dtype=np.uint8)

            processed_image = base_image.copy()
            
            # 1. 应用流水线中的已提交操作
            for operation in pipeline:
                processed_image = self.apply_single_operation(
                    processed_image, operation, scale_factor
                )

            # 2. 如果有预览操作，则应用它
            if preview_op_params and "op" in preview_op_params:
                processed_image = self._apply_preview_operation(
                    processed_image, preview_op_params, scale_factor
                )
                        
            # 记录渲染完成时间并发布事件
            render_end_time = time.time()
            render_duration = render_end_time - render_start_time
            
            # 发布流水线渲染完成事件
            self._event_publisher.publish_pipeline_rendered(
                pipeline_length=len(pipeline),
                processing_time=render_duration,
                success=True
            )
            
            # 如果渲染时间超过一定阈值，记录性能信息
            if render_duration > 0.1:  # 100ms
                print(f"渲染流水线耗时: {render_duration:.3f}秒")

            return processed_image
            
        except Exception as e:
            render_end_time = time.time()
            render_duration = render_end_time - render_start_time
            
            # 发布处理失败事件
            self._event_publisher.publish_pipeline_rendered(
                pipeline_length=len(pipeline),
                processing_time=render_duration,
                success=False,
                error_message=str(e)
            )
            
            # 重新抛出异常，让上层处理
            raise

    def apply_single_operation(
        self,
        image: np.ndarray,
        operation: ImageOperation,
        scale_factor: float = 1.0
    ) -> np.ndarray:
        """
        应用单个图像操作
        
        Args:
            image: 输入图像
            operation: 要应用的操作
            scale_factor: 缩放因子
            
        Returns:
            处理后的图像
        """
        try:
            # 检查操作是否支持scale_factor参数
            if hasattr(operation, 'apply') and 'scale_factor' in operation.apply.__code__.co_varnames:
                return operation.apply(image, scale_factor=scale_factor)
            else:
                return operation.apply(image)
        except Exception as e:
            print(f"应用操作失败 {type(operation).__name__}: {e}")
            # 操作失败时返回原图像
            return image

    def _apply_preview_operation(
        self,
        image: np.ndarray,
        preview_op_params: Dict,
        scale_factor: float
    ) -> np.ndarray:
        """
        应用预览操作
        
        Args:
            image: 输入图像
            preview_op_params: 预览操作参数
            scale_factor: 缩放因子
            
        Returns:
            应用预览操作后的图像
        """
        op_name = preview_op_params["op"]
        
        if op_name == "reset":
            # "reset" 是一个特殊指令，直接返回当前已提交的状态
            return image

        OpClass = OPERATION_MAP.get(op_name)
        if not OpClass:
            print(f"未知的预览操作: {op_name}")
            return image

        try:
            # 从字典中移除 'op' 键，剩下的就是操作的参数
            params = {
                k: v for k, v in preview_op_params.items() if k != "op"
            }
            preview_op = OpClass(**params)
            
            return self.apply_single_operation(image, preview_op, scale_factor)
            
        except Exception as e:
            print(f"应用预览操作失败 '{op_name}': {e}")
            # 在预览出错时，返回当前无预览的图像
            return image