# 图像滤镜功能扩展代码结构指导

## 代码文件结构对比

### 修改前的代码文件结构
```
app/core/
├── models/
│   └── regular_filter_params.py (现有5个滤镜参数类)
├── operations/
│   ├── regular_filters/
│   │   ├── regular_filter_base.py
│   │   ├── emboss_filter_op.py
│   │   ├── mosaic_filter_op.py
│   │   ├── oil_painting_filter_op.py
│   │   ├── sketch_filter_op.py
│   │   ├── vintage_filter_op.py
│   │   └── __init__.py (导出5个滤镜)
│   └── registry.py (注册5个常规滤镜)

app/ui/
├── dialogs/
│   └── regular_filters/
│       ├── regular_filter_dialog_base.py
│       ├── emboss_dialog.py
│       ├── mosaic_dialog.py
│       ├── oil_painting_dialog.py
│       ├── sketch_dialog.py
│       ├── vintage_dialog.py
│       └── __init__.py (导出5个对话框)
└── managers/
    ├── menu_manager.py (包含5个常规滤镜菜单项)
    └── dialog_manager.py (创建5个常规滤镜对话框)

app/handlers/
└── processing_handler.py (处理5个常规滤镜操作)
```

### 修改后的代码文件结构
```
app/core/
├── models/
│   └── regular_filter_params.py (扩展为15个滤镜参数类)
├── operations/
│   ├── regular_filters/
│   │   ├── regular_filter_base.py (保持不变)
│   │   ├── emboss_filter_op.py (保持不变)
│   │   ├── mosaic_filter_op.py (保持不变)
│   │   ├── oil_painting_filter_op.py (保持不变)
│   │   ├── sketch_filter_op.py (保持不变)
│   │   ├── vintage_filter_op.py (保持不变)
│   │   ├── additional_filters_ops.py (新增，包含10个滤镜操作类)
│   │   └── __init__.py (导出15个滤镜)
│   └── registry.py (注册15个常规滤镜)

app/ui/
├── dialogs/
│   └── regular_filters/
│       ├── regular_filter_dialog_base.py (保持不变)
│       ├── emboss_dialog.py (保持不变)
│       ├── mosaic_dialog.py (保持不变)
│       ├── oil_painting_dialog.py (保持不变)
│       ├── sketch_dialog.py (保持不变)
│       ├── vintage_dialog.py (保持不变)
│       ├── additional_filters_dialogs.py (新增，包含10个对话框类)
│       └── __init__.py (导出15个对话框)
└── managers/
    ├── menu_manager.py (扩展为15个常规滤镜菜单项)
    └── dialog_manager.py (创建15个常规滤镜对话框)

app/handlers/
└── processing_handler.py (处理15个常规滤镜操作)
```

## 新增代码文件职责说明

### 核心操作类文件 (app/core/operations/regular_filters/)

**additional_filters_ops.py**
- 职责：包含10个新增滤镜操作类的实现
- 功能：
  - WatercolorFilterOp：实现水彩画滤镜效果算法，模拟水彩流动和渗透效果
  - PencilSketchFilterOp：实现铅笔画滤镜效果算法，创建细腻铅笔素描效果
  - CartoonFilterOp：实现卡通化滤镜效果算法，简化色彩并增强边缘轮廓
  - WarmToneFilterOp：实现暖色调滤镜效果算法，增强图像暖色成分
  - CoolToneFilterOp：实现冷色调滤镜效果算法，增强图像冷色成分
  - FilmGrainFilterOp：实现黑白胶片滤镜效果算法，模拟经典胶片对比度和颗粒感
  - NoiseFilterOp：实现噪点滤镜效果算法，为图像添加可控噪点效果
  - FrostedGlassFilterOp：实现磨砂玻璃滤镜效果算法，创建模糊和扭曲效果
  - FabricTextureFilterOp：实现织物纹理滤镜效果算法，为图像添加织物质感
  - VignetteFilterOp：实现暗角滤镜效果算法，在图像边缘添加渐变暗化效果

### 用户界面对话框文件 (app/ui/dialogs/regular_filters/)

**additional_filters_dialogs.py**
- 职责：包含10个新增滤镜对话框类的实现
- 功能：
  - WatercolorDialog：提供水彩画滤镜参数调整界面，包含流动强度和渗透程度滑块
  - PencilSketchDialog：提供铅笔画滤镜参数调整界面，包含线条粗细和阴影强度滑块
  - CartoonDialog：提供卡通化滤镜参数调整界面，包含色彩简化程度和边缘增强滑块
  - WarmToneDialog：提供暖色调滤镜参数调整界面，包含暖色强度和色温调整滑块
  - CoolToneDialog：提供冷色调滤镜参数调整界面，包含冷色强度和色温调整滑块
  - FilmGrainDialog：提供黑白胶片滤镜参数调整界面，包含颗粒强度和对比度滑块
  - NoiseDialog：提供噪点滤镜参数调整界面，包含噪点类型选择和强度滑块
  - FrostedGlassDialog：提供磨砂玻璃滤镜参数调整界面，包含模糊程度和扭曲强度滑块
  - FabricTextureDialog：提供织物纹理滤镜参数调整界面，包含织物类型选择和纹理强度滑块
  - VignetteDialog：提供暗角滤镜参数调整界面，包含暗角强度和渐变范围滑块
- 所有对话框都支持主视图实时预览功能

## 修改的代码文件职责说明

### app/core/models/regular_filter_params.py
- 修改内容：添加10个新增滤镜的参数数据类
- 清理内容：移除任何未使用的旧参数类定义
- 职责：定义所有常规滤镜的参数数据结构

### app/core/operations/regular_filters/__init__.py
- 修改内容：添加additional_filters_ops.py中10个新增滤镜操作类的导出
- 清理内容：确保导出列表与实际文件一致
- 职责：统一导出所有常规滤镜操作类

### app/core/operations/registry.py
- 修改内容：添加10个新增滤镜操作类的导入和注册
- 清理内容：移除任何未使用的导入语句
- 职责：维护操作类名称到操作类的映射注册表

### app/ui/dialogs/regular_filters/__init__.py
- 修改内容：添加additional_filters_dialogs.py中10个新增滤镜对话框的导出
- 清理内容：确保导出列表与实际文件一致
- 职责：统一导出所有常规滤镜对话框类

### app/ui/managers/menu_manager.py
- 修改内容：在常规滤镜子菜单中添加10个新增滤镜菜单项
- 清理内容：移除任何未使用的菜单项定义
- 职责：管理应用程序菜单结构，包括滤镜菜单项

### app/ui/managers/dialog_manager.py
- 修改内容：添加10个新增滤镜对话框的创建逻辑
- 清理内容：移除任何未使用的对话框创建分支
- 职责：管理对话框的创建、初始化和生命周期

### app/handlers/processing_handler.py
- 修改内容：添加10个新增滤镜操作的处理方法和路由映射
- 清理内容：移除任何未使用的处理方法
- 职责：处理用户操作请求，协调核心服务和UI组件

## 代码清理指导

### 清理原则
1. **彻底移除**：删除所有未使用的导入语句、类定义和方法
2. **一致性检查**：确保导入、注册和导出的一致性
3. **命名规范**：遵循现有的命名约定和代码风格
4. **注释更新**：更新相关注释以反映新的功能范围

### 清理检查清单
- [ ] 移除未使用的导入语句
- [ ] 删除未使用的类定义和方法
- [ ] 更新导出列表以匹配实际文件
- [ ] 验证注册表的完整性和一致性
- [ ] 检查菜单项和对话框的对应关系
- [ ] 确保处理器路由的完整覆盖

## 文件命名规范

### 操作类文件命名
- 格式：`additional_filters_ops.py` (包含所有10个新增滤镜操作类)

### 对话框文件命名
- 格式：`additional_filters_dialogs.py` (包含所有10个新增滤镜对话框类)

### 类命名规范
- 操作类：`{FilterName}FilterOp`
- 对话框类：`{FilterName}Dialog`
- 参数类：`{FilterName}Params`

### 方法命名规范
- 处理器方法：`apply_{filter_name}`
- 示例：`apply_watercolor`, `apply_pencil_sketch`

## 架构合规性检查

### 分层架构合规
- 核心层不依赖UI层或处理器层
- UI层通过信号与处理器层通信
- 处理器层协调核心层和UI层的交互

### 依赖注入合规
- 对话框通过构造函数接收ProcessingHandler实例
- 操作类保持无状态设计
- 参数通过数据类传递

### 接口一致性
- 所有滤镜操作继承RegularFilterOperation基类
- 所有对话框继承RegularFilterDialog基类
- 保持现有的序列化和反序列化接口