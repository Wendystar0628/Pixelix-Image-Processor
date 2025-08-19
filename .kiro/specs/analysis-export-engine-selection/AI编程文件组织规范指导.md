# AI编程文件组织规范指导

## 概述

本指导文档旨在规范AI在实现"数据分析图表导出引擎选择功能"时的文件组织、代码结构和命名约定，避免代码职责混乱、功能耦合和文件组织不当的问题。

## 文件夹结构规范

### 核心原则

1. **单一职责原则**：每个文件夹和文件都应有明确的单一职责
2. **功能内聚原则**：相关功能的代码应组织在同一模块内
3. **层次分离原则**：不同抽象层次的代码应分离到不同目录
4. **可扩展性原则**：文件结构应便于未来功能扩展

### 推荐的文件夹结构

```
app/
├── core/
│   ├── gpu/                          # GPU相关功能模块
│   │   ├── __init__.py
│   │   ├── detector.py               # GPU检测器
│   │   ├── models.py                 # GPU相关数据模型
│   │   └── exceptions.py             # GPU相关异常
│   │
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── base_exporter.py          # 现有基类
│   │   ├── matplotlib_exporter.py    # 现有Matplotlib导出器
│   │   ├── pyqtgraph_exporter.py     # 新增PyQtGraph导出器
│   │   ├── quality/                  # 质量控制子模块
│   │   │   ├── __init__.py
│   │   │   ├── settings.py           # 质量设置定义
│   │   │   └── manager.py            # 质量管理器
│   │   └── safe_exporter_wrapper.py  # 现有安全包装器
│   │
│   ├── models/
│   │   ├── analysis_export_config.py # 现有配置模型（需扩展）
│   │   └── export_engine_config.py   # 新增引擎配置模型
│   │
│   └── services/
│       ├── export_preferences_manager.py # 现有偏好管理器（需扩展）
│       └── engine_selection_service.py   # 新增引擎选择服务
│
├── ui/
│   ├── dialogs/
│   │   └── analysis_export/
│   │       ├── export_config_dialog.py    # 现有对话框（需扩展）
│   │       └── components/                # 新增组件子目录
│   │           ├── __init__.py
│   │           ├── engine_selector.py     # 引擎选择器组件
│   │           └── quality_control.py     # 质量控制组件
│   │
│   └── widgets/
│       └── export/                        # 新增导出相关控件目录
│           ├── __init__.py
│           ├── engine_info_widget.py      # 引擎信息显示控件
│           └── gpu_status_widget.py       # GPU状态显示控件
│
└── config.py                             # 现有配置文件（需扩展）
```

## 文件命名规范

### 命名约定

1. **模块文件**：使用小写字母和下划线，描述功能 (`gpu_detector.py`)
2. **类文件**：文件名应反映主要类的功能 (`rendering_engine_selector.py`)
3. **组件文件**：UI组件使用`_widget.py`或`_component.py`后缀
4. **服务文件**：业务逻辑服务使用`_service.py`后缀
5. **模型文件**：数据模型使用`_models.py`或`_config.py`后缀

### 具体文件命名

```
# GPU相关
app/core/gpu/detector.py              # GPUDetector类
app/core/gpu/models.py                # GPUSupportInfo等数据类
app/core/gpu/exceptions.py            # GPU相关异常类

# 导出器相关
app/core/exporters/pyqtgraph_exporter.py    # PyQtGraphExporter类
app/core/exporters/quality/settings.py      # 质量设置常量
app/core/exporters/quality/manager.py       # QualityManager类

# UI组件
app/ui/dialogs/analysis_export/components/engine_selector.py  # RenderingEngineSelector类
app/ui/dialogs/analysis_export/components/quality_control.py  # QualityControlWidget类

# 服务和配置
app/core/services/engine_selection_service.py  # EngineSelectionService类
app/core/models/export_engine_config.py        # ExportEngineInfo等类
```

## 代码文件内容规范

### 文件头部规范

每个新文件都应包含标准的文件头：

```python
"""
模块功能的简要描述

详细描述模块的职责、主要类和功能。
"""

import logging
from typing import Optional, List, Dict, Any
# 其他导入...

# 设置日志记录器
logger = logging.getLogger(__name__)
```

### 类设计规范

#### 1. GPU检测器 (`app/core/gpu/detector.py`)

```python
"""
GPU检测和支持验证模块

负责检测系统GPU硬件、驱动支持和PyQtGraph GPU功能。
"""

class GPUDetector:
    """GPU支持检测器
    
    职责：
    - 检测NVIDIA GPU硬件
    - 验证PyQtGraph GPU支持
    - 获取GPU性能信息
    - 推荐质量设置
    """
    
    def __init__(self):
        """初始化GPU检测器"""
        
    def detect_gpu_support(self) -> 'GPUSupportInfo':
        """检测完整的GPU支持情况"""
        
    def _detect_nvidia_gpu(self) -> bool:
        """检测NVIDIA GPU（私有方法）"""
        
    def _check_pyqtgraph_support(self) -> bool:
        """检查PyQtGraph GPU支持（私有方法）"""
```

#### 2. PyQtGraph导出器 (`app/core/exporters/pyqtgraph_exporter.py`)

```python
"""
PyQtGraph渲染引擎导出器

实现基于PyQtGraph的GPU加速图表导出功能。
"""

class PyQtGraphExporter(BaseExporter):
    """PyQtGraph导出器
    
    职责：
    - 使用PyQtGraph渲染各种分析图表
    - 应用质量设置和GPU优化
    - 处理GPU相关错误和回退
    """
    
    def __init__(self, quality_manager: 'QualityManager'):
        """初始化PyQtGraph导出器"""
        
    def export_histogram(self, data: List[np.ndarray], 
                        filepath: str, config: ExportConfig) -> bool:
        """导出RGB直方图"""
        
    def _create_histogram_widget(self, config: ExportConfig) -> pg.PlotWidget:
        """创建直方图控件（私有方法）"""
```

#### 3. 渲染引擎选择器 (`app/ui/dialogs/analysis_export/components/engine_selector.py`)

```python
"""
渲染引擎选择器UI组件

提供用户选择渲染引擎和质量设置的界面。
"""

class RenderingEngineSelector(QWidget):
    """渲染引擎选择器控件
    
    职责：
    - 显示可用的渲染引擎选项
    - 提供质量等级选择
    - 显示引擎特性和GPU状态
    - 发出选择变化信号
    """
    
    # 信号定义
    engine_changed = pyqtSignal(str)
    quality_changed = pyqtSignal(str)
    
    def __init__(self, gpu_support_info: 'GPUSupportInfo', parent=None):
        """初始化引擎选择器"""
        
    def _init_ui(self):
        """初始化UI组件（私有方法）"""
        
    def _create_engine_combo(self) -> QComboBox:
        """创建引擎选择下拉框（私有方法）"""
```

### 职责分离规范

#### 避免的反模式

❌ **错误示例：将所有功能放在一个文件中**

```python
# 错误：app/ui/dialogs/analysis_export/export_config_dialog.py
class AnalysisExportDialog(QDialog):
    def __init__(self):
        # GPU检测代码（应该在独立的GPU模块中）
        self.detect_gpu()
        
        # PyQtGraph导出代码（应该在导出器模块中）
        self.setup_pyqtgraph_exporter()
        
        # 质量管理代码（应该在质量管理模块中）
        self.setup_quality_settings()
    
    def detect_gpu(self):
        # 大量GPU检测逻辑...
        pass
    
    def export_with_pyqtgraph(self):
        # 大量导出逻辑...
        pass
```

✅ **正确示例：职责分离**

```python
# 正确：app/ui/dialogs/analysis_export/export_config_dialog.py
class AnalysisExportDialog(QDialog):
    def __init__(self, gpu_detector: GPUDetector, 
                 engine_service: EngineSelectionService):
        super().__init__()
        
        # 依赖注入，而不是直接创建
        self.gpu_detector = gpu_detector
        self.engine_service = engine_service
        
        # 使用专门的组件
        self.engine_selector = RenderingEngineSelector(
            self.gpu_detector.detect_gpu_support()
        )
        
        self._init_ui()
    
    def _init_ui(self):
        # 只负责UI布局和组装
        pass
```

### 模块依赖规范

#### 依赖层次

```
UI层 (app/ui/)
    ↓ 依赖
服务层 (app/core/services/)
    ↓ 依赖  
核心逻辑层 (app/core/exporters/, app/core/gpu/)
    ↓ 依赖
数据模型层 (app/core/models/)
```

#### 依赖注入示例

```python
# app/ui/dialogs/analysis_export/export_config_dialog.py
class AnalysisExportDialog(QDialog):
    def __init__(self, 
                 batch_handler: BatchProcessingHandler,
                 gpu_detector: GPUDetector,
                 engine_service: EngineSelectionService,
                 parent=None):
        """通过构造函数注入依赖，而不是在内部创建"""
        super().__init__(parent)
        
        self.batch_handler = batch_handler
        self.gpu_detector = gpu_detector
        self.engine_service = engine_service
```

## 测试文件组织规范

### 测试文件结构

```
tests/
├── unit/
│   ├── core/
│   │   ├── gpu/
│   │   │   ├── test_detector.py
│   │   │   └── test_models.py
│   │   ├── exporters/
│   │   │   ├── test_pyqtgraph_exporter.py
│   │   │   └── test_quality_manager.py
│   │   └── services/
│   │       └── test_engine_selection_service.py
│   └── ui/
│       └── dialogs/
│           └── analysis_export/
│               └── test_engine_selector.py
├── integration/
│   ├── test_export_engine_integration.py
│   └── test_gpu_detection_integration.py
└── fixtures/
    ├── gpu_mock_data.py
    └── export_test_data.py
```

### 测试文件命名

- 单元测试：`test_<模块名>.py`
- 集成测试：`test_<功能名>_integration.py`
- 测试数据：`<功能名>_test_data.py`或`<功能名>_mock_data.py`

## 实施检查清单

在实施每个任务时，请确保：

### 文件创建检查

- [ ] 新文件放在正确的功能目录中
- [ ] 文件名准确反映其主要职责
- [ ] 包含适当的`__init__.py`文件
- [ ] 文件头部包含清晰的模块说明

### 代码组织检查

- [ ] 每个类有明确的单一职责
- [ ] 私有方法使用下划线前缀
- [ ] 依赖通过构造函数注入
- [ ] 避免循环依赖

### 接口设计检查

- [ ] 公共接口简洁明确
- [ ] 使用类型提示
- [ ] 包含适当的文档字符串
- [ ] 错误处理得当

### 测试覆盖检查

- [ ] 每个新类都有对应的单元测试
- [ ] 关键功能有集成测试
- [ ] 测试文件组织合理
- [ ] 使用适当的测试数据和模拟

通过遵循这些规范，可以确保代码结构清晰、职责明确、易于维护和扩展。