"""
分析数据格式转换工具
"""

import json
import csv
import os
import logging
from typing import Dict, Any, List
import numpy as np
import pandas as pd

from app.core.models.analysis_export_config import AnalysisDataFormat

logger = logging.getLogger(__name__)


class AnalysisDataConverter:
    """分析数据格式转换工具类"""
    
    @staticmethod
    def export_data(data: Dict[str, Any], file_path: str, 
                   format_type: AnalysisDataFormat) -> bool:
        """
        导出分析数据到文件
        
        Args:
            data: 分析数据字典
            file_path: 输出文件路径
            format_type: 数据格式
            
        Returns:
            bool: 是否导出成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if format_type == AnalysisDataFormat.JSON:
                return AnalysisDataConverter._to_json(data, file_path)
            elif format_type == AnalysisDataFormat.CSV:
                return AnalysisDataConverter._to_csv(data, file_path)
            elif format_type == AnalysisDataFormat.XLSX:
                return AnalysisDataConverter._to_xlsx(data, file_path)
            else:
                logger.error(f"不支持的数据格式: {format_type}")
                return False
                
        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            return False
    
    @staticmethod
    def _to_json(data: Dict[str, Any], file_path: str) -> bool:
        """导出为JSON格式"""
        try:
            # 转换numpy数组为列表
            json_data = AnalysisDataConverter._convert_numpy_to_list(data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"JSON数据已保存到: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存JSON失败: {e}")
            return False
    
    @staticmethod
    def _to_csv(data: Dict[str, Any], file_path: str) -> bool:
        """导出为CSV格式"""
        try:
            # 将数据转换为表格格式
            table_data = AnalysisDataConverter._convert_to_table_format(data)
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入表头
                if table_data:
                    writer.writerow(table_data[0].keys())
                    
                    # 写入数据行
                    for row in table_data:
                        writer.writerow(row.values())
            
            logger.debug(f"CSV数据已保存到: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存CSV失败: {e}")
            return False
    
    @staticmethod
    def _to_xlsx(data: Dict[str, Any], file_path: str) -> bool:
        """导出为Excel格式"""
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 为每种分析类型创建工作表
                if 'histogram' in data:
                    hist_df = AnalysisDataConverter._format_histogram_data(data['histogram'])
                    hist_df.to_excel(writer, sheet_name='色彩直方图', index=False)
                
                if 'rgb_parade' in data:
                    parade_df = AnalysisDataConverter._format_rgb_parade_data(data['rgb_parade'])
                    parade_df.to_excel(writer, sheet_name='RGB波形', index=False)
                
                if 'hue_histogram' in data:
                    hue_df = AnalysisDataConverter._format_hue_data(data['hue_histogram'])
                    hue_df.to_excel(writer, sheet_name='色相直方图', index=False)
                
                if 'sat_histogram' in data:
                    sat_df = AnalysisDataConverter._format_saturation_data(data['sat_histogram'])
                    sat_df.to_excel(writer, sheet_name='饱和度直方图', index=False)
                
                if 'luma_waveform' in data:
                    luma_df = AnalysisDataConverter._format_luma_waveform_data(data['luma_waveform'])
                    luma_df.to_excel(writer, sheet_name='亮度波形图', index=False)
                
                if 'lab_chromaticity' in data:
                    lab_df = AnalysisDataConverter._format_lab_analysis_data(data['lab_chromaticity'])
                    lab_df.to_excel(writer, sheet_name='Lab色度', index=False)
            
            logger.debug(f"Excel数据已保存到: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存Excel失败: {e}")
            return False
    
    @staticmethod
    def _convert_numpy_to_list(data: Any) -> Any:
        """递归转换numpy数组为列表"""
        if isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, dict):
            return {k: AnalysisDataConverter._convert_numpy_to_list(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [AnalysisDataConverter._convert_numpy_to_list(item) for item in data]
        else:
            return data
    
    @staticmethod
    def _convert_to_table_format(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """将分析数据转换为表格格式"""
        table_data = []
        
        # 处理色彩直方图数据
        if 'histogram' in data:
            hist_data = data['histogram']
            if isinstance(hist_data, list) and len(hist_data) > 0:
                for i, channel_data in enumerate(hist_data):
                    channel_name = ['蓝色', '绿色', '红色'][i] if i < 3 else f'通道{i}'
                    for j, value in enumerate(channel_data):
                        table_data.append({
                            '分析类型': '色彩直方图',
                            '通道': channel_name,
                            '像素值': j,
                            '频次': float(value)
                        })
        
        # 处理RGB波形数据
        if 'rgb_parade' in data:
            parade_data = data['rgb_parade']
            if isinstance(parade_data, list) and len(parade_data) > 0:
                channel_names = ['蓝色', '绿色', '红色']
                for i, channel_data in enumerate(parade_data):
                    channel_name = channel_names[i] if i < len(channel_names) else f'通道{i}'
                    height, width = channel_data.shape
                    sample_step = max(1, width // 50)  # 采样以减少数据量
                    for x in range(0, width, sample_step):
                        for y in range(height):
                            if channel_data[y, x] > 0:
                                table_data.append({
                                    '分析类型': 'RGB波形',
                                    '通道': channel_name,
                                    'X坐标': x,
                                    '像素值': y,
                                    '强度': float(channel_data[y, x])
                                })
        
        # 处理色相直方图数据
        if 'hue_histogram' in data:
            hue_data = data['hue_histogram']
            if isinstance(hue_data, np.ndarray) and len(hue_data) > 0:
                for i, value in enumerate(hue_data):
                    table_data.append({
                        '分析类型': '色相直方图',
                        '色相值': i,
                        '频次': float(value)
                    })
        
        # 处理饱和度直方图数据
        if 'sat_histogram' in data:
            sat_data = data['sat_histogram']
            if isinstance(sat_data, np.ndarray) and len(sat_data) > 0:
                for i, value in enumerate(sat_data):
                    table_data.append({
                        '分析类型': '饱和度直方图',
                        '饱和度值': i,
                        '频次': float(value)
                    })
        
        # 处理亮度波形数据
        if 'luma_waveform' in data:
            luma_data = data['luma_waveform']
            if isinstance(luma_data, list) and len(luma_data) > 0:
                # 使用第一个通道作为亮度参考
                luma_channel = luma_data[0]
                height, width = luma_channel.shape
                sample_step = max(1, width // 50)  # 采样以减少数据量
                for x in range(0, width, sample_step):
                    for y in range(height):
                        if luma_channel[y, x] > 0:
                            table_data.append({
                                '分析类型': '亮度波形图',
                                'X坐标': x,
                                '像素值': y,
                                '强度': float(luma_channel[y, x])
                            })
        
        # 处理Lab色度数据
        if 'lab_chromaticity' in data:
            lab_data = data['lab_chromaticity']
            if isinstance(lab_data, dict):
                a_values = lab_data.get('a_star', [])
                b_values = lab_data.get('b_star', [])
                l_values = lab_data.get('l_values', [])
                
                for i in range(len(a_values)):
                    table_data.append({
                        '分析类型': 'Lab色度',
                        'a*值': float(a_values[i]) if i < len(a_values) else 0,
                        'b*值': float(b_values[i]) if i < len(b_values) else 0,
                        'L*值': float(l_values[i]) if i < len(l_values) else 0
                    })
        
        return table_data
    
    @staticmethod
    def _format_histogram_data(hist_data: List[np.ndarray]) -> pd.DataFrame:
        """格式化直方图数据"""
        data_rows = []
        channel_names = ['蓝色通道', '绿色通道', '红色通道']
        
        for i, channel_data in enumerate(hist_data):
            channel_name = channel_names[i] if i < len(channel_names) else f'通道{i}'
            for j, value in enumerate(channel_data):
                data_rows.append({
                    '通道': channel_name,
                    '像素值': j,
                    '频次': float(value)
                })
        
        return pd.DataFrame(data_rows)
    
    @staticmethod
    def _format_rgb_parade_data(parade_data: List[np.ndarray]) -> pd.DataFrame:
        """格式化RGB波形数据"""
        data_rows = []
        channel_names = ['蓝色通道', '绿色通道', '红色通道']
        
        for i, channel_data in enumerate(parade_data):
            channel_name = channel_names[i] if i < len(channel_names) else f'通道{i}'
            height, width = channel_data.shape
            
            # 采样数据以减少文件大小
            sample_step = max(1, width // 100)
            for x in range(0, width, sample_step):
                for y in range(height):
                    if channel_data[y, x] > 0:
                        data_rows.append({
                            '通道': channel_name,
                            'X坐标': x,
                            '像素值': y,
                            '强度': float(channel_data[y, x])
                        })
        
        return pd.DataFrame(data_rows)
    
    @staticmethod
    def _format_hue_data(hue_data: np.ndarray) -> pd.DataFrame:
        """格式化色相直方图数据"""
        data_rows = []
        
        for i, value in enumerate(hue_data):
            data_rows.append({
                '色相值': i,
                '频次': float(value)
            })
        
        return pd.DataFrame(data_rows)
    
    @staticmethod
    def _format_saturation_data(sat_data: np.ndarray) -> pd.DataFrame:
        """格式化饱和度直方图数据"""
        data_rows = []
        
        for i, value in enumerate(sat_data):
            data_rows.append({
                '饱和度值': i,
                '频次': float(value)
            })
        
        return pd.DataFrame(data_rows)
    
    @staticmethod
    def _format_lab_analysis_data(lab_data: Dict[str, np.ndarray]) -> pd.DataFrame:
        """格式化Lab分析数据"""
        data_rows = []
        
        a_values = lab_data.get('a_star', [])
        b_values = lab_data.get('b_star', [])
        l_values = lab_data.get('l_values', [])
        
        for i in range(len(a_values)):
            data_rows.append({
                'a*值': float(a_values[i]) if i < len(a_values) else 0,
                'b*值': float(b_values[i]) if i < len(b_values) else 0,
                'L*值': float(l_values[i]) if i < len(l_values) else 0
            })
        
        return pd.DataFrame(data_rows)
    
    @staticmethod
    def _format_luma_waveform_data(luma_data: List[np.ndarray]) -> pd.DataFrame:
        """格式化亮度波形数据"""
        data_rows = []
        
        # 亮度波形通常使用第一个通道或计算亮度
        if len(luma_data) > 0:
            luma_channel = luma_data[0]  # 使用第一个通道作为亮度参考
            height, width = luma_channel.shape
            
            # 采样数据以减少文件大小
            sample_step = max(1, width // 100)
            for x in range(0, width, sample_step):
                for y in range(height):
                    if luma_channel[y, x] > 0:
                        data_rows.append({
                            '类型': '亮度波形图',
                            'X坐标': x,
                            '像素值': y,
                            '强度': float(luma_channel[y, x])
                        })
        
        return pd.DataFrame(data_rows)
    
    @staticmethod
    def get_file_extension(format_type: AnalysisDataFormat) -> str:
        """获取格式对应的文件扩展名"""
        format_map = {
            AnalysisDataFormat.JSON: '.json',
            AnalysisDataFormat.CSV: '.csv',
            AnalysisDataFormat.XLSX: '.xlsx'
        }
        return format_map.get(format_type, '.csv')