# 服务定位器消除实施计划

## 任务列表

- [x] 1. 创建DirectServiceInitializer替代ServiceLocator


  - 创建app/core/initialization/direct_service_initializer.py文件
  - 实现按层次直接创建服务的逻辑（core->business->handler）
  - 添加initialize_all_services方法返回服务字典
  - 实现基本的错误处理和日志记录
  - _需求: 1.1, 2.1_



- [ ] 2. 重构StateManager消除运行时依赖查找
  - 修改StateManager构造函数接收ImageProcessor参数
  - 在构造函数中直接创建ProxyWorkflowManager，移除运行时导入
  - 删除set_image_processor方法及相关逻辑


  - 确保所有依赖在构造时确定
  - _需求: 1.2, 3.1, 3.3_

- [ ] 3. 重构ApplicationBootstrap使用DirectServiceInitializer
  - 修改ApplicationBootstrap类，移除ServiceLocator和LayeredServiceInitializer依赖


  - 添加initialize_all_services方法，使用DirectServiceInitializer创建所有服务
  - 简化bootstrap_application方法，直接返回服务创建结果
  - 保留必要的应用状态管理功能
  - _需求: 1.1, 2.2_


- [ ] 4. 重构main.py消除ServiceLocator使用
  - 移除所有service_locator相关的代码和导入
  - 修改服务获取逻辑，直接从bootstrap.initialize_all_services()获取服务字典
  - 直接传递服务实例给MainWindow构造函数和属性设置
  - 简化_setup_signal_connections函数，直接使用services字典
  - _需求: 1.1, 1.3_


- [ ] 5. 创建代码文件结构指导文档
  - 创建code-structure-guide.md文档
  - 列出修改前后的代码文件结构对比
  - 说明每个新增和修改文件的职责
  - 提供清理旧代码的详细步骤清单
  - _需求: 4.1, 4.2, 4.3_

- [x] 6. 彻底清理ServiceLocator相关代码

  - 完全删除app/core/container/service_locator.py文件
  - 完全删除app/core/interfaces/service_locator_interface.py文件
  - 完全删除app/core/initialization/layered_initializer.py文件
  - 清理所有相关的import语句和类型注解
  - 验证没有任何地方仍在引用这些已删除的类
  - _需求: 4.3_

- [x] 7. 更新ApplicationBootstrap清理ServiceLocator依赖


  - 移除ServiceLocator、LayeredServiceInitializer相关的导入和属性
  - 删除get_service_locator方法和相关的兼容性代码
  - 简化类结构，只保留DirectServiceInitializer相关功能
  - 清理UIServiceFactory和CompatibilityAdapter等不再需要的组件
  - _需求: 2.2, 4.3_

- [x] 8. 验证应用启动和核心功能


  - 测试应用能够正常启动，无ServiceLocator相关错误
  - 验证所有核心服务正确创建和初始化
  - 测试图像加载、处理、保存等基本功能
  - 验证批处理功能正常工作
  - _需求: 1.3, 2.1_



- [x] 9. 添加简单的错误处理和诊断

  - 在DirectServiceInitializer中添加服务创建失败的错误处理
  - 添加基本的依赖验证，确保必需服务都已创建
  - 在main.py中添加服务初始化失败的错误提示
  - 保持错误处理逻辑简单，避免过度设计
  - _需求: 3.2_





- [ ] 10. 最终代码清理和验证
  - 执行完整的代码清理检查，确保没有遗留的ServiceLocator引用
  - 清理所有未使用的导入语句
  - 验证代码结构符合架构设计，文件职责清晰
  - 运行应用进行最终功能验证
  - _需求: 4.3_