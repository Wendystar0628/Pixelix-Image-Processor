# 批处理协调器迁移与整合重构任务指导 (v1.1)

本任务清单旨在为开发者提供一个清晰、分步的执行路径，以确保重构过程的顺利进行。请严格按照任务顺序执行，并在完成每一步后进行验证。

## 阶段 1：准备与迁移 (Preparation & Migration)

- [ ] **任务 1.1：重构与整合 Handler 逻辑**
    - **目标**: 将旧 `handler` 的功能和职责整合进新 `handler`，并建立正确的依赖关系。
    - **步骤**:
        1.  打开 `app/handlers/batch_processing/batch_processing_handler.py` (旧) 和 `app/features/batch_processing/handler.py` (新)。
        2.  **重构**新 `handler` 的 `__init__` 方法，使其接收 `JobManager`, `StateManager` 等所有**外部核心依赖**作为参数。
        3.  在新 `handler` 的 `__init__` 方法中，**实例化**所有**内部管理器** (`ImportManager`, `ProgressManager`, `ConfigManager`)，并将所需的核心依赖传递给它们。
        4.  将旧 `handler` 中与信号连接、方法委托相关的逻辑，**迁移并适配**到新 `handler` 中。
    - **验证**: 确保新 `handler.py` 在逻辑上完整，并且正确地管理了其内部和外部的依赖关系。

- [ ] **任务 1.2：迁移管理器 (Managers)**
    - **目标**: 将旧的协调器管理器移动到新的功能模块目录中。
    - **步骤**:
        1.  将文件 `app/handlers/batch_processing/import_manager.py` **移动**到 `app/features/batch_processing/managers/`。
        2.  将文件 `app/handlers/batch_processing/progress_manager.py` **移动**到 `app/features/batch_processing/managers/`。
        3.  将文件 `app/handlers/batch_processing/config_manager.py` **移动**到 `app/features/batch_processing/managers/`。
    - **验证**: 确认上述文件已出现在新的目录位置，并且原位置已不存在这些文件。

## 阶段 2：修复与整合 (Fixing & Integration)

- [ ] **任务 2.1：修复新 Handler 的内部导入**
    - **目标**: 更新 `handler.py` 内部的 `import` 语句，使其指向正确的位置。
    - **步骤**:
        1.  在 `app/features/batch_processing/handler.py` 中，查找所有 `import` 语句。
        2.  将所有指向旧管理器位置的导入，更改为指向新的管理器位置（例如 `from .managers.progress_manager import ...`）。
    - **验证**: 使用Linter或IDE检查 `handler.py` 文件，确保没有未解析的导入错误。

- [ ] **任务 2.2：修复 Controller 的导入**
    - **目标**: 将 `BatchProcessingController` 的依赖从旧 `handler` 切换到新 `handler`。
    - **步骤**:
        1.  打开 `app/controllers/batch_processing_controller.py`。
        2.  找到导入 `BatchProcessingHandler` 的语句。
        3.  将其从 `from app.handlers.batch_processing.handler import BatchProcessingHandler` 修改为 `from app.features.batch_processing.handler import BatchProcessingHandler`。
    - **验证**: 检查 `BatchProcessingController` 文件，确保没有导入错误。

- [ ] **任务 2.3：修复应用上下文 (`AppContext`) 的导入与实例化**
    - **目标**: 更新应用的依赖注入中心，使其能正确创建并提供新的 `Handler` 实例。
    - **步骤**:
        1.  打开 `app/context.py` (或类似文件)。
        2.  将 `BatchProcessingHandler` 的导入路径修改为 `from app.features.batch_processing.handler import BatchProcessingHandler`。
        3.  **修改** `BatchProcessingHandler` 的**实例化代码**，确保所有必需的核心依赖（`JobManager`, `StateManager`等）都作为参数被正确传入。
    - **验证**: 检查 `AppContext` 文件，确保没有导入和依赖注入的错误。

## 阶段 3：清理与验证 (Cleanup & Verification)

- [ ] **任务 3.1：删除旧的协调器代码**
    - **目标**: 彻底移除已废弃的旧代码。
    - **步骤**:
        1.  **删除**整个 `app/handlers/batch_processing/` 目录。
    - **验证**: 确认该目录已从文件系统中消失。

- [ ] **任务 3.2：完整功能回归测试**
    - **目标**: 确保重构没有引入任何功能性缺陷 (regression)。
    - **步骤**:
        1.  启动应用程序。
        2.  系统性地测试所有批处理功能（具体测试用例待定）。
    - **验证**: 所有测试用例均通过，且功能表现与重构前一致。

- [ ] **任务 3.3：代码审查**
    - **目标**: 确保代码质量和架构一致性。
    - **步骤**:
        1.  提交所有代码改动。
        2.  发起一次代码审查 (Code Review)，邀请团队成员检查重构的合理性和实现质量。
    - **验证**: 代码审查通过并合并。
