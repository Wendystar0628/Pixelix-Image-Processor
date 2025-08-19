# "上帝对象"反模式消除代码文件规范指导

## 文件结构对比

### 修改前结构
```
app/core/container/
├── application_bootstrap.py        # 上帝对象：承担多种职责
├── application_state.py            # 应用状态管理
└── ui_service_factory.py          # UI服务工厂
```

### 修改后结构
```
app/core/container/
├── application_bootstrap.py        # 【修改】简化为纯协调器（≤50行）
├── service_manager.py              # 【新增】服务存储管理器
├── service_cleanup_manager.py      # 【新增】服务清理管理器
├── app_lifecycle_coordinator.py    # 【新增】应用生命周期协调器
├── application_state.py            # 【保持】应用状态管理
├── ui_service_factory.py          # 【保持】UI服务工厂
└── global_state_cleaner.py        # 【保持】代码分析工具（非服务组件）
```

## 代码文件职责说明

### 【修改】application_bootstrap.py
**职责:** 纯协调器，委托专门组件处理具体任务
- 创建和组装专门组件
- 委托生命周期管理给 AppLifecycleCoordinator
- 委托UI服务创建给 UIServiceFactory
- 提供向后兼容的接口

**代码特点:**
- 代码行数：≤ 50行
- 方法数量：≤ 4个
- 不再直接管理任何服务实例或具体逻辑

### 【新增】service_manager.py
**职责:** 专门管理服务实例的存储和获取，替代ApplicationBootstrap的services字典
- 注册和获取服务实例
- 维护服务字典
- 提供向后兼容的get_all_services()方法
- 简单的服务容器实现

**代码特点:**
- 代码行数：≤ 50行
- 方法数量：4个（register_service, get_service, get_all_services, clear_all）
- 纯数据管理，替代self.services字典

### 【新增】service_cleanup_manager.py  
**职责:** 专门处理各种服务的清理逻辑
- 清理分析线程服务
- 清理批处理服务
- 清理其他类型服务
- 错误容忍的清理策略

**代码特点:**
- 代码行数：≤ 70行
- 方法数量：4个（cleanup_all_services, cleanup_analysis_services, cleanup_batch_services, _safe_cleanup）
- 从 ApplicationBootstrap.cleanup_services() 迁移而来

### 【新增】app_lifecycle_coordinator.py
**职责:** 专门管理应用的启动和关闭生命周期
- 协调应用启动流程
- 协调应用关闭流程  
- 整合服务创建和清理
- 管理启动状态和错误处理

**代码特点:**
- 代码行数：≤ 80行
- 方法数量：5个（startup_application, shutdown_application, _handle_startup_error, _log_startup_info, _log_shutdown_info）
- 纯协调逻辑，委托具体工作给其他组件

## 代码清理指导

### ApplicationBootstrap 清理内容

#### 删除的属性
```python
# 删除这些属性
self.services = {}                    # 服务容器管理移到 ServiceContainerRegistry
self.direct_initializer = ...        # 服务初始化移到 AppLifecycleCoordinator  
```

#### 删除的方法
```python
# 删除这些方法的具体实现，改为委托
def initialize_all_services(self) -> dict:
    # 旧实现：直接管理服务
    if not self.services:
        self.services = self.direct_initializer.initialize_all_services()
    return self.services
    
    # 新实现：委托给服务容器
    return self.service_registry.get_all_services()

def cleanup_services(self) -> None:
    # 删除70行的具体清理逻辑
    # 改为委托调用
    
def bootstrap_application(self) -> bool:
    # 删除具体的启动逻辑
    # 改为委托给生命周期协调器
```

#### 保留的方法（简化实现）
```python
def create_ui_services(self, main_window) -> None:
    """保留但简化为委托"""
    services = self.service_registry.get_all_services()
    self.ui_service_factory.create_ui_services(main_window, services)

def shutdown(self) -> None:
    """保留但简化为委托"""
    self.lifecycle_coordinator.shutdown_application()
```

### 代码迁移指导

#### 从 ApplicationBootstrap 迁移到 ServiceCleanupManager
```python
# 源代码位置：ApplicationBootstrap.cleanup_services()
# 目标位置：ServiceCleanupManager.cleanup_all_services()

# 迁移内容：
- 分析线程清理逻辑 → cleanup_analysis_services()
- 批处理清理逻辑 → cleanup_batch_services()  
- 服务字典清理逻辑 → 委托给 ServiceContainerRegistry.clear_all()
```

#### 从 ApplicationBootstrap 迁移到 AppLifecycleCoordinator
```python
# 源代码位置：ApplicationBootstrap.bootstrap_application()
# 目标位置：AppLifecycleCoordinator.startup_application()

# 迁移内容：
- DirectServiceInitializer 调用逻辑
- 应用状态管理逻辑
- 启动成功/失败处理逻辑
- 服务创建诊断信息记录
```

## 命名规范

### 文件命名原则
- 使用 `snake_case` 命名
- 体现文件的具体职责
- 避免通用名称（如 manager.py, handler.py）
- 确保在整个项目中唯一

### 类命名原则
- 使用 `PascalCase` 命名
- 名称体现单一职责
- 避免使用 Manager, Handler 等通用后缀
- 优先使用具体的业务术语

### 方法命名原则
- 使用动词开头，清晰表达操作
- 参数名称具有描述性
- 避免缩写和模糊术语

## 导入规范

### 各文件的导入依赖

#### service_container_registry.py
```python
# 仅导入基础库
from typing import Dict, Any, Optional
import logging
```

#### service_cleanup_manager.py  
```python
# 仅导入基础库和日志
from typing import Dict, Any
import logging
```

#### app_lifecycle_coordinator.py
```python
# 导入必要的组件
from typing import Optional
import logging
from ..initialization.direct_service_initializer import DirectServiceInitializer
from .service_manager import ServiceManager
from .service_cleanup_manager import ServiceCleanupManager
from .application_state import ApplicationState
```

#### application_bootstrap.py (修改后)
```python
# 简化导入，只导入直接使用的组件
import logging
from app.config import AppConfig, ConfigManager
from .service_manager import ServiceManager
from .service_cleanup_manager import ServiceCleanupManager  
from .app_lifecycle_coordinator import AppLifecycleCoordinator
from .application_state import ApplicationState
from .ui_service_factory import UIServiceFactory
```

## 验证清单

### 文件创建验证
- [ ] service_manager.py 创建完成
- [ ] service_cleanup_manager.py 创建完成  
- [ ] app_lifecycle_coordinator.py 创建完成

### 代码清理验证
- [ ] ApplicationBootstrap.services 属性已删除
- [ ] ApplicationBootstrap 代码行数≤50行
- [ ] 旧的服务管理逻辑已迁移

### 职责分离验证
- [ ] ApplicationBootstrap 只负责委托协调
- [ ] ServiceManager 只负责服务存储管理
- [ ] ServiceCleanupManager 只负责服务清理
- [ ] AppLifecycleCoordinator 只负责生命周期协调

### 代码质量验证
- [ ] 每个文件代码行数符合要求
- [ ] 每个类方法数量符合要求  
- [ ] 注释简洁且准确
- [ ] 无冗余或重复代码