# ServiceRegistry清理重构设计文档

## 架构设计

### 目标架构概览

```
app/
├── handlers/
│   ├── app_controller.py                  # 重构后，包含内部组件类
│   ├── processing_handler.py              # 保持不变
│   ├── preset_handler.py                  # 重构为依赖注入
│   └── file_handler.py                    # 保持不变
├── core/
│   ├── container/
│   │   ├── application_bootstrap.py       # 简化，移除ServiceRegistry
│   │   └── application_state.py           # 保持不变
│   └── dependency_injection/
│       └── service_builder.py             # 增强，支持所有服务构建
└── controllers/                           # ❌ 整个目录将被删除
```

### 核心组件设计

#### 1. AppController重构 (app/handlers/app_controller.py)

**职责**：应用总控制器，内部包含专业化组件类

**设计模式**：组合模式 + 依赖注入

```python
class AppController:
    """应用总控制器 - 重构版本"""
    
    def __init__(self, 
                 state_manager: StateManagerInterface,
                 image_processor: ImageProcessorInterface,
                 file_handler: FileHandler,
                 preset_handler: PresetHandler):
        # 核心依赖
        self.state_manager = state_manager
        
        # 内部组件（原独立控制器）
        self.file_ops = self.FileOperationsComponent(state_manager, file_handler)
        self.image_ops = self.ImageOperationsComponent(state_manager, image_processor)
        self.batch_ops = self.BatchOperationsComponent(state_manager)
        self.preset_ops = self.PresetOperationsComponent(preset_handler)
        
    class FileOperationsComponent:
        """文件操作组件（原FileIOController）"""
        
    class ImageOperationsComponent:
        """图像操作组件（原ImageOperationController）"""
        
    class BatchOperationsComponent:
        """批处理操作组件（原BatchProcessingController）"""
        
    class PresetOperationsComponent:
        """预设操作组件（原PresetController）"""
```

#### 2. PresetHandler重构 (app/handlers/preset_handler.py)

**职责**：预设处理业务逻辑

**重构内容**：移除ServiceRegistry，使用直接依赖注入

```python
class PresetHandler:
    """预设处理器 - 重构版本"""
    
    def __init__(self, state_manager: StateManagerInterface):
        self.state_manager = state_manager
        self.preset_manager = PresetManager()
```

#### 3. ApplicationBootstrap简化 (app/core/container/application_bootstrap.py)

**职责**：应用启动配置，纯依赖注入模式

**简化内容**：
- 移除ServiceRegistry创建和填充
- 直接使用DependencyContainer
- 清理向后兼容代码

```python
class ApplicationBootstrap:
    """应用引导器 - 简化版本"""
    
    def __init__(self, config: AppConfig, config_manager: ConfigManager):
        self.container = DependencyContainer()
        self.service_builder = ServiceBuilder(self.container)
```

## 详细设计

### 1. 文件变更清单

#### 删除的文件
```
app/controllers/                           # 整个目录删除
├── __init__.py
├── base_controller.py
├── app_controller.py                      # 内容迁移到handlers/app_controller.py
├── file_io_controller.py                  # 整合为AppController内部组件
├── image_loader_controller.py             # 整合为AppController内部组件
├── image_operation_controller.py          # 整合为AppController内部组件
├── batch_processing_controller.py         # 整合为AppController内部组件
├── preset_controller.py                   # 整合为AppController内部组件
├── dialog_controller.py                   # 整合为AppController内部组件
├── state_controller.py                    # 整合为AppController内部组件
└── signal_router.py                       # 功能整合到AppController

app/core/container/service_registry.py     # 完全删除
```

#### 重构的文件
```
app/handlers/app_controller.py             # 重构，包含内部组件
app/handlers/preset_handler.py             # 重构为依赖注入
app/core/container/application_bootstrap.py # 简化，移除ServiceRegistry
app/core/dependency_injection/service_builder.py # 增强构建能力
```

### 2. 内部组件设计

#### 2.1 FileOperationsComponent
- **职责**：文件相关操作（打开、保存、最近文件）
- **依赖**：StateManager, FileHandler
- **方法**：open_file, save_file, open_recent_file

#### 2.2 ImageOperationsComponent  
- **职责**：图像处理操作（滤镜、变换）
- **依赖**：StateManager, ImageProcessor
- **方法**：apply_simple_operation, get_available_operations

#### 2.3 BatchOperationsComponent
- **职责**：批处理相关操作
- **依赖**：StateManager
- **方法**：add_to_pool, show_import_dialog

#### 2.4 PresetOperationsComponent
- **职责**：预设相关操作
- **依赖**：PresetHandler
- **方法**：show_apply_preset_dialog, save_as_preset, delete_preset

### 3. 依赖注入流程

```
ApplicationBootstrap.bootstrap_application():
├── 配置依赖关系
├── 构建核心服务
│   ├── StateManager
│   ├── ImageProcessor  
│   ├── FileHandler
│   └── PresetHandler (新：直接依赖注入)
├── 构建UI服务
│   └── AppController (新：内部组件模式)
└── 完成服务连接
```

## 数据流设计

### 重构前数据流
```
UI → AppController → 子控制器(通过ServiceRegistry获取依赖) → 核心服务
```

### 重构后数据流  
```
UI → AppController → 内部组件(构造函数注入依赖) → 核心服务
```

## 错误处理设计

### 1. 依赖验证
- **构造时检查**：确保所有必需依赖都已注入
- **明确错误信息**：依赖缺失时提供清晰提示
- **快速失败**：启动时立即发现依赖问题

### 2. 组件初始化
- **逐步初始化**：按依赖顺序创建组件
- **错误传播**：组件初始化失败时正确传播错误
- **资源清理**：确保部分初始化时正确清理

## 测试策略

### 1. 关键节点测试
- **AppController创建**：验证内部组件正确初始化
- **依赖注入**：验证PresetHandler接收正确依赖
- **功能完整性**：验证核心操作正常工作

### 2. 简单集成测试
- **应用启动**：验证完整启动流程
- **基本操作**：验证文件操作、图像操作正常
- **预设功能**：验证预设保存和应用

## 性能考量

### 1. 内存优化
- **延迟创建**：内部组件按需创建
- **共享依赖**：避免重复创建相同服务
- **资源释放**：确保组件正确释放资源

### 2. 启动优化
- **减少文件数**：通过整合减少模块加载
- **简化依赖链**：直接依赖注入避免中间层
- **快速验证**：启动时快速验证关键依赖

## 兼容性保证

### 1. 公共接口保持
- **AppController接口**：所有公共方法签名不变
- **信号机制**：PyQt信号完全保留
- **返回值**：方法返回值类型和格式不变

### 2. 行为兼容
- **业务逻辑**：核心业务逻辑完全不变
- **错误处理**：错误类型和处理方式保持一致
- **配置访问**：配置读取和更新方式不变

## 风险缓解

### 1. 整合风险
- **职责明确**：内部组件保持单一职责
- **接口清晰**：组件间通过明确接口通信
- **测试验证**：关键路径必须有测试覆盖

### 2. 重构风险  
- **渐进迁移**：分阶段迁移代码到内部组件
- **功能验证**：每个阶段都验证功能完整性
- **回滚准备**：保留旧代码直到完全验证

## 总结

本设计采用组合模式将分散的控制器整合为AppController的内部组件，同时完全移除ServiceRegistry依赖。设计简洁务实，专注于解决架构不一致问题，为整个应用建立统一的依赖注入模式。通过减少文件数量和简化依赖关系，使代码更易于理解和维护。