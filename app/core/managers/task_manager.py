"""
任务管理器模块

该模块定义了负责管理各种后台任务的类。
它将任务的异步执行与业务逻辑分离。
"""

from typing import Dict, Any, Optional, Callable, Protocol
from PyQt6.QtCore import QObject, pyqtSignal, QThread


class TaskWorker(Protocol):
    """定义任务工作器需要实现的接口协议。"""
    task_progress: pyqtSignal
    task_finished: pyqtSignal
    finished: pyqtSignal
    
    def run(self, params: Dict[str, Any]) -> None:
        """执行任务的方法。"""
        ...
        
    def cancel(self) -> None:
        """取消任务的方法。"""
        ...


class TaskManager(QObject):
    """
    任务管理器，负责创建和管理后台线程中的任务执行。
    
    这个类提供了一个通用的基础设施，用于在后台线程中异步执行耗时任务，
    而不会阻塞UI线程。它可以处理任何类型的任务，只要任务的工作器符合
    TaskWorker接口。
    """
    
    # 定义信号
    task_started = pyqtSignal()  # 当任务开始时发出
    task_progress = pyqtSignal(int, int, str)  # 当前进度, 总数, 当前状态消息
    task_finished = pyqtSignal(dict)  # 包含任务结果的字典
    
    def __init__(self):
        """初始化任务管理器。"""
        super().__init__()
        self._processing_thread = None
        self._processing_worker = None
    
    def run_task_in_background(self, worker: QObject, task_params: Dict[str, Any], 
                              start_method: str = "run") -> bool:
        """
        在后台线程中运行任务。
        
        Args:
            worker: 任务工作器对象，必须有task_progress、task_finished和finished信号，
                    并且有一个可以接受task_params的方法（默认为"run"）
            task_params: 任务参数字典，将被传递给worker的执行方法
            start_method: worker用于执行任务的方法名称
            
        Returns:
            bool: 是否成功启动任务
        """
        # 检查是否已经有任务在运行
        if self._processing_thread is not None and self._processing_thread.isRunning():
            print("已有任务正在运行。")
            return False
            
        # 检查worker是否有必要的信号和方法
        if not hasattr(worker, "task_progress") or not hasattr(worker, "task_finished") or not hasattr(worker, "finished"):
            print("工作器缺少必要的信号。")
            return False
            
        if not hasattr(worker, start_method):
            print(f"工作器缺少必要的方法: {start_method}")
            return False
        
        # 发出任务开始信号
        self.task_started.emit()
        
        # 创建工作线程和设置工作器
        self._processing_thread = QThread()
        self._processing_worker = worker
        
        # 将工作器移动到工作线程
        self._processing_worker.moveToThread(self._processing_thread)
        
        # 连接信号和槽
        # 1. 工作器的信号连接到管理器的信号
        getattr(self._processing_worker, "task_progress").connect(self.task_progress)
        getattr(self._processing_worker, "task_finished").connect(self.task_finished)
        
        # 2. 线程启动后开始处理
        # 保存task_params的引用，以避免捕获可能变化的外部变量
        task_params_copy = task_params.copy()
        start_method_copy = start_method
        
        # 使用独立函数代替lambda
        def start_task():
            if self._processing_worker:  # 检查worker是否存在
                # 使用getattr获取方法并调用
                method = getattr(self._processing_worker, start_method_copy)
                method(task_params_copy)
        
        # 连接线程启动信号到任务启动函数
        self._processing_thread.started.connect(start_task)
        
        # 3. 任务完成后清理线程和工作器
        getattr(self._processing_worker, "finished").connect(self._cleanup)
        
        # 启动线程
        self._processing_thread.start()
        return True
    
    def _cleanup(self):
        """清理线程和工作器资源"""
        if self._processing_thread:
            self._processing_thread.quit()
            self._processing_thread.deleteLater()
            
        if self._processing_worker:
            self._processing_worker.deleteLater()
            
        self._processing_thread = None
        self._processing_worker = None
    
    def cancel_task(self) -> None:
        """
        取消当前的任务。
        
        如果当前工作器有cancel方法，则调用它。
        """
        if self._processing_worker and hasattr(self._processing_worker, "cancel"):
            method = getattr(self._processing_worker, "cancel")
            method() 