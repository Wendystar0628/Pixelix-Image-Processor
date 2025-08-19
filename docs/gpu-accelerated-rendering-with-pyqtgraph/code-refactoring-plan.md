# GPU加速渲染代码重构计划

## 发现的重复和冗余代码

### 1. 重复的初始化模式

**问题描述：**
所有PyQtGraph控件都有相似的初始化代码：
- 创建布局 (`QVBoxLayout`)
- 设置边距为0 (`setContentsMargins(0, 0, 0, 0)`)
- 存储最新分析数据 (`self.latest_analysis_data = {}`)

**影响的文件：**
- `pyqtgraph_histogram_widget.py`
- `pyqtgraph_luma_waveform_widget.py`
- `pyqtgraph_rgb_parade_widget.py`
- `pyqtgraph_hue_saturation_widget.py`
- `pyqtgraph_combined_analysis_widget.py`

### 2. 重复的绘图控件配置

**问题描述：**
多个控件都有相似的绘图控件配置代码：
- 设置背景颜色为白色 (`setBackground('w')`)
- 启用网格 (`showGrid(x=True, y=True, alpha=0.3)`)
- 设置Y轴范围为0-255
- 设置Y轴刻度 `[0, 64, 128, 192, 255]`

**影响的文件：**
- `pyqtgraph_luma_waveform_widget.py`
- `pyqtgraph_rgb_parade_widget.py`
- `pyqtgraph_hue_saturation_widget.py`

### 3. 重复的图像数据处理

**问题描述：**
多个控件都有相似的图像数据处理逻辑：
- 对数缩放 (`np.log1p(data)`)
- 设置图像项目属性 (`autoLevels=True, autoDownsample=True`)
- 设置图像矩形 (`setRect(0, 0, width, 255)`)

**影响的文件：**
- `pyqtgraph_luma_waveform_widget.py`
- `pyqtgraph_rgb_parade_widget.py`

### 4. 重复的清除方法

**问题描述：**
所有控件都有相似的清除方法：
- 清除图像数据或绘图项目
- 重置标题为"无数据"
- 清空存储的分析数据

### 5. 重复的数据存储模式

**问题描述：**
所有控件都使用相同的模式存储分析数据：
```python
self.latest_analysis_data = results.copy()
```

## 重构解决方案

### 1. 创建基类 `PyQtGraphBaseWidget`

创建一个基类来封装所有PyQtGraph控件的通用功能：

```python
class PyQtGraphBaseWidget(QWidget):
    """PyQtGraph控件的基类，提供通用功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.latest_analysis_data = {}
        self._setup_layout()
        
    def _setup_layout(self):
        """设置基本布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout
        
    def _configure_plot_widget(self, plot_widget, title="", y_label="", x_label=""):
        """配置绘图控件的通用属性"""
        plot_widget.setTitle(title)
        plot_widget.setLabel('left', y_label)
        plot_widget.setLabel('bottom', x_label)
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        plot_widget.setBackground('w')
        
    def _configure_image_plot_widget(self, plot_widget, title="", y_label="", x_label=""):
        """配置用于图像显示的绘图控件"""
        self._configure_plot_widget(plot_widget, title, y_label, x_label)
        plot_widget.setYRange(0, 255)
        
        # 设置Y轴刻度
        y_ticks = [0, 64, 128, 192, 255]
        y_axis = plot_widget.getAxis('left')
        y_axis.setTicks([[(v, str(v)) for v in y_ticks]])
        
    def _setup_image_item(self, image_item, data, width=None, height=None):
        """设置图像项目的通用属性"""
        # 对数缩放
        log_data = np.log1p(data)
        
        # 设置图像数据
        image_item.setImage(
            log_data,
            autoLevels=True,
            autoDownsample=True
        )
        
        # 设置图像矩形
        if width is None:
            height, width = data.shape
        image_item.setRect(0, 0, width, 255)
        
    def store_analysis_data(self, results):
        """存储分析数据"""
        self.latest_analysis_data = results.copy() if results else {}
        
    def clear_analysis_data(self):
        """清除存储的分析数据"""
        self.latest_analysis_data = {}
```

### 2. 创建工具函数模块

创建 `pyqtgraph_utils.py` 模块来存放通用的工具函数：

```python
def create_hue_colors(num_bins):
    """创建色相颜色数组"""
    colors = []
    for i in range(num_bins):
        hue_angle = i / num_bins
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(hue_angle, 1.0, 1.0)
        colors.append((int(r*255), int(g*255), int(b*255), 180))
    return colors

def create_gradient_colors(num_bins, base_color=(0, 0, 255)):
    """创建渐变颜色数组"""
    colors = []
    for i in range(num_bins):
        intensity = 0.3 + 0.7 * (i / num_bins)
        r, g, b = base_color
        colors.append((int(r*intensity), int(g*intensity), int(b*intensity), 180))
    return colors
```

### 3. 重构现有控件

将所有PyQtGraph控件重构为继承自基类，并使用通用方法。

## 实施步骤

### 阶段一：创建基础设施
- [ ] 1. 创建 `PyQtGraphBaseWidget` 基类
- [ ] 2. 创建 `pyqtgraph_utils.py` 工具模块
- [ ] 3. 编写单元测试验证基类功能

### 阶段二：重构控件
- [ ] 4. 重构 `PyQtGraphHistogramWidget`
- [ ] 5. 重构 `PyQtGraphLumaWaveformWidget`
- [ ] 6. 重构 `PyQtGraphRGBParadeWidget`
- [ ] 7. 重构 `PyQtGraphHueSaturationWidget`
- [ ] 8. 重构 `PyQtGraphCombinedAnalysisWidget`

### 阶段三：测试和验证
- [ ] 9. 运行性能测试确保重构后性能不受影响
- [ ] 10. 运行功能测试确保所有功能正常
- [ ] 11. 更新文档

## 预期收益

1. **代码减少**：预计减少约30-40%的重复代码
2. **维护性提升**：通用功能集中管理，便于维护和扩展
3. **一致性改善**：所有控件使用统一的配置和行为
4. **可扩展性增强**：新增控件可以轻松继承基类功能

## 风险评估

1. **低风险**：重构主要是代码组织优化，不改变核心逻辑
2. **向后兼容**：所有公共接口保持不变
3. **测试覆盖**：通过现有的性能测试和功能测试验证

## 后续优化建议

1. 考虑为Matplotlib控件也创建类似的基类
2. 统一错误处理和日志记录
3. 添加更多的配置选项和自定义功能