# GPU加速渲染 (PyQtGraph) 实施计划

- [ ] 1. **环境准备与依赖集成**
  - 在 `requirements.txt` 文件中添加 `pyqtgraph`。
  - 运行 `pip install -r requirements.txt` 或相应的环境更新命令，确保新依赖被正确安装。
  - _需求: 1.1_

- [ ] 2. **原型验证**
  - 创建一个临时的Python脚本（例如 `prototypes/test_pyqtgraph.py`）。
  - 在脚本中创建一个简单的`QApplication`和`QMainWindow`。
  - 在窗口中添加一个 `pyqtgraph.PlotWidget`，并使用 `setData` 绘制一条简单的正弦曲线。
  - 运行脚本，确认图表能正常显示，没有环境或驱动问题。
  - _需求: 1.1, 3.1_

- [ ] 3. **重构直方图面板**
  - 定位到负责显示数据分析图表的UI文件（推测为 `app/ui/panels/analysis_panel.py` 或类似文件）。
  - 将用于显示直方图的旧图表控件（如 Matplotlib 的 `FigureCanvas`）替换为 `pyqtgraph.PlotWidget`。
  - 在该类的 `__init__` 方法中初始化 `PlotWidget`，并获取其 `PlotItem`。
  - 修改 `update_histogram_plot` 方法：
    - 清除旧的绘图代码。
    - 调用 `plot_item.setData(x=np.arange(256), y=hist_data)` 来更新数据。
    - 根据需要设置画笔（`pen`）和填充（`fillLevel`, `brush`）来调整图表样式，使其接近原始设计。
  - _需求: 2.2, 2.3_

- [ ] 4. **重构RGB波形图面板**
  - 将用于显示RGB波形图的旧控件替换为 `pyqtgraph.PlotWidget`。
  - 在 `__init__` 方法中，向 `PlotWidget` 添加一个 `pyqtgraph.ImageItem`。
  - 修改 `update_waveform_plot` 方法：
    - 清除旧的绘图代码。
    - **注意**: 波形图数据是(256, width)的二维数组，应被视为图像。需要将 `AnalysisCalculator` 返回的波形数据（可能需要堆叠或转置）转换为适合 `setImage` 的NumPy数组。
    - 调用 `image_item.setImage(image_data)` 来高效渲染整个波形图。
    - 可能需要设置 `ImageItem` 的颜色映射（`lookup table`）来模拟RGB三色的效果。
  - _需求: 2.2, 2.3_

- [ ] 5. **重构其他图表**
  - 按照与步骤3和4类似的方法，逐一替换项目中所有其他的数据分析图表（如色相/饱和度图）。
  - _需求: 2.2, 2.3_

- [ ] 6. **代码清理与最终测试**
  - 审查 `app/utils/plot_renderer.py` 文件，删除所有不再被引用的旧的、基于CPU的渲染函数。
  - 完整地运行应用，并进行全面的交互测试。
  - **重点测试**:
    - 反复、快速地拖拽UI分割线，确认无卡顿现象。
    - 加载不同的图像，确认所有图表都能正确更新数据。
    - 在打包后的应用中进行测试，确保依赖被正确包含。
  - _需求: 1.2, 2.1, 3.2_
