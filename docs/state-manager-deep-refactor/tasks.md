# StateManager深度重构实施计划

## 实施任务列表

### 阶段一：核心重构实施

- [ ] 1. 重构现有ToolManager，实现状态自治
  - 修改app/core/tools/tool_manager.py的__init__方法，移除state_manager依赖
  - 在ToolManager内部添加_active_tool_name和_tool_states属性
  - 使用ToolStateModel替代原始字典管理工具状态
  - 修改所有状态相关方法，操作内部状态而非委托StateManager
  - 添加operation_created信号用于工具操作完成通知
  - _需求: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 2. 解耦BaseTool，实现工具独立性
  - 修改app/core/tools/base_tool.py的__init__方法，移除state_manager依赖
  - 添加operation_completed信号用于发出操作完成通知
  - 添加_emit_operation方法供具体工具使用
  - 更新所有具体工具类，使用信号机制替代直接调用StateManager
  - 确保工具完全独立，可独立测试
  - _需求: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 3. 净化StateManager，建立纯粹门面
  - 从StateManager中移除所有工具状态相关的私有属性
  - 在StateManager.__init__中创建重构后的ToolManager实例（无依赖参数）
  - 修改工具相关方法为ToolManager的代理调用
  - 连接ToolManager信号并实现转发机制
  - 保持向后兼容的公共接口不变
  - _需求: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 4. 重构StateManager为原子化状态操作
  - 创建set_image_data()原子方法仅设置图像数据
  - 创建set_proxy_image_data()原子方法仅设置代理图像数据
  - 创建clear_image_data()原子方法仅清除图像数据
  - 将reset_all_processing_state()方法公开为原子操作
  - 确保所有新方法都是原子性的，不包含业务编排
  - _需求: 2.4, 4.4_

- [ ] 5. 增强ProcessingHandler的业务编排能力
  - 创建load_image_complete()方法处理完整的图像加载流程
  - 创建clear_image_complete()方法处理完整的图像清除流程
  - 创建load_image_proxy_complete()方法处理代理图像加载流程
  - 实现错误处理和状态回滚机制
  - 确保ProcessingHandler调用StateManager的原子方法
  - _需求: 2.1, 2.3, 6.1, 6.3_

- [ ] 6. 修改StateManager的复合方法为委托调用
  - 修改load_image()方法内部委托给ProcessingHandler
  - 修改clear_image()方法内部委托给ProcessingHandler
  - 修改load_image_proxy()方法内部委托给ProcessingHandler
  - 保持方法签名和外部行为完全不变
  - 确保信号发射行为保持一致
  - _需求: 2.2, 5.1, 5.2_

- [ ] 7. 实现ProcessingHandler的获取机制
  - 创建get_processing_handler()函数或单例模式
  - 确保StateManager可以获取ProcessingHandler实例
  - 处理循环依赖问题（如使用延迟导入）
  - _需求: 6.2, 6.4_

### 阶段二：验证和测试

- [ ] 8. 验证tool系统重构效果
  - 验证ToolManager完全独立，不依赖StateManager
  - 验证BaseTool通过信号机制与外界通信
  - 验证ToolStateModel正确管理工具状态数据
  - 测试工具激活/停用的完整流程
  - 验证工具操作完成信号的正确处理
  - _需求: 1.5, 3.5, 4.5_

- [ ] 9. 验证向后兼容性
  - 确保所有现有StateManager工具相关方法行为不变
  - 验证现有ToolManager接口保持兼容
  - 确保UI层（ToolbarManager）无需修改
  - 验证重构不影响任何现有代码的运行
  - _需求: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 10. 创建核心功能单元测试
  - 测试重构后ToolManager的状态管理功能
  - 测试解耦后BaseTool的独立性
  - 测试StateManager的工具门面功能
  - 测试ProcessingHandler的业务编排逻辑
  - 测试错误处理和状态回滚机制
  - _需求: 7.1, 7.2, 7.3_

- [ ] 11. 创建集成测试验证重构效果
  - 测试StateManager与重构后ToolManager的集成
  - 测试ToolManager与解耦后BaseTool的集成
  - 测试工具操作信号链路的完整性
  - 测试复杂工具使用场景的端到端执行
  - _需求: 7.3, 7.4_

### 阶段三：完善和部署

- [ ] 12. 验证架构一致性和代码质量
  - 检查重构后的tool系统是否符合ARCHITECTURE.txt定义的分层原则
  - 验证ToolManager、BaseTool、StateManager的职责分离
  - 检查工具子系统的高内聚低耦合设计实现
  - 确保tool相关代码组织结构清晰且易于理解
  - 验证ToolStateModel的正确使用和数据一致性
  - _需求: 7.1, 7.2, 7.4, 7.5_

- [ ] 13. 运行完整的回归测试
  - 执行所有现有的单元测试确保通过
  - 运行UI交互测试验证工具栏和工具切换功能正常
  - 测试应用的完整启动和关闭流程
  - 验证核心功能（图像处理、工具操作等）的正常工作
  - 测试工具状态在应用重启后的持久化
  - _需求: 5.1, 5.2, 5.3_

- [ ] 14. 最终清理和文档更新
  - 更新StateManager类的文档字符串，明确其门面角色和tool聚合功能
  - 更新ToolManager类的文档，说明其状态自治的设计
  - 更新BaseTool类的文档，说明其独立性和信号机制
  - 移除已注释的旧代码和临时兼容性代码
  - 清理不再使用的导入和依赖
  - 进行最终的代码审查和质量检查
  - _需求: 4.1, 4.2, 7.2, 7.4_