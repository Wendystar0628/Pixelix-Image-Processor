# ProcessingHandler 重构设计文档

## 概述

本设计文档描述了如何重构 ProcessingHandler 以实现职责分离，简化图像加载流程，并移除不必要的代理预览和异步渲染机制。重构将遵循现有的分层架构和关注点分离原则。

## 架构设计

### 职责重新分配

#### 1. ProcessingHandler (重构后)
- **职责**: 专注于图像操作相关的UI事件处理
- **保留功能**:
  - 图像操作命令的创建和执行
  - 预览相关的交互处理 (slider pressed/released)
  - 实时预览参数设置
  - 各种图像操作的槽函数
- **移除功能**:
  - 图像加载业务流程编排
  - 状态捕获和恢复逻辑
  - 错误回滚机制

#### 2. ImageLoadingService (新增核心服务)
- **位置**: `app/core/services/image_loading_service.py`
- **职责**: 专门负责图像加载的业务流程编排
- **功能**:
  - 简化的图像加载流程 (直接加载全分辨率图像)
  - 图像清除流程
  - 与 StateManager 的协调

#### 3. 利用现有的 ErrorRecoveryService
- **职责**: 处理图像加载过程中的错误恢复
- **功能**: 状态捕获、恢复和回滚机制

### 组件交互设计

```
UI Layer (MainWindow/AppController)
    ↓ (图像加载请求)
ImageLoadingService
    ↓ (调用核心管理器)
StateManager → ImageRepository
    ↓ (状态变化通知)
UI Layer (更新显示)

UI Layer (图像操作请求)
    ↓ (操作信号)
ProcessingHandler
    ↓ (创建命令)
PipelineManager
    ↓ (执行操作)
StateManager
```

## 数据模型

### 简化的图像加载流程
```python
# 原流程 (复杂)
reset_state() → set_image_data() → create_proxy() → set_proxy() → notify()

# 新流程 (简化)
reset_state() → set_image_data() → notify()
```

### 错误处理模型
```python
# 使用现有的 ErrorRecoveryService
try:
    # 图像加载操作
    pass
except Exception as e:
    # 通过 ErrorRecoveryService 进行状态恢复
    error_recovery_service.recover_from_error(e, context)
```

## 接口设计

### ImageLoadingService 接口
```python
class ImageLoadingService:
    def load_image(self, image: np.ndarray, file_path: str = None) -> None
    def clear_image(self) -> None
    def _setup_error_recovery(self) -> None
```

### ProcessingHandler 简化接口
```python
class ProcessingHandler:
    # 保留的方法
    def _create_and_execute_command(...)
    def on_slider_pressed(...)
    def on_slider_released(...)
    def start_preview(...)
    def cancel_preview(...)
    def apply_*(...) # 各种图像操作方法
    
    # 移除的方法
    # load_image_complete() - 移至 ImageLoadingService
    # clear_image_complete() - 移至 ImageLoadingService  
    # load_image_proxy_complete() - 删除 (不再需要)
    # _capture_current_state() - 移至 ErrorRecoveryService
    # _restore_state() - 移至 ErrorRecoveryService
```

## 错误处理策略

### 图像加载错误处理
1. 在 ImageLoadingService 中集成 ErrorRecoveryService
2. 定义图像加载特定的恢复策略
3. 在加载失败时自动触发状态恢复

### 操作执行错误处理
1. ProcessingHandler 中的操作执行保持现有错误处理机制
2. 通过 PipelineManager 的内置错误处理进行管理

## 测试策略

### 单元测试
1. ImageLoadingService 的图像加载流程测试
2. ProcessingHandler 的操作执行测试
3. 错误恢复机制测试

### 集成测试
1. 完整的图像加载到显示流程测试
2. 图像操作的端到端测试
3. 预览功能的交互测试

## 实现注意事项

### 1. 保持向后兼容
- AppController 调用接口保持不变
- UI 层的信号连接保持不变

### 2. 最小化变更
- 尽量复用现有代码逻辑
- 只移动和简化，不重写核心算法

### 3. 错误处理
- 利用现有的 ErrorRecoveryService 框架
- 确保错误恢复的完整性

### 4. 性能考虑
- 移除代理图像创建步骤可能提升加载性能
- 简化的流程减少了内存使用