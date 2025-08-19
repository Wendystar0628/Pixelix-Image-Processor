"""文件名安全处理器"""
import os
import re
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FileProcessingResult:
    """文件处理结果"""
    success: bool
    processed_path: str
    original_encoding: str
    target_encoding: str
    error_message: Optional[str]


class FilenameSanitizer:
    """文件名安全处理器"""
    
    # Windows文件名非法字符
    INVALID_CHARS = r'[<>:"/\\|?*]'
    # 保留名称
    RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    # 最大文件名长度
    MAX_FILENAME_LENGTH = 200
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        清理和标准化文件名
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的安全文件名
        """
        try:
            if not filename:
                return "unnamed_file"
            
            # 分离文件名和扩展名
            name, ext = os.path.splitext(filename)
            
            # 清理文件名部分
            clean_name = cls._clean_filename_part(name)
            
            # 检查保留名称
            if clean_name.upper() in cls.RESERVED_NAMES:
                clean_name = f"_{clean_name}"
            
            # 限制长度
            if len(clean_name) > cls.MAX_FILENAME_LENGTH:
                clean_name = clean_name[:cls.MAX_FILENAME_LENGTH]
            
            # 确保不以点或空格结尾
            clean_name = clean_name.rstrip('. ')
            
            # 如果清理后为空，使用默认名称
            if not clean_name:
                clean_name = "unnamed_file"
            
            result = clean_name + ext
            logger.debug(f"文件名清理: {filename} -> {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"文件名清理失败: {e}")
            return "error_filename.tmp"
    
    @classmethod
    def generate_safe_export_name(cls, original_name: str, suffix: str = "") -> str:
        """
        生成安全的导出文件名
        
        Args:
            original_name: 原始文件名
            suffix: 后缀（如分析类型）
            
        Returns:
            str: 安全的导出文件名
        """
        try:
            # 分离文件名和扩展名
            name, ext = os.path.splitext(original_name)
            
            # 清理文件名
            clean_name = cls.sanitize_filename(name)
            
            # 添加后缀
            if suffix:
                clean_suffix = cls._clean_filename_part(suffix)
                export_name = f"{clean_name}_{clean_suffix}"
            else:
                export_name = clean_name
            
            # 再次检查长度
            if len(export_name) > cls.MAX_FILENAME_LENGTH:
                # 截断主文件名，保留后缀
                if suffix:
                    clean_suffix = cls._clean_filename_part(suffix)
                    available_length = cls.MAX_FILENAME_LENGTH - len(clean_suffix) - 1
                    export_name = f"{clean_name[:available_length]}_{clean_suffix}"
                else:
                    export_name = export_name[:cls.MAX_FILENAME_LENGTH]
            
            return export_name + ext
            
        except Exception as e:
            logger.error(f"导出文件名生成失败: {e}")
            return f"export_{suffix}.tmp" if suffix else "export.tmp"
    
    @classmethod
    def handle_filename_conflicts(cls, base_path: str, filename: str) -> str:
        """
        处理文件名冲突，自动生成唯一文件名
        
        Args:
            base_path: 基础路径
            filename: 文件名
            
        Returns:
            str: 唯一的文件名
        """
        try:
            full_path = os.path.join(base_path, filename)
            
            # 如果文件不存在，直接返回
            if not os.path.exists(full_path):
                return filename
            
            # 分离文件名和扩展名
            name, ext = os.path.splitext(filename)
            
            # 尝试添加数字后缀
            counter = 1
            while counter <= 9999:  # 限制尝试次数
                new_filename = f"{name}_{counter:04d}{ext}"
                new_full_path = os.path.join(base_path, new_filename)
                
                if not os.path.exists(new_full_path):
                    logger.debug(f"文件名冲突解决: {filename} -> {new_filename}")
                    return new_filename
                
                counter += 1
            
            # 如果仍然冲突，使用时间戳
            import time
            timestamp = int(time.time())
            new_filename = f"{name}_{timestamp}{ext}"
            logger.warning(f"使用时间戳解决文件名冲突: {filename} -> {new_filename}")
            
            return new_filename
            
        except Exception as e:
            logger.error(f"文件名冲突处理失败: {e}")
            # 返回带时间戳的文件名作为最后的回退
            import time
            timestamp = int(time.time())
            name, ext = os.path.splitext(filename)
            return f"{name}_{timestamp}{ext}"
    
    @classmethod
    def _clean_filename_part(cls, name_part: str) -> str:
        """
        清理文件名部分（不包括扩展名）
        
        Args:
            name_part: 文件名部分
            
        Returns:
            str: 清理后的文件名部分
        """
        try:
            # 移除非法字符
            clean_part = re.sub(cls.INVALID_CHARS, '_', name_part)
            
            # 移除控制字符
            clean_part = ''.join(char for char in clean_part if ord(char) >= 32)
            
            # 压缩连续的下划线
            clean_part = re.sub(r'_+', '_', clean_part)
            
            # 移除开头和结尾的下划线
            clean_part = clean_part.strip('_')
            
            return clean_part
            
        except Exception as e:
            logger.error(f"文件名部分清理失败: {e}")
            return "cleaned_name"
    
    @classmethod
    def validate_filename(cls, filename: str) -> bool:
        """
        验证文件名是否安全
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否为安全的文件名
        """
        try:
            if not filename or len(filename) > cls.MAX_FILENAME_LENGTH:
                return False
            
            # 检查非法字符
            if re.search(cls.INVALID_CHARS, filename):
                return False
            
            # 检查保留名称
            name, _ = os.path.splitext(filename)
            if name.upper() in cls.RESERVED_NAMES:
                return False
            
            # 检查是否以点或空格结尾
            if filename.endswith('.') or filename.endswith(' '):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"文件名验证失败: {e}")
            return False