# ServiceRegistry清理重构任务文档

## 任务概述

本任务将分4个阶段实施ServiceRegistry清理重构，每个阶段都确保系统可正常运行，采用渐进式重构策略最小化风险。

## 阶段1: PresetHandler重构 (Phase 1)

### 任务1.1: 重构PresetHandler依赖注入
**目标**: 将PresetHandler从ServiceRegistry改为依赖注入

**修改文件**:
- `app/handlers/preset_handler.py`

**实施步骤**:
1. 修改构造函数参数：
   - 移除`service_registry: ServiceRegistry`参数
   - 添加`state_manager: StateManagerInterface`参数
2. 移除ServiceRegistry相关代码：
   - 删除`self.service_registry = service_registry`
   - 删除`cast(StateManager, self.service_registry.get('state_manager'))`
   - 直接使用注入的`state_manager`
3. 清理导入：
   - 移除`from app.core.container import ServiceRegistry`
   - 移除不需要的`cast`导入

**验收标准**:
- [ ] PresetHandler构造函数使用直接依赖注入
- [ ] 无ServiceRegistry相关代码
- [ ] 预设功能正常工作

### 任务1.2: 更新PresetHandler创建方式
**目标**: 修改ApplicationBootstrap中PresetHandler的创建

**修改文件**:
- `app/core/container/application_bootstrap.py`

**实施步骤**:
1. 找到PresetHandler创建位置
2. 修改创建方式：
   - 获取state_manager实例
   - 直接传递给PresetHandler构造函数
3. 更新相关注释

**验收标准**:
- [ ] PresetHandler正确创建
- [ ] 应用正常启动
- [ ] 预设相关功能正常

## 阶段2: AppController重构 (Phase 2)

### 任务2.1: 设计AppController内部组件
**目标**: 将app/controllers/下的控制器整合为AppController内部组件

**修改文件**:
- `app/handlers/app_controller.py`

**实施步骤**:
1. 分析现有子控制器的职责和接口
2. 在AppController内部定义组件类：
   - `FileOperationsComponent` (整合FileIOController)
   - `ImageOperationsComponent` (整合ImageOperationController)
   - `BatchOperationsComponent` (整合BatchProcessingController)
   - `PresetOperationsComponent` (整合PresetController)
3. 修改AppController构造函数：
   - 使用依赖注入接收核心服务
   - 创建内部组件实例
4. 将现有子控制器的方法迁移到对应组件
5. 更新AppController的公共方法，委托给内部组件

**验收标准**:
- [ ] AppController包含所有内部组件
- [ ] 公共接口保持不变
- [ ] 所有功能正常工作

### 任务2.2: 更新AppController创建方式
**目标**: 在ApplicationBootstrap中使用新的AppController

**修改文件**:
- `app/core/container/application_bootstrap.py`
- `app/core/dependency_injection/service_builder.py`

**实施步骤**:
1. 修改service_builder中AppController构建方法：
   - 移除ServiceRegistry参数
   - 添加具体的服务依赖参数
2. 更新ApplicationBootstrap中AppController创建：
   - 获取所需的核心服务
   - 使用依赖注入创建AppController
3. 清理临时方案注释

**验收标准**:
- [ ] AppController正确创建和初始化
- [ ] 所有子功能正常工作
- [ ] 信号连接正确

### 任务2.3: 简单功能测试
**目标**: 验证重构后的核心功能

**新增文件**:
- `tests/handlers/test_app_controller_refactored.py`

**实施步骤**:
1. 测试AppController创建
2. 测试基本文件操作
3. 测试预设操作
4. 测试批处理操作

**验收标准**:
- [ ] 基本功能测试通过
- [ ] 无明显功能回归
- [ ] 核心操作流程正常

## 阶段3: ApplicationBootstrap清理 (Phase 3)

### 任务3.1: 移除ServiceRegistry兼容支持
**目标**: 彻底清理ApplicationBootstrap中的ServiceRegistry代码

**修改文件**:
- `app/core/container/application_bootstrap.py`

**实施步骤**:
1. 移除ServiceRegistry相关代码：
   - 删除`from .service_registry import ServiceRegistry`
   - 删除`self.service_registry = ServiceRegistry()`
   - 删除`_populate_legacy_service_registry()`方法
   - 删除`_create_legacy_services()`方法
2. 简化服务创建流程：
   - 直接使用DependencyContainer
   - 移除向后兼容逻辑
3. 清理相关注释和说明

**验收标准**:
- [ ] 无ServiceRegistry相关代码
- [ ] 应用正常启动
- [ ] 所有服务正确创建

### 任务3.2: 更新服务获取方式
**目标**: 修改main.py中的服务获取

**修改文件**:
- `app/main.py`

**实施步骤**:
1. 移除对`bootstrap.service_registry.get()`的调用
2. 使用DependencyContainer直接解析服务
3. 更新相关注释说明

**验收标准**:
- [ ] 主程序正常启动
- [ ] 服务正确注入到MainWindow
- [ ] 完整启动流程无错误

## 阶段4: 文件清理 (Phase 4)

### 任务4.1: 删除controllers目录
**目标**: 彻底删除不再需要的controllers层

**删除文件**:
- `app/controllers/` (整个目录)
  - `__init__.py`
  - `app_controller.py` (功能已迁移)
  - `base_controller.py`
  - `batch_processing_controller.py`
  - `dialog_controller.py`
  - `file_io_controller.py`
  - `image_loader_controller.py`
  - `image_operation_controller.py`
  - `preset_controller.py`
  - `state_controller.py`
  - `signal_router.py`

**实施步骤**:
1. 确认所有功能已迁移到AppController内部组件
2. 验证无其他地方引用这些文件
3. 删除整个`app/controllers/`目录
4. 清理任何相关的导入语句

**验收标准**:
- [ ] controllers目录完全删除
- [ ] 应用正常运行
- [ ] 无导入错误

### 任务4.2: 删除ServiceRegistry相关文件
**目标**: 移除ServiceRegistry类和相关文件

**删除文件**:
- `app/core/container/service_registry.py`

**修改文件**:
- `app/core/container/__init__.py`

**实施步骤**:
1. 确认ServiceRegistry不再被使用
2. 删除`service_registry.py`文件
3. 更新`__init__.py`：
   - 移除ServiceRegistry导入
   - 从__all__中移除ServiceRegistry
4. 清理任何残留的导入

**验收标准**:
- [ ] ServiceRegistry文件完全删除
- [ ] 无ServiceRegistry相关导入
- [ ] 应用正常运行

### 任务4.3: 清理UI层context使用
**目标**: 移除UI层残留的context相关代码

**修改文件**:
- `app/ui/dialogs/apply_preset_dialog.py`

**实施步骤**:
1. 移除对`preset_handler.context`的访问
2. 通过更直接的方式获取所需功能
3. 简化相关逻辑

**验收标准**:
- [ ] 无context相关代码
- [ ] 预设对话框功能正常
- [ ] 批处理集成正常

### 任务4.4: 最终验证
**目标**: 确保重构完全成功

**验证项目**:
1. 应用正常启动
2. 所有核心功能工作
3. 无ServiceRegistry残留
4. 架构清晰一致

**实施步骤**:
1. 完整的功能测试
2. 代码结构审查
3. 依赖关系验证
4. 清理临时注释

**验收标准**:
- [ ] 所有功能正常工作
- [ ] 架构清晰一致
- [ ] 代码质量提升
- [ ] 无多余文件和代码

## 风险控制

### 每阶段的风险控制措施
1. **阶段完成标准**: 每阶段结束时应用都能正常运行
2. **功能验证**: 关键功能必须验证正常
3. **渐进替换**: 逐步替换，避免大规模同时修改
4. **依赖验证**: 确保依赖注入正确配置

### 质量保证
1. **代码审查**: 关键文件必须审查
2. **功能测试**: 每阶段都进行功能完整性测试  
3. **架构一致性**: 确保符合分层架构原则
4. **文档同步**: 及时更新相关文档

## 清理检查清单

### 必须删除的代码模式
- [ ] `from app.core.container import ServiceRegistry`
- [ ] `service_registry: ServiceRegistry`
- [ ] `self.service_registry.get()`
- [ ] `cast(Type, self.service_registry.get())`
- [ ] ServiceRegistry相关注释和TODO

### 必须保留的功能
- [ ] 所有公共API接口
- [ ] PyQt信号机制
- [ ] 现有业务逻辑
- [ ] 错误处理方式
- [ ] 配置访问方式

## 总结

本任务采用分阶段重构策略，每个阶段都确保系统稳定可运行。通过整合控制器、清理ServiceRegistry和简化依赖关系四个核心步骤，彻底实现纯依赖注入架构，建立清晰一致的代码结构。