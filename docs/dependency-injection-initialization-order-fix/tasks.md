# 依赖注入初始化顺序修复实现计划

## 实现任务

### 阶段1：核心服务创建层修复

- [ ] 1. 修复Direct Service Initializer

  - 修改`app/core/initialization/direct_service_initializer.py`
  - 在`_create_layer_3_services()`方法中添加AppController创建逻辑
  - 确保AppController接收StateManager、ProcessingHandler等依赖
  - 调用AppController的`_register_core_services()`方法
  - 将AppController添加到services字典并返回
  - _需求: 1.1, 2.1_

- [ ] 2. 验证服务创建完整性

  - 确认所有必要的Handler层服务都已创建
  - 验证FileHandler、ProcessingHandler、PresetHandler等可用
  - 确保AppController创建时所需依赖都已准备好
  - _需求: 2.2, 5.1_

### 阶段2：AppController配置完善

- [ ] 3. 完善AppController的核心服务注册

  - 修改`app/handlers/app_controller.py`
  - 完善`_register_core_services()`方法实现
  - 移除TODO注释，实现ConfigDataAccessor注册逻辑
  - 确保StateManager、ToolManager、ConfigDataAccessor都正确注册
  - 添加注册完整性验证方法
  - _需求: 3.1, 3.2, 3.3_

- [ ] 4. 增强AppController构造函数

  - 修改构造函数，确保接收完整的核心服务依赖
  - 调整服务注册时机，确保在构造函数中完成
  - 添加桥接适配器配置验证逻辑
  - _需求: 2.2, 3.1_

### 阶段3：应用启动流程重构

- [ ] 5. 修复Application Startup的服务获取逻辑

  - 修改`app/application_startup.py`
  - 在`_create_main_window()`方法前确保AppController可用
  - 从services字典正确获取AppController实例
  - 添加AppController非None的验证检查
  - _需求: 1.1, 1.3_

- [ ] 6. 完善MainWindow创建流程

  - 修改`_create_main_window()`方法中的MainWindow构造调用
  - 确保正确传递AppController参数
  - 添加AppController桥接适配器配置的验证
  - 提供清晰的错误信息当验证失败时
  - _需求: 1.3, 2.3, 5.1_

- [ ] 7. 添加启动流程验证机制

  - 在关键节点添加依赖验证检查
  - 验证AppController的桥接适配器已正确配置
  - 验证核心服务已正确注册到桥接适配器
  - 提供详细的验证失败信息
  - _需求: 5.1, 5.2_

### 阶段4：清理机制修复

- [ ] 8. 修复ApplicationBootstrap清理机制

  - 修改`app/core/container/application_bootstrap.py`
  - 修复`cleanup_services()`方法的参数传递
  - 确保调用`cleanup_all_services(services)`时传递services参数
  - 完善shutdown方法的调用逻辑
  - _需求: 4.1, 4.2_

- [ ] 9. 完善应用退出流程

  - 修改`app/application_startup.py`中的`_cleanup_services()`方法
  - 添加异常处理确保清理过程不影响应用退出
  - 提供清理状态的明确反馈信息
  - 确保线程正确终止
  - _需求: 4.2, 4.3_

### 阶段5：系统验证和测试

- [ ] 10. 验证依赖注入完整性

  - 创建测试脚本验证启动流程各阶段
  - 验证AppController在MainWindow创建前已准备好
  - 验证UI组件能正确通过桥接适配器访问核心服务
  - 验证应用能正常启动到主界面
  - _需求: 2.1, 2.2, 2.3_

- [ ] 11. 验证清理机制正确性

  - 测试应用正常退出流程
  - 验证无线程未清理警告
  - 验证无资源泄漏报告
  - 确认清理过程中的异常处理正确
  - _需求: 4.1, 4.2, 4.3_

- [ ] 12. 完整功能验证

  - 测试所有主要UI功能正常工作
  - 验证桥接适配器模式完全生效
  - 确认分层架构依赖方向正确
  - 验证错误处理和验证机制有效
  - _需求: 5.3, 2.3_

## 验证清单

### 启动流程验证
- [ ] 应用能正常启动到主界面
- [ ] AppController在MainWindow创建前已创建
- [ ] 所有核心服务已注册到桥接适配器
- [ ] UI组件能正确访问核心服务

### 架构合规性验证
- [ ] 依赖方向严格遵循分层架构
- [ ] 无循环依赖或空引用问题
- [ ] 桥接适配器模式完全生效
- [ ] 服务访问链完整无断裂

### 退出机制验证
- [ ] 应用能正常关闭
- [ ] 无线程未清理警告
- [ ] 无资源泄漏报告
- [ ] 清理异常不影响退出

## 关键风险点

1. **服务创建顺序**：确保AppController创建时所需依赖已准备好
2. **参数传递链**：确保AppController正确传递到MainWindow
3. **桥接适配器配置**：确保所有核心服务正确注册
4. **清理参数传递**：确保清理机制接收正确参数

## 回滚策略

如果修复过程中出现问题：
1. 立即回滚到上一个可工作的状态
2. 分析失败的具体原因和影响范围
3. 调整修复策略，采用更保守的方法
4. 逐个组件验证，避免批量修改风险