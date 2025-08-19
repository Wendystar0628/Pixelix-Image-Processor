# 分层架构合规性代码结构指导

## 修改前后文件结构对比

### 修改前结构
```
app/
├── core/
│   ├── interfaces/
│   │   └── (现有接口文件)
│   ├── processing_context.py          # 直接导入app.config
│   └── ...
├── ui/
│   ├── managers/
│   │   └── analysis_update_manager.py # 直接导入app.config
│   └── panels/managers/
│       └── rendering_engine_manager.py # 直接导入app.config
└── config.py                          # 配置管理器
```

### 修改后结构
```
app/
├── core/
│   ├── interfaces/
│   │   ├── configuration_provider_interface.py  # 新增：配置提供者接口
│   │   └── (现有接口文件)
│   ├── providers/
│   │   ├── __init__.py                          # 新增：提供者导出
│   │   └── app_configuration_provider.py       # 新增：配置提供者实现
│   ├── processing_context.py                   # 修改：使用配置提供者接口
│   └── ...
├── ui/
│   ├── managers/
│   │   └── analysis_update_manager.py          # 修改：通过依赖注入获取配置
│   └── panels/managers/
│       └── rendering_engine_manager.py         # 修改：通过依赖注入获取配置
└── config.py                                   # 保持不变：配置管理器
```

## 新增文件职责说明

### `app/core/interfaces/configuration_provider_interface.py`
- **职责**: 定义配置访问的抽象接口
- **核心功能**: 提供配置获取方法的抽象定义
- **依赖**: 无外部依赖，纯接口定义

### `app/core/providers/app_configuration_provider.py`
- **职责**: 实现配置提供者接口，封装配置访问逻辑
- **核心功能**: 将配置访问请求转发给ConfigManager
- **依赖**: ConfigManagerInterface（通过依赖注入）

### `app/core/providers/__init__.py`
- **职责**: 导出配置提供者实现类
- **核心功能**: 简化配置提供者的导入

## 修改文件变更说明

### `app/core/interfaces/__init__.py`
- **变更**: 添加ConfigurationProviderInterface导出
- **清理**: 无需清理

### `app/core/dependency_injection/service_builder.py`
- **变更**: 添加配置提供者接口绑定方法
- **清理**: 无需清理

### `app/core/container/application_bootstrap.py`
- **变更**: 创建配置提供者实例并注册
- **清理**: 无需清理

### `app/core/processing_context.py`
- **变更**: 通过构造函数注入配置提供者接口
- **清理**: 移除`from app.config import AppConfig`语句
- **清理**: 移除直接创建AppConfig实例的代码

### `app/ui/managers/analysis_update_manager.py`
- **变更**: 通过构造函数注入配置提供者
- **清理**: 移除`from app.config import AppConfig`语句
- **清理**: 移除`self.config = AppConfig()`代码

### `app/ui/panels/managers/rendering_engine_manager.py`
- **变更**: 通过构造函数注入配置提供者
- **清理**: 移除`from app.config import AppConfig`语句
- **清理**: 移除`config = AppConfig()`代码

## 代码清理检查清单

### 必须移除的代码模式
1. **直接配置导入**: `from app.config import AppConfig`
2. **直接配置创建**: `config = AppConfig()`
3. **全局配置访问**: `get_config_manager()`调用
4. **过时注释**: 包含"已重构为不依赖全局配置管理器"等说明
5. **临时变量**: `self.config = AppConfig()`等临时配置实例

### 必须添加的代码模式
1. **接口导入**: `from app.core.interfaces import ConfigurationProviderInterface`
2. **构造函数参数**: `config_provider: ConfigurationProviderInterface`
3. **配置访问**: `self.config_provider.get_xxx()`
4. **依赖注入**: 通过构造函数接收配置提供者

### 具体清理步骤
1. **搜索定位**: 使用`grep -r "from app.config import AppConfig" app/`定位所有直接导入
2. **逐文件清理**: 按文件逐个移除直接配置访问代码
3. **移除实例化**: 删除所有`AppConfig()`实例化代码
4. **清理注释**: 移除过时的重构说明注释
5. **更新构造函数**: 添加配置提供者参数
6. **更新配置访问**: 将`self.config.xxx`改为`self.config_provider.get_xxx()`

### 验证清理完整性
1. 搜索`from app.config import AppConfig`应无结果（除基础设施层）
2. 搜索`AppConfig()`应无结果（除基础设施层）
3. 搜索`get_config_manager()`应无结果
4. 搜索`self.config = AppConfig()`应无结果
5. 所有配置访问应通过配置提供者接口

### 清理验证命令
```bash
# 验证直接配置导入已清理
grep -r "from app.config import AppConfig" app/core/ app/ui/ app/handlers/

# 验证配置实例化已清理  
grep -r "AppConfig()" app/core/ app/ui/ app/handlers/

# 验证全局配置访问已清理
grep -r "get_config_manager()" app/core/ app/ui/ app/handlers/

# 验证临时配置变量已清理
grep -r "self.config = AppConfig" app/
```

## 架构合规性验证

### 分层依赖检查
- 核心层不应直接导入基础设施层
- 处理器层不应直接创建配置实例
- 所有配置访问应通过接口抽象

### 依赖注入验证
- 配置提供者应通过依赖注入容器管理
- 需要配置的服务应通过构造函数注入获取
- 不应存在服务定位器模式的配置访问