# 核心层分层架构违规修复代码结构指导

## 修改前后文件结构对比

### 修改前结构（存在分层违规）
```
app/
├── core/
│   ├── interfaces/
│   │   └── (现有接口文件)
│   ├── container/
│   │   └── ui_service_factory.py          # 直接导入app.ui.managers.dialog_manager
│   ├── tools/
│   │   └── base_tool.py                   # 直接导入app.ui.widgets.interactive_image_label
│   └── ...
├── ui/
│   ├── managers/
│   │   └── dialog_manager.py              # 被核心层直接导入
│   ├── widgets/
│   │   └── interactive_image_label.py     # 被核心层直接导入
│   └── ...
```

### 修改后结构（分层合规）
```
app/
├── core/
│   ├── interfaces/
│   │   ├── interactive_widget_interface.py       # 新增：交互组件抽象接口
│   │   ├── dialog_manager_interface.py           # 新增：对话框管理抽象接口
│   │   ├── ui_service_factory_interface.py       # 新增：UI服务工厂抽象接口
│   │   └── (现有接口文件)
│   ├── container/
│   │   └── ui_service_factory.py                 # 修改：使用UI抽象接口
│   ├── tools/
│   │   └── base_tool.py                          # 修改：使用交互组件抽象接口
│   └── ...
├── ui/
│   ├── implementations/                          # 新增：核心接口实现层
│   │   ├── __init__.py                           # 实现层导出
│   │   ├── widget_implementation.py              # 新增：交互组件实现
│   │   ├── dialog_implementation.py              # 新增：对话框管理实现
│   │   └── ui_factory_implementation.py          # 新增：UI服务工厂实现
│   ├── managers/
│   │   └── dialog_manager.py                     # 保持不变：具体实现
│   ├── widgets/
│   │   └── interactive_image_label.py            # 保持不变：具体实现
│   └── ...
```

## 新增文件职责说明

### `app/core/interfaces/interactive_widget_interface.py`
- **职责**: 定义核心层与UI交互组件的抽象接口
- **核心功能**: 鼠标操作、光标设置、事件绑定、显示更新
- **依赖**: 无外部依赖，纯接口定义
- **约束**: 仅定义核心层真正需要的UI交互能力

### `app/core/interfaces/dialog_manager_interface.py`
- **职责**: 定义对话框管理操作的抽象接口
- **核心功能**: 对话框创建、显示、关闭、状态查询
- **依赖**: 无外部依赖，纯接口定义
- **约束**: 避免暴露UI层的具体实现细节

### `app/core/interfaces/ui_service_factory_interface.py`
- **职责**: 定义UI服务创建的抽象工厂接口
- **核心功能**: UI组件创建、依赖配置、服务组装
- **依赖**: 依赖其他UI抽象接口
- **约束**: 使用抽象工厂模式，不直接创建具体实现

### `app/ui/implementations/widget_implementation.py`
- **职责**: 实现InteractiveWidgetInterface，适配InteractiveImageLabel
- **核心功能**: 提供UI交互能力的接口实现，封装具体UI组件行为
- **依赖**: InteractiveImageLabel、InteractiveWidgetInterface
- **约束**: 仅作为接口实现，不添加额外业务逻辑，保持轻量级代理模式

### `app/ui/implementations/dialog_implementation.py`
- **职责**: 实现DialogManagerInterface，适配DialogManager
- **核心功能**: 提供对话框管理能力的接口实现，封装对话框操作逻辑
- **依赖**: DialogManager、DialogManagerInterface
- **约束**: 保持原有对话框功能完整性，确保接口契约的正确实现

### `app/ui/implementations/ui_factory_implementation.py`
- **职责**: 实现UIServiceFactoryInterface，适配UIServiceFactory
- **核心功能**: 提供UI服务创建能力的接口实现，返回标准接口类型
- **依赖**: UIServiceFactory、各UI抽象接口
- **约束**: 返回的服务必须是接口类型，隐藏具体实现细节

## 修改文件变更说明

### `app/core/interfaces/__init__.py`
- **变更**: 添加三个新UI抽象接口的导出
- **新增导出**: InteractiveWidgetInterface, DialogManagerInterface, UIServiceFactoryInterface
- **清理**: 无需清理，仅添加导出

### `app/core/container/ui_service_factory.py`
- **变更**: 使用DialogManagerInterface而非直接导入DialogManager
- **清理**: 移除`from app.ui.managers.dialog_manager import DialogManager`
- **新增**: 通过依赖注入获取UI抽象接口
- **更新**: 构造函数接受UI工厂接口参数

### `app/core/tools/base_tool.py`
- **变更**: 使用InteractiveWidgetInterface而非直接导入InteractiveImageLabel
- **清理**: 移除`from ...ui.widgets.interactive_image_label import InteractiveImageLabel`
- **新增**: 通过依赖注入获取交互组件接口
- **更新**: 所有UI操作通过接口方法调用

### `app/core/dependency_injection/service_builder.py`
- **变更**: 添加UI抽象接口的绑定配置
- **新增**: 注册UI接口到适配器的映射关系
- **更新**: 确保UI抽象接口可以正确解析

### `app/core/container/application_bootstrap.py`
- **变更**: 创建UI适配器实例并注册到容器
- **新增**: UI适配器的实例化逻辑
- **更新**: UI服务启动流程配置

## 代码实现模式

### UI抽象接口定义模式

```python
from abc import ABC, abstractmethod
from typing import Tuple, Callable, Any
from PyQt6.QtGui import QCursor

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

### UI接口实现模式

```python
from app.core.interfaces import InteractiveWidgetInterface
from app.ui.widgets.interactive_image_label import InteractiveImageLabel

class WidgetImplementation(InteractiveWidgetInterface):
    """交互组件接口实现"""
    
    def __init__(self, widget: InteractiveImageLabel):
        self._widget = widget
    
    def set_cursor(self, cursor: QCursor) -> None:
        """设置鼠标光标"""
        self._widget.setCursor(cursor)
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        pos = self._widget.mapFromGlobal(QCursor.pos())
        return (pos.x(), pos.y())
    
    def update_display(self) -> None:
        """更新显示内容"""
        self._widget.update()
    
    def bind_mouse_event(self, event_type: str, handler: Callable) -> None:
        """绑定鼠标事件处理器"""
        # 实现事件绑定逻辑
        pass
```

### 核心层使用模式

```python
from app.core.interfaces import InteractiveWidgetInterface

class BaseTool:
    """基础工具类"""
    
    def __init__(self, interactive_widget: InteractiveWidgetInterface):
        self.interactive_widget = interactive_widget
    
    def set_tool_cursor(self, cursor: QCursor):
        """设置工具光标"""
        self.interactive_widget.set_cursor(cursor)
    
    def handle_mouse_operation(self):
        """处理鼠标操作"""
        pos = self.interactive_widget.get_mouse_position()
        # 使用位置信息进行处理
```

### UI服务工厂实现模式

```python
from app.core.interfaces import UIServiceFactoryInterface, DialogManagerInterface, InteractiveWidgetInterface
from app.ui.managers.dialog_manager import DialogManager
from app.ui.widgets.interactive_image_label import InteractiveImageLabel

class UIFactoryImplementation(UIServiceFactoryInterface):
    """UI服务工厂接口实现"""
    
    def __init__(self, ui_service_factory):
        self._ui_factory = ui_service_factory
    
    def create_dialog_manager(self) -> DialogManagerInterface:
        """创建对话框管理器接口实现"""
        dialog_manager = self._ui_factory.create_dialog_manager()
        return DialogImplementation(dialog_manager)
    
    def create_interactive_widget(self) -> InteractiveWidgetInterface:
        """创建交互组件接口实现"""
        widget = self._ui_factory.create_interactive_widget()
        return WidgetImplementation(widget)
    
    def configure_ui_dependencies(self, main_window: Any) -> None:
        """配置UI依赖关系"""
        self._ui_factory.configure_ui_dependencies(main_window)
```

### 依赖注入配置模式

```python
# 在ServiceBuilder中
def configure_ui_dependencies(self):
    """配置UI依赖关系"""
    # 注册UI抽象接口绑定
    self.container.register_interface(
        InteractiveWidgetInterface, 
        WidgetImplementation
    )
    self.container.register_interface(
        DialogManagerInterface, 
        DialogImplementation
    )
    self.container.register_interface(
        UIServiceFactoryInterface, 
        UIFactoryImplementation
    )

# 在ApplicationBootstrap中
def create_ui_implementations(self, main_window):
    """创建UI接口实现"""
    interactive_widget = main_window.get_interactive_widget()
    widget_impl = WidgetImplementation(interactive_widget)
    
    self.container.register_instance(
        InteractiveWidgetInterface, 
        widget_impl
    )
```

## 代码清理检查清单

### 必须移除的代码模式
1. **核心层直接UI导入**: `from app.ui.* import *`
2. **具体UI组件引用**: 直接使用InteractiveImageLabel、DialogManager等
3. **跨层直接实例化**: 在核心层直接创建UI组件实例
4. **硬编码UI依赖**: 不通过依赖注入的UI访问

### 必须添加的代码模式
1. **接口导入**: `from app.core.interfaces import *Interface`
2. **构造函数注入**: `def __init__(self, ui_interface: UIInterface)`
3. **接口方法调用**: `self.ui_interface.method_name()`
4. **接口实现注册**: 在依赖注入容器中注册接口绑定

### 具体清理步骤
1. **搜索定位**: 使用`grep -r "from app.ui" app/core/`定位所有直接UI导入
2. **逐文件修改**: 按文件逐个替换直接UI依赖为接口依赖
3. **移除导入**: 删除所有`from app.ui.*`导入语句
4. **更新构造函数**: 添加UI接口参数
5. **更新方法调用**: 将直接UI操作改为接口调用
6. **测试验证**: 验证功能完整性和正确性

### 验证清理完整性命令
```bash
# 验证核心层无直接UI导入
grep -r "from app.ui" app/core/

# 验证核心层无UI组件引用
grep -r "InteractiveImageLabel\|DialogManager" app/core/ --exclude-dir=interfaces

# 验证接口使用正确性
grep -r "Interface" app/core/ | grep "import\|:"

# 验证接口实现完整性
find app/ui/implementations/ -name "*.py" -exec grep -l "Interface" {} \;
```

## 架构合规性验证

### 分层依赖检查
- 核心层只能依赖自身定义的抽象接口
- UI层实现核心层定义的接口
- 接口实现层作为UI层与核心层的桥梁

### 依赖方向验证
- 依赖方向：UI层 → 核心层接口
- 禁止方向：核心层 → UI层实现
- 桥接方式：通过接口实现连接两层

### 接口完整性检查
- 所有核心层需要的UI功能都有对应接口
- 所有接口都有对应的具体实现
- 依赖注入容器正确配置接口绑定