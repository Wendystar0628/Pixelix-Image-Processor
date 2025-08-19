"""
批处理导出配置管理器模块

负责管理批处理的导出配置，包括配置的获取、更新和枚举类型转换。
"""
from typing import Dict, Optional, Any
from PyQt6.QtCore import QObject

from app.features.batch_processing.managers.batch_job_manager import JobManager
from app.core.models.export_config import (
    ExportConfig, OutputDirectoryMode, ConflictResolution, 
    NamingPattern, ExportFormat
)


class BatchExportConfigManager(QObject):
    """
    批处理导出配置管理器
    
    职责：
    - 管理导出配置的获取和更新
    - 处理枚举类型的转换
    - 提供配置验证和默认值管理
    """
    
    def __init__(self, job_manager: JobManager, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.job_manager = job_manager
    
    def get_export_config(self) -> ExportConfig:
        """
        获取当前的导出配置
        
        Returns:
            ExportConfig: 导出配置
        """
        return self.job_manager.get_default_export_config()
    
    def update_export_config(self, config_updates: Dict[str, Any]) -> None:
        """
        更新导出配置
        
        Args:
            config_updates: 包含要更新的配置项的字典
        """
        if not config_updates:
            return
            
        config = self.job_manager.get_default_export_config()
        
        # 更新配置项，处理枚举转换
        for key, value in config_updates.items():
            if hasattr(config, key):
                try:
                    # 处理枚举类型的转换
                    converted_value = self._convert_enum_value(key, value)
                    setattr(config, key, converted_value)
                except Exception as e:
                    # 记录错误但继续处理其他配置项
                    print(f"Warning: Failed to set config {key}={value}: {e}")
        
        # 更新默认配置
        self.job_manager.set_default_export_config(config)
    
    def _convert_enum_value(self, key: str, value: Any) -> Any:
        """
        将字符串值转换为对应的枚举对象
        
        Args:
            key: 配置项键名
            value: 配置项值
            
        Returns:
            转换后的值（枚举对象或原值）
        """
        # 如果已经是枚举对象，直接返回
        if hasattr(value, 'value'):
            return value
        
        # 如果不是字符串，直接返回
        if not isinstance(value, str):
            return value
        
        # 根据键名进行枚举转换
        if key == "output_directory_mode":
            return self._convert_to_enum(OutputDirectoryMode, value)
        elif key == "conflict_resolution":
            return self._convert_to_enum(ConflictResolution, value)
        elif key == "naming_pattern":
            return self._convert_to_enum(NamingPattern, value)
        elif key == "export_format":
            return self._convert_to_enum(ExportFormat, value)
        
        # 不是枚举类型，返回原值
        return value
    
    def _convert_to_enum(self, enum_class, value: str) -> Any:
        """
        将字符串值转换为指定的枚举对象
        
        Args:
            enum_class: 枚举类
            value: 字符串值
            
        Returns:
            枚举对象或原字符串值（如果转换失败）
        """
        try:
            # 尝试通过值查找枚举
            for enum_item in enum_class:
                if enum_item.value == value:
                    return enum_item
            
            # 如果没找到，尝试直接构造
            return enum_class(value)
        except (ValueError, AttributeError):
            # 转换失败，返回原值
            return value
    
    def validate_config(self, config: ExportConfig) -> bool:
        """
        验证导出配置的有效性
        
        Args:
            config: 要验证的配置
            
        Returns:
            bool: 配置是否有效
        """
        # 检查输出目录模式
        if config.output_directory_mode == OutputDirectoryMode.SAVE_TO_SINGLE_FOLDER:
            if not config.output_directory:
                return False
        
        # 检查命名模式相关设置
        if config.naming_pattern == NamingPattern.PREFIX and not config.prefix:
            return False
        
        if config.naming_pattern == NamingPattern.SUFFIX and not config.suffix:
            return False
        
        if config.naming_pattern == NamingPattern.CUSTOM and not config.custom_pattern:
            return False
        
        # 检查质量设置范围
        if not (0 <= config.jpeg_quality <= 100):
            return False
        
        if not (0 <= config.png_compression <= 9):
            return False
        
        return True
    
    def get_default_config(self) -> ExportConfig:
        """
        获取默认的导出配置
        
        Returns:
            ExportConfig: 默认配置
        """
        return ExportConfig()
    
    def reset_to_defaults(self) -> None:
        """
        重置配置为默认值
        """
        default_config = self.get_default_config()
        self.job_manager.set_default_export_config(default_config)