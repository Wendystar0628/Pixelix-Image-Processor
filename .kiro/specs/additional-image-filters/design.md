# 图像滤镜功能扩展设计文档

## 概述

本设计文档基于现有的四层分层架构，为数字图像处理工坊添加10个额外的常见图像滤镜。设计遵循现有的操作模式和代码结构，通过扩展常规滤镜操作类、对话框和菜单系统来实现新增滤镜功能。

## 架构设计

### 核心组件架构

```
UI层 (app/ui/)
├── 常规滤镜菜单扩展 (MenuManager扩展)
└── 新增滤镜对话框组 (dialogs/regular_filters/)

核心层 (app/core/)
├── 新增常规滤镜操作组 (operations/regular_filters/)
└── 操作注册表更新 (operations/registry.py)

处理器层 (app/handlers/)
└── ProcessingHandler扩展 (新增滤镜操作路由)
```

### 新增滤镜分类设计

#### 艺术风格滤镜 (Artistic Style Filters)
- **WatercolorFilterOp**: 水彩画滤镜 - 模拟水彩流动和渗透效果
- **PencilSketchFilterOp**: 铅笔画滤镜 - 创建细腻铅笔素描效果
- **CartoonFilterOp**: 卡通化滤镜 - 简化色彩并增强边缘轮廓

#### 色彩效果滤镜 (Color Effect Filters)
- **WarmToneFilterOp**: 暖色调滤镜 - 增强暖色成分
- **CoolToneFilterOp**: 冷色调滤镜 - 增强冷色成分
- **FilmGrainFilterOp**: 黑白胶片滤镜 - 模拟胶片对比度和颗粒感

#### 纹理效果滤镜 (Texture Effect Filters)
- **NoiseFilterOp**: 噪点滤镜 - 添加可控噪点效果
- **FrostedGlassFilterOp**: 磨砂玻璃滤镜 - 创建模糊和扭曲效果
- **FabricTextureFilterOp**: 织物纹理滤镜 - 添加织物质感
- **VignetteFilterOp**: 暗角滤镜 - 边缘渐变暗化效果

## 组件设计

### 操作类设计

所有新增滤镜操作继承自现有的`RegularFilterOperation`基类，保持一致的接口：

**艺术风格滤镜特点：**
- 基于边缘检测和色彩简化算法
- 参数包括艺术效果强度、细节保持程度等
- 使用OpenCV的图像分割和边缘检测技术

**色彩效果滤镜特点：**
- 基于色彩空间变换和色调调整
- 参数包括色调强度、饱和度调整等
- 使用HSV和LAB色彩空间进行精确控制

**纹理效果滤镜特点：**
- 基于噪声生成和纹理合成算法
- 参数包括纹理强度、纹理尺度等
- 结合随机噪声和图像混合技术

### 对话框设计

**新增滤镜对话框组：**
- `WatercolorDialog`: 流动强度和渗透程度参数调整，支持主视图实时预览
- `PencilSketchDialog`: 线条粗细和阴影强度参数调整，支持主视图实时预览
- `CartoonDialog`: 色彩简化程度和边缘增强参数调整，支持主视图实时预览
- `WarmToneDialog`: 暖色强度和色温调整参数，支持主视图实时预览
- `CoolToneDialog`: 冷色强度和色温调整参数，支持主视图实时预览
- `FilmGrainDialog`: 颗粒强度和对比度参数调整，支持主视图实时预览
- `NoiseDialog`: 噪点类型和强度参数调整，支持主视图实时预览
- `FrostedGlassDialog`: 模糊程度和扭曲强度参数调整，支持主视图实时预览
- `FabricTextureDialog`: 织物类型和纹理强度参数调整，支持主视图实时预览
- `VignetteDialog`: 暗角强度和渐变范围参数调整，支持主视图实时预览

**实时预览机制：**
- 继承现有的`RegularFilterDialog`基类，获得预览功能支持
- 滑块拖动时使用降采样图像进行快速预览
- 滑块释放时使用原始分辨率图像更新最终效果
- 通过`ProcessingHandler`的滑块事件处理机制实现预览控制

### 菜单集成设计

在现有"常规滤镜"子菜单中添加10个新增滤镜选项，保持菜单结构的简洁性。

### 参数模型设计

为每个新增滤镜创建对应的参数数据类，继承自现有的`RegularFilterParams`基类：

```python
@dataclass
class WatercolorParams(RegularFilterParams):
    flow_intensity: float = 0.5
    penetration: float = 0.3
    
@dataclass
class PencilSketchParams(RegularFilterParams):
    line_thickness: float = 1.0
    shadow_intensity: float = 0.5
    
@dataclass
class CartoonParams(RegularFilterParams):
    color_simplification: float = 0.7
    edge_enhancement: float = 0.8
```

## 数据模型

### 参数数据结构

每个滤镜的参数结构设计遵循以下原则：
- 参数数量控制在2-3个以内，避免过度复杂
- 参数范围标准化为0.0-1.0或整数范围
- 提供合理的默认值确保良好的初始效果

### 操作序列化

所有新增滤镜操作支持完整的序列化和反序列化：
- 参数字典序列化用于预设保存
- 操作名称和参数的JSON格式存储
- 向后兼容性保证

## 错误处理

### 参数验证
- 对话框级别：滑块范围限制和实时验证
- 操作级别：apply方法中的参数边界检查
- 图像兼容性：输入图像格式和尺寸验证

### 异常处理
- 算法计算异常：复杂滤镜算法的数值稳定性
- 内存不足异常：大图像处理的内存管理
- 参数无效异常：极端参数值的处理

## 测试策略

### 单元测试重点
- 新增操作类的apply方法功能验证
- 参数序列化和反序列化正确性
- 边界条件和异常情况处理

### 集成测试重点
- 对话框参数传递和信号连接
- 菜单操作触发和流程完整性
- 预览功能的实时响应性

## 性能考虑

### 优化策略
- 预览模式：使用缩略图进行实时预览
- 算法优化：选择高效的图像处理算法
- 内存管理：及时释放临时图像数据

### 响应性保证
- 复杂滤镜显示处理进度
- 大图像采用分块处理策略
- UI线程与计算线程分离

## 代码结构规范

### 文件命名规范
- 操作类文件：`additional_filters_ops.py` (包含10个新增滤镜操作类)
- 对话框文件：`additional_filters_dialogs.py` (包含10个新增滤镜对话框类)
- 参数类文件：使用现有的`regular_filter_params.py`

### 类命名规范
- 操作类：`{FilterName}FilterOp`
- 对话框类：`{FilterName}Dialog`
- 参数类：`{FilterName}Params`

### 代码组织原则
- 功能聚合：相似功能的类放在同一文件中
- 一致性：与现有代码风格保持一致
- 可维护性：清晰的代码结构和适度的注释
- 简洁性：避免创建过多的单独文件

## 扩展性设计

### 插件化支持
- 操作注册机制支持动态添加
- 对话框模板化设计便于扩展
- 参数系统支持灵活配置

### 未来增强
- 滤镜效果预设库
- 自定义滤镜参数组合
- 滤镜效果强度曲线编辑