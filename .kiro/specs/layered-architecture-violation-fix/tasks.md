# 分层架构违反问题修复实施计划

## 实施概述

本实施计划将分层架构违反问题的修复分解为可管理的编码任务。每个任务都专注于特定的代码实现，按照从基础设施到应用层的顺序逐步重构系统，确保在每个阶段都能保持系统的可运行性。

## 任务列表

### 阶段1：建立新的架构基础

- [ ] 1. 创建事件总线和命令处理基础设施




  - 创建目录：`app/shared/events/`, `app/shared/commands/`
  - 实现 `EventBus` 类，支持事件的发布、订阅和异步处理
  - 实现 `Command` 和 `CommandHandler` 基类，建立命令模式基础
  - 创建 `Event` 和相关事件类型的数据模型
  - 编写事件总线和命令处理的单元测试
  - **清理步骤**：无需清理，这是新增功能
  - _需求: 1.2, 2.2, 5.3_

- [ ] 2. 实现分层架构检查工具



  - 创建 `ArchitectureComplianceChecker` 类，检查模块间依赖关系
  - 实现循环依赖检测算法
  - 创建架构违反报告生成器
  - 编写架构检查工具的测试用例
  - _需求: 7.1, 7.2, 7.3_






- [ ] 3. 重构目录结构以反映真正的分层架构

  - 创建新的目录结构：`app/layers/application/`, `app/layers/presentation/`, `app/layers/controller/`, `app/layers/business/`, `app/layers/infrastructure/`
  - 创建各层的 `__init__.py` 文件和接口定义
  - 实现层级导入控制机制
  - 更新构建脚本以支持新的目录结构
  - _需求: 4.1, 4.2_

### 阶段2：重构基础设施层

- [ ] 4. 重构配置服务为纯基础设施组件






  - 创建目录：`app/layers/infrastructure/configuration/`
  - 将 `ConfigManager` 移动到新目录
  - 实现 `ConfigurationServiceInterface` 接口
  - 创建配置服务的工厂类
  - 移除配置服务对业务层的任何依赖
  - **清理步骤**：
    - 删除 `app/infrastructure/configuration/config_manager.py` 原文件
    - 更新所有导入 `app.infrastructure.configuration.config_manager` 的代码
    - 移除 `app/core/configuration/` 中的配置相关代码
  - _需求: 1.1, 2.1_

- [x] 5. 实现文件系统服务


  - 创建 `FileSystemServiceInterface` 接口
  - 实现 `FileSystemService` 类，提供文件操作功能
  - 将现有的文件处理逻辑迁移到基础设施层
  - 编写文件系统服务的单元测试
  - _需求: 1.1, 4.1_

- [x] 6. 创建简化的日志基础设施

  - 实现 `SimpleLogger` 类，提供基本日志功能
  - 集成架构违反检查的日志记录
  - 编写日志组件的测试
  - _需求: 7.1_

### 阶段3：重构业务层

- [ ] 7. 重构图像处理引擎为纯业务组件


  - 创建目录：`app/layers/business/processing/`
  - 将 `ImageProcessor` 移动到新目录
  - 移除对上层的任何直接依赖
  - 实现业务事件发布机制
  - 重构图像处理流水线，使其完全无状态
  - **清理步骤**：
    - 删除 `app/core/engines/image_processor.py` 原文件
    - 更新所有导入 `app.core.engines.image_processor` 的代码
    - 移除 `ImageProcessor` 中任何对控制器或UI层的引用
    - 清理 `app/core/__init__.py` 中的相关导入
  - _需求: 1.1, 1.2_

- [ ] 8. 重构状态管理器
  - 将 `StateManager` 移动到 `app/layers/business/state/`
  - 实现状态变化事件发布
  - 移除对控制器层的直接调用
  - 创建状态管理器的接口定义
  - _需求: 1.1, 1.2, 5.1_

- [ ] 9. 实现业务事件发布器
  - 创建 `BusinessEventPublisher` 类
  - 定义业务层事件类型（状态变化、处理完成等）
  - 实现事件的异步发布机制
  - 编写业务事件发布的测试
  - _需求: 1.2, 2.2_

### 阶段4：重构控制器层

- [ ] 10. 创建新的应用控制器架构
  - 实现 `ApplicationController` 基类
  - 创建专门的控制器：`ImageOperationController`, `FileOperationController`, `BatchProcessingController`
  - 实现控制器的命令处理机制
  - 建立控制器与业务层的事件订阅关系
  - _需求: 2.1, 2.2, 3.2_

- [ ] 11. 重构文件操作控制器
  - 将文件操作逻辑从 `FileHandler` 重构为 `FileOperationController`
  - 实现文件操作命令处理
  - 建立与基础设施层文件服务的连接
  - 移除对UI层的直接依赖
  - _需求: 3.1, 3.2_

- [ ] 12. 重构图像操作控制器
  - 将图像操作逻辑从 `ProcessingHandler` 重构为 `ImageOperationController`
  - 实现图像操作命令的路由和处理
  - 建立与业务层图像处理引擎的连接
  - 实现操作结果的事件发布
  - _需求: 3.1, 3.2_

- [ ] 12.1 重构批处理业务层
  - 创建 `app/layers/business/batch/` 目录结构
  - 实现 `BatchService` 核心业务服务（无状态）
  - 实现 `JobManager` 作业管理服务，发布作业状态事件
  - 实现 `PoolManager` 图像池管理服务，发布池状态变化事件
  - 创建 `BatchProcessor` 纯批处理算法执行引擎
  - _需求: 1.1, 1.2, 2.2_

- [ ] 12.2 重构批处理控制器
  - 创建 `BatchProcessingController` 处理批处理命令
  - 实现批处理命令路由：`create_job`, `add_to_pool`, `execute_batch`
  - 建立与业务层批处理服务的连接
  - 订阅业务层事件，转换为UI层可理解的事件
  - 移除对 `BatchProcessingHandler` 的依赖
  - _需求: 2.1, 2.2, 3.2_

- [ ] 12.3 重构批处理基础设施层
  - 创建 `app/layers/infrastructure/batch/` 目录结构
  - 实现 `JobStorage` 作业数据持久化存储
  - 实现 `PoolStorage` 图像池数据持久化存储
  - 重构 `BatchWorker` 后台批处理执行线程
  - 实现 `ProgressTracker` 批处理进度跟踪器
  - _需求: 1.1, 4.1_

### 阶段5：重构表示层

- [ ] 13. 重构主窗口以消除直接依赖
  - 创建目录：`app/layers/presentation/windows/`
  - 将 `MainWindow` 移动到新目录
  - 修改构造函数，只接收控制器接口
  - 实现基于事件的UI更新机制
  - 移除对 `handlers` 和 `features` 层的直接导入
  - 建立UI事件到控制器命令的映射
  - **清理步骤**：
    - 删除 `app/ui/main_window.py` 原文件
    - 删除构造函数中的以下参数：`state_manager`, `image_processor`, `analysis_calculator`, `app_controller`, `batch_processing_handler`
    - 移除所有 `from app.handlers` 和 `from app.features` 的导入
    - 删除所有直接调用业务层方法的代码（如 `self.state_manager.load_image()`）
    - 清理 `app/application_startup.py` 中创建MainWindow的相关代码
  - _需求: 3.1, 3.2, 3.3_

- [ ] 14. 重构对话框管理器
  - 修改 `DialogManager` 以使用控制器接口
  - 实现对话框参数变化的事件发布
  - 移除对处理器的直接依赖
  - 建立对话框与控制器的松耦合连接
  - _需求: 3.1, 3.2_

- [ ] 15. 重构批处理UI组件
  - 创建 `app/layers/presentation/panels/batch/` 目录结构
  - 重构 `BatchProcessingMainPanel` 只与控制器接口交互
  - 重构 `JobListPanel`, `JobDetailPanel`, `ImagePoolPanel` 使用事件机制
  - 重构 `ExportSettingsPanel` 移除对业务层的直接依赖
  - 实现基于事件的UI状态更新机制
  - 将用户操作转换为命令发送给控制器
  - 移除所有对 `app.features.batch_processing` 的导入
  - _需求: 3.1, 3.2, 3.3_

- [ ] 15.1 清理批处理遗留代码
  - 删除 `app/features/batch_processing/batch_coordinator.py`
  - 删除 `app/features/batch_processing/managers/` 下的管理器类
  - 删除 `app/features/batch_processing/pools/` 下的池管理类
  - 保留并迁移 `batch_job_models.py` 到业务层
  - 保留并重构 `batch_processing_worker.py` 到基础设施层
  - 验证批处理功能完整性
  - _需求: 1.1, 1.3_

- [ ] 15.2 重新实现完整的作业系统功能
  - 在业务层实现与旧架构功能一致的作业管理系统
  - 创建 `JobManager` 支持作业的创建、删除、重命名、状态跟踪
  - 实现作业与图像的关联管理（添加图像到作业、从作业移除图像）
  - 实现作业配置管理（输出设置、预设应用、导出参数）
  - 在控制器层实现作业操作的命令处理
  - 在UI层重新实现作业列表、作业详情等界面组件
  - 确保新架构中的作业系统功能与旧架构完全一致
  - _需求: 1.1, 2.2, 3.1_

- [ ] 15.3 实现数据分析图表功能
  - 在业务层创建 `ImageAnalysisService` 图像分析服务
  - 实现直方图、色彩分布、统计信息等分析算法
  - 在表示层创建 `AnalysisPanel` 显示分析图表
  - 实现图表的实时更新和交互功能
  - 集成分析结果到批处理流程中
  - _需求: 1.2, 3.1_

- [ ] 15.4 批处理功能完整性测试
  - 测试作业管理功能（创建、删除、重命名、状态跟踪）
  - 测试图像池管理功能（添加、导入、清理）
  - 测试批处理执行功能（多线程、进度跟踪、错误处理）
  - 测试预设应用功能（保存、批量应用）
  - 测试导出配置功能（目录、命名、格式）
  - 测试作业恢复功能（断点续传、状态恢复）
  - 测试数据分析图表功能（实时更新、交互）
  - 验证UI与控制器的事件驱动交互
  - _需求: 2.3, 3.3_

### 阶段6：重构应用启动层

- [ ] 16. 创建新的应用引导器
  - 实现 `ApplicationBootstrap` 类，按层级顺序初始化服务
  - 创建服务注册表，管理各层服务的生命周期
  - 实现依赖注入容器的架构合规性验证
  - 移除 `DirectServiceInitializer` 中的架构违反代码
  - _需求: 2.1, 2.2, 8.1_

- [ ] 17. 重构应用启动流程
  - 修改 `ApplicationStartup` 以使用新的引导器
  - 实现分层服务初始化顺序控制
  - 建立服务初始化失败的回滚机制
  - 添加启动过程的架构合规性检查
  - _需求: 2.1, 2.2, 8.2_

### 阶段7：消除遗留依赖

- [ ] 18. 移除核心层中的上层导入
  - 删除 `app/core/initialization/direct_service_initializer.py` 中的上层导入
  - 重构或移除 `UpperLayerServiceAdapter` 和相关桥接代码
  - 验证核心层不再有任何上层依赖
  - 运行架构合规性检查确认修复完成
  - **清理步骤**：
    - 完全删除 `app/core/initialization/direct_service_initializer.py` 文件
    - 删除 `app/core/interfaces/upper_layer_service_interface.py` 文件
    - 删除 `app/core/adapters/upper_layer_service_adapter.py` 文件
    - 移除 `app/core/dependency_injection/service_builder.py` 中的 `build_app_controller()` 方法
    - 清理 `app/core/dependency_injection/infrastructure_bridge.py` 中的上层服务注册代码
    - 更新 `app/application_startup.py`，移除对 `DirectServiceInitializer` 的引用
  - _需求: 1.1, 1.3, 5.1_

- [ ] 19. 清理遗留的桥接适配器代码
  - 移除不再需要的桥接适配器类
  - 清理相关的接口定义
  - 更新依赖注入容器，移除桥接相关代码
  - 验证系统功能完整性
  - _需求: 6.1, 6.2, 6.3_

- [ ] 19.1 验证批处理架构合规性
  - 运行架构检查工具验证批处理模块无向上依赖
  - 确认批处理UI层不直接导入业务层或基础设施层
  - 验证批处理控制器正确使用事件机制与业务层通信
  - 测试批处理功能的端到端工作流程
  - _需求: 1.3, 7.1, 7.2_

### 阶段8：建立架构治理

- [ ] 20. 实现持续架构合规性检查
  - 创建预提交钩子，运行架构检查
  - 实现CI/CD流水线中的架构验证步骤
  - 创建架构违反的自动报告机制
  - 编写架构检查工具的文档
  - _需求: 7.1, 7.2, 7.3_

- [ ] 21. 创建架构文档和培训材料
  - 更新架构文档以反映新的分层结构
  - 创建开发者指南，说明如何遵循架构原则
  - 编写常见架构违反的修复指南
  - 创建架构决策记录(ADR)模板
  - _需求: 4.2, 7.3_

### 阶段9：测试和验证

- [ ] 22. 实现分层架构的集成测试
  - 创建层间交互的集成测试套件
  - 实现端到端业务流程测试
  - 验证事件驱动机制的正确性
  - 测试错误处理和恢复机制
  - _需求: 1.3, 2.3, 5.2_

- [ ] 23. 性能测试和优化
  - 测试事件处理机制的性能影响
  - 优化命令处理的响应时间
  - 验证内存使用情况和潜在泄漏
  - 实现性能基准测试
  - _需求: 2.3_

- [ ] 24. 最终验证和文档更新
  - 运行完整的架构合规性检查
  - 验证所有功能的正确性
  - 更新用户文档和API文档
  - 创建迁移完成报告
  - _需求: 1.3, 4.2, 7.3_