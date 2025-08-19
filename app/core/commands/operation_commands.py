from typing import TYPE_CHECKING, List, Union
from .base_command import BaseCommand
from ..operations.base_operation import ImageOperation

if TYPE_CHECKING:
    from ..managers.state_manager import StateManager
    from ..managers.pipeline_manager import PipelineManager


class AddOperationCommand(BaseCommand):
    """
    添加ImageOperation到操作流水线的命令。
    """

    def __init__(self, operation: ImageOperation, pipeline_manager: 'PipelineManager'):
        self._operation = operation
        self._pipeline_manager = pipeline_manager

    def execute(self):
        """
        执行命令：将操作添加到流水线末尾。
        """
        self._pipeline_manager.operation_pipeline.append(self._operation)

    def undo(self):
        """
        撤销命令：从流水线中移除最后一个操作。
        """
        if self._pipeline_manager.operation_pipeline:
            self._pipeline_manager.operation_pipeline.pop()


class ClearPipelineCommand(BaseCommand):
    """
    清空操作流水线的命令。
    """

    def __init__(self, pipeline_manager: 'PipelineManager'):
        self._pipeline_manager = pipeline_manager
        self._backup_pipeline = []

    def execute(self):
        """
        执行命令：清空操作流水线。
        """
        # 备份当前流水线
        self._backup_pipeline = self._pipeline_manager.operation_pipeline.copy()
        # 清空流水线
        self._pipeline_manager.operation_pipeline.clear()

    def undo(self):
        """
        撤销命令：恢复之前的操作流水线。
        """
        # 恢复备份的流水线
        self._pipeline_manager.operation_pipeline = self._backup_pipeline.copy() 