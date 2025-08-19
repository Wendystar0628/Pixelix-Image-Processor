"""对话框管理接口实现"""

from typing import Any, Optional, Dict, List
from PyQt6.QtWidgets import QMessageBox

from app.core.interfaces import DialogManagerInterface


class DialogImplementation(DialogManagerInterface):
    """对话框管理接口实现
    
    将DialogManager适配为DialogManagerInterface，
    为核心层提供对话框管理能力的接口实现。
    """
    
    def __init__(self, dialog_manager):
        """初始化对话框管理实现
        
        Args:
            dialog_manager: DialogManager实例
        """
        self._dialog_manager = dialog_manager
        self._open_dialogs = {}  # 跟踪打开的对话框
        self._dialog_results = {}  # 存储对话框结果
        self._callbacks = {}  # 对话框回调函数
    
    def show_dialog(self, dialog_type: str, **kwargs) -> Any:
        """显示指定类型的对话框
        
        Args:
            dialog_type: 对话框类型（如 'brightness_contrast', 'threshold', 'export_options'）
            **kwargs: 对话框特定的参数
            
        Returns:
            Any: 对话框实例或结果，具体类型取决于对话框类型
        """
        try:
            # 使用现有的show_dialog方法
            if hasattr(self._dialog_manager, 'show_dialog'):
                dialog = self._dialog_manager.show_dialog(dialog_type)
                if dialog:
                    # 记录打开的对话框
                    dialog_id = f"{dialog_type}_{id(dialog)}"
                    self._open_dialogs[dialog_id] = {
                        'type': dialog_type,
                        'dialog': dialog
                    }
                    
                    # 连接对话框关闭信号
                    if hasattr(dialog, 'finished'):
                        dialog.finished.connect(
                            lambda result, did=dialog_id: self._on_dialog_finished(did, result)
                        )
                    
                    return dialog
            
            return None
            
        except Exception as e:
            print(f"显示对话框失败 [{dialog_type}]: {e}")
            return None
    
    def close_dialog(self, dialog_id: str) -> None:
        """关闭指定的对话框
        
        Args:
            dialog_id: 对话框标识符
        """
        try:
            if dialog_id in self._open_dialogs:
                dialog_info = self._open_dialogs[dialog_id]
                dialog = dialog_info['dialog']
                
                if hasattr(dialog, 'close'):
                    dialog.close()
                elif hasattr(dialog, 'reject'):
                    dialog.reject()
                    
                # 清理记录
                del self._open_dialogs[dialog_id]
                
        except Exception as e:
            print(f"关闭对话框失败 [{dialog_id}]: {e}")
    
    def is_dialog_open(self, dialog_type: str) -> bool:
        """检查指定类型的对话框是否打开
        
        Args:
            dialog_type: 对话框类型
            
        Returns:
            bool: True表示对话框已打开，False表示未打开
        """
        try:
            for dialog_info in self._open_dialogs.values():
                if dialog_info['type'] == dialog_type:
                    dialog = dialog_info['dialog']
                    # 检查对话框是否仍然可见
                    if hasattr(dialog, 'isVisible') and dialog.isVisible():
                        return True
            return False
            
        except Exception as e:
            print(f"检查对话框状态失败 [{dialog_type}]: {e}")
            return False
    
    def get_dialog_result(self, dialog_id: str) -> Optional[Any]:
        """获取对话框的结果
        
        Args:
            dialog_id: 对话框标识符
            
        Returns:
            Any: 对话框的结果数据，如果对话框未完成则返回None
        """
        try:
            return self._dialog_results.get(dialog_id)
        except Exception as e:
            print(f"获取对话框结果失败 [{dialog_id}]: {e}")
            return None
    
    def close_all_dialogs(self) -> None:
        """关闭所有打开的对话框"""
        try:
            # 创建副本以避免在迭代时修改字典
            dialog_ids = list(self._open_dialogs.keys())
            for dialog_id in dialog_ids:
                self.close_dialog(dialog_id)
                
        except Exception as e:
            print(f"关闭所有对话框失败: {e}")
    
    def get_open_dialogs(self) -> List[str]:
        """获取所有打开的对话框列表
        
        Returns:
            list: 打开的对话框类型列表
        """
        try:
            open_types = []
            for dialog_info in self._open_dialogs.values():
                dialog_type = dialog_info['type']
                dialog = dialog_info['dialog']
                # 只返回仍然可见的对话框
                if hasattr(dialog, 'isVisible') and dialog.isVisible():
                    open_types.append(dialog_type)
            return open_types
            
        except Exception as e:
            print(f"获取对话框列表失败: {e}")
            return []
    
    def register_dialog_callback(self, dialog_type: str, callback: callable) -> None:
        """注册对话框回调函数
        
        Args:
            dialog_type: 对话框类型
            callback: 当对话框关闭时调用的回调函数
        """
        try:
            self._callbacks[dialog_type] = callback
        except Exception as e:
            print(f"注册对话框回调失败 [{dialog_type}]: {e}")
    
    def show_message_dialog(self, title: str, message: str, dialog_type: str = 'info') -> Any:
        """显示消息对话框
        
        Args:
            title: 对话框标题
            message: 消息内容
            dialog_type: 消息类型（'info', 'warning', 'error', 'question'）
            
        Returns:
            Any: 用户的选择结果
        """
        try:
            parent = getattr(self._dialog_manager, 'parent', None)
            
            if dialog_type == 'info':
                return QMessageBox.information(parent, title, message)
            elif dialog_type == 'warning':
                return QMessageBox.warning(parent, title, message)
            elif dialog_type == 'error':
                return QMessageBox.critical(parent, title, message)
            elif dialog_type == 'question':
                return QMessageBox.question(parent, title, message)
            else:
                return QMessageBox.information(parent, title, message)
                
        except Exception as e:
            print(f"显示消息对话框失败: {e}")
            return None
    
    def _on_dialog_finished(self, dialog_id: str, result: Any) -> None:
        """对话框完成时的内部处理
        
        Args:
            dialog_id: 对话框标识符
            result: 对话框结果
        """
        try:
            # 存储结果
            self._dialog_results[dialog_id] = result
            
            # 获取对话框类型并调用回调
            if dialog_id in self._open_dialogs:
                dialog_type = self._open_dialogs[dialog_id]['type']
                if dialog_type in self._callbacks:
                    self._callbacks[dialog_type](result)
                
                # 清理记录
                del self._open_dialogs[dialog_id]
                
        except Exception as e:
            print(f"处理对话框完成事件失败 [{dialog_id}]: {e}")
    
    # 额外的便利方法，供UI层使用
    def get_dialog_manager(self):
        """获取原始DialogManager实例
        
        Returns:
            原始的DialogManager实例
        """
        return self._dialog_manager