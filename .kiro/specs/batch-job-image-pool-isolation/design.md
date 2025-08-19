# 设计文档

## 概述

本设计旨在重构图像池和批处理作业的架构，将图像池从作业系统中分离出来，使其成为独立的存储组件，同时优化作业管理的一致性和用户体验。

## 架构

### 核心设计原则

1. **职责分离**: 图像池只负责文件IO和图像存储，不参与作业管理
2. **数据一致性**: 作业删除时自动清理相关数据
3. **用户体验**: 确保界面状态的一致性和可预测性
4. **最小化修改**: 在现有架构基础上进行最小化改动

### 架构变更

```
当前架构:
ImagePoolManager -> 创建"图像池"作业 -> 出现在作业列表中

新架构:
ImagePoolManager -> 独立存储组件 -> 不出现在作业列表中
```

## 组件和接口

### 1. 图像池存储组件 (ImagePoolStorage)

**职责:**
- 管理图像文件的存储和检索
- 提供图像的缩略图生成和缓存
- 处理图像的添加、删除、清空操作

**接口:**
```python
class ImagePoolStorage:
    def add_images(self, file_paths: List[str]) -> int
    def remove_images(self, indices: List[int]) -> int
    def clear_images(self) -> int
    def get_all_images(self) -> List[str]
    def get_image_count(self) -> int
    def is_empty(self) -> bool
    def get_thumbnail(self, file_path: str) -> Optional[np.ndarray]
```

### 2. 作业选择管理器 (JobSelectionManager)

**职责:**
- 管理当前选中的作业状态
- 确保作业列表中始终有选中项（如果存在作业）
- 处理作业删除时的选择逻辑

**接口:**
```python
class JobSelectionManager:
    def set_selected_job(self, job_id: str) -> bool
    def get_selected_job(self) -> Optional[BatchJob]
    def handle_job_deletion(self, deleted_job_id: str) -> Optional[str]
    def ensure_selection_consistency(self) -> None
```

### 3. 作业效果管理器 (JobEffectsManager)

**职责:**
- 管理每个作业的独立效果配置
- 提供效果的应用、清除、隔离功能
- 处理作业删除时的效果清理

**接口:**
```python
class JobEffectsManager:
    def apply_current_effects_to_job(self, job_id: str) -> int
    def clear_job_effects(self, job_id: str) -> bool
    def get_job_effects(self, job_id: str) -> List[ImageOperation]
    def cleanup_job_effects(self, job_id: str) -> None
```

### 4. 重构的图像池管理器 (RefactoredPoolManager)

**职责:**
- 协调图像池存储和作业系统的交互
- 处理"一键添加到作业"的逻辑
- 不再创建或管理"图像池"作业

## 数据模型

### 图像池数据结构

```python
@dataclass
class ImagePoolData:
    images: List[str] = field(default_factory=list)
    thumbnails: Dict[str, np.ndarray] = field(default_factory=dict)
    
    def add_image(self, file_path: str) -> bool
    def remove_image(self, index: int) -> bool
    def clear(self) -> None
```

### 作业选择状态

```python
@dataclass
class JobSelectionState:
    selected_job_id: Optional[str] = None
    last_selected_job_id: Optional[str] = None
    
    def update_selection(self, job_id: Optional[str]) -> None
    def get_fallback_selection(self, available_jobs: List[BatchJob]) -> Optional[str]
```

## 错误处理

### 图像池操作错误
- 文件不存在或无法访问时的处理
- 缩略图生成失败的降级处理
- 内存不足时的优雅处理

### 作业选择错误
- 选中的作业被删除时的自动切换
- 作业列表为空时的状态处理
- 并发操作时的状态一致性保护

### 效果管理错误
- 效果应用失败时的回滚机制
- 无效效果配置的过滤处理
- 作业删除时的资源清理保证

## 旧代码清理策略

### 需要删除的旧逻辑
1. **图像池作业创建逻辑**: 移除所有在PoolManager中创建"图像池"作业的代码
2. **硬编码的作业ID**: 清除所有对"image_pool"作业ID的直接引用
3. **作业列表过滤逻辑**: 移除JobListPanel中过滤图像池作业的临时代码
4. **旧的图像池管理器**: 直接删除原有的image_pool_manager.py文件

### 清理验证
- 确保没有代码路径会创建名为"图像池"的作业
- 验证图像池操作完全独立于作业系统
- 检查所有相关的import语句和依赖关系

## 测试策略

### 单元测试重点
1. 图像池存储组件的基本操作
2. 作业选择管理器的状态转换
3. 效果管理器的隔离性验证
4. 旧代码路径的完全移除验证

### 集成测试重点
1. 图像池与作业系统的交互
2. 作业删除时的数据一致性
3. 用户界面状态的同步性
4. 重构后系统的完整性验证

### 用户场景测试
1. 图像池不出现在作业列表的验证
2. "一键添加到作业"的完整流程
3. 作业删除后的界面状态恢复
4. 旧功能路径的不可访问性验证