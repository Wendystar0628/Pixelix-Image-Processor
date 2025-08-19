"""命令数据模型"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from abc import ABC


@dataclass
class Command(ABC):
    """基础命令类"""
    command_type: str
    parameters: Dict[str, Any]
    source: str
    correlation_id: str


@dataclass
class CommandResult:
    """命令执行结果"""
    success: bool
    result_data: Any
    error_message: Optional[str]
    events_generated: list


@dataclass
class ImageOperationCommand(Command):
    """图像操作命令"""
    operation_type: str
    operation_params: Dict[str, Any]
    target_image: Optional[str] = None


@dataclass
class FileOperationCommand(Command):
    """文件操作命令"""
    operation_type: str  # 'open', 'save', 'load_recent'
    file_path: Optional[str] = None
    save_params: Optional[Dict[str, Any]] = None


@dataclass
class BatchOperationCommand(Command):
    """批处理操作命令"""
    operation_type: str  # 'create_job', 'add_to_pool', 'execute_batch'
    job_name: Optional[str] = None
    file_paths: Optional[list] = None


@dataclass
class LoadImageCommand(FileOperationCommand):
    """加载图像命令"""
    def __init__(self, file_path: str, source: str, correlation_id: str):
        super().__init__(
            command_type="load_image",
            parameters={"file_path": file_path},
            source=source,
            correlation_id=correlation_id,
            operation_type="load",
            file_path=file_path
        )


@dataclass
class SaveImageCommand(FileOperationCommand):
    """保存图像命令"""
    def __init__(self, file_path: str, source: str, correlation_id: str, save_params: Optional[Dict[str, Any]] = None):
        super().__init__(
            command_type="save_image",
            parameters={"file_path": file_path, "save_params": save_params},
            source=source,
            correlation_id=correlation_id,
            operation_type="save",
            file_path=file_path,
            save_params=save_params
        )


@dataclass
class ApplyFilterCommand(ImageOperationCommand):
    """应用滤镜命令"""
    filter_type: str = ""
    
    def __post_init__(self):
        self.command_type = "apply_filter"
        self.operation_type = self.filter_type