# "上帝对象"反模式消除实施任务

## 实施概述

按照依赖顺序实施重构，确保每一步都保持系统可运行状态。重点关注代码简洁性和职责单一性。

## 任务阶段

### 阶段1: 创建服务管理器 🏗️

#### 任务1.1: 创建 ServiceManager
**文件:** `app/core/container/service_manager.py`

**实施步骤:**
1. 创建新文件 `service_manager.py`
2. 实现 `ServiceManager` 类，替代ApplicationBootstrap的services字典
3. 添加服务注册、获取、清理方法（总计约50行代码）

**验证方法:**
- 创建简单测试验证服务注册和获取功能
- 确保线程安全（如果需要）

#### 任务1.2: 集成到 ApplicationBootstrap
1. 在 `ApplicationBootstrap.__init__()` 中创建 `ServiceManager` 实例
2. 暂时保留 `self.services` 属性，后续阶段清理
3. 验证应用仍能正常启动

### 阶段2: 创建服务清理管理器 🧹

#### 任务2.1: 创建 ServiceCleanupManager
**文件:** `app/core/container/service_cleanup_manager.py`

**实施步骤:**
1. 创建新文件 `service_cleanup_manager.py`
2. 将 `ApplicationBootstrap.cleanup_services()` 中的逻辑迁移过来
3. 按服务类型分组清理逻辑（约70行代码）

**清理步骤:**
1. 从 `ApplicationBootstrap` 复制清理逻辑
2. 重构为独立的清理方法
3. 保持原有清理功能不变

#### 任务2.2: 集成清理管理器
1. 在 `ApplicationBootstrap.__init__()` 中创建 `ServiceCleanupManager` 实例
2. 修改 `ApplicationBootstrap.cleanup_services()` 委托给新的清理管理器
3. 验证服务清理功能正常

### 阶段3: 创建生命周期协调器 ⚙️

#### 任务3.1: 创建 AppLifecycleCoordinator
**文件:** `app/core/container/app_lifecycle_coordinator.py`

**实施步骤:**
1. 创建新文件 `app_lifecycle_coordinator.py`
2. 实现应用启动和关闭协调逻辑（约80行代码）
3. 整合服务容器和清理管理器

**实施内容:**
- `startup_application()` 方法：调用 DirectServiceInitializer，注册服务到容器
- `shutdown_application()` 方法：获取服务，调用清理管理器

#### 任务3.2: 集成生命周期协调器
1. 在 `ApplicationBootstrap.__init__()` 中创建 `AppLifecycleCoordinator` 实例
2. 暂时保留现有方法，添加委托调用
3. 验证应用启动和关闭流程

### 阶段4: 彻底清理 ApplicationBootstrap 🗑️

#### 任务4.1: 清理 ApplicationBootstrap 方法
**清理内容:**
1. 删除 `initialize_all_services()` 方法
2. 删除 `cleanup_services()` 方法中的具体实现，改为委托
3. 删除 `create_ui_services()` 方法中的具体实现，改为委托
4. 删除 `self.services` 属性

**修改内容:**
```python
# 简化后的 ApplicationBootstrap
class ApplicationBootstrap:
    def __init__(self, config: AppConfig, config_manager: ConfigManager):
        self.config = config
        self.config_manager = config_manager
        # 创建专门组件
        self.service_registry = ServiceContainerRegistry()
        self.cleanup_manager = ServiceCleanupManager() 
        self.lifecycle_coordinator = AppLifecycleCoordinator(
            self.service_registry, self.cleanup_manager)
        self.ui_service_factory = UIServiceFactory()
        self.application_state = ApplicationState()

    def bootstrap_application(self) -> bool:
        """委托给生命周期协调器"""
        return self.lifecycle_coordinator.startup_application(
            self.config, self.config_manager)
    
    def shutdown(self) -> None:
        """委托给生命周期协调器"""
        self.lifecycle_coordinator.shutdown_application()
        
    def create_ui_services(self, main_window) -> None:
        """委托给UI服务工厂"""
        services = self.service_registry.get_all_services()
        self.ui_service_factory.create_ui_services(main_window, services)
    
    def initialize_all_services(self) -> dict:
        """向后兼容方法"""
        return self.service_registry.get_all_services()
```

#### 任务4.2: 更新 main.py 服务获取方式
**修改内容:**
```python
# 旧方式
services = bootstrap.initialize_all_services()

# 保持不变，但通过新的服务注册表获取
services = bootstrap.initialize_all_services()  # 内部委托给 service_registry
```

#### 任务4.3: 清理不再需要的导入和依赖
1. 检查 `ApplicationBootstrap` 中不再需要的导入
2. 清理不再使用的模块引用
3. 更新相关注释和文档

### 阶段5: 验证和测试 ✅

#### 任务5.1: 核心功能测试
**测试内容:**
验证应用能正常启动、显示主窗口、创建核心服务、正确清理

#### 任务5.2: 代码质量验证
1. 确保每个新类代码行数不超过80行
2. 验证方法数量不超过5个
3. 检查注释的简洁性和准确性

#### 任务5.3: 架构验证
1. 验证 `ApplicationBootstrap` 代码行数减少到50行以内
2. 确认职责分离：每个类只承担一种职责
3. 检查依赖方向：确保没有循环依赖

## 实施注意事项

### 代码风格要求
- 注释保持简洁，能让AI理解即可
- 方法名使用动词开头，清晰表达功能
- 类名使用名词，体现职责

### 风险控制
- 每个阶段完成后立即测试应用启动
- 保留向后兼容的方法，逐步迁移
- 出现问题时可快速回滚到上一阶段

### 性能考虑
- 新增的委托调用开销忽略不计
- 服务容器查找使用字典，O(1)复杂度
- 清理逻辑保持原有效率

## 完成标准

### 功能完成标准
- [ ] 应用能正常启动和关闭
- [ ] 所有核心服务正确创建和清理
- [ ] main.py 调用方式保持不变

### 代码质量标准  
- [ ] ApplicationBootstrap 代码行数 ≤ 50行
- [ ] 每个新类代码行数 ≤ 80行
- [ ] 每个类方法数量 ≤ 5个
- [ ] 旧的服务管理代码完全清理

### 架构质量标准
- [ ] 每个类职责单一明确
- [ ] 无循环依赖
- [ ] 依赖方向正确（低层依赖高层抽象）