# 批处理协调器迁移与整合重构需求文档 (v1.1)

## 1. 背景与目标

随着核心业务逻辑向 `app/features/batch_processing` 模块的成功迁移，旧的协调层代码（位于 `app/handlers/batch_processing`）已成为技术债务，其存在破坏了新架构的统一性和内聚性。

本次重构的核心目标是**彻底消除**旧的批处理协调层，将其职责完全、合理地整合进新的 `app/features/batch_processing` 模块中，完成批处理功能内聚的“最后一公里”，从而实现架构的完整性和代码的整洁性。

## 2. 功能性需求

### 需求 1：保持现有批处理功能完整性
- **用户故事**: 作为用户，在重构完成后，我希望所有批处理功能（包括从文件/文件夹导入图像、将图像添加到作业、应用效果、配置导出选项、启动/取消处理、查看进度）的使用体验和功能与重构前完全一致。
- **验收标准**:
    - 1.1 **WHEN** 用户执行任何批处理相关的UI操作 **THEN** 系统应能正确响应，其功能表现与重构前无任何差异。
    - 1.2 **WHEN** 批处理任务执行 **THEN** 其输出结果（处理后的图像）必须与重构前完全一致。

### 需求 2：将协调层职责内聚到功能模块
- **用户故事**: 作为开发者，我希望所有与批处理功能相关的协调和管理逻辑都封装在 `app/features/batch_processing` 模块内部，而不是分散在 `handlers` 目录中。
- **验收标准**:
    - 2.1 **WHEN** 查看代码结构 **THEN** `app/handlers/` 目录下**不得**再有 `batch_processing` 相关的子目录或文件。
    - 2.2 **WHEN** `BatchProcessingController` 调用批处理功能 **THEN** 它**必须**直接与 `app/features/batch_processing/handler.py` 交互，而不是旧的 `handler`。

### 需求 3：优化模块接口清晰度
- **用户故事**: 作为开发者，我希望 `app/features/batch_processing` 模块对外暴露一个单一、清晰的入口点 (`handler.py`)，所有外部调用（如 `Controller`）都通过这个入口进行。
- **验收标准**:
    - 3.1 **WHEN** `BatchProcessingController` 需要与批处理功能交互 **THEN** 它只应 `import` `app.features.batch_processing.handler`，而不应 `import` 任何批处理模块内部的管理器（`managers`）。
    - 3.2 **WHEN** 应用启动 **THEN** `AppContext` (或同等依赖注入容器) **只应**直接实例化 `BatchProcessingHandler`，而不应实例化任何其内部的管理器。

## 3. 非功能性需求

### 需求 4：提升代码可维护性
- **目标**: 消除代码冗余和不一致的架构模式，降低未来维护成本。
- **验收标准**:
    - 4.1 **GIVEN** 一位新加入的开发者 **WHEN** 他需要理解批处理功能 **THEN** 他只需聚焦于 `app/features/batch_processing` 这一个目录即可。
    - 4.2 **WHEN** 运行静态代码分析 **THEN** 项目中不应存在因本次重构导致的任何死代码（unreachable code）或冗余导入。

### 需求 5：确保架构一致性与健壮性
- **目标**: 使批处理功能的实现完全符合项目“按功能组织”的架构理念，并确保事件通信的完整性。
- **验收标准**:
    - 5.1 **WHEN** 审视项目结构 **THEN** `app/features/batch_processing/` 目录应包含处理该功能所需的所有非UI后端逻辑（`handler`, `managers`, `worker`, `models`）。
    - 5.2 **WHEN** 重构完成 **THEN** 所有之前由旧 `handler` 负责协调的信号/槽连接必须被完整保留和正确迁移，确保UI与业务逻辑的事件通信链路完好无损。

## 4. 约束与限制
- 本次重构**不涉及**任何UI层 (`app/ui`) 文件的功能性改动，仅修改其导入路径以适应新的 `handler` 位置。
- 本次重构**不新增**任何面向用户的功能。
- 所有文件和类的重命名与移动，**必须**遵循项目既定的命名规范（`snake_case` for files, `PascalCase` for classes）。
