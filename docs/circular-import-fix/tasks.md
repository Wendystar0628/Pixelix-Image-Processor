# 循环导入修复任务执行指南

## 执行准备

### 环境准备
```powershell
# 激活虚拟环境
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\Rebirth\Scripts\Activate.ps1

# 验证当前状态
python -c "from app.core import interfaces" # 应该失败，证明循环导入存在
```

## 任务执行顺序

### 任务1：创建基础设施层架构 (优先级：高)

#### 1.1 创建基础设施目录结构
```bash
mkdir -p app/infrastructure/configuration
mkdir -p app/infrastructure/factories
touch app/infrastructure/__init__.py
touch app/infrastructure/configuration/__init__.py  
touch app/infrastructure/factories/__init__.py
```

#### 1.2 实现配置服务接口
**文件**：`app/infrastructure/configuration/config_service_interface.py`
**内容**：定义配置访问的抽象接口
**行数**：约30行
**测试**：`python -c "from app.infrastructure.configuration.config_service_interface import ConfigServiceInterface"`

#### 1.3 实现配置服务实现类
**文件**：`app/infrastructure/configuration/app_config_service.py` 
**内容**：封装原ConfigManager的功能
**行数**：约50行
**清理**：移除对core.interfaces的依赖

### 任务2：重构核心层接口 (优先级：高)

#### 2.1 创建核心抽象层
**文件**：`app/core/abstractions/__init__.py`
**文件**：`app/core/abstractions/config_access_interface.py`
**内容**：定义核心层需要的最小配置接口
**行数**：约25行

#### 2.2 拆分业务接口
**文件**：`app/core/interfaces/business_interfaces.py`
**操作**：从`interfaces.py`中提取纯业务接口
**清理**：移除ConfigManagerInterface相关导入
**行数**：约-15行 (减少)

#### 2.3 更新接口导出
**文件**：`app/core/interfaces/__init__.py`
**操作**：更新导出清单，移除配置相关接口
**清理**：确保无循环导入源头

### 任务3：修复依赖注入 (优先级：高)

#### 3.1 创建基础设施桥接
**文件**：`app/core/dependency_injection/infrastructure_bridge.py`
**内容**：提供基础设施服务访问接口
**行数**：约35行

#### 3.2 重构服务构建器
**文件**：`app/core/dependency_injection/service_builder.py`
**操作**：移除第43行的直接import
**替换**：使用基础设施桥接获取配置服务
**清理**：删除`from app.config import ConfigManager`行
**行数**：约-20行 (减少)

#### 3.3 创建服务工厂
**文件**：`app/infrastructure/factories/service_factory.py`
**内容**：统一创建基础设施服务
**行数**：约40行
**测试**：验证服务创建无循环导入

### 任务4：清理和验证 (优先级：中)

#### 4.1 简化配置文件
**文件**：`app/config.py`
**操作**：移除第10行的core.interfaces导入
**清理**：仅保留AppConfig数据类和基础配置逻辑
**行数**：约-10行 (减少)

#### 4.2 恢复核心接口导入
**文件**：`app/core/__init__.py`
**操作**：取消注释第5-6行
**验证**：`from .interfaces import *`应能正常执行
**测试**：`python -c "from app.core import interfaces"`

#### 4.3 更新初始化流程
**文件**：`app/core/initialization/direct_service_initializer.py`
**操作**：使用基础设施层服务
**清理**：移除直接创建ConfigManager的逻辑
**行数**：约±5行

### 任务5：功能验证测试 (优先级：中)

#### 5.1 基础功能测试
```python
# 测试脚本：test_circular_import_fix.py
def test_no_circular_import():
    # 验证核心接口可正常导入
    from app.core import interfaces
    
def test_config_service_works():
    # 验证配置服务正常工作
    from app.infrastructure.configuration.app_config_service import AppConfigService
    
def test_app_startup():
    # 验证应用正常启动
    # python -m app.main
```

#### 5.2 集成测试
```powershell
# 完整启动测试
python -m app.main
# 应无循环导入错误，应用正常启动
```

## 任务检查点

### 检查点1：基础设施层就绪
- [ ] infrastructure目录结构创建完成
- [ ] 配置服务接口和实现完成
- [ ] 基础功能测试通过

### 检查点2：接口分离完成  
- [ ] 核心抽象层创建完成
- [ ] 业务接口拆分完成
- [ ] 循环导入源头消除

### 检查点3：依赖注入修复
- [ ] 基础设施桥接实现完成
- [ ] 服务构建器重构完成
- [ ] 服务工厂创建完成

### 检查点4：完整验证
- [ ] `app/core/__init__.py`接口导入恢复
- [ ] 应用正常启动无错误
- [ ] 所有旧代码清理完成

## 回滚检查

每个任务执行前先备份关键文件：
- `app/config.py`
- `app/core/__init__.py`  
- `app/core/dependency_injection/service_builder.py`

如需回滚，恢复备份文件即可。