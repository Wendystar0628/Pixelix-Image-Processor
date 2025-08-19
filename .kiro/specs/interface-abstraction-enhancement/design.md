# 接口抽象完善设计文档

## 设计概述

本设计基于现有的依赖注入架构，为Handler层的三个核心服务（FileHandler、ProcessingHandler、PresetHandler）添加接口抽象，提升系统的可测试性和可扩展性。设计遵循最小化原则，仅添加必要的接口定义，不改变现有功能。

## 架构设计

### 接口层次结构

```
app/core/interfaces/
├── file_handler_interface.py          # 文件处理接口
├── processing_handler_interface.py    # 图像处理接口  
├── preset_handler_interface.py        # 预设处理接口
└── __init__.py                        # 接口导出
```

### 依赖关系图

```
ApplicationBootstrap
    ↓ (配置绑定)
DependencyContainer
    ↓ (解析接口)
AppController → FileHandlerInterface
             → ProcessingHandlerInterface  
             → PresetHandlerInterface
```

## 组件设计

### 1. FileHandlerInterface设计

**职责：** 定义文件I/O操作的抽象接口

**核心方法：**
- `show_open_dialog(parent) -> str` - 显示打开文件对话框
- `show_save_dialog(parent) -> str` - 显示保存文件对话框  
- `load_image_from_path(path) -> tuple` - 从路径加载图像
- `save_image(image, path) -> None` - 保存图像到文件

### 2. ProcessingHandlerInterface设计

**职责：** 定义图像处理操作的抽象接口

**核心方法：**
- `apply_simple_operation(op_id) -> None` - 应用简单操作
- `clear_all_effects() -> None` - 清除所有效果
- `apply_operation(operation) -> None` - 应用操作对象

**信号定义：**
- `show_error_message` - 错误消息信号
- `show_info_message` - 信息消息信号

### 3. PresetHandlerInterface设计

**职责：** 定义预设管理操作的抽象接口

**核心方法：**
- `save_current_as_preset(parent) -> None` - 保存当前为预设
- `delete_preset(parent) -> None` - 删除预设
- `load_preset(preset_name) -> bool` - 加载预设

**信号定义：**
- `show_error_message` - 错误消息信号
- `show_info_message` - 信息消息信号

## 实现策略

### 1. 接口定义策略

- 使用ABC抽象基类确保接口契约
- 对于包含Qt信号的接口，使用自定义元类处理多重继承
- 接口方法仅定义必要的公共API，避免暴露内部实现细节

### 2. 现有类改造策略

- 现有Handler类继承对应接口
- 保持所有现有方法和功能不变
- 添加必要的类型注解以明确接口契约

### 3. 依赖注入集成策略

- 在ServiceBuilder中添加接口绑定配置
- 在ApplicationBootstrap中注册新的接口映射
- 更新AppController使用接口类型进行依赖注入

## 数据模型

### 接口元类设计

```python
class HandlerInterfaceMeta(type(QObject), type(ABC)):
    """处理QObject和ABC多重继承的元类"""
    pass
```

### 接口基础结构

```python
class BaseHandlerInterface(QObject, ABC, metaclass=HandlerInterfaceMeta):
    """Handler接口基类，包含通用信号定义"""
    
    show_error_message = pyqtSignal(str)
    show_info_message = pyqtSignal(str)
```

## 错误处理

### 接口实现验证

- 在依赖注入时验证实现类是否正确实现接口
- 在系统启动时检查接口绑定的完整性
- 提供清晰的错误消息指示缺失的接口实现

### 向后兼容性

- 保持现有API完全不变
- 确保现有调用代码无需修改
- 渐进式迁移，支持新旧代码共存

## 测试策略

### 接口契约测试

- 验证接口定义的完整性
- 确保实现类正确实现所有抽象方法
- 测试依赖注入容器的接口解析功能

### 集成测试

- 验证接口在实际应用场景中的正确工作
- 测试通过接口进行的服务交互
- 确保系统启动和运行的稳定性

## 部署考虑

### 代码清理

- 移除不再使用的直接类引用
- 更新import语句使用接口类型
- 清理过时的依赖注入配置

### 配置更新

- 更新依赖注入容器的绑定配置
- 确保所有服务使用接口进行依赖声明
- 验证系统启动流程的正确性