"""
新增滤镜对话框模块

包含10个新增常规滤镜的参数调整对话框
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout

from .regular_filter_dialog_base import RegularFilterDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.regular_filter_params import (
    WatercolorParams, PencilSketchParams, CartoonParams,
    WarmToneParams, CoolToneParams, FilmGrainParams,
    NoiseParams, FrostedGlassParams, FabricTextureParams, VignetteParams
)


class WatercolorDialog(RegularFilterDialog):
    """水彩画滤镜参数调整对话框"""
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("水彩画滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组"""
        # 流动强度控制组
        flow_group, self.flow_slider, self.flow_label = self._create_slider_group(
            "流动强度", 0, 100, 50
        )
        main_layout.addWidget(flow_group)
        
        # 渗透程度控制组
        penetration_group, self.penetration_slider, self.penetration_label = self._create_slider_group(
            "渗透程度", 0, 100, 30
        )
        main_layout.addWidget(penetration_group)
        
        # 连接信号
        self.flow_slider.valueChanged.connect(self._update_flow_label)
        self.flow_slider.valueChanged.connect(self._emit_params_changed)
        self.penetration_slider.valueChanged.connect(self._update_penetration_label)
        self.penetration_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        """连接滑块预览事件"""
        if self.processing_handler is not None:
            self.flow_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.flow_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            self.penetration_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.penetration_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_flow_label(self):
        value = self.flow_slider.value()
        self.flow_label.setText(str(value))
    
    @pyqtSlot()
    def _update_penetration_label(self):
        value = self.penetration_slider.value()
        self.penetration_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        params = WatercolorParams(
            flow_intensity=self.flow_slider.value() / 100.0,
            penetration=self.penetration_slider.value() / 100.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        self.flow_slider.setValue(50)
        self.penetration_slider.setValue(30)
    
    def get_final_parameters(self) -> WatercolorParams:
        return WatercolorParams(
            flow_intensity=self.flow_slider.value() / 100.0,
            penetration=self.penetration_slider.value() / 100.0
        )
    
    def set_initial_parameters(self, params: Dict):
        if params is None:
            return
        flow_intensity = int(params.get('flow_intensity', 0.5) * 100)
        penetration = int(params.get('penetration', 0.3) * 100)
        self.flow_slider.setValue(flow_intensity)
        self.penetration_slider.setValue(penetration)


class PencilSketchDialog(RegularFilterDialog):
    """铅笔画滤镜参数调整对话框"""
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("铅笔画滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        # 线条粗细控制组
        thickness_group, self.thickness_slider, self.thickness_label = self._create_slider_group(
            "线条粗细", 10, 300, 100
        )
        main_layout.addWidget(thickness_group)
        
        # 阴影强度控制组
        shadow_group, self.shadow_slider, self.shadow_label = self._create_slider_group(
            "阴影强度", 0, 100, 50
        )
        main_layout.addWidget(shadow_group)
        
        # 连接信号
        self.thickness_slider.valueChanged.connect(self._update_thickness_label)
        self.thickness_slider.valueChanged.connect(self._emit_params_changed)
        self.shadow_slider.valueChanged.connect(self._update_shadow_label)
        self.shadow_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        if self.processing_handler is not None:
            self.thickness_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.thickness_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            self.shadow_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.shadow_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_thickness_label(self):
        value = self.thickness_slider.value() / 100.0
        self.thickness_label.setText(f"{value:.1f}")
    
    @pyqtSlot()
    def _update_shadow_label(self):
        value = self.shadow_slider.value()
        self.shadow_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        params = PencilSketchParams(
            line_thickness=self.thickness_slider.value() / 100.0,
            shadow_intensity=self.shadow_slider.value() / 100.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        self.thickness_slider.setValue(100)
        self.shadow_slider.setValue(50)
    
    def get_final_parameters(self) -> PencilSketchParams:
        return PencilSketchParams(
            line_thickness=self.thickness_slider.value() / 100.0,
            shadow_intensity=self.shadow_slider.value() / 100.0
        )
    
    def set_initial_parameters(self, params: Dict):
        if params is None:
            return
        thickness = int(params.get('line_thickness', 1.0) * 100)
        shadow = int(params.get('shadow_intensity', 0.5) * 100)
        self.thickness_slider.setValue(thickness)
        self.shadow_slider.setValue(shadow)


class CartoonDialog(RegularFilterDialog):
    """卡通化滤镜参数调整对话框"""
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("卡通化滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        # 色彩简化控制组
        simplification_group, self.simplification_slider, self.simplification_label = self._create_slider_group(
            "色彩简化程度", 0, 100, 70
        )
        main_layout.addWidget(simplification_group)
        
        # 边缘增强控制组
        edge_group, self.edge_slider, self.edge_label = self._create_slider_group(
            "边缘增强", 0, 100, 80
        )
        main_layout.addWidget(edge_group)
        
        # 连接信号
        self.simplification_slider.valueChanged.connect(self._update_simplification_label)
        self.simplification_slider.valueChanged.connect(self._emit_params_changed)
        self.edge_slider.valueChanged.connect(self._update_edge_label)
        self.edge_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        if self.processing_handler is not None:
            self.simplification_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.simplification_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            self.edge_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.edge_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_simplification_label(self):
        value = self.simplification_slider.value()
        self.simplification_label.setText(str(value))
    
    @pyqtSlot()
    def _update_edge_label(self):
        value = self.edge_slider.value()
        self.edge_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        params = CartoonParams(
            color_simplification=self.simplification_slider.value() / 100.0,
            edge_enhancement=self.edge_slider.value() / 100.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        self.simplification_slider.setValue(70)
        self.edge_slider.setValue(80)
    
    def get_final_parameters(self) -> CartoonParams:
        return CartoonParams(
            color_simplification=self.simplification_slider.value() / 100.0,
            edge_enhancement=self.edge_slider.value() / 100.0
        )
    
    def set_initial_parameters(self, params: Dict):
        if params is None:
            return
        simplification = int(params.get('color_simplification', 0.7) * 100)
        edge = int(params.get('edge_enhancement', 0.8) * 100)
        self.simplification_slider.setValue(simplification)
        self.edge_slider.setValue(edge)


class WarmToneDialog(RegularFilterDialog):
    """暖色调滤镜参数调整对话框"""
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("暖色调滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        # 暖色强度控制组
        warmth_group, self.warmth_slider, self.warmth_label = self._create_slider_group(
            "暖色强度", 0, 100, 50
        )
        main_layout.addWidget(warmth_group)
        
        # 色温偏移控制组
        temp_group, self.temp_slider, self.temp_label = self._create_slider_group(
            "色温偏移", 0, 100, 30
        )
        main_layout.addWidget(temp_group)
        
        # 连接信号
        self.warmth_slider.valueChanged.connect(self._update_warmth_label)
        self.warmth_slider.valueChanged.connect(self._emit_params_changed)
        self.temp_slider.valueChanged.connect(self._update_temp_label)
        self.temp_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        if self.processing_handler is not None:
            self.warmth_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.warmth_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            self.temp_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.temp_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_warmth_label(self):
        value = self.warmth_slider.value()
        self.warmth_label.setText(str(value))
    
    @pyqtSlot()
    def _update_temp_label(self):
        value = self.temp_slider.value()
        self.temp_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        params = WarmToneParams(
            warmth_intensity=self.warmth_slider.value() / 100.0,
            temperature_shift=self.temp_slider.value() / 100.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        self.warmth_slider.setValue(50)
        self.temp_slider.setValue(30)
    
    def get_final_parameters(self) -> WarmToneParams:
        return WarmToneParams(
            warmth_intensity=self.warmth_slider.value() / 100.0,
            temperature_shift=self.temp_slider.value() / 100.0
        )
    
    def set_initial_parameters(self, params: Dict):
        if params is None:
            return
        warmth = int(params.get('warmth_intensity', 0.5) * 100)
        temp = int(params.get('temperature_shift', 0.3) * 100)
        self.warmth_slider.setValue(warmth)
        self.temp_slider.setValue(temp)


class CoolToneDialog(RegularFilterDialog):
    """冷色调滤镜参数调整对话框"""
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("冷色调滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        # 冷色强度控制组
        coolness_group, self.coolness_slider, self.coolness_label = self._create_slider_group(
            "冷色强度", 0, 100, 50
        )
        main_layout.addWidget(coolness_group)
        
        # 色温偏移控制组
        temp_group, self.temp_slider, self.temp_label = self._create_slider_group(
            "色温偏移", 0, 100, 30
        )
        main_layout.addWidget(temp_group)
        
        # 连接信号
        self.coolness_slider.valueChanged.connect(self._update_coolness_label)
        self.coolness_slider.valueChanged.connect(self._emit_params_changed)
        self.temp_slider.valueChanged.connect(self._update_temp_label)
        self.temp_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        if self.processing_handler is not None:
            self.coolness_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.coolness_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            self.temp_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.temp_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_coolness_label(self):
        value = self.coolness_slider.value()
        self.coolness_label.setText(str(value))
    
    @pyqtSlot()
    def _update_temp_label(self):
        value = self.temp_slider.value()
        self.temp_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        params = CoolToneParams(
            coolness_intensity=self.coolness_slider.value() / 100.0,
            temperature_shift=self.temp_slider.value() / 100.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        self.coolness_slider.setValue(50)
        self.temp_slider.setValue(30)
    
    def get_final_parameters(self) -> CoolToneParams:
        return CoolToneParams(
            coolness_intensity=self.coolness_slider.value() / 100.0,
            temperature_shift=self.temp_slider.value() / 100.0
        )
    
    def set_initial_parameters(self, params: Dict):
        if params is None:
            return
        coolness = int(params.get('coolness_intensity', 0.5) * 100)
        temp = int(params.get('temperature_shift', 0.3) * 100)
        self.coolness_slider.setValue(coolness)
        self.temp_slider.setValue(temp)


class FilmGrainDialog(RegularFilterDialog):
    """黑白胶片滤镜参数调整对话框"""
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("黑白胶片滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        # 颗粒强度控制组
        grain_group, self.grain_slider, self.grain_label = self._create_slider_group(
            "颗粒强度", 0, 100, 50
        )
        main_layout.addWidget(grain_group)
        
        # 对比度增强控制组
        contrast_group, self.contrast_slider, self.contrast_label = self._create_slider_group(
            "对比度增强", 0, 100, 30
        )
        main_layout.addWidget(contrast_group)
        
        # 连接信号
        self.grain_slider.valueChanged.connect(self._update_grain_label)
        self.grain_slider.valueChanged.connect(self._emit_params_changed)
        self.contrast_slider.valueChanged.connect(self._update_contrast_label)
        self.contrast_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        if self.processing_handler is not None:
            self.grain_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.grain_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            self.contrast_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.contrast_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_grain_label(self):
        value = self.grain_slider.value()
        self.grain_label.setText(str(value))
    
    @pyqtSlot()
    def _update_contrast_label(self):
        value = self.contrast_slider.value()
        self.contrast_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        params = FilmGrainParams(
            grain_intensity=self.grain_slider.value() / 100.0,
            contrast_boost=self.contrast_slider.value() / 100.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        self.grain_slider.setValue(50)
        self.contrast_slider.setValue(30)
    
    def get_final_parameters(self) -> FilmGrainParams:
        return FilmGrainParams(
            grain_intensity=self.grain_slider.value() / 100.0,
            contrast_boost=self.contrast_slider.value() / 100.0
        )
    
    def set_initial_parameters(self, params: Dict):
        if params is None:
            return
        grain = int(params.get('grain_intensity', 0.5) * 100)
        contrast = int(params.get('contrast_boost', 0.3) * 100)
        self.grain_slider.setValue(grain)
        self.contrast_slider.setValue(contrast)


class NoiseDialog(RegularFilterDialog):
    """噪点滤镜参数调整对话框"""
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("噪点滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        # 噪点类型控制组
        type_group, self.type_combo = self._create_combo_group(
            "噪点类型", ["高斯噪声", "椒盐噪声", "泊松噪声"], 0
        )
        main_layout.addWidget(type_group)
        
        # 噪点强度控制组
        intensity_group, self.intensity_slider, self.intensity_label = self._create_slider_group(
            "噪点强度", 0, 100, 10
        )
        main_layout.addWidget(intensity_group)
        
        # 连接信号
        self.type_combo.currentIndexChanged.connect(self._emit_params_changed)
        self.intensity_slider.valueChanged.connect(self._update_intensity_label)
        self.intensity_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        if self.processing_handler is not None:
            self.intensity_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.intensity_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_intensity_label(self):
        value = self.intensity_slider.value()
        self.intensity_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        params = NoiseParams(
            noise_type=self.type_combo.currentIndex(),
            noise_intensity=self.intensity_slider.value() / 100.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        self.type_combo.setCurrentIndex(0)
        self.intensity_slider.setValue(10)
    
    def get_final_parameters(self) -> NoiseParams:
        return NoiseParams(
            noise_type=self.type_combo.currentIndex(),
            noise_intensity=self.intensity_slider.value() / 100.0
        )
    
    def set_initial_parameters(self, params: Dict):
        if params is None:
            return
        noise_type = params.get('noise_type', 0)
        intensity = int(params.get('noise_intensity', 0.1) * 100)
        self.type_combo.setCurrentIndex(noise_type)
        self.intensity_slider.setValue(intensity)


class FrostedGlassDialog(RegularFilterDialog):
    """磨砂玻璃滤镜参数调整对话框"""
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("磨砂玻璃滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        # 模糊程度控制组
        blur_group, self.blur_slider, self.blur_label = self._create_slider_group(
            "模糊程度", 0, 100, 50
        )
        main_layout.addWidget(blur_group)
        
        # 扭曲强度控制组
        distortion_group, self.distortion_slider, self.distortion_label = self._create_slider_group(
            "扭曲强度", 0, 100, 30
        )
        main_layout.addWidget(distortion_group)
        
        # 连接信号
        self.blur_slider.valueChanged.connect(self._update_blur_label)
        self.blur_slider.valueChanged.connect(self._emit_params_changed)
        self.distortion_slider.valueChanged.connect(self._update_distortion_label)
        self.distortion_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        if self.processing_handler is not None:
            self.blur_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.blur_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            self.distortion_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.distortion_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_blur_label(self):
        value = self.blur_slider.value()
        self.blur_label.setText(str(value))
    
    @pyqtSlot()
    def _update_distortion_label(self):
        value = self.distortion_slider.value()
        self.distortion_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        params = FrostedGlassParams(
            blur_amount=self.blur_slider.value() / 100.0,
            distortion_strength=self.distortion_slider.value() / 100.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        self.blur_slider.setValue(50)
        self.distortion_slider.setValue(30)
    
    def get_final_parameters(self) -> FrostedGlassParams:
        return FrostedGlassParams(
            blur_amount=self.blur_slider.value() / 100.0,
            distortion_strength=self.distortion_slider.value() / 100.0
        )
    
    def set_initial_parameters(self, params: Dict):
        if params is None:
            return
        blur = int(params.get('blur_amount', 0.5) * 100)
        distortion = int(params.get('distortion_strength', 0.3) * 100)
        self.blur_slider.setValue(blur)
        self.distortion_slider.setValue(distortion)


class FabricTextureDialog(RegularFilterDialog):
    """织物纹理滤镜参数调整对话框"""
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("织物纹理滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        # 织物类型控制组
        type_group, self.type_combo = self._create_combo_group(
            "织物类型", ["帆布", "丝绸", "麻布"], 0
        )
        main_layout.addWidget(type_group)
        
        # 纹理强度控制组
        intensity_group, self.intensity_slider, self.intensity_label = self._create_slider_group(
            "纹理强度", 0, 100, 50
        )
        main_layout.addWidget(intensity_group)
        
        # 连接信号
        self.type_combo.currentIndexChanged.connect(self._emit_params_changed)
        self.intensity_slider.valueChanged.connect(self._update_intensity_label)
        self.intensity_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        if self.processing_handler is not None:
            self.intensity_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.intensity_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_intensity_label(self):
        value = self.intensity_slider.value()
        self.intensity_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        params = FabricTextureParams(
            fabric_type=self.type_combo.currentIndex(),
            texture_intensity=self.intensity_slider.value() / 100.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        self.type_combo.setCurrentIndex(0)
        self.intensity_slider.setValue(50)
    
    def get_final_parameters(self) -> FabricTextureParams:
        return FabricTextureParams(
            fabric_type=self.type_combo.currentIndex(),
            texture_intensity=self.intensity_slider.value() / 100.0
        )
    
    def set_initial_parameters(self, params: Dict):
        if params is None:
            return
        fabric_type = params.get('fabric_type', 0)
        intensity = int(params.get('texture_intensity', 0.5) * 100)
        self.type_combo.setCurrentIndex(fabric_type)
        self.intensity_slider.setValue(intensity)


class VignetteDialog(RegularFilterDialog):
    """暗角滤镜参数调整对话框"""
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("暗角滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        # 暗角强度控制组
        strength_group, self.strength_slider, self.strength_label = self._create_slider_group(
            "暗角强度", 0, 100, 50
        )
        main_layout.addWidget(strength_group)
        
        # 渐变范围控制组
        range_group, self.range_slider, self.range_label = self._create_slider_group(
            "渐变范围", 10, 100, 70
        )
        main_layout.addWidget(range_group)
        
        # 连接信号
        self.strength_slider.valueChanged.connect(self._update_strength_label)
        self.strength_slider.valueChanged.connect(self._emit_params_changed)
        self.range_slider.valueChanged.connect(self._update_range_label)
        self.range_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        if self.processing_handler is not None:
            self.strength_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.strength_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            self.range_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.range_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_strength_label(self):
        value = self.strength_slider.value()
        self.strength_label.setText(str(value))
    
    @pyqtSlot()
    def _update_range_label(self):
        value = self.range_slider.value()
        self.range_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        params = VignetteParams(
            vignette_strength=self.strength_slider.value() / 100.0,
            gradient_range=self.range_slider.value() / 100.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        self.strength_slider.setValue(50)
        self.range_slider.setValue(70)
    
    def get_final_parameters(self) -> VignetteParams:
        return VignetteParams(
            vignette_strength=self.strength_slider.value() / 100.0,
            gradient_range=self.range_slider.value() / 100.0
        )
    
    def set_initial_parameters(self, params: Dict):
        if params is None:
            return
        strength = int(params.get('vignette_strength', 0.5) * 100)
        range_val = int(params.get('gradient_range', 0.7) * 100)
        self.strength_slider.setValue(strength)
        self.range_slider.setValue(range_val)