from typing import Dict, List, Optional, Any, Type
from PyQt6.QtCore import QObject, pyqtSignal

from ..commands.base_command import BaseCommand
from ..operations.base_operation import ImageOperation


class PipelineManager(QObject):
    """
    操作流水线管理器。
    
    负责管理操作流水线 (operation_pipeline)、命令执行和撤销/重做栈。
    继承自 QObject 以便能够发出信号。
    """
    
    # 当流水线发生变化时发出的信号
    pipeline_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.operation_pipeline: List[ImageOperation] = []
        self._undo_stack: List[BaseCommand] = []
        self._redo_stack: List[BaseCommand] = []
    
    def execute_command(self, command: BaseCommand):
        """
        执行一个命令，修改状态，并管理历史记录。

        Args:
            command (BaseCommand): 要执行的命令对象。
        """
        command.execute()
        self._undo_stack.append(command)
        # 执行新命令后，重做栈需要被清空
        self._redo_stack.clear()
        self.pipeline_changed.emit()

    def undo(self):
        """
        撤销上一个命令。
        """
        if not self._undo_stack:
            return  # 没有可撤销的命令

        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        self.pipeline_changed.emit()

    def redo(self):
        """
        重做上一个被撤销的命令。
        """
        if not self._redo_stack:
            return  # 没有可重做的命令

        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        self.pipeline_changed.emit()
        
    def set_pipeline(self, pipeline: List[ImageOperation]):
        """
        设置当前操作流水线
        
        Args:
            pipeline: 新的操作流水线
        """
        self.operation_pipeline = pipeline
        self.pipeline_changed.emit()
    
    def clone_pipeline(self) -> List[ImageOperation]:
        """
        克隆当前操作流水线
        
        Returns:
            List[ImageOperation]: 克隆后的操作流水线
        """
        cloned_pipeline = []
        
        for op in self.operation_pipeline:
            # 获取操作参数
            params = op.get_params()
            
            # 创建相同类型的新操作
            op_class = op.__class__
            cloned_op = op_class(**params)
            
            cloned_pipeline.append(cloned_op)
            
        return cloned_pipeline
    
    def clear_pipeline(self):
        """
        清空当前操作流水线
        """
        self.operation_pipeline = []
        self.pipeline_changed.emit()
        
    def get_operation_params(self, op_id: str) -> Optional[Dict[str, Any]]:
        """
        从操作历史中获取指定操作的最新参数。

        它会从后往前搜索操作流水线，返回第一个匹配的操作的参数。
        这允许对话框恢复用户上次使用的设置。

        Args:
            op_id: 操作的唯一标识符 (例如 "brightness_contrast").

        Returns:
            一个包含参数的字典，如果未找到则返回 None。
        """
        # 从后往前遍历操作流水线
        for operation in reversed(self.operation_pipeline):
            # 获取操作类型并与op_id比较
            op_type = operation.__class__.__name__
            if op_type.endswith("Op"):
                op_type = op_type[:-2].replace("_", "").lower()
            
            # 规范化op_id以进行比较
            normalized_op_id = op_id.replace("_", "").lower()

            if op_type == normalized_op_id:
                return operation.get_params()
        
        return None
    
    def can_undo(self) -> bool:
        """
        检查是否可以执行撤销操作
        
        Returns:
            bool: 如果撤销栈不为空则返回True
        """
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """
        检查是否可以执行重做操作
        
        Returns:
            bool: 如果重做栈不为空则返回True
        """
        return len(self._redo_stack) > 0
    
    def get_undo_stack_size(self) -> int:
        """
        获取撤销栈的大小
        
        Returns:
            int: 撤销栈中的命令数量
        """
        return len(self._undo_stack)
    
    def get_redo_stack_size(self) -> int:
        """
        获取重做栈的大小
        
        Returns:
            int: 重做栈中的命令数量
        """
        return len(self._redo_stack)
    
    def add_operation(self, operation: ImageOperation):
        """
        直接添加操作到流水线（用于工具系统）
        
        Args:
            operation: 要添加的图像操作
        """
        self.operation_pipeline.append(operation)
        # 清空重做栈，因为添加了新操作
        self._redo_stack.clear()
        self.pipeline_changed.emit()

    def reset(self):
        """
        统一的重置方法
        
        重置操作流水线、撤销栈和重做栈，用于消除StateManager中的代码重复
        """
        # 清空操作流水线
        self.operation_pipeline.clear()
        
        # 清空撤销和重做栈
        self._undo_stack.clear()
        self._redo_stack.clear()
        
        # 发出变化信号
        self.pipeline_changed.emit()
    
    def apply_pipeline(self, image) -> Any:
        """
        应用处理管道到图像
        
        Args:
            image: 输入图像
            
        Returns:
            处理后的图像
        """
        if not self.operation_pipeline:
            return image
            
        result = image
        for operation in self.operation_pipeline:
            try:
                result = operation.apply(result)
            except Exception as e:
                print(f"应用操作 {operation.__class__.__name__} 失败: {e}")
                continue
        
        return result 