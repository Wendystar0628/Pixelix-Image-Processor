"""命令模式基础设施"""
import logging
import uuid
from typing import Dict, Callable, Any
from .command_models import Command, CommandResult

logger = logging.getLogger(__name__)


class CommandHandler:
    """命令处理器基类"""
    
    def __init__(self):
        self._handlers: Dict[str, Callable[[Command], CommandResult]] = {}
    
    def execute_command(self, command: Command) -> CommandResult:
        """执行命令"""
        try:
            if command.command_type not in self._handlers:
                return CommandResult(
                    success=False,
                    result_data=None,
                    error_message=f"未找到命令处理器: {command.command_type}",
                    events_generated=[]
                )
            
            handler = self._handlers[command.command_type]
            return handler(command)
            
        except Exception as e:
            logger.error(f"命令执行失败: {e}")
            return CommandResult(
                success=False,
                result_data=None,
                error_message=str(e),
                events_generated=[]
            )
    
    def register_handler(self, command_type: str, handler: Callable[[Command], CommandResult]) -> None:
        """注册命令处理器"""
        self._handlers[command_type] = handler
    
    def unregister_handler(self, command_type: str) -> None:
        """注销命令处理器"""
        if command_type in self._handlers:
            del self._handlers[command_type]
    
    def get_supported_commands(self) -> list:
        """获取支持的命令类型"""
        return list(self._handlers.keys())


class CommandDispatcher:
    """命令分发器"""
    
    def __init__(self):
        self._command_handlers: Dict[str, CommandHandler] = {}
    
    def register_command_handler(self, layer_name: str, handler: CommandHandler) -> None:
        """注册层级命令处理器"""
        self._command_handlers[layer_name] = handler
    
    def dispatch_command(self, command: Command, target_layer: str = None) -> CommandResult:
        """分发命令到指定层"""
        try:
            # 如果没有指定目标层，根据命令类型自动选择
            if not target_layer:
                target_layer = self._determine_target_layer(command)
            
            if target_layer not in self._command_handlers:
                return CommandResult(
                    success=False,
                    result_data=None,
                    error_message=f"未找到目标层处理器: {target_layer}",
                    events_generated=[]
                )
            
            handler = self._command_handlers[target_layer]
            return handler.execute_command(command)
            
        except Exception as e:
            logger.error(f"命令分发失败: {e}")
            return CommandResult(
                success=False,
                result_data=None,
                error_message=str(e),
                events_generated=[]
            )
    
    def _determine_target_layer(self, command: Command) -> str:
        """根据命令类型确定目标层"""
        # 简单的路由规则
        if command.command_type.startswith('load_') or command.command_type.startswith('save_'):
            return 'controller'
        elif command.command_type.startswith('apply_') or command.command_type.startswith('process_'):
            return 'controller'
        elif command.command_type.startswith('batch_'):
            return 'controller'
        else:
            return 'controller'  # 默认路由到控制器层


def generate_correlation_id() -> str:
    """生成关联ID"""
    return str(uuid.uuid4())


# 全局命令分发器实例
_global_dispatcher = None


def get_command_dispatcher() -> CommandDispatcher:
    """获取全局命令分发器实例"""
    global _global_dispatcher
    if _global_dispatcher is None:
        _global_dispatcher = CommandDispatcher()
    return _global_dispatcher