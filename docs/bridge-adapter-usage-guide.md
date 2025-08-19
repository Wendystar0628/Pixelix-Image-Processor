# 桥接适配器模式使用指南

## 概述

本指南说明如何在项目中正确使用桥接适配器模式，确保核心层严格遵循分层架构原则，避免向上依赖。

## 设计原则

### 分层架构依赖方向
```
Application Layer (应用层)
    ↓ 使用
Features Layer (特性层) 
    ↓ 使用
Business Interfaces Layer (业务接口层)
    ↓ 依赖
Core Layer (核心层) - 只能向下依赖
    ↓ 依赖
Infrastructure Layer (基础设施层)
```

### 核心规则
- **禁止向上导入**: 核心层绝对不能导入handlers层和features层
- **桥接访问**: 核心层通过桥接适配器访问上层服务
- **服务分离**: 服务创建在初始化层，服务访问在核心层

## 桥接适配器架构

### 组件结构
```
app/core/
├── interfaces/
│   └── upper_layer_service_interface.py    # 桥接抽象接口
├── adapters/
│   └── upper_layer_service_adapter.py      # 桥接适配器实现
├── dependency_injection/
│   ├── service_builder.py                  # 无上层导入
│   └── infrastructure_bridge.py            # 适配器注册
└── initialization/
    └── direct_service_initializer.py       # 服务创建和注册
```

## 使用方法

### 1. 添加新的上层服务

当需要在核心层访问新的上层服务时：

**步骤1**: 在桥接接口中添加新方法
```python
# app/core/interfaces/upper_layer_service_interface.py
class UpperLayerServiceInterface(ABC):
    @abstractmethod
    def get_new_service(self) -> Any:
        """获取新服务实例"""
        pass
```

**步骤2**: 在桥接适配器中实现方法
```python
# app/core/adapters/upper_layer_service_adapter.py
class UpperLayerServiceAdapter(UpperLayerServiceInterface):
    def get_new_service(self) -> Any:
        """获取新服务实例"""
        return self._services.get('new_service')
```

**步骤3**: 在初始化器中注册服务
```python
# app/core/initialization/direct_service_initializer.py
def _create_layer_3_services(self, ...):
    # 创建新服务实例
    from app.handlers.new_service import NewService
    new_service = NewService()
    
    # 注册到桥接适配器
    self.upper_layer_adapter.register_service('new_service', new_service)
```

### 2. 在核心层访问上层服务

**正确方式** - 通过桥接适配器访问：
```python
# app/core/dependency_injection/service_builder.py
def some_core_method(self):
    from ..interfaces.upper_layer_service_interface import UpperLayerServiceInterface
    
    upper_layer_adapter = self.infrastructure_bridge.get_service(UpperLayerServiceInterface)
    if upper_layer_adapter:
        service = upper_layer_adapter.get_new_service()
        # 使用服务...
```

**错误方式** - 直接导入上层服务：
```python
# ❌ 违反分层架构 - 绝对禁止
from app.handlers.new_service import NewService  # 不允许在核心层
```

### 3. 检查分层架构合规性

定期运行以下检查确保架构合规：

```bash
# 检查核心层是否有上层导入
grep -r "from app\.handlers\." app/core/dependency_injection/
grep -r "from app\.features\." app/core/dependency_injection/

# 应该返回空结果，如有结果说明存在违规
```

## 最佳实践

### 1. 服务命名规范
- 接口方法: `get_{service_name}()` 
- 注册key: `{service_name}` (与方法名中的service_name一致)

### 2. 错误处理
```python
def get_some_service(self) -> Any:
    service = self._services.get('some_service')
    if service is None:
        logger.warning("Some service not registered in bridge adapter")
    return service
```

### 3. 类型安全
虽然返回类型是Any，但在使用时应明确服务的预期类型：
```python
# 获取服务时添加类型注释
file_handler: FileHandler = upper_layer_adapter.get_file_handler()
```

### 4. 空值检查
```python
upper_layer_adapter = self.infrastructure_bridge.get_service(UpperLayerServiceInterface)
if upper_layer_adapter:
    service = upper_layer_adapter.get_some_service()
    if service:
        # 使用服务
        service.do_something()
```

## 故障排除

### 常见问题

**Q: 获取服务时返回None**
A: 检查服务是否已在DirectServiceInitializer中正确注册

**Q: 无法获取桥接适配器**
A: 确认适配器已在InfrastructureBridge中注册

**Q: IDE提示导入错误**
A: 确保不在核心层直接导入上层服务，使用桥接适配器

### 调试步骤

1. 确认服务实例创建成功
2. 确认服务已注册到桥接适配器
3. 确认桥接适配器已注册到InfrastructureBridge
4. 确认通过正确方式访问服务

## 架构优势

### 1. 分层架构合规
- 核心层零上层导入
- 严格的单向依赖关系
- 消除循环导入风险

### 2. 可维护性
- 上层服务变更不影响核心层
- 清晰的服务访问路径
- 易于测试和调试

### 3. 扩展性
- 新增服务遵循统一模式
- 桥接适配器可复用
- 向后兼容性保证

## 注意事项

1. **只在初始化层创建服务**: 上层服务实例只应在DirectServiceInitializer中创建
2. **核心层只访问不创建**: 核心层通过桥接适配器访问服务，不创建服务
3. **保持接口简单**: 桥接接口保持简单明确，避免过度设计
4. **遵循命名规范**: 统一的方法命名和服务key命名
5. **文档同步更新**: 新增服务时同步更新相关文档

## 总结

桥接适配器模式是确保分层架构合规的关键机制。通过正确使用该模式，可以：

- 彻底消除核心层向上依赖
- 保持代码的清晰性和可维护性  
- 确保系统的稳定性和可扩展性

遵循本指南的最佳实践，可以确保项目始终保持健康的架构状态。