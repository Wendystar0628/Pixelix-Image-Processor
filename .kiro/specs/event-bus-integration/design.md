# 事件总线集成设计文档

## 概述

设计一个轻量级的事件总线系统，集成到现有的分层架构中。事件总线将提供发布-订阅机制，减少服务间直接依赖。

## 架构设计

### 核心组件

#### 1. 事件总线实现 (EventBusImpl)
- 位置：`app/core/events/event_bus_impl.py`
- 职责：管理事件订阅、发布和取消订阅
- 特点：线程安全、简单轻量

#### 2. 事件类型注册表 (EventTypeRegistry)
- 位置：`app/core/events/event_type_registry.py`
- 职责：定义和管理所有事件类型常量
- 特点：集中管理、支持扩展

#### 3. 事件载荷模型 (EventPayloadModels)
- 位置：`app/core/events/event_payload_models.py`
- 职责：定义事件携带的数据结构
- 特点：类型安全、结构化

### 集成点设计

#### 1. 分层初始化器集成
- 在第1层核心服务中初始化事件总线
- 通过依赖容器注册事件总线实例
- 确保所有服务都能获取到同一个事件总线实例

#### 2. 服务定位器扩展
- 添加获取事件总线的便捷方法
- 保持与现有服务获取模式一致

## 组件接口

### EventBusInterface接口
```python
class EventBusInterface:
    def subscribe(self, event_type: str, handler: Callable) -> None
    def unsubscribe(self, event_type: str, handler: Callable) -> None
    def publish(self, event_type: str, data: Any = None) -> None
    def clear_all_subscriptions(self) -> None
```

### 事件类型注册表
```python
class EventTypeRegistry:
    IMAGE_LOADED = "image.loaded"
    IMAGE_PROCESSED = "image.processed"
    STATE_CHANGED = "state.changed"
    ERROR_OCCURRED = "error.occurred"
    BATCH_PROGRESS_UPDATED = "batch.progress.updated"
```

## 数据模型

### 基础事件载荷
```python
@dataclass
class BaseEventPayload:
    timestamp: float
    source: str
```

### 图像事件载荷
```python
@dataclass
class ImageEventPayload(BaseEventPayload):
    image_path: Optional[str] = None
    image_size: Optional[tuple] = None
```

## 错误处理

- 事件处理器异常不应影响其他处理器
- 提供简单的错误日志记录
- 避免复杂的错误恢复机制

## 测试策略

- 核心事件总线功能测试
- 事件发布订阅集成测试
- 现有功能回归验证