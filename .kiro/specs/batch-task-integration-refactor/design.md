# 批处理任务系统整合重构设计文档

## 概述

本设计文档描述了如何将批处理功能整合到核心任务系统中，消除功能重合，简化架构。重构的核心思想是让批处理功能使用统一的任务协调器，而不是维护自己的线程管理系统。

## 架构设计

### 整合后的架构层次

```
批处理特性层 (app/features/batch_processing/)
├── BatchProcessingHandler (协调器，保持不变)
├── 管理器层 (managers/) - 保持现有功能
│   ├── JobManager (作业管理)
│   ├── PoolManager (图像池管理)  
│   ├── JobSelectionManager (作业选择)
│   └── JobEffectsManager (作业效果)
└── BatchProcessingWorker (保持QObject，移动到核心层)

核心任务层 (app/core/tasks/)
├── TaskCoordinator (任务协调器，保持不变)
├── TaskHandler接口 (保持不变)
├── 各种TaskHandler实现
└── BatchTaskHandler (新增：实现TaskHandler接口)
```

### 核心组件设计

#### 1. BatchTaskHandler (新增)

**职责：**
- 实现TaskHandler接口，处理批处理任务
- 将批处理作业转换为可执行的任务
- 管理BatchProcessingWorker的生命周期

**接口实现：**
```python
class BatchTaskHandler(BaseTaskHandler):
    handler_name = "batch_processing_handler"
    supported_task_types = ["batch_job_processing"]
    
    def _execute_task_internal(self, task_info: TaskInfo, 
                              progress_callback: Optional[Callable],
                              cancel_event: threading.Event) -> Any:
        # 创建BatchProcessingWorker实例
        # 连接信号到进度回调
        # 执行批处理逻辑
```

#### 2. BatchProcessingHandler (修改)

**保持职责：**
- 作业管理协调
- 图像池管理协调  
- UI信号转发

**移除职责：**
- 直接的线程管理
- ExecutionManager依赖

**新增职责：**
- 通过TaskCoordinator提交批处理任务
- 监听任务状态变化并转发信号

#### 3. BatchProcessingWorker (保持QObject)

**保持现状：**
- 继续使用QObject继承和pyqtSignal
- 保持现有的处理逻辑和接口
- 保持所有信号定义

**使用方式：**
- 在BatchTaskHandler中实例化
- 通过信号连接实现进度回调
- 通过cancel()方法实现任务取消

### 任务提交流程

```
用户点击"开始处理" 
    ↓
BatchProcessingHandler.start_processing()
    ↓
为每个待处理作业创建TaskInfo
    ↓
通过TaskCoordinator.submit_task()提交任务
    ↓
TaskCoordinator分配给BatchTaskHandler
    ↓
BatchTaskHandler创建BatchProcessingWorker实例
    ↓
BatchProcessingWorker执行批处理逻辑（保持QObject和信号）
    ↓
任务状态通过事件监听器回传给BatchProcessingHandler
```

### QObject使用策略

考虑到系统中广泛使用QObject进行信号槽通信，我们采用以下策略：

1. **保持BatchProcessingWorker的QObject特性**：
   - 继续使用QObject继承和pyqtSignal
   - 保持现有的信号接口不变
   - 在BatchTaskHandler中管理其生命周期

2. **在TaskHandler中桥接信号**：
   - BatchTaskHandler负责创建和管理BatchProcessingWorker
   - 将Worker的信号转换为TaskHandler的进度回调
   - 实现统一的任务取消机制

## 组件接口

### BatchTaskHandler接口

```python
class BatchTaskHandler(BaseTaskHandler):
    def __init__(self, file_handler: FileHandler, image_processor: ImageProcessor):
        super().__init__("batch_processing_handler", ["batch_job_processing"])
        self.file_handler = file_handler
        self.image_processor = image_processor
    
    def _execute_task_internal(self, task_info: TaskInfo, 
                              progress_callback: Optional[Callable],
                              cancel_event: threading.Event) -> Any:
        # 创建BatchProcessingWorker
        worker = BatchProcessingWorker()
        
        # 连接信号到回调
        worker.progress_updated.connect(
            lambda job_id, progress: progress_callback(progress) if progress_callback else None
        )
        
        # 执行任务
        config = task_info.get_metadata('config')
        worker.process_job(
            config['job_id'],
            config['source_paths'],
            config['operations'],
            config['export_config'],
            self.file_handler,
            self.image_processor
        )
```

### 任务配置格式

```python
task_config = {
    'job_id': str,
    'source_paths': List[str],
    'operations': List[ImageOperation],
    'export_config': ExportConfig
}
```

## 数据模型

### 任务信息扩展

批处理任务将使用TaskInfo的metadata字段存储批处理特定信息：

```python
task_info.add_metadata('batch_job_id', job_id)
task_info.add_metadata('source_count', len(source_paths))
task_info.add_metadata('operations_count', len(operations))
```

## 错误处理

### 任务失败处理

1. **任务级别失败：** 单个批处理作业失败时，通过TaskHandler的异常机制处理
2. **文件级别失败：** 作业中单个文件处理失败时，记录错误但继续处理其他文件
3. **系统级别失败：** TaskCoordinator级别的失败通过事件监听器传播

### 取消机制

1. **单作业取消：** 通过TaskCoordinator.cancel_task()实现
2. **全部取消：** 遍历活跃任务并逐个取消
3. **优雅关闭：** 等待当前文件处理完成后停止

## 测试策略

### 单元测试重点

1. **BatchTaskHandler功能测试：** 验证任务执行逻辑正确性
2. **任务提交流程测试：** 验证从BatchProcessingHandler到TaskCoordinator的任务流
3. **状态同步测试：** 验证任务状态正确回传到批处理界面

### 集成测试重点

1. **端到端批处理测试：** 从UI操作到任务完成的完整流程
2. **并发处理测试：** 多个批处理作业同时执行的场景
3. **取消和错误恢复测试：** 各种异常情况的处理

## 迁移策略

### 阶段性迁移

1. **第一阶段：** 创建BatchTaskHandler，保持现有ExecutionManager并行运行
2. **第二阶段：** 修改BatchProcessingHandler使用TaskCoordinator
3. **第三阶段：** 移除ExecutionManager和相关代码
4. **第四阶段：** 清理未使用的导入和依赖

### 向后兼容

- 保持BatchProcessingHandler的公共接口不变
- 保持所有信号的签名和行为不变
- 确保UI层无需修改