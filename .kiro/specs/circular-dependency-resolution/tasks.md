# 循环依赖解决方案实施计划

## 任务列表

- [x] 1. 分析和诊断当前循环依赖问题



  - 添加详细的依赖解析日志，识别具体的循环依赖路径
  - 创建依赖关系图，可视化当前的服务依赖结构
  - 确认ConfigurationProviderInterface和ConfigManagerInterface之间的循环依赖


  - _需求: 1.1, 2.2_

- [ ] 2. 创建ConfigurationRegistry替代配置提供者接口
  - 设计ConfigurationRegistry类，直接管理配置访问
  - 实现配置缓存机制，提高性能


  - 将原有ConfigurationProviderInterface的功能迁移到ConfigurationRegistry
  - 创建单元测试验证ConfigurationRegistry的功能
  - _需求: 2.1, 4.2_

- [-] 3. 简化依赖注入容器实现

  - 创建SimpleDependencyContainer类，移除自动依赖解析功能
  - 实现显式的服务注册和获取方法
  - 添加基本的错误处理和诊断信息
  - 保留必要的单例模式支持
  - _需求: 1.1, 2.1, 5.1_

- [x] 4. 实现分层服务初始化器

  - 创建LayeredServiceInitializer类，按依赖层次初始化服务
  - 实现第1层核心服务初始化（ConfigurationRegistry、ImageProcessor）
  - 实现第2层业务服务初始化（StateManager等依赖核心服务的服务）
  - 实现第3层处理器服务初始化（各种Handler服务）
  - _需求: 3.1, 3.2, 4.3_



- [ ] 5. 重构ApplicationBootstrap使用新的初始化策略
  - 修改ApplicationBootstrap使用LayeredServiceInitializer
  - 移除对原有DependencyContainer的依赖
  - 实现分阶段的服务创建和依赖设置
  - 确保所有服务按正确顺序创建


  - _需求: 3.3, 4.3_

- [ ] 6. 更新主窗口和UI服务创建逻辑
  - 修改main.py中的服务获取逻辑，使用新的容器

  - 更新MainWindow构造函数，接收ConfigurationRegistry而不是ConfigurationProvider
  - 修改UI服务创建逻辑，适配新的依赖注入方式
  - _需求: 1.3, 3.2_

- [ ] 7. 彻底清理旧的接口和实现

  - 完全删除app/core/interfaces/configuration_provider_interface.py文件
  - 完全删除app/core/providers/app_configuration_provider.py文件
  - 完全删除app/core/dependency_injection/dependency_container.py文件
  - 清理app/core/interfaces/__init__.py中的相关导入
  - 验证没有任何地方仍在引用这些已删除的类
  - _需求: 6.1, 6.2, 6.3_

- [ ] 8. 按代码结构指导创建新文件
  - 创建app/core/dependency_injection/simple_container.py（SimpleDependencyContainer）
  - 创建app/core/configuration/configuration_registry.py（ConfigurationRegistry）
  - 创建app/core/initialization/layered_initializer.py（LayeredServiceInitializer）
  - 确保每个文件职责单一，符合架构设计
  - _需求: 7.1, 7.2_

- [ ] 9. 更新所有使用配置提供者的代码
  - 查找所有使用ConfigurationProviderInterface的地方
  - 将这些地方改为使用ConfigurationRegistry
  - 更新相关的构造函数和依赖注入代码
  - 确保没有遗留的旧接口引用
  - _需求: 4.2, 4.3, 6.3_

- [ ] 10. 添加错误处理和诊断功能
  - 在SimpleDependencyContainer中添加详细的错误信息
  - 实现服务创建失败时的回退机制
  - 添加启动过程的详细日志记录
  - 创建诊断工具，帮助识别潜在的依赖问题
  - _需求: 2.2, 5.1, 5.2, 5.3_

- [ ] 11. 创建全面的测试套件
  - 为ConfigurationRegistry创建单元测试
  - 为SimpleDependencyContainer创建单元测试
  - 为LayeredServiceInitializer创建集成测试
  - 创建应用启动的端到端测试，验证无循环依赖
  - _需求: 1.1, 1.2, 1.3_

- [ ] 12. 验证和优化应用启动流程
  - 测试应用能够正常启动，无循环依赖错误
  - 验证所有核心功能正常工作
  - 优化启动性能，确保服务创建效率
  - 添加启动时间监控和性能指标
  - _需求: 1.1, 1.3_

- [ ] 13. 最终代码清理和验证
  - 执行完整的代码清理检查清单（参考code-structure-guide.md）
  - 验证所有旧代码和导入已完全清理
  - 确保没有未使用的文件和类
  - 运行全面测试，确保重构后功能完整
  - 更新相关文档，反映新的架构设计
  - _需求: 6.1, 6.2, 6.3, 7.3_