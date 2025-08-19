# AI编程文件结构和代码组织规范

## 概述

本文档为AI编程提供详细的文件结构规范和代码组织指导，旨在解决AI编程中常见的问题：
- 大量代码集中在单个文件中
- 代码文件职责混乱，功能耦合严重
- 文件夹结构不合理，新建文件放置位置不当
- 缺乏统一的命名和组织规范

## 核心原则

### 1. 单一职责原则
- 每个文件只负责一个明确的功能或概念
- 单个文件代码行数不超过500行（特殊情况除外）
- 类的职责要清晰，避免"上帝类"

### 2. 分层架构原则
- 严格按照分层架构组织代码
- 上层可以依赖下层，下层不能依赖上层
- 同层之间通过接口或事件通信

### 3. 模块化原则
- 相关功能组织在同一个模块（文件夹）中
- 模块之间通过明确的接口交互
- 每个模块都有清晰的边界和职责

## 项目文件结构规范

### 基础架构层次

```
app/
├── ui/                          # 用户界面层
│   ├── main_window.py          # 主窗口（单一文件）
│   ├── dialogs/                # 对话框模块
│   │   ├── __init__.py
│   │   ├── base_dialog.py      # 基础对话框类
│   │   ├── analysis_export/    # 分析导出对话框模块
│   │   │   ├── __init__.py
│   │   │   ├── export_config_dialog.py
│   │   │   └── export_progress_dialog.py
│   │   └── batch_processing/   # 批处理对话框模块
│   ├── panels/                 # 面板组件
│   ├── widgets/                # 自定义控件
│   └── managers/               # UI管理器
├── handlers/                    # 处理器层（控制器）
│   ├── __init__.py
│   ├── file_handler.py         # 文件处理器
│   ├── batch_processing/       # 批处理处理器模块
│   │   ├── __init__.py
│   │   ├── batch_processing_handler.py
│   │   ├── progress_manager.py
│   │   └── config_manager.py
│   └── export_handler.py       # 导出处理器
├── core/                       # 核心业务层
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── batch_models.py     # 批处理模型
│   │   ├── analysis_export_config.py
│   │   └── integration/        # 集成相关模型
│   │       ├── __init__.py
│   │       ├── enhanced_batch_models.py
│   │       └── resource_models.py
│   ├── services/               # 业务服务
│   │   ├── __init__.py
│   │   ├── analysis_export_service.py
│   │   ├── file_organization_service.py
│   │   └── integration/        # 集成服务
│   │       ├── __init__.py
│   │       └── integrated_export_service.py
│   ├── managers/               # 业务管理器
│   │   ├── __init__.py
│   │   ├── batch_job_manager.py
│   │   └── enhanced/           # 增强管理器
│   │       ├── __init__.py
│   │       └── enhanced_job_manager.py
│   ├── integration/            # 集成层（新增）
│   │   ├── __init__.py
│   │   ├── thread_safe_processor.py
│   │   ├── resource_manager.py
│   │   └── task_coordinator.py
│   ├── monitoring/             # 监控组件（新增）
│   │   ├── __init__.py
│   │   ├── performance_monitor.py
│   │   └── memory_manager.py
│   ├── exporters/              # 导出器
│   ├── exceptions/             # 异常定义
│   └── utils/                  # 工具类
├── workers/                    # 工作线程
│   ├── __init__.py
│   ├── analysis_export_worker.py
│   └── batch_processing_worker.py
└── config/                     # 配置管理
    ├── __init__.py
    └── settings.py
```

## 文件命名规范

### 1. 文件命名规则

#### Python文件
- 使用小写字母和下划线：`analysis_export_service.py`
- 类名使用驼峰命名：`AnalysisExportService`
- 模块名简洁明了，体现功能：`thread_safe_processor.py`

#### 文件夹命名
- 使用小写字母和下划线：`batch_processing`
- 功能模块文件夹：`analysis_export`, `integration`
- 按功能分组：`dialogs`, `services`, `managers`

### 2. 特殊文件命名

#### 基础类文件
- `base_*.py`：基础类文件，如 `base_dialog.py`, `base_exporter.py`
- `abstract_*.py`：抽象类文件

#### 接口文件
- `*_interface.py`：接口定义文件
- `*_protocol.py`：协议定义文件

#### 工厂类文件
- `*_factory.py`：工厂类文件

## 代码组织规范

### 1. 单文件代码结构

```python
"""
模块文档字符串
简要描述模块的功能和用途
"""

# 标准库导入
import os
import sys
from typing import List, Dict, Optional

# 第三方库导入
from PyQt6.QtCore import QObject, pyqtSignal
import numpy as np

# 项目内部导入
from app.core.models.batch_models import BatchJob
from app.core.exceptions import ExportError

# 常量定义
DEFAULT_TIMEOUT = 30
MAX_RETRY_COUNT = 3

# 类型别名
ImageData = np.ndarray
ConfigDict = Dict[str, Any]


class ClassName:
    """类文档字符串
    
    详细描述类的功能、用途和使用方法
    
    Attributes:
        attribute_name: 属性描述
        
    Example:
        使用示例
    """
    
    def __init__(self, param1: str, param2: Optional[int] = None):
        """初始化方法"""
        pass
        
    def public_method(self) -> bool:
        """公共方法"""
        pass
        
    def _private_method(self) -> None:
        """私有方法"""
        pass


# 模块级函数
def utility_function(param: str) -> str:
    """工具函数"""
    pass
```

### 2. 文件大小控制

#### 推荐文件大小
- **小型文件**（< 200行）：单一功能类、工具函数、数据模型
- **中型文件**（200-400行）：业务服务类、管理器类
- **大型文件**（400-500行）：复杂的处理器类、主要的控制器类
- **超大文件**（> 500行）：需要拆分，除非有特殊原因

#### 文件拆分策略
当文件超过500行时，考虑以下拆分方式：

1. **按功能拆分**
```python
# 原文件：large_service.py (800行)
# 拆分为：
# - base_service.py (基础功能)
# - data_processor.py (数据处理)
# - export_handler.py (导出处理)
# - error_handler.py (错误处理)
```

2. **按职责拆分**
```python
# 原文件：complex_manager.py (600行)
# 拆分为：
# - manager_core.py (核心管理功能)
# - manager_config.py (配置管理)
# - manager_events.py (事件处理)
```

### 3. 类的职责分离

#### 单一职责类示例

```python
# ❌ 错误：职责混乱的类
class BadExportManager:
    def export_data(self): pass
    def validate_config(self): pass
    def create_directory(self): pass
    def send_email(self): pass  # 不相关的职责
    def log_activity(self): pass  # 不相关的职责

# ✅ 正确：职责清晰的类
class ExportManager:
    """专门负责导出管理"""
    def export_data(self): pass
    def get_export_status(self): pass

class ConfigValidator:
    """专门负责配置验证"""
    def validate_config(self): pass
    def get_validation_errors(self): pass

class FileSystemManager:
    """专门负责文件系统操作"""
    def create_directory(self): pass
    def ensure_path_exists(self): pass
```

## 模块组织规范

### 1. 功能模块组织

#### 分析导出模块示例
```
app/core/services/analysis_export/
├── __init__.py                 # 模块初始化，导出主要类
├── base_export_service.py      # 基础导出服务（< 200行）
├── data_processor.py           # 数据处理器（< 300行）
├── file_manager.py             # 文件管理器（< 250行）
├── progress_tracker.py         # 进度跟踪器（< 200行）
└── export_validators.py        # 导出验证器（< 150行）
```

#### 模块初始化文件
```python
# __init__.py
"""
分析导出服务模块

提供图像分析数据的导出功能，包括数据处理、文件管理、进度跟踪等。
"""

from .base_export_service import BaseExportService
from .data_processor import AnalysisDataProcessor
from .file_manager import ExportFileManager
from .progress_tracker import ExportProgressTracker

# 主要导出类
__all__ = [
    'BaseExportService',
    'AnalysisDataProcessor', 
    'ExportFileManager',
    'ExportProgressTracker'
]

# 版本信息
__version__ = '1.0.0'
```

### 2. 集成模块组织

#### 批处理集成模块（可扩展架构）
```
app/core/integration/
├── __init__.py
├── base/                       # 基础集成组件
│   ├── __init__.py
│   ├── thread_safe_base.py     # 线程安全基类
│   ├── resource_base.py        # 资源管理基类
│   └── extension_base.py       # 扩展基础组件
├── processors/                 # 处理器组件
│   ├── __init__.py
│   ├── extensible_processor.py # 可扩展处理器
│   ├── processor_extensions.py # 处理器扩展接口
│   └── processing_strategy.py  # 处理策略选择器
├── managers/                   # 管理器组件
│   ├── __init__.py
│   ├── resource_manager.py     # 资源管理器
│   ├── extension_manager.py    # 扩展管理器
│   └── task_coordinator.py     # 任务协调器
├── monitoring/                 # 监控组件
│   ├── __init__.py
│   ├── performance_monitor.py  # 性能监控器
│   └── memory_monitor.py       # 内存监控器
└── extensions/                 # 扩展接口（为未来功能预留）
    ├── __init__.py
    ├── task_handlers.py        # 任务处理器接口
    ├── resource_providers.py   # 资源提供者接口
    └── processor_extensions.py # 处理器扩展接口
```

## 依赖管理规范

### 1. 导入顺序规范

```python
# 1. 标准库导入
import os
import sys
import threading
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

# 2. 第三方库导入
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QDialog

# 3. 项目内部导入 - 按层次从低到高
# 3.1 核心模型
from app.core.models.batch_models import BatchJob
from app.core.models.analysis_export_config import ExportConfig

# 3.2 异常和工具
from app.core.exceptions import ExportError
from app.core.utils.file_utils import ensure_directory

# 3.3 服务和管理器
from app.core.services.analysis_export_service import AnalysisExportService
from app.core.managers.batch_job_manager import BatchJobManager

# 3.4 处理器和控制器
from app.handlers.batch_processing import BatchProcessingHandler
```

### 2. 循环依赖避免

#### 使用接口解耦
```python
# ❌ 错误：直接依赖导致循环
# file_a.py
from file_b import ClassB

class ClassA:
    def __init__(self):
        self.b = ClassB()

# file_b.py  
from file_a import ClassA  # 循环依赖！

# ✅ 正确：使用接口解耦
# interfaces.py
from abc import ABC, abstractmethod

class ProcessorInterface(ABC):
    @abstractmethod
    def process(self, data): pass

# file_a.py
from interfaces import ProcessorInterface

class ClassA:
    def __init__(self, processor: ProcessorInterface):
        self.processor = processor

# file_b.py
from interfaces import ProcessorInterface

class ClassB(ProcessorInterface):
    def process(self, data): pass
```

## 测试文件组织

### 1. 测试文件结构

```
tests/
├── __init__.py
├── unit/                       # 单元测试
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── test_integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_thread_safe_processor.py
│   │   │   ├── test_resource_manager.py
│   │   │   └── test_task_coordinator.py
│   │   └── test_services/
│   └── handlers/
├── integration/                # 集成测试
│   ├── __init__.py
│   ├── test_batch_analysis_integration.py
│   └── test_export_workflow.py
└── fixtures/                   # 测试数据
    ├── __init__.py
    ├── sample_images/
    └── test_configs/
```

### 2. 测试文件命名

- 测试文件以 `test_` 开头
- 测试类以 `Test` 开头
- 测试方法以 `test_` 开头
- 测试文件名对应被测试的模块名

## AI编程指导原则

### 1. 文件创建指导

当AI需要创建新文件时，应该：

1. **确定文件职责**：明确文件要解决的单一问题
2. **选择合适位置**：根据功能层次选择正确的目录
3. **检查文件大小**：预估代码量，必要时提前拆分
4. **定义清晰接口**：明确文件对外提供的接口

### 2. 代码组织指导

```python
# AI编程时的思考流程：

# 1. 这个功能属于哪一层？
# - UI层：用户界面相关 -> app/ui/
# - 处理器层：业务逻辑控制 -> app/handlers/
# - 核心层：业务逻辑实现 -> app/core/
# - 工作线程：后台任务 -> app/workers/

# 2. 这个功能的具体分类？
# - 数据模型 -> app/core/models/
# - 业务服务 -> app/core/services/
# - 管理器 -> app/core/managers/
# - 工具类 -> app/core/utils/

# 3. 是否需要创建新的子模块？
# - 功能复杂度高 -> 创建子文件夹
# - 多个相关文件 -> 组织在同一模块
# - 单一文件 -> 直接放在对应目录

# 4. 文件大小是否合理？
# - > 500行 -> 考虑拆分
# - 多个职责 -> 按职责拆分
# - 复杂逻辑 -> 提取到单独文件
```

### 3. 重构指导

当现有代码需要重构时：

1. **识别问题**：文件过大、职责混乱、耦合严重
2. **制定计划**：确定拆分策略和目标结构
3. **渐进重构**：保持功能完整性，逐步重构
4. **验证结果**：确保重构后功能正常

## 实际应用示例

### 批处理分析集成的文件组织（可扩展架构）

基于当前需求和未来扩展性考虑，推荐的文件组织结构：

```
app/core/integration/
├── __init__.py                 # 导出主要集成类
├── extensible_processor.py     # 可扩展处理器（400-500行）
├── resource_manager.py         # 资源管理器（400-500行）
├── task_coordinator.py         # 任务协调器（300-400行）
├── performance_monitor.py      # 性能监控器（250-350行）
└── extension_manager.py        # 扩展管理器（200-300行）

app/core/managers/enhanced/
├── __init__.py
└── enhanced_job_manager.py     # 增强作业管理器（450-550行）

app/core/services/integration/
├── __init__.py
└── integrated_export_service.py # 集成导出服务（350-450行）

app/core/models/integration/
├── __init__.py
├── enhanced_batch_models.py    # 增强批处理模型（300-400行）
├── resource_models.py          # 资源管理模型（200-300行）
└── extension_models.py         # 扩展相关模型（150-250行）

app/core/extensions/             # 扩展接口（为未来功能预留）
├── __init__.py
├── task_handlers.py            # 任务处理器接口（200-300行）
├── resource_providers.py       # 资源提供者接口（150-250行）
└── processor_extensions.py     # 处理器扩展接口（200-300行）
```

### 可扩展架构设计原则

#### 1. 接口抽象化
- 通过抽象接口支持未来功能扩展
- 插件式架构，便于添加新功能模块
- 统一的扩展注册和管理机制

#### 2. 模块化设计
- 每个功能模块独立实现，便于维护和测试
- 清晰的模块边界和依赖关系
- 支持运行时动态加载扩展

#### 3. 向前兼容性
- 预留扩展点，避免未来重构
- 配置驱动的功能启用机制
- 渐进式功能集成策略

这种组织方式确保了：
- 每个文件职责单一且大小合理
- 为未来功能扩展预留了清晰的接口
- 模块边界清晰，便于维护和扩展
- 支持未来功能的无缝集成
- 避免技术债务的积累

通过遵循这些规范，AI编程可以产生更加清晰、可维护的代码结构。