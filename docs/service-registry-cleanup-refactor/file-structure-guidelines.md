# ServiceRegistry清理重构代码文件规范指导

## 修改前后文件结构对比

### 修改前文件结构（当前）
```
app/
├── controllers/                           # ❌ 整个目录需要删除
│   ├── __init__.py
│   ├── app_controller.py                  # 与handlers/app_controller.py重名
│   ├── base_controller.py                 # 抽象基类，职责不明确
│   ├── batch_processing_controller.py     # 批处理控制逻辑
│   ├── dialog_controller.py               # 对话框控制逻辑
│   ├── file_io_controller.py              # 文件操作控制逻辑
│   ├── image_loader_controller.py         # 图像加载控制逻辑
│   ├── image_operation_controller.py      # 图像操作控制逻辑
│   ├── preset_controller.py               # 预设控制逻辑
│   ├── state_controller.py                # 状态控制逻辑
│   └── signal_router.py                   # 信号路由逻辑
├── handlers/
│   ├── app_controller.py                  # 应用总控制器
│   ├── preset_handler.py                  # ❌ 使用ServiceRegistry
│   ├── processing_handler.py              # ✅ 已是依赖注入
│   └── file_handler.py                    # ✅ 已是依赖注入
├── core/
│   ├── container/
│   │   ├── application_bootstrap.py       # ❌ 包含ServiceRegistry兼容代码
│   │   └── service_registry.py            # ❌ 整个文件需要删除
│   └── dependency_injection/
│       └── service_builder.py             # ❌ 包含临时方案注释
└── ui/dialogs/
    └── apply_preset_dialog.py             # ❌ 使用preset_handler.context
```

### 修改后文件结构（目标）
```
app/
├── handlers/                              # ✅ 符合架构的控制器层
│   ├── app_controller.py                  # ✅ 整合所有子控制器为内部组件
│   ├── preset_handler.py                  # ✅ 纯依赖注入
│   ├── processing_handler.py              # ✅ 保持不变
│   └── file_handler.py                    # ✅ 保持不变
├── core/
│   ├── container/
│   │   ├── application_bootstrap.py       # ✅ 纯依赖注入，无兼容代码
│   │   └── application_state.py           # ✅ 保持不变
│   └── dependency_injection/
│       └── service_builder.py             # ✅ 完整的服务构建支持
└── ui/dialogs/
    └── apply_preset_dialog.py             # ✅ 清理context使用
```

## 文件职责说明

### 保留并重构的文件

#### `app/handlers/app_controller.py` - 应用总控制器
- **职责**: 统一的应用控制入口，包含内部组件类
- **内部组件**:
  - `FileOperationsComponent`: 文件操作（打开、保存、最近文件）
  - `ImageOperationsComponent`: 图像操作（滤镜、变换）
  - `BatchOperationsComponent`: 批处理操作（作业管理、导入）
  - `PresetOperationsComponent`: 预设操作（应用、保存、删除）
- **设计原则**: 组合模式，依赖注入，单一入口

#### `app/handlers/preset_handler.py` - 预设处理器
- **职责**: 预设业务逻辑处理
- **重构内容**: 移除ServiceRegistry，直接依赖注入StateManager
- **接口**: 保持所有公共方法不变

#### `app/core/container/application_bootstrap.py` - 应用引导器
- **职责**: 应用启动和依赖配置
- **简化内容**: 移除ServiceRegistry支持，纯依赖注入配置
- **清理**: 删除所有向后兼容代码和方法

#### `app/core/dependency_injection/service_builder.py` - 服务构建器
- **职责**: 所有服务的构建和配置
- **增强内容**: 添加AppController和PresetHandler构建方法
- **清理**: 移除临时方案注释

### 删除的文件

#### `app/controllers/` - 整个目录删除
- **原因**: 与架构设计不符，职责重复
- **迁移方式**: 功能整合到AppController内部组件
- **清理要求**: 彻底删除，不保留任何文件

#### `app/core/container/service_registry.py` - ServiceRegistry类
- **原因**: 不再使用，与依赖注入架构冲突
- **清理要求**: 删除文件，清理所有导入引用

## 代码清理步骤

### 1. ServiceRegistry清理检查清单

**必须删除的代码模式**:
```python
# ❌ 导入清理
from app.core.container import ServiceRegistry
from app.core.container.service_registry import ServiceRegistry

# ❌ 构造函数参数清理
def __init__(self, service_registry: ServiceRegistry)

# ❌ 服务获取清理
self.service_registry.get('service_name')
cast(ServiceType, self.service_registry.get('service_name'))

# ❌ 注释清理
# TODO: 重构为依赖注入
# 临时方案：使用ServiceRegistry
# 向后兼容：保留ServiceRegistry
```

**替换为依赖注入模式**:
```python
# ✅ 直接依赖注入
def __init__(self, state_manager: StateManagerInterface)

# ✅ 直接使用注入的服务
self.state_manager.method()
```

### 2. 文件迁移清理步骤

**AppController整合步骤**:
1. **保留接口**: 所有公共方法签名不变
2. **整合逻辑**: 将子控制器方法迁移为内部组件方法
3. **清理导入**: 移除对app/controllers/的所有导入
4. **删除引用**: 确保无其他地方引用旧控制器

**controllers目录删除步骤**:
1. **功能验证**: 确认所有功能已迁移
2. **引用检查**: 搜索并清理所有导入引用
3. **彻底删除**: 删除整个目录，不保留任何文件
4. **测试验证**: 确保应用正常启动和运行

### 3. 依赖注入转换步骤

**PresetHandler重构步骤**:
```python
# ❌ 旧方式 - 删除
def __init__(self, service_registry: ServiceRegistry):
    self.service_registry = service_registry
    self.state_manager = cast(StateManager, service_registry.get('state_manager'))

# ✅ 新方式 - 替换
def __init__(self, state_manager: StateManagerInterface):
    self.state_manager = state_manager
```

**ApplicationBootstrap简化步骤**:
```python
# ❌ 删除这些方法
def _populate_legacy_service_registry(self): pass
def _create_legacy_services(self): pass

# ❌ 删除这些属性
self.service_registry = ServiceRegistry()

# ✅ 保留纯依赖注入逻辑
def create_ui_services(self, main_window): 
    # 直接使用DependencyContainer
```

## 文件命名规范

### 避免重名原则
- **handlers层**: 使用`xxx_handler.py`命名（如`preset_handler.py`）
- **内部组件**: 使用`XxxComponent`类名（如`FileOperationsComponent`）
- **避免generic名称**: 不使用`controller.py`、`manager.py`等通用名
- **职责明确**: 文件名能清晰表达职责

### AI友好命名
- **描述性命名**: `file_operations_component`而非`file_ops`
- **避免缩写**: `preset_handler`而非`preset_hdl`
- **分层清晰**: 目录名体现架构层次
- **职责单一**: 一个文件一个主要职责

## 架构职责边界

### handlers层职责
- **业务流程协调**: 连接UI层和Core层
- **信号处理**: 响应UI信号，调用核心服务
- **不包含**: UI逻辑、数据结构定义、算法实现

### core层职责
- **核心业务逻辑**: 独立于UI的业务规则
- **数据管理**: 状态管理、数据存储
- **不包含**: UI相关代码、具体的业务流程

### 避免职责混乱
- **单向依赖**: handlers依赖core，core不依赖handlers
- **接口隔离**: 通过接口定义清晰边界
- **组件独立**: 每个组件可独立测试和使用

## 代码质量要求

### 注释规范
```python
# ✅ 简洁有效
class FileOperationsComponent:
    """文件操作组件：处理打开、保存、最近文件"""

# ❌ 冗长无用
class FileOperationsComponent:
    """
    这个类负责处理所有与文件相关的操作，包括但不限于
    文件的打开、保存、另存为、最近文件管理等功能...
    """
```

### 清理要求
- **删除debug代码**: 移除所有调试打印和临时代码
- **清理TODO**: 删除已完成或不相关的TODO注释
- **统一格式**: 保持一致的代码格式和风格
- **移除dead code**: 删除未使用的导入、方法、变量

## 验证清单

### 文件结构验证
- [ ] `app/controllers/`目录完全删除
- [ ] `service_registry.py`文件完全删除
- [ ] 无ServiceRegistry相关导入
- [ ] 内部组件正确定义在AppController中

### 功能验证
- [ ] 应用正常启动
- [ ] 所有菜单功能正常
- [ ] 预设功能正常
- [ ] 批处理功能正常
- [ ] 文件操作正常

### 代码质量验证
- [ ] 无TODO和临时方案注释
- [ ] 无未使用的导入
- [ ] 无ServiceRegistry残留代码
- [ ] 依赖注入正确配置

## 总结

本指导文档确保重构过程中文件组织清晰、职责明确、代码质量高。重点是彻底清理旧代码，避免新旧代码混用导致的混乱，建立清晰一致的架构结构。