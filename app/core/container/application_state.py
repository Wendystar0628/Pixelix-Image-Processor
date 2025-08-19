"""
应用状态管理模块
"""

import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class ApplicationStatus(Enum):
    """应用状态枚举"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"
    ERROR = "error"


class ApplicationState:
    """
    应用状态管理器，负责跟踪应用程序生命周期状态
    """
    
    def __init__(self):
        self._status = ApplicationStatus.UNINITIALIZED
        self._error_message: Optional[str] = None
        
    @property
    def status(self) -> ApplicationStatus:
        """获取当前状态"""
        return self._status
    
    @property
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._status == ApplicationStatus.INITIALIZED
    
    @property
    def is_shutting_down(self) -> bool:
        """检查是否正在关闭"""
        return self._status in (ApplicationStatus.SHUTTING_DOWN, ApplicationStatus.SHUTDOWN)
    
    @property
    def error_message(self) -> Optional[str]:
        """获取错误信息"""
        return self._error_message
    
    def set_initializing(self) -> None:
        """设置为初始化中状态"""
        if self._status != ApplicationStatus.UNINITIALIZED:
            logger.warning(f"状态转换警告: {self._status} -> {ApplicationStatus.INITIALIZING}")
        self._status = ApplicationStatus.INITIALIZING
        self._error_message = None
        logger.info("应用状态: 初始化中")
    
    def set_initialized(self) -> None:
        """设置为已初始化状态"""
        if self._status != ApplicationStatus.INITIALIZING:
            logger.warning(f"状态转换警告: {self._status} -> {ApplicationStatus.INITIALIZED}")
        self._status = ApplicationStatus.INITIALIZED
        self._error_message = None
        logger.info("应用状态: 已初始化")
    
    def set_shutting_down(self) -> None:
        """设置为关闭中状态"""
        self._status = ApplicationStatus.SHUTTING_DOWN
        logger.info("应用状态: 关闭中")
    
    def set_shutdown(self) -> None:
        """设置为已关闭状态"""
        self._status = ApplicationStatus.SHUTDOWN
        logger.info("应用状态: 已关闭")
    
    def set_error(self, error_message: str) -> None:
        """设置为错误状态"""
        self._status = ApplicationStatus.ERROR
        self._error_message = error_message
        logger.error(f"应用状态: 错误 - {error_message}")