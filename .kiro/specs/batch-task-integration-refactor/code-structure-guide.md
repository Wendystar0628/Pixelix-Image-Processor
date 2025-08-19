# 批处理任务系统整合重构代码文件规范指导

## 修改前后的代码文件结构对比

### 修改前的文件结构
```
app/features/batch_processing/
├── batch_coordinator.py (BatchProcessingHandler)
├── batch_processing_worker.py (BatchProcessingWorker - QObject)
├── managers/
│   ├── batch_execution_manager.py (ExecutionManager - 将被删除)
│   ├── batch_job_manager.py (JobManager - 保持不变)
│   ├── pool_manager.py (PoolManager - 保持不变)
│   ├── job_selection_manager.py (JobSelectionManager - 保持不变)
│   └── job_effects_manager.py (JobEffectsManager - 保持不变)

app/core/tasks/
├── coordinator.py (TaskCoordinator - 保持不变)
├── interfaces.py (TaskHandler等接口 - 保持不变)
└── handlers.py (BaseTaskHandler等 - 保持不变)
```

### 修改后的文件结构
```
app/features/batch_processing/
├── batch_coordinator.py (BatchProcessingHandler - 修改)
├── batch_processing_worker.py (BatchProcessingWorker - 保持不变)
├── managers/
│   ├── batch_job_manager.py (JobManager - 保持不变)
│   ├── pool_manager.py (PoolManager - 保持不变)
│   ├── job_selection_manager.py (JobSelectionManager - 保持不变)
│   └── job_effects_manager.py (JobEffectsManager - 保持不变)

app/core/tasks/
├── coordinator.py (TaskCoordinator - 保持不变)
├── interfaces.py (TaskHandler等接口 - 保持不变)
├── handlers.py (BaseTaskHandler等 - 保持不变)
└── batch_task_handler.py (BatchTaskHandler - 新增)
```

## 新增和修改的代码文件职责说明

### 新增文件

#### app/core/tasks/batch_task_handler.py
- **职责：** 实现TaskHandler接口，专门处理批处理任务
- **核心功能：** 将批处理作业转换为可执行任务，管理BatchProcessingWorker生命周期
- **依赖：** BaseTaskHandler, FileHandler, ImageProcessor, BatchProcessingWorker

### 修改文件

#### app/features/batch_processing/batch_coordinator.py (BatchProcessingHandler)
- **移除职责：** 直接的线程管理，ExecutionManager依赖
- **新增职责：** 通过TaskCoordinator提交任务，实现TaskEventListener接口
- **保持职责：** 作业管理协调，图像池管理协调，UI信号转发

#### app/features/batch_processing/batch_processing_worker.py (BatchProcessingWorker)
- **保持职责：** QObject继承，所有pyqtSignal定义，完整的处理逻辑
- **保持接口：** 所有现有方法和信号保持不变
- **使用方式：** 在BatchTaskHandler中实例化和管理

#### app/core/dependency_injection/service_builder.py
- **移除：** ExecutionManager的创建和注入逻辑
- **新增：** BatchTaskHandler的注册到TaskCoordinator

### 删除文件

#### app/features/batch_processing/managers/batch_execution_manager.py
- **原职责：** 管理批处理作业执行，协调工作线程，处理作业状态更新
- **删除原因：** 功能完全由TaskCoordinator和BatchTaskHandler替代

## 代码清理指导

### 清理步骤

1. **删除ExecutionManager相关代码**
   - 从BatchProcessingHandler.__init__中移除ExecutionManager实例化
   - 删除所有ExecutionManager方法调用
   - 移除ExecutionManager相关的信号连接

2. **保持BatchProcessingWorker不变**
   - 保留所有pyqtSignal定义
   - 保持QObject继承
   - 保持所有现有方法和接口
   - 确保可以在BatchTaskHandler中正确使用

3. **更新导入语句**
   - 移除对batch_execution_manager的导入
   - 添加对TaskCoordinator和相关接口的导入
   - 保持对BatchProcessingWorker的导入

4. **清理依赖注入**
   - 从ServiceBuilder中移除ExecutionManager相关配置
   - 确保BatchProcessingHandler不再接收ExecutionManager参数
   - 添加BatchTaskHandler的注册到TaskCoordinator

### QObject处理策略

由于系统中广泛使用QObject进行信号槽通信，我们采用以下策略：

1. **保持现有QObject使用**
   - BatchProcessingWorker继续使用QObject和pyqtSignal
   - 所有现有信号接口保持不变
   - 在BatchTaskHandler中通过信号连接实现通信

2. **信号桥接**
   - BatchTaskHandler负责连接Worker信号到TaskHandler回调
   - 实现信号到进度回调的转换
   - 保持取消机制的一致性

### 避免的常见问题

1. **不要在单一文件中混合职责**
   - BatchTaskHandler只负责任务执行，不处理UI逻辑
   - BatchProcessingHandler只负责协调，不直接执行任务

2. **保持接口一致性**
   - 确保BatchProcessingHandler的公共方法签名不变
   - 保持所有信号的参数和行为一致

3. **避免循环依赖**
   - BatchTaskHandler不应该直接依赖BatchProcessingHandler
   - 通过事件监听器实现松耦合通信

4. **正确处理QObject生命周期**
   - 确保BatchProcessingWorker在TaskHandler中正确创建和销毁
   - 避免信号连接泄漏

## 测试验证要点

1. **功能完整性验证**
   - 所有批处理功能应该正常工作
   - UI响应和进度显示应该正确

2. **信号机制验证**
   - 所有信号应该正确发射和接收
   - 进度更新应该及时准确

3. **性能验证**
   - 批处理性能不应该下降
   - 内存使用应该更加高效

4. **代码质量验证**
   - 没有未使用的导入
   - 没有死代码或注释掉的代码
   - 所有新代码都有适当的文档注释