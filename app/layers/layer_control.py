"""层级导入控制机制"""
import sys
import importlib.util
from typing import Dict, Set
from enum import Enum


class LayerType(Enum):
    """层级类型"""
    APPLICATION = "application"
    PRESENTATION = "presentation"
    CONTROLLER = "controller"
    BUSINESS = "business"
    INFRASTRUCTURE = "infrastructure"


class LayerImportController:
    """层级导入控制器"""
    
    # 定义允许的依赖关系（下层可以被上层依赖）
    ALLOWED_DEPENDENCIES = {
        LayerType.APPLICATION: {LayerType.PRESENTATION, LayerType.CONTROLLER, LayerType.BUSINESS, LayerType.INFRASTRUCTURE},
        LayerType.PRESENTATION: {LayerType.CONTROLLER, LayerType.BUSINESS, LayerType.INFRASTRUCTURE},
        LayerType.CONTROLLER: {LayerType.BUSINESS, LayerType.INFRASTRUCTURE},
        LayerType.BUSINESS: {LayerType.INFRASTRUCTURE},
        LayerType.INFRASTRUCTURE: set()  # 基础设施层不依赖其他层
    }
    
    def __init__(self):
        self.layer_mapping = self._build_layer_mapping()
    
    def _build_layer_mapping(self) -> Dict[str, LayerType]:
        """构建模块路径到层级的映射"""
        return {
            "app.layers.application": LayerType.APPLICATION,
            "app.layers.presentation": LayerType.PRESENTATION,
            "app.layers.controller": LayerType.CONTROLLER,
            "app.layers.business": LayerType.BUSINESS,
            "app.layers.infrastructure": LayerType.INFRASTRUCTURE,
        }
    
    def get_module_layer(self, module_name: str) -> LayerType:
        """获取模块所属层级"""
        for prefix, layer in self.layer_mapping.items():
            if module_name.startswith(prefix):
                return layer
        return None
    
    def is_import_allowed(self, from_module: str, to_module: str) -> bool:
        """检查导入是否被允许"""
        from_layer = self.get_module_layer(from_module)
        to_layer = self.get_module_layer(to_module)
        
        # 如果任一模块不在分层架构中，允许导入
        if not from_layer or not to_layer:
            return True
        
        # 检查是否违反分层原则
        return to_layer in self.ALLOWED_DEPENDENCIES.get(from_layer, set())
    
    def validate_import(self, from_module: str, to_module: str) -> None:
        """验证导入，如果违反则抛出异常"""
        if not self.is_import_allowed(from_module, to_module):
            from_layer = self.get_module_layer(from_module)
            to_layer = self.get_module_layer(to_module)
            raise ImportError(
                f"架构违反: {from_layer.value}层不能导入{to_layer.value}层 "
                f"({from_module} -> {to_module})"
            )


# 全局控制器实例
_layer_controller = LayerImportController()


def validate_layer_import(from_module: str, to_module: str) -> None:
    """验证层级导入的公共函数"""
    _layer_controller.validate_import(from_module, to_module)