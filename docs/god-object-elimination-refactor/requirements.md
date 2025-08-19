# "上帝对象"反模式彻底消除需求文档

## 概述

当前 `ApplicationBootstrap` 仍承担过多职责，需要进一步拆解为职责单一的独立组件，彻底消除"上帝对象"反模式。

## 当前问题

### 问题1: ApplicationBootstrap 职责过多
```python
class ApplicationBootstrap:
    def bootstrap_application(self): ...    # 启动协调
    def initialize_all_services(self): ...  # 服务初始化
    def cleanup_services(self): ...         # 服务清理
    def create_ui_services(self): ...       # UI服务创建
    def shutdown(self): ...                 # 生命周期管理
    # 还直接管理 services 字典
```

### 问题2: 服务管理逻辑分散
- 服务字典直接存储在 ApplicationBootstrap 中
- 服务清理逻辑硬编码在 cleanup_services 方法中
- 缺乏专门的服务容器抽象

## 重构目标

### 目标1: 职责彻底分离 🎯
- **ApplicationBootstrap** 仅负责启动流程协调（≤50行）
- **ServiceManager** 专门管理服务存储（替代services字典）
- **ServiceCleanupManager** 专门处理服务清理（迁移现有清理逻辑）
- **AppLifecycleCoordinator** 专门管理应用生命周期（整合DirectServiceInitializer）

### 目标2: 简化设计 🎯
- 每个类职责明确单一
- 避免过度抽象和复杂设计
- 保持代码简洁易懂

### 目标3: 彻底清理旧代码 🎯
- 移除 ApplicationBootstrap 中的服务管理逻辑
- 清理冗余的生命周期管理代码
- 删除不必要的方法和属性

## 功能需求

### 需求1: 服务存储管理重构
WHEN 使用服务时 THEN 系统 SHALL 通过专门的ServiceManager而非ApplicationBootstrap直接管理

### 需求2: 服务清理重构  
WHEN 应用关闭时 THEN 系统 SHALL 使用专门的ServiceCleanupManager处理清理逻辑

### 需求3: ApplicationBootstrap 简化
WHEN ApplicationBootstrap启动时 THEN 它 SHALL 仅负责委托协调，代码≤50行

## 非功能需求

### 性能要求
- 重构不影响应用启动性能
- 服务创建和清理时间保持在当前水平

### 可维护性要求
- 每个新组件代码行数不超过80行
- 方法数量不超过5个
- 避免深层继承结构

### 兼容性要求
- main.py 的调用接口保持不变
- 现有服务的创建和使用方式不变