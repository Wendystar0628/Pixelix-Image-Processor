# 重构后代码清理实施计划

## 实施任务列表

- [ ] 1. 创建清理工具和脚本



  - 创建 `scripts/cleanup/` 目录结构
  - 实现文件分析器 (`file_analyzer.py`)
  - 实现清理执行器 (`cleanup_executor.py`)
  - 实现验证器 (`validator.py`)
  - 创建主清理脚本 (`cleanup_main.py`)
  - _需求: 7.1, 7.2_




- [ ] 2. 分析项目文件使用情况
  - 扫描所有 Python 文件构建导入依赖图
  - 识别未被任何文件导入的模块
  - 分析类和方法的使用情况
  - 生成详细的使用情况报告
  - 标记确定可以删除的文件
  - _需求: 1.1, 1.2, 3.1_

- [ ] 3. 创建项目备份
  - 创建完整项目备份到 `.cleanup_backup_[timestamp]` 目录
  - 验证备份的完整性
  - 记录备份位置和时间戳
  - 创建备份恢复脚本
  - _需求: 6.3, 7.3_

- [ ] 4. 删除确定的过时批处理文件
  - 删除 `app/core/batch_processor.py`
  - 删除 `app/workers/batch_processor_worker.py`
  - 删除 `app/handlers/batch_processing/batch_processing_handler.py`（如果已完全迁移）
  - 验证删除后应用仍能正常启动
  - _需求: 1.1, 3.3_

- [ ] 5. 删除过时的集成层文件
  - 删除 `app/core/integration/extensible_processor.py`
  - 删除 `app/core/integration/resource_manager.py`
  - 删除 `app/core/integration/task_coordinator.py`
  - 删除 `app/core/integration/performance_monitor.py`
  - 验证新的实现文件正常工作
  - _需求: 1.1, 3.3_

- [ ] 6. 删除过时的扩展文件
  - 删除 `app/core/integration/extensions/processor_extensions.py`
  - 删除 `app/core/integration/extensions/resource_providers.py`
  - 删除 `app/core/integration/extensions/task_handlers.py`
  - 验证新的扩展文件正常工作
  - _需求: 1.1, 3.3_

- [ ] 7. 评估和处理可能冗余的文件
  - 分析 `app/workers/analysis_export_worker.py` 的使用情况
  - 分析 `app/core/managers/batch_job_manager.py` 的使用情况
  - 分析 `app/core/managers/job_execution_manager.py` 的使用情况
  - 分析 `app/core/managers/image_pool_manager.py` 的使用情况
  - 根据分析结果决定是否删除
  - _需求: 1.2, 3.2_

- [ ] 8. 清理空目录


  - 删除空的 `app/core/integration/extensions/` 目录
  - 删除空的 `app/core/integration/` 目录（如果完全清空）
  - 删除空的 `app/workers/` 目录（如果完全清空）

  - 删除空的 `app/handlers/batch_processing/` 目录（如果完全清空）
  - 删除所有空的 `__pycache__` 目录
  - _需求: 4.1, 4.2, 4.5_

- [x] 9. 清理未使用的导入语句

  - 扫描所有 Python 文件查找未使用的导入
  - 自动移除未使用的导入语句
  - 修复因删除文件导致的导入错误
  - 优化导入语句的顺序和格式
  - 验证清理后代码仍能正常运行
  - _需求: 2.1, 2.2, 2.3_

- [ ] 10. 更新配置文件
  - 检查 `.gitignore` 文件，移除不再需要的忽略规则
  - 更新 IDE 配置文件中的模块路径
  - 更新测试配置文件中的路径引用
  - 更新文档中的模块路径引用
  - _需求: 5.1, 5.2, 5.4_

- [ ] 11. 修复循环导入问题
  - 使用静态分析工具检测循环导入
  - 重构代码消除发现的循环导入
  - 验证修复后的导入关系正确
  - 添加导入关系的文档说明
  - _需求: 2.4_

- [ ] 12. 清理测试文件
  - 删除针对已删除文件的测试用例
  - 更新测试文件中的导入路径
  - 修复因重构导致的测试失败
  - 添加针对新架构的测试用例
  - _需求: 6.2_

- [ ] 13. 运行完整性验证
  - 运行静态代码分析工具检查语法错误
  - 验证所有导入语句都能正确解析
  - 运行完整的测试套件
  - 验证应用能够正常启动和运行
  - 测试核心功能的完整性
  - _需求: 6.1, 6.4_

- [ ] 14. 性能和结构优化
  - 分析清理后的项目结构合理性
  - 优化模块间的依赖关系
  - 重组不合理的文件位置
  - 优化导入路径的长度和复杂度
  - 验证优化后的性能表现
  - _需求: 8.1, 8.2, 8.3_

- [ ] 15. 生成清理报告
  - 统计删除的文件数量和大小
  - 记录清理过程中的所有操作
  - 生成清理前后的对比报告
  - 创建清理结果的详细日志
  - 提供回滚操作的指导文档
  - _需求: 7.1, 7.2, 7.4_

- [ ] 16. 创建清理文档
  - 编写清理过程的详细文档
  - 创建新项目结构的说明文档
  - 更新开发者指南反映新架构
  - 创建故障排除指南
  - 记录清理过程中的经验教训
  - _需求: 7.1, 7.4_

- [ ] 17. 验证清理结果
  - 在干净环境中重新部署应用
  - 验证所有功能正常工作
  - 进行回归测试确保无功能丢失
  - 验证性能没有退化
  - 确认清理目标全部达成
  - _需求: 6.1, 6.3, 6.5_

- [ ] 18. 清理临时文件和缓存
  - 删除清理过程中产生的临时文件
  - 清理 Python 缓存文件 (*.pyc, __pycache__)
  - 清理 IDE 生成的临时文件
  - 清理日志文件和调试输出
  - 重置项目到最终清洁状态
  - _需求: 4.3, 4.4_

## 清理脚本示例

### 主清理脚本结构

```python
# scripts/cleanup/cleanup_main.py
def main():
    """主清理流程"""
    print("开始重构后代码清理...")
    
    # 1. 创建备份
    backup_path = create_backup()
    print(f"备份已创建: {backup_path}")
    
    # 2. 分析文件使用情况
    analyzer = FileAnalyzer(".")
    unused_files = analyzer.find_unused_files()
    dead_code = analyzer.find_dead_code()
    
    # 3. 用户确认
    if not confirm_cleanup(unused_files):
        print("清理已取消")
        return
    
    # 4. 执行清理
    executor = CleanupExecutor(analyzer)
    executor.remove_files(unused_files)
    executor.clean_imports()
    executor.remove_empty_directories()
    
    # 5. 验证结果
    validator = PostCleanupValidator(".")
    if not validator.validate_all():
        print("验证失败，建议回滚")
        return
    
    # 6. 生成报告
    generate_cleanup_report()
    print("清理完成！")

if __name__ == "__main__":
    main()
```

### 文件删除清单

```python
# 确定删除的文件列表
CONFIRMED_DELETE_FILES = [
    # 旧批处理文件
    "app/core/batch_processor.py",
    "app/workers/batch_processor_worker.py",
    
    # 旧集成层文件
    "app/core/integration/extensible_processor.py",
    "app/core/integration/resource_manager.py",
    "app/core/integration/task_coordinator.py",
    "app/core/integration/performance_monitor.py",
    
    # 旧扩展文件
    "app/core/integration/extensions/processor_extensions.py",
    "app/core/integration/extensions/resource_providers.py",
    "app/core/integration/extensions/task_handlers.py",
]

# 需要评估的文件列表
EVALUATE_FILES = [
    "app/workers/analysis_export_worker.py",
    "app/core/managers/batch_job_manager.py",
    "app/core/managers/job_execution_manager.py",
    "app/core/managers/image_pool_manager.py",
]

# 确定删除的目录列表（如果为空）
DIRECTORIES_TO_CLEAN = [
    "app/core/integration/extensions/",
    "app/core/integration/",
    "app/workers/",
    "app/handlers/batch_processing/",
]
```

这个实施计划提供了系统化的清理步骤，确保在移除旧代码的同时保持项目的完整性和功能性。