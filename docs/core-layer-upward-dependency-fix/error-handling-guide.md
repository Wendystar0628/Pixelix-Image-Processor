# 核心层向上依赖违反分层架构修复错误处理指导文档

## 概述

本文档针对核心层向上依赖违反分层架构修复项目，预测开发过程中可能出现的基本错误，提供简单的错误分类、诊断方法和修正策略。通过建立简单的桥接适配器模式，可能遇到服务注册失败、适配器访问异常等问题，本文档为这些问题提供快速诊断和解决方案。

## 常见错误类型

### 1. 服务注册错误

**症状特征:**
```python
AttributeError: 'NoneType' object has no attribute 'some_method'
KeyError: 'app_controller'
```

**可能原因:**
- 服务实例未正确注册到适配器
- 服务名称不匹配

**诊断方法:**
```python
# 手动验证适配器注册
def test_adapter_registration(adapter, service_name: str):
    try:
        service = getattr(adapter, f'get_{service_name}')()
        if service is not None:
            print(f"✓ 服务注册成功: {service_name}")
            return service
        else:
            print(f"✗ 服务未注册: {service_name}")
            return None
    except Exception as e:
        print(f"✗ 获取服务失败: {e}")
        return None
```

**修正策略:**
- 验证DirectServiceInitializer中的服务注册调用
- 确保适配器方法名与服务名一致

### 2. 服务创建错误

**症状特征:**
```python
TypeError: __init__() missing 1 required positional argument: 'state_manager'
TypeError: __init__() got an unexpected keyword argument: 'image_processor'
```

**可能原因:**
- 服务类构造函数签名发生变化
- 依赖注入参数名称不匹配

**诊断方法:**
```python
# 检查服务类构造函数签名
import inspect

def check_constructor_signature(module_path: str, class_name: str):
    import importlib
    module = importlib.import_module(module_path)
    service_class = getattr(module, class_name)
    sig = inspect.signature(service_class.__init__)
    
    print(f"{class_name}构造函数参数:")
    for name, param in sig.parameters.items():
        if name != 'self':
            print(f"  {name}: {param.annotation if param.annotation != param.empty else 'Any'}")
```

**修正策略:**
- 在服务创建前验证参数匹配性
- 更新依赖注入的参数名称

### 3. 应用启动错误

**症状特征:**
```python
# 应用无法启动或启动异常
AttributeError: 'ServiceBuilder' object has no attribute 'upper_layer_adapter'
```

**可能原因:**
- 桥接适配器未正确初始化
- 适配器未注册到InfrastructureBridge

**修正策略:**
- 检查桥接适配器的初始化代码
- 验证所有新增文件的导入路径

## 基本质量检查

### 简单验证脚本

```python
# 验证上层服务桥接适配器
def test_upper_layer_adapter():
    from app.core.adapters.upper_layer_service_adapter import UpperLayerServiceAdapter
    
    adapter = UpperLayerServiceAdapter()
    
    # 模拟服务注册
    class MockService:
        def __init__(self, name):
            self.name = name
    
    adapter.register_service('file_handler', MockService('FileHandler'))
    adapter.register_service('app_controller', MockService('AppController'))
    
    # 测试服务访问
    try:
        file_handler = adapter.get_file_handler()
        print("✓ FileHandler访问成功")
    except Exception as e:
        print(f"✗ FileHandler访问失败: {e}")
    
    try:
        app_controller = adapter.get_app_controller()
        print("✓ AppController访问成功")
    except Exception as e:
        print(f"✗ AppController访问失败: {e}")

# 验证应用启动
def test_app_startup():
    try:
        from app.main import main
        print("✓ 应用导入成功")
    except Exception as e:
        print(f"✗ 应用导入失败: {e}")
```

## 完成标准

修复完成后，系统应该达到：

### 功能完整性
1. 应用可以正常启动，无导入错误
2. 所有上层服务可以通过桥接适配器正常访问
3. 业务功能保持完整，无回归问题

### 架构清晰性
1. 核心层无任何向上依赖的直接导入
2. 桥接适配器正确实现服务访问，复用ConfigAccessAdapter成功模式
3. 分层架构原则得到严格遵循

通过这套简化的错误处理指导，可以快速定位和解决重构过程中的基本问题。