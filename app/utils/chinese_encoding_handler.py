"""中文编码处理工具"""
import os
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EncodingDetectionResult:
    """编码检测结果"""
    detected_encoding: str
    confidence: float
    is_chinese: bool
    fallback_used: bool


class ChineseEncodingHandler:
    """中文编码处理器"""
    
    # 支持的中文编码列表，按优先级排序
    CHINESE_ENCODINGS = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    DEFAULT_ENCODING = 'utf-8'
    
    # 编码检测缓存
    _encoding_cache = {}
    
    @classmethod
    def detect_encoding(cls, file_path: str) -> EncodingDetectionResult:
        """
        检测文件路径编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            EncodingDetectionResult: 检测结果
        """
        try:
            # 检查缓存
            if file_path in cls._encoding_cache:
                return cls._encoding_cache[file_path]
            
            # 检查是否包含中文字符
            is_chinese = cls._contains_chinese_chars(file_path)
            
            if not is_chinese:
                # 非中文路径直接返回UTF-8
                result = EncodingDetectionResult(
                    detected_encoding=cls.DEFAULT_ENCODING,
                    confidence=1.0,
                    is_chinese=False,
                    fallback_used=False
                )
                cls._encoding_cache[file_path] = result
                return result
            
            # 尝试各种编码
            for encoding in cls.CHINESE_ENCODINGS:
                try:
                    # 尝试编码和解码
                    encoded = file_path.encode(encoding)
                    decoded = encoded.decode(encoding)
                    
                    if decoded == file_path:
                        logger.debug(f"检测到编码: {encoding} for path: {file_path}")
                        result = EncodingDetectionResult(
                            detected_encoding=encoding,
                            confidence=0.9,
                            is_chinese=True,
                            fallback_used=False
                        )
                        cls._encoding_cache[file_path] = result
                        return result
                except (UnicodeEncodeError, UnicodeDecodeError):
                    continue
            
            # 所有编码都失败，使用默认编码
            logger.warning(f"编码检测失败，使用默认编码 {cls.DEFAULT_ENCODING}: {file_path}")
            result = EncodingDetectionResult(
                detected_encoding=cls.DEFAULT_ENCODING,
                confidence=0.5,
                is_chinese=True,
                fallback_used=True
            )
            cls._encoding_cache[file_path] = result
            return result
            
        except Exception as e:
            logger.error(f"编码检测异常: {e}")
            result = EncodingDetectionResult(
                detected_encoding=cls.DEFAULT_ENCODING,
                confidence=0.0,
                is_chinese=False,
                fallback_used=True
            )
            cls._encoding_cache[file_path] = result
            return result
    
    @classmethod
    def safe_encode_path(cls, path: str, target_encoding: str = None) -> Tuple[str, bool]:
        """
        安全编码转换路径
        
        Args:
            path: 原始路径
            target_encoding: 目标编码，None则自动检测
            
        Returns:
            Tuple[str, bool]: (转换后路径, 是否成功)
        """
        try:
            if target_encoding is None:
                detection_result = cls.detect_encoding(path)
                target_encoding = detection_result.detected_encoding
            
            # 尝试转换
            if target_encoding == cls.DEFAULT_ENCODING:
                return path, True
            
            # 转换为目标编码再转回UTF-8
            encoded = path.encode(target_encoding)
            decoded = encoded.decode(target_encoding)
            
            return decoded, True
            
        except Exception as e:
            logger.error(f"编码转换失败: {e}")
            return path, False
    
    @classmethod
    def normalize_chinese_path(cls, path: str) -> str:
        """
        标准化中文路径
        
        Args:
            path: 原始路径
            
        Returns:
            str: 标准化后的路径
        """
        try:
            # 检测并转换编码
            normalized_path, success = cls.safe_encode_path(path)
            
            if not success:
                logger.warning(f"路径标准化失败，使用原始路径: {path}")
                return path
            
            # 标准化路径分隔符
            normalized_path = os.path.normpath(normalized_path)
            
            return normalized_path
            
        except Exception as e:
            logger.error(f"路径标准化异常: {e}")
            return path
    
    @classmethod
    def _contains_chinese_chars(cls, text: str) -> bool:
        """
        检查文本是否包含中文字符
        
        Args:
            text: 待检查文本
            
        Returns:
            bool: 是否包含中文字符
        """
        try:
            for char in text:
                if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
                    return True
            return False
        except Exception:
            return False
    
    @classmethod
    def handle_encoding_error(cls, error: Exception, file_path: str) -> str:
        """
        处理编码错误
        
        Args:
            error: 编码错误
            file_path: 文件路径
            
        Returns:
            str: 错误处理后的路径
        """
        logger.error(f"编码错误处理: {error} for path: {file_path}")
        
        try:
            # 尝试使用默认编码
            return cls.normalize_chinese_path(file_path)
        except Exception:
            # 最后的回退方案
            return file_path
    
    @classmethod
    def clear_cache(cls):
        """清理编码检测缓存"""
        cls._encoding_cache.clear()
        logger.debug("编码检测缓存已清理")
    
    @classmethod
    def get_cache_size(cls) -> int:
        """获取缓存大小"""
        return len(cls._encoding_cache)