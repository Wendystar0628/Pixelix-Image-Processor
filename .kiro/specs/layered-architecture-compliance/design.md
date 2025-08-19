# 分层架构合规性设计文档

## 设计概述

本设计通过引入配置提供者接口和依赖注入，消除核心层对基础设施层的直接依赖，建立清晰的分层架构边界。设计遵循最小化原则，仅添加必要的抽象层，不改变现有配置功能。

## 架构设计

### 分层依赖关系

```
视图层 (UI Layer)
    ↓ (依赖接口)
控制器层 (Handler Layer) 
    ↓ (依赖接口)
核心层 (Core Layer)
    ↓ (依赖接口)
配置抽象层 (Configuration Abstraction)
    ↓ (实现接口)
基础设施层 (Infrastructure Layer)
```

### 配置抽象结构

```
app/core/interfaces/
├── configuration_provider_interface.py    # 配置提供者接口
└── __init__.py                            # 接口导出

app/core/providers/
├── app_configuration_provider.py          # 应用配置提供者实现
└── __init__.py                            # 提供者导出
```

## 组件设计

### 1. ConfigurationProviderInterface设计

**职责：** 定义配置访问的抽象接口

**核心方法：**
- `get_rendering_mode() -> str` - 获取渲染模式
- `get_proxy_quality_factor() -> float` - 获取代理质量因子
- `get_analysis_update_config() -> dict` - 获取分析更新配置
- `is_feature_enabled(feature_name: str) -> bool` - 检查功能是否启用

### 2. AppConfigurationProvider设计

**职责：** 实现配置提供者接口，封装具体配置访问逻辑

**实现策略：**
- 内部持有ConfigManager实例
- 将配置访问请求转发给ConfigManager
- 提供类型安全的配置访问方法

### 3. 依赖注入集成

**注册策略：**
- 在ServiceBuilder中注册配置提供者接口绑定
- 在ApplicationBootstrap中创建配置提供者实例
- 通过构造函数注入将配置提供者传递给需要的服务

## 实现策略

### 1. 接口定义策略

- 使用ABC抽象基类确保接口契约
- 接口方法仅定义必要的配置访问操作
- 避免暴露配置管理的内部实现细节

### 2. 现有代码迁移策略

- 识别所有直接配置导入的位置
- 将配置访问改为通过依赖注入的配置提供者
- 彻底移除旧的配置访问代码

### 3. 清理策略

**彻底清理原则**: 移除所有违反分层架构的配置访问代码

**清理范围**:
- 移除所有`from app.config import AppConfig`语句（除基础设施层外）
- 移除所有`get_config_manager()`调用
- 移除所有`AppConfig()`直接实例化
- 移除所有`self.config = AppConfig()`临时变量
- 移除相关的过时注释和说明

**替换策略**:
- 更新构造函数以接受配置提供者接口
- 将配置访问改为通过配置提供者接口
- 通过依赖注入容器管理配置提供者生命周期

**清理验证**:
- 使用grep命令验证清理完整性
- 确保系统启动和基本功能正常
- 验证无分层违反残留

## 数据模型

### 配置提供者接口结构

```python
class ConfigurationProviderInterface(ABC):
    """配置提供者抽象接口"""
    
    @abstractmethod
    def get_rendering_mode(self) -> str:
        """获取渲染模式"""
        pass
    
    @abstractmethod
    def get_proxy_quality_factor(self) -> float:
        """获取代理质量因子"""
        pass
    
    @abstractmethod
    def get_analysis_update_config(self) -> dict:
        """获取分析更新配置"""
        pass
    
    @abstractmethod
    def is_feature_enabled(self, feature_name: str) -> bool:
        """检查功能是否启用"""
        pass
```

## 错误处理

### 迁移验证

- 在依赖注入时验证配置提供者是否正确注册
- 在系统启动时检查配置提供者绑定的完整性
- 提供清晰的错误消息指示配置访问问题

### 向后兼容性

- 保持现有配置功能完全不变
- 确保配置访问性能不受影响
- 渐进式迁移，支持新旧代码共存

## 测试策略

### 接口契约测试

- 验证配置提供者接口的完整性
- 确保实现类正确实现所有抽象方法
- 测试依赖注入容器的配置提供者解析功能

### 迁移验证测试

- 验证所有直接配置导入已移除
- 测试配置访问功能的正确性
- 确保系统启动和运行的稳定性

## 部署考虑

### 代码清理

- 移除所有直接配置导入语句
- 更新构造函数参数以使用配置提供者接口
- 清理过时的配置访问代码

### 配置更新

- 更新依赖注入容器的配置提供者绑定
- 确保所有需要配置的服务通过接口获取
- 验证系统启动流程的正确性