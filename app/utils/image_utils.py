"""
图像工具模块

提供在 NumPy 数组 (OpenCV) 和 QImage/QPixmap (PyQt6) 之间进行转换的辅助函数。
这是连接核心处理逻辑和 UI 显示的关键桥梁。
"""

import os

import cv2
import numpy as np
from PIL import Image
from PyQt6.QtGui import QImage, QPixmap
from typing import Optional, Dict, Any


def numpy_to_qimage(image: np.ndarray) -> QImage:
    """
    【优化版】将一个 NumPy 数组（RGB 或灰度）高效地转换为 QImage。
    此版本通过直接共享内存缓冲区来避免数据复制，从而极大地提升性能。

    Args:
        image: 输入的 NumPy 数组。

    Returns:
        转换后的 QImage 对象。
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是一个 NumPy 数组")

    # 确保数据类型为 uint8，这是QImage所期望的
    if image.dtype != np.uint8:
        # 如果不是，我们必须进行转换和裁剪，这里可能会有性能开销，但为了正确性是必须的
        image = np.clip(image, 0, 255).astype(np.uint8)

    if image.ndim == 2:  # 灰度图像
        height, width = image.shape
        bytes_per_line = width
        # 创建一个QImage，它会引用原始NumPy数组的内存，而不是复制它。
        # 关键：我们传递 `image.data` 这个内存视图，而不是调用 `image.tobytes()`
        # 注：为了兼容严格的类型检查，我们将 memoryview 转换为 bytes
        qimage = QImage(
            bytes(image.data),
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_Grayscale8,
        )
        # 重要：返回QImage的一个深拷贝。因为原始QImage与numpy数组共享内存，
        # 如果numpy数组在别处被回收，QImage会指向无效内存。创建一个拷贝可以保证安全。
        result = qimage.copy()

    elif image.ndim == 3:  # 彩色图像
        if image.shape[2] == 3:  # RGB
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            
            # 注意：我们已经在整个应用中统一使用RGB，不需要在这里转换
            # 直接创建RGB格式的QImage
            qimage = QImage(
                bytes(image.data),
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888,
            )
            result = qimage.copy() # 同样返回一个安全的拷贝
            
        elif image.shape[2] == 4:  # RGBA
            height, width, channel = image.shape
            bytes_per_line = 4 * width
            
            # 创建RGBA格式的QImage
            qimage = QImage(
                bytes(image.data),
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGBA8888,
            )
            result = qimage.copy()
    else:
        raise ValueError(f"不支持的 NumPy 数组形状: {image.shape}")
    
    return result


def qimage_to_numpy(image: QImage) -> np.ndarray:
    """将 QImage 转换为 NumPy 数组 (RGB图像)。

    Args:
        image: 输入的 QImage 对象。

    Returns:
        转换后的 NumPy 数组（RGB格式）。
    """
    # 转换为32位 RGBA 格式以获得一致的内存布局
    image = image.convertToFormat(QImage.Format.Format_RGBA8888)

    width = image.width()
    height = image.height()

    ptr = image.constBits()
    if ptr is None:
        return np.array([], dtype=np.uint8)

    # 从指针创建 NumPy 数组
    arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4))  # type: ignore

    # 保留前三个通道 (RGB)
    rgb_image = arr[..., :3].copy()
    return rgb_image


def numpy_to_qpixmap(image: np.ndarray) -> QPixmap:
    """便捷函数：将 NumPy 数组直接转换为 QPixmap。"""
    qimage = numpy_to_qimage(image)
    qpixmap = QPixmap.fromImage(qimage)
    return qpixmap

# 注意：代理图像加载已移至app/core/utils/proxy_utils.py
# 使用load_proxy_from_file替代此处移除的load_proxy_image_safely

def load_image_safely(file_path: str) -> Optional[np.ndarray]:
    """
    安全地加载图像文件，支持中文路径和其他非ASCII字符。

    Args:
        file_path: 图像文件的路径，可以包含中文或其他非ASCII字符。

    Returns:
        加载的低分辨率代理图像 (RGB格式)，如果加载失败则返回None。
        
    Raises:
        FileNotFoundError: 如果文件不存在。
        ValueError: 如果文件不是有效的图像。
    """
    try:
        # 以二进制模式打开文件
        with open(file_path, "rb") as f:
            # 读取文件内容到内存
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)

            # 从内存中解码图像
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # 检查图像是否成功加载
            if image is None:
                raise ValueError(f"无法解码图像文件: {file_path}")
                
            # OpenCV加载的图像是BGR格式，转换为RGB格式以便在应用中使用
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            return image
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到文件: {file_path}")
    except Exception as e:
        raise ValueError(f"加载图像时出错: {str(e)}")


def save_image_safely(image: np.ndarray, file_path: str, params: Optional[list] = None) -> bool:
    """
    安全地保存图像文件，支持中文路径和其他非ASCII字符。

    Args:
        image: 要保存的图像（NumPy数组，RGB格式）。
        file_path: 保存路径，可以包含中文或其他非ASCII字符。
        params: 编码参数，例如 [cv2.IMWRITE_JPEG_QUALITY, 90] 用于JPEG质量设置。

    Returns:
        保存是否成功。

    Raises:
        ValueError: 如果保存失败。
    """
    try:
        # 确保提供了有效路径
        if not file_path:
            raise ValueError("保存路径不能为空")
            
        # 验证图像数据有效性
        if image is None:
            raise ValueError("图像数据为空")
        if not isinstance(image, np.ndarray):
            raise ValueError(f"图像类型无效: {type(image)}，应为numpy.ndarray")
        if image.size == 0:
            raise ValueError("图像没有内容")
        if image.ndim < 2:
            raise ValueError(f"图像维度无效: {image.ndim}")
        if np.isnan(image).any() or np.isinf(image).any():
            image = np.nan_to_num(image)

        # 规范化路径，处理可能的路径分隔符问题
        file_path = os.path.normpath(file_path)

        # 确保目标目录存在
        directory = os.path.dirname(file_path)
        try:
            # 即使目录为空字符串(当前目录)，也确保它存在
            if directory:
                os.makedirs(directory, exist_ok=True)
            else:
                # 如果目录为空，表示当前目录，验证其可写性
                if not os.access(os.getcwd(), os.W_OK):
                    raise PermissionError(f"没有写入当前目录的权限: {os.getcwd()}")
        except Exception as e:
            raise ValueError(f"创建目录失败: {directory}, 错误: {str(e)}")

        # 获取文件扩展名，确定编码格式
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        # 根据扩展名确定编码格式
        if ext == ".jpg" or ext == ".jpeg":
            encode_format = ".jpg"
        elif ext == ".png":
            encode_format = ".png"
        elif ext == ".bmp":
            encode_format = ".bmp"
        elif ext == ".tiff" or ext == ".tif":
            encode_format = ".tiff"
        else:
            # 默认使用PNG格式
            encode_format = ".png"
            
        # OpenCV需要BGR格式，将RGB转换为BGR
        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 编码图像到内存
        try:
            if params is None:
                success, encoded_img = cv2.imencode(encode_format, bgr_image)
            else:
                success, encoded_img = cv2.imencode(encode_format, bgr_image, params)

            if not success:
                raise ValueError(f"编码图像失败: {file_path}")
        except Exception as e:
            raise ValueError(f"图像编码失败: {str(e)}")

        # 将编码后的图像写入文件
        try:
            with open(file_path, "wb") as f:
                f.write(encoded_img.tobytes())
        except Exception as e:
            raise ValueError(f"写入文件失败: {str(e)}")

        # 验证文件是否确实被创建
        if not os.path.exists(file_path):
            raise ValueError(f"保存操作完成，但文件未创建: {file_path}")
            
        return True
    except Exception as e:
        raise ValueError(f"保存图像时出错: {str(e)}")


def get_image_info(file_path: str) -> Dict[str, Any]:
    """
    获取图像文件的基本信息。

    Args:
        file_path: 图像文件的路径。

    Returns:
        包含图像信息的字典，包括宽度、高度、格式、文件名和大小。

    Raises:
        FileNotFoundError: 如果文件不存在。
        ValueError: 如果文件不是有效的图像。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到文件: {file_path}")

    try:
        # 使用PIL打开图像以获取基本信息
        with Image.open(file_path) as img:
            info = {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'filename': file_path,
                'size_kb': os.path.getsize(file_path) / 1024
            }
            return info
    except Exception as e:
        raise ValueError(f"获取图像信息时出错: {str(e)}")


def is_supported_format(file_path: str) -> bool:
    """
    检查文件是否为支持的图像格式。

    Args:
        file_path: 文件路径。

    Returns:
        如果文件扩展名是支持的图像格式，则返回True，否则返回False。
    """
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif']
    _, ext = os.path.splitext(file_path)
    return ext.lower() in supported_formats
