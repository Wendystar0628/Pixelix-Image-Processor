# 事件总线集成代码文件结构指导

## 修改前的代码文件结构

```
app/core/
├── container/
│   ├── application_bootstrap.py
│   └── service_locator.py
├── initialization/
│   └── layered_initializer.py
├── managers/
│   └── state_manager.py
└── interfaces.py
```

## 修改后的代码文件结构

```
app/core/
├── container/
│   ├── application_bootstrap.py          # 修改：添加事件总线清理
│   └── service_locator.py               # 修改：添加事件总线获取方法
├── events/                              # 新增：事件系统目录
│   ├── __init__.py                      # 新增：模块初始化
│   ├── event_bus_impl.py               # 新增：事件总线实现
│   ├── event_type_registry.py          # 新增：事件类型注册表
│   └── event_payload_models.py         # 新增：事件载荷数据模型
├── initialization/
│   └── layered_initializer.py          # 修改：第1层添加事件总线初始化
├── managers/
│   └── state_manager.py                # 修改：使用事件发布状态变更
├── interfaces/
│   └── event_bus_interface.py          # 新增：事件总线接口定义
└── tests/                              # 新增：测试目录（如不存在）
    └── test_event_bus_impl.py          # 新增：事件总线实现测试
```

## 新增文件职责说明

### app/core/events/event_bus_impl.py
- 职责：事件总线的具体实现类
- 特点：线程安全、异常隔离、轻量级实现

### app/core/events/event_type_registry.py
- 职责：事件类型的注册表和常量定义
- 特点：集中管理事件类型，支持动态注册

### app/core/events/event_payload_models.py
- 职责：事件载荷的数据结构定义
- 特点：类型安全的事件数据模型

### app/core/interfaces/event_bus_interface.py
- 职责：事件总线的接口定义
- 特点：符合现有接口组织模式

### app/core/tests/test_event_bus_impl.py
- 职责：事件总线实现的单元测试
- 特点：简单的功能验证测试

## 修改文件的变更说明

### app/core/initialization/layered_initializer.py
- 变更：在initialize_layer_1_core_services方法中添加事件总线初始化
- 清理：无需清理，纯新增功能

### app/core/container/service_locator.py
- 变更：添加get_event_bus方法
- 清理：无需清理，纯新增功能

### app/core/container/application_bootstrap.py
- 变更：在cleanup_services方法中添加事件总线清理
- 清理：无需清理，纯新增功能

### app/core/managers/state_manager.py
- 变更：在状态变更方法中添加事件发布
- 清理：移除部分直接的回调调用（如果存在）

### app/core/interfaces/event_bus_interface.py
- 变更：新增事件总线接口定义文件
- 清理：无需清理，纯新增功能

## 代码清理指导

### 状态管理器清理
1. 识别StateManager中的直接回调调用
2. 将直接回调替换为事件发布
3. 移除不再需要的回调参数和方法

### 图像处理流程清理
1. 识别图像加载/处理完成后的直接通知调用
2. 替换为相应的事件发布
3. 移除不再需要的直接依赖注入

### 批处理进度通知清理
1. 识别批处理进度的直接更新调用
2. 替换为进度事件发布
3. 移除不再需要的进度回调接口

## 实现注意事项

1. **保持简单**：事件总线实现应尽可能简单，避免过度设计
2. **异常隔离**：确保单个事件处理器的异常不影响其他处理器
3. **线程安全**：使用适当的锁机制确保多线程环境下的安全性
4. **清理机制**：确保应用关闭时正确清理所有事件订阅
5. **向后兼容**：在重构过程中保持现有功能的完整性
## 
文件命名和位置改进说明

### 改进理由

1. **文件命名规范化**
   - `event_bus_core.py` → `event_bus_impl.py`：更明确表示这是实现类
   - `business_event_types.py` → `event_type_registry.py`：更通用，支持扩展
   - `event_data_models.py` → `event_payload_models.py`：更精确描述用途

2. **目录结构优化**
   - 接口文件放入`interfaces/`目录：符合现有架构模式
   - 测试文件放入`tests/`目录：如果不存在则创建

3. **架构一致性**
   - 遵循现有的接口-实现分离模式
   - 保持与其他核心组件的命名一致性
   - 符合分层架构的组织原则

### 命名合理性分析

✅ **合理的命名**：
- `event_bus_impl.py`：明确表示事件总线的实现
- `event_type_registry.py`：表示事件类型的注册管理
- `event_payload_models.py`：明确表示事件载荷数据
- `event_bus_interface.py`：符合接口命名规范

✅ **位置合理性**：
- `app/core/events/`：专门的事件系统目录
- `app/core/interfaces/`：接口定义的标准位置
- `app/core/tests/`：测试文件的标准位置

✅ **避免命名冲突**：
- 所有文件名都具有明确的业务含义
- 在整个项目中保持唯一性
- 易于AI理解和维护