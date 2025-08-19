# MainWindow重构代码文件结构指导

## 修改前的文件结构

```
app/ui/
├── main_window.py (600+行，职责过多)
└── ... (其他UI文件)
```

## 修改后的文件结构

```
app/ui/
├── main_window.py (重构后，约200行)
└── managers/
    ├── main_window_layout_manager.py (UI布局管理)
    └── main_window_connection_manager.py (信号连接管理)
```

## 新增文件职责说明

### app/ui/managers/main_window_layout_manager.py
- **职责**: UI布局的创建和组装
- **核心功能**: 创建分割器、面板布局、动态布局调整
- **约100行代码**

### app/ui/managers/main_window_connection_manager.py  
- **职责**: 集中管理所有信号连接
- **核心功能**: 菜单信号连接、工具栏信号连接、服务信号连接
- **约150行代码**

### app/ui/main_window.py (重构后)
- **职责**: 主窗口容器和管理器协调
- **核心功能**: 基本初始化、管理器创建、事件处理、业务回调
- **约200行代码**

## 代码清理要求

### 必须删除的旧代码

1. **MainWindow中的布局方法**:
   - `_create_central_widget()`
   - `_create_main_widget()`
   - `_create_main_splitter()`
   - `_create_top_splitter()`
   - `_setup_three_column_layout()`
   - `_setup_two_column_layout()`
   - `_create_batch_panel_widget()`
   - `_create_bottom_panel()`
   - `_setup_full_bottom_layout()`
   - `_setup_placeholder_bottom_layout()`
   - `_assemble_main_layout()`

2. **MainWindow中的信号连接方法**:
   - `_connect_menu_signals()`
   - `_connect_toolbar_signals()`
   - `_get_common_signal_mappings()`
   - `_setup_ui_state_manager()`
   - `_register_ui_components()`
   - `_connect_state_management()`
   - `complete_ui_initialization()`

3. **MainWindow中的事件处理方法**:
   - `keyPressEvent()` (移动到事件处理器)
   - `dragEnterEvent()` (移动到事件处理器)
   - `dropEvent()` (移动到事件处理器)
   - `closeEvent()` (移动到事件处理器)

4. **MainWindow中的辅助方法**:
   - `_update_menu_action_state()`
   - `_update_toolbar_action_state()`
   - `_update_action_state()`
   - `_connect_basic_signals()`
   - `_refresh_ui_services()`

### 保留的核心方法

1. **基本初始化**:
   - `__init__()` (简化版)
   - `_get_service()` (服务获取辅助方法)

2. **业务回调**:
   - `_on_image_loaded()`
   - `_on_image_saved()`
   - `_render_and_update_display()`
   - `_show_error_message()`
   - `_show_info_message()`

3. **工具相关**:
   - `_setup_tools()`
   - `_on_tool_changed()`

## 重构原则

1. **彻底清理**: 删除所有移动到新组件的旧代码，避免重复
2. **职责单一**: 每个新文件只负责一个明确的功能领域  
3. **依赖注入**: 通过构造函数传递依赖，避免服务查找
4. **简单设计**: 保持最小化实现，避免过度设计
5. **清晰命名**: 文件和类名清楚表达其职责，便于AI理解

## 实现注意事项

1. **分步实现**: 按任务顺序逐步创建新组件，最后重构MainWindow
2. **保持功能**: 确保重构过程中不破坏现有功能
3. **测试验证**: 每个组件完成后进行基本功能测试
4. **代码注释**: 使用简洁的中文注释，便于AI理解
5. **错误处理**: 对服务不可用等异常情况进行优雅处理