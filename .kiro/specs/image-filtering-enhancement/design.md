# 图像滤波功能增强设计文档

## 概述

本设计文档基于现有的四层分层架构，为数字图像处理工坊添加完整的图像滤波功能。设计遵循现有的操作模式，通过扩展操作类、对话框和菜单系统来实现空间滤波和常规滤镜功能。

## 架构设计

### 核心组件架构

```
UI层 (app/ui/)
├── 滤波菜单项 (MenuManager扩展)
├── 空间滤波对话框组 (dialogs/spatial_filtering/)
└── 常规滤镜对话框组 (dialogs/regular_filters/)

核心层 (app/core/)
├── 空间滤波操作组 (operations/spatial_filtering/)
├── 常规滤镜操作组 (operations/regular_filters/)
└── 操作注册表更新 (operations/registry.py)

处理器层 (app/handlers/)
└── ProcessingHandler扩展 (滤波操作路由)
```

### 操作分类设计

#### 空间滤波操作 (Spatial Filtering Operations)
- **GaussianBlurFilterOp**: 高斯模糊滤波
- **LaplacianEdgeFilterOp**: 拉普拉斯边缘检测
- **SobelEdgeFilterOp**: Sobel边缘检测
- **SharpenFilterOp**: 锐化滤波
- **MeanFilterOp**: 均值滤波

#### 常规滤镜操作 (Regular Filter Operations)
- **EmbossFilterOp**: 浮雕滤镜
- **MosaicFilterOp**: 马赛克滤镜
- **OilPaintingFilterOp**: 油画滤镜
- **SketchFilterOp**: 素描滤镜
- **VintageFilterOp**: 怀旧滤镜

## 组件设计

### 操作类设计

每个滤波操作继承自`ImageOperation`基类，实现标准接口：

**空间滤波操作特点：**
- 基于卷积核的数学运算
- 参数主要为核大小、标准差等数值参数
- 使用OpenCV或NumPy进行高效计算

**常规滤镜操作特点：**
- 基于像素变换和艺术效果算法
- 参数包括强度、块大小、纹理参数等
- 组合多种图像处理技术实现特效

### 对话框设计

**空间滤波对话框组：**
- `GaussianBlurDialog`: 标准差参数调整
- `LaplacianEdgeDialog`: 核大小参数调整
- `SobelEdgeDialog`: 方向选择和阈值调整
- `SharpenDialog`: 锐化强度参数调整
- `MeanFilterDialog`: 核大小参数调整

**常规滤镜对话框组：**
- `EmbossDialog`: 方向和深度参数调整
- `MosaicDialog`: 块大小参数调整
- `OilPaintingDialog`: 笔触大小和细节参数调整
- `SketchDialog`: 线条强度和对比度参数调整
- `VintageDialog`: 色调强度和纹理参数调整

### 菜单集成设计

在现有菜单系统中添加"滤波"主菜单，包含两个子菜单：
- "空间滤波"子菜单：包含5个空间滤波操作
- "常规滤镜"子菜单：包含5个常规滤镜操作

### 参数模型设计

为每个滤波操作创建对应的参数数据类：
- 空间滤波参数类：`SpatialFilterParams`基类及其子类
- 常规滤镜参数类：`RegularFilterParams`基类及其子类

## 数据模型

### 参数数据结构

```python
# 空间滤波参数基类
@dataclass
class SpatialFilterParams:
    pass

# 具体参数类示例
@dataclass  
class GaussianBlurParams(SpatialFilterParams):
    sigma_x: float = 1.0
    sigma_y: float = 1.0
    kernel_size: int = 5

@dataclass
class MosaicParams(RegularFilterParams):
    block_size: int = 10
    preserve_edges: bool = False
```

### 操作序列化

每个滤波操作支持完整的序列化和反序列化，确保：
- 预设保存和加载功能正常
- 批处理操作支持
- 撤销重做功能完整

## 错误处理

### 参数验证
- 对话框级别：实时参数范围检查
- 操作级别：apply方法中的参数有效性验证
- 图像兼容性：检查输入图像格式和尺寸要求

### 异常处理
- 卷积操作异常：核大小超出图像尺寸
- 内存不足异常：大图像滤波处理
- 参数越界异常：滤波强度参数超出有效范围

## 测试策略

### 单元测试重点
- 操作类的apply方法正确性测试
- 参数序列化和反序列化测试
- 边界条件和异常情况测试

### 集成测试重点
- 对话框参数传递正确性
- 菜单操作触发流程完整性
- 预览功能实时性测试

## 性能考虑

### 优化策略
- 预览模式：使用降采样图像进行实时预览
- 卷积优化：利用OpenCV的优化卷积实现
- 内存管理：及时释放中间计算结果

### 响应性保证
- 复杂滤波操作显示进度指示
- 大图像处理采用分块处理策略
- UI线程与计算线程分离

## 扩展性设计

### 插件化支持
- 操作注册机制支持动态添加新滤波器
- 参数对话框模板化设计便于扩展
- 菜单系统支持动态菜单项添加

### 未来增强
- 自定义卷积核编辑器
- 滤波效果预设库
- 批量滤波参数优化建议