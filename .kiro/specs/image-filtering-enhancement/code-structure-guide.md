# 图像滤波功能代码文件结构指导

## 修改前后文件结构对比

### 修改前结构
```
app/
├── core/
│   ├── models/
│   │   └── operation_params.py (现有参数类)
│   └── operations/
│       ├── registry.py (现有操作注册)
│       └── [现有操作类文件]
├── ui/
│   ├── dialogs/
│   │   └── [现有对话框文件]
│   └── managers/
│       ├── menu_manager.py (现有菜单)
│       └── dialog_manager.py (现有对话框管理)
└── handlers/
    └── processing_handler.py (现有处理器)
```

### 修改后结构
```
app/
├── core/
│   ├── models/
│   │   ├── operation_params.py (扩展)
│   │   ├── spatial_filter_params.py (新增)
│   │   └── regular_filter_params.py (新增)
│   └── operations/
│       ├── spatial_filtering/ (新增目录)
│       │   ├── __init__.py
│       │   ├── spatial_filter_base.py
│       │   ├── gaussian_blur_filter_op.py
│       │   ├── laplacian_edge_filter_op.py
│       │   ├── sobel_edge_filter_op.py
│       │   ├── sharpen_filter_op.py
│       │   └── mean_filter_op.py
│       ├── regular_filters/ (新增目录)
│       │   ├── __init__.py
│       │   ├── regular_filter_base.py
│       │   ├── emboss_filter_op.py
│       │   ├── mosaic_filter_op.py
│       │   ├── oil_painting_filter_op.py
│       │   ├── sketch_filter_op.py
│       │   └── vintage_filter_op.py
│       └── registry.py (扩展)
├── ui/
│   ├── dialogs/
│   │   ├── spatial_filtering/ (新增目录)
│   │   │   ├── __init__.py
│   │   │   ├── spatial_filter_dialog_base.py
│   │   │   ├── gaussian_blur_dialog.py
│   │   │   ├── laplacian_edge_dialog.py
│   │   │   ├── sobel_edge_dialog.py
│   │   │   ├── sharpen_dialog.py
│   │   │   └── mean_filter_dialog.py
│   │   └── regular_filters/ (新增目录)
│   │       ├── __init__.py
│   │       ├── regular_filter_dialog_base.py
│   │       ├── emboss_dialog.py
│   │       ├── mosaic_dialog.py
│   │       ├── oil_painting_dialog.py
│   │       ├── sketch_dialog.py
│   │       └── vintage_dialog.py
│   └── managers/
│       ├── menu_manager.py (扩展)
│       └── dialog_manager.py (扩展)
└── handlers/
    └── processing_handler.py (扩展)
```

## 新增文件职责说明

### 核心层新增文件

**app/core/models/spatial_filter_params.py**
- 定义空间滤波参数数据类基类和5个具体参数类
- 提供参数验证和序列化方法

**app/core/models/regular_filter_params.py**
- 定义常规滤镜参数数据类基类和5个具体参数类
- 提供参数验证和序列化方法

**app/core/operations/spatial_filtering/spatial_filter_base.py**
- 空间滤波操作抽象基类，定义卷积操作通用接口
- 提供核大小验证和边界处理通用方法

**app/core/operations/spatial_filtering/[具体操作文件]**
- 每个文件实现一个具体的空间滤波算法
- 继承spatial_filter_base，实现apply方法和参数处理

**app/core/operations/regular_filters/regular_filter_base.py**
- 常规滤镜操作抽象基类，定义艺术效果滤镜通用接口
- 提供像素变换和效果强度控制通用方法

**app/core/operations/regular_filters/[具体操作文件]**
- 每个文件实现一个具体的常规滤镜算法
- 继承regular_filter_base，实现apply方法和效果处理

### UI层新增文件

**app/ui/dialogs/spatial_filtering/spatial_filter_dialog_base.py**
- 空间滤波对话框抽象基类，定义参数调节界面通用布局
- 提供滑块创建和实时预览信号处理通用方法

**app/ui/dialogs/spatial_filtering/[具体对话框文件]**
- 每个文件实现一个空间滤波操作的参数调节界面
- 继承spatial_filter_dialog_base，定义特定参数控件

**app/ui/dialogs/regular_filters/regular_filter_dialog_base.py**
- 常规滤镜对话框抽象基类，定义效果参数界面通用布局
- 提供复合参数控件和预览管理通用方法

**app/ui/dialogs/regular_filters/[具体对话框文件]**
- 每个文件实现一个常规滤镜的参数调节界面
- 继承regular_filter_dialog_base，定义特定效果控件

## 修改文件内容说明

### app/core/models/operation_params.py (扩展)
- 添加滤波参数类的导入语句
- 保持现有参数类不变，仅添加新的导入

### app/core/operations/registry.py (扩展)
- 清理任何旧的滤波操作导入（如果存在）
- 添加10个新滤波操作类的导入语句
- 在OPERATION_REGISTRY字典中注册所有新操作类

### app/ui/managers/menu_manager.py (扩展)
- 清理旧的滤波菜单项创建代码（如果存在）
- 在create_menus方法中添加_create_filtering_menu调用
- 实现_create_filtering_menu方法，创建滤波主菜单和子菜单
- 为10个滤波操作添加菜单项和对应的信号定义

### app/ui/managers/dialog_manager.py (扩展)
- 清理旧的滤波对话框创建逻辑（如果存在）
- 在_create_dialog方法中添加10个滤波对话框的创建分支
- 添加滤波对话框类的导入语句
- 确保对话框参数初始化和信号连接正确

### app/handlers/processing_handler.py (扩展)
- 清理旧的滤波操作处理方法（如果存在）
- 在apply_simple_operation方法的操作映射表中添加10个滤波操作
- 为每个滤波操作实现对应的apply_xxx处理方法
- 添加滤波操作类和参数类的导入语句

## 代码清理指导

### 清理步骤

1. **搜索旧代码**: 在修改文件前，搜索是否存在旧的滤波相关代码
   - 搜索关键词: "filter", "blur", "edge", "emboss", "mosaic"等
   - 检查是否有未完成的滤波功能实现

2. **清理导入语句**: 删除任何旧的滤波相关导入
   - 移除未使用的滤波操作类导入
   - 清理过时的滤波参数类导入

3. **清理方法定义**: 删除旧的滤波处理方法
   - 移除processing_handler中的旧滤波方法
   - 清理menu_manager中的旧滤波菜单创建代码

4. **清理注册项**: 从操作注册表中移除旧的滤波操作
   - 检查OPERATION_REGISTRY中是否有冲突的操作名称
   - 确保新操作名称的唯一性

### 验证清理完成

- 确保没有未使用的导入语句
- 验证没有重复的方法定义
- 检查操作注册表中没有名称冲突
- 确保菜单中没有重复的滤波选项

## 架构合规性检查

### 分层职责验证
- 核心层文件只包含业务逻辑，不包含UI相关代码
- UI层文件只处理界面交互，不包含图像处理算法
- 处理器层只负责协调，不直接实现图像操作

### 依赖关系检查
- 确保新文件遵循现有的依赖注入模式
- 验证操作类无状态设计原则
- 检查对话框类正确继承BaseOperationDialog

### 命名规范验证
- 操作类以"Op"结尾，对话框类以"Dialog"结尾
- 文件名使用snake_case，类名使用PascalCase
- 确保所有新文件名在整个项目中唯一