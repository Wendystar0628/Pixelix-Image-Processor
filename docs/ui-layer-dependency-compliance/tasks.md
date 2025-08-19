# UI层依赖合规性实施任务

## 实施概述

通过建立Handler层UI服务门面，消除UI层对核心层的直接跳级导入。采用渐进式重构策略，确保现有功能完全不变的前提下，建立清晰的分层架构。

## 实施任务

- [ ] 1. 创建核心服务桥接接口

  - 创建 `app/core/interfaces/core_service_interface.py` 文件
  - 定义StateManager、ConfigDataAccessor、ToolManager的获取接口
  - 保持与现有UpperLayerServiceInterface相同的设计模式
  - 遵循抽象基类和接口设计原则
  - _需求: 1.1, 2.1_

- [ ] 2. 创建核心服务桥接适配器

  - 创建 `app/core/adapters/core_service_adapter.py` 文件
  - 实现CoreServiceInterface的具体实现
  - 提供register_service和get_xxx方法
  - 确保与UpperLayerServiceAdapter的设计一致性
  - _需求: 1.2, 2.2_

- [ ] 3. 在Handler层集成核心服务适配器

  - 修改 `app/handlers/app_controller.py` 集成CoreServiceAdapter
  - 在初始化时注册StateManager、ConfigDataAccessor等服务
  - 提供get_core_service_adapter()方法供UI层使用
  - 确保适配器生命周期管理正确
  - _需求: 1.3, 2.3_

- [ ] 4. 重构高优先级UI组件

  - 重构MainWindow中的核心层直接导入
  - 重构DialogManager中的状态管理访问
  - 重构主要面板中的配置访问
  - 验证功能保持完全不变
  - _需求: 1.1, 1.3_

- [ ] 5. 重构剩余UI组件

  - 重构各种对话框中的核心层导入
  - 重构管理器组件中的直接访问
  - 重构小部件中的模型导入
  - 保持渐进式重构节奏
  - _需求: 1.2, 1.3_

- [ ] 6. 建立数据模型访问规范

  - 编写数据模型直接导入的指导原则
  - 更新代码规范文档
  - 建立代码检查规则
  - 提供开发者指导
  - _需求: 3.1, 3.3_

- [ ] 7. 验证架构合规性

  - 运行UI层跳级导入检查脚本
  - 验证所有UI功能正常工作
  - 检查性能影响评估
  - 确认分层架构合规
  - _需求: 1.3, 2.3, 3.3_

## 重要提醒

### 渐进式重构原则
- 每次只重构一个UI组件或一类导入
- 每步完成后验证功能正常
- 避免大规模并行修改

### 功能完整性验证
每个任务完成后，必须验证：
```bash
python -m app.main
```

### 架构合规性检查
定期运行以下检查：
```python
# 检查UI层是否还有跳级导入
python -c "检查脚本"
```

## 数据模型访问规范

### 允许直接导入
- 纯数据结构：BatchJob, ExportConfig等
- 枚举类型：BatchJobStatus, ConflictResolution等  
- 参数类：CurvesParams, LevelsParams等

### 必须通过Handler访问
- StateManager实例
- ConfigDataAccessor实例
- ToolManager实例
- 任何包含业务逻辑的组件

## 验证清单

### 架构合规性验证
- [ ] UI层无核心层服务的直接导入
- [ ] 所有核心服务通过Handler层访问
- [ ] 数据模型访问符合规范

### 功能完整性验证
- [ ] 所有UI功能保持正常
- [ ] 用户体验无任何变化
- [ ] 性能无显著下降

### 代码质量验证
- [ ] Handler层接口简洁明确
- [ ] 错误处理机制完善
- [ ] 代码结构清晰易懂