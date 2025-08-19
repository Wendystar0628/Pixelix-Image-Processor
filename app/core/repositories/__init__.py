# -*- coding: utf-8 -*-
"""
仓库模块

实现仓库模式，负责数据存储和访问。
仓库层提供统一的数据访问接口，隔离数据存储的具体实现。
"""

from .image_repository import ImageRepository

__all__ = ['ImageRepository']