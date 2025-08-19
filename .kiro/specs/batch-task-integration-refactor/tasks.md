# 批处理任务系统完全整合重构实施计划

## 实施任务

- [ ] 1. 创建统一任务处理架构的目录结构
  - 在app/core/tasks/下创建coordinator/、handlers/、models/、interfaces/、services/、workers/子目录
  - 创建各子目录的__init__.py文件
  - 建立清晰的模块导入结构
  - _需求: 2.1, 2.2_

- [ ] 2. 重构和迁移任务协调器
  - 将app/core/tasks/coordinator.py重命名为app/core/tasks/coordinator/task_coordinator.py
  - 创建app/core/tasks/coordinator/task_scheduler.py实现任务调度逻辑
  - 整合原ExecutionManager的功能到TaskCoordinator中
  - _需求: 1.1, 3.1_

- [ ] 3. 拆分和重构接口定义
  - 将app/core/tasks/interfaces.py拆分到interfaces/目录下的多个文件
  - 创建task_handler_interface.py、task_coordinator_interface.py、task_event_listener.py
  - 将TaskInfo等模型类迁移到models/目录
  - _需求: 2.2, 2.3_

- [ ] 4. 创建任务数据模型层
  - 创建app/core/tasks/models/task_info.py，从interfaces.py迁移TaskInfo类
  - 创建app/core/tasks/models/batch_job.py，迁移批处理作业模型
  - 创建app/core/tasks/models/task_result.py，定义统一的任务结果模型
  - _需求: 2.2, 2.3_

- [ ] 5. 重构任务处理器层
  - 将app/core/tasks/handlers.py重命名为app/core/tasks/handlers/base_handler.py
  - 创建app/core/tasks/handlers/batch_processing_handler.py实现批处理任务处理器
  - 创建app/core/tasks/handlers/simple_task_handler.py迁移简单任务处理器
  - _需求: 1.1, 2.2_

- [ ] 6. 创建任务服务层
  - 创建app/core/tasks/services/batch_job_service.py整合原批处理管理器功能
  - 创建app/core/tasks/services/image_pool_service.py整合图像池管理功能
  - 创建app/core/tasks/services/task_progress_service.py实现统一的进度管理
  - _需求: 1.1, 3.1_

- [ ] 7. 迁移和简化工作器层
  - 将app/features/batch_processing/batch_processing_worker.py迁移到app/core/tasks/workers/
  - 移除QObject继承和信号机制，简化为纯处理逻辑
  - 创建app/core/tasks/workers/image_analysis_worker.py用于图像分析任务
  - _需求: 3.1, 3.3_

- [ ] 8. 更新批处理协调器为服务门面
  - 重构app/features/batch_processing/batch_coordinator.py为轻量级门面
  - 移除所有管理器依赖，改为调用统一任务服务
  - 保持原有的公共接口和信号不变
  - _需求: 1.1, 4.1_

- [ ] 9. 完全重构依赖注入配置
  - 修改app/core/dependency_injection/service_builder.py
  - 注册所有新的任务服务和处理器
  - 移除所有旧的批处理管理器注册
  - _需求: 1.1, 3.1_

- [ ] 10. 删除所有旧的批处理文件和目录
  - 删除app/features/batch_processing/managers/目录及所有文件
  - 删除app/features/batch_processing/pools/目录及所有文件
  - 删除app/features/batch_processing/interfaces/目录及所有文件
  - 清理所有相关的导入语句
  - _需求: 3.2, 3.3_

- [ ] 11. 更新UI层的依赖注入
  - 修改MainWindow和相关UI组件的构造函数
  - 将BatchProcessingHandler的依赖改为注入统一的任务服务
  - 确保UI层无需感知底层架构变化
  - _需求: 4.1, 4.2_

- [ ] 12. 创建统一任务处理的测试用例
  - 为新的任务服务层创建单元测试
  - 为任务处理器创建集成测试
  - 为完整的批处理流程创建端到端测试
  - _需求: 4.1, 4.2_

- [ ] 13. 验证重构完整性和性能
  - 运行所有批处理功能测试确保功能完整
  - 进行性能基准测试确保性能不下降
  - 验证内存使用和资源管理的改进
  - 确认没有遗留的未使用代码和文件
  - _需求: 4.1, 4.2_