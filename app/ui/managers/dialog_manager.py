"""
对话框管理器模块
"""
from typing import Dict, Optional, Tuple, cast, Callable, Type, Any, Union
from PyQt6.QtWidgets import QDialog, QMessageBox

# 移除核心层直接导入，通过桥接适配器访问
# from app.core.managers.state_manager import StateManager  # 已移除
from app.core.models.operation_params import BaseOperationParams  # 数据模型可以直接导入
from app.handlers.processing_handler import ProcessingHandler
from app.handlers.preset_handler import PresetHandler
from app.ui.dialogs.base_dialog import BaseOperationDialog
from app.ui.dialogs.brightness_contrast_dialog import BrightnessContrastDialog
from app.ui.dialogs.color_balance_dialog import ColorBalanceDialog
# 导入重构后的对话框
from app.ui.dialogs.curves.curves_dialog import CurvesDialog
from app.ui.dialogs.levels.levels_dialog import LevelsDialog
from app.ui.dialogs.hue_saturation_dialog import HueSaturationDialog
from app.ui.dialogs.threshold_dialog import ThresholdDialog
from app.ui.dialogs.apply_preset_dialog import ApplyPresetDialog

# 导入空间滤波对话框
from app.ui.dialogs.spatial_filtering import (
    GaussianBlurDialog,
    LaplacianEdgeDialog,
    SobelEdgeDialog,
    SharpenDialog,
    MeanFilterDialog
)

# 导入常规滤镜对话框
from app.ui.dialogs.regular_filters import (
    EmbossDialog,
    MosaicDialog,
    OilPaintingDialog,
    SketchDialog,
    VintageDialog,
    # 新增滤镜对话框
    WatercolorDialog,
    PencilSketchDialog,
    CartoonDialog,
    WarmToneDialog,
    CoolToneDialog,
    FilmGrainDialog,
    NoiseDialog,
    FrostedGlassDialog,
    FabricTextureDialog,
    VignetteDialog
)

# 导入图像变换对话框
from app.ui.dialogs.image_scaling import (
    ScaleUpDialog,
    ScaleDownDialog
)
from app.ui.dialogs.image_compression import CompressionDialog
from app.ui.dialogs.help_dialog import HelpDialog


class DialogManager:
    """
    负责创建、管理和显示所有参数调整对话框。
    """
    def __init__(self, 
                 app_controller,  # 通过AppController获取核心服务
                 processing_handler: ProcessingHandler,
                 preset_handler: PresetHandler,
                 parent=None):
        self.parent = parent  # 主窗口，作为对话框的父级
        self.app_controller = app_controller
        
        # 通过桥接适配器获取状态管理器
        core_adapter = self.app_controller.get_core_service_adapter()
        self.state_manager = core_adapter.get_state_manager() if core_adapter else None
        
        # 从 state_manager 获取子模块引用
        self.image_repository = self.state_manager.image_repository if self.state_manager else None
        self.pipeline_manager = self.state_manager.pipeline_manager if self.state_manager else None
        self.processing_handler = processing_handler
        self.preset_handler = preset_handler
        self._dialogs = {}  # 缓存对话框实例

        # 使用类型注解确保类型检查器理解这是一个字典
        self._dialog_map: Dict[str, Tuple[Type[BaseOperationDialog], Callable]] = {}
        
        # 只有当 processing_handler 不为 None 时才初始化 _dialog_map
        if self.processing_handler:
            self._dialog_map = {
                "brightness_contrast": (BrightnessContrastDialog, self.processing_handler.apply_brightness_contrast),
                "color_balance": (ColorBalanceDialog, self.processing_handler.apply_color_balance),
                "hue_saturation": (HueSaturationDialog, self.processing_handler.apply_hue_saturation),
                "curves": (CurvesDialog, self.processing_handler.apply_curves),
                "levels": (LevelsDialog, self.processing_handler.apply_levels),
                "threshold": (ThresholdDialog, self.processing_handler.apply_threshold),
                # 空间滤波对话框
                "gaussian_blur": (GaussianBlurDialog, self.processing_handler.apply_gaussian_blur),
                "laplacian_edge": (LaplacianEdgeDialog, self.processing_handler.apply_laplacian_edge),
                "sobel_edge": (SobelEdgeDialog, self.processing_handler.apply_sobel_edge),
                "sharpen": (SharpenDialog, self.processing_handler.apply_sharpen),
                "mean_filter": (MeanFilterDialog, self.processing_handler.apply_mean_filter),
                # 常规滤镜对话框
                "emboss": (EmbossDialog, self.processing_handler.apply_emboss),
                "mosaic": (MosaicDialog, self.processing_handler.apply_mosaic),
                "oil_painting": (OilPaintingDialog, self.processing_handler.apply_oil_painting),
                "sketch": (SketchDialog, self.processing_handler.apply_sketch),
                "vintage": (VintageDialog, self.processing_handler.apply_vintage),
                # 新增滤镜对话框
                "watercolor": (WatercolorDialog, self.processing_handler.apply_watercolor),
                "pencil_sketch": (PencilSketchDialog, self.processing_handler.apply_pencil_sketch),
                "cartoon": (CartoonDialog, self.processing_handler.apply_cartoon),
                "warm_tone": (WarmToneDialog, self.processing_handler.apply_warm_tone),
                "cool_tone": (CoolToneDialog, self.processing_handler.apply_cool_tone),
                "film_grain": (FilmGrainDialog, self.processing_handler.apply_film_grain),
                "noise": (NoiseDialog, self.processing_handler.apply_noise),
                "frosted_glass": (FrostedGlassDialog, self.processing_handler.apply_frosted_glass),
                "fabric_texture": (FabricTextureDialog, self.processing_handler.apply_fabric_texture),
                "vignette": (VignetteDialog, self.processing_handler.apply_vignette),
                # 图像放大对话框
                "nearest_scale_up": (ScaleUpDialog, self.processing_handler.apply_nearest_scale_up),
                "bilinear_scale_up": (ScaleUpDialog, self.processing_handler.apply_bilinear_scale_up),
                "bicubic_scale_up": (ScaleUpDialog, self.processing_handler.apply_bicubic_scale_up),
                "lanczos_scale_up": (ScaleUpDialog, self.processing_handler.apply_lanczos_scale_up),
                "edge_preserving_scale_up": (ScaleUpDialog, self.processing_handler.apply_edge_preserving_scale_up),
                # 图像缩小对话框
                "nearest_scale_down": (ScaleDownDialog, self.processing_handler.apply_nearest_scale_down),
                "bilinear_scale_down": (ScaleDownDialog, self.processing_handler.apply_bilinear_scale_down),
                "area_average_scale_down": (ScaleDownDialog, self.processing_handler.apply_area_average_scale_down),
                "gaussian_scale_down": (ScaleDownDialog, self.processing_handler.apply_gaussian_scale_down),
                "anti_alias_scale_down": (ScaleDownDialog, self.processing_handler.apply_anti_alias_scale_down),
                # 图像压缩对话框
                "jpeg_compression": (CompressionDialog, self.processing_handler.apply_jpeg_compression),
                "png_compression": (CompressionDialog, self.processing_handler.apply_png_compression),
                "webp_compression": (CompressionDialog, self.processing_handler.apply_webp_compression),
                "color_quantization": (CompressionDialog, self.processing_handler.apply_color_quantization),
                "lossy_optimization": (CompressionDialog, self.processing_handler.apply_lossy_optimization),
            }

    def show_dialog(self, op_id: str):
        """
        根据操作ID显示对应的对话框。
        如果对话框已存在，则激活它；否则创建新实例。
        """
        # 特殊处理 apply_preset 对话框
        if op_id == "apply_preset":
            self._show_apply_preset_dialog()
            return
            
        # 检查图像是否加载
        if not self.image_repository or not self.image_repository.is_image_loaded():
            QMessageBox.critical(self.parent, "错误", "请先打开一张图片。")
            return

        if op_id in self._dialogs and self._dialogs[op_id].isVisible():
            self._dialogs[op_id].activateWindow()
            return

        if op_id in self._dialog_map:
            DialogClass, apply_method = self._dialog_map[op_id]

            # 获取初始参数 (仍然以字典形式获取，向后兼容)
            initial_params = None
            if self.pipeline_manager and hasattr(self.pipeline_manager, 'get_operation_params'):
                params = self.pipeline_manager.get_operation_params(op_id)
                if params and isinstance(params, dict):
                    initial_params = params
            
            # 根据操作ID设置特定的算法参数
            initial_params = self._get_algorithm_specific_params(op_id, initial_params)
            
            # 实例化对话框
            # 只为简单对话框传递处理程序，复杂对话框（曲线和色阶）需要特殊处理
            if DialogClass in [CurvesDialog, LevelsDialog]:
                dialog = DialogClass(self.parent, initial_params)
            else:
                dialog = DialogClass(self.parent, initial_params, self.processing_handler)

            # 1. 连接实时预览信号（仅对需要预览的操作）
            if self.processing_handler and self._should_enable_preview(op_id):
                dialog.params_changed.connect(
                    lambda params, op_id=op_id: self.processing_handler.start_preview(op_id, params)
                )
                # 连接对话框取消信号
                dialog.rejected.connect(self.processing_handler.cancel_preview)

            # 缓存并显示对话框
            self._dialogs[op_id] = dialog
            
            # dialog.exec() 会阻塞，直到用户关闭对话框
            # 如果用户点击 "OK" (返回 True), 则应用最终参数
            if dialog.exec():
                # 3. 获取最终参数并应用操作
                final_params = dialog.get_final_parameters()
                if final_params and apply_method:
                    # 3.1 触发最终的高质量渲染（相当于模拟滑块释放）
                    if self.processing_handler:
                        self.processing_handler.on_slider_released()
                    # 3.2 清理预览状态
                    if self.processing_handler:
                        self.processing_handler.cancel_preview()
                    # 3.3 应用最终操作
                    # 调用在 _dialog_map 中定义的处理函数
                    # (e.g., self.processing_handler.apply_brightness_contrast)
                    apply_method(final_params)
            
            # 无论结果如何，执行后都从缓存中移除
            del self._dialogs[op_id]
        else:
            QMessageBox.critical(self.parent, "错误", f"未知的操作ID: {op_id}")
            
    def _show_apply_preset_dialog(self):
        """
        显示应用预设对话框。
        """
        if not self.preset_handler:
            QMessageBox.critical(self.parent, "错误", "预设处理器未初始化。")
            return
            
        # 创建对话框
        dialog = ApplyPresetDialog(self.parent, self.preset_handler)
        
        # 显示对话框并等待用户操作
        if dialog.exec():
            # 获取用户选择的预设和目标作业
            preset_name, apply_to_current, selected_jobs = dialog.get_selected_options()
            
            # 检查是否选择了有效的预设
            if preset_name and preset_name != "(无可用预设)":
                if apply_to_current:
                    # 应用预设到当前图像
                    success = self.preset_handler.load_preset(preset_name)
                    if success:
                        QMessageBox.information(self.parent, "成功", f"预设 '{preset_name}' 已应用到当前图像。")
                    else:
                        QMessageBox.critical(self.parent, "错误", f"应用预设 '{preset_name}' 失败。")
                else:
                    # 检查是否有选择的作业
                    if not selected_jobs:
                        QMessageBox.warning(self.parent, "警告", "未选择任何作业。")
                        return
                        
                    # 应用预设到选定的作业
                    self.preset_handler.apply_preset_to_named_jobs(preset_name, selected_jobs)
    
    def _get_algorithm_specific_params(self, op_id: str, existing_params: Optional[Dict] = None) -> Optional[Dict]:
        """根据操作ID获取算法特定的参数"""
        if existing_params is None:
            existing_params = {}
        
        # 图像放大算法映射
        scale_up_algorithms = {
            "nearest_scale_up": "nearest",
            "bilinear_scale_up": "bilinear", 
            "bicubic_scale_up": "bicubic",
            "lanczos_scale_up": "lanczos",
            "edge_preserving_scale_up": "edge_preserving"
        }
        
        # 图像缩小算法映射
        scale_down_algorithms = {
            "nearest_scale_down": "nearest",
            "bilinear_scale_down": "bilinear",
            "area_average_scale_down": "area_average", 
            "gaussian_scale_down": "gaussian",
            "anti_alias_scale_down": "anti_alias"
        }
        
        # 图像压缩算法映射
        compression_algorithms = {
            "jpeg_compression": "jpeg",
            "png_compression": "png",
            "webp_compression": "webp",
            "color_quantization": "color_quantization",
            "lossy_optimization": "lossy_optimization"
        }
        
        # 设置对应的算法
        if op_id in scale_up_algorithms:
            existing_params["algorithm"] = scale_up_algorithms[op_id]
        elif op_id in scale_down_algorithms:
            existing_params["algorithm"] = scale_down_algorithms[op_id]
        elif op_id in compression_algorithms:
            existing_params["algorithm"] = compression_algorithms[op_id]
        
        return existing_params
    
    def _should_enable_preview(self, op_id: str) -> bool:
        """判断操作是否需要启用实时预览"""
        # 缩放和压缩操作不需要实时预览
        no_preview_operations = {
            # 图像放大操作
            "nearest_scale_up", "bilinear_scale_up", "bicubic_scale_up", 
            "lanczos_scale_up", "edge_preserving_scale_up",
            # 图像缩小操作
            "nearest_scale_down", "bilinear_scale_down", "area_average_scale_down",
            "gaussian_scale_down", "anti_alias_scale_down",
            # 图像压缩操作
            "jpeg_compression", "png_compression", "webp_compression",
            "color_quantization", "lossy_optimization"
        }
        
        return op_id not in no_preview_operations 
    
    def show_help_dialog(self):
        """显示帮助对话框"""
        help_dialog = HelpDialog(self.parent)
        help_dialog.exec()