"""
任务处理核心接口定义

定义任务处理系统的核心抽象接口，支持可扩展的任务处理器架构。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, Generic, TypeVar
from enum import Enum
import threading
import uuid
from datetime import datetime


T = TypeVar('T')


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class TaskInfo:
    """
    任务信息类
    
    包含任务的基本信息和状态。
    """
    
    def __init__(self, task_id: str, task_type: str, name: str, 
                 priority: TaskPriority = TaskPriority.NORMAL):
        self.task_id = task_id
        self.task_type = task_type
        self.name = name
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.progress = 0.0
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.result: Optional[Any] = None
        self.lock = threading.RLock()
        self.dependencies: List[str] = []
        self.tags: List[str] = []
    
    def set_status(self, status: TaskStatus, error_message: Optional[str] = None) -> None:
        """设置任务状态"""
        with self.lock:
            old_status = self.status
            self.status = status
            
            if status == TaskStatus.RUNNING and old_status == TaskStatus.PENDING:
                self.started_at = datetime.now()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                self.completed_at = datetime.now()
            
            if error_message:
                self.error_message = error_message
    
    def set_progress(self, progress: float) -> None:
        """设置任务进度"""
        with self.lock:
            self.progress = max(0.0, min(100.0, progress))
    
    def add_metadata(self, key: str, value: Any) -> None:
        """添加元数据"""
        with self.lock:
            self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        with self.lock:
            return self.metadata.get(key, default)
    
    def add_dependency(self, task_id: str) -> None:
        """添加依赖任务"""
        with self.lock:
            if task_id not in self.dependencies:
                self.dependencies.append(task_id)
    
    def add_tag(self, tag: str) -> None:
        """添加标签"""
        with self.lock:
            if tag not in self.tags:
                self.tags.append(tag)
    
    def get_duration(self) -> Optional[float]:
        """获取任务执行时长（秒）"""
        with self.lock:
            if self.started_at and self.completed_at:
                return (self.completed_at - self.started_at).total_seconds()
            elif self.started_at:
                return (datetime.now() - self.started_at).total_seconds()
            return None
    
    def is_finished(self) -> bool:
        """检查任务是否已完成"""
        with self.lock:
            return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        with self.lock:
            return {
                'task_id': self.task_id,
                'task_type': self.task_type,
                'name': self.name,
                'priority': self.priority.value,
                'status': self.status.value,
                'progress': self.progress,
                'metadata': self.metadata.copy(),
                'created_at': self.created_at.isoformat(),
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'error_message': self.error_message,
                'dependencies': self.dependencies.copy(),
                'tags': self.tags.copy(),
                'duration': self.get_duration()
            }


class TaskHandler(ABC):
    """
    任务处理器抽象基类
    
    定义了任务处理器的标准接口，允许不同类型的任务处理器
    实现统一的任务处理接口。
    """
    
    @property
    @abstractmethod
    def handler_name(self) -> str:
        """
        处理器名称
        
        Returns:
            str: 处理器的唯一标识名称
        """
        pass
    
    @property
    @abstractmethod
    def supported_task_types(self) -> List[str]:
        """
        支持的任务类型
        
        Returns:
            List[str]: 支持的任务类型列表
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        初始化任务处理器
        
        Args:
            config: 可选的配置参数
            
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        清理任务处理器
        """
        pass
    
    @abstractmethod
    def can_handle_task(self, task_info: TaskInfo) -> bool:
        """
        检查是否可以处理指定任务
        
        Args:
            task_info: 任务信息
            
        Returns:
            bool: 是否可以处理
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 取消是否成功
        """
        pass
    
    def validate_task_config(self, config: Dict[str, Any]) -> bool:
        """
        验证任务配置
        
        Args:
            config: 任务配置
            
        Returns:
            bool: 配置是否有效
        """
        return True
    
    def get_handler_info(self) -> Dict[str, Any]:
        """
        获取处理器信息
        
        Returns:
            Dict[str, Any]: 处理器信息
        """
        return {
            'handler_name': self.handler_name,
            'supported_task_types': self.supported_task_types,
            'version': getattr(self, 'version', '1.0.0'),
            'description': getattr(self, 'description', ''),
            'max_concurrent_tasks': getattr(self, 'max_concurrent_tasks', 1)
        }
    
    def supports_task_type(self, task_type: str) -> bool:
        """
        检查是否支持指定的任务类型
        
        Args:
            task_type: 任务类型
            
        Returns:
            bool: 是否支持
        """
        return task_type in self.supported_task_types
    
    def get_task_metadata_schema(self, task_type: str) -> Optional[Dict[str, Any]]:
        """
        获取任务元数据模式
        
        Args:
            task_type: 任务类型
            
        Returns:
            Optional[Dict[str, Any]]: 元数据模式，不支持时返回None
        """
        return None


class TaskCoordinatorInterface(ABC):
    """
    任务协调器接口
    
    定义了任务协调器的核心功能接口。
    """
    
    @abstractmethod
    def register_handler(self, handler: TaskHandler) -> bool:
        """
        注册任务处理器
        
        Args:
            handler: 要注册的处理器
            
        Returns:
            bool: 注册是否成功
        """
        pass
    
    @abstractmethod
    def unregister_handler(self, handler_name: str) -> bool:
        """
        注销任务处理器
        
        Args:
            handler_name: 要注销的处理器名称
            
        Returns:
            bool: 注销是否成功
        """
        pass
    
    @abstractmethod
    def get_registered_handlers(self) -> List[TaskHandler]:
        """
        获取已注册的处理器列表
        
        Returns:
            List[TaskHandler]: 已注册的处理器列表
        """
        pass
    
    @abstractmethod
    def submit_task(self, task_type: str, name: str, 
                   config: Dict[str, Any], 
                   priority: TaskPriority = TaskPriority.NORMAL) -> Optional[str]:
        """
        提交任务
        
        Args:
            task_type: 任务类型
            name: 任务名称
            config: 任务配置
            priority: 任务优先级
            
        Returns:
            Optional[str]: 任务ID，提交失败时返回None
        """
        pass
    
    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 取消是否成功
        """
        pass
    
    @abstractmethod
    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[TaskInfo]: 任务信息
        """
        pass
    
    @abstractmethod
    def list_tasks(self, status_filter: Optional[TaskStatus] = None,
                  task_type_filter: Optional[str] = None) -> List[TaskInfo]:
        """
        列出任务
        
        Args:
            status_filter: 可选的状态过滤
            task_type_filter: 可选的任务类型过滤
            
        Returns:
            List[TaskInfo]: 任务信息列表
        """
        pass
    
# get_task_statistics 抽象方法已删除 - 简化统计功能
    
    def pause_task(self, task_id: str) -> bool:
        """
        暂停任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 暂停是否成功
        """
        return False
    
    def resume_task(self, task_id: str) -> bool:
        """
        恢复任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 恢复是否成功
        """
        return False
    
    def cleanup_finished_tasks(self, max_age_hours: int = 24) -> int:
        """
        清理已完成的任务
        
        Args:
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            int: 清理的任务数量
        """
        return 0


class TaskEventListener(ABC):
    """
    任务事件监听器接口
    """
    
    @abstractmethod
    def on_task_submitted(self, task_info: TaskInfo) -> None:
        """
        任务提交事件
        
        Args:
            task_info: 任务信息
        """
        pass
    
    @abstractmethod
    def on_task_started(self, task_info: TaskInfo) -> None:
        """
        任务开始事件
        
        Args:
            task_info: 任务信息
        """
        pass
    
    @abstractmethod
    def on_task_progress(self, task_id: str, progress: float) -> None:
        """
        任务进度更新事件
        
        Args:
            task_id: 任务ID
            progress: 进度百分比
        """
        pass
    
    @abstractmethod
    def on_task_completed(self, task_info: TaskInfo, result: Any) -> None:
        """
        任务完成事件
        
        Args:
            task_info: 任务信息
            result: 任务结果
        """
        pass
    
    @abstractmethod
    def on_task_failed(self, task_info: TaskInfo, error: Exception) -> None:
        """
        任务失败事件
        
        Args:
            task_info: 任务信息
            error: 错误信息
        """
        pass
    
    @abstractmethod
    def on_task_cancelled(self, task_info: TaskInfo) -> None:
        """
        任务取消事件
        
        Args:
            task_info: 任务信息
        """
        pass


class TaskQueue(ABC, Generic[T]):
    """
    任务队列抽象基类
    """
    
    @abstractmethod
    def put(self, item: T, priority: TaskPriority = TaskPriority.NORMAL) -> None:
        """
        添加任务到队列
        
        Args:
            item: 任务项
            priority: 优先级
        """
        pass
    
    @abstractmethod
    def get(self, timeout: Optional[float] = None) -> Optional[T]:
        """
        从队列获取任务
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            Optional[T]: 任务项，超时时返回None
        """
        pass
    
    @abstractmethod
    def empty(self) -> bool:
        """
        检查队列是否为空
        
        Returns:
            bool: 是否为空
        """
        pass
    
    @abstractmethod
    def size(self) -> int:
        """
        获取队列大小
        
        Returns:
            int: 队列大小
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        清空队列
        """
        pass


class TaskExecutor(ABC):
    """
    任务执行器抽象基类
    """
    
    @abstractmethod
    def start(self) -> None:
        """
        启动执行器
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        停止执行器
        """
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """
        检查执行器是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        pass
    
    @abstractmethod
    def get_active_task_count(self) -> int:
        """
        获取活跃任务数量
        
        Returns:
            int: 活跃任务数量
        """
        pass
    
    @abstractmethod
    def get_max_concurrent_tasks(self) -> int:
        """
        获取最大并发任务数
        
        Returns:
            int: 最大并发任务数
        """
        pass
    
    @abstractmethod
    def set_max_concurrent_tasks(self, max_tasks: int) -> None:
        """
        设置最大并发任务数
        
        Args:
            max_tasks: 最大并发任务数
        """
        pass