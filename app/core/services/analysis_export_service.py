"""
数据分析导出服务
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

from app.core.models.analysis_export_config import AnalysisExportConfig, AnalysisExportType
from app.utils.matplotlib_export_utils import MatplotlibExportUtils
from app.utils.analysis_data_converter import AnalysisDataConverter
from app.utils.matplotlib_chart_styles import MatplotlibChartStyles
from app.utils.filename_sanitizer import FilenameSanitizer
from app.utils.chinese_encoding_handler import ChineseEncodingHandler
from app.utils.chinese_encoding_handler import ChineseEncodingHandler
from app.utils.filename_sanitizer import FilenameSanitizer

logger = logging.getLogger(__name__)


class AnalysisExportService:
    """数据分析导出服务"""
    
    def __init__(self, state_manager, image_processor, analysis_calculator, batch_coordinator=None):
        self.state_manager = state_manager
        self.image_processor = image_processor
        self.analysis_calculator = analysis_calculator
        self.batch_coordinator = batch_coordinator
        
    def export_analysis_data(self, config: AnalysisExportConfig, 
                           progress_callback: Optional[Callable[[int, int, str], None]] = None) -> bool:
        """
        导出分析数据
        
        Args:
            config: 导出配置
            progress_callback: 进度回调函数(current, total, message)
            
        Returns:
            bool: 是否导出成功
        """
        try:
            # 创建导出目录结构
            export_root = self._create_export_directory_structure(config.export_path)
            
            # 获取选中作业的图像数据
            jobs_data = self._get_selected_jobs_with_images(config.selected_job_ids)
            
            if not jobs_data:
                logger.warning("没有找到可导出的作业和图像")
                return False
            
            # 计算总任务数
            total_images = sum(len(images) for images in jobs_data.values())
            current_count = 0
            
            # 为每个作业导出数据
            for job_name, images in jobs_data.items():
                # 使用新的文件名安全处理器
                safe_job_name = FilenameSanitizer.sanitize_filename(job_name)
                job_dir = os.path.join(export_root, safe_job_name)
                
                # 确保目录创建成功，支持中文路径
                try:
                    os.makedirs(job_dir, exist_ok=True)
                except Exception as e:
                    logger.error(f"创建作业目录失败: {e}")
                    # 尝试使用更安全的目录名
                    safe_job_name = FilenameSanitizer.generate_safe_export_name(job_name, "")
                    job_dir = os.path.join(export_root, safe_job_name)
                    os.makedirs(job_dir, exist_ok=True)
                
                for image_path in images:
                    if progress_callback:
                        progress_callback(current_count, total_images, f"处理: {os.path.basename(image_path)}")
                    
                    # 检查图像路径是否存在
                    if not os.path.exists(image_path):
                        # 如果路径不存在，尝试从当前状态管理器获取图像
                        if self.state_manager.image_repository.is_image_loaded():
                            original_image = self.state_manager.image_repository.original_image
                            if original_image is not None:
                                success = self._export_image_analysis_from_array(
                                    original_image, image_path, job_dir, config
                                )
                            else:
                                success = False
                        else:
                            success = False
                    else:
                        success = self._export_image_analysis(image_path, job_dir, config)
                    
                    if not success:
                        logger.warning(f"导出图像分析失败: {image_path}")
                    
                    current_count += 1
            
            if progress_callback:
                progress_callback(total_images, total_images, "导出完成")
            
            logger.info(f"分析数据导出完成，共处理 {total_images} 个图像")
            return True
            
        except Exception as e:
            logger.error(f"导出分析数据失败: {e}")
            return False
    
    def _create_export_directory_structure(self, base_path: str) -> str:
        """创建导出目录结构"""
        try:
            # 标准化基础路径
            normalized_base = ChineseEncodingHandler.normalize_chinese_path(base_path)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir_name = f"数据分析_{timestamp}"
            
            # 确保导出目录名安全
            safe_export_name = FilenameSanitizer.sanitize_filename(export_dir_name)
            export_root = os.path.join(normalized_base, safe_export_name)
            
            # 处理目录名冲突
            if os.path.exists(export_root):
                safe_export_name = FilenameSanitizer.handle_filename_conflicts(
                    normalized_base, safe_export_name
                )
                export_root = os.path.join(normalized_base, safe_export_name)
            
            os.makedirs(export_root, exist_ok=True)
            logger.info(f"创建导出目录: {export_root}")
            
            return export_root
            
        except Exception as e:
            logger.error(f"创建导出目录结构失败: {e}")
            # 回退到临时目录
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="analysis_export_")
            logger.warning(f"使用临时目录: {temp_dir}")
            return temp_dir
    
    def _get_all_jobs_with_images(self) -> Dict[str, List[str]]:
        """获取所有作业及其图像列表"""
        jobs_data = {}
        
        # 尝试从批处理系统获取作业
        if self.batch_coordinator:
            try:
                jobs = self.batch_coordinator.get_all_jobs()
                for job in jobs:
                    if job.source_paths:  # 只包含有图像的作业
                        jobs_data[job.name] = job.source_paths
            except Exception as e:
                logger.warning(f"获取批处理作业数据失败: {e}")
                
        # 如果没有批处理作业，尝试获取当前图像
        if not jobs_data:
            current_file_path = self.state_manager.get_current_file_path()
            if current_file_path:
                jobs_data["当前作业"] = [current_file_path]
                
        return jobs_data
        
    def _get_selected_jobs_with_images(self, selected_job_ids: List[str]) -> Dict[str, List[str]]:
        """获取选中作业及其图像列表"""
        jobs_data = {}
        
        if self.batch_coordinator and selected_job_ids:
            try:
                all_jobs = self.batch_coordinator.get_all_jobs()
                job_dict = {job.job_id: job for job in all_jobs}
                
                for job_id in selected_job_ids:
                    if job_id in job_dict:
                        job = job_dict[job_id]
                        if job.source_paths:  # 只包含有图像的作业
                            jobs_data[job.name] = job.source_paths
            except Exception as e:
                logger.warning(f"获取选中作业数据失败: {e}")
                
        return jobs_data
        

    
    def _export_image_analysis(self, image_path: str, output_dir: str, 
                             config: AnalysisExportConfig) -> bool:
        """
        导出单个图像的分析数据
        
        Args:
            image_path: 图像路径
            output_dir: 输出目录
            config: 导出配置
            
        Returns:
            bool: 是否导出成功
        """
        try:
            # 使用文件服务加载图像以支持中文路径
            from app.layers.infrastructure.filesystem.file_service import FileService
            file_service = FileService()
            
            image, actual_path = file_service.load_image(image_path)
            if image is None:
                logger.error(f"无法加载图像: {image_path}")
                return False
            
            # 转换RGB到BGR（因为分析计算器可能需要BGR格式）
            if len(image.shape) == 3 and image.shape[2] == 3:
                import cv2
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # 生成分析数据
            analysis_data = self._generate_analysis_for_image(image, config.selected_analysis_types)
            
            # 获取图像文件名（不含扩展名）
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            
            # 导出图表和数据
            success = True
            for analysis_type in config.selected_analysis_types:
                type_name = self._get_analysis_type_name(analysis_type)
                
                # 导出图表
                chart_success = self._export_chart_image(
                    analysis_data, analysis_type, output_dir, image_name, config
                )
                success = success and chart_success
                
                # 导出原始数据
                if config.include_raw_data:
                    data_success = self._export_raw_data(
                        analysis_data, analysis_type, output_dir, image_name, config
                    )
                    success = success and data_success
            
            return success
            
        except Exception as e:
            logger.error(f"导出图像分析失败: {e}")
            return False
    
    def _export_image_analysis_from_array(self, image_array, image_path: str, output_dir: str, 
                                        config: AnalysisExportConfig) -> bool:
        """
        从图像数组导出分析数据
        
        Args:
            image_array: 图像数组
            image_path: 图像路径（用于命名）
            output_dir: 输出目录
            config: 导出配置
            
        Returns:
            bool: 是否导出成功
        """
        try:
            # 生成分析数据
            analysis_data = self._generate_analysis_for_image(image_array, config.selected_analysis_types)
            
            # 获取图像文件名（不含扩展名）
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            
            # 导出数据
            success = True
            for analysis_type in config.selected_analysis_types:
                # 导出图表
                chart_success = self._export_chart_image(
                    analysis_data, analysis_type, output_dir, image_name, config
                )
                success = success and chart_success
                
                # 导出原始数据
                if config.include_raw_data:
                    data_success = self._export_raw_data(
                        analysis_data, analysis_type, output_dir, image_name, config
                    )
                    success = success and data_success
            
            return success
            
        except Exception as e:
            logger.error(f"从数组导出图像分析失败: {e}")
            return False
    
    def _generate_analysis_for_image(self, image, analysis_types: List[AnalysisExportType]) -> Dict[str, Any]:
        """为图像生成分析数据"""
        from app.core.engines.image_analysis_engine import ImageAnalysisEngine
        
        results = {}
        
        # 计算色彩直方图
        if AnalysisExportType.COLOR_HISTOGRAM in analysis_types:
            results['histogram'] = ImageAnalysisEngine.calculate_histogram(image)
        
        # 计算RGB波形
        if AnalysisExportType.RGB_PARADE in analysis_types:
            results['rgb_parade'] = ImageAnalysisEngine.get_rgb_parade_efficient(image)
        
        # 计算亮度波形（使用RGB波形数据）
        if AnalysisExportType.LUMA_WAVEFORM in analysis_types:
            if 'rgb_parade' not in results:
                results['rgb_parade'] = ImageAnalysisEngine.get_rgb_parade_efficient(image)
            # 亮度波形使用RGB波形的亮度分量
            results['luma_waveform'] = results['rgb_parade']
        
        # 计算色相和饱和度（如果需要任一个都要计算）
        need_hue_sat = (AnalysisExportType.HUE_HISTOGRAM in analysis_types or 
                       AnalysisExportType.SATURATION_HISTOGRAM in analysis_types)
        if need_hue_sat:
            hue_hist, sat_hist = ImageAnalysisEngine.get_hue_saturation_histograms(image)
            if AnalysisExportType.HUE_HISTOGRAM in analysis_types:
                results['hue_histogram'] = hue_hist
            if AnalysisExportType.SATURATION_HISTOGRAM in analysis_types:
                results['sat_histogram'] = sat_hist
        
        # 计算Lab分析
        if AnalysisExportType.LAB_CHROMATICITY in analysis_types:
            chromaticity_data, lab_3d_data = ImageAnalysisEngine.calculate_lab_analysis(image)
            results['lab_chromaticity'] = chromaticity_data
            results['lab_3d'] = lab_3d_data
        
        return results
    
    def _export_raw_data(self, analysis_data: Dict[str, Any], analysis_type: AnalysisExportType,
                        output_dir: str, image_name: str, config: AnalysisExportConfig) -> bool:
        """导出原始数据"""
        try:
            type_name = self._get_analysis_type_name(analysis_type)
            data_ext = AnalysisDataConverter.get_file_extension(config.data_format)
            
            # 使用安全的文件名生成
            safe_image_name = FilenameSanitizer.sanitize_filename(image_name)
            data_filename = FilenameSanitizer.generate_safe_export_name(
                f"{safe_image_name}_{type_name}", "数据"
            ) + data_ext
            
            # 处理文件名冲突
            data_filename = FilenameSanitizer.handle_filename_conflicts(output_dir, data_filename)
            data_path = os.path.join(output_dir, data_filename)
            
            # 提取对应类型的数据
            type_data = self._extract_analysis_type_data(analysis_data, analysis_type)
            
            return AnalysisDataConverter.export_data(type_data, data_path, config.data_format)
            
        except Exception as e:
            logger.error(f"导出原始数据失败: {e}")
            return False
    
    def _extract_analysis_type_data(self, analysis_data: Dict[str, Any], 
                                  analysis_type: AnalysisExportType) -> Dict[str, Any]:
        """提取特定类型的分析数据"""
        if analysis_type == AnalysisExportType.COLOR_HISTOGRAM:
            return {'histogram': analysis_data.get('histogram', [])}
        elif analysis_type == AnalysisExportType.LUMA_WAVEFORM:
            return {'luma_waveform': analysis_data.get('luma_waveform', [])}
        elif analysis_type == AnalysisExportType.RGB_PARADE:
            return {'rgb_parade': analysis_data.get('rgb_parade', [])}
        elif analysis_type == AnalysisExportType.HUE_HISTOGRAM:
            return {'hue_histogram': analysis_data.get('hue_histogram', [])}
        elif analysis_type == AnalysisExportType.SATURATION_HISTOGRAM:
            return {'sat_histogram': analysis_data.get('sat_histogram', [])}
        elif analysis_type == AnalysisExportType.LAB_CHROMATICITY:
            return {'lab_chromaticity': analysis_data.get('lab_chromaticity', {})}
        else:
            return {}
    
    def _get_analysis_type_name(self, analysis_type: AnalysisExportType) -> str:
        """获取分析类型的中文名称"""
        name_map = {
            AnalysisExportType.COLOR_HISTOGRAM: "色彩直方图",
            AnalysisExportType.LUMA_WAVEFORM: "亮度波形图",
            AnalysisExportType.RGB_PARADE: "RGB波形",
            AnalysisExportType.HUE_HISTOGRAM: "色相直方图",
            AnalysisExportType.SATURATION_HISTOGRAM: "饱和度直方图",
            AnalysisExportType.LAB_CHROMATICITY: "Lab色度"
        }
        return name_map.get(analysis_type, "未知")
    

    
    def _export_chart_image(self, analysis_data: Dict[str, Any], analysis_type: AnalysisExportType,
                           output_dir: str, image_name: str, config: AnalysisExportConfig) -> bool:
        """
        导出分析图表图像（固定使用Matplotlib引擎）
        
        Args:
            analysis_data: 分析数据
            analysis_type: 分析类型
            output_dir: 输出目录
            image_name: 图像名称
            config: 导出配置
            
        Returns:
            bool: 是否导出成功
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # 使用非交互式后端
            
            # 设置Matplotlib默认参数
            MatplotlibChartStyles.setup_matplotlib_defaults()
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 根据分析类型绘制不同的图表
            if analysis_type == AnalysisExportType.COLOR_HISTOGRAM:
                self._plot_color_histogram(ax, analysis_data.get('histogram', []))
            elif analysis_type == AnalysisExportType.RGB_PARADE:
                self._plot_rgb_parade(ax, analysis_data.get('rgb_parade', []))
            elif analysis_type == AnalysisExportType.HUE_HISTOGRAM:
                self._plot_hue_histogram(ax, analysis_data.get('hue_histogram', []))
            elif analysis_type == AnalysisExportType.SATURATION_HISTOGRAM:
                self._plot_saturation_histogram(ax, analysis_data.get('sat_histogram', []))
            elif analysis_type == AnalysisExportType.LUMA_WAVEFORM:
                self._plot_luma_waveform(ax, analysis_data.get('luma_waveform', []))
            elif analysis_type == AnalysisExportType.LAB_CHROMATICITY:
                self._plot_lab_chromaticity(ax, analysis_data.get('lab_chromaticity', {}))
            
            # 保存图表
            type_name = self._get_analysis_type_name(analysis_type)
            from app.utils.matplotlib_export_utils import MatplotlibExportUtils
            chart_ext = MatplotlibExportUtils.get_file_extension(config.chart_format)
            
            # 使用安全的文件名生成
            safe_image_name = FilenameSanitizer.sanitize_filename(image_name)
            chart_filename = FilenameSanitizer.generate_safe_export_name(
                f"{safe_image_name}_{type_name}", ""
            ) + chart_ext
            
            # 处理文件名冲突
            chart_filename = FilenameSanitizer.handle_filename_conflicts(output_dir, chart_filename)
            chart_path = os.path.join(output_dir, chart_filename)
            
            success = MatplotlibExportUtils.save_figure_to_file(
                fig, chart_path, config.chart_format, config.chart_quality
            )
            
            plt.close(fig)  # 释放内存
            return success
            
        except Exception as e:
            logger.error(f"导出图表失败: {e}")
            return False
    
    def _plot_color_histogram(self, ax, hist_data):
        """绘制色彩直方图（与主界面Matplotlib渲染一致）"""
        if not hist_data or len(hist_data) == 0:
            return
            
        style = MatplotlibChartStyles.get_color_histogram_style()
        colors = style['colors']
        labels = style['labels']
        
        for i, channel_data in enumerate(hist_data):
            color = colors[i] if i < len(colors) else f'C{i}'
            label = labels[i] if i < len(labels) else f'通道{i}'
            ax.plot(channel_data, color=color, alpha=style['alpha'], 
                   linewidth=style['linewidth'], label=label)
        
        MatplotlibChartStyles.setup_common_axis_properties(
            ax, '色彩直方图', '像素值', '频次')
        ax.legend()
    
    def _plot_rgb_parade(self, ax, parade_data):
        """绘制RGB波形（与主界面Matplotlib渲染一致）"""
        if not parade_data or len(parade_data) == 0:
            return
            
        style = MatplotlibChartStyles.get_rgb_parade_style()
        
        if len(parade_data) == 3:  # 彩色图
            # OpenCV的split返回B,G,R，重新排列为R,G,B显示
            data_to_plot = [parade_data[2], parade_data[1], parade_data[0]]  # R,G,B
            cmaps = style['cmaps']
            
            # 创建子图显示三个通道
            fig = ax.get_figure()
            fig.clear()
            # 设置图形大小
            fig.set_size_inches(10, 8)
            axes = fig.subplots(3, 1)
            
            for i, (data, cmap) in enumerate(zip(data_to_plot, cmaps)):
                if style['log_scale']:
                    log_data = MatplotlibChartStyles.apply_log_scaling(data)
                else:
                    log_data = data
                    
                axes[i].imshow(log_data, aspect=style['aspect'], cmap=cmap,
                             origin=style['origin'], extent=[0, data.shape[1], 0, 255])
                axes[i].set_title(f'{["红色", "绿色", "蓝色"][i]}通道')
                
            fig.suptitle('RGB Parade')
            fig.tight_layout()
        else:
            # 单通道处理
            channel_data = parade_data[0]
            if style['log_scale']:
                log_data = MatplotlibChartStyles.apply_log_scaling(channel_data)
            else:
                log_data = channel_data
                
            ax.imshow(log_data, aspect=style['aspect'], cmap='viridis',
                     origin=style['origin'], extent=[0, channel_data.shape[1], 0, 255])
            ax.set_title('RGB波形')
            ax.grid(True, alpha=0.3)
    
    def _plot_hue_histogram(self, ax, hue_data):
        """绘制色相直方图（与主界面Matplotlib渲染一致）"""
        if not isinstance(hue_data, np.ndarray) or len(hue_data) == 0:
            return
            
        style = MatplotlibChartStyles.get_hue_histogram_style()
        
        if style['polar']:
            # 使用极坐标显示色相圆环
            fig = ax.get_figure()
            fig.clear()
            ax = fig.add_subplot(111, projection='polar')
            
            # 创建色相角度
            theta = np.linspace(0, 2*np.pi, len(hue_data), endpoint=False)
            colors = MatplotlibChartStyles.create_hue_colors(len(hue_data))
            
            ax.bar(theta, hue_data, width=2*np.pi/len(hue_data), 
                   color=colors, alpha=style['alpha'])
            ax.set_title('色相直方图', pad=20)
        else:
            x = range(len(hue_data))
            ax.bar(x, hue_data, color='orange', alpha=style['alpha'])
            MatplotlibChartStyles.setup_common_axis_properties(
                ax, '色相直方图', '色相值', '频次')
    
    def _plot_saturation_histogram(self, ax, sat_data):
        """绘制饱和度直方图（与主界面Matplotlib渲染一致）"""
        if not isinstance(sat_data, np.ndarray) or len(sat_data) == 0:
            return
            
        style = MatplotlibChartStyles.get_saturation_histogram_style()
        x = range(len(sat_data))
        ax.bar(x, sat_data, color=style['color'], alpha=style['alpha'])
        MatplotlibChartStyles.setup_common_axis_properties(
            ax, '饱和度直方图', '饱和度值', '频次')
    
    def _plot_luma_waveform(self, ax, luma_data):
        """绘制亮度波形（与主界面Matplotlib渲染一致）"""
        if not luma_data or len(luma_data) == 0:
            return
            
        style = MatplotlibChartStyles.get_luma_waveform_style()
        channel_data = luma_data[0]
        
        if style['log_scale']:
            log_data = MatplotlibChartStyles.apply_log_scaling(channel_data)
        else:
            log_data = channel_data
            
        ax.imshow(log_data, aspect=style['aspect'], cmap=style['cmap'],
                 origin=style['origin'], extent=[0, channel_data.shape[1], 0, 255])
        ax.set_title('亮度波形图')
        ax.set_xlabel('X坐标')
        ax.set_ylabel('亮度值')
        ax.grid(True, alpha=0.3)
    
    def _plot_lab_chromaticity(self, ax, lab_data):
        """绘制Lab色度散点图（与主界面Matplotlib渲染一致）"""
        if not lab_data or not isinstance(lab_data, dict):
            return
            
        a_values = lab_data.get('a_star', [])
        b_values = lab_data.get('b_star', [])
        l_values = lab_data.get('l_values', [])
        
        if len(a_values) == 0 or len(b_values) == 0:
            return
        
        style = MatplotlibChartStyles.get_lab_chromaticity_style()
        
        # 创建散点图
        scatter = ax.scatter(a_values, b_values, 
                           c=l_values if len(l_values) > 0 else 'blue',
                           cmap=style['cmap'], alpha=style['alpha'], s=style['size'])
        
        ax.set_title('Lab色度分析')
        ax.set_xlabel('a* (绿色 ← → 红色)')
        ax.set_ylabel('b* (蓝色 ← → 黄色)')
        ax.set_xlim(-128, 127)
        ax.set_ylim(-128, 127)
        ax.grid(True, alpha=0.3)
        
        # 添加颜色条
        if len(l_values) > 0:
            import matplotlib.pyplot as plt
            plt.colorbar(scatter, ax=ax, label='L* (Lightness)')