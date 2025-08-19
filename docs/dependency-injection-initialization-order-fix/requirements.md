# 依赖注入初始化顺序修复需求文档

## 介绍

当前应用启动时出现AppController为None的问题，导致AnalysisPanel无法通过桥接适配器访问核心服务。问题根源是依赖注入的初始化顺序不正确，需要彻底重构启动流程，确保依赖项在被使用前已准备就绪。

## 需求

### 需求1：修复AppController创建时机

**用户故事：** 作为应用系统，我希望AppController在任何UI组件创建之前就已经完全准备好，以确保桥接适配器模式正常工作。

#### 验收标准

1. WHEN 应用启动 THEN AppController SHALL 在服务初始化阶段被创建
2. WHEN AppController创建完成 THEN 它 SHALL 已完成所有核心服务的注册
3. WHEN MainWindow创建时 THEN 它 SHALL 接收到非None的AppController实例

### 需求2：确保依赖注入顺序正确

**用户故事：** 作为架构系统，我希望严格按照分层架构的依赖方向进行初始化，避免循环依赖和空引用。

#### 验收标准

1. WHEN 应用启动 THEN 初始化顺序 SHALL 为：基础设施→核心→Handler→UI
2. WHEN 每个层级初始化 THEN 所需依赖 SHALL 已在前序步骤中准备就绪
3. WHEN UI组件创建 THEN 它们 SHALL 能安全地通过桥接适配器访问核心服务

### 需求3：完善核心服务注册机制

**用户故事：** 作为桥接适配器，我希望所有必要的核心服务都已正确注册，以提供完整的服务访问能力。

#### 验收标准

1. WHEN AppController创建 THEN StateManager SHALL 已注册到桥接适配器
2. WHEN AppController创建 THEN ConfigDataAccessor SHALL 已注册到桥接适配器  
3. WHEN AppController创建 THEN ToolManager SHALL 已注册到桥接适配器

### 需求4：修复应用清理机制

**用户故事：** 作为应用用户，我希望应用能正常退出，不会出现线程未清理或资源泄漏的警告。

#### 验收标准

1. WHEN 应用退出 THEN 清理机制 SHALL 正确传递服务参数
2. WHEN 清理执行 THEN 所有线程 SHALL 正确终止
3. WHEN 清理完成 THEN 不 SHALL 出现资源泄漏警告

### 需求5：确保启动流程健壮性

**用户故事：** 作为开发者，我希望启动流程具有足够的验证和错误处理机制，便于调试和维护。

#### 验收标准

1. WHEN 关键依赖缺失 THEN 系统 SHALL 提供明确的错误信息
2. WHEN 初始化失败 THEN 系统 SHALL 优雅地终止并清理资源
3. WHEN 启动成功 THEN 所有组件 SHALL 能正常协作工作