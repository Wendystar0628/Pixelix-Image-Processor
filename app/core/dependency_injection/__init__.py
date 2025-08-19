"""
依赖注入模块

提供依赖注入容器和服务构建器，实现控制反转。
"""


from .service_builder import ServiceBuilder

__all__ = [
    'ServiceBuilder'
]