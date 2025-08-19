# 循环导入修复代码文件结构指导

## 修改前的文件结构

```
app/
├── config.py                           # 导入core.interfaces (第10行) - 循环导入源头
├── core/
│   ├── __init__.py                    # 第5-6行被注释，无法导入interfaces
│   ├── interfaces.py                  # 混合业务和配置接口
│   ├── interfaces/
│   │   ├── config_manager_interface.py # 配置接口在core层 - 架构违反
│   │   └── ...
│   └── dependency_injection/
│       └── service_builder.py         # 第43行导入app.config - 循环导入
└── ...
```

## 修改后的文件结构

```
app/
├── config.py                           # 简化为纯数据结构，移除core导入
├── infrastructure/                     # 新增：基础设施层
│   ├── __init__.py                    # 基础设施层导出
│   ├── configuration/                 # 配置基础设施
│   │   ├── __init__.py
│   │   ├── config_service_interface.py    # 新增：配置服务抽象接口
│   │   └── app_config_service.py          # 新增：配置服务实现
│   └── factories/                     # 服务工厂
│       ├── __init__.py
│       └── service_factory.py            # 新增：基础设施服务工厂
├── core/
│   ├── __init__.py                    # 恢复完整接口导入
│   ├── abstractions/                  # 新增：核心抽象层
│   │   ├── __init__.py
│   │   └── config_access_interface.py    # 新增：核心层配置访问接口
│   ├── interfaces/
│   │   ├── business_interfaces.py        # 重构：纯业务接口
│   │   ├── config_manager_interface.py   # 删除：迁移到基础设施层
│   │   └── ...
│   └── dependency_injection/
│       ├── service_builder.py            # 重构：移除直接导入
│       └── infrastructure_bridge.py      # 新增：基础设施桥接
└── ...
```

## 新增文件职责说明

### 基础设施层文件

#### `infrastructure/configuration/config_service_interface.py`
**职责**：定义配置访问的抽象接口
**依赖**：无外部依赖
**输出**：ConfigServiceInterface抽象类

#### `infrastructure/configuration/app_config_service.py` 
**职责**：实现配置服务，封装ConfigManager
**依赖**：config.py的ConfigManager
**输出**：AppConfigService实现类

#### `infrastructure/factories/service_factory.py`
**职责**：创建和管理基础设施服务实例  
**依赖**：基础设施层组件
**输出**：服务实例工厂方法

### 核心层新增文件

#### `core/abstractions/config_access_interface.py`
**职责**：定义核心层需要的最小配置访问接口
**依赖**：无外部依赖
**输出**：ConfigAccessInterface抽象类

#### `core/dependency_injection/infrastructure_bridge.py`
**职责**：提供基础设施服务的访问桥梁
**依赖**：infrastructure层接口
**输出**：基础设施服务访问方法

## 修改文件变更说明

### `app/config.py` (简化，约-10行)
**变更内容**：
- 移除第10行的`from app.core.interfaces import ConfigManagerInterface`
- ConfigManager类保持不变，仅移除接口继承
- 保留AppConfig数据类定义

**清理内容**：
- 删除对core.interfaces的任何导入
- 移除ConfigManagerInterface的继承声明

### `app/core/__init__.py` (恢复，约+2行)
**变更内容**：  
- 取消注释第5-6行：`from .interfaces import *`
- 恢复完整的接口导出功能

**清理内容**：
- 移除循环导入的临时注释
- 确保接口导入正常工作

### `app/core/interfaces/business_interfaces.py` (拆分，约-15行)
**变更内容**：
- 从`interfaces.py`拆分出纯业务接口
- 移除ConfigManagerInterface相关内容
- 保持现有业务接口不变

**清理内容**：
- 删除所有配置管理相关接口
- 移除对config层的任何依赖

### `app/core/dependency_injection/service_builder.py` (重构，约-20行)
**变更内容**：
- 移除第43行的`from app.config import ConfigManager`
- 使用infrastructure_bridge获取配置服务
- 重构configure_core_services方法

**清理内容**：
- 删除所有直接导入app.config的语句
- 移除ConfigManager的直接实例化代码
- 清理相关的注册逻辑

### `app/core/initialization/direct_service_initializer.py` (微调，约±5行)
**变更内容**：
- 使用基础设施层提供的配置服务
- 保持分层初始化逻辑不变

**清理内容**：
- 移除直接使用ConfigManager的代码
- 确保通过抽象接口访问配置

## 删除文件清单

### 完全删除的文件
- `app/core/interfaces/config_manager_interface.py` (迁移到基础设施层)

### 重命名的文件
- 无重命名文件，仅新增和修改

## 代码清理检查清单

### 循环导入清理
- [ ] config.py不再导入core.interfaces
- [ ] service_builder.py不再导入app.config  
- [ ] 所有core层文件不直接导入config.py

### 旧代码清理
- [ ] 删除ConfigManagerInterface从core.interfaces
- [ ] 移除service_builder中的直接ConfigManager导入
- [ ] 清理临时的循环导入注释

### 接口一致性
- [ ] 新的配置接口提供相同功能
- [ ] 现有业务接口保持不变
- [ ] 服务创建逻辑功能等价

## 命名规范遵循

### 避免重名原则
- 基础设施层使用"Service"后缀：`ConfigService`
- 核心层使用"Access"后缀：`ConfigAccess` 
- 工厂使用"Factory"后缀：`ServiceFactory`
- 桥接使用"Bridge"后缀：`InfrastructureBridge`

### AI友好命名
- 使用完整单词而非缩写
- 文件名明确表达职责
- 目录结构清晰分层
- 接口与实现明确区分