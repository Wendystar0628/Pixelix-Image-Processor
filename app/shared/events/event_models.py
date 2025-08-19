"""事件数据模型"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from abc import ABC


@dataclass
class Event(ABC):
    """基础事件类"""
    event_type: str
    source_layer: str
    target_layer: str
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: str


@dataclass
class StateChangeEvent(Event):
    """状态变化事件"""
    old_state: Optional[Dict[str, Any]]
    new_state: Dict[str, Any]
    change_reason: str


@dataclass
class UserActionEvent(Event):
    """用户操作事件"""
    action_type: str
    user_input: Dict[str, Any]
    context: Dict[str, Any]


@dataclass
class ImageProcessedEvent(Event):
    """图像处理完成事件"""
    image_path: str
    operation_type: str
    processing_time: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class FileOperationEvent(Event):
    """文件操作事件"""
    operation_type: str  # 'open', 'save', 'load'
    file_path: str
    success: bool
    error_message: Optional[str] = None