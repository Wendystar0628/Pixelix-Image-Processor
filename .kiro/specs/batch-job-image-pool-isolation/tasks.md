# 实现计划

- [x] 1. 创建图像池存储组件



  - 实现独立的ImagePoolStorage类，负责图像文件的存储和管理
  - 提供图像添加、删除、清空的基本操作接口
  - 实现缩略图生成和缓存功能
  - _需求: 1.1, 1.3_



- [ ] 2. 创建作业选择管理器
  - 实现JobSelectionManager类，管理当前选中的作业状态
  - 确保作业列表中始终有选中项（如果存在作业）
  - 处理作业删除时的自动选择逻辑


  - _需求: 2.1, 2.2, 2.3_

- [ ] 3. 创建作业效果管理器
  - 实现JobEffectsManager类，管理每个作业的独立效果配置
  - 提供从StateManager获取当前效果并应用到作业的功能


  - 实现清除作业效果的功能
  - 处理作业删除时的效果清理
  - _需求: 3.1, 3.2, 3.3, 3.4_

- [-] 4. 重构图像池管理器

  - 创建新的pool_manager_refactored.py文件
  - 集成ImagePoolStorage组件，移除所有图像池作业创建逻辑
  - 重构"一键添加到作业"功能，确保只在有选中作业时才能使用
  - 完全删除app/features/batch_processing/managers/image_pool_manager.py文件
  - _需求: 1.1, 1.2, 4.1, 4.2, 4.3_

- [x] 5. 更新批处理协调器

  - 修改BatchProcessingHandler，集成新的管理器组件
  - 删除以下代码：`from .managers.image_pool_manager import PoolManager`
  - 删除以下代码：`self.image_pool_manager = PoolManager(...)`
  - 删除以下代码：`get_pool_job()`方法中依赖图像池作业的逻辑
  - 删除所有调用旧image_pool_manager的代码（约50-80行）
  - 更新作业管理方法，确保新建作业时自动选中
  - 实现作业删除时的数据一致性清理
  - _需求: 2.1, 5.1, 5.2, 5.3_



- [ ] 6. 更新作业列表面板
  - 修改JobListPanel，删除以下过滤代码：
    - `if job.name != "__IMAGE_POOL__":` 过滤逻辑
    - `if job.name != "图像池":` 过滤逻辑
    - 任何硬编码的图像池作业名称检查（约20-30行代码）
  - 集成JobSelectionManager，确保选择状态的一致性
  - 添加"清除当前作业效果"按钮和功能


  - _需求: 1.1, 1.2, 2.2, 3.3_

- [ ] 7. 更新图像池面板
  - 修改ImagePoolPanel，删除以下依赖图像池作业的代码：
    - 依赖图像池作业的显示逻辑
    - `handler.get_pool_job()`调用中依赖作业的部分
    - 通过作业系统管理图像池的代码
    - 图像池作业相关的UI更新逻辑（约40-60行代码）
  - 使用新的ImagePoolStorage组件


  - 更新"一键添加到作业"按钮的启用逻辑
  - 确保图像池操作不依赖作业系统
  - _需求: 1.3, 4.2, 4.3_

- [ ] 8. 更新批处理主面板
  - 修改BatchProcessingPanel，删除以下图像池作业相关代码：
    - 与图像池作业相关的信号连接
    - 图像池作业状态检查的代码
    - 依赖图像池作业存在的逻辑


    - 图像池作业相关的事件处理方法（约30-50行代码）
  - 协调新的组件交互
  - 确保界面状态的同步和一致性
  - 处理组件间的信号连接


  - _需求: 2.2, 2.3, 5.1, 5.2_

- [ ] 9. 添加数据一致性检查
  - 实现系统启动时的孤立数据清理功能
  - 添加作业删除时的完整性验证
  - 确保图像池和作业系统的数据隔离
  - _需求: 5.3, 1.1_



- [ ] 10. 清理旧的图像池作业逻辑
  - 完全删除app/features/batch_processing/managers/image_pool_manager.py文件（约200-300行代码）
  - 删除以下具体代码模式：
    - `self._pool_job_id = "image_pool"` 硬编码引用
    - `self._ensure_pool_job()` 方法
    - `BatchJob(job_id=self._pool_job_id, name="图像池")` 创建逻辑
    - `PoolManager` 类的完整实现
  - 验证所有文件中不再存在对"image_pool"作业ID的引用
  - _需求: 6.1, 6.2, 6.3, 6.4_

- [ ] 11. 更新所有相关的import语句和清理验证
  - 删除以下import语句：
    - `from .managers.image_pool_manager import PoolManager`
    - `from app.features.batch_processing.managers.image_pool_manager import PoolManager`
  - 更新BatchProcessingHandler中的组件引用，使用新的管理器
  - 确保所有UI面板使用新的组件接口
  - 清理未使用的import和依赖
  - 验证代码中不存在任何对已删除类和方法的引用
  - 运行代码检查，确保没有导入错误
  - _需求: 6.2, 6.3_

- [-] 12. 编写核心功能测试和删除验证

  - 测试图像池存储组件的基本操作
  - 测试作业选择管理器的状态转换
  - 测试作业效果管理器的隔离性
  - 验证"一键添加到作业"的完整流程
  - 验证旧代码路径的完全移除：
    - 确认图像池不会出现在作业列表中
    - 确认删除image_pool_manager.py后系统正常运行
    - 确认所有硬编码的"image_pool"引用已清除
    - 验证总计删除了340-520行旧代码
  - 进行回归测试，确保重构后功能完整
  - _需求: 1.1, 2.1, 3.1, 4.1, 6.4_