"""
分析数据处理器

专门负责数据处理协调：图像处理、分析计算、计算锁管理等。
职责单一：只处理"数据计算和处理流程"的逻辑。
"""

import logging
from typing import Optional, Dict, Any, Callable
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from app.core.models.analysis_tab_config import TabConfigManager, TabType

logger = logging.getLogger(__name__)


class AnalysisDataProcessor(QObject):
    """
    分析数据处理器
    
    专门负责数据处理协调，包括：
    - 图像处理协调
    - 分析计算管理
    - 计算锁管理
    - 数据流控制和分发
    """
    
    # 信号：分析完成，带有结果数据
    analysis_completed = pyqtSignal(dict)
    
    # 信号：图像信息更新完成
    image_info_updated = pyqtSignal(object, str, object)
    
    def __init__(self, state_manager, image_processor, analysis_calculator, parent=None):
        super().__init__(parent)
        
        # 数据处理相关组件
        self.state_manager = state_manager
        self.image_processor = image_processor
        self.analysis_calculator = analysis_calculator
        
        # 计算状态锁，防止重复计算
        self.is_calculating = False
        
        # 标签页配置管理器
        self.tab_config_manager = TabConfigManager()
        
        # 连接分析计算器的完成信号
        self.analysis_calculator.analysis_finished.connect(self.on_analysis_finished)
        
        logger.debug("分析数据处理器初始化完成")
    
    def process_immediate_update(self, tab_index: int):
        """
        立即处理指定标签页的数据更新
        
        Args:
            tab_index: 要更新的标签页索引
        """
        try:
            logger.debug(f"开始处理标签页 {tab_index} 的立即更新")
            
            # 基本检查
            if not self._can_process_update():
                return
            
            # 获取渲染后的图像数据
            image_data = self._get_rendered_image()
            if image_data is None:
                return
            
            # 设置计算锁
            self.is_calculating = True
            
            # 根据标签页类型处理不同的更新逻辑
            self._process_tab_specific_update(tab_index, image_data)
                
        except Exception as e:
            logger.error(f"处理标签页 {tab_index} 立即更新时发生错误: {e}")
            self.is_calculating = False
    
    def _can_process_update(self) -> bool:
        """
        检查是否可以处理更新
        
        Returns:
            bool: 是否可以处理更新
        """
        # 检查是否正在计算中
        if self.is_calculating:
            logger.debug("正在计算中，跳过更新")
            return False
            
        # 检查是否有图像加载
        if not self.state_manager.image_repository.is_image_loaded():
            logger.debug("没有图像加载，跳过更新")
            return False
        
        return True
    
    def _get_rendered_image(self):
        """
        获取当前渲染的图像
        
        Returns:
            渲染后的图像副本，如果获取失败则返回None
        """
        try:
            # 获取当前渲染的图像
            rendered_image = self.image_processor.render_pipeline(
                self.state_manager.image_repository.original_image,
                self.state_manager.pipeline_manager.operation_pipeline
            )
            
            return rendered_image.copy()
            
        except Exception as e:
            logger.error(f"获取渲染图像时发生错误: {e}")
            return None
    
    def _process_tab_specific_update(self, tab_index: int, image_data):
        """
        根据标签页类型处理特定的更新逻辑
        
        Args:
            tab_index: 标签页索引
            image_data: 图像数据
        """
        try:
            # 使用配置管理器获取标签页类型
            tab_type = self.tab_config_manager.get_tab_type(tab_index)
            
            if tab_type == TabType.INFO:
                # 信息面板是轻量级的，可以直接更新
                self._process_info_tab_update(image_data)
                
            elif tab_type == TabType.HISTOGRAM:
                # 直方图和波形图分析
                self.analysis_calculator.request_selective_analysis.emit(
                    image_data, "histogram_and_waveform"
                )
                
            elif tab_type == TabType.RGB_PARADE:
                # RGB Parade分析
                self.analysis_calculator.request_selective_analysis.emit(
                    image_data, "rgb_parade"
                )
                
            elif tab_type == TabType.HUE_SATURATION:
                # 色相饱和度分析
                self.analysis_calculator.request_selective_analysis.emit(
                    image_data, "hue_saturation"
                )
                
            elif tab_type == TabType.LUMA_WAVEFORM:
                # 亮度波形分析
                self.analysis_calculator.request_selective_analysis.emit(
                    image_data, "luma_waveform"
                )
                
            elif tab_type == TabType.LAB_CHROMATICITY:
                # Lab色度分析
                self.analysis_calculator.request_selective_analysis.emit(
                    image_data, "lab_analysis"
                )
                
            else:
                logger.warning(f"未知的标签页索引: {tab_index}")
                self.is_calculating = False
                
        except Exception as e:
            logger.error(f"处理标签页 {tab_index} 特定更新时发生错误: {e}")
            self.is_calculating = False
    
    def _process_info_tab_update(self, image_data):
        """
        处理信息标签页的更新
        
        Args:
            image_data: 图像数据
        """
        try:
            # 获取操作管道
            operations = self.state_manager.pipeline_manager.operation_pipeline
            
            # 获取文件路径
            file_path = self.state_manager.image_repository.get_current_file_path()
            
            # 发出图像信息更新信号
            self.image_info_updated.emit(image_data, file_path, operations)
            
            # 信息面板更新完成，立即释放锁
            self.is_calculating = False
            
        except Exception as e:
            logger.error(f"处理信息标签页更新时发生错误: {e}")
            self.is_calculating = False
    
    @pyqtSlot(dict)
    def on_analysis_finished(self, results: Dict[str, Any]):
        """
        处理来自分析计算器的结果
        这个方法会在主线程中被调用，因为它连接到Qt信号。
        
        Args:
            results: 分析结果字典
        """
        try:
            logger.debug("分析计算完成，发出结果信号")
            
            # 发出分析完成信号，让其他组件处理结果
            self.analysis_completed.emit(results)
            
            # 释放计算锁
            self.is_calculating = False
            
        except Exception as e:
            logger.error(f"处理分析完成结果时发生错误: {e}")
            self.is_calculating = False
    
    def get_processing_status(self) -> Dict[str, Any]:
        """
        获取当前处理状态信息
        
        Returns:
            dict: 包含处理状态的字典
        """
        try:
            status = {
                'is_calculating': self.is_calculating,
                'has_image_loaded': self.state_manager.image_repository.is_image_loaded(),
                'processor_type': type(self.image_processor).__name__,
                'calculator_type': type(self.analysis_calculator).__name__
            }
            
            return status
            
        except Exception as e:
            logger.error(f"获取处理状态时发生错误: {e}")
            return {'error': str(e)}
    
    def reset_calculating_state(self):
        """
        重置计算状态（用于错误恢复）
        """
        self.is_calculating = False
        logger.debug("计算状态已重置")
    
    def force_stop_calculation(self):
        """
        强制停止当前计算（如果支持的话）
        """
        try:
            # 重置计算状态
            self.is_calculating = False
            
            # 如果分析计算器支持停止操作，可以在此添加
            if hasattr(self.analysis_calculator, 'stop_calculation'):
                self.analysis_calculator.stop_calculation()
            
            logger.debug("已强制停止计算")
            
        except Exception as e:
            logger.error(f"强制停止计算时发生错误: {e}")
    
    def get_image_info(self) -> Optional[Dict[str, Any]]:
        """
        获取当前图像的基本信息
        
        Returns:
            dict: 图像信息字典，如果没有图像则返回None
        """
        try:
            if not self.state_manager.image_repository.is_image_loaded():
                return None
            
            original_image = self.state_manager.image_repository.original_image
            file_path = self.state_manager.image_repository.get_current_file_path()
            
            if original_image is not None:
                return {
                    'file_path': file_path,
                    'shape': original_image.shape,
                    'dtype': str(original_image.dtype),
                    'size_mb': original_image.nbytes / (1024 * 1024),
                    'has_operations': len(self.state_manager.pipeline_manager.operation_pipeline) > 0
                }
            
            return None
            
        except Exception as e:
            logger.error(f"获取图像信息时发生错误: {e}")
            return None