# Requirements Document

## Introduction

简化图像池和主视窗的加载逻辑，建立清晰的单向数据流。图像池作为唯一的文件IO入口，主视图作为唯一的作业效果参考标准。消除当前混乱的双向导入机制，确保数据流向清晰且易于维护。

## Requirements

### Requirement 1

**User Story:** 作为用户，我希望只能通过图像池添加新图像，这样我就能有一个统一的文件管理入口。

#### Acceptance Criteria

1. WHEN 用户需要添加图像时 THEN 系统 SHALL 只允许通过图像池进行添加
2. WHEN 用户双击主视窗时 THEN 系统 SHALL NOT 触发图像添加功能
3. WHEN 用户使用工具栏添加图像时 THEN 系统 SHALL 将操作重定向到图像池

### Requirement 2

**User Story:** 作为用户，我希望从图像池选择图像加载到主视图，这样我就能清楚地控制当前的工作对象。

#### Acceptance Criteria

1. WHEN 用户在图像池中选择图像时 THEN 系统 SHALL 提供加载到主视图的选项
2. WHEN 图像加载到主视图时 THEN 系统 SHALL 将其设置为当前作业对象
3. WHEN 图像池中添加新图像时 THEN 系统 SHALL NOT 自动加载到主视图

### Requirement 3

**User Story:** 作为用户，我希望主视图只作为作业效果的参考标准，这样我就能专注于当前处理的图像效果。

#### Acceptance Criteria

1. WHEN 主视图显示图像时 THEN 系统 SHALL 将其作为所有作业效果的参考标准
2. WHEN 进行图像处理操作时 THEN 系统 SHALL 以主视图中的图像为基准
3. WHEN 主视图为空时 THEN 系统 SHALL 禁用所有图像处理功能

### Requirement 4

**User Story:** 作为用户，我希望图像池只作为存储单元，这样我就能有一个纯粹的文件管理界面。

#### Acceptance Criteria

1. WHEN 图像池显示图像时 THEN 系统 SHALL NOT 将其作为作业对象
2. WHEN 用户在图像池中操作时 THEN 系统 SHALL 只提供文件管理功能
3. WHEN 图像池中的图像被删除时 THEN 系统 SHALL NOT 影响主视图中的图像（除非是同一张图像）

### Requirement 5

**User Story:** 作为开发者，我希望删除所有旧的双向导入代码，这样系统就能保持代码整洁和逻辑清晰。

#### Acceptance Criteria

1. WHEN 实现新逻辑后 THEN 系统 SHALL 删除所有未使用的自动加载相关方法
2. WHEN 移除旧功能后 THEN 系统 SHALL 删除相关的信号连接和事件处理器
3. WHEN 清理代码后 THEN 系统 SHALL 确保没有死代码或未使用的导入