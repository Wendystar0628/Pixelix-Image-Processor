"""对话框管理抽象接口"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List


class DialogManagerInterface(ABC):
    """对话框管理抽象接口
    
    定义对话框管理操作的抽象接口，提供对话框创建、显示、关闭、状态查询等功能。
    核心层通过此接口管理对话框，避免直接依赖具体的对话框管理实现。
    """
    
    @abstractmethod
    def show_dialog(self, dialog_type: str, **kwargs) -> Any:
        """显示指定类型的对话框
        
        Args:
            dialog_type: 对话框类型（如 'brightness_contrast', 'threshold', 'export_options'）
            **kwargs: 对话框特定的参数
            
        Returns:
            Any: 对话框实例或结果，具体类型取决于对话框类型
        """
        pass
    
    @abstractmethod
    def close_dialog(self, dialog_id: str) -> None:
        """关闭指定的对话框
        
        Args:
            dialog_id: 对话框标识符
        """
        pass
    
    @abstractmethod
    def is_dialog_open(self, dialog_type: str) -> bool:
        """检查指定类型的对话框是否打开
        
        Args:
            dialog_type: 对话框类型
            
        Returns:
            bool: True表示对话框已打开，False表示未打开
        """
        pass
    
    @abstractmethod
    def get_dialog_result(self, dialog_id: str) -> Optional[Any]:
        """获取对话框的结果
        
        Args:
            dialog_id: 对话框标识符
            
        Returns:
            Any: 对话框的结果数据，如果对话框未完成则返回None
        """
        pass
    
    @abstractmethod
    def close_all_dialogs(self) -> None:
        """关闭所有打开的对话框"""
        pass
    
    @abstractmethod
    def get_open_dialogs(self) -> List[str]:
        """获取所有打开的对话框列表
        
        Returns:
            list: 打开的对话框类型列表
        """
        pass
    
    @abstractmethod
    def register_dialog_callback(self, dialog_type: str, callback: callable) -> None:
        """注册对话框回调函数
        
        Args:
            dialog_type: 对话框类型
            callback: 当对话框关闭时调用的回调函数
        """
        pass
    
    @abstractmethod
    def show_message_dialog(self, title: str, message: str, dialog_type: str = 'info') -> Any:
        """显示消息对话框
        
        Args:
            title: 对话框标题
            message: 消息内容
            dialog_type: 消息类型（'info', 'warning', 'error', 'question'）
            
        Returns:
            Any: 用户的选择结果
        """
        pass