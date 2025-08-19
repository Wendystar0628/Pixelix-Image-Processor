# 循环导入修复设计文档

## 设计概述

通过创建基础设施层和抽象接口层，彻底切断config.py与core.interfaces的循环依赖。采用接口分离和依赖倒置原则，建立清晰的分层架构。

## 架构设计

### 修复后的分层架构
```
app/core/                    # 核心业务层 (不依赖具体实现)
├── abstractions/            # 抽象接口层 (新增)
├── interfaces/              # 业务接口层 (清理)
└── ...

app/infrastructure/          # 基础设施层 (新增)
├── configuration/           # 配置基础设施
└── factories/               # 服务工厂

app/config.py               # 纯数据结构 (简化)
```

### 依赖关系修复
```
修复前 (循环):
config.py → core.interfaces → service_builder → config.py

修复后 (单向):
core.abstractions ← infrastructure.configuration ← config.py
core.interfaces (仅业务接口，无配置依赖)
```

## 组件设计

### 1. 基础设施层组件

#### `infrastructure/configuration/config_service_interface.py` (新增)
**职责**：定义配置服务的抽象接口
**代码量**：约30行
```python
# 配置访问抽象接口，替代原ConfigManagerInterface在core中的位置
```

#### `infrastructure/configuration/app_config_service.py` (新增)  
**职责**：实现配置服务接口
**代码量**：约50行
```python
# 封装ConfigManager，提供配置访问服务
```

#### `infrastructure/factories/service_factory.py` (新增)
**职责**：创建基础设施服务实例
**代码量**：约40行
```python
# 负责创建配置服务等基础设施组件
```

### 2. 核心层组件重构

#### `core/abstractions/config_access_interface.py` (新增)
**职责**：定义核心层需要的配置访问抽象
**代码量**：约25行
```python
# 核心层访问配置的最小接口定义
```

#### `core/interfaces/business_interfaces.py` (重构)
**职责**：仅包含业务相关接口，移除配置接口
**代码量**：约-15行
```python
# 从现有interfaces.py拆分出纯业务接口
```

### 3. 依赖注入重构

#### `core/dependency_injection/infrastructure_bridge.py` (新增)
**职责**：连接基础设施层与核心层
**代码量**：约35行
```python
# 提供基础设施服务的访问桥梁
```

#### `core/dependency_injection/service_builder.py` (重构)
**职责**：移除直接import，使用工厂模式
**代码量**：约-20行
```python
# 移除第43行的直接import，使用工厂创建
```

## 实现策略

### 阶段1：基础设施层创建
1. 创建infrastructure目录结构
2. 实现配置服务接口和实现
3. 创建服务工厂

### 阶段2：接口分离
1. 拆分core.interfaces文件
2. 创建核心层抽象接口
3. 建立基础设施桥接

### 阶段3：依赖注入修复
1. 重构service_builder的导入逻辑
2. 使用工厂模式替代直接导入
3. 验证分层初始化流程

### 阶段4：清理和验证
1. 简化config.py为纯数据结构
2. 恢复core/__init__.py接口导入
3. 清理旧的临时代码

## 关键技术点

### 接口分离原则
- ConfigManagerInterface迁移到基础设施层
- 核心层仅定义业务需要的最小配置接口
- 通过适配器模式连接两层

### 依赖倒置实现
- 核心层依赖抽象，不依赖具体实现
- 基础设施层实现抽象接口
- 通过工厂模式管理依赖创建

### 分层边界维护
- 基础设施层不依赖任何上层
- 核心层不直接依赖基础设施实现
- 清晰的依赖方向：业务层→抽象层←基础设施层