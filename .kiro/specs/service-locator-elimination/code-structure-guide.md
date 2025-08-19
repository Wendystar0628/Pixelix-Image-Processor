# 代码文件结构指导文档

## 修改前后文件结构对比

### 修改前的文件结构
```
app/
├── core/
│   ├── container/
│   │   ├── application_bootstrap.py          # 应用引导器（依赖ServiceLocator）
│   │   ├── service_locator.py               # ServiceLocator实现（需删除）
│   │   └── ...
│   ├── interfaces/
│   │   ├── service_locator_interface.py     # ServiceLocator接口（需删除）
│   │   └── ...
│   ├── initialization/
│   │   ├── layered_initializer.py           # 分层初始化器（需删除）
│   │   └── ...
│   └── managers/
│       ├── state_manager.py                 # 状态管理器（需修改）
│       └── ...
└── main.py                                  # 主入口（需修改）
```

### 修改后的文件结构
```
app/
├── core/
│   ├── container/
│   │   ├── application_bootstrap.py          # 应用引导器（简化，使用DirectServiceInitializer）
│   │   └── ...
│   ├── initialization/
│   │   ├── direct_service_initializer.py    # 直接服务初始化器（新增）
│   │   └── ...
│   └── managers/
│       ├── state_manager.py                 # 状态管理器（构造函数注入）
│       └── ...
└── main.py                                  # 主入口（直接使用服务字典）
```

## 新增文件职责说明

### app/core/initialization/direct_service_initializer.py
**职责：** 直接服务初始化器，替代ServiceLocator模式
- 按照core->business->handler的层次顺序创建服务
- 管理服务间的依赖关系，确保正确的创建顺序
- 返回包含所有服务实例的字典，供main.py直接使用
- 提供基本的错误处理和日志记录

**核心方法：**
- `initialize_all_services()` - 创建所有服务并返回服务字典
- `_create_layer_1_services()` - 创建核心服务（ConfigurationRegistry、ImageProcessor）
- `_create_layer_2_services()` - 创建业务服务（StateManager）
- `_create_layer_3_services()` - 创建处理器服务（各种Handler）

## 修改文件职责说明

### app/core/managers/state_manager.py（修改）
**修改内容：**
- 构造函数现在接收`ImageProcessor`参数，实现构造函数注入
- 在构造函数中直接创建`ProxyWorkflowManager`，消除运行时依赖查找
- 删除`set_image_processor`方法及相关逻辑

**修改前：**
```python
def __init__(self):
    # 初始化基本组件
    
def set_image_processor(self, image_processor):
    self.image_processor = image_processor
    # 运行时导入和创建ProxyWorkflowManager
    from app.core.managers.proxy_workflow_manager import ProxyWorkflowManager
    self.proxy_workflow_manager = ProxyWorkflowManager(...)
```

**修改后：**
```python
def __init__(self, image_processor: ImageProcessorInterface):
    self.image_processor = image_processor
    # 直接在构造函数中创建所有依赖
    from app.core.managers.proxy_workflow_manager import ProxyWorkflowManager
    self.proxy_workflow_manager = ProxyWorkflowManager(...)
```

### app/core/container/application_bootstrap.py（修改）
**修改内容：**
- 移除ServiceLocator、LayeredServiceInitializer相关的导入和属性
- 使用DirectServiceInitializer替代原有的服务创建逻辑
- 简化类结构，删除不再需要的兼容性代码
- 添加`initialize_all_services`方法，直接返回服务字典

**删除的组件：**
- `ServiceLocator`相关属性和方法
- `LayeredServiceInitializer`相关代码
- `CompatibilityAdapter`相关代码
- `get_service_locator`方法

### app/main.py（修改）
**修改内容：**
- 移除所有`service_locator`相关的代码和导入
- 直接从`bootstrap.initialize_all_services()`获取服务字典
- 直接传递服务实例给MainWindow构造函数和属性设置
- 简化`_setup_signal_connections`函数，直接使用services字典

**修改前：**
```python
service_locator = bootstrap.get_service_locator()
image_processor = service_locator.get_service('image_processor')
# ... 其他服务获取
```

**修改后：**
```python
services = bootstrap.initialize_all_services()
image_processor = services['image_processor']
# ... 直接从字典获取服务
```

## 删除文件清单

### 必须完全删除的文件
1. **app/core/container/service_locator.py**
   - ServiceLocator的具体实现
   - 提供中心化的服务获取接口
   - 是服务定位器反模式的核心

2. **app/core/interfaces/service_locator_interface.py**
   - ServiceLocator的抽象接口
   - 定义服务定位器的标准方法
   - 与ServiceLocator实现配套使用

3. **app/core/initialization/layered_initializer.py**
   - 原有的分层服务初始化器
   - 被DirectServiceInitializer完全替代
   - 包含复杂的容器管理逻辑

## 清理旧代码的详细步骤

### 步骤1：删除文件前的依赖检查
1. 搜索所有对`ServiceLocator`的引用
2. 搜索所有对`ServiceLocatorInterface`的引用
3. 搜索所有对`LayeredServiceInitializer`的引用
4. 确认这些引用都已在修改过程中处理

### 步骤2：清理导入语句
在以下文件中清理相关导入：
- `app/core/container/application_bootstrap.py`
- `app/main.py`
- 任何其他可能导入这些类的文件

**需要清理的导入示例：**
```python
# 删除这些导入
from .service_locator import ServiceLocator
from ..interfaces.service_locator_interface import ServiceLocatorInterface
from ..initialization.layered_initializer import LayeredServiceInitializer
```

### 步骤3：清理类型注解
搜索并清理所有使用已删除类型的类型注解：
```python
# 删除这些类型注解
def some_method(locator: ServiceLocatorInterface) -> None:
def get_locator() -> ServiceLocator:
```

### 步骤4：清理方法和属性
在ApplicationBootstrap中删除：
- `get_service_locator`方法
- `service_locator`属性
- 所有ServiceLocator相关的初始化代码

### 步骤5：验证清理完整性
1. 使用IDE或grep搜索`ServiceLocator`，确保没有遗留引用
2. 使用IDE或grep搜索`LayeredServiceInitializer`，确保没有遗留引用
3. 尝试启动应用，确保没有导入错误
4. 运行基本功能测试，确保应用正常工作

### 步骤6：清理未使用的导入
使用工具或手动检查：
1. 清理所有未使用的import语句
2. 清理所有未使用的类型注解
3. 确保代码整洁，没有冗余内容

## 架构合规性检查

### 分层架构验证
确保修改后的代码仍然遵循分层架构：
1. **Core层**：ConfigurationRegistry、ImageProcessor等核心服务
2. **Business层**：StateManager等业务逻辑服务
3. **Handler层**：各种Handler处理器服务

### 依赖方向检查
验证依赖关系的正确性：
- Handler层可以依赖Business层和Core层
- Business层可以依赖Core层
- Core层不应依赖上层服务
- 避免任何循环依赖

### 职责单一性检查
确保每个文件职责清晰：
- DirectServiceInitializer只负责服务创建
- StateManager只负责状态管理
- ApplicationBootstrap只负责应用启动协调
- main.py只负责应用入口和服务组装

## 防止回退措施

### 代码审查检查点
1. 确保没有重新引入ServiceLocator模式
2. 验证所有依赖都通过构造函数注入
3. 检查没有运行时依赖查找
4. 确保服务创建顺序正确

### 持续监控
1. 定期检查是否有新的服务定位器模式引入
2. 监控依赖关系的复杂度
3. 确保架构设计的一致性
4. 维护清晰的服务创建文档

## 注意事项

### AI代码生成指导
为确保AI生成的代码符合架构设计：
1. 明确每个文件的单一职责
2. 严格遵循构造函数注入原则
3. 避免在方法内部进行服务查找
4. 保持服务创建的确定性顺序

### 维护性考虑
1. 保持DirectServiceInitializer的简洁性
2. 避免在服务创建中添加复杂逻辑
3. 确保错误处理简单明了
4. 维护清晰的服务依赖关系文档