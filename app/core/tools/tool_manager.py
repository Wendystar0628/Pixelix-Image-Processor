import logging
from typing import Dict, Optional, Type, Any

from PyQt6.QtCore import QObject, QPoint, pyqtSignal

from .base_tool import BaseTool
from ..models.tool_state_model import ToolStateModel

logger = logging.getLogger(__name__)


class ToolManager(QObject):
    """
    工具管理器 - 管理工具实例、状态和事件分发
    
    主要功能：
    - 工具注册、激活/停用
    - 工具状态保存和恢复
    - 鼠标/键盘事件分发到活动工具
    - 工具操作完成信号转发
    """
    
    # 工具状态变化信号
    tool_changed = pyqtSignal(str)
    # 工具操作完成信号（新增）
    operation_created = pyqtSignal(object)  # 发送操作对象
    
    def __init__(self):
        """初始化工具管理器"""
        super().__init__()
        
        # 工具实例注册表
        self._tools: Dict[str, BaseTool] = {}
        
        # 工具状态管理（使用ToolStateModel替代原始字典）
        self._active_tool_name: Optional[str] = None
        self._tool_states: Dict[str, ToolStateModel] = {}
        
        logger.debug("ToolManager初始化完成 - 独立状态管理")
        
    def register_tool(self, name: str, tool: BaseTool):
        """
        注册工具实例
        
        Args:
            name: 工具名称
            tool: BaseTool实例
        """
        self._tools[name] = tool
        
        # 连接工具的操作完成信号，实现异步通信
        if hasattr(tool, 'operation_completed'):
            tool.operation_completed.connect(self.operation_created)
        
        # 初始化工具状态模型，提供类型安全的状态管理
        if name not in self._tool_states:
            self._tool_states[name] = ToolStateModel(name)
        
        # 自动恢复工具的历史状态
        tool.set_state(self._tool_states[name].parameters)
        
        logger.debug(f"工具已注册: {name}")
        
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取指定名称的工具"""
        return self._tools.get(name)
        
    def set_active_tool(self, name: str) -> bool:
        """
        设置活动工具，自动处理状态保存和恢复
        
        Args:
            name: 工具名称，空字符串表示取消激活
            
        Returns:
            bool: 是否成功
        """
        if name == self._active_tool_name:
            return True
        
        # 停用当前工具并保存状态
        if self._active_tool_name and self._active_tool_name in self._tools:
            current_tool = self._tools[self._active_tool_name]
            current_tool.deactivate()
            # 自动保存工具状态到ToolStateModel
            self._tool_states[self._active_tool_name].parameters = current_tool.get_state()
        
        # 激活新工具
        if name in self._tools:
            self._tools[name].activate()
            self._active_tool_name = name
            self.tool_changed.emit(name)
            logger.info(f"工具激活: {name}")
            return True
        elif name == "":
            # 取消所有工具的激活状态
            self._active_tool_name = None
            self.tool_changed.emit("")
            return True
        else:
            logger.warning(f"尝试激活未注册的工具: {name}")
            return False
            
    @property
    def active_tool_name(self) -> Optional[str]:
        return self._active_tool_name
    
    @property
    def active_tool(self) -> Optional[BaseTool]:
        if self._active_tool_name and self._active_tool_name in self._tools:
            return self._tools[self._active_tool_name]
        return None
        
    def save_tool_state(self, tool_name: str, state: Dict[str, Any]):
        """保存工具状态"""
        if tool_name not in self._tool_states:
            self._tool_states[tool_name] = ToolStateModel(tool_name)
        self._tool_states[tool_name].parameters = state.copy()
    
    def get_tool_state(self, tool_name: str) -> Dict[str, Any]:
        """获取工具状态"""
        if tool_name in self._tool_states:
            return self._tool_states[tool_name].parameters.copy()
        return {}
    
    def reset_all_tool_state(self):
        """重置所有工具状态"""
        old_tool = self._active_tool_name
        
        # 停用当前工具
        if old_tool and old_tool in self._tools:
            self._tools[old_tool].deactivate()
        
        self._active_tool_name = None
        self._tool_states.clear()
        
        logger.info("所有工具状态已重置")
        
        if old_tool is not None:
            self.tool_changed.emit("")
    
    def save_all_tool_states(self):
        """保存所有工具状态"""
        if self._active_tool_name and self._active_tool_name in self._tools:
            current_tool = self._tools[self._active_tool_name]
            self._tool_states[self._active_tool_name].parameters = current_tool.get_state()
            logger.debug(f"已保存活动工具状态: {self._active_tool_name}")
        
        logger.debug("所有工具状态保存完成")
    
    def restore_all_tool_states(self):
        """恢复所有工具状态"""
        for name, tool in self._tools.items():
            if name in self._tool_states:
                tool.set_state(self._tool_states[name].parameters)
                logger.debug(f"已恢复工具状态: {name}")
        
        logger.debug("所有工具状态恢复完成")
        
    def handle_mouse_press(self, pos: QPoint, button: int, modifiers: int) -> bool:
        """处理鼠标按下事件"""
        if self.active_tool:
            return self.active_tool.mouse_press_event(pos, button, modifiers)
        return False
        
    def handle_mouse_move(self, pos: QPoint, buttons: int, modifiers: int) -> bool:
        """处理鼠标移动事件"""
        if self.active_tool:
            return self.active_tool.mouse_move_event(pos, buttons, modifiers)
        return False
        
    def handle_mouse_release(self, pos: QPoint, button: int, modifiers: int) -> bool:
        """处理鼠标释放事件"""
        if self.active_tool:
            return self.active_tool.mouse_release_event(pos, button, modifiers)
        return False
        
    def handle_key_press(self, key: int, modifiers: int) -> bool:
        """处理键盘按下事件"""
        if self.active_tool:
            return self.active_tool.key_press_event(key, modifiers)
        return False
        
    def handle_key_release(self, key: int, modifiers: int) -> bool:
        """处理键盘释放事件"""
        if self.active_tool:
            return self.active_tool.key_release_event(key, modifiers)
        return False