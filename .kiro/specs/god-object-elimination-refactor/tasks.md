# ApplicationBootstrap "上帝对象" 消除实施任务

## 实施概述

按照依赖顺序逐步实施重构，确保每个阶段都保持系统可运行状态。采用增量式重构策略，先创建新组件，再逐步迁移功能，最后清理旧代码。

## 实施任务

- [x] 1. 创建服务管理器组件


  - 创建 ServiceManager 类，提供服务注册、获取、清理的基础功能
  - 实现线程安全的服务字典管理
  - 添加详细的日志记录和错误处理
  - _需求: 1.1, 1.2, 1.3_

- [x] 2. 创建服务清理管理器组件


  - 创建 ServiceCleanupManager 类，**完整迁移** ApplicationBootstrap.cleanup_services() 中的清理逻辑
  - 实现 cleanup_analysis_services() 方法：迁移分析线程停止和等待逻辑
  - 实现 cleanup_batch_services() 方法：迁移批处理作业强制清理逻辑
  - 实现 cleanup_all_services() 方法：协调所有清理操作
  - 添加容错机制，确保单个服务清理失败不影响其他服务
  - 代码行数控制在≤70行
  - _需求: 2.1, 2.2, 2.3, 2.4_


- [x] 3. 创建应用生命周期协调器组件

  - 创建 AppLifecycleCoordinator 类，整合 DirectServiceInitializer 和服务管理
  - **迁移** ApplicationBootstrap.bootstrap_application() 中的启动协调逻辑
  - 实现 startup_application 方法，协调服务创建和注册流程
  - 实现 shutdown_application 方法，协调服务清理和容器清空
  - 添加启动失败时的清理机制和详细的错误处理
  - 代码行数控制在≤80行
  - _需求: 3.1, 3.2, 3.3_

- [x] 4. 重构 ApplicationBootstrap 为纯协调器


  - 修改 ApplicationBootstrap 构造函数，创建和组装专门组件
  - **彻底删除** self.services 属性和 self.direct_initializer 属性
  - **彻底删除** cleanup_services() 方法的具体实现（约70行），改为委托调用
  - **彻底删除** initialize_all_services() 方法的具体实现，改为委托调用
  - 重构 bootstrap_application 方法为委托调用
  - 重构 shutdown 方法为委托调用
  - 保持 create_ui_services 方法的向后兼容性
  - 确保最终代码行数≤50行
  - _需求: 4.1, 4.2, 4.3, 4.4_

- [x] 5. 验证向后兼容性和功能完整性


  - 验证 main.py 调用方式保持不变，应用能正常启动
  - 验证所有服务正确创建和注册，功能正常工作
  - 验证应用关闭时所有服务正确清理，无资源泄漏
  - 验证错误处理机制，启动失败时能正确清理和报告错误
  - _需求: 5.1, 5.2, 5.3_

- [ ] 6. 代码质量验证和优化


  - 验证 ApplicationBootstrap 代码行数不超过 50 行
  - 验证每个新组件代码行数不超过 80 行，方法数量不超过 5 个
  - 优化日志记录和错误信息，确保便于调试和维护
  - 添加必要的类型注解和文档字符串
  - _需求: 代码质量要求_
## 重要提
醒

### 虚拟环境激活
在执行任何测试前，必须先激活虚拟环境：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\Rebirth\Scripts\Activate.ps1
```

### 应用启动测试
每个任务完成后，使用以下命令测试应用启动：
```bash
python -m app.main
```

### 代码清理要求
- **必须彻底删除**旧的方法实现，不能保留任何冗余代码
- **必须完整迁移**功能逻辑，确保不遗漏任何清理步骤
- **必须保持**向后兼容性，main.py 调用方式不变
- **必须控制**代码行数在规定范围内

### 注释编写规范
- 类注释：一行简要说明职责
- 方法注释：一行说明功能，AI能理解即可
- 避免冗长解释，保持简洁明了