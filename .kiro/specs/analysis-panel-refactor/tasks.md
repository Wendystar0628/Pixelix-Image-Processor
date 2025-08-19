# Implementation Plan

- [x] 1. 创建分析组件工厂类


  - 在 `app/ui/panels/managers/` 目录下创建 `analysis_widget_factory.py`
  - 实现 `AnalysisWidgetFactory` 类，包含静态方法 `create_widgets(engine_name)`
  - 将组件创建逻辑从 `AnalysisPanel._create_engine_widgets` 迁移过来
  - 添加 `get_supported_engines()` 方法返回支持的引擎列表
  - 包含完整的错误处理和日志记录
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 2. 创建渲染引擎管理器类


  - 在 `app/ui/panels/managers/` 目录下创建 `rendering_engine_manager.py`
  - 实现 `RenderingEngineManager` 类的基本结构和初始化方法
  - 将信号管理逻辑从 `AnalysisPanel._disconnect_manager_signals` 迁移过来
  - 将资源清理逻辑从 `AnalysisPanel._cleanup_current_engine` 迁移过来
  - 将错误处理逻辑从 `AnalysisPanel._handle_switch_error` 迁移过来
  - _Requirements: 1.1, 1.2, 1.3_



- [ ] 3. 实现引擎切换核心逻辑
  - 在 `RenderingEngineManager` 中实现 `switch_engine` 方法
  - 将切换逻辑从 `AnalysisPanel._switch_to_engine` 迁移过来
  - 使用 `AnalysisWidgetFactory` 创建组件
  - 实现完整的错误处理和回退机制
  - 添加状态管理（当前引擎、上一个工作引擎等）


  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 4. 添加管理器的公共接口
  - 在 `RenderingEngineManager` 中添加 `get_current_engine()` 方法
  - 添加 `get_analysis_manager()` 方法
  - 添加 `request_analysis_update()` 方法


  - 添加 `clear_all_analyses()` 方法
  - 确保所有方法都有适当的错误处理
  - _Requirements: 3.3_

- [ ] 5. 重构 AnalysisPanel 类
  - 移除 `AnalysisPanel` 中的复杂业务逻辑方法

  - 删除 `_disconnect_manager_signals`, `_cleanup_current_engine`, `_create_engine_widgets`, `_handle_switch_error` 方法
  - 修改 `_switch_to_engine` 方法，委托给 `RenderingEngineManager`
  - 简化 `_apply_engine_change` 方法
  - 在 `__init__` 中创建 `RenderingEngineManager` 实例
  - _Requirements: 3.1, 3.2_


- [ ] 6. 更新导入和依赖
  - 在 `AnalysisPanel` 中导入新的管理器类
  - 移除不再需要的直接组件导入
  - 确保所有依赖关系正确
  - 更新类型注解
  - _Requirements: 4.1_



- [ ] 7. 保持接口兼容性
  - 确保 `request_analysis_update()` 方法保持原有签名
  - 确保 `clear_all_analyses()` 方法保持原有签名
  - 确保 `rendering_engine_changed` 信号正常工作
  - 验证所有公共接口的行为与重构前一致
  - _Requirements: 4.1, 4.2, 4.3_


- [ ] 8. 测试重构结果
  - 启动应用程序并验证基本功能
  - 测试渲染引擎切换功能
  - 测试多次切换的性能表现
  - 测试错误处理和回退机制
  - 验证内存使用情况
  - 检查日志输出的完整性
  - _Requirements: 4.2_

- [x] 9. 代码清理和优化

  - 移除不再使用的导入语句
  - 优化日志记录的一致性
  - 添加必要的文档字符串
  - 确保代码风格一致
  - 验证没有遗留的死代码
  - _Requirements: 3.1_