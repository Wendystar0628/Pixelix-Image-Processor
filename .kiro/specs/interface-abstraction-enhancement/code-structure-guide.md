# 代码文件结构规范指导

## 修改前后文件结构对比

### 修改前结构
```
app/core/interfaces/
├── __init__.py
├── app_controller_interface.py
├── config_manager_interface.py  
├── image_processor_interface.py
└── state_manager_interface.py

app/handlers/
├── app_controller.py
├── file_handler.py              # 无接口抽象
├── processing_handler.py        # 无接口抽象
└── preset_handler.py            # 无接口抽象
```

### 修改后结构
```
app/core/interfaces/
├── __init__.py                  # 更新：新增接口导出
├── app_controller_interface.py
├── config_manager_interface.py
├── file_handler_interface.py   # 新增：文件处理接口
├── image_processor_interface.py
├── preset_handler_interface.py # 新增：预设处理接口
├── processing_handler_interface.py # 新增：图像处理接口
└── state_manager_interface.py

app/handlers/
├── app_controller.py           # 更新：使用接口依赖注入
├── file_handler.py             # 更新：实现接口
├── processing_handler.py       # 更新：实现接口
└── preset_handler.py           # 更新：实现接口

app/core/dependency_injection/
└── service_builder.py          # 更新：新增接口绑定配置
```

## 新增文件职责说明

### app/core/interfaces/file_handler_interface.py
- **职责**：定义文件I/O操作的抽象接口
- **核心功能**：文件对话框显示、图像加载保存的抽象方法定义
- **依赖关系**：被FileHandler实现，被AppController依赖

### app/core/interfaces/processing_handler_interface.py  
- **职责**：定义图像处理操作的抽象接口
- **核心功能**：图像操作应用、效果清除的抽象方法和信号定义
- **依赖关系**：被ProcessingHandler实现，被AppController依赖

### app/core/interfaces/preset_handler_interface.py
- **职责**：定义预设管理操作的抽象接口
- **核心功能**：预设保存、删除、加载的抽象方法和信号定义
- **依赖关系**：被PresetHandler实现，被AppController依赖

## 更改文件职责说明

### app/core/interfaces/__init__.py
- **新增职责**：导出新增的Handler接口类型
- **保持职责**：维持现有接口的导出功能
- **清理内容**：无需清理，仅新增导出

### app/handlers/file_handler.py
- **新增职责**：实现FileHandlerInterface接口
- **保持职责**：维持所有现有的文件处理功能
- **清理内容**：无需清理旧代码，仅新增接口继承

### app/handlers/processing_handler.py
- **新增职责**：实现ProcessingHandlerInterface接口
- **保持职责**：维持所有现有的图像处理功能
- **清理内容**：无需清理旧代码，仅新增接口继承

### app/handlers/preset_handler.py
- **新增职责**：实现PresetHandlerInterface接口
- **保持职责**：维持所有现有的预设管理功能
- **清理内容**：无需清理旧代码，仅新增接口继承

### app/handlers/app_controller.py
- **更改职责**：使用接口类型进行依赖注入而非具体类
- **保持职责**：维持所有现有的控制器功能
- **清理内容**：
  - 移除直接的Handler类导入语句
  - 替换构造函数参数类型为接口类型
  - 更新类型注解使用接口类型

### app/core/dependency_injection/service_builder.py
- **新增职责**：配置Handler接口到实现类的绑定关系
- **保持职责**：维持现有的服务构建功能
- **清理内容**：无需清理，仅新增接口绑定配置方法

## 代码清理检查清单

### 导入语句清理
- [ ] 检查app_controller.py中是否移除了直接Handler类的导入
- [ ] 确认使用接口类型替代具体实现类的导入
- [ ] 验证所有新增接口在__init__.py中正确导出

### 类型注解清理
- [ ] 确认AppController构造函数参数使用接口类型
- [ ] 验证内部组件类的类型注解使用接口类型
- [ ] 检查方法参数和返回值的类型注解正确性

### 依赖注入配置清理
- [ ] 确认ServiceBuilder中添加了新的接口绑定
- [ ] 验证ApplicationBootstrap正确注册接口映射
- [ ] 检查依赖解析逻辑的正确性

### 功能完整性检查
- [ ] 确认所有Handler类正确实现对应接口
- [ ] 验证接口方法签名与实现类方法一致
- [ ] 检查信号定义在接口和实现中的一致性

## 需要删除的过时代码清单

### app/handlers/app_controller.py 中需要删除的代码

#### 删除的导入语句
```python
# 完全删除这些导入行
from app.handlers.file_handler import FileHandler
from app.handlers.preset_handler import PresetHandler  
from app.handlers.processing_handler import ProcessingHandler
```

#### 删除的类型注解
```python
# 在构造函数中删除这些具体类型注解，替换为接口类型
file_handler: FileHandler,                    # 删除
preset_handler: PresetHandler,                # 删除
processing_handler: ProcessingHandler,        # 删除

# 在内部组件类中删除这些具体类型注解
file_handler: FileHandler                     # 删除
processing_handler: ProcessingHandler         # 删除
preset_handler: PresetHandler                 # 删除
```

### app/core/dependency_injection/service_builder.py 中需要删除的代码

#### 删除的过时方法
```python
# 完全删除这个方法（如果存在）
def _register_legacy_services(self) -> None:
    """注册遗留服务以保持向后兼容性"""
    # 这些服务暂时保持现有的创建方式
    # 在后续阶段将逐步迁移到依赖注入模式
    pass
```

#### 删除的无类型注解参数
```python
# 在build_app_controller方法中删除这些无类型注解的参数
file_handler,                    # 删除，替换为有类型注解的版本
preset_handler,                  # 删除，替换为有类型注解的版本
processing_handler,              # 删除，替换为有类型注解的版本
```

### 需要清理的注释和文档

#### 删除过时的注释
```python
# 删除类似这样的过时注释
# 这些服务暂时保持现有的创建方式
# 在后续阶段将逐步迁移到依赖注入模式

# 删除类似这样的TODO注释
# TODO: 迁移到依赖注入模式
```

#### 删除过时的文档字符串内容
```python
# 在相关方法的文档字符串中删除类似内容
"""
注意：此方法使用直接类依赖，后续将迁移到接口依赖
"""
```

## 代码清理执行步骤

### 步骤1：备份当前代码
```bash
# 在开始清理前创建备份
git add .
git commit -m "备份：接口抽象实施前的代码状态"
```

### 步骤2：按顺序删除过时代码
1. 首先删除导入语句中的具体类引用
2. 然后删除类型注解中的具体类型
3. 接着删除过时的方法和配置
4. 最后删除过时的注释和文档

### 步骤3：验证删除结果
```bash
# 检查是否还有直接类引用
grep -r "from app.handlers.file_handler import FileHandler" app/
grep -r "from app.handlers.preset_handler import PresetHandler" app/
grep -r "from app.handlers.processing_handler import ProcessingHandler" app/

# 检查是否还有过时的方法
grep -r "_register_legacy_services" app/
```

### 步骤4：测试清理后的代码
```bash
# 激活虚拟环境
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\Rebirth\Scripts\Activate.ps1

# 启动应用测试
python -m app.main
```

## 命名规范要求

### 接口命名规范
- 所有接口使用`*Interface`后缀
- 接口文件名使用下划线分隔的小写形式
- 接口类名使用驼峰命名法

### 文件命名规范
- 接口文件：`{service_name}_interface.py`
- 避免与现有文件名冲突
- 保持与对应实现类的命名一致性

### 方法命名规范
- 接口方法名与实现类方法名完全一致
- 使用描述性的方法名
- 保持现有API的命名不变

## 架构职责边界

### 接口层职责
- 仅定义抽象方法和信号
- 不包含任何实现逻辑
- 不依赖具体的实现细节

### Handler层职责
- 实现对应的接口契约
- 保持现有的业务逻辑不变
- 不添加接口未定义的公共方法

### 依赖注入层职责
- 配置接口到实现的绑定关系
- 管理服务实例的生命周期
- 不涉及具体的业务逻辑实现