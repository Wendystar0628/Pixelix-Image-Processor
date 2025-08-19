# 依赖注入重构文件结构指导

## 文件结构对比

### 重构前文件结构
```
app/
├── core/
│   ├── container/
│   │   ├── service_factory.py          # 服务工厂(职责过重)
│   │   ├── service_registry.py         # 服务注册表
│   │   └── application_state.py        # 应用状态
│   ├── engines/
│   │   └── image_processor.py          # 图像处理器实现
│   └── managers/
│       └── state_manager.py            # 状态管理器(含全局访问器)
├── controllers/
│   └── app_controller.py               # 应用控制器
├── config.py                           # 配置管理(含全局访问器)
├── context.py                          # 应用上下文(含全局访问器)
├── ui/
│   └── main_window.py                  # 主窗口(通过context获取服务)
└── main.py                             # 主入口(设置全局状态)
```

### 重构后文件结构
```
app/
├── core/
│   ├── interfaces/                     # 【新增】服务接口定义
│   │   ├── __init__.py
│   │   ├── image_processor_interface.py
│   │   ├── state_manager_interface.py  
│   │   ├── config_manager_interface.py
│   │   └── app_controller_interface.py
│   ├── dependency_injection/           # 【新增】依赖注入容器
│   │   ├── __init__.py
│   │   ├── dependency_container.py
│   │   └── service_builder.py
│   ├── container/
│   │   ├── application_bootstrap.py    # 【新增】应用引导器
│   │   ├── service_factory.py          # 【简化】移除服务定位逻辑
│   │   ├── service_registry.py         # 【保留】向后兼容
│   │   └── application_state.py        # 【保留】不变
│   ├── engines/
│   │   └── image_processor.py          # 【修改】实现接口,构造函数注入
│   └── managers/
│       └── state_manager.py            # 【修改】移除全局访问器
├── controllers/
│   └── app_controller.py               # 【修改】实现接口,构造函数注入  
├── config.py                           # 【修改】移除全局访问器
├── ui/
│   └── main_window.py                  # 【重构】构造函数注入依赖
└── main.py                             # 【重构】使用依赖注入启动
```

## 新增文件职责说明

### 1. 服务接口层 (core/interfaces/)

#### `image_processor_interface.py`
- **职责**: 定义图像处理服务的抽象接口
- **核心方法**: process_image, get_current_image, clear_image
- **依赖**: ConfigManagerInterface
- **特点**: 纯抽象,不含实现逻辑

#### `state_manager_interface.py`  
- **职责**: 定义应用状态管理的抽象接口
- **核心方法**: load_image, get_pipeline, set_active_tool
- **依赖**: 无直接服务依赖
- **特点**: 状态访问和修改的契约定义

#### `config_manager_interface.py`
- **职责**: 定义配置管理的抽象接口  
- **核心方法**: get_config, update_config, save_config
- **依赖**: 无服务依赖
- **特点**: 配置持久化的抽象定义

#### `app_controller_interface.py`
- **职责**: 定义应用控制的抽象接口
- **核心方法**: load_image, save_image, export_analysis  
- **依赖**: ImageProcessorInterface, StateManagerInterface
- **特点**: 业务流程协调的接口契约

### 2. 依赖注入容器 (core/dependency_injection/)

#### `dependency_container.py`
- **职责**: 管理服务注册和依赖解析
- **核心方法**: register_interface, resolve, build_with_dependencies
- **特点**: 替换ServiceRegistry,支持接口绑定和构造函数注入
- **功能**: 循环依赖检测,生命周期管理

#### `service_builder.py`  
- **职责**: 配置服务的依赖关系和创建策略
- **核心方法**: configure_core_services, configure_ui_services
- **特点**: 声明式依赖配置,简化ServiceFactory职责
- **功能**: 依赖关系图构建,服务创建策略定义

### 3. 应用引导器 (core/container/)

#### `application_bootstrap.py`
- **职责**: 应用启动时的依赖配置和初始化
- **核心方法**: bootstrap_application, configure_dependencies
- **特点**: 替换ServiceFactory的启动逻辑,专注依赖配置
- **功能**: 启动流程编排,错误处理和回滚

## 修改文件职责变更

### 1. 核心服务层修改

#### `image_processor.py` 【修改】
- **变更**: 实现ImageProcessorInterface,构造函数接收ConfigManagerInterface
- **移除**: 通过全局函数获取配置的逻辑
- **新增**: 接口方法实现,依赖注入构造函数
- **职责**: 纯图像处理逻辑,不涉及配置获取

#### `state_manager.py` 【修改】
- **变更**: 实现StateManagerInterface
- **移除**: `get_state_manager()`全局访问器函数
- **移除**: 全局变量`_state_manager_instance`
- **职责**: 应用状态管理,不提供全局访问

#### `app_controller.py` 【修改】
- **变更**: 实现AppControllerInterface,构造函数注入依赖
- **移除**: 通过context或全局函数获取服务
- **新增**: 明确的依赖声明
- **职责**: 业务流程协调,通过接口访问服务

### 2. 配置和上下文层修改

#### `config.py` 【修改】
- **变更**: ConfigManager实现ConfigManagerInterface  
- **移除**: `get_config_manager()`全局访问器函数
- **移除**: `set_global_config_manager()`全局设置函数
- **移除**: 全局变量`_global_config_manager`
- **职责**: 纯配置管理,不提供全局访问

#### `service_factory.py` 【简化】
- **变更**: 移除服务定位和获取逻辑
- **保留**: 基本的服务创建逻辑(向后兼容)
- **职责**: 简单的服务实例化,不负责依赖管理

### 3. UI层修改

#### `main_window.py` 【重构】
- **变更**: 构造函数接收接口类型参数而非AppContext
- **移除**: `_get_service`方法和所有context访问
- **移除**: 对AppContext的依赖
- **新增**: 明确的接口依赖声明
- **职责**: UI容器,通过注入的依赖提供功能

#### `main.py` 【重构】  
- **变更**: 使用DependencyContainer和ServiceBuilder配置依赖
- **移除**: AppContext创建和全局状态设置
- **移除**: `set_app_context`和`set_global_config_manager`调用
- **新增**: 依赖注入启动流程
- **职责**: 应用入口点,依赖配置和启动编排

## 删除文件说明

### 计划删除的文件
- `app/context.py` - AppContext及其全局访问器不再需要
- 旧版本的main_window.py和main.py(重构完成后)

### 删除原因
- **context.py**: 全局状态容器被依赖注入替代
- **旧版本文件**: 被重构后的版本完全替代

## 文件命名规范

### 1. 接口文件命名
- **模式**: `{服务名}_interface.py`
- **示例**: `image_processor_interface.py`
- **目的**: 明确标识接口文件,易于AI理解

### 2. 容器文件命名  
- **模式**: `{功能}_{类型}.py`
- **示例**: `dependency_container.py`, `service_builder.py`
- **目的**: 功能导向命名,避免generic名称

### 3. 实现文件命名
- **保持**: 现有文件名不变(除非有冲突)
- **原则**: 实现文件名体现具体功能而非抽象概念
- **避免**: 同名文件在不同目录下

## 职责边界原则

### 1. 接口层原则
- **纯抽象**: 只定义契约,不包含实现
- **稳定性**: 接口变更需要慎重考虑
- **最小化**: 只包含必要的方法定义

### 2. 实现层原则
- **单一职责**: 每个类只负责一个明确的功能
- **依赖明确**: 通过构造函数明确声明依赖
- **无全局访问**: 不使用任何全局变量或函数

### 3. 容器层原则
- **配置分离**: 依赖配置与业务逻辑分离
- **生命周期**: 明确管理服务的创建和销毁
- **错误处理**: 提供清晰的依赖解析错误信息

## 迁移注意事项

### 1. 代码清理要求
- **彻底移除**: 所有全局访问器函数必须完全删除
- **导入清理**: 移除对已删除函数的import语句  
- **注释更新**: 更新相关代码注释
- **测试同步**: 同步更新相关测试代码

### 2. 实施顺序
- **先新增后删除**: 先创建新文件,再删除旧文件
- **保持兼容**: 重构过程中保持功能完整性
- **分阶段验证**: 每阶段完成后进行完整测试

### 3. 质量控制
- **接口审查**: 确保接口设计合理完整
- **依赖验证**: 检查依赖关系的正确性
- **功能测试**: 验证重构后功能完整性

这个文件结构指导确保了重构过程的系统性和完整性,为AI实现提供了清晰的路径和边界。