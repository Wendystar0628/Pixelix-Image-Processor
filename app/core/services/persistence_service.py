from typing import Dict, List, Optional, Any, Type
import json
import os

from ..operations.base_operation import ImageOperation
from ..operations.brightness_contrast_op import BrightnessContrastOp
from ..operations.color_balance_op import ColorBalanceOp
from ..operations.curves_op import CurvesOp
from ..operations.grayscale_op import GrayscaleOp
from ..operations.histogram_equalization_op import HistogramEqualizationOp
from ..operations.hue_saturation_op import HueSaturationOp
from ..operations.invert_op import InvertOp
from ..operations.levels_op import LevelsOp
from ..operations.otsu_threshold_op import OtsuThresholdOp
from ..operations.threshold_op import ThresholdOp

# 导入空间滤波操作
from ..operations.spatial_filtering import (
    GaussianBlurFilterOp,
    LaplacianEdgeFilterOp,
    SobelEdgeFilterOp,
    SharpenFilterOp,
    MeanFilterOp,
)

# 导入常规滤镜操作
from ..operations.regular_filters import (
    EmbossFilterOp,
    MosaicFilterOp,
    OilPaintingFilterOp,
    SketchFilterOp,
    VintageFilterOp,
    # 新增滤镜操作
    WatercolorFilterOp,
    PencilSketchFilterOp,
    CartoonFilterOp,
    WarmToneFilterOp,
    CoolToneFilterOp,
    FilmGrainFilterOp,
    NoiseFilterOp,
    FrostedGlassFilterOp,
    FabricTextureFilterOp,
    VignetteFilterOp,
)


# 操作类型映射
OPERATION_CLASS_MAP: Dict[str, Type[ImageOperation]] = {
    "brightness_contrast": BrightnessContrastOp,
    "color_balance": ColorBalanceOp,
    "curves": CurvesOp,
    "grayscale": GrayscaleOp,
    "histogram_equalization": HistogramEqualizationOp,
    "hue_saturation": HueSaturationOp,
    "invert": InvertOp,
    "levels": LevelsOp,
    "otsu_threshold": OtsuThresholdOp,
    "threshold": ThresholdOp,
    # 空间滤波操作
    "gaussian_blur": GaussianBlurFilterOp,
    "laplacian_edge": LaplacianEdgeFilterOp,
    "sobel_edge": SobelEdgeFilterOp,
    "sharpen": SharpenFilterOp,
    "mean_filter": MeanFilterOp,
    # 常规滤镜操作
    "emboss": EmbossFilterOp,
    "mosaic": MosaicFilterOp,
    "oil_painting": OilPaintingFilterOp,
    "sketch": SketchFilterOp,
    "vintage": VintageFilterOp,
    # 新增滤镜操作
    "watercolor": WatercolorFilterOp,
    "pencil_sketch": PencilSketchFilterOp,
    "cartoon": CartoonFilterOp,
    "warm_tone": WarmToneFilterOp,
    "cool_tone": CoolToneFilterOp,
    "film_grain": FilmGrainFilterOp,
    "noise": NoiseFilterOp,
    "frosted_glass": FrostedGlassFilterOp,
    "fabric_texture": FabricTextureFilterOp,
    "vignette": VignetteFilterOp,
}


class PersistenceService:
    """
    持久化服务。
    
    负责所有与文件系统交互的序列化/反序列化操作（读/写项目文件、配置等）。
    """
    
    def __init__(self):
        pass
        
    @staticmethod
    def serialize_operation(operation: ImageOperation) -> Dict[str, Any]:
        """
        将操作序列化为字典
        
        Args:
            operation: 要序列化的操作
            
        Returns:
            Dict[str, Any]: 序列化后的字典
        """
        # 获取操作类型
        op_type = operation.__class__.__name__
        if op_type.endswith("Op"):
            op_type = op_type[:-2].lower()  # 移除"Op"后缀并转为小写
            
        # 获取操作参数
        params = operation.get_params()
        
        # 构建序列化字典
        serialized = {
            "type": op_type,
            "params": params
        }
        
        return serialized
        
    @staticmethod
    def deserialize_operation(serialized: Dict[str, Any]) -> Optional[ImageOperation]:
        """
        从序列化字典创建操作实例
        
        Args:
            serialized: 序列化的操作字典
            
        Returns:
            Optional[ImageOperation]: 创建的操作实例，如果失败则返回None
        """
        op_type = serialized.get("type", "")
        params = serialized.get("params", {})
        
        # 获取操作类
        op_class = OPERATION_CLASS_MAP.get(op_type)
        if op_class is None:
            print(f"未知的操作类型: {op_type}")
            return None
            
        try:
            # 创建操作实例
            operation = op_class(**params)
            return operation
        except Exception as e:
            print(f"创建操作实例失败: {e}")
            return None
    
    def serialize_pipeline(self, pipeline_manager) -> List[Dict[str, Any]]:
        """
        将当前操作流水线序列化为字典列表
        
        Args:
            pipeline_manager: PipelineManager 实例
            
        Returns:
            List[Dict[str, Any]]: 序列化后的字典列表
        """
        return [self.serialize_operation(op) for op in pipeline_manager.operation_pipeline]
    
    def deserialize_pipeline(self, serialized: List[Dict[str, Any]]) -> List[ImageOperation]:
        """
        从序列化字典列表创建操作流水线
        
        Args:
            serialized: 序列化的操作字典列表
            
        Returns:
            List[ImageOperation]: 创建的操作流水线
        """
        pipeline = []
        
        for op_dict in serialized:
            operation = self.deserialize_operation(op_dict)
            if operation is not None:
                pipeline.append(operation)
                
        return pipeline
    
    def save_pipeline_to_file(self, pipeline_manager, file_path: str) -> bool:
        """
        将当前操作流水线保存到文件
        
        Args:
            pipeline_manager: PipelineManager 实例
            file_path: 保存路径
            
        Returns:
            bool: 是否成功保存
        """
        try:
            # 序列化流水线
            serialized = self.serialize_pipeline(pipeline_manager)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serialized, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"保存操作流水线失败: {e}")
            return False
    
    def load_pipeline_from_file(self, file_path: str) -> Optional[List[ImageOperation]]:
        """
        从文件加载操作流水线
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[List[ImageOperation]]: 加载的操作流水线，如果失败则返回None
        """
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                serialized = json.load(f)
                
            # 反序列化流水线
            pipeline = self.deserialize_pipeline(serialized)
            
            return pipeline
        except Exception as e:
            print(f"加载操作流水线失败: {e}")
            return None
            
    def serialize_tools_state(self, tool_manager) -> Dict[str, Any]:
        """
        序列化所有工具状态
        
        Args:
            tool_manager: ToolManager 实例
            
        Returns:
            Dict[str, Any]: 包含工具状态的字典
        """
        # 新的 ToolManager 不再有 serialize_tools_state 方法
        # 我们需要直接构建工具状态字典
        return {
            "active_tool": tool_manager.active_tool_name,
            "tool_states": {name: tool.get_state() for name, tool in tool_manager._tools.items()}
        }
            
    def save_complete_state_to_file(self, pipeline_manager, tool_manager, file_path: str) -> bool:
        """
        将完整的应用程序状态保存到文件
        
        Args:
            pipeline_manager: PipelineManager 实例
            tool_manager: ToolManager 实例（新的基于 app.core.tools.tool_manager 的实现）
            file_path: 保存路径
            
        Returns:
            bool: 是否成功保存
        """
        try:
            # 序列化操作流水线
            pipeline_data = self.serialize_pipeline(pipeline_manager)
            
            # 序列化工具状态
            tools_data = self.serialize_tools_state(tool_manager)
            
            # 构建完整状态
            complete_state = {
                "pipeline": pipeline_data,
                "tools": tools_data,
                # 可以添加其他状态组件
            }
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(complete_state, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"保存完整状态失败: {e}")
            return False
            
    def load_complete_state_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        从文件加载完整的应用程序状态
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[Dict[str, Any]]: 加载的完整状态，如果失败则返回None
        """
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                complete_state = json.load(f)
                
            return complete_state
        except Exception as e:
            print(f"加载完整状态失败: {e}")
            return None 