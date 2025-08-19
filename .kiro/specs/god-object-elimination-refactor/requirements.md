# ApplicationBootstrap "上帝对象" 消除需求文档

## 介绍

当前的 `ApplicationBootstrap` 虽然已经从 ServiceLocator 模式重构为直接依赖注入，但仍然承担了过多职责，包括服务管理、生命周期协调、清理逻辑等。需要进一步拆分为职责单一的组件，彻底消除"上帝对象"反模式。

## 需求

### 需求 1: 服务存储管理职责分离

**用户故事:** 作为开发者，我希望有专门的服务管理器来处理服务的存储和获取，这样 ApplicationBootstrap 就不需要直接管理 services 字典

#### 验收标准

1. WHEN 应用需要注册服务时 THEN 系统 SHALL 使用专门的 ServiceManager 而不是 ApplicationBootstrap 的 services 属性
2. WHEN 应用需要获取服务时 THEN 系统 SHALL 通过 ServiceManager.get_service() 方法获取
3. WHEN 需要获取所有服务时 THEN 系统 SHALL 通过 ServiceManager.get_all_services() 方法保持向后兼容

### 需求 2: 服务清理逻辑职责分离

**用户故事:** 作为开发者，我希望有专门的清理管理器来处理各种服务的清理逻辑，这样清理代码更加模块化和可维护

#### 验收标准

1. WHEN 应用关闭时 THEN 系统 SHALL 使用 ServiceCleanupManager 处理所有服务清理
2. WHEN 清理分析线程时 THEN 系统 SHALL 调用 ServiceCleanupManager.cleanup_analysis_services()
3. WHEN 清理批处理服务时 THEN 系统 SHALL 调用 ServiceCleanupManager.cleanup_batch_services()
4. WHEN 单个服务清理失败时 THEN 系统 SHALL 继续清理其他服务而不中断整个清理流程

### 需求 3: 应用生命周期协调职责分离

**用户故事:** 作为开发者，我希望有专门的生命周期协调器来管理应用的启动和关闭流程，这样生命周期管理逻辑更加清晰

#### 验收标准

1. WHEN 应用启动时 THEN 系统 SHALL 使用 AppLifecycleCoordinator 协调启动流程
2. WHEN 应用关闭时 THEN 系统 SHALL 使用 AppLifecycleCoordinator 协调关闭流程
3. WHEN 启动过程中出现错误时 THEN 系统 SHALL 通过 AppLifecycleCoordinator 处理错误和清理

### 需求 4: ApplicationBootstrap 简化为纯协调器

**用户故事:** 作为开发者，我希望 ApplicationBootstrap 只负责委托协调，这样它的职责单一且代码简洁

#### 验收标准

1. WHEN ApplicationBootstrap 初始化时 THEN 它 SHALL 只创建和组装专门组件
2. WHEN 调用 bootstrap_application() 时 THEN 它 SHALL 委托给 AppLifecycleCoordinator
3. WHEN 调用 shutdown() 时 THEN 它 SHALL 委托给 AppLifecycleCoordinator
4. WHEN ApplicationBootstrap 完成重构后 THEN 它的代码行数 SHALL 不超过 50 行

### 需求 5: 向后兼容性保持

**用户故事:** 作为开发者，我希望重构后的接口保持向后兼容，这样 main.py 和其他调用代码不需要修改

#### 验收标准

1. WHEN main.py 调用 bootstrap.initialize_all_services() 时 THEN 系统 SHALL 返回相同格式的服务字典
2. WHEN 调用 bootstrap.bootstrap_application() 时 THEN 系统 SHALL 保持相同的返回值和行为
3. WHEN 调用 bootstrap.create_ui_services() 时 THEN 系统 SHALL 保持相同的功能

## 非功能需求

### 代码质量要求

1. 每个新创建的组件代码行数不超过 80 行
2. 每个组件的方法数量不超过 5 个
3. ApplicationBootstrap 重构后代码行数不超过 50 行

### 性能要求

1. 重构不应影响应用启动性能
2. 服务获取的性能应保持在 O(1) 复杂度
3. 服务清理的总时间不应增加

### 可维护性要求

1. 每个组件职责单一明确
2. 组件间依赖关系清晰，无循环依赖
3. 代码注释简洁准确，便于 AI 理解