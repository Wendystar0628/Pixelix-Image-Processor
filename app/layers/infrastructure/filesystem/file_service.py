"""文件系统服务实现"""
import os
import logging
from typing import Optional, List, Tuple
from pathlib import Path
import numpy as np
import cv2

from .file_service_interface import FileServiceInterface
from app.utils.chinese_encoding_handler import ChineseEncodingHandler
from app.utils.filename_sanitizer import FilenameSanitizer

logger = logging.getLogger(__name__)


class FileService(FileServiceInterface):
    """文件系统服务实现"""
    
    # 支持的图像格式
    SUPPORTED_FORMATS = [
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', 
        '.webp', '.ico', '.ppm', '.pgm', '.pbm'
    ]
    
    def __init__(self):
        """初始化文件服务"""
        logger.info("文件系统服务初始化")
    
    def load_image(self, file_path: str) -> Tuple[Optional[np.ndarray], str]:
        """加载图像文件"""
        try:
            # 标准化中文路径
            normalized_path = ChineseEncodingHandler.normalize_chinese_path(file_path)
            
            if not os.path.exists(normalized_path):
                return None, f"文件不存在: {file_path}"
            
            if not self.is_image_file(normalized_path):
                return None, f"不支持的图像格式: {file_path}"
            
            # 对于中文路径，使用numpy和cv2的组合方式读取
            encoding_result = ChineseEncodingHandler.detect_encoding(file_path)
            if encoding_result.is_chinese:
                try:
                    # 使用numpy读取文件字节，然后用cv2解码
                    with open(normalized_path, 'rb') as f:
                        file_bytes = f.read()
                    
                    # 将字节转换为numpy数组
                    nparr = np.frombuffer(file_bytes, np.uint8)
                    
                    # 使用cv2解码图像
                    image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                    
                    if image is None:
                        return None, f"无法解码图像文件: {file_path}"
                        
                except Exception as decode_error:
                    logger.warning(f"中文路径解码失败，尝试直接读取: {decode_error}")
                    # 回退到直接读取
                    image = cv2.imread(normalized_path, cv2.IMREAD_UNCHANGED)
                    
                    if image is None:
                        return None, f"无法读取图像文件: {file_path}"
            else:
                # 英文路径直接使用OpenCV读取
                image = cv2.imread(normalized_path, cv2.IMREAD_UNCHANGED)
                
                if image is None:
                    return None, f"无法读取图像文件: {file_path}"
            
            # 转换BGR到RGB（如果是彩色图像）
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            elif len(image.shape) == 3 and image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
            
            logger.info(f"成功加载图像: {file_path}, 尺寸: {image.shape}")
            return image, normalized_path
            
        except Exception as e:
            error_msg = f"加载图像失败: {e}"
            logger.error(error_msg)
            return None, error_msg
    
    def save_image(self, image: np.ndarray, file_path: str, quality: int = 85) -> bool:
        """保存图像文件"""
        try:
            # 标准化和清理文件路径
            normalized_path = ChineseEncodingHandler.normalize_chinese_path(file_path)
            
            # 确保文件名安全
            dir_path = os.path.dirname(normalized_path)
            filename = os.path.basename(normalized_path)
            safe_filename = FilenameSanitizer.sanitize_filename(filename)
            safe_path = os.path.join(dir_path, safe_filename)
            
            # 处理文件名冲突
            if os.path.exists(safe_path):
                safe_filename = FilenameSanitizer.handle_filename_conflicts(dir_path, safe_filename)
                safe_path = os.path.join(dir_path, safe_filename)
            
            # 确保目录存在
            if not self.ensure_directory(dir_path):
                return False
            
            # 转换RGB到BGR（如果是彩色图像）
            save_image = image.copy()
            if len(save_image.shape) == 3:
                if save_image.shape[2] == 3:
                    save_image = cv2.cvtColor(save_image, cv2.COLOR_RGB2BGR)
                elif save_image.shape[2] == 4:
                    save_image = cv2.cvtColor(save_image, cv2.COLOR_RGBA2BGRA)
            
            # 检测是否为中文路径
            encoding_result = ChineseEncodingHandler.detect_encoding(safe_path)
            
            # 根据文件扩展名设置保存参数
            ext = Path(safe_path).suffix.lower()
            encode_params = []
            
            if ext in ['.jpg', '.jpeg']:
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
            elif ext == '.png':
                compression = max(0, min(9, (100 - quality) // 10))
                encode_params = [cv2.IMWRITE_PNG_COMPRESSION, compression]
            
            if encoding_result.is_chinese:
                try:
                    # 对于中文路径，使用cv2.imencode然后写入文件
                    success, encoded_img = cv2.imencode(ext, save_image, encode_params)
                    
                    if success:
                        with open(safe_path, 'wb') as f:
                            f.write(encoded_img.tobytes())
                        success = True
                    else:
                        success = False
                        
                except Exception as encode_error:
                    logger.warning(f"中文路径编码保存失败，尝试直接保存: {encode_error}")
                    # 回退到直接保存
                    success = cv2.imwrite(safe_path, save_image, encode_params)
            else:
                # 英文路径直接使用OpenCV保存
                success = cv2.imwrite(safe_path, save_image, encode_params)
            
            if success:
                logger.info(f"成功保存图像: {file_path} -> {safe_path}")
                return True
            else:
                logger.error(f"保存图像失败: {safe_path}")
                return False
                
        except Exception as e:
            logger.error(f"保存图像异常: {e}")
            return False
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的图像格式"""
        return self.SUPPORTED_FORMATS.copy()
    
    def is_image_file(self, file_path: str) -> bool:
        """检查是否为支持的图像文件"""
        try:
            ext = Path(file_path).suffix.lower()
            return ext in self.SUPPORTED_FORMATS
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """获取文件信息"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            path_obj = Path(file_path)
            
            info = {
                'name': path_obj.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': path_obj.suffix.lower(),
                'is_image': self.is_image_file(file_path)
            }
            
            # 如果是图像文件，获取图像尺寸
            if info['is_image']:
                try:
                    # 使用自己的load_image方法以支持中文路径
                    image, _ = self.load_image(file_path)
                    if image is not None:
                        info['width'] = image.shape[1]
                        info['height'] = image.shape[0]
                        info['channels'] = image.shape[2] if len(image.shape) == 3 else 1
                except Exception:
                    pass
            
            return info
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            return None
    
    def ensure_directory(self, dir_path: str) -> bool:
        """确保目录存在"""
        try:
            if not dir_path:
                return True
            
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
            
        except Exception as e:
            logger.error(f"创建目录失败: {e}")
            return False
    
    def get_image_files_in_directory(self, dir_path: str) -> List[str]:
        """获取目录中的所有图像文件"""
        try:
            # 标准化目录路径
            normalized_dir = ChineseEncodingHandler.normalize_chinese_path(dir_path)
            
            if not os.path.exists(normalized_dir):
                return []
            
            image_files = []
            try:
                for file_path in Path(normalized_dir).rglob("*"):
                    if file_path.is_file():
                        file_str = str(file_path)
                        # 标准化文件路径
                        normalized_file = ChineseEncodingHandler.normalize_chinese_path(file_str)
                        
                        if self.is_image_file(normalized_file):
                            image_files.append(normalized_file)
            except Exception as scan_error:
                logger.warning(f"目录扫描部分失败: {scan_error}")
                # 尝试使用os.walk作为备选方案
                try:
                    for root, dirs, files in os.walk(normalized_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            normalized_file = ChineseEncodingHandler.normalize_chinese_path(file_path)
                            if self.is_image_file(normalized_file):
                                image_files.append(normalized_file)
                except Exception as walk_error:
                    logger.error(f"备选扫描方案也失败: {walk_error}")
            
            return sorted(image_files)
            
        except Exception as e:
            logger.error(f"扫描目录失败: {e}")
            return []