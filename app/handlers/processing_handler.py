from typing import Dict, Type, Optional, Tuple, Any
import logging

import os
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget

logger = logging.getLogger(__name__)

from ..core.commands.operation_commands import AddOperationCommand
from ..core.operations.base_operation import ImageOperation
from ..core.operations import (
    BrightnessContrastOp,
    ColorBalanceOp,
    CurvesOp,
    GrayscaleOp,
    HistogramEqualizationOp,
    HueSaturationOp,
    InvertOp,
    LevelsOp,
    OtsuThresholdOp,
    ThresholdOp,
)

# 导入空间滤波操作
from ..core.operations.spatial_filtering import (
    GaussianBlurFilterOp,
    LaplacianEdgeFilterOp,
    SobelEdgeFilterOp,
    SharpenFilterOp,
    MeanFilterOp,
)

# 导入常规滤镜操作
from ..core.operations.regular_filters import (
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

# 导入图像变换操作
from ..core.operations.image_scaling import (
    NearestScaleUpOp,
    BilinearScaleUpOp,
    BicubicScaleUpOp,
    LanczosScaleUpOp,
    EdgePreservingScaleUpOp,
    NearestScaleDownOp,
    BilinearScaleDownOp,
    AreaAverageScaleDownOp,
    GaussianScaleDownOp,
    AntiAliasScaleDownOp,
)

from ..core.operations.image_compression import (
    JpegCompressionOp,
    PngCompressionOp,
    WebpCompressionOp,
    ColorQuantizationOp,
    LossyOptimizationOp,
)
from ..core.models.operation_params import (
    BaseOperationParams,
    BrightnessContrastParams,
    ColorBalanceParams,
    CurvesParams,
    HueSaturationParams,
    LevelsParams,
    ThresholdParams,
)

# 导入滤波参数类
from ..core.models.spatial_filter_params import (
    GaussianBlurParams,
    LaplacianEdgeParams,
    SobelEdgeParams,
    SharpenParams,
    MeanFilterParams,
)

from ..core.models.regular_filter_params import (
    EmbossParams,
    MosaicParams,
    OilPaintingParams,
    SketchParams,
    VintageParams,
    # 新增滤镜参数
    WatercolorParams,
    PencilSketchParams,
    CartoonParams,
    WarmToneParams,
    CoolToneParams,
    FilmGrainParams,
    NoiseParams,
    FrostedGlassParams,
    FabricTextureParams,
    VignetteParams,
)

# 导入图像变换参数类
from ..core.models.scale_up_params import ScaleUpParams
from ..core.models.scale_down_params import ScaleDownParams
from ..core.models.compression_params import CompressionParams
from ..core.managers.state_manager import StateManager
from ..core.managers.pipeline_manager import PipelineManager
from ..core.managers.preview_manager import PreviewManager
from ..core.interfaces.processing_handler_interface import ProcessingHandlerInterface
# from ..utils.timer_utils import timer # 移除导入


class ProcessingHandler(ProcessingHandlerInterface):
    """
    处理图像操作相关UI事件的处理器。

    它监听来自UI的信号，创建对应的Command，并交由PipelineManager执行。
    """
    # 添加信号，用于通知UI更新
    show_error_message = pyqtSignal(str)  # 错误信息
    
    # 处理状态信号（转发自StateManager）
    processing_started = pyqtSignal()  # 处理开始
    processing_finished = pyqtSignal()  # 处理完成

    def __init__(self, state_manager: StateManager):
        super().__init__()
        self._state_manager = state_manager
        # 从 state_manager 获取子模块引用
        self.pipeline_manager = state_manager.pipeline_manager
        self.preview_manager = state_manager.preview_manager
        
        # 连接处理状态信号
        self._state_manager.processing_started.connect(self.processing_started)
        self._state_manager.processing_finished.connect(self.processing_finished)

    def _create_and_execute_command(self, op_class: Type[ImageOperation], params: Optional[BaseOperationParams] = None):
        """
        一个通用的辅助方法，用于创建和执行一个操作命令。
        
        Args:
            op_class: 要实例化的操作类 (例如 BrightnessContrastOp).
            params: 传递给操作类构造函数的参数对象。
        """
        if params:
            # 将dataclass转换为字典，用于传递给操作类
            op_params = params.__dict__
            operation = op_class(**op_params)
        else:
            operation = op_class()
            
        command = AddOperationCommand(operation, self.pipeline_manager)
        # 直接使用 pipeline_manager 执行命令
        self.pipeline_manager.execute_command(command)
        print(f"{op_class.__name__} command executed.")

    # --- 预览和交互相关方法 ---
    
    @pyqtSlot()
    def on_slider_pressed(self):
        """
        响应滑块按下事件
        
        启动代理工作流，创建低分辨率的代理图像以进行快速预览。
        
        注意：此方法假设调用时已有图像加载，UI层负责确保这一前置条件。
        """
        # 开始交互模式
        self._state_manager.start_interaction()
    
    @pyqtSlot()
    def on_slider_released(self):
        """
        响应滑块释放事件
        
        结束代理工作流，触发高质量的最终渲染。
        
        注意：此方法假设调用时已有图像加载，UI层负责确保这一前置条件。
        """
        # 结束交互模式
        self._state_manager.end_interaction()
    
    def start_preview(self, op_id: str, params: BaseOperationParams) -> None:
        """
        开始一个实时预览。
        它会将操作ID和参数传递给预览管理器。
        
        Args:
            op_id: 操作ID，用于指示预览操作的类型
            params: 操作参数
        """
        # 将dataclass转换为字典，并添加操作ID
        preview_params = params.__dict__.copy()
        preview_params['op'] = op_id
        # 使用预览管理器设置预览参数
        self.preview_manager.set_preview_params(preview_params)

    @pyqtSlot()
    def cancel_preview(self) -> None:
        """响应UI的请求，清除预览状态。"""
        # 直接使用 preview_manager 清除预览参数
        self.preview_manager.clear_preview_params()
    
    def get_current_image_info(self) -> Optional[Tuple[int, int, int]]:
        """
        获取当前图像的基本信息
        
        Returns:
            Optional[Tuple[int, int, int]]: (width, height, channels) 或 None
        """
        if self._state_manager and self._state_manager.image_repository:
            image = self._state_manager.image_repository.get_image_for_processing()
            if image is not None:
                height, width = image.shape[:2]
                channels = image.shape[2] if len(image.shape) == 3 else 1
                return (width, height, channels)
        return None

    @pyqtSlot(BrightnessContrastParams)
    def apply_brightness_contrast(self, params: BrightnessContrastParams):
        """响应"亮度/对比度"对话框的应用信号。"""
        self._create_and_execute_command(BrightnessContrastOp, params)

    @pyqtSlot(ColorBalanceParams)
    def apply_color_balance(self, params: ColorBalanceParams):
        """响应"色彩平衡"对话框的应用信号。"""
        self._create_and_execute_command(ColorBalanceOp, params)

    @pyqtSlot(LevelsParams)
    def apply_levels(self, params: LevelsParams):
        """响应"色阶调整"对话框的应用信号。"""
        self._create_and_execute_command(LevelsOp, params)

    @pyqtSlot(CurvesParams)
    def apply_curves(self, params: CurvesParams):
        """响应"曲线调整"对话框的应用信号。"""
        self._create_and_execute_command(CurvesOp, params)

    @pyqtSlot(HueSaturationParams)
    def apply_hue_saturation(self, params: HueSaturationParams):
        """响应"色相/饱和度"对话框的应用信号。"""
        self._create_and_execute_command(HueSaturationOp, params)

    @pyqtSlot()
    def apply_grayscale(self):
        """响应灰度转换操作。"""
        self._create_and_execute_command(GrayscaleOp)

    @pyqtSlot()
    def apply_invert(self):
        """响应色彩反转操作。"""
        self._create_and_execute_command(InvertOp)

    @pyqtSlot(ThresholdParams)
    def apply_threshold(self, params: ThresholdParams):
        """响应手动阈值处理操作。"""
        self._create_and_execute_command(ThresholdOp, params)

    @pyqtSlot()
    def apply_otsu_threshold(self):
        """响应大津法自动阈值操作。"""
        self._create_and_execute_command(OtsuThresholdOp)

    @pyqtSlot()
    def apply_histogram_equalization(self):
        """响应直方图均衡化操作。"""
        self._create_and_execute_command(HistogramEqualizationOp)

    # --- 空间滤波操作方法 ---
    
    @pyqtSlot(GaussianBlurParams)
    def apply_gaussian_blur(self, params: GaussianBlurParams):
        """响应高斯模糊滤波操作。"""
        self._create_and_execute_command(GaussianBlurFilterOp, params)
    
    @pyqtSlot(LaplacianEdgeParams)
    def apply_laplacian_edge(self, params: LaplacianEdgeParams):
        """响应拉普拉斯边缘检测操作。"""
        self._create_and_execute_command(LaplacianEdgeFilterOp, params)
    
    @pyqtSlot(SobelEdgeParams)
    def apply_sobel_edge(self, params: SobelEdgeParams):
        """响应Sobel边缘检测操作。"""
        self._create_and_execute_command(SobelEdgeFilterOp, params)
    
    @pyqtSlot(SharpenParams)
    def apply_sharpen(self, params: SharpenParams):
        """响应锐化滤波操作。"""
        self._create_and_execute_command(SharpenFilterOp, params)
    
    @pyqtSlot(MeanFilterParams)
    def apply_mean_filter(self, params: MeanFilterParams):
        """响应均值滤波操作。"""
        self._create_and_execute_command(MeanFilterOp, params)

    # --- 常规滤镜操作方法 ---
    
    @pyqtSlot(EmbossParams)
    def apply_emboss(self, params: EmbossParams):
        """响应浮雕滤镜操作。"""
        self._create_and_execute_command(EmbossFilterOp, params)
    
    @pyqtSlot(MosaicParams)
    def apply_mosaic(self, params: MosaicParams):
        """响应马赛克滤镜操作。"""
        self._create_and_execute_command(MosaicFilterOp, params)
    
    @pyqtSlot(OilPaintingParams)
    def apply_oil_painting(self, params: OilPaintingParams):
        """响应油画滤镜操作。"""
        self._create_and_execute_command(OilPaintingFilterOp, params)
    
    @pyqtSlot(SketchParams)
    def apply_sketch(self, params: SketchParams):
        """响应素描滤镜操作。"""
        self._create_and_execute_command(SketchFilterOp, params)
    
    @pyqtSlot(VintageParams)
    def apply_vintage(self, params: VintageParams):
        """响应怀旧滤镜操作。"""
        self._create_and_execute_command(VintageFilterOp, params)

    # --- 新增滤镜操作方法 ---
    
    @pyqtSlot(WatercolorParams)
    def apply_watercolor(self, params: WatercolorParams):
        """响应水彩画滤镜操作。"""
        self._create_and_execute_command(WatercolorFilterOp, params)
    
    @pyqtSlot(PencilSketchParams)
    def apply_pencil_sketch(self, params: PencilSketchParams):
        """响应铅笔画滤镜操作。"""
        self._create_and_execute_command(PencilSketchFilterOp, params)
    
    @pyqtSlot(CartoonParams)
    def apply_cartoon(self, params: CartoonParams):
        """响应卡通化滤镜操作。"""
        self._create_and_execute_command(CartoonFilterOp, params)
    
    @pyqtSlot(WarmToneParams)
    def apply_warm_tone(self, params: WarmToneParams):
        """响应暖色调滤镜操作。"""
        self._create_and_execute_command(WarmToneFilterOp, params)
    
    @pyqtSlot(CoolToneParams)
    def apply_cool_tone(self, params: CoolToneParams):
        """响应冷色调滤镜操作。"""
        self._create_and_execute_command(CoolToneFilterOp, params)
    
    @pyqtSlot(FilmGrainParams)
    def apply_film_grain(self, params: FilmGrainParams):
        """响应黑白胶片滤镜操作。"""
        self._create_and_execute_command(FilmGrainFilterOp, params)
    
    @pyqtSlot(NoiseParams)
    def apply_noise(self, params: NoiseParams):
        """响应噪点滤镜操作。"""
        self._create_and_execute_command(NoiseFilterOp, params)
    
    @pyqtSlot(FrostedGlassParams)
    def apply_frosted_glass(self, params: FrostedGlassParams):
        """响应磨砂玻璃滤镜操作。"""
        self._create_and_execute_command(FrostedGlassFilterOp, params)
    
    @pyqtSlot(FabricTextureParams)
    def apply_fabric_texture(self, params: FabricTextureParams):
        """响应织物纹理滤镜操作。"""
        self._create_and_execute_command(FabricTextureFilterOp, params)
    
    @pyqtSlot(VignetteParams)
    def apply_vignette(self, params: VignetteParams):
        """响应暗角滤镜操作。"""
        self._create_and_execute_command(VignetteFilterOp, params)

    # --- 图像放大操作方法 ---
    
    @pyqtSlot(ScaleUpParams)
    def apply_nearest_scale_up(self, params: ScaleUpParams):
        """响应最近邻放大操作。"""
        self._create_and_execute_command(NearestScaleUpOp, params)
    
    @pyqtSlot(ScaleUpParams)
    def apply_bilinear_scale_up(self, params: ScaleUpParams):
        """响应双线性放大操作。"""
        self._create_and_execute_command(BilinearScaleUpOp, params)
    
    @pyqtSlot(ScaleUpParams)
    def apply_bicubic_scale_up(self, params: ScaleUpParams):
        """响应双三次放大操作。"""
        self._create_and_execute_command(BicubicScaleUpOp, params)
    
    @pyqtSlot(ScaleUpParams)
    def apply_lanczos_scale_up(self, params: ScaleUpParams):
        """响应Lanczos放大操作。"""
        self._create_and_execute_command(LanczosScaleUpOp, params)
    
    @pyqtSlot(ScaleUpParams)
    def apply_edge_preserving_scale_up(self, params: ScaleUpParams):
        """响应边缘保持放大操作。"""
        self._create_and_execute_command(EdgePreservingScaleUpOp, params)

    # --- 图像缩小操作方法 ---
    
    @pyqtSlot(ScaleDownParams)
    def apply_nearest_scale_down(self, params: ScaleDownParams):
        """响应最近邻缩小操作。"""
        self._create_and_execute_command(NearestScaleDownOp, params)
    
    @pyqtSlot(ScaleDownParams)
    def apply_bilinear_scale_down(self, params: ScaleDownParams):
        """响应双线性缩小操作。"""
        self._create_and_execute_command(BilinearScaleDownOp, params)
    
    @pyqtSlot(ScaleDownParams)
    def apply_area_average_scale_down(self, params: ScaleDownParams):
        """响应区域平均缩小操作。"""
        self._create_and_execute_command(AreaAverageScaleDownOp, params)
    
    @pyqtSlot(ScaleDownParams)
    def apply_gaussian_scale_down(self, params: ScaleDownParams):
        """响应高斯缩小操作。"""
        self._create_and_execute_command(GaussianScaleDownOp, params)
    
    @pyqtSlot(ScaleDownParams)
    def apply_anti_alias_scale_down(self, params: ScaleDownParams):
        """响应抗锯齿缩小操作。"""
        self._create_and_execute_command(AntiAliasScaleDownOp, params)

    # --- 图像压缩操作方法 ---
    
    @pyqtSlot(CompressionParams)
    def apply_jpeg_compression(self, params: CompressionParams):
        """响应JPEG压缩操作。"""
        self._create_and_execute_command(JpegCompressionOp, params)
    
    @pyqtSlot(CompressionParams)
    def apply_png_compression(self, params: CompressionParams):
        """响应PNG压缩操作。"""
        self._create_and_execute_command(PngCompressionOp, params)
    
    @pyqtSlot(CompressionParams)
    def apply_webp_compression(self, params: CompressionParams):
        """响应WebP压缩操作。"""
        self._create_and_execute_command(WebpCompressionOp, params)
    
    @pyqtSlot(CompressionParams)
    def apply_color_quantization(self, params: CompressionParams):
        """响应颜色量化操作。"""
        self._create_and_execute_command(ColorQuantizationOp, params)
    
    @pyqtSlot(CompressionParams)
    def apply_lossy_optimization(self, params: CompressionParams):
        """响应智能优化操作。"""
        self._create_and_execute_command(LossyOptimizationOp, params)
        
    @pyqtSlot(str)
    def apply_simple_operation(self, op_id: str) -> None:
        """
        应用简单操作（无需参数的操作）
        
        Args:
            op_id: 操作标识符
        """
        # 操作ID到方法的映射表
        simple_operation_map = {
            'grayscale': self.apply_grayscale,
            'invert': self.apply_invert,
            'otsu_threshold': self.apply_otsu_threshold,
            'histogram_equalization': self.apply_histogram_equalization,
        }
        
        if op_id in simple_operation_map:
            simple_operation_map[op_id]()
            print(f"简单操作已应用: {op_id}")
        else:
            print(f"未知的简单操作ID: {op_id}")
        
    # --- 业务流程编排方法 ---
    
    def load_image_complete(self, image, file_path=None):
        """
        完整的图像加载流程 - 从StateManager移出的业务编排逻辑
        
        业务流程：重置状态 -> 加载图像 -> 创建代理 -> 通知更新
        """
        # 保存当前状态用于错误回滚
        original_state = self._capture_current_state()
        
        try:
            # 1. 重置所有处理状态
            self._state_manager.reset_all_processing_state()
            
            # 2. 设置图像数据
            self._state_manager.set_image_data(image, file_path)
            
            # 3. 创建并设置代理图像
            proxy_image = self._state_manager.proxy_workflow_manager.create_proxy_for_main_view(image)
            self._state_manager.image_repository.set_proxy_image(proxy_image)
            
            # 4. 最终通知
            self._state_manager.notify()
            
            logger.info(f"图像加载完成: {file_path}")
            
        except Exception as e:
            # 错误处理和状态回滚
            self._restore_state(original_state)
            logger.error(f"图像加载失败，已回滚状态: {e}")
            raise
    
    def clear_image_complete(self):
        """
        完整的图像清除流程
        
        业务流程：重置状态 -> 清除图像 -> 通知更新
        """
        try:
            # 1. 重置所有处理状态
            self._state_manager.reset_all_processing_state()
            
            # 2. 清除图像数据
            self._state_manager.clear_image_data()
            
            # 3. 最终通知
            self._state_manager.notify()
            
            logger.info("图像清除完成")
            
        except Exception as e:
            logger.error(f"图像清除失败: {e}")
            raise
    
    def load_image_proxy_complete(self, proxy_image, file_path=None):
        """
        完整的代理图像加载流程
        """
        # 保存当前状态用于错误回滚
        original_state = self._capture_current_state()
        
        try:
            # 1. 重置所有处理状态
            self._state_manager.reset_all_processing_state()
            
            # 2. 设置代理图像数据
            self._state_manager.set_proxy_image_data(proxy_image, file_path)
            
            # 3. 最终通知
            self._state_manager.notify()
            
            logger.info(f"代理图像加载完成: {file_path}")
            
        except Exception as e:
            # 错误处理
            self._restore_state(original_state)
            logger.error(f"代理图像加载失败: {e}")
            raise
    
    def _capture_current_state(self) -> Dict[str, Any]:
        """
        捕获当前状态用于错误回滚
        """
        return {
            'has_image': self._state_manager.is_image_loaded(),
            'file_path': self._state_manager.get_current_file_path(),
            'pipeline_count': len(self._state_manager.get_pipeline()),
            'preview_params': self._state_manager.get_preview_params()
        }
    
    def _restore_state(self, state: Dict[str, Any]):
        """
        恢复状态用于错误回滚
        """
        try:
            if not state['has_image']:
                # 如果原来没有图像，清除当前图像
                self._state_manager.clear_image_data()
            
            # 清除预览参数
            if state['preview_params']:
                self._state_manager.cancel_preview()
                
            logger.info("状态已回滚")
            
        except Exception as e:
            logger.error(f"状态回滚失败: {e}")
    
    def clear_all_effects(self) -> None:
        """
        清除所有效果（接口方法）
        """
        try:
            # 清空操作流水线
            self.pipeline_manager.clear_pipeline()
            logger.info("所有效果已清除")
        except Exception as e:
            logger.error(f"清除效果失败: {e}")
            self.show_error_message.emit(f"清除效果失败: {str(e)}")
    
    def apply_operation(self, operation) -> None:
        """
        应用操作对象（接口方法）
        
        Args:
            operation: 操作对象实例
        """
        try:
            command = AddOperationCommand(operation, self.pipeline_manager)
            self.pipeline_manager.execute_command(command)
            logger.info(f"操作已应用: {operation.__class__.__name__}")
        except Exception as e:
            logger.error(f"应用操作失败: {e}")
            self.show_error_message.emit(f"应用操作失败: {str(e)}")


# 单例模式已移除，使用依赖注入模式

# 全局访问器函数已删除
# 使用依赖注入方式获取ProcessingHandler实例
