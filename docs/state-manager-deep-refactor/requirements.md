# StateManager深度重构需求文档

## 介绍

本项目旨在对StateManager进行深度重构，将其从承担过多职责的"上帝类"精炼为纯粹的状态管理门面。重构的核心目标是剥离工具状态管理和高层业务流程编排职责，让StateManager专注于作为"应用运行时状态的唯一访问点"和"统一门面"，严格遵循单一职责原则和架构分层设计。

通过对现有tool系统的深入分析，我们发现当前架构存在以下关键问题：
- `app/core/tools/tool_manager.py` 作为工具控制器，却将所有状态管理委托给StateManager
- `app/core/tools/base_tool.py` 直接依赖StateManager，造成紧耦合
- `app/core/models/tool_state_model.py` 提供了良好的数据模型，但未被充分利用
- `app/ui/managers/toolbar_manager.py` 职责清晰，无需修改

本次重构将通过协调这些tool相关文件，实现真正的职责分离和松耦合设计。

## 需求

### 需求 1: 为现有ToolManager赋能，实现状态自治

**用户故事:** 作为开发者，我希望现有的`app/core/tools/tool_manager.py`能够管理自身的状态，而不是将状态管理委托给StateManager，以实现真正的职责分离和模块独立性。

#### 验收标准

1. WHEN ToolManager初始化时 THEN 系统应该不再依赖StateManager作为构造参数，实现完全独立
2. WHEN 工具状态需要存储时 THEN 系统应该使用ToolStateModel数据模型替代原始字典，提升代码健壮性
3. WHEN ToolManager管理工具状态时 THEN 系统应该在ToolManager内部维护_active_tool_name和_tool_states属性
4. WHEN 工具状态发生变化时 THEN 系统应该由ToolManager直接发出tool_changed信号，不再依赖StateManager转发
5. WHEN 重构完成时 THEN ToolManager应该成为工具子系统的"唯一真实来源"，完全自治

### 需求 2: 上移高层业务流程编排到ProcessingHandler

**用户故事:** 作为开发者，我希望StateManager专注于状态管理，复杂的业务流程编排应该上移到ProcessingHandler层，以符合架构分层原则。

#### 验收标准

1. WHEN ProcessingHandler需要执行复杂图像加载流程时 THEN 系统应该在ProcessingHandler中编排多个StateManager原子操作
2. WHEN StateManager的load_image方法被调用时 THEN 系统应该只执行核心的图像数据设置，不包含业务流程编排
3. WHEN 需要协调多个子模块操作时 THEN 系统应该在ProcessingHandler中调用StateManager的多个原子方法
4. WHEN StateManager提供状态操作时 THEN 系统应该确保方法具有原子性特征，职责单一明确
5. WHEN 重构完成时 THEN StateManager的方法应该不包含复杂的多步骤业务逻辑

### 需求 3: 解耦BaseTool，实现工具独立性

**用户故事:** 作为开发者，我希望BaseTool及其子类不再直接依赖StateManager，实现工具的完全独立和可测试性。

#### 验收标准

1. WHEN BaseTool初始化时 THEN 系统应该移除对StateManager的直接依赖，提升工具的独立性
2. WHEN 工具需要执行操作时 THEN 系统应该通过信号机制发出操作指令，而不是直接调用StateManager
3. WHEN 工具完成操作时 THEN 系统应该由ToolManager监听工具信号并负责将操作提交给StateManager
4. WHEN 工具需要状态管理时 THEN 系统应该仅依赖工具自身的_tool_state属性和get_state/set_state方法
5. WHEN 重构完成时 THEN BaseTool应该成为完全独立的组件，可以独立测试和复用

### 需求 4: 建立纯粹的状态管理门面

**用户故事:** 作为开发者，我希望StateManager成为真正的状态管理门面，只负责聚合子模块和提供统一访问接口。

#### 验收标准

1. WHEN StateManager作为门面时 THEN 系统应该聚合重构后的ToolManager实例作为子模块
2. WHEN 外部组件需要访问工具状态时 THEN 系统应该通过StateManager代理访问ToolManager
3. WHEN ToolManager状态发生变化时 THEN 系统应该通过StateManager统一转发为state_changed信号
4. WHEN StateManager处理工具相关请求时 THEN 系统应该主要执行对ToolManager的代理调用
5. WHEN 需要向后兼容时 THEN 系统应该保留现有的工具相关属性和方法，但内部实现改为代理调用

### 需求 5: 保持完全的向后兼容性

**用户故事:** 作为用户，我希望深度重构后的StateManager完全不影响现有代码的运行，所有现有接口保持可用。

#### 验收标准

1. WHEN 现有代码调用StateManager的任何方法时 THEN 系统应该保持完全相同的行为和返回值
2. WHEN 现有UI组件监听StateManager信号时 THEN 系统应该继续发出相同的信号
3. WHEN 现有代码访问StateManager的属性时 THEN 系统应该返回相同的结果
4. WHEN 重构完成时 THEN 系统应该无需修改任何现有的调用代码
5. IF 方法实现发生变化 THEN 系统应该通过内部重新实现保持外部接口不变

### 需求 6: 增强ProcessingHandler的业务编排能力

**用户故事:** 作为开发者，我希望ProcessingHandler能够承担更多的业务流程编排职责，成为真正的业务逻辑协调器。

#### 验收标准

1. WHEN ProcessingHandler处理图像加载时 THEN 系统应该在ProcessingHandler中编排完整的加载流程
2. WHEN ProcessingHandler需要状态操作时 THEN 系统应该调用StateManager的原子化方法
3. WHEN ProcessingHandler处理复杂操作时 THEN 系统应该能够处理错误恢复和状态回滚
4. WHEN ProcessingHandler与StateManager交互时 THEN 系统应该保持清晰的职责边界
5. WHEN 新增复杂业务流程时 THEN 系统应该在ProcessingHandler中实现，不在StateManager中添加

### 需求 7: 确保代码质量和架构一致性

**用户故事:** 作为开发者，我希望深度重构后的代码严格遵循项目架构原则，展现卓越的代码质量。

#### 验收标准

1. WHEN 重构完成时 THEN 系统应该完全符合ARCHITECTURE.txt中定义的分层架构原则
2. WHEN StateManager处理状态时 THEN 系统应该体现高内聚低耦合的设计原则
3. WHEN 各个组件交互时 THEN 系统应该展现清晰的职责分离和依赖关系
4. WHEN 代码审查时 THEN 系统应该展现优秀的代码组织结构和可维护性
5. WHEN 新团队成员查看代码时 THEN 系统应该通过清晰的架构让其快速理解各组件职责