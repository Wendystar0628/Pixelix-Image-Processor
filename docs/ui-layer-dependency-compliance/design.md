# UI层依赖合规性设计文档

## 设计概述

通过在Handler层建立UI服务接口层，封装UI层对核心层的访问需求。采用服务门面模式，让UI层通过Handler层统一访问核心服务，同时建立数据模型访问的明确规范。

## 架构设计

### 当前问题架构
```
UI Layer (UI层)
    ↓ 跳级导入（违反分层架构）
Core Layer (核心层) - StateManager, ConfigDataAccessor, Models
```

### 修复后架构
```
UI Layer (UI层)
    ↓ 通过Handler层获取桥接适配器
Handler Layer (处理器层)
    ↓ 注册核心服务到桥接适配器
Core Interfaces Layer (核心接口层)
    ├── CoreServiceInterface (下行桥接接口)
    └── CoreServiceAdapter (下行桥接适配器)
    ↓ 管理核心服务实例
Core Layer (核心层) - StateManager, ConfigDataAccessor
```

## 组件设计

### 1. 核心服务桥接接口

**新增组件：** `app/core/interfaces/core_service_interface.py`

**职责：** 定义UI层访问核心服务的抽象接口

**设计原则：** 复用现有桥接适配器模式，保持架构一致性

**核心方法：**
```python
@abstractmethod
def get_state_manager() -> Any:
    """获取状态管理器实例"""
    pass

@abstractmethod  
def get_config_accessor() -> Any:
    """获取配置访问器实例"""
    pass

@abstractmethod
def get_tool_manager() -> Any:
    """获取工具管理器实例"""
    pass
```

### 2. 核心服务桥接适配器

**新增组件：** `app/core/adapters/core_service_adapter.py`

**职责：** 实现核心服务的桥接适配器，提供服务实例管理

**设计模式：** 与`UpperLayerServiceAdapter`保持相同的设计模式

### 3. 数据模型访问规范

**允许直接导入的模型：**
- 纯数据结构类（如BatchJob、ExportConfig）
- 枚举类型（如BatchJobStatus）
- 参数类（如CurvesParams、LevelsParams）

**必须通过Handler访问：**
- StateManager实例
- ConfigDataAccessor实例  
- ToolManager实例

## 实现策略

### 阶段1：扩展桥接适配器模式
1. 创建CoreServiceInterface接口
2. 创建CoreServiceAdapter适配器
3. 在Handler层注册核心服务到适配器

### 阶段2：Handler层集成桥接适配器
1. 在AppController中集成CoreServiceAdapter
2. 提供获取桥接适配器的方法
3. 确保适配器正确初始化和注册

### 阶段3：UI层逐步迁移
1. UI层通过Handler层获取CoreServiceAdapter
2. 通过适配器访问核心服务而非直接导入
3. 保持现有功能完全不变

## 错误处理策略

### 服务不可用处理
- Handler层方法提供优雅的错误处理
- 返回默认值或空状态而非抛出异常
- 记录适当的警告日志

### 向后兼容性保证
- 保持所有现有UI功能不变
- 渐进式重构，避免破坏性变更
- 提供过渡期的兼容性支持

## 数据流设计

### 核心服务访问流程
```
1. UI组件需要核心服务
   ↓
2. 通过Handler层获取CoreServiceAdapter
   ↓  
3. 通过桥接适配器获取核心服务实例
   ↓
4. 使用核心服务完成业务逻辑
```

### 桥接适配器管理流程
```
1. Handler层初始化时创建CoreServiceAdapter
   ↓
2. 注册StateManager、ConfigDataAccessor等核心服务
   ↓
3. UI层通过Handler层获取适配器实例
   ↓
4. 通过适配器的get_xxx()方法获取具体服务
```