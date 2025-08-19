"""
线程安全并发工具

提供线程安全操作的基础实现和并发相关的工具类。
"""

import threading
from typing import Any, Optional
from abc import ABC, abstractmethod


class ThreadSafeBase(ABC):
    """线程安全基类
    
    为需要线程安全操作的类提供基础实现。
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        self._shutdown = False
        
    def _safe_operation(self, operation, *args, **kwargs) -> Any:
        """执行线程安全操作
        
        Args:
            operation: 要执行的操作函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            操作结果
            
        Raises:
            RuntimeError: 当对象已关闭时
        """
        with self._lock:
            if self._shutdown:
                raise RuntimeError("对象已关闭，无法执行操作")
            return operation(*args, **kwargs)
    
    def is_shutdown(self) -> bool:
        """检查是否已关闭"""
        with self._lock:
            return self._shutdown
    
    @abstractmethod
    def shutdown(self) -> None:
        """关闭对象并释放资源"""
        with self._lock:
            self._shutdown = True