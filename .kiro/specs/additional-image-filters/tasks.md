# 图像滤镜功能扩展实现计划

## 实现任务

- [x] 1. 扩展滤镜参数数据模型


  - 修改app/core/models/regular_filter_params.py文件
  - 清理旧的未使用参数类（如果存在）
  - 添加10个新增滤镜的参数数据类
  - 确保所有参数类继承自RegularFilterParams基类
  - _需求: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 2. 实现新增滤镜操作类


  - 创建app/core/operations/regular_filters/additional_filters_ops.py文件
  - 实现10个新增滤镜操作类：WatercolorFilterOp、PencilSketchFilterOp、CartoonFilterOp、WarmToneFilterOp、CoolToneFilterOp、FilmGrainFilterOp、NoiseFilterOp、FrostedGlassFilterOp、FabricTextureFilterOp、VignetteFilterOp
  - 所有操作类继承RegularFilterOperation基类
  - 实现各自的apply方法和参数控制逻辑
  - 编写关键滤镜效果验证测试
  - _需求: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1_



- [ ] 5. 更新操作注册表
  - 修改app/core/operations/registry.py文件
  - 清理旧的未使用滤镜导入（如果存在）
  - 添加10个新增滤镜操作类的导入语句
  - 在OPERATION_REGISTRY字典中注册所有新增操作


  - _需求: 6.1, 6.2_

- [ ] 6. 创建新增滤镜对话框
  - 创建app/ui/dialogs/regular_filters/additional_filters_dialogs.py文件
  - 实现10个新增滤镜对话框类：WatercolorDialog、PencilSketchDialog、CartoonDialog、WarmToneDialog、CoolToneDialog、FilmGrainDialog、NoiseDialog、FrostedGlassDialog、FabricTextureDialog、VignetteDialog
  - 所有对话框继承RegularFilterDialog基类
  - 实现各自的参数控制界面和滑块组件
  - 实现_connect_slider_preview_events方法，连接滑块的sliderPressed和sliderReleased事件到ProcessingHandler


  - 实现参数变化时的params_changed信号发射，支持主视图实时预览
  - 确保滑块拖动时使用降采样图像进行快速预览，释放时使用原始分辨率更新
  - _需求: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 7.3_

- [x] 7. 扩展菜单管理器


  - 修改app/ui/managers/menu_manager.py文件
  - 清理旧的未使用滤镜菜单项（如果存在）
  - 在现有的常规滤镜子菜单中添加10个新增滤镜菜单项
  - 为新增滤镜添加菜单项和信号连接
  - _需求: 7.1, 7.2_



- [ ] 8. 扩展对话框管理器
  - 修改app/ui/managers/dialog_manager.py文件
  - 清理旧的未使用滤镜对话框创建逻辑（如果存在）
  - 在_create_dialog方法中添加10个新增滤镜对话框的创建分支
  - 实现新增滤镜对话框的参数初始化和信号连接
  - 确保对话框正确集成到现有的对话框生命周期管理

  - _需求: 7.3, 7.4_

- [ ] 9. 扩展处理器路由
  - 修改app/handlers/processing_handler.py文件
  - 清理旧的未使用滤镜操作处理方法（如果存在）
  - 在apply_simple_operation方法的路由表中添加10个新增滤镜操作映射
  - 为每个新增滤镜实现对应的apply_xxx方法
  - 确保新增滤镜操作正确集成到命令模式和流水线管理
  - _需求: 6.3, 6.4_

- [ ] 10. 集成测试和验证
  - 编写新增滤镜功能集成测试，验证菜单到操作的完整流程
  - 测试新增滤镜操作的预设保存和加载功能
  - 验证新增滤镜操作在批处理中的正确执行
  - 测试撤销重做功能对新增滤镜操作的支持
  - 验证主视图实时预览功能的正确性和响应性
  - _需求: 6.1, 6.2, 6.3, 6.4, 6.5_