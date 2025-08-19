# Implementation Plan

- [x] 1. 重构初始化逻辑，移除预创建组件


  - 在 `app/ui/panels/analysis_panel.py` 中删除 `_init_widgets` 方法
  - 删除 `__init__` 方法中的 `self.matplotlib_widgets` 和 `self.pyqtgraph_widgets` 初始化
  - 将 `self.analysis_manager` 初始化为 `None`
  - 添加 `self.last_working_engine` 用于错误回退
  - _Requirements: 1.1, 1.4_

- [x] 2. 实现信号断开方法


  - 创建私有方法 `_disconnect_manager_signals(self)`
  - 实现安全的信号断开逻辑，包含异常处理
  - 断开 `analysis_tabs.currentChanged` 和 `analysis_calculator.analysis_finished` 信号
  - 添加日志记录用于调试
  - _Requirements: 2.1, 2.3_

- [x] 3. 实现资源清理方法




  - 创建私有方法 `_cleanup_current_engine(self)`
  - 实现以下清理步骤：
    - 调用 `_disconnect_manager_signals()` 断开信号
    - 清空 `analysis_tabs` 中的所有标签页
    - 对 `analysis_manager` 调用 `deleteLater()` 并设为 `None`
  - 添加异常处理和日志记录
  - _Requirements: 1.1, 1.4, 2.1_

- [x] 4. 实现组件创建方法


  - 创建私有方法 `_create_engine_widgets(self, engine_name: str)`
  - 根据 `engine_name` 创建对应的UI组件实例
  - 返回组件字典，创建失败时返回 `None`
  - 包含异常处理，记录创建失败的详细信息
  - _Requirements: 1.1, 3.1_

- [x] 5. 实现错误处理方法



  - 创建私有方法 `_handle_switch_error(self, error: Exception, target_engine: str)`
  - 实现错误回退逻辑：尝试切换回 `last_working_engine`
  - 如果回退失败，记录错误并可选择显示用户友好的错误消息
  - 添加详细的错误日志记录
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 6. 重构核心切换逻辑


  - 修改 `_switch_to_engine(self, engine_name)` 方法
  - 在方法开始时调用 `_cleanup_current_engine()`
  - 使用 `_create_engine_widgets()` 创建新组件
  - 创建新的 `AnalysisComponentsManager` 实例
  - 将新组件添加到 `analysis_tabs`
  - 添加完整的异常处理，失败时调用 `_handle_switch_error()`
  - 成功时更新 `last_working_engine`
  - _Requirements: 1.1, 1.4, 3.1_

- [x] 7. 优化应用切换方法


  - 修改 `_apply_engine_change(self)` 方法
  - 确保切换成功后触发分析更新
  - 添加用户反馈（如切换过程中的加载指示）
  - _Requirements: 1.3_



- [ ] 8. 添加日志和调试支持
  - 在关键方法中添加适当的日志记录
  - 使用Python的logging模块记录组件创建、销毁和错误信息
  - 添加调试级别的详细信息用于开发时排查问题


  - _Requirements: 1.5, 2.3, 3.3_

- [ ] 9. 验证和测试重构结果


  - 启动应用程序并加载测试图像
  - 在 "matplotlib" 和 "pyqtgraph" 之间进行多次切换（至少15次）
  - 使用任务管理器监控内存使用情况，确认无持续增长
  - 测试切换后的UI响应速度，确认与初始启动时一致
  - 测试错误场景：模拟组件创建失败，验证错误处理机制
  - 检查日志输出，确认所有操作都被正确记录
  - _Requirements: 1.2, 1.3, 3.1, 3.2_