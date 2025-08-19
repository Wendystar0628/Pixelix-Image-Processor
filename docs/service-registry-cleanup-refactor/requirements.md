# ServiceRegistry清理重构需求文档

## 概述

本文档描述了彻底移除ServiceRegistry依赖，完成向纯依赖注入架构过渡的需求。重构目标是简化架构，移除中间层，实现清晰的依赖关系。

## 当前问题

### 1. ServiceRegistry残留使用
- `app/controllers/` - 整个控制器层使用ServiceRegistry
- `app/handlers/preset_handler.py` - 预设处理器依赖ServiceRegistry
- `app/core/container/application_bootstrap.py` - 保留向后兼容支持

### 2. 架构不一致
- 部分组件使用依赖注入
- 部分组件仍使用ServiceRegistry
- 混合模式增加了代码复杂度

### 3. 职责混乱
- Controllers层职责与架构设计不符
- AppController内部组件分散在独立文件中

## 重构目标

### 1. 完全移除ServiceRegistry 🎯
- **删除**ServiceRegistry类和相关文件
- **清理**所有ServiceRegistry导入和使用
- **统一**为纯依赖注入架构

### 2. 重构控制器架构 🎯
- **合并**app/controllers/为AppController内部组件
- **简化**控制器层级结构
- **明确**AppController的协调职责

### 3. 清理兼容性代码 🎯
- **移除**ApplicationBootstrap中的兼容支持
- **删除**过时的context相关代码
- **清理**临时方案和TODO注释

## 功能需求

### 1. AppController重构
- 将子控制器整合为内部组件类
- 使用构造函数依赖注入
- 保持现有公共接口不变

### 2. PresetHandler重构
- 从ServiceRegistry改为依赖注入
- 简化构造函数参数
- 移除不必要的类型转换

### 3. ApplicationBootstrap简化
- 移除ServiceRegistry创建和填充
- 直接使用DependencyContainer构建服务
- 清理向后兼容代码

## 非功能需求

### 1. 代码简洁性
- 减少代码行数和文件数量
- 避免过度设计
- 保持单一职责原则

### 2. 架构一致性
- 所有组件使用统一的依赖注入
- 遵循既定的分层架构
- 明确的职责边界

### 3. 维护性
- 易于AI理解的代码结构
- 避免文件名冲突
- 清晰的依赖关系

## 约束条件

### 1. 向后兼容
- 保持公共接口不变
- 不影响现有业务逻辑
- 信号机制完全保留

### 2. 最小化修改
- 优先整合而非重写
- 保持现有功能逻辑
- 避免引入新概念

### 3. 测试要求
- 仅在关键节点添加简单测试
- 专注核心功能验证
- 避免过度测试

## 验收标准

### 1. ServiceRegistry完全移除 ✓
- [ ] ServiceRegistry类和文件被删除
- [ ] 所有ServiceRegistry导入被移除
- [ ] ApplicationBootstrap不再包含兼容代码

### 2. 控制器架构简化 ✓
- [ ] app/controllers/目录被移除
- [ ] AppController整合所有子控制器
- [ ] 控制器使用纯依赖注入

### 3. 功能完整性 ✓
- [ ] 所有现有功能正常工作
- [ ] 信号连接正确
- [ ] 错误处理保持不变

## 风险控制

### 1. 架构风险
- **职责混乱** - 通过明确的内部组件划分避免
- **依赖复杂** - 使用简单的构造函数注入
- **耦合增加** - 保持清晰的接口边界

### 2. 实施风险
- **功能破坏** - 分阶段重构并保持接口不变
- **测试遗漏** - 专注关键路径测试
- **理解困难** - 提供清晰的代码组织

## 总结

本次重构将彻底移除ServiceRegistry，实现纯依赖注入架构。通过简化控制器层级和清理兼容代码，使整个架构更加清晰和一致。重构采用最小化修改的策略，确保在提升代码质量的同时保持系统稳定性。