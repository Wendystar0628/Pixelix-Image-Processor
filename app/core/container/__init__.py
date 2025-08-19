"""
容器模块

提供依赖注入和服务管理功能
"""

from .application_state import ApplicationState, ApplicationStatus

__all__ = [
    'ApplicationState', 
    'ApplicationStatus'
]