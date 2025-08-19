# 依赖注入重构设计文档

## 架构设计

### 目标架构概览

```
app/
├── core/
│   ├── interfaces/                 # 服务接口定义
│   │   ├── __init__.py
│   │   ├── image_processor_interface.py
│   │   ├── state_manager_interface.py  
│   │   ├── config_manager_interface.py
│   │   └── app_controller_interface.py
│   ├── dependency_injection/       # 依赖注入容器
│   │   ├── __init__.py
│   │   ├── dependency_container.py
│   │   └── service_builder.py
│   └── container/                 # 现有容器(重构)
│       ├── application_bootstrap.py (重构ServiceFactory)
│       └── ...
├── ui/
│   └── main_window_injected.py   # 重构后的主窗口
└── main_injected.py              # 重构后的主入口
```

### 核心组件设计

#### 1. 服务接口层 (core/interfaces/)

**图像处理服务接口**
- 文件: `image_processor_interface.py`
- 职责: 定义图像处理的抽象接口
- 方法: process_image, get_current_image等核心方法

**状态管理服务接口** 
- 文件: `state_manager_interface.py`
- 职责: 定义状态管理的抽象接口
- 方法: load_image, get_pipeline等状态操作

**配置管理服务接口**
- 文件: `config_manager_interface.py` 
- 职责: 定义配置访问的抽象接口
- 方法: get_config, update_config等配置操作

**应用控制服务接口**
- 文件: `app_controller_interface.py`
- 职责: 定义应用控制的抽象接口
- 方法: load_image, save_image等控制操作

#### 2. 依赖注入容器 (core/dependency_injection/)

**依赖容器**
- 文件: `dependency_container.py`
- 职责: 管理服务注册和依赖解析
- 特点: 替换ServiceRegistry，支持接口绑定

**服务构建器**
- 文件: `service_builder.py`
- 职责: 配置服务依赖关系和创建服务实例
- 特点: 简化ServiceFactory，专注依赖配置

#### 3. 应用引导器 (core/container/)

**应用引导器**
- 文件: `application_bootstrap.py`
- 职责: 应用启动时的依赖配置和初始化
- 特点: 替换当前ServiceFactory的部分职责

### 依赖注入设计模式

#### 1. 构造函数注入模式

```python
# 当前模式 (需要移除)
class MainWindow:
    def __init__(self, context: AppContext):
        self.image_processor = context.get_service('image_processor')

# 目标模式
class MainWindow:
    def __init__(self, 
                 image_processor: ImageProcessorInterface,
                 state_manager: StateManagerInterface,
                 config_manager: ConfigManagerInterface):
        self.image_processor = image_processor
```

#### 2. 接口约束模式

```python
# 服务实现必须遵循接口契约
class ImageProcessor(ImageProcessorInterface):
    def __init__(self, config: ConfigManagerInterface):
        self.config = config  # 依赖注入，而非全局访问
```

#### 3. 容器配置模式

```python
# 在应用启动时配置所有依赖关系
container.register_interface(ImageProcessorInterface, ImageProcessor)
container.register_interface(StateManagerInterface, StateManager)
```

## 详细设计

### 1. 接口定义设计

#### ImageProcessorInterface
- **抽象方法**: process_image, get_current_image, clear_image
- **依赖**: ConfigManagerInterface
- **职责边界**: 纯图像处理逻辑，不涉及UI或状态管理

#### StateManagerInterface  
- **抽象方法**: load_image, get_pipeline, set_active_tool
- **依赖**: 无直接服务依赖
- **职责边界**: 应用状态管理，不涉及具体处理逻辑

#### ConfigManagerInterface
- **抽象方法**: get_config, update_config, save_config
- **依赖**: 无服务依赖
- **职责边界**: 配置持久化，不涉及业务逻辑

#### AppControllerInterface
- **抽象方法**: load_image, save_image, export_analysis
- **依赖**: ImageProcessorInterface, StateManagerInterface
- **职责边界**: 协调各服务，不直接处理数据

### 2. 依赖容器设计

#### DependencyContainer
```python
class DependencyContainer:
    """依赖注入容器，管理服务注册和解析"""
    
    def register_interface(self, interface_type, implementation_type): pass
    def register_instance(self, interface_type, instance): pass  
    def resolve(self, interface_type): pass
    def build_with_dependencies(self, target_type): pass
```

#### ServiceBuilder
```python
class ServiceBuilder:
    """服务构建器，配置依赖关系"""
    
    def configure_core_services(self): pass
    def configure_ui_services(self): pass
    def configure_batch_services(self): pass
```

### 3. 重构策略

#### 阶段1: 接口定义
1. 创建所有服务接口
2. 让现有实现类继承接口
3. 验证接口完整性

#### 阶段2: 容器实现
1. 实现DependencyContainer
2. 实现ServiceBuilder  
3. 基本的依赖解析测试

#### 阶段3: 主窗口重构
1. 重构MainWindow构造函数
2. 移除context依赖
3. 使用接口类型声明依赖

#### 阶段4: 全局清理
1. 移除所有全局访问器函数
2. 清理全局变量
3. 更新main.py启动流程

## 数据流设计

### 重构前数据流
```
main.py → 创建AppContext → 各组件通过context.get_service()获取依赖
```

### 重构后数据流  
```
main.py → ServiceBuilder配置依赖 → DependencyContainer解析依赖 → 构造函数注入
```

## 错误处理设计

### 1. 依赖解析错误
- **缺失依赖**: 抛出DependencyNotRegisteredException
- **循环依赖**: 抛出CircularDependencyException  
- **接口不匹配**: 抛出InterfaceMismatchException

### 2. 服务创建错误
- **构造失败**: 包装原始异常并提供依赖上下文
- **接口验证**: 确保实现类符合接口契约
- **生命周期管理**: 确保服务正确初始化和清理

## 测试策略

### 1. 接口测试
- **接口完整性**: 验证所有必要方法都已定义
- **契约测试**: 确保实现类遵循接口契约
- **模拟测试**: 使用接口创建Mock对象

### 2. 容器测试  
- **依赖解析**: 测试简单和复杂依赖解析
- **循环检测**: 验证循环依赖检测机制
- **错误处理**: 测试各种错误场景

### 3. 集成测试
- **端到端**: 从main.py启动到UI显示的完整流程
- **服务交互**: 验证服务间通过接口正确交互
- **功能完整性**: 确保所有现有功能正常工作

## 性能考量

### 1. 容器性能
- **单例模式**: 对重复使用的服务使用单例
- **延迟加载**: 对非关键服务实现按需创建
- **缓存机制**: 缓存已解析的依赖关系

### 2. 内存管理
- **弱引用**: 避免不必要的强引用循环
- **资源清理**: 确保服务正确释放资源
- **生命周期**: 明确服务的生命周期边界

## 兼容性保证

### 1. API兼容性
- **现有方法**: 所有公共方法签名保持不变
- **信号机制**: PyQt6信号-槽机制完全保留
- **返回值**: 方法返回值类型和格式不变

### 2. 行为兼容性
- **业务逻辑**: 核心业务逻辑完全不变
- **错误处理**: 错误类型和处理方式保持一致
- **性能特征**: 不引入明显的性能退化

## 风险缓解

### 1. 技术风险
- **复杂度控制**: 采用最简单可行的设计
- **渐进重构**: 分阶段实施，每阶段都可运行
- **回滚机制**: 保持旧代码，便于快速回滚

### 2. 质量风险  
- **接口设计**: 基于现有使用模式设计接口
- **测试覆盖**: 重点测试依赖注入机制
- **文档完整**: 提供清晰的使用指导

## 总结

本设计采用标准的依赖注入模式，通过接口抽象和构造函数注入实现真正的控制反转。设计简单务实，专注于解决当前的全局状态污染问题，为后续的架构演进奠定基础。