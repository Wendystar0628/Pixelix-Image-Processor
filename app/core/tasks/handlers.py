"""
任务处理器实现

提供基础的任务处理器实现和常用的任务处理器。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
import time
import threading

from .interfaces import TaskHandler, TaskInfo, TaskStatus, TaskPriority


class BaseTaskHandler(TaskHandler):
    """
    基础任务处理器实现
    
    提供任务处理器的基本功能实现。
    """
    
    def __init__(self, handler_name: str, supported_task_types: List[str]):
        self._handler_name = handler_name
        self._supported_task_types = supported_task_types
        self._active_tasks: Dict[str, threading.Event] = {}
        self._tasks_lock = threading.RLock()
        self._initialized = False
    
    @property
    def handler_name(self) -> str:
        """处理器名称"""
        return self._handler_name
    
    @property
    def supported_task_types(self) -> List[str]:
        """支持的任务类型"""
        return self._supported_task_types.copy()
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        初始化任务处理器
        
        Args:
            config: 可选的配置参数
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            self._initialized = True
            return True
        except Exception:
            return False
    
    def cleanup(self) -> None:
        """清理任务处理器"""
        # 取消所有活跃任务
        with self._tasks_lock:
            for task_id, cancel_event in self._active_tasks.items():
                cancel_event.set()
            self._active_tasks.clear()
        
        self._initialized = False
    
    def can_handle_task(self, task_info: TaskInfo) -> bool:
        """
        检查是否可以处理指定任务
        
        Args:
            task_info: 任务信息
            
        Returns:
            bool: 是否可以处理
        """
        return task_info.task_type in self._supported_task_types
    
    def execute_task(self, task_info: TaskInfo, 
                    progress_callback: Optional[Callable[[float], None]] = None,
                    cancel_callback: Optional[Callable[[], bool]] = None) -> Any:
        """
        执行任务
        
        Args:
            task_info: 任务信息
            progress_callback: 进度回调函数
            cancel_callback: 取消检查回调函数
            
        Returns:
            Any: 任务执行结果
        """
        if not self._initialized:
            raise RuntimeError("任务处理器未初始化")
        
        if not self.can_handle_task(task_info):
            raise ValueError(f"不支持的任务类型: {task_info.task_type}")
        
        # 注册活跃任务
        cancel_event = threading.Event()
        with self._tasks_lock:
            self._active_tasks[task_info.task_id] = cancel_event
        
        try:
            # 执行具体任务
            result = self._execute_task_internal(
                task_info, progress_callback, cancel_event
            )
            return result
        finally:
            # 清理活跃任务
            with self._tasks_lock:
                self._active_tasks.pop(task_info.task_id, None)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 取消是否成功
        """
        with self._tasks_lock:
            cancel_event = self._active_tasks.get(task_id)
            if cancel_event:
                cancel_event.set()
                return True
            return False
    
    @abstractmethod
    def _execute_task_internal(self, task_info: TaskInfo, 
                              progress_callback: Optional[Callable[[float], None]],
                              cancel_event: threading.Event) -> Any:
        """
        内部任务执行实现
        
        Args:
            task_info: 任务信息
            progress_callback: 进度回调函数
            cancel_event: 取消事件
            
        Returns:
            Any: 任务执行结果
        """
        pass
    
    def _check_cancelled(self, cancel_event: threading.Event) -> bool:
        """检查任务是否被取消"""
        return cancel_event.is_set()
    
    def _report_progress(self, progress: float, 
                        progress_callback: Optional[Callable[[float], None]]):
        """报告进度"""
        if progress_callback:
            try:
                progress_callback(progress)
            except Exception:
                pass


class SimpleTaskHandler(BaseTaskHandler):
    """
    简单任务处理器
    
    用于处理简单的函数调用任务。
    """
    
    def __init__(self):
        super().__init__("simple_task_handler", ["function_call", "simple_operation"])
    
    def _execute_task_internal(self, task_info: TaskInfo, 
                              progress_callback: Optional[Callable[[float], None]],
                              cancel_event: threading.Event) -> Any:
        """执行简单任务"""
        config = task_info.get_metadata('config', {})
        
        if task_info.task_type == "function_call":
            return self._execute_function_call(config, progress_callback, cancel_event)
        elif task_info.task_type == "simple_operation":
            return self._execute_simple_operation(config, progress_callback, cancel_event)
        else:
            raise ValueError(f"不支持的任务类型: {task_info.task_type}")
    
    def _execute_function_call(self, config: Dict[str, Any], 
                              progress_callback: Optional[Callable[[float], None]],
                              cancel_event: threading.Event) -> Any:
        """执行函数调用"""
        func = config.get('function')
        args = config.get('args', ())
        kwargs = config.get('kwargs', {})
        
        if not callable(func):
            raise ValueError("无效的函数对象")
        
        self._report_progress(0.0, progress_callback)
        
        # 检查取消
        if self._check_cancelled(cancel_event):
            raise InterruptedError("任务已取消")
        
        # 执行函数
        result = func(*args, **kwargs)
        
        self._report_progress(100.0, progress_callback)
        return result
    
    def _execute_simple_operation(self, config: Dict[str, Any], 
                                 progress_callback: Optional[Callable[[float], None]],
                                 cancel_event: threading.Event) -> Any:
        """执行简单操作"""
        operation_type = config.get('operation_type')
        data = config.get('data')
        
        self._report_progress(0.0, progress_callback)
        
        if operation_type == "sleep":
            # 模拟长时间运行的任务
            duration = config.get('duration', 1.0)
            steps = 10
            step_duration = duration / steps
            
            for i in range(steps):
                if self._check_cancelled(cancel_event):
                    raise InterruptedError("任务已取消")
                
                time.sleep(step_duration)
                progress = (i + 1) / steps * 100
                self._report_progress(progress, progress_callback)
            
            return f"睡眠 {duration} 秒完成"
        
        elif operation_type == "data_processing":
            # 模拟数据处理
            if not isinstance(data, list):
                raise ValueError("数据必须是列表")
            
            result = []
            total = len(data)
            
            for i, item in enumerate(data):
                if self._check_cancelled(cancel_event):
                    raise InterruptedError("任务已取消")
                
                # 模拟处理
                processed_item = str(item).upper()
                result.append(processed_item)
                
                progress = (i + 1) / total * 100
                self._report_progress(progress, progress_callback)
            
            return result
        
        else:
            raise ValueError(f"不支持的操作类型: {operation_type}")