# -*- coding: utf-8 -*-
"""
图像池管理模块

包含图像池的存储、管理和相关数据结构。
专门用于批处理功能中的多图像集合管理。
"""

from .image_pool_storage import ImagePoolStorage, ImagePoolData
from .pool_manager import PoolManager

__all__ = ['ImagePoolStorage', 'ImagePoolData', 'PoolManager']