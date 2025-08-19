"""
数据分析导出配置模型
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class AnalysisExportType(Enum):
    """分析导出类型枚举"""
    COLOR_HISTOGRAM = "color_histogram"      # 色彩直方图
    LUMA_WAVEFORM = "luma_waveform"         # 亮度波形图
    RGB_PARADE = "rgb_parade"               # RGB波形
    HUE_HISTOGRAM = "hue_histogram"         # 色相直方图
    SATURATION_HISTOGRAM = "saturation_histogram"  # 饱和度直方图
    LAB_CHROMATICITY = "lab_chromaticity"   # Lab色度


class AnalysisDataFormat(Enum):
    """分析数据格式枚举"""
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"


class AnalysisChartFormat(Enum):
    """分析图表格式枚举"""
    PNG = "png"
    JPEG = "jpeg"
    SVG = "svg"


@dataclass
class AnalysisExportConfig:
    """数据分析导出配置"""
    export_path: str = ""
    selected_analysis_types: List[AnalysisExportType] = None
    chart_format: AnalysisChartFormat = AnalysisChartFormat.PNG
    data_format: AnalysisDataFormat = AnalysisDataFormat.CSV
    chart_quality: int = 95  # JPEG质量
    include_raw_data: bool = True
    # 多作业选择相关字段
    selected_job_ids: List[str] = None  # 选中的作业ID列表
    export_mode: str = "selected"  # 导出模式: 仅支持 "selected"
    
    def __post_init__(self):
        if self.selected_analysis_types is None:
            self.selected_analysis_types = [
                AnalysisExportType.COLOR_HISTOGRAM,
                AnalysisExportType.LUMA_WAVEFORM,
                AnalysisExportType.RGB_PARADE,
                AnalysisExportType.HUE_HISTOGRAM,
                AnalysisExportType.SATURATION_HISTOGRAM,
                AnalysisExportType.LAB_CHROMATICITY
            ]
        if self.selected_job_ids is None:
            self.selected_job_ids = []
    
    def get_analysis_type_display_names(self) -> dict:
        """获取分析类型的显示名称"""
        return {
            AnalysisExportType.COLOR_HISTOGRAM: "色彩直方图",
            AnalysisExportType.LUMA_WAVEFORM: "亮度波形图",
            AnalysisExportType.RGB_PARADE: "RGB波形",
            AnalysisExportType.HUE_HISTOGRAM: "色相直方图",
            AnalysisExportType.SATURATION_HISTOGRAM: "饱和度直方图",
            AnalysisExportType.LAB_CHROMATICITY: "Lab色度"
        }
    
    def is_valid(self) -> bool:
        """验证配置是否有效"""
        basic_valid = (
            bool(self.export_path) and
            bool(self.selected_analysis_types) and
            self.chart_quality > 0 and self.chart_quality <= 100
        )
        
        # 验证是否选择了作业
        return basic_valid and bool(self.selected_job_ids)