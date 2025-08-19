"""架构违反数据模型"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ViolationType(Enum):
    """违反类型枚举"""
    UPWARD_DEPENDENCY = "upward_dependency"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    CROSS_LAYER_DEPENDENCY = "cross_layer_dependency"
    INTERFACE_VIOLATION = "interface_violation"


class LayerType(Enum):
    """层级类型枚举"""
    APPLICATION = "application"
    PRESENTATION = "presentation"
    CONTROLLER = "controller"
    BUSINESS = "business"
    INFRASTRUCTURE = "infrastructure"
    SHARED = "shared"
    LEGACY = "legacy"  # 旧代码层


@dataclass
class ArchitectureViolation:
    """架构违反记录"""
    violation_type: ViolationType
    source_file: str
    target_file: str
    source_layer: LayerType
    target_layer: LayerType
    line_number: int
    import_statement: str
    severity: str  # 'error', 'warning', 'info'
    description: str
    suggestion: Optional[str] = None


@dataclass
class CircularDependency:
    """循环依赖记录"""
    cycle_path: List[str]
    cycle_length: int
    description: str
    affected_files: List[str]


@dataclass
class InterfaceViolation:
    """接口违反记录"""
    interface_file: str
    implementation_file: str
    missing_methods: List[str]
    extra_methods: List[str]
    description: str


@dataclass
class ArchitectureReport:
    """架构检查报告"""
    violations: List[ArchitectureViolation]
    circular_dependencies: List[CircularDependency]
    interface_violations: List[InterfaceViolation]
    total_files_checked: int
    violation_count: int
    error_count: int
    warning_count: int
    is_compliant: bool