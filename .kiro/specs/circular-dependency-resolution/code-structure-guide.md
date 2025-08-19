# 循环依赖解决方案 - 代码文件结构指导

## 文件结构变更概览

### 修改前的文件结构
```
app/core/
├── dependency_injection/
│   ├── dependency_container.py          # 复杂的自动依赖解析容器
│   └── service_builder.py               # 复杂的服务构建器
├── interfaces/
│   ├── configuration_provider_interface.py  # 循环依赖源头接口
│   └── config_manager_interface.py      # 配置管理接口
├── providers/
│   └── app_configuration_provider.py    # 配置提供者实现
└── container/
    └── application_bootstrap.py         # 复杂的引导逻辑
```

### 修改后的文件结构
```
app/core/
├── dependency_injection/
│   └── simple_container.py              # 简化的依赖容器（新增）
├── configuration/
│   └── configuration_registry.py        # 配置注册表（新增）
├── initialization/
│   └── layered_initializer.py          # 分层初始化器（新增）
├── interfaces/
│   └── config_manager_interface.py      # 保留的配置管理接口
└── container/
    └── application_bootstrap.py         # 简化的引导逻辑（重构）
```

## 新增文件职责说明

### app/core/dependency_injection/simple_container.py
- **职责**: 简化的依赖注入容器，只管理实例注册和获取
- **核心功能**: register_instance(), register_factory(), get_instance()
- **设计原则**: 不进行自动依赖解析，避免循环依赖

### app/core/configuration/configuration_registry.py
- **职责**: 中心化的配置管理，替代ConfigurationProviderInterface
- **核心功能**: 配置缓存、配置访问方法
- **设计原则**: 直接依赖ConfigManager，消除循环依赖

### app/core/initialization/layered_initializer.py
- **职责**: 分层服务初始化，确保正确的创建顺序
- **核心功能**: 三层初始化方法，依赖层次管理
- **设计原则**: 按层次顺序创建服务，消除循环依赖可能性

## 需要删除的文件

### 完全删除的文件
- `app/core/interfaces/configuration_provider_interface.py` - 循环依赖源头
- `app/core/providers/app_configuration_provider.py` - 相关实现
- `app/core/dependency_injection/dependency_container.py` - 复杂容器

### 需要重构的文件
- `app/core/dependency_injection/service_builder.py` - 简化或删除
- `app/core/container/application_bootstrap.py` - 大幅简化
- `app/core/interfaces/__init__.py` - 移除已删除接口的导入

## 代码清理检查清单

### 1. 接口清理
- [ ] 删除ConfigurationProviderInterface相关导入
- [ ] 更新__init__.py文件，移除已删除的接口
- [ ] 检查所有使用ConfigurationProviderInterface的地方

### 2. 实现类清理
- [ ] 删除AppConfigurationProvider类
- [ ] 删除相关的工厂方法和注册逻辑
- [ ] 清理ServiceBuilder中的配置提供者相关代码

### 3. 依赖注入清理
- [ ] 删除DependencyContainer类
- [ ] 移除自动依赖解析相关代码
- [ ] 清理循环依赖检测的临时代码

### 4. 导入清理
- [ ] 移除所有对已删除类的导入
- [ ] 更新相关的类型注解
- [ ] 清理未使用的导入语句

## 代码编写规范

### 1. 文件职责原则
- 每个文件只负责一个明确的功能领域
- 避免在单一文件中混合多种职责
- 新增功能时优先考虑创建新文件而非扩展现有文件

### 2. 依赖管理原则
- 使用显式的依赖注入，避免隐式依赖
- 构造函数参数保持简洁，避免过多依赖
- 优先使用组合而非继承

### 3. 注释规范
- 类和方法使用简洁的文档字符串
- 复杂逻辑添加行内注释说明
- 避免冗长的注释，保持代码自解释性

### 4. 错误处理规范
- 使用具体的异常类型
- 提供清晰的错误消息
- 在关键位置添加日志记录

## 重构步骤指导

### 步骤1: 创建新组件
1. 创建SimpleDependencyContainer
2. 创建ConfigurationRegistry
3. 创建LayeredServiceInitializer

### 步骤2: 更新现有代码
1. 重构ApplicationBootstrap使用新组件
2. 更新main.py使用新的初始化流程
3. 修改所有使用配置提供者的地方

### 步骤3: 清理旧代码
1. 删除ConfigurationProviderInterface相关文件
2. 清理DependencyContainer相关代码
3. 移除ServiceBuilder中的冗余逻辑

### 步骤4: 验证和测试
1. 确保应用正常启动
2. 验证所有功能正常工作
3. 检查没有遗留的旧代码引用

## 注意事项

### 避免的反模式
- 不要在新代码中重新引入自动依赖解析
- 不要创建新的循环依赖
- 不要在单一类中混合多种职责

### 推荐的模式
- 使用工厂模式创建复杂对象
- 使用注册表模式管理配置
- 使用分层架构组织服务

### 测试要求
- 每个新组件都需要单元测试
- 集成测试验证服务初始化流程
- 端到端测试确保应用正常启动