# "上帝对象"反模式消除设计文档

## 设计概述

将 `ApplicationBootstrap` 的职责拆分为4个专门组件，实现彻底的职责分离。每个组件职责单一，代码简洁，易于维护。

## 组件设计

### 1. ServiceManager (服务管理器)
**文件路径:** `app/core/container/service_manager.py`

**职责:** 专门管理服务实例的存储和获取，替代ApplicationBootstrap中的services字典

```python
class ServiceManager:
    """服务管理器 - 替代ApplicationBootstrap中的services字典"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
    
    def register_service(self, name: str, service: Any) -> None:
        """注册服务"""
        
    def get_service(self, name: str) -> Any:
        """获取服务"""
        
    def get_all_services(self) -> Dict[str, Any]:
        """获取所有服务，与现有bootstrap.services用法兼容"""
        
    def clear_all(self) -> None:
        """清空所有服务"""
```

### 2. ServiceCleanupManager (服务清理管理器)
**文件路径:** `app/core/container/service_cleanup_manager.py`

**职责:** 专门处理各种服务的清理逻辑

```python
class ServiceCleanupManager:
    """服务清理管理器 - 专门处理服务清理"""
    
    def cleanup_all_services(self, services: Dict[str, Any]) -> None:
        """清理所有服务"""
        
    def cleanup_analysis_services(self, services: Dict[str, Any]) -> None:
        """清理分析相关服务"""
        
    def cleanup_batch_services(self, services: Dict[str, Any]) -> None:
        """清理批处理相关服务"""
```

### 3. AppLifecycleCoordinator (应用生命周期协调器)  
**文件路径:** `app/core/container/app_lifecycle_coordinator.py`

**职责:** 专门管理应用的启动和关闭生命周期，整合DirectServiceInitializer

```python
class AppLifecycleCoordinator:
    """应用生命周期协调器 - 整合DirectServiceInitializer和服务管理"""
    
    def __init__(self, service_manager: ServiceManager,
                 cleanup_manager: ServiceCleanupManager):
        
    def startup_application(self, config, config_manager) -> bool:
        """启动应用，委托DirectServiceInitializer创建服务"""
        
    def shutdown_application(self) -> None:
        """关闭应用"""
```

### 4. ApplicationBootstrap (简化后的应用引导器)
**文件路径:** `app/core/container/application_bootstrap.py` (修改现有文件)

**职责:** 仅负责委托协调，不再直接管理任何具体逻辑

```python
class ApplicationBootstrap:
    """应用引导器 - 仅负责委托协调"""
    
    def __init__(self, config: AppConfig, config_manager: ConfigManager):
        self.config = config
        self.config_manager = config_manager
        # 创建专门组件
        self.service_manager = ServiceManager()
        self.cleanup_manager = ServiceCleanupManager()
        self.lifecycle_coordinator = AppLifecycleCoordinator(
            self.service_manager, self.cleanup_manager)
        # 保留必要组件
        self.ui_service_factory = UIServiceFactory()
        self.application_state = ApplicationState()
    
    def bootstrap_application(self) -> bool:
        """启动应用 - 委托给生命周期协调器"""
        return self.lifecycle_coordinator.startup_application(
            self.config, self.config_manager)
    
    def shutdown(self) -> None:
        """关闭应用 - 委托给生命周期协调器"""  
        self.lifecycle_coordinator.shutdown_application()
        
    def initialize_all_services(self) -> dict:
        """向后兼容方法 - 返回服务字典"""
        return self.service_manager.get_all_services()
```

## 架构图

```
ApplicationBootstrap (纯协调器，≤50行)
    ↓
AppLifecycleCoordinator (生命周期管理)
    ↓                ↓
ServiceManager        ServiceCleanupManager
(服务存储管理)         (服务清理管理)
    ↓
DirectServiceInitializer (现有的服务创建器)
```

## 数据流设计

### 启动流程
1. `ApplicationBootstrap.bootstrap_application()` 委托给 `AppLifecycleCoordinator`
2. `AppLifecycleCoordinator` 调用现有的 `DirectServiceInitializer` 创建服务
3. 创建的服务存储到 `ServiceManager` 替代原有的`self.services`字典  
4. 返回启动成功状态

### 关闭流程
1. `ApplicationBootstrap.shutdown()` 委托给 `AppLifecycleCoordinator`
2. `AppLifecycleCoordinator` 从 `ServiceManager` 获取所有服务
3. 调用 `ServiceCleanupManager` 清理所有服务（迁移现有清理逻辑）
4. `ServiceManager` 清空服务容器

## 接口设计

### ServiceManager 接口
- `register_service(name, service)` - 注册服务
- `get_service(name)` - 获取单个服务  
- `get_all_services()` - 获取所有服务（兼容现有用法）
- `clear_all()` - 清空容器

### ServiceCleanupManager 接口
- `cleanup_all_services(services)` - 清理所有服务
- `cleanup_analysis_services(services)` - 清理分析线程
- `cleanup_batch_services(services)` - 清理批处理

### AppLifecycleCoordinator 接口  
- `startup_application(config, config_manager)` - 启动应用
- `shutdown_application()` - 关闭应用

## 错误处理策略

### 启动失败处理
- 如果服务创建失败，立即调用已创建服务的清理
- 返回失败状态，不继续后续步骤

### 清理失败处理
- 单个服务清理失败不影响其他服务清理
- 记录清理失败的详细信息
- 继续清理剩余服务

## 向后兼容性

main.py调用方式完全保持不变：
```python
bootstrap = ApplicationBootstrap(config, config_manager)
services = bootstrap.initialize_all_services()  # 内部委托给ServiceManager
```

## 代码清理计划

### ApplicationBootstrap 清理内容
1. 删除 `self.services` 属性
2. 删除 `initialize_all_services()` 方法
3. 删除 `cleanup_services()` 方法  
4. 删除 `create_ui_services()` 方法
5. 简化 `bootstrap_application()` 为委托调用
6. 简化 `shutdown()` 为委托调用

### 清理验证
- 确保删除的方法在其他地方没有直接调用
- 更新 main.py 中的服务获取方式
- 清理导入的不再需要的模块