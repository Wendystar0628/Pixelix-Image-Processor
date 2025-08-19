# 渲染引擎状态管理代码文件组织规范

## 概述

本文档为渲染引擎状态管理功能的实现提供详细的文件结构规范和代码组织指导，确保新增功能与现有架构保持一致，代码结构清晰、可维护且具有良好的扩展性。

## 核心原则

### 1. 集成一致性原则
- 新增组件必须与现有StateManager架构保持一致
- 遵循现有的分层架构和模块化原则
- 保持与现有命名约定和代码风格的统一

### 2. 单一职责原则
- 每个文件专注于一个特定的引擎管理功能
- 避免在单个文件中混合多种职责
- 引擎管理相关的功能应集中在专门的模块中

### 3. 可扩展性原则
- 为未来新渲染引擎的添加预留接口
- 支持插件式的引擎扩展机制
- 保持向前兼容性

## 项目文件结构规范

### 核心引擎管理模块结构

```
app/core/managers/
├── state_manager.py              # 现有StateManager（需要扩展）
├── rendering_engine/             # 新增引擎管理模块
│   ├── __init__.py              # 模块导出和版本信息
│   ├── rendering_engine_manager.py     # 主引擎管理器（400-500行）
│   ├── engine_state_controller.py      # 引擎状态控制器（300-400行）
│   ├── engine_capability_detector.py   # 引擎能力检测器（350-450行）
│   ├── engine_config_persistence.py    # 配置持久化管理（250-350行）
│   ├── engine_health_monitor.py        # 引擎健康监控（200-300行）
│   └── engine_performance_monitor.py   # 性能监控器（200-300行）
└── [其他现有管理器...]
```

### 数据模型和接口结构

```
app/core/models/
├── rendering_engine/             # 引擎相关数据模型
│   ├── __init__.py
│   ├── engine_state_models.py          # 引擎状态数据模型（200-300行）
│   ├── engine_capability_models.py     # 引擎能力数据模型（150-250行）
│   ├── engine_config_models.py         # 引擎配置数据模型（150-250行）
│   └── engine_event_models.py          # 引擎事件数据模型（100-200行）
└── [其他现有模型...]

app/core/interfaces/
├── __init__.py
├── rendering_engine_interface.py       # 引擎接口定义（200-300行）
├── engine_plugin_interface.py          # 插件接口定义（150-250行）
└── engine_capability_interface.py      # 能力检测接口（100-200行）
```

### 异常处理和监控结构

```
app/core/exceptions/
├── __init__.py
├── rendering_engine_exceptions.py      # 引擎相关异常（150-250行）
└── [其他现有异常...]

app/core/monitoring/
├── __init__.py
├── performance_monitor.py              # 现有性能监控器
├── engine_monitoring/                  # 新增引擎监控模块
│   ├── __init__.py
│   ├── engine_metrics_collector.py     # 指标收集器（250-350行）
│   ├── engine_alert_manager.py         # 告警管理器（200-300行）
│   └── engine_health_checker.py        # 健康检查器（200-300行）
└── [其他监控组件...]
```

### 服务和工具结构

```
app/core/services/
├── __init__.py
├── rendering_engine_detector.py        # 现有引擎检测器（需要扩展）
├── engine_services/                    # 新增引擎服务模块
│   ├── __init__.py
│   ├── engine_registry_service.py      # 引擎注册服务（200-300行）
│   ├── engine_lifecycle_service.py     # 引擎生命周期服务（250-350行）
│   └── engine_validation_service.py    # 引擎验证服务（200-300行）
└── [其他现有服务...]

app/core/utils/
├── __init__.py
├── engine_utils/                       # 引擎工具模块
│   ├── __init__.py
│   ├── engine_discovery.py             # 引擎发现工具（150-250行）
│   ├── engine_compatibility.py         # 兼容性检查工具（150-250行）
│   └── engine_migration.py             # 配置迁移工具（200-300行）
└── [其他现有工具...]
```

## 文件命名规范

### 1. 模块文件命名

#### 主要组件文件
- `rendering_engine_manager.py` - 主管理器，使用完整描述性名称
- `engine_state_controller.py` - 状态控制器，简洁且明确
- `engine_capability_detector.py` - 能力检测器，突出功能特性

#### 数据模型文件
- `engine_state_models.py` - 状态相关模型
- `engine_capability_models.py` - 能力相关模型
- `engine_config_models.py` - 配置相关模型

#### 接口定义文件
- `rendering_engine_interface.py` - 主要引擎接口
- `engine_plugin_interface.py` - 插件扩展接口
- `engine_capability_interface.py` - 能力检测接口

### 2. 类和函数命名

#### 类命名规范
```python
# 主要管理器类
class RenderingEngineManager(QObject):
    """渲染引擎管理器"""

# 状态控制类
class EngineStateController(QObject):
    """引擎状态控制器"""

# 数据模型类
@dataclass
class EngineState:
    """引擎状态数据模型"""

# 异常类
class EngineNotAvailableError(Exception):
    """引擎不可用异常"""
```

#### 方法命名规范
```python
# 获取方法
def get_current_engine(self) -> str:
def get_available_engines(self) -> List[str]:
def get_engine_capability(self, engine_name: str) -> Dict:

# 设置方法
def set_current_engine(self, engine_name: str) -> bool:
def set_engine_preference(self, preference: Dict) -> None:

# 检查方法
def is_engine_available(self, engine_name: str) -> bool:
def is_switch_in_progress(self) -> bool:

# 操作方法
def switch_engine(self, target_engine: str) -> bool:
def refresh_capabilities(self) -> Dict:
def validate_engine(self, engine_name: str) -> bool:
```

## 代码组织规范

### 1. 文件内部结构

#### 主管理器文件结构
```python
"""
渲染引擎管理器模块

提供统一的渲染引擎状态管理功能，集成到StateManager中。
支持引擎切换、能力检测、配置持久化等核心功能。
"""

# 标准库导入
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# 第三方库导入
from PyQt6.QtCore import QObject, pyqtSignal

# 项目内部导入 - 按层次排序
from app.config import get_config_manager
from app.core.models.rendering_engine import EngineState, EngineCapability
from app.core.exceptions.rendering_engine_exceptions import (
    EngineNotAvailableError,
    EngineSwitchTimeoutError
)
from app.core.interfaces.rendering_engine_interface import RenderingEngineInterface

# 常量定义
DEFAULT_ENGINE = "matplotlib"
SWITCH_TIMEOUT = 5000  # milliseconds
CAPABILITY_CACHE_TIMEOUT = 300  # seconds

# 类型别名
EngineDict = Dict[str, Any]
CapabilityDict = Dict[str, EngineCapability]


class RenderingEngineManager(QObject):
    """
    渲染引擎统一管理器
    
    作为StateManager的子模块，提供统一的引擎状态管理功能。
    支持引擎切换、能力检测、配置持久化等。
    
    Attributes:
        current_engine: 当前激活的引擎名称
        available_engines: 可用引擎列表
        
    Signals:
        engine_changed: 引擎切换完成信号 (old_engine, new_engine)
        engine_status_changed: 引擎状态变化信号 (engine, status)
        capability_detected: 能力检测完成信号 (capabilities)
    """
    
    # 信号定义
    engine_changed = pyqtSignal(str, str)
    engine_status_changed = pyqtSignal(str, str)
    capability_detected = pyqtSignal(dict)
    
    def __init__(self, config_manager):
        """初始化引擎管理器"""
        super().__init__()
        # 初始化代码...
    
    # 公共接口方法
    def get_current_engine(self) -> str:
        """获取当前引擎"""
        pass
    
    def set_current_engine(self, engine_name: str) -> bool:
        """设置当前引擎"""
        pass
    
    # 私有辅助方法
    def _initialize_components(self):
        """初始化子组件"""
        pass
    
    def _setup_connections(self):
        """设置信号连接"""
        pass
```

### 2. 模块初始化文件

#### __init__.py 结构规范
```python
"""
渲染引擎管理模块

提供统一的渲染引擎状态管理功能，包括：
- 引擎状态控制和切换
- 引擎能力检测和监控
- 配置持久化和迁移
- 性能监控和健康检查
"""

# 主要公共接口
from .rendering_engine_manager import RenderingEngineManager
from .engine_state_controller import EngineStateController
from .engine_capability_detector import EngineCapabilityDetector

# 数据模型
from ..models.rendering_engine import (
    EngineState,
    EngineCapability,
    EngineSwitchEvent,
    EngineConfig
)

# 异常类
from ..exceptions.rendering_engine_exceptions import (
    EngineError,
    EngineNotAvailableError,
    EngineSwitchTimeoutError
)

# 主要导出类
__all__ = [
    # 核心管理器
    'RenderingEngineManager',
    'EngineStateController',
    'EngineCapabilityDetector',
    
    # 数据模型
    'EngineState',
    'EngineCapability',
    'EngineSwitchEvent',
    'EngineConfig',
    
    # 异常类
    'EngineError',
    'EngineNotAvailableError',
    'EngineSwitchTimeoutError'
]

# 版本信息
__version__ = '1.0.0'
__author__ = 'Digital Image Processing Team'

# 模块配置
DEFAULT_CONFIG = {
    'preferred_engine': 'matplotlib',
    'auto_fallback': True,
    'switch_timeout': 5000,
    'capability_cache_timeout': 300
}
```

## 依赖管理规范

### 1. 导入顺序和分组

```python
# 1. 标准库导入（按字母顺序）
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union

# 2. 第三方库导入（按重要性排序）
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import numpy as np

# 3. 项目内部导入（按依赖层次从低到高）
# 3.1 配置和常量
from app.config import get_config_manager
from app.core.constants import ENGINE_TYPES, DEFAULT_SETTINGS

# 3.2 基础模型和异常
from app.core.models.rendering_engine import EngineState, EngineCapability
from app.core.exceptions.rendering_engine_exceptions import EngineError

# 3.3 接口和抽象类
from app.core.interfaces.rendering_engine_interface import RenderingEngineInterface

# 3.4 服务和工具
from app.core.services.rendering_engine_detector import RenderingEngineDetector
from app.core.utils.engine_utils import EngineDiscovery

# 3.5 现有管理器和组件（如果需要）
from ..state_manager import get_state_manager
```

### 2. 循环依赖避免策略

#### 使用接口解耦
```python
# ❌ 错误：直接依赖可能导致循环
from app.core.managers.state_manager import StateManager

class RenderingEngineManager:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager

# ✅ 正确：使用接口或延迟导入
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.managers.state_manager import StateManager

class RenderingEngineManager:
    def __init__(self, state_manager: 'StateManager'):
        self.state_manager = state_manager
        
    def notify_state_change(self):
        # 延迟导入避免循环依赖
        from app.core.managers.state_manager import get_state_manager
        state_manager = get_state_manager()
        state_manager.notify()
```

#### 使用事件/信号解耦
```python
# 使用信号机制避免直接依赖
class RenderingEngineManager(QObject):
    # 定义信号而不是直接调用其他组件
    engine_changed = pyqtSignal(str, str)
    
    def switch_engine(self, target: str):
        # 发信号通知，而不是直接调用
        self.engine_changed.emit(self.current_engine, target)
```

## 测试文件组织

### 1. 测试文件结构

```
tests/
├── unit/
│   ├── core/
│   │   ├── managers/
│   │   │   ├── rendering_engine/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_rendering_engine_manager.py
│   │   │   │   ├── test_engine_state_controller.py
│   │   │   │   ├── test_engine_capability_detector.py
│   │   │   │   └── test_engine_config_persistence.py
│   │   │   └── test_state_manager_integration.py
│   │   ├── models/
│   │   │   └── test_rendering_engine_models.py
│   │   └── services/
│   │       └── test_engine_services.py
│   └── fixtures/
│       ├── engine_configs/
│       └── mock_engines/
├── integration/
│   ├── test_engine_state_management.py
│   ├── test_engine_switching_workflow.py
│   └── test_state_manager_engine_integration.py
└── performance/
    ├── test_engine_switch_performance.py
    └── test_capability_detection_performance.py
```

### 2. 测试文件命名规范

- 测试文件以 `test_` 前缀命名
- 测试类以 `Test` 前缀命名
- 测试方法以 `test_` 前缀命名
- 测试文件名对应被测试的模块名

```python
# test_rendering_engine_manager.py
class TestRenderingEngineManager:
    """RenderingEngineManager的单元测试"""
    
    def test_get_current_engine(self):
        """测试获取当前引擎功能"""
        pass
    
    def test_set_current_engine_success(self):
        """测试成功切换引擎"""
        pass
    
    def test_set_current_engine_failure(self):
        """测试引擎切换失败处理"""
        pass
```

## 配置和常量管理

### 1. 配置文件结构

```python
# app/core/constants/rendering_engine_constants.py
"""引擎管理相关常量定义"""

# 引擎类型常量
ENGINE_TYPES = {
    'matplotlib': 'Matplotlib (CPU)',
    'pyqtgraph': 'PyQtGraph (GPU)',
}

# 引擎状态常量
ENGINE_STATUS = {
    'AVAILABLE': 'available',
    'UNAVAILABLE': 'unavailable',
    'ERROR': 'error',
    'SWITCHING': 'switching',
    'INITIALIZING': 'initializing'
}

# 性能相关常量
PERFORMANCE_CONSTANTS = {
    'SWITCH_TIMEOUT': 5000,  # ms
    'CAPABILITY_CACHE_TIMEOUT': 300,  # seconds
    'HEALTH_CHECK_INTERVAL': 60,  # seconds
    'MAX_RETRY_COUNT': 3,
}

# 默认配置
DEFAULT_ENGINE_CONFIG = {
    'preferred_engine': 'matplotlib',
    'auto_fallback': True,
    'switch_timeout': PERFORMANCE_CONSTANTS['SWITCH_TIMEOUT'],
    'capability_cache_timeout': PERFORMANCE_CONSTANTS['CAPABILITY_CACHE_TIMEOUT'],
    'health_check_interval': PERFORMANCE_CONSTANTS['HEALTH_CHECK_INTERVAL'],
    'log_level': 'INFO',
    'performance_monitoring': True
}
```

### 2. 配置验证和迁移

```python
# app/core/utils/engine_utils/engine_migration.py
"""引擎配置迁移和验证工具"""

class EngineConfigMigrator:
    """引擎配置迁移器"""
    
    def migrate_from_v1_to_v2(self, old_config: Dict) -> Dict:
        """从v1配置格式迁移到v2"""
        # 迁移逻辑
        pass
    
    def validate_config(self, config: Dict) -> bool:
        """验证配置格式正确性"""
        # 验证逻辑
        pass
    
    def repair_config(self, config: Dict) -> Dict:
        """修复损坏的配置"""
        # 修复逻辑
        pass
```

## AI编程指导原则

### 1. 功能实现优先级

当AI需要实现引擎管理功能时，应按以下优先级进行：

1. **核心功能优先**：首先实现基本的引擎切换和状态管理
2. **集成完整性**：确保与StateManager的正确集成
3. **错误处理**：添加完善的异常处理和恢复机制
4. **性能优化**：优化引擎切换和检测性能
5. **扩展性支持**：为未来功能预留接口

### 2. 代码质量检查清单

AI在编写代码时应确保：

```python
# ✅ 代码质量检查清单

# 1. 文件大小控制
# - 单个文件不超过500行
# - 复杂功能拆分到多个文件
# - 每个类职责单一明确

# 2. 错误处理完整
# - 所有公共方法都有异常处理
# - 提供有意义的错误信息
# - 实现恢复和回滚机制

# 3. 线程安全保证
# - 状态变更使用锁保护
# - 信号发射在正确的线程
# - 避免死锁和竞争条件

# 4. 性能考虑
# - 避免阻塞主线程
# - 使用缓存减少重复计算
# - 实现超时机制

# 5. 文档和注释
# - 所有公共接口都有文档字符串
# - 复杂逻辑有清晰注释
# - 提供使用示例
```

### 3. 重构和优化指导

当需要重构或优化现有代码时：

1. **保持向后兼容**：不破坏现有的公共接口
2. **渐进式重构**：分步骤进行，确保每步都能正常工作
3. **测试覆盖**：重构前后都要有充分的测试覆盖
4. **性能验证**：确保重构后性能不下降

## 实际应用示例

### 引擎管理器集成示例

以下是将引擎管理器正确集成到现有架构中的示例：

```
实施步骤：

1. 创建核心模块
   app/core/managers/rendering_engine/
   ├── rendering_engine_manager.py    # 400-500行，主要管理逻辑
   ├── engine_state_controller.py     # 300-400行，状态控制
   └── engine_capability_detector.py  # 350-450行，能力检测

2. 扩展StateManager
   修改 app/core/managers/state_manager.py
   - 添加RenderingEngineManager实例
   - 添加门面接口方法
   - 设置信号连接

3. 更新UI组件
   修改 app/ui/panels/analysis_panel.py
   - 使用StateManager的统一接口
   - 移除直接的引擎管理代码

4. 添加测试覆盖
   tests/unit/core/managers/rendering_engine/
   ├── test_rendering_engine_manager.py
   ├── test_engine_state_controller.py
   └── test_integration_with_state_manager.py
```

这种组织方式确保了：
- 每个文件职责单一且大小合理
- 与现有架构完美集成
- 为未来扩展预留了清晰的接口
- 代码结构清晰，易于维护和调试

通过遵循这些规范，AI编程可以产生高质量、易维护的渲染引擎状态管理代码。