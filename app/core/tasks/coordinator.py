"""
任务协调器

协调不同类型的异步任务，避免资源冲突。
"""

import threading
import time
import uuid
import heapq
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from enum import Enum, IntEnum

from .interfaces import TaskHandler, TaskCoordinatorInterface, TaskInfo, TaskStatus, TaskPriority, TaskEventListener


@dataclass
class Task:
    """任务定义"""
    task_id: str
    task_type: str
    priority: TaskPriority
    operation: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    resource_estimate: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    timeout: Optional[float] = None
    
    def __lt__(self, other):
        """优先级队列排序：优先级数值越小越优先，创建时间越早越优先"""
        if self.priority != other.priority:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[Exception] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    resource_allocation_id: Optional[str] = None
    
    @property
    def duration(self) -> float:
        """任务执行时长"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


@dataclass
class QueueStatus:
    """队列状态"""
    pending_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    total_tasks: int = 0
    
    @property
    def completion_rate(self) -> float:
        """完成率"""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100


class TaskCoordinator(TaskCoordinatorInterface):
    """任务协调器
    
    协调不同类型的异步任务，管理资源分配和任务依赖。
    """
    
    def __init__(self, max_workers: int = 4):
        """初始化任务协调器
        
        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
        
        # 任务处理器注册
        self._handlers: Dict[str, TaskHandler] = {}
        self._handlers_lock = threading.RLock()
        
        # 任务队列（优先级队列）
        self._task_queue: List[Task] = []
        self._queue_lock = threading.RLock()
        
        # 任务状态跟踪
        self._tasks: Dict[str, TaskInfo] = {}
        self._task_results: Dict[str, TaskResult] = {}
        self._task_futures: Dict[str, Future] = {}
        self._tasks_lock = threading.RLock()
        
        # 线程池
        self._executor = ThreadPoolExecutor(max_workers=max_workers, 
                                          thread_name_prefix="TaskCoordinator")
        
        # 并发限制
        self._concurrency_limits: Dict[str, int] = {}
        self._running_tasks_by_type: Dict[str, int] = {}
        self._concurrency_lock = threading.RLock()
        
        # 任务依赖管理
        self._dependency_graph: Dict[str, List[str]] = {}  # task_id -> [dependent_task_ids]
        self._reverse_dependencies: Dict[str, List[str]] = {}  # task_id -> [dependency_task_ids]
        
        # 事件监听器
        self._event_listeners: List[TaskEventListener] = []
        self._listeners_lock = threading.RLock()
        
        # 调度线程
        self._scheduling = False
        self._scheduler_thread: Optional[threading.Thread] = None
        self._shutdown = False
        self._start_scheduler()
        
        # 统计信息
        self._stats = QueueStatus()
        self._stats_lock = threading.RLock()
    
    def register_handler(self, handler: TaskHandler) -> bool:
        """
        注册任务处理器
        
        Args:
            handler: 要注册的处理器
            
        Returns:
            bool: 注册是否成功
        """
        try:
            with self._handlers_lock:
                handler_name = handler.handler_name
                if handler_name in self._handlers:
                    return False
                
                # 初始化处理器
                if not handler.initialize():
                    return False
                
                self._handlers[handler_name] = handler
                return True
        except Exception:
            return False
    
    def unregister_handler(self, handler_name: str) -> bool:
        """
        注销任务处理器
        
        Args:
            handler_name: 要注销的处理器名称
            
        Returns:
            bool: 注销是否成功
        """
        try:
            with self._handlers_lock:
                handler = self._handlers.pop(handler_name, None)
                if handler:
                    handler.cleanup()
                    return True
                return False
        except Exception:
            return False
    
    def get_registered_handlers(self) -> List[TaskHandler]:
        """
        获取已注册的处理器列表
        
        Returns:
            List[TaskHandler]: 已注册的处理器列表
        """
        with self._handlers_lock:
            return list(self._handlers.values())
    
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
        try:
            # 查找合适的处理器
            handler = self._find_handler_for_task_type(task_type)
            if not handler:
                return None
            
            # 创建任务信息
            task_id = str(uuid.uuid4())
            task_info = TaskInfo(task_id, task_type, name, priority)
            task_info.add_metadata('config', config)
            
            # 创建任务操作
            def task_operation():
                return handler.execute_task(task_info)
            
            # 创建任务
            task = Task(
                task_id=task_id,
                task_type=task_type,
                priority=priority,
                operation=task_operation,
                resource_estimate=config.get('resource_estimate'),
                dependencies=config.get('dependencies', []),
                timeout=config.get('timeout')
            )
            
            return self._submit_task_internal(task, task_info)
            
        except Exception:
            return None
    
    def _find_handler_for_task_type(self, task_type: str) -> Optional[TaskHandler]:
        """查找支持指定任务类型的处理器"""
        with self._handlers_lock:
            for handler in self._handlers.values():
                if task_type in handler.supported_task_types:
                    return handler
        return None
    
    def _start_scheduler(self):
        """启动任务调度器"""
        if self._scheduling:
            return
        
        self._scheduling = True
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True,
            name="TaskScheduler"
        )
        self._scheduler_thread.start()
    
    def _scheduler_loop(self):
        """调度器循环"""
        while self._scheduling and not self._shutdown:
            try:
                self._process_task_queue()
                time.sleep(0.1)  # 100ms调度间隔
            except Exception as e:
                print(f"任务调度错误: {e}")
                time.sleep(0.1)
    
    def _process_task_queue(self):
        """处理任务队列"""
        with self._queue_lock:
            if not self._task_queue:
                return
            
            # 找到可以执行的任务
            executable_tasks = []
            remaining_tasks = []
            
            for task in self._task_queue:
                if self._can_execute_task(task):
                    executable_tasks.append(task)
                else:
                    remaining_tasks.append(task)
            
            # 更新队列
            self._task_queue = remaining_tasks
            heapq.heapify(self._task_queue)
        
        # 执行可执行的任务
        for task in executable_tasks:
            self._execute_task(task)
    
    def _can_execute_task(self, task: Task) -> bool:
        """检查任务是否可以执行"""
        # 检查依赖是否完成
        if not self._are_dependencies_completed(task.task_id):
            return False
        
        # 检查并发限制
        if not self._check_concurrency_limit(task.task_type):
            return False
        
        return True
    
    def _are_dependencies_completed(self, task_id: str) -> bool:
        """检查任务依赖是否都已完成"""
        dependencies = self._reverse_dependencies.get(task_id, [])
        
        for dep_id in dependencies:
            with self._tasks_lock:
                result = self._task_results.get(dep_id)
                if not result or result.status != TaskStatus.COMPLETED:
                    return False
        
        return True
    
    def _check_concurrency_limit(self, task_type: str) -> bool:
        """检查并发限制"""
        with self._concurrency_lock:
            limit = self._concurrency_limits.get(task_type)
            if limit is None:
                return True
            
            running_count = self._running_tasks_by_type.get(task_type, 0)
            return running_count < limit
    
    def _execute_task(self, task: Task):
        """执行任务"""
        try:
            # 创建任务结果
            task_result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.RUNNING,
                start_time=time.time()
            )
            
            with self._tasks_lock:
                self._task_results[task.task_id] = task_result
                task_info = self._tasks.get(task.task_id)
                if task_info:
                    task_info.set_status(TaskStatus.RUNNING)
            
            # 更新并发计数
            with self._concurrency_lock:
                self._running_tasks_by_type[task.task_type] = \
                    self._running_tasks_by_type.get(task.task_type, 0) + 1
            
            # 更新统计
            with self._stats_lock:
                self._stats.running_tasks += 1
                self._stats.pending_tasks -= 1
            
            # 通知监听器
            self._notify_task_started(task.task_id)
            
            # 提交到线程池执行
            future = self._executor.submit(self._run_task, task)
            
            with self._tasks_lock:
                self._task_futures[task.task_id] = future
            
            # 设置完成回调
            future.add_done_callback(lambda f: self._on_task_complete(task, f))
            
        except Exception as e:
            # 执行失败
            self._handle_task_failure(task, e)
    
    def _run_task(self, task: Task) -> Any:
        """运行任务"""
        try:
            # 检查超时
            if task.timeout:
                start_time = time.time()
            
            # 执行任务
            result = task.operation(*task.args, **task.kwargs)
            
            # 检查是否超时
            if task.timeout and (time.time() - start_time) > task.timeout:
                raise TimeoutError(f"任务 {task.task_id} 执行超时")
            
            return result
            
        except Exception as e:
            raise e
    
    def _on_task_complete(self, task: Task, future: Future):
        """任务完成回调"""
        try:
            result = future.result()
            status = TaskStatus.COMPLETED
            error = None
        except Exception as e:
            result = None
            status = TaskStatus.FAILED
            error = e
        
        # 更新任务结果
        with self._tasks_lock:
            task_result = self._task_results.get(task.task_id)
            if task_result:
                task_result.status = status
                task_result.result = result
                task_result.error = error
                task_result.end_time = time.time()
            
            # 更新任务信息
            task_info = self._tasks.get(task.task_id)
            if task_info:
                task_info.set_status(status, str(error) if error else None)
                task_info.result = result
            
            # 清理future
            self._task_futures.pop(task.task_id, None)
        
        # 更新并发计数
        with self._concurrency_lock:
            current_count = self._running_tasks_by_type.get(task.task_type, 0)
            if current_count > 0:
                self._running_tasks_by_type[task.task_type] = current_count - 1
        
        # 更新统计
        with self._stats_lock:
            self._stats.running_tasks -= 1
            if status == TaskStatus.COMPLETED:
                self._stats.completed_tasks += 1
            else:
                self._stats.failed_tasks += 1
        
        # 通知监听器
        if status == TaskStatus.COMPLETED:
            self._notify_task_completed(task.task_id, result)
        else:
            self._notify_task_failed(task.task_id, error)
        
        # 触发依赖任务的检查
        self._notify_dependents(task.task_id)
    
    def _handle_task_failure(self, task: Task, error: Exception):
        """处理任务失败"""
        task_result = TaskResult(
            task_id=task.task_id,
            status=TaskStatus.FAILED,
            error=error,
            start_time=time.time(),
            end_time=time.time()
        )
        
        with self._tasks_lock:
            self._task_results[task.task_id] = task_result
            task_info = self._tasks.get(task.task_id)
            if task_info:
                task_info.set_status(TaskStatus.FAILED, str(error))
        
        # 更新统计
        with self._stats_lock:
            self._stats.failed_tasks += 1
            self._stats.pending_tasks -= 1
        
        # 通知监听器
        self._notify_task_failed(task.task_id, error)
    
    def _notify_dependents(self, completed_task_id: str):
        """通知依赖任务"""
        dependents = self._dependency_graph.get(completed_task_id, [])
        # 依赖任务会在下次调度循环中被检查
    
    def _submit_task_internal(self, task: Task, task_info: TaskInfo) -> str:
        """内部提交任务实现"""
        # 存储任务
        with self._tasks_lock:
            self._tasks[task.task_id] = task_info
        
        # 处理依赖关系
        for dep_id in task.dependencies:
            if dep_id not in self._dependency_graph:
                self._dependency_graph[dep_id] = []
            self._dependency_graph[dep_id].append(task.task_id)
            
            if task.task_id not in self._reverse_dependencies:
                self._reverse_dependencies[task.task_id] = []
            self._reverse_dependencies[task.task_id].append(dep_id)
        
        # 添加到队列
        with self._queue_lock:
            heapq.heappush(self._task_queue, task)
        
        # 更新统计
        with self._stats_lock:
            self._stats.pending_tasks += 1
            self._stats.total_tasks += 1
        
        # 通知监听器
        self._notify_task_submitted(task_info)
        
        return task.task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 取消是否成功
        """
        try:
            # 检查任务是否存在
            with self._tasks_lock:
                if task_id not in self._tasks:
                    return False
                
                task_info = self._tasks[task_id]
                
                # 检查任务状态
                if task_info.is_finished():
                    return False
                
                # 尝试通过处理器取消任务
                handler = self._find_handler_for_task_type(task_info.task_type)
                if handler:
                    handler.cancel_task(task_id)
                
                # 取消正在运行的任务
                future = self._task_futures.get(task_id)
                if future:
                    future.cancel()
                    self._task_futures.pop(task_id, None)
                
                # 从队列中移除
                with self._queue_lock:
                    self._task_queue = [t for t in self._task_queue if t.task_id != task_id]
                    heapq.heapify(self._task_queue)
                
                # 更新任务状态
                task_info.set_status(TaskStatus.CANCELLED)
                
                # 更新任务结果
                result = self._task_results.get(task_id)
                if not result:
                    result = TaskResult(task_id=task_id, status=TaskStatus.CANCELLED)
                    self._task_results[task_id] = result
                else:
                    result.status = TaskStatus.CANCELLED
                    result.end_time = time.time()
                
                # 更新统计
                with self._stats_lock:
                    if result.status == TaskStatus.RUNNING:
                        self._stats.running_tasks -= 1
                    else:
                        self._stats.pending_tasks -= 1
                    self._stats.cancelled_tasks += 1
                
                # 通知监听器
                self._notify_task_cancelled(task_info)
            
            return True
        except Exception:
            return False
    
    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[TaskInfo]: 任务信息
        """
        with self._tasks_lock:
            return self._tasks.get(task_id)
    
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
        with self._tasks_lock:
            tasks = list(self._tasks.values())
            
            if status_filter:
                tasks = [t for t in tasks if t.status == status_filter]
            
            if task_type_filter:
                tasks = [t for t in tasks if t.task_type == task_type_filter]
            
            return tasks
    
# get_task_statistics 方法已删除 - 简化统计功能
    
    def add_event_listener(self, listener: TaskEventListener):
        """添加事件监听器"""
        with self._listeners_lock:
            if listener not in self._event_listeners:
                self._event_listeners.append(listener)
    
    def remove_event_listener(self, listener: TaskEventListener):
        """移除事件监听器"""
        with self._listeners_lock:
            if listener in self._event_listeners:
                self._event_listeners.remove(listener)
    
    def _notify_task_submitted(self, task_info: TaskInfo):
        """通知任务提交事件"""
        with self._listeners_lock:
            for listener in self._event_listeners:
                try:
                    listener.on_task_submitted(task_info)
                except Exception:
                    pass
    
    def _notify_task_started(self, task_id: str):
        """通知任务开始事件"""
        with self._listeners_lock:
            task_info = self._tasks.get(task_id)
            if task_info:
                for listener in self._event_listeners:
                    try:
                        listener.on_task_started(task_info)
                    except Exception:
                        pass
    
    def _notify_task_completed(self, task_id: str, result: Any):
        """通知任务完成事件"""
        with self._listeners_lock:
            task_info = self._tasks.get(task_id)
            if task_info:
                for listener in self._event_listeners:
                    try:
                        listener.on_task_completed(task_info, result)
                    except Exception:
                        pass
    
    def _notify_task_failed(self, task_id: str, error: Exception):
        """通知任务失败事件"""
        with self._listeners_lock:
            task_info = self._tasks.get(task_id)
            if task_info:
                for listener in self._event_listeners:
                    try:
                        listener.on_task_failed(task_info, error)
                    except Exception:
                        pass
    
    def _notify_task_cancelled(self, task_info: TaskInfo):
        """通知任务取消事件"""
        with self._listeners_lock:
            for listener in self._event_listeners:
                try:
                    listener.on_task_cancelled(task_info)
                except Exception:
                    pass
    
    def set_concurrency_limits(self, task_type: str, max_concurrent: int):
        """设置并发限制
        
        Args:
            task_type: 任务类型
            max_concurrent: 最大并发数
        """
        with self._concurrency_lock:
            self._concurrency_limits[task_type] = max_concurrent
    
    def get_queue_status(self) -> QueueStatus:
        """获取队列状态"""
        with self._stats_lock:
            return QueueStatus(
                pending_tasks=self._stats.pending_tasks,
                running_tasks=self._stats.running_tasks,
                completed_tasks=self._stats.completed_tasks,
                failed_tasks=self._stats.failed_tasks,
                cancelled_tasks=self._stats.cancelled_tasks,
                total_tasks=self._stats.total_tasks
            )
    
    def shutdown(self):
        """关闭任务协调器"""
        self._shutdown = True
        
        # 停止调度器
        self._scheduling = False
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=5.0)
        
        # 取消所有待处理任务
        with self._tasks_lock:
            for task_id in list(self._tasks.keys()):
                self.cancel_task(task_id)
        
        # 关闭线程池
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=True)
        
        # 清理处理器
        with self._handlers_lock:
            for handler in self._handlers.values():
                try:
                    handler.cleanup()
                except Exception:
                    pass
            self._handlers.clear()