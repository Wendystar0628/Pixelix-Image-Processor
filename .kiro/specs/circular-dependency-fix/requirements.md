# 循环依赖消除需求文档

## 介绍

当前应用存在严重的循环导入问题：ConfigurationRegistry（core层）直接导入ConfigManager（应用层），违反了分层架构原则。这导致在某些导入场景下出现循环依赖错误，需要通过依赖注入方式彻底解决。

## 需求

### 需求 1: 消除ConfigurationRegistry的直接导入依赖

**用户故事:** 作为开发者，我希望ConfigurationRegistry不直接导入ConfigManager，这样就不会违反分层架构原则

#### 验收标准

1. WHEN ConfigurationRegistry初始化时 THEN 系统 SHALL 通过构造函数注入接收配置数据而不是ConfigManager实例
2. WHEN ConfigurationRegistry需要配置信息时 THEN 系统 SHALL 使用注入的配置数据而不是调用ConfigManager方法
3. WHEN 应用启动时 THEN 系统 SHALL 在DirectServiceInitializer中将配置数据传递给ConfigurationRegistry

### 需求 2: 简化ConfigurationRegistry的职责

**用户故事:** 作为开发者，我希望ConfigurationRegistry只负责配置数据的访问，这样职责更加单一

#### 验收标准

1. WHEN ConfigurationRegistry提供配置访问时 THEN 它 SHALL 只提供简单的数据访问方法
2. WHEN 需要配置缓存时 THEN 系统 SHALL 使用简单的字典缓存而不是复杂的缓存机制
3. WHEN 配置发生变化时 THEN 系统 SHALL 通过重新创建ConfigurationRegistry实例来更新配置

### 需求 3: 保持向后兼容性

**用户故事:** 作为开发者，我希望重构后的ConfigurationRegistry接口保持不变，这样其他代码不需要修改

#### 验收标准

1. WHEN 其他组件调用ConfigurationRegistry方法时 THEN 系统 SHALL 返回相同格式的数据
2. WHEN 应用启动时 THEN 系统 SHALL 确保ConfigurationRegistry正常工作
3. WHEN 运行测试时 THEN 系统 SHALL 不出现循环导入错误

## 非功能需求

### 简单性要求

2. 不引入复杂的设计模式或抽象层
3. 保持代码逻辑简单直观

### 性能要求

1. 配置访问性能不应下降
2. 内存使用不应显著增加
3. 应用启动时间不应受影响