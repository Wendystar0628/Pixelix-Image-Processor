# 依赖注入初始化顺序修复代码结构指南

## 目录结构

```
app/
├── core/
│   └── initialization/
│       └── direct_service_initializer.py    # 主要修改：添加AppController创建
├── handlers/
│   └── app_controller.py                    # 主要修改：完善服务注册
├── ui/
│   └── main_window.py                       # 验证：确认正确接收AppController
├── core/container/
│   └── application_bootstrap.py             # 修复：清理机制参数传递
└── application_startup.py                   # 核心修改：启动流程重构
```

## 关键修改点

### 1. direct_service_initializer.py 修改指南

#### 修改位置：_create_layer_3_services方法

**当前结构分析**：
- 该方法创建Handler层服务
- 包括FileHandler、ProcessingHandler、PresetHandler等
- 缺少AppController的创建逻辑

**添加内容框架**：
```python
# 在_create_layer_3_services方法中添加
def _create_layer_3_services(self, layer_1_services, layer_2_services):
    # ... 现有的handler创建逻辑 ...
    
    # 新增：创建AppController
    from app.handlers.app_controller import AppController
    
    # 获取必要的依赖
    state_manager = layer_2_services['state_manager']
    file_handler = services.get('file_handler')
    processing_handler = services.get('processing_handler')
    preset_handler = services.get('preset_handler')
    batch_processor = services.get('batch_processor')  # 可选
    
    # 创建AppController实例
    app_controller = AppController(
        state_manager=state_manager,
        file_handler=file_handler,
        preset_handler=preset_handler,
        processing_handler=processing_handler,
        batch_processor=batch_processor
    )
    
    # 添加到服务字典
    services['app_controller'] = app_controller
    
    return services
```

#### 关键检查点：
- 确保AppController创建时所有依赖都已在前面步骤中创建
- 验证服务字典中包含app_controller
- 确认AppController的桥接适配器已自动配置

### 2. app_controller.py 修改指南

#### 修改位置1：_register_core_services方法

**当前问题**：
- 包含TODO注释的未完成代码
- ConfigDataAccessor注册逻辑缺失

**修改框架**：
```python
def _register_core_services(self):
    """注册核心服务到桥接适配器"""
    # 注册状态管理器
    if self.state_manager:
        self.core_service_adapter.register_service('state_manager', self.state_manager)
        
        # 注册工具管理器（通过StateManager访问）
        if hasattr(self.state_manager, 'tool_manager'):
            self.core_service_adapter.register_service('tool_manager', self.state_manager.tool_manager)
    
    # 注册配置访问器（需要从依赖注入容器获取或通过其他方式）
    # 具体实现取决于ConfigDataAccessor的创建方式
```

#### 修改位置2：构造函数增强

**添加验证逻辑**：
- 验证关键依赖不为None
- 确保桥接适配器正确配置
- 提供初始化完整性检查方法

### 3. application_startup.py 修改指南

#### 修改位置1：_create_main_window方法

**当前问题分析**：
- 查找MainWindow构造调用（约第106行）
- 确认app_controller参数的传递情况

**修改策略**：
```python
def _create_main_window(self):
    """创建MainWindow"""
    # 添加：验证AppController可用性
    app_controller = self._services.get('app_controller')
    if not app_controller:
        raise RuntimeError("AppController未创建或未正确配置")
    
    # 验证桥接适配器配置
    if not hasattr(app_controller, 'get_core_service_adapter'):
        raise RuntimeError("AppController桥接适配器未配置")
    
    core_adapter = app_controller.get_core_service_adapter()
    if not core_adapter:
        raise RuntimeError("核心服务桥接适配器未初始化")
    
    # 验证核心服务注册
    if not core_adapter.get_state_manager():
        raise RuntimeError("StateManager未注册到桥接适配器")
    
    # 创建MainWindow，传递AppController
    self._main_window = MainWindow(
        image_processor=self._services['image_processor'],
        state_manager=self._services['state_manager'],
        analysis_calculator=self._services['analysis_calculator'],
        config_registry=self._services['config_registry'],
        app_controller=app_controller,  # 确保传递有效的AppController
        batch_processing_handler=self._services.get('batch_processing_handler')
    )
```

#### 修改位置2：_cleanup_services方法

**当前问题**：
- 清理过程中可能出现异常
- 需要更健壮的异常处理

**增强框架**：
```python
def _cleanup_services(self):
    """清理服务"""
    print("开始清理服务...")
    if self._bootstrap:
        try:
            self._bootstrap.shutdown()
            print("服务清理完成")
        except Exception as e:
            print(f"服务清理过程中出现警告: {e}")
            print("继续关闭应用...")
```

### 4. application_bootstrap.py 修改指南

#### 修改位置：cleanup_services方法

**当前问题**：
- 调用ServiceCleanupManager.cleanup_all_services()时缺少services参数

**修改框架**：
```python
def cleanup_services(self) -> None:
    """清理服务 - 向后兼容方法"""
    # 获取服务字典
    services = self.service_manager.get_all_services()
    # 传递给清理管理器
    self.cleanup_manager.cleanup_all_services(services)
```

## 验证机制设计

### 启动时验证检查点

1. **服务创建验证**：
   - 检查AppController是否成功创建
   - 验证所有必要依赖是否传递

2. **桥接适配器验证**：
   - 检查get_core_service_adapter()方法可用
   - 验证核心服务已注册

3. **UI创建验证**：
   - 确认MainWindow接收到有效的AppController
   - 验证UI组件能访问核心服务

### 错误处理策略

#### 明确的错误信息
- 指出具体缺失的依赖
- 提供修复建议
- 包含调试所需的上下文信息

#### 优雅的失败处理
- 关键依赖缺失时立即终止
- 清理已创建的资源
- 避免部分初始化状态

## 测试验证清单

### 代码级验证
- [ ] 所有修改文件的语法正确性
- [ ] 导入语句的正确性
- [ ] 方法调用的参数匹配

### 运行时验证
- [ ] AppController在正确时机创建
- [ ] 桥接适配器正确配置
- [ ] MainWindow接收有效的AppController
- [ ] UI组件能正常访问核心服务

### 集成验证
- [ ] 完整启动流程无错误
- [ ] 应用能显示主界面
- [ ] 所有功能模块正常工作
- [ ] 应用能正常退出

## 常见陷阱与解决方案

### 陷阱1：服务创建顺序错误
**问题**：AppController创建时依赖的服务尚未创建
**解决**：严格按照layer_1 → layer_2 → layer_3的顺序

### 陷阱2：参数传递链断裂
**问题**：AppController创建了但没有传递到MainWindow
**解决**：在application_startup.py中添加验证和正确传递

### 陷阱3：桥接适配器配置不完整
**问题**：AppController存在但核心服务未注册
**解决**：确保构造函数中调用_register_core_services()

### 陷阱4：清理机制参数错误
**问题**：cleanup方法调用时参数不匹配
**解决**：确保传递完整的services字典