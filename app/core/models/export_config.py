"""
导出配置模块

定义了用于批量导出图像的配置类。
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class NamingPattern(Enum):
    """命名模式枚举"""
    ORIGINAL = "original"  # 原始文件名
    PREFIX = "prefix"      # 前缀+原始文件名
    SUFFIX = "suffix"      # 原始文件名+后缀
    INDEX = "index"        # 索引号
    PREFIX_INDEX = "prefix_index"  # 前缀+索引号
    CUSTOM = "custom"      # 自定义模式


class ExportFormat(Enum):
    """导出格式枚举"""
    ORIGINAL = "original"  # 保持原始格式
    PNG = "png"
    JPEG = "jpeg"
    BMP = "bmp"
    TIFF = "tiff"


class OutputDirectoryMode(Enum):
    """输出目录模式枚举"""
    SAVE_IN_PLACE = "save_in_place"  # 在原图位置保存
    SAVE_TO_SINGLE_FOLDER = "save_to_single_folder"  # 保存到统一文件夹
    MAINTAIN_DIRECTORY_STRUCTURE = "maintain_directory_structure"  # 保持目录结构


class ConflictResolution(Enum):
    """文件冲突解决策略枚举"""
    OVERWRITE = "overwrite"  # 覆盖现有文件
    SKIP = "skip"  # 跳过已存在的文件
    RENAME = "rename"  # 重命名新文件（添加数字后缀）


@dataclass
class ExportConfig:
    """
    导出配置类，用于封装批量导出的配置信息。
    """
    # 输出目录
    output_directory: str = ""
    
    # 输出目录模式
    output_directory_mode: OutputDirectoryMode = OutputDirectoryMode.SAVE_TO_SINGLE_FOLDER
    
    # 命名相关
    naming_pattern: NamingPattern = NamingPattern.ORIGINAL
    prefix: str = ""
    suffix: str = ""
    start_index: int = 1
    index_digits: int = 3  # 索引数字的位数，如001, 002...
    custom_pattern: str = "{filename}"
    
    # 格式相关
    export_format: ExportFormat = ExportFormat.ORIGINAL
    jpeg_quality: int = 90  # JPEG质量 (0-100)
    png_compression: int = 9  # PNG压缩级别 (0-9)
    
    # 其他选项
    overwrite_existing: bool = False
    create_subfolders: bool = False
    subfolder_pattern: str = "{date}"
    
    # 冲突解决
    conflict_resolution: ConflictResolution = ConflictResolution.OVERWRITE
    
    # 格式特定参数的缓存
    _format_params: Dict[str, List[Any]] = field(default_factory=dict, init=False, repr=False)
    
    def __post_init__(self):
        """初始化后的处理，预计算格式参数"""
        import cv2
        
        # 预计算各种格式的参数
        self._format_params = {
            ".jpg": [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality],
            ".jpeg": [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality],
            ".png": [int(cv2.IMWRITE_PNG_COMPRESSION), self.png_compression],
        }
    
    def get_output_filename(self, original_filename: str, index: int) -> str:
        """
        根据命名模式生成输出文件名（不含路径和扩展名）
        
        Args:
            original_filename: 原始文件名（不含扩展名）
            index: 当前索引号
            
        Returns:
            str: 生成的输出文件名（不含扩展名）
        """
        # 获取不含扩展名的原始文件名
        filename_no_ext = os.path.splitext(original_filename)[0]
        
        # 格式化索引号
        formatted_index = str(index + self.start_index - 1).zfill(self.index_digits)
        
        # 根据命名模式生成文件名
        if self.naming_pattern == NamingPattern.ORIGINAL:
            return filename_no_ext
        elif self.naming_pattern == NamingPattern.PREFIX:
            return f"{self.prefix}{filename_no_ext}"
        elif self.naming_pattern == NamingPattern.SUFFIX:
            return f"{filename_no_ext}{self.suffix}"
        elif self.naming_pattern == NamingPattern.INDEX:
            return formatted_index
        elif self.naming_pattern == NamingPattern.PREFIX_INDEX:
            return f"{self.prefix}{formatted_index}"
        elif self.naming_pattern == NamingPattern.CUSTOM:
            # 替换自定义模式中的占位符
            return (self.custom_pattern
                   .replace("{filename}", filename_no_ext)
                   .replace("{index}", formatted_index)
                   .replace("{prefix}", self.prefix)
                   .replace("{suffix}", self.suffix))
        else:
            # 默认使用原始文件名
            return filename_no_ext
    
    def get_output_extension(self, original_extension: str) -> str:
        """
        获取输出文件扩展名
        
        Args:
            original_extension: 原始文件扩展名（包含点，如".jpg"）
            
        Returns:
            str: 输出文件扩展名（包含点，如".jpg"）
        """
        if self.export_format == ExportFormat.ORIGINAL:
            # 如果原始扩展名为空，默认使用PNG
            return original_extension if original_extension else ".png"
        elif self.export_format == ExportFormat.PNG:
            return ".png"
        elif self.export_format == ExportFormat.JPEG:
            return ".jpg"
        elif self.export_format == ExportFormat.BMP:
            return ".bmp"
        elif self.export_format == ExportFormat.TIFF:
            return ".tiff"
        else:
            # 默认使用PNG
            return ".png"
    
    def get_output_path(self, original_filename: str, original_path: str, index: int, job_name: Optional[str] = None) -> Optional[str]:
        """
        获取完整的输出文件路径
        
        Args:
            original_filename: 原始文件名
            original_path: 原始文件路径
            index: 当前索引号
            job_name: 作业名称（用于创建作业子文件夹）
            
        Returns:
            Optional[str]: 完整的输出文件路径，如果应该跳过则返回None
        """
        # 规范化输入路径
        original_path = os.path.normpath(original_path)
        
        # 获取原始扩展名
        original_ext = os.path.splitext(original_path)[1].lower()
        
        # 获取输出文件名（不含扩展名）
        output_filename = self.get_output_filename(original_filename, index)
        
        # 获取输出扩展名
        output_ext = self.get_output_extension(original_ext)
        
        # 完整文件名
        full_filename = f"{output_filename}{output_ext}"
        
        # 确定输出目录
        if self.output_directory_mode == OutputDirectoryMode.SAVE_IN_PLACE:
            # 在原图位置保存
            output_dir = os.path.dirname(original_path)
            # 确保输出目录存在并且有效
            if not output_dir:
                output_dir = "."  # 如果为空，使用当前目录
        elif self.output_directory_mode == OutputDirectoryMode.MAINTAIN_DIRECTORY_STRUCTURE:
            # 保持目录结构
            # 获取原始路径相对于某个基准目录的相对路径
            # 这里假设所有原始路径都在一个共同的父目录下
            # 实际应用中可能需要更复杂的逻辑来确定相对路径
            try:
                # 尝试找到所有原始路径的共同父目录
                # 这里简化处理，取原始路径的父目录的父目录
                base_dir = os.path.dirname(os.path.dirname(original_path))
                rel_path = os.path.relpath(os.path.dirname(original_path), base_dir)
                output_dir = os.path.normpath(os.path.join(self.output_directory, rel_path))
            except:
                # 如果出错，直接使用输出目录
                if not self.output_directory:
                    raise ValueError("输出目录未设置，请选择一个有效的输出目录")
                output_dir = os.path.normpath(self.output_directory)
        else:  # OutputDirectoryMode.SAVE_TO_SINGLE_FOLDER
            if not self.output_directory:
                # 如果输出目录为空，抛出异常而不是使用当前目录
                raise ValueError("输出目录未设置，请选择一个有效的输出目录")
            output_dir = os.path.normpath(self.output_directory)
        
        # 如果提供了作业名称，在输出目录下创建作业子文件夹
        if job_name:
            # 清理作业名称，移除不适合作为文件夹名的字符
            safe_job_name = self._sanitize_folder_name(job_name)
            output_dir = os.path.join(output_dir, safe_job_name)
        elif job_name is not None:  # 空字符串也创建默认文件夹
            safe_job_name = self._sanitize_folder_name("")
            output_dir = os.path.join(output_dir, safe_job_name)
        
        # 如果需要创建子文件夹
        if self.create_subfolders:
            import datetime
            
            # 获取当前日期时间
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H-%M-%S")
            
            # 替换子文件夹模式中的占位符
            subfolder = (self.subfolder_pattern
                        .replace("{date}", date_str)
                        .replace("{time}", time_str)
                        .replace("{job_name}", safe_job_name if job_name else ""))
            
            # 完整子文件夹路径
            output_dir = os.path.join(output_dir, subfolder)
        
        # 构建完整路径
        output_path = os.path.normpath(os.path.join(output_dir, full_filename))
        
        # 处理文件冲突
        if os.path.exists(output_path) and self.conflict_resolution != ConflictResolution.OVERWRITE:
            if self.conflict_resolution == ConflictResolution.SKIP:
                # 跳过已存在的文件（返回None表示跳过）
                return None
            elif self.conflict_resolution == ConflictResolution.RENAME:
                # 重命名新文件
                base_name = os.path.splitext(full_filename)[0]
                ext = os.path.splitext(full_filename)[1]
                counter = 1
                
                # 尝试添加数字后缀，直到找到不冲突的名称
                while True:
                    new_name = f"{base_name}_{counter}{ext}"
                    new_path = os.path.normpath(os.path.join(output_dir, new_name))
                    if not os.path.exists(new_path):
                        return new_path
                    counter += 1
        
        # 返回完整路径
        return output_path
    
    def _sanitize_folder_name(self, name: str) -> str:
        """
        清理文件夹名称，移除不适合作为文件夹名的字符
        
        Args:
            name: 原始名称
            
        Returns:
            str: 清理后的安全文件夹名称
        """
        import re
        
        # 移除或替换不安全的字符
        # Windows和Unix系统都不允许的字符: < > : " | ? * \ /
        unsafe_chars = r'[<>:"|?*\\/]'
        safe_name = re.sub(unsafe_chars, '_', name)
        
        # 移除前后空格和点
        safe_name = safe_name.strip(' .')
        
        # 如果名称为空或只包含不安全字符，使用默认名称
        if not safe_name:
            safe_name = "unnamed_job"
        
        # 限制长度（Windows路径限制）
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
        
        return safe_name
    
    def get_format_params(self, file_path: str) -> Optional[List[Any]]:
        """
        获取指定文件路径的格式特定参数
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[List[Any]]: 格式特定参数，如果没有则返回None
        """
        ext = os.path.splitext(file_path)[1].lower()
        return self._format_params.get(ext)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典，便于序列化
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return {
            "output_directory": self.output_directory,
            "output_directory_mode": self.output_directory_mode.value,
            "naming_pattern": self.naming_pattern.value,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "start_index": self.start_index,
            "index_digits": self.index_digits,
            "custom_pattern": self.custom_pattern,
            "export_format": self.export_format.value,
            "jpeg_quality": self.jpeg_quality,
            "png_compression": self.png_compression,
            "overwrite_existing": self.overwrite_existing,
            "create_subfolders": self.create_subfolders,
            "subfolder_pattern": self.subfolder_pattern,
            "conflict_resolution": self.conflict_resolution.value,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ExportConfig':
        """
        从字典创建配置对象
        
        Args:
            config_dict: 配置字典
            
        Returns:
            ExportConfig: 配置对象
        """
        # 转换枚举值
        naming_pattern = NamingPattern(config_dict.get("naming_pattern", NamingPattern.ORIGINAL.value))
        export_format = ExportFormat(config_dict.get("export_format", ExportFormat.ORIGINAL.value))
        
        # 新增枚举值转换
        output_directory_mode = OutputDirectoryMode(
            config_dict.get("output_directory_mode", OutputDirectoryMode.SAVE_TO_SINGLE_FOLDER.value)
        )
        conflict_resolution = ConflictResolution(
            config_dict.get("conflict_resolution", ConflictResolution.OVERWRITE.value)
        )
        
        return cls(
            output_directory=config_dict.get("output_directory", ""),
            output_directory_mode=output_directory_mode,
            naming_pattern=naming_pattern,
            prefix=config_dict.get("prefix", ""),
            suffix=config_dict.get("suffix", ""),
            start_index=config_dict.get("start_index", 1),
            index_digits=config_dict.get("index_digits", 3),
            custom_pattern=config_dict.get("custom_pattern", "{filename}"),
            export_format=export_format,
            jpeg_quality=config_dict.get("jpeg_quality", 90),
            png_compression=config_dict.get("png_compression", 9),
            overwrite_existing=config_dict.get("overwrite_existing", False),
            create_subfolders=config_dict.get("create_subfolders", False),
            subfolder_pattern=config_dict.get("subfolder_pattern", "{date}"),
            conflict_resolution=conflict_resolution,
        ) 