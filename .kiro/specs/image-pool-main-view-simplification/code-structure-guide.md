# 代码文件结构规范指导

## 修改前的代码文件结构

```
app/
├── features/batch_processing/managers/
│   └── image_pool_manager.py          # 图像池管理器，包含自动加载逻辑
├── features/batch_processing/
│   └── batch_coordinator.py           # 批处理协调器，处理自动加载信号
├── ui/widgets/
│   └── interactive_image_label.py     # 主视图组件，包含双击打开文件功能
├── ui/managers/
│   ├── toolbar_manager.py             # 工具栏管理器，直接打开文件对话框
│   └── menu_manager.py                # 菜单管理器，直接打开文件对话框
└── ui/panels/batch_processing_panel/
    └── image_pool_panel.py            # 图像池面板，双击加载到主视图
```

## 修改后的代码文件结构

```
app/
├── features/batch_processing/managers/
│   └── image_pool_manager.py          # 纯粹的文件管理功能，无自动加载
├── features/batch_processing/
│   └── batch_coordinator.py           # 移除自动加载逻辑，保持批处理协调
├── ui/widgets/
│   └── interactive_image_label.py     # 纯粹的图像显示组件，无文件IO
├── ui/managers/
│   ├── toolbar_manager.py             # 重定向到图像池的添加功能
│   └── menu_manager.py                # 重定向到图像池的添加功能
└── ui/panels/batch_processing_panel/
    └── image_pool_panel.py            # 保持双击加载功能，作为唯一的文件入口
```

## 各文件职责说明

### 修改的文件

**image_pool_manager.py**
- 职责：纯粹的图像池文件管理，不包含任何自动加载逻辑

**batch_coordinator.py**
- 职责：批处理协调，移除图像添加时的自动加载信号发送

**interactive_image_label.py**
- 职责：图像显示和交互，移除文件打开功能

**toolbar_manager.py**
- 职责：工具栏管理，将添加图像操作重定向到图像池

**menu_manager.py**
- 职责：菜单管理，将打开文件操作重定向到图像池

### 保持不变的文件

**image_pool_panel.py**
- 职责：图像池UI面板，保持双击加载到主视图的功能，作为唯一的用户文件操作入口

## 需要删除的旧代码

### BatchProcessingHandler (batch_coordinator.py)
- 删除 `_on_image_added_to_pool` 方法
- 删除相关的自动加载信号发送逻辑

### ImagePoolManager (image_pool_manager.py)
- 删除自动加载相关的信号定义
- 删除任何触发主视图加载的方法调用

### 主程序 (main.py)
- 删除不再需要的信号连接：`load_image_to_main_view.connect`
- 清理相关的导入语句

### 各个修改文件
- 删除未使用的导入语句
- 删除不再被调用的私有方法
- 删除未使用的变量和常量

## 设计原则

1. **单一职责**：每个文件只负责一个明确的功能
2. **最小修改**：只修改必要的代码，避免大范围重构
3. **数据流清晰**：确保文件 → 图像池 → 主视图的单向流动
4. **用户体验一致**：所有文件添加操作都重定向到图像池
5. **代码整洁**：删除所有旧的、未使用的代码，保持代码库的整洁性