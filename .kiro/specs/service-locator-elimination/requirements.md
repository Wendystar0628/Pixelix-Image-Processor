# 服务定位器消除需求文档

## 介绍

当前应用仍然使用ServiceLocator作为中心节点进行服务获取，并且存在部分服务的运行时依赖查找问题。需要彻底消除ServiceLocator模式，转向纯依赖注入模式，减少服务定位器的使用，避免中心化通信和运行时依赖查找。

## 需求

### 需求 1

**用户故事:** 作为开发者，我希望消除ServiceLocator的中心节点作用，这样应用就不再通过单一节点进行所有服务间通信

#### 验收标准

1. WHEN 应用启动时 THEN 系统 SHALL 直接通过构造函数注入创建所有服务而不使用ServiceLocator
2. WHEN 服务需要其他服务时 THEN 系统 SHALL 通过构造函数参数获取依赖而不是运行时查找
3. WHEN 主窗口创建时 THEN 系统 SHALL 直接接收所有必需的服务实例

### 需求 2

**用户故事:** 作为开发者，我希望实现分层依赖管理，这样各层服务职责清晰且不会相互耦合

#### 验收标准

1. WHEN 初始化核心服务时 THEN 系统 SHALL 按照core->business->handler的顺序创建服务
2. WHEN 服务依赖其他服务时 THEN 系统 SHALL 确保依赖的服务已在更低层级创建
3. WHEN 高层级服务需要配置时 THEN 系统 SHALL 通过注入的配置注册表获取而不是直接访问配置管理器

### 需求 3

**用户故事:** 作为开发者，我希望清理运行时依赖查找，这样所有依赖关系在编译时就确定

#### 验收标准

1. WHEN 服务初始化时 THEN 系统 SHALL 通过构造函数接收所有必需的依赖
2. WHEN 代码中存在import语句时 THEN 系统 SHALL 确保不会导致循环依赖
3. WHEN 服务需要其他服务时 THEN 系统 SHALL 避免在方法内部进行服务查找

### 需求 4

**用户故事:** 作为开发者，我希望有清晰的代码文件结构，这样AI生成代码时不会违反架构设计

#### 验收标准

1. WHEN 创建新的服务初始化器时 THEN 系统 SHALL 将其放置在app/core/initialization/目录下
2. WHEN 创建配置注册表时 THEN 系统 SHALL 将其放置在app/core/configuration/目录下
3. WHEN 修改现有文件时 THEN 系统 SHALL 完全清除旧的ServiceLocator相关代码和方法