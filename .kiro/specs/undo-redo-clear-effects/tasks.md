# 撤销重做功能修复和清除效果功能实现计划

- [ ] 1. 修复PipelineManager的现有问题
  - 修复redo()方法缺失pipeline_changed.emit()信号发射
  - 修复get_redo_stack_size()方法的缩进错误  
  - 清理所有方法中冗余的state_manager参数，直接使用self操作
  - 确保所有撤销重做方法正确发射信号
  - 清理向后兼容代码，移除未使用的导入
  - _需求: 1.1, 1.6_

- [ ] 2. 实现StateController的业务逻辑方法
  - 在StateController中添加undo_last_operation()方法
  - 在StateController中添加redo_last_operation()方法  
  - 在StateController中添加clear_all_effects()方法使用ClearPipelineCommand
  - 在StateController中添加can_undo()和can_redo()方法
  - 在StateController中添加has_effects()方法检查流水线是否为空
  - 添加完善的错误处理和用户反馈机制
  - _需求: 1.1, 1.2, 1.6, 2.4, 2.7_

- [ ] 3. 扩展AppController的委托方法
  - 在AppController中添加undo_last_operation()委托方法
  - 在AppController中添加redo_last_operation()委托方法
  - 在AppController中添加clear_all_effects()委托方法
  - 确保所有委托方法正确调用StateController的对应方法
  - 不在AppController中添加任何业务逻辑实现
  - _需求: 2.3_

- [ ] 4. 扩展ToolbarManager添加清除效果按钮
  - 在ToolbarManager中添加clear_effects_triggered信号
  - 在工具栏的保存按钮右边添加清除效果按钮
  - 将清除效果按钮添加到图像依赖actions列表中
  - 设置清除效果按钮的图标和提示文本
  - _需求: 2.1, 2.5, 3.4_

- [ ] 5. 扩展MenuManager添加清除效果菜单项
  - 在MenuManager中添加clear_effects_triggered信号
  - 在编辑菜单中添加清除所有效果菜单项
  - 为清除效果菜单项设置Ctrl+Shift+C快捷键
  - 将清除效果菜单项添加到图像依赖actions列表中
  - _需求: 2.2, 2.5, 3.4_

- [ ] 6. 更新MainWindow的信号连接
  - 在MainWindow的_connect_toolbar_signals()中连接清除效果信号
  - 在MainWindow的_connect_menu_signals()中连接清除效果信号
  - 确保所有新增信号正确连接到AppController的相应委托方法
  - _需求: 2.1, 2.2_

- [ ] 7. 完善UI状态管理机制
  - 确保撤销重做按钮根据StateController的can_undo/can_redo动态启用/禁用
  - 确保清除效果按钮根据StateController的has_effects动态启用/禁用
  - 验证所有相关按钮在无图像时被正确禁用
  - 添加操作完成后的状态消息显示
  - _需求: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 8. 清理命令系统的冗余代码
  - 修改AddOperationCommand和ClearPipelineCommand，移除state_manager依赖
  - 简化命令接口，直接操作PipelineManager
  - 清理未使用的导入和向后兼容代码
  - 统一错误处理机制
  - _需求: 1.1, 2.4_

- [ ] 9. 测试和验证功能完整性
  - 测试修复后的PipelineManager撤销重做功能
  - 测试StateController业务逻辑的完整工作流程
  - 测试清除效果功能的完整工作流程
  - 验证UI状态管理的正确性
  - 测试快捷键和菜单项功能
  - 进行端到端的用户场景测试
  - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

## 代码清理注意事项

### 必须清理的旧代码：

1. **PipelineManager清理**：
   - 移除所有方法签名中的`state_manager=None`参数
   - 清理方法体内对state_manager的调用
   - 移除向后兼容注释和代码

2. **命令系统清理**：
   - 从AddOperationCommand和ClearPipelineCommand中移除state_manager依赖
   - 简化execute()和undo()方法签名
   - 清理未使用的导入语句

3. **避免StateManager职责污染**：
   - 绝不在StateManager中添加业务逻辑方法
   - 保持StateManager的纯粹门面职责
   - 所有业务逻辑必须在StateController中实现

### 架构原则确认：

- **分层清晰**：UI → Controller → Manager → Core
- **职责单一**：每个组件专注自己的职责
- **松耦合**：通过信号和接口通信，避免直接依赖