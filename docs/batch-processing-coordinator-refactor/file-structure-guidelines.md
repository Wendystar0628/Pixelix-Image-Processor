# 批处理协调器迁移与整合代码文件规范 (v1.1)

本文档为本次重构任务提供明确的文件组织与迁移规范，确保所有代码改动都符合项目统一的架构标准。

## 1. 核心原则

- **内聚性**: 所有与批处理功能强相关的协调、管理逻辑，都必须内聚于 `app/features/batch_processing/` 模块之内。
- **职责导向**: 文件的命名和存放位置必须清晰地反映其承担的职责。
- **消除冗余**: 任何因迁移而废弃的旧文件或目录都必须被彻底删除。

## 2. 文件迁移路径 (File Migration Paths)

以下表格详细定义了本次重构中涉及到的所有文件的迁移路径。

| 源文件 (Source)                                      | 目标文件 (Destination)                               | 操作   | 备注                                     |
| ---------------------------------------------------- | ---------------------------------------------------- | ------ | ---------------------------------------- |
| `app/handlers/batch_processing/`                     | (无)                                                 | **删除** | 整个旧的协调器目录将被废弃。           |
| `app/handlers/batch_processing/__init__.py`          | (无)                                                 | **删除** | 随目录一同删除。                         |
| `app/handlers/batch_processing/batch_processing_handler.py` | `app/features/batch_processing/handler.py`           | **整合** | 逻辑与功能整合入新的 `handler`，然后删除源文件。 |
| `app/handlers/batch_processing/import_manager.py`    | `app/features/batch_processing/managers/import_manager.py` | **移动** | 职责不变，仅改变存放位置以实现内聚。   |
| `app/handlers/batch_processing/progress_manager.py`  | `app/features/batch_processing/managers/progress_manager.py`| **移动** | 职责不变，仅改变存放位置以实现内聚。   |
| `app/handlers/batch_processing/config_manager.py`    | `app/features/batch_processing/managers/config_manager.py` | **移动** | 职责不变，仅改变存放位置以实现内聚。   |

## 3. 目标目录结构预览

重构完成后，`app/features/batch_processing/` 目录的结构应如下所示，体现了职责的清晰划分：

```
app/
└── features/
    └── batch_processing/
        ├── __init__.py
        ├── handler.py             # <-- 模块总入口，协调器
        ├── worker.py              # 批处理后台工作线程
        │
        ├── managers/              # 存放该功能内部的专属管理器
        │   ├── __init__.py
        │   ├── execution_manager.py
        │   ├── pool_manager.py
        │   ├── job_manager.py
        │   ├── import_manager.py      # <-- 新迁入
        │   ├── progress_manager.py    # <-- 新迁入
        │   └── config_manager.py      # <-- 新迁入
        │
        ├── models.py              # 批处理相关的所有数据模型
        │
        └── ui/                    # (不变) 批处理相关的所有UI组件
            └── ...
```

## 4. 导入路径修复规范

### 4.1 内部导入 (Intra-module Imports)
- **规范**: 在 `app/features/batch_processing/` 模块**内部**，应优先使用**相对导入**。
- **示例**: 在 `handler.py` 中导入 `ProgressManager`：
  - **推荐**: `from .managers.progress_manager import ProgressManager`
  - **不推荐**: `from app.features.batch_processing.managers.progress_manager import ProgressManager`

### 4.2 外部导入 (Cross-module Imports)
- **规范**: 当外部模块需要引用批处理功能时，**必须**通过其统一入口导入。
- **示例**: `BatchProcessingController` 导入 `BatchProcessingHandler`：
  - **正确**: `from app.features.batch_processing.handler import BatchProcessingHandler`
- **禁止**: 外部模块**禁止**直接导入批处理模块内部的管理器。
  - **错误**: `from app.features.batch_processing.managers.job_manager import JobManager`

## 5. 命名与编码风格
- **文件名**: 保持小写蛇形命名法 (`snake_case`)。
- **类名**: 保持大驼峰命名法 (`PascalCase`)。
- **代码风格**: 遵循 PEP 8 规范，确保与项目现有代码风格一致。
- **文档字符串与注释规范**: 所有被移动和修改的类/方法，其 Docstring 都必须被更新，以反映其在新架构下的角色和依赖关系。任何已过时、与新架构不符的注释都必须被移除或修正。
