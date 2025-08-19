# 撤销重做和清除效果功能代码文件规范指导

## 概述

本文档列出了实现撤销重做功能修复和清除效果功能的详细文件结构变化，明确各文件的职责边界，确保架构分层清晰。

## 修改前文件结构

```
app/
├── controllers/
│   ├── app_controller.py               # 应用控制器，需要添加委托方法
│   └── state_controller.py             # 状态控制器，需要实现业务逻辑
├── core/
│   ├── commands/
│   │   └── operation_commands.py       # 命令系统，需要清理state_manager依赖
│   └── managers/
│       └── pipeline_manager.py         # 流水线管理器，需要修复信号和清理代码
├── ui/
│   ├── main_window.py                   # 主窗口，需要连接新信号
│   └── managers/
│       ├── toolbar_manager.py          # 工具栏管理器，需要添加清除按钮
│       └── menu_manager.py             # 菜单管理器，需要添加清除菜单项
```

## 修改后文件结构

```
app/
├── controllers/
│   ├── app_controller.py               # [修改] 添加委托方法，保持协调器职责
│   └── state_controller.py             # [修改] 实现撤销重做和清除效果业务逻辑
├── core/
│   ├── commands/
│   │   └── operation_commands.py       # [清理] 移除state_manager依赖，简化接口
│   └── managers/
│       └── pipeline_manager.py         # [修复] 修复信号发射和代码清理
├── ui/
│   ├── main_window.py                   # [修改] 连接新的清除效果信号
│   └── managers/
│       ├── toolbar_manager.py          # [扩展] 添加清除效果按钮和信号
│       └── menu_manager.py             # [扩展] 添加清除效果菜单项和快捷键
```

## 文件职责详细说明

### 修改的核心文件

#### 1. `app/controllers/app_controller.py` [修改]
**新增职责：**
- 添加委托方法：`undo_last_operation()`, `redo_last_operation()`, `clear_all_effects()`
- 将所有撤销重做相关请求委托给StateController

**保持职责：**
- 作为应用级协调器，不包含具体业务逻辑
- 负责子控制器间的协调

#### 2. `app/controllers/state_controller.py` [修改]
**新增职责：**
- 实现撤销重做业务逻辑：`undo_last_operation()`, `redo_last_operation()`
- 实现清除效果业务逻辑：`clear_all_effects()`
- 提供状态检查方法：`can_undo()`, `can_redo()`, `has_effects()`
- 处理错误情况和用户反馈

**设计原则：**
- 承担具体的业务逻辑实现
- 与StateManager交互获取PipelineManager
- 使用ClearPipelineCommand执行清除操作

#### 3. `app/core/managers/pipeline_manager.py` [修复和清理]
**修复内容：**
- 修复`redo()`方法缺失`pipeline_changed.emit()`
- 修复`get_redo_stack_size()`方法缩进错误

**清理内容：**
- 移除所有方法中的`state_manager=None`参数
- 清理向后兼容代码和注释
- 移除未使用的导入

**保持职责：**
- 管理操作流水线和命令栈
- 提供撤销重做的核心功能

#### 4. `app/core/commands/operation_commands.py` [清理]
**清理内容：**
- 从`AddOperationCommand`和`ClearPipelineCommand`移除state_manager依赖
- 简化`execute()`和`undo()`方法签名
- 直接操作PipelineManager实例

**保持职责：**
- 实现具体的命令操作
- 支持命令的执行和撤销

### 扩展的UI文件

#### 5. `app/ui/managers/toolbar_manager.py` [扩展]
**新增职责：**
- 添加`clear_effects_triggered`信号
- 在保存按钮右边添加清除效果按钮
- 将清除按钮加入图像依赖actions列表

**保持职责：**
- 管理工具栏的创建和状态
- 处理工具栏相关的用户交互

#### 6. `app/ui/managers/menu_manager.py` [扩展]
**新增职责：**
- 添加`clear_effects_triggered`信号
- 在编辑菜单添加"清除所有效果"菜单项
- 设置Ctrl+Shift+C快捷键

**保持职责：**
- 管理菜单的创建和状态
- 处理菜单相关的用户交互

#### 7. `app/ui/main_window.py` [修改]
**新增职责：**
- 在`_connect_toolbar_signals()`中连接清除效果信号
- 在`_connect_menu_signals()`中连接清除效果信号

**保持职责：**
- 作为UI的主要容器
- 协调各UI管理器的信号连接

## 严禁修改的文件

### `app/core/managers/state_manager.py` [严禁修改]
**保持原因：**
- StateManager应保持纯粹的门面职责
- 不应添加任何业务逻辑方法
- 避免违反单一职责原则

**现有职责：**
- 作为状态访问的统一门面
- 聚合核心管理器
- 信号转发和向后兼容

## 代码清理检查清单

### 必须清理的旧代码模式

1. **参数清理**：
   ```python
   # 旧代码（必须清理）
   def undo(self, state_manager=None):
       command.undo(state_manager)
   
   # 新代码
   def undo(self):
       command.undo()
   ```

2. **信号发射修复**：
   ```python
   # 旧代码（缺少信号）
   def redo(self, state_manager=None):
       # ... 重做逻辑
       # 缺少: self.pipeline_changed.emit()
   
   # 新代码
   def redo(self):
       # ... 重做逻辑
       self.pipeline_changed.emit()
   ```

3. **注释清理**：
   ```python
   # 必须移除的注释
   # "(向后兼容)"
   # "用于向后兼容"
   ```

### 架构合规性检查

1. **分层检查**：
   - UI层只发送信号，不直接调用业务逻辑
   - Controller层处理业务逻辑
   - Manager层提供核心功能

2. **职责检查**：
   - StateManager不包含业务逻辑方法
   - StateController包含具体的业务实现
   - AppController只包含委托方法

3. **依赖检查**：
   - 命令系统不依赖state_manager参数
   - UI组件通过信号与控制器通信
   - 所有组件保持松耦合

## 实现顺序建议

1. **第一阶段**：修复和清理核心组件
   - 修复PipelineManager的问题
   - 清理命令系统的冗余代码

2. **第二阶段**：实现业务逻辑
   - 在StateController中实现撤销重做逻辑

3. **第三阶段**：扩展UI组件
   - 添加工具栏和菜单的清除效果功能

4. **第四阶段**：集成和测试
   - 连接所有信号
   - 完善UI状态管理
   - 进行端到端测试