# 循环依赖消除实施任务

## 实施概述

通过重构ConfigurationRegistry为ConfigDataRegistry，消除对ConfigManager的直接导入依赖。采用简单的依赖注入方式，确保分层架构原则得到遵守。

## 实施任务

- [x] 1. 创建新的ConfigDataRegistry


  - 创建 `app/core/configuration/config_data_registry.py` 文件
  - 实现通过配置数据初始化的ConfigDataRegistry类
  - 保持与原ConfigurationRegistry相同的公共接口
  - 移除对ConfigManager的直接导入依赖
  - _需求: 1.1, 1.2, 1.3_

- [x] 2. 修改DirectServiceInitializer


  - 修改 `_create_config_registry()` 方法，创建ConfigDataRegistry而不是ConfigurationRegistry
  - 将配置数据通过构造函数传递给ConfigDataRegistry
  - 更新服务注册名称为 'config_data_registry'
  - 添加向后兼容的 'config_registry' 服务名映射
  - _需求: 1.3, 3.1, 3.2_



- [ ] 3. 验证循环依赖消除
  - 创建简单的导入测试，验证不再出现循环导入错误
  - 验证应用能正常启动，所有配置访问功能正常
  - 验证ConfigDataRegistry的所有方法返回正确的配置值
  - _需求: 2.1, 2.2, 3.3_

- [x] 4. 清理旧的ConfigurationRegistry


  - **彻底删除** `app/core/configuration/configuration_registry.py` 文件
  - 清理所有对旧ConfigurationRegistry的导入引用
  - 更新相关的__init__.py文件，移除旧的导入
  - 确保没有遗留的旧代码引用
  - _需求: 2.3_

## 重要提醒

### 虚拟环境激活
在执行任何测试前，必须先激活虚拟环境：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\Rebirth\Scripts\Activate.ps1
```

### 应用启动测试
每个任务完成后，使用以下命令测试应用启动：
```bash
python -m app.main
```

### 代码清理要求
- **必须彻底删除**旧的ConfigurationRegistry文件和相关导入
- **必须保持**接口兼容性，确保其他代码不需要修改
- **必须验证**循环导入问题已完全解决
- **必须控制**新文件代码行数在40行以内

### 注释编写规范
- 类注释：一行简要说明职责
- 方法注释：一行说明功能，AI能理解即可
- 避免冗长解释，保持简洁明了