# 核心层分层架构违规修复设计文档

## 设计概述

本设计通过引入UI抽象接口层和适配器模式，彻底消除核心层对UI层的直接依赖，建立清晰的分层架构边界。设计遵循依赖倒置原则，核心层定义所需的UI抽象接口，UI层实现这些接口，通过依赖注入实现松耦合集成。

## 架构设计

### 修复后的分层依赖关系

```
UI层 (UI Layer) - 具体实现
    ↑ (实现接口)
UI接口实现层 (UI Implementation Layer) - 新增
    ↑ (依赖接口)  
核心层 (Core Layer) - 定义抽象接口
    ↑ (依赖接口)
基础设施层 (Infrastructure Layer)
```

### UI抽象接口架构

```
app/core/interfaces/
├── ui_interaction_interface.py         # UI交互抽象接口
├── dialog_manager_interface.py         # 对话框管理抽象接口
├── interactive_widget_interface.py     # 交互式组件抽象接口
└── ui_service_factory_interface.py     # UI服务工厂抽象接口

app/ui/implementations/
├── __init__.py                         # 接口实现导出
├── dialog_implementation.py            # 对话框管理接口实现
├── widget_implementation.py            # 交互组件接口实现
└── ui_factory_implementation.py        # UI服务工厂接口实现
```

## 组件设计

### 1. InteractiveWidgetInterface设计

**职责：** 定义工具与UI组件交互的抽象接口

**核心方法：**
- `set_cursor(cursor: QCursor) -> None` - 设置鼠标光标
- `get_mouse_position() -> Tuple[int, int]` - 获取鼠标位置
- `update_display() -> None` - 更新显示内容
- `bind_mouse_event(event_type: str, handler: Callable) -> None` - 绑定鼠标事件

### 2. DialogManagerInterface设计

**职责：** 定义对话框管理操作的抽象接口

**核心方法：**
- `show_dialog(dialog_type: str, **kwargs) -> Any` - 显示指定类型对话框
- `close_dialog(dialog_id: str) -> None` - 关闭指定对话框
- `is_dialog_open(dialog_type: str) -> bool` - 检查对话框是否打开

### 3. UIServiceFactoryInterface设计

**职责：** 定义UI服务创建的抽象接口

**核心方法：**
- `create_dialog_manager() -> DialogManagerInterface` - 创建对话框管理器
- `create_interactive_widget() -> InteractiveWidgetInterface` - 创建交互组件
- `configure_ui_dependencies(main_window: Any) -> None` - 配置UI依赖

### 4. UI接口实现设计

**实现策略：**
- 接口实现模式：将具体UI组件包装为抽象接口的实现
- 封装性：隐藏UI层的具体实现细节
- 代理模式：代理核心层对UI层的所有访问

## 实现策略

### 1. 接口抽象策略

**设计原则：**
- 最小化接口：仅定义核心层真正需要的UI功能
- 行为导向：专注于行为抽象而非数据抽象
- 稳定性：接口应该稳定，不随UI实现变化而变化

### 2. 现有代码迁移策略

**分阶段迁移：**
1. **接口定义阶段**：创建所有UI抽象接口
2. **接口实现阶段**：实现UI层到接口的具体实现
3. **核心层迁移阶段**：将核心层的直接UI依赖改为接口依赖
4. **清理验证阶段**：移除直接导入并验证功能完整性

### 3. 依赖注入集成策略

**注册策略：**
- 在ServiceBuilder中注册UI抽象接口绑定
- 在ApplicationBootstrap中创建UI接口实现实例
- 通过构造函数注入将UI抽象传递给核心层组件

### 4. 错误隔离策略

**故障隔离：**
- UI层错误不应影响核心层稳定性
- 使用异常处理包装UI操作
- 提供降级机制应对UI组件不可用场景

## 数据模型

### UI交互接口结构

```python
class InteractiveWidgetInterface(ABC):
    """交互式组件抽象接口"""
    
    @abstractmethod
    def set_cursor(self, cursor: QCursor) -> None:
        """设置鼠标光标"""
        pass
    
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        pass
    
    @abstractmethod
    def update_display(self) -> None:
        """更新显示内容"""
        pass
    
    @abstractmethod
    def bind_mouse_event(self, event_type: str, handler: Callable) -> None:
        """绑定鼠标事件处理器"""
        pass
```

### 对话框管理接口结构

```python
class DialogManagerInterface(ABC):
    """对话框管理抽象接口"""
    
    @abstractmethod
    def show_dialog(self, dialog_type: str, **kwargs) -> Any:
        """显示指定类型的对话框"""
        pass
    
    @abstractmethod
    def close_dialog(self, dialog_id: str) -> None:
        """关闭指定的对话框"""
        pass
    
    @abstractmethod
    def is_dialog_open(self, dialog_type: str) -> bool:
        """检查指定类型的对话框是否打开"""
        pass
```

## 错误处理

### UI操作异常处理

**策略：**
- 所有UI适配器操作使用try-catch包装
- 提供默认的失败处理逻辑
- 记录UI操作失败的详细日志

### 接口不可用处理

**降级机制：**
- 当UI组件不可用时，提供空实现（Null Object Pattern）
- 核心层功能应该能够在UI不可用时继续运行
- 提供明确的错误反馈机制

## 测试策略

### 接口契约测试

**验证内容：**
- 验证所有UI抽象接口的完整性
- 确保适配器正确实现所有抽象方法
- 测试依赖注入容器的UI接口解析功能

### Mock实现测试

**测试优势：**
- 为核心层组件创建UI接口的Mock实现
- 独立测试核心层逻辑而无需真实UI
- 验证核心层与UI层的交互协议

### 集成测试

**验证范围：**
- 验证UI接口实现与真实UI组件的集成
- 测试完整的用户交互流程
- 确保UI抽象不影响用户体验

## 部署考虑

### 渐进式迁移

**迁移步骤：**
1. 创建UI抽象接口和接口实现
2. 更新依赖注入配置
3. 逐个迁移核心层组件到接口依赖
4. 移除所有直接UI导入
5. 验证功能完整性和性能

### 向后兼容性

**兼容性保证：**
- UI层现有功能完全保持不变
- 用户交互体验不受影响
- 现有UI组件无需修改内部逻辑

### 性能优化

**优化考虑：**
- 接口实现层应该是轻量级的代理
- 避免不必要的对象创建和方法调用
- 保持UI操作的响应性能