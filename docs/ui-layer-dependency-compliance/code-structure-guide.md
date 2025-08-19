# UI层依赖合规性代码结构指导

## 文件结构变更概览

### 修改前的问题结构
```
app/ui/
├── main_window.py                   # 【问题】直接导入core.tools.ToolManager
├── managers/dialog_manager.py      # 【问题】直接导入core.managers.StateManager
└── panels/analysis_panel.py        # 【问题】直接导入core.configuration.ConfigDataAccessor
```

### 修改后的清洁结构
```
app/core/interfaces/
└── core_service_interface.py       # 【新增】核心服务桥接接口

app/core/adapters/
└── core_service_adapter.py         # 【新增】核心服务桥接适配器

app/handlers/
└── app_controller.py               # 【修改】集成CoreServiceAdapter

app/ui/
├── main_window.py                  # 【修改】通过桥接适配器访问核心服务
├── managers/dialog_manager.py     # 【修改】使用桥接适配器
└── panels/analysis_panel.py       # 【修改】通过适配器获取配置
```

## 代码重构指导

### 核心服务访问重构

#### 【错误方式】直接导入核心层
```python
# ❌ 违反分层架构
from app.core.managers.state_manager import StateManager
from app.core.configuration.config_data_accessor import ConfigDataAccessor

class SomeUIComponent:
    def __init__(self):
        self.state_manager = StateManager()  # 直接实例化
        self.config_accessor = ConfigDataAccessor()
```

#### 【正确方式】通过桥接适配器访问
```python
# ✅ 符合分层架构 - 复用现有桥接适配器模式
class SomeUIComponent:
    def __init__(self, app_controller):
        self.app_controller = app_controller
    
    def get_current_state(self):
        core_adapter = self.app_controller.get_core_service_adapter()
        if core_adapter:
            state_manager = core_adapter.get_state_manager()
            if state_manager:
                return state_manager.get_current_image_info()
        return {}
    
    def get_config_value(self, key):
        core_adapter = self.app_controller.get_core_service_adapter()
        if core_adapter:
            config_accessor = core_adapter.get_config_accessor()
            if config_accessor:
                return config_accessor.get_value(key)
        return None
```

### 核心服务桥接适配器设计

#### CoreServiceInterface接口
```python
# app/core/interfaces/core_service_interface.py
from abc import ABC, abstractmethod
from typing import Any

class CoreServiceInterface(ABC):
    """核心服务桥接接口 - 与UpperLayerServiceInterface保持设计一致性"""
    
    @abstractmethod
    def get_state_manager(self) -> Any:
        """获取状态管理器实例"""
        pass
    
    @abstractmethod
    def get_config_accessor(self) -> Any:
        """获取配置访问器实例"""
        pass
    
    @abstractmethod
    def get_tool_manager(self) -> Any:
        """获取工具管理器实例"""
        pass
```

#### CoreServiceAdapter实现
```python
# app/core/adapters/core_service_adapter.py  
from typing import Any, Dict
from ..interfaces.core_service_interface import CoreServiceInterface

class CoreServiceAdapter(CoreServiceInterface):
    """核心服务桥接适配器 - 复用UpperLayerServiceAdapter的设计模式"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
    
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """注册核心服务实例"""
        self._services[service_name] = service_instance
    
    def get_state_manager(self) -> Any:
        """获取状态管理器实例"""
        return self._services.get('state_manager')
    
    def get_config_accessor(self) -> Any:
        """获取配置访问器实例"""
        return self._services.get('config_accessor')
    
    def get_tool_manager(self) -> Any:
        """获取工具管理器实例"""
        return self._services.get('tool_manager')
```

### 数据模型访问规范

#### 允许直接导入的模型
```python
# ✅ 纯数据结构可以直接导入
from app.core.models.batch_models import BatchJob, BatchJobStatus
from app.core.models.export_config import ExportConfig, ConflictResolution
from app.core.models.operation_params import CurvesParams, LevelsParams

class BatchDialog:
    def create_job(self) -> BatchJob:
        return BatchJob(name="test", status=BatchJobStatus.PENDING)
```

#### 必须通过Handler访问的服务
```python
# ✅ 服务实例必须通过Handler访问
class MainWindow:
    def __init__(self, app_controller):
        self.app_controller = app_controller
    
    def get_current_state(self):
        # 通过Handler获取状态，而不是直接导入StateManager
        return self.app_controller.get_current_image_info()
```

### AppController桥接适配器集成

#### 集成CoreServiceAdapter
```python
# app/handlers/app_controller.py 修改
from app.core.adapters.core_service_adapter import CoreServiceAdapter

class AppController:
    def __init__(self, ...):
        # 现有初始化代码...
        
        # 创建并配置核心服务适配器
        self.core_service_adapter = CoreServiceAdapter()
        self._register_core_services()
    
    def _register_core_services(self):
        """注册核心服务到桥接适配器"""
        # 注册状态管理器
        if hasattr(self, 'state_manager'):
            self.core_service_adapter.register_service('state_manager', self.state_manager)
        
        # 注册配置访问器  
        if hasattr(self, 'config_accessor'):
            self.core_service_adapter.register_service('config_accessor', self.config_accessor)
            
        # 注册工具管理器
        if hasattr(self, 'tool_manager'):
            self.core_service_adapter.register_service('tool_manager', self.tool_manager)
    
    def get_core_service_adapter(self) -> CoreServiceAdapter:
        """为UI层提供核心服务适配器"""
        return self.core_service_adapter
```

## UI组件重构模式

### 1. 构造函数注入模式
```python
# 重构前
class AnalysisPanel(QWidget):
    def __init__(self):
        self.config_accessor = ConfigDataAccessor()  # 直接创建

# 重构后  
class AnalysisPanel(QWidget):
    def __init__(self, app_controller):
        self.app_controller = app_controller  # 注入Handler
```

### 2. 方法调用重构模式
```python
# 重构前
def update_config(self):
    value = self.config_accessor.get_analysis_config()

# 重构后
def update_config(self):
    value = self.app_controller.get_config_value('analysis_config')
```

### 3. 信号连接重构模式
```python
# 重构前
self.state_manager.image_changed.connect(self.on_image_changed)

# 重构后
self.app_controller.image_changed.connect(self.on_image_changed)
```

## 重构验证清单

### 文件级验证
- [ ] 移除所有对core层服务的直接导入
- [ ] 添加必要的Handler层依赖注入
- [ ] 保持所有数据模型导入的合规性

### 功能级验证  
- [ ] UI组件功能保持完全不变
- [ ] 用户交互体验无任何差异
- [ ] 错误处理机制正常工作

### 架构级验证
- [ ] UI层不再有跳级导入核心层
- [ ] 所有核心服务通过Handler层访问
- [ ] 分层依赖方向严格遵守

## 常见重构问题处理

### 如果Handler层方法不存在
1. 在AppController或UIServiceFacade中添加对应方法
2. 封装对核心服务的访问
3. 确保返回格式适合UI层使用

### 如果需要复杂的核心层交互
1. 将复杂逻辑封装在Handler层方法中
2. 提供简化的UI层接口
3. 保持Handler层方法的单一职责

### 如果性能出现问题
1. 在Handler层添加适当的缓存
2. 避免频繁的服务调用
3. 考虑异步处理复杂操作

## 命名规范

### Handler层方法命名
- UI数据获取：`get_ui_xxx_data()`
- 配置访问：`get_config_value(key)`
- 状态查询：`get_current_xxx_info()`

### UI组件重构命名
- 保持原有的公共方法名不变
- 内部实现方法可以重命名为更清晰的名称
- 添加必要的类型注解提高代码可读性