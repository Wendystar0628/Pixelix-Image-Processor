# 依赖注入重构任务文档

## 任务概述

本任务将分4个阶段实施依赖注入重构，每个阶段都确保系统可正常运行，采用渐进式重构策略最小化风险。

## 阶段1: 接口定义 (Phase 1)

### 任务1.1: 创建核心服务接口
**目标**: 为主要服务定义抽象接口

**新增文件**:
- `app/core/interfaces/__init__.py`
- `app/core/interfaces/image_processor_interface.py`  
- `app/core/interfaces/state_manager_interface.py`
- `app/core/interfaces/config_manager_interface.py`
- `app/core/interfaces/app_controller_interface.py`

**实施步骤**:
1. 创建interfaces目录和__init__.py
2. 基于现有ImageProcessor创建ImageProcessorInterface
3. 基于现有StateManager创建StateManagerInterface  
4. 基于现有ConfigManager创建ConfigManagerInterface
5. 基于现有AppController创建AppControllerInterface

**验收标准**:
- [ ] 所有接口文件创建完成
- [ ] 接口方法覆盖现有服务的主要功能
- [ ] 接口导入无错误

### 任务1.2: 现有服务实现接口
**目标**: 让现有服务类继承对应接口

**修改文件**:
- `app/core/engines/image_processor.py`
- `app/core/managers/state_manager.py`  
- `app/config.py`
- `app/controllers/app_controller.py`

**实施步骤**:
1. ImageProcessor继承ImageProcessorInterface
2. StateManager继承StateManagerInterface
3. ConfigManager继承ConfigManagerInterface
4. AppController继承AppControllerInterface
5. 确保所有接口方法都已实现

**验收标准**:
- [ ] 所有服务类正确继承接口
- [ ] 应用启动无错误
- [ ] 现有功能完全正常

### 任务1.3: 基础测试
**目标**: 验证接口定义的正确性

**新增文件**:
- `tests/core/interfaces/test_interfaces_basic.py`

**实施步骤**:
1. 测试接口导入
2. 测试服务类实现接口
3. 测试接口方法可调用

**验收标准**:
- [ ] 接口测试通过
- [ ] 无导入错误
- [ ] 接口-实现关系正确

## 阶段2: 依赖容器实现 (Phase 2)

### 任务2.1: 创建依赖注入容器
**目标**: 实现基本的依赖注入容器

**新增文件**:
- `app/core/dependency_injection/__init__.py`
- `app/core/dependency_injection/dependency_container.py`
- `app/core/dependency_injection/service_builder.py`

**实施步骤**:
1. 实现DependencyContainer类
   - register_interface方法
   - register_instance方法  
   - resolve方法
   - build_with_dependencies方法
2. 实现ServiceBuilder类
   - configure_core_services方法
   - configure_ui_services方法
3. 基本的循环依赖检测

**验收标准**:
- [ ] 容器可以注册和解析简单依赖
- [ ] 容器可以处理构造函数注入
- [ ] 基本错误处理机制工作

### 任务2.2: 重构应用引导器
**目标**: 替换ServiceFactory为更简单的引导器

**新增文件**:
- `app/core/container/application_bootstrap.py`

**修改文件**:
- `app/core/container/service_factory.py` (简化)

**实施步骤**:
1. 创建ApplicationBootstrap类
2. 迁移ServiceFactory的核心服务配置逻辑
3. 使用DependencyContainer替代ServiceRegistry
4. 保持向后兼容性

**验收标准**:
- [ ] 新引导器可以创建所有核心服务
- [ ] 应用正常启动
- [ ] 服务依赖关系正确

### 任务2.3: 容器测试
**目标**: 测试依赖注入容器的核心功能

**新增文件**:
- `tests/core/dependency_injection/test_dependency_container.py`

**实施步骤**:
1. 测试服务注册和解析
2. 测试构造函数依赖注入
3. 测试循环依赖检测
4. 测试错误处理

**验收标准**:
- [ ] 容器核心功能测试通过
- [ ] 错误场景正确处理
- [ ] 性能满足要求

## 阶段3: 主窗口重构 (Phase 3)

### 任务3.1: 重构MainWindow
**目标**: 将MainWindow改为构造函数注入模式

**新增文件**:
- `app/ui/main_window_injected.py`

**实施步骤**:
1. 复制current MainWindow代码
2. 修改构造函数接收接口类型参数:
   - ImageProcessorInterface
   - StateManagerInterface  
   - AppControllerInterface
3. 移除所有context.get_service()调用
4. 移除_get_service方法
5. 更新所有服务引用为注入的依赖

**验收标准**:
- [ ] 新MainWindow通过构造函数接收所有依赖
- [ ] 无任何全局服务获取
- [ ] UI功能完全正常

### 任务3.2: 更新main.py
**目标**: 使用依赖注入创建MainWindow

**新增文件**:
- `app/main_injected.py`

**实施步骤**:
1. 复制current main.py
2. 使用ApplicationBootstrap配置依赖
3. 通过DependencyContainer解析依赖
4. 使用构造函数注入创建MainWindow
5. 移除AppContext相关代码

**验收标准**:
- [ ] 应用正常启动
- [ ] 所有服务正确注入
- [ ] 功能完整性保持

### 任务3.3: 集成测试
**目标**: 测试重构后的主窗口功能

**新增文件**:
- `tests/ui/test_main_window_injected.py`

**实施步骤**:
1. 测试MainWindow创建
2. 测试基本UI功能
3. 测试服务交互

**验收标准**:
- [ ] 主窗口创建成功
- [ ] 核心功能正常工作
- [ ] 服务间交互正确

## 阶段4: 全局清理 (Phase 4)

### 任务4.1: 移除全局访问器
**目标**: 彻底清理所有全局访问函数

**修改文件**:
- `app/config.py` (移除get_config_manager等)
- `app/context.py` (移除get_app_context等)
- `app/core/managers/state_manager.py` (移除get_state_manager)
- `app/handlers/processing_handler.py` (移除get_processing_handler)

**实施步骤**:
1. 标记所有全局访问器为废弃
2. 确保没有代码还在使用这些函数
3. 删除全局访问器函数
4. 删除相关全局变量
5. 清理导入语句

**验收标准**:
- [ ] 所有`get_*`函数被移除
- [ ] 所有全局变量被清理  
- [ ] 应用正常运行

### 任务4.2: 清理旧代码
**目标**: 移除不再需要的旧代码文件

**删除文件**:
- `app/context.py` (如果不再需要)
- `app/ui/main_window.py` (替换为main_window_injected.py)
- `app/main.py` (替换为main_injected.py)

**重命名文件**:
- `app/main_injected.py` → `app/main.py`
- `app/ui/main_window_injected.py` → `app/ui/main_window.py`

**实施步骤**:
1. 确认新代码完全替代旧代码
2. 删除旧文件  
3. 重命名新文件
4. 更新所有import语句
5. 清理不再使用的测试文件

**验收标准**:
- [ ] 旧代码文件完全移除
- [ ] 新文件正确重命名
- [ ] 所有导入正确更新

### 任务4.3: 最终验证
**目标**: 确保重构完全成功

**验证项目**:
1. 应用正常启动
2. 所有核心功能工作
3. 无全局访问器残留
4. 代码结构清晰

**实施步骤**:
1. 完整的功能测试
2. 性能测试
3. 代码审查
4. 文档更新

**验收标准**:
- [ ] 所有功能正常工作
- [ ] 性能无明显退化
- [ ] 代码质量提升
- [ ] 依赖关系清晰

## 风险控制

### 每阶段的风险控制措施
1. **阶段完成标准**: 每阶段结束时应用都能正常运行
2. **回滚准备**: 保留旧代码直到新代码完全验证
3. **测试驱动**: 关键功能必须有测试覆盖
4. **渐进替换**: 新旧代码并存，逐步切换

### 质量保证
1. **代码审查**: 每个关键文件都需要审查
2. **功能测试**: 每阶段都进行功能完整性测试  
3. **性能监控**: 确保性能不受影响
4. **文档同步**: 及时更新相关文档

## 总结

本任务采用分阶段重构策略，每个阶段都确保系统稳定可运行。通过接口抽象、依赖注入和全局清理三个核心步骤，彻底解决全局状态污染问题，建立清晰的依赖关系。