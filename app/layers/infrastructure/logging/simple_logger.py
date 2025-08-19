"""简化的日志服务"""
import logging
import sys
from datetime import datetime
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SimpleLogger:
    """简化的日志记录器"""
    
    def __init__(self, name: str = "app", level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志记录器"""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, self.level.value))
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.level.value))
            
            # 简单格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """错误日志"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", **kwargs)
        else:
            self.logger.error(message, **kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """严重错误日志"""
        if exception:
            self.logger.critical(f"{message}: {str(exception)}", **kwargs)
        else:
            self.logger.critical(message, **kwargs)
    
    def log_architecture_violation(self, violation_type: str, source: str, target: str, description: str):
        """记录架构违反"""
        self.warning(f"架构违反 [{violation_type}]: {source} -> {target} - {description}")
    
    def log_event_flow(self, event_type: str, source: str, target: str):
        """记录事件流（调试用）"""
        self.debug(f"事件流: {event_type} from {source} to {target}")


# 全局日志实例
_global_logger = None


def get_logger(name: str = "app", level: LogLevel = LogLevel.INFO) -> SimpleLogger:
    """获取全局日志实例"""
    global _global_logger
    if _global_logger is None:
        _global_logger = SimpleLogger(name, level)
    return _global_logger


def log_info(message: str, **kwargs):
    """快捷信息日志"""
    get_logger().info(message, **kwargs)


def log_error(message: str, exception: Optional[Exception] = None, **kwargs):
    """快捷错误日志"""
    get_logger().error(message, exception, **kwargs)


def log_architecture_violation(violation_type: str, source: str, target: str, description: str):
    """快捷架构违反日志"""
    get_logger().log_architecture_violation(violation_type, source, target, description)