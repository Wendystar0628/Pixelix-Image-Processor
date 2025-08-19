import time
from typing import Dict, List, Optional

import numpy as np

from .. import operations
from ..operations.base_operation import ImageOperation
from ..services.persistence_service import OPERATION_CLASS_MAP
from ..interfaces.image_processor_interface import ImageProcessorInterface

# 使用从 persistence_service.py 导入的 OPERATION_CLASS_MAP
OPERATION_MAP = OPERATION_CLASS_MAP


class ImageProcessor(ImageProcessorInterface):
    """
    一个无状态的图像处理引擎。

    它负责执行计算密集型任务，如渲染一个操作流水线。
    这个类不持有任何状态。
    
    注意: 所有与图像分析相关的功能（如直方图计算、RGB波形图等）
    已经被移动到 ImageAnalysisEngine 类中，以实现关注点分离。
    ImageProcessor 现在只专注于图像处理操作的应用。
    """

    def render_pipeline(
        self,
        base_image: Optional[np.ndarray],
        pipeline: List[ImageOperation],
        preview_op_params: Optional[Dict] = None,
        scale_factor: float = 1.0,
    ) -> np.ndarray:
        """
        渲染一个完整的操作流水线。

        该方法会获取基础图像，并按顺序应用流水线中的所有操作。
        如果提供了预览参数，它将在所有已提交的操作之上应用一个临时的预览操作。

        Args:
            base_image (Optional[np.ndarray]): 要处理的基础图像。如果为None，返回占位符图像。
            pipeline (List[ImageOperation]): 要应用的操作流水线。
            preview_op_params (Optional[Dict]): 一个包含预览操作及其参数的字典。
                                               例如: {'op': 'hue_saturation', 'hue': 50, ...}
            scale_factor (float): 图像的缩放因子，用于代理图像处理。当处理低分辨率代理时，
                                 尺度依赖的操作需要相应调整其参数。默认为1.0表示原始尺寸。

        Returns:
            np.ndarray: 应用了所有操作（包括预览）后的最终图像。
        """
        # 记录渲染开始时间
        render_start_time = time.time()
        
        if base_image is None:
            # 如果没有基础图像，则返回一个黑色小方块作为占位符
            return np.zeros((100, 100, 3), dtype=np.uint8)

        processed_image = base_image.copy()
        
        # 1. 应用流水线中的已提交操作
        for i, operation in enumerate(pipeline):
            # 检查操作是否支持scale_factor参数
            if hasattr(operation, 'apply') and 'scale_factor' in operation.apply.__code__.co_varnames:
                processed_image = operation.apply(processed_image, scale_factor=scale_factor)
            else:
                processed_image = operation.apply(processed_image)

        # 2. 如果有预览操作，则应用它
        if preview_op_params and "op" in preview_op_params:
            op_name = preview_op_params["op"]
            if op_name == "reset":
                # "reset" 是一个特殊指令，直接返回当前已提交的状态
                return processed_image

            OpClass = OPERATION_MAP.get(op_name)
            if OpClass:
                try:
                    # 从字典中移除 'op' 键，剩下的就是操作的参数
                    params = {
                        k: v for k, v in preview_op_params.items() if k != "op"
                    }
                    preview_op = OpClass(**params)
                    
                    # 检查预览操作是否支持scale_factor参数
                    if hasattr(preview_op, 'apply') and 'scale_factor' in preview_op.apply.__code__.co_varnames:
                        processed_image = preview_op.apply(processed_image, scale_factor=scale_factor)
                    else:
                        processed_image = preview_op.apply(processed_image)
                        
                except Exception as e:
                    print(f"Error applying preview operation '{op_name}': {e}")
                    # 在预览出错时，最好还是返回当前无预览的图像
                    pass
                        
        # 记录渲染完成时间并计算耗时
        render_end_time = time.time()
        render_duration = render_end_time - render_start_time
        # 如果渲染时间超过一定阈值，可以考虑打印日志或优化相关操作
        if render_duration > 0.1:  # 100ms
            print(f"渲染流水线耗时: {render_duration:.3f}秒")

        return processed_image
