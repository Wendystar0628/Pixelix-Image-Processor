# UI组件构造函数兼容性修复需求文档

## 介绍

重构过程中修改了多个UI组件的构造函数签名以支持桥接适配器模式，但调用这些组件的代码未同步更新，导致运行时参数不匹配错误。本修复旨在系统性地更新所有UI组件的实例化代码，确保构造函数调用与新签名保持一致。

## 需求

### 需求1：修复AnalysisPanel构造函数调用

**用户故事：** 作为应用用户，我希望应用能正常启动，不会因为AnalysisPanel构造函数参数不匹配而崩溃。

#### 验收标准

1. WHEN 应用启动 THEN AnalysisPanel SHALL 使用正确的构造函数参数创建
2. WHEN AnalysisPanel初始化 THEN 它 SHALL 通过app_controller获取核心服务
3. WHEN 核心服务可用 THEN AnalysisPanel SHALL 正常完成初始化

### 需求2：修复DialogManager构造函数调用

**用户故事：** 作为开发者，我希望DialogManager能正确创建，不会因为参数类型不匹配而失败。

#### 验收标准

1. WHEN DialogManager创建 THEN 它 SHALL 接收app_controller作为第一个参数
2. WHEN DialogManager需要核心服务 THEN 它 SHALL 通过桥接适配器获取
3. WHEN 对话框显示 THEN DialogManager SHALL 正常工作不报错

### 需求3：修复其他重构组件的构造函数调用

**用户故事：** 作为系统，我希望所有重构过的UI组件都能正确创建，保持架构一致性。

#### 验收标准

1. WHEN 任何重构组件创建 THEN 它们 SHALL 使用统一的桥接适配器访问模式
2. WHEN 组件需要核心服务 THEN 它们 SHALL 通过app_controller获取
3. WHEN 应用运行 THEN 所有组件 SHALL 正常协作无错误

### 需求4：确保应用清理机制正常

**用户故事：** 作为应用用户，我希望应用能正常退出，不会出现线程未清理的警告。

#### 验收标准

1. WHEN 应用退出 THEN ApplicationBootstrap SHALL 正确执行cleanup_services
2. WHEN 线程运行中 THEN 系统 SHALL 等待线程完成再退出
3. WHEN 清理失败 THEN 系统 SHALL 记录错误但不崩溃

### 需求5：保持现有功能完整性

**用户故事：** 作为应用用户，我希望修复后的应用功能与之前完全一致。

#### 验收标准

1. WHEN 修复完成 THEN 所有UI功能 SHALL 与修复前保持一致
2. WHEN 用户操作 THEN 界面响应 SHALL 正常无异常
3. WHEN 核心服务调用 THEN 它们 SHALL 通过桥接适配器正确访问