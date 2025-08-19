"""
批处理控制器模块 (重构版)

重构后的BatchProcessingHandler作为纯粹的协调器，将具体功能委托给专门的管理器。
"""
import os
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget

from .managers.batch_job_manager import JobManager
from .pools.pool_manager import PoolManager
from .managers.job_selection_manager import JobSelectionManager
from .managers.job_effects_manager import JobEffectsManager
from .managers.batch_execution_manager import ExecutionManager
from .batch_job_models import BatchJob, BatchJobStatus
from app.core.managers.state_manager import StateManager
from app.layers.business.processing.image_processor import ImageProcessor
from app.core.models.export_config import ExportConfig
from app.handlers.file_handler import FileHandler
from .interfaces.batch_processing_interface import BatchProcessingInterface

from .managers.batch_progress_manager import ProgressManager


class BatchProcessingHandler(BatchProcessingInterface):
    """
    批处理控制器 (重构版)
    
    作为批处理功能的协调器，将具体职责委托给专门的管理器：
    - BatchProgressManager: 进度管理
    
    本类只负责：
    - 管理器之间的协调
    - 主要信号的转发
    - 基本的作业和图像池操作委托
    """
    
    # 定义信号
    show_error_message = pyqtSignal(str)
    show_info_message = pyqtSignal(str)
    
    # 作业处理相关信号
    job_processing_started = pyqtSignal(str)   # job_id
    job_processing_finished = pyqtSignal(str, bool, str)  # job_id, success, message
    job_file_progress = pyqtSignal(str, str, int, int)  # job_id, file_name, current, total
    
    def __init__(self, job_manager: JobManager,
                state_manager: StateManager,
                file_handler: FileHandler,
                image_processor: ImageProcessor,
                config_service=None):
        """
        初始化批处理控制器
        
        Args:
            job_manager: 批处理作业管理器实例
            state_manager: 状态管理器实例
            file_handler: 文件处理器实例
            image_processor: 图像处理器实例
            config_service: 配置服务实例（可选）
        """
        super().__init__()
        
        # 核心依赖（外部注入）
        self.job_manager = job_manager
        self.state_manager = state_manager
        self.file_handler = file_handler
        self.image_processor = image_processor
        self.config_service = config_service
        
        # 创建核心管理器
        self.job_selection_manager = JobSelectionManager(self.job_manager)
        self.job_effects_manager = JobEffectsManager(self.job_manager, state_manager)
        self.pool_manager = PoolManager(self.job_manager, self.job_selection_manager, file_handler)
        self.job_execution_manager = ExecutionManager(self.job_manager, file_handler, image_processor)
        
        # 创建功能管理器（内部依赖）
        self.progress_manager = ProgressManager(self.job_execution_manager, self.job_manager, self)
        
        # 先导入需要的管理器类，然后创建实例
        from .managers.batch_config_manager import BatchExportConfigManager
        from .managers.batch_import_manager import BatchImportManager
        
        self.config_manager = BatchExportConfigManager(self.job_manager, self)
        self.import_manager = BatchImportManager(self.pool_manager, file_handler, self)
        
        # 连接信号
        self._connect_signals()
    
    def _connect_signals(self) -> None:
        """连接内部信号和槽"""
        # 连接作业执行管理器信号
        self.job_execution_manager.job_processing_started.connect(self.job_processing_started)
        self.job_execution_manager.job_processing_finished.connect(self.job_processing_finished)
        self.job_execution_manager.job_file_progress.connect(self.job_file_progress)
        self.job_execution_manager.processing_info.connect(self._on_processing_info)
        
        # 连接新管理器的信号
        self.job_selection_manager.selection_changed.connect(self._on_job_selection_changed)
        self.pool_manager.pool_changed.connect(self._on_pool_changed)
        self.pool_manager.images_added_to_job.connect(self._on_images_added_to_job)
        
        # 连接功能管理器信号
        self.progress_manager.show_info_message.connect(self.show_info_message)
        self.import_manager.show_error_message.connect(self.show_error_message)
    

    
    def _on_processing_info(self, job_id: str, info: str) -> None:
        """
        处理处理信息
        
        Args:
            job_id: 作业ID
            info: 信息
        """
        # 如果是系统消息，显示为信息消息
        if job_id == "system":
            self.show_info_message.emit(info)
    
    def _on_job_selection_changed(self, job_id: str) -> None:
        """
        处理作业选择变化
        
        Args:
            job_id: 新选中的作业ID
        """
        # 这里可以添加选择变化时的额外逻辑
        pass
    
    def _on_pool_changed(self) -> None:
        """处理图像池内容变化"""
        # 这里可以添加图像池变化时的额外逻辑
        pass
    
    def _on_images_added_to_job(self, job_id: str, count: int) -> None:
        """
        处理图像添加到作业的事件
        
        Args:
            job_id: 作业ID
            count: 添加的图像数量
        """
        pass
    # --- 作业管理方法 (委托给BatchJobManager) ---
    
    def add_job(self, name: str) -> Optional[BatchJob]:
        """
        添加新作业
        
        Args:
            name: 作业名称
            
        Returns:
            Optional[BatchJob]: 创建的作业，如果创建失败则返回None
        """
        # 检查名称是否已存在
        if self.job_manager.get_job_by_name(name) is not None:
            self.show_error_message.emit(f"作业名称 '{name}' 已存在。")
            return None
                
        job = self.job_manager.add_job(name)
        if job:
            # 自动选中新创建的作业
            self.job_selection_manager.handle_job_creation(job.job_id)
        
        return job
    
    def quick_create_jobs(self, count: int) -> List[BatchJob]:
        """
        快速创建多个作业
        
        Args:
            count: 要创建的作业数量
            
        Returns:
            List[BatchJob]: 创建的作业列表
        """
        created_jobs = []
        for i in range(1, count + 1):
            job_name = f"新建作业{i}"
            
            # 检查名称是否已存在，如果存在则添加后缀
            original_name = job_name
            suffix = 1
            while self.job_manager.get_job_by_name(job_name) is not None:
                job_name = f"{original_name}_{suffix}"
                suffix += 1
            
            job = self.job_manager.add_job(job_name)
            if job:
                created_jobs.append(job)
        
        # 自动选中第一个新创建的作业
        if created_jobs:
            self.job_selection_manager.handle_job_creation(created_jobs[0].job_id)
        
        return created_jobs
    
    def remove_job(self, job_id: str) -> bool:
        """
        删除作业
        
        Args:
            job_id: 作业ID
            
        Returns:
            bool: 是否成功删除
        """
        # 确保作业删除时的数据一致性
        self.ensure_data_consistency_on_job_deletion(job_id)
        
        # 删除作业
        return self.job_manager.remove_job(job_id)
    
    def rename_job(self, job_id: str, new_name: str) -> bool:
        """
        重命名作业
        
        Args:
            job_id: 作业ID
            new_name: 新名称
            
        Returns:
            bool: 是否成功重命名
        """
        # 检查新名称是否已存在
        if self.job_manager.get_job_by_name(new_name) is not None:
            self.show_error_message.emit(f"名为 '{new_name}' 的作业已存在。")
            return False
        
        return self.job_manager.rename_job(job_id, new_name)
    
    def get_all_jobs(self) -> List[BatchJob]:
        """
        获取所有作业的副本
        
        Returns:
            List[BatchJob]: 所有作业的列表
        """
        return self.job_manager.get_all_jobs()
    
    def get_job_selection_manager(self) -> 'JobSelectionManager':
        """
        获取作业选择管理器
        
        Returns:
            JobSelectionManager: 作业选择管理器实例
        """
        return self.job_selection_manager
    
            # --- 图像池管理方法 (委托给PoolManager) ---
            
    def add_images_to_pool(self, file_paths: List[str]) -> int:
        """
        向图像池添加图像
        
        Args:
            file_paths: 图像文件路径列表
            
        Returns:
            成功添加的图像数量
        """
        return self.pool_manager.add_images_to_pool(file_paths)
    
    def remove_from_pool(self, indices: List[int]) -> int:
        """
        从图像池中移除图像
        
        Args:
            indices: 要移除的索引列表
            
        Returns:
            int: 成功移除的图像数量
        """
        return self.pool_manager.remove_from_pool(indices)
    
    def clear_image_pool(self) -> int:
        """
        清空图像池
        
        Returns:
            int: 清除的图像数量
        """
        return self.pool_manager.clear_image_pool()
    
    def is_pool_empty(self) -> bool:
        """
        检查图像池是否为空
        
        Returns:
            bool: 如果图像池为空则返回True，否则返回False
        """
        return self.pool_manager.is_pool_empty()
    
    def get_pool_images(self) -> List[str]:
        """
        获取图像池中的所有图像路径
        
        Returns:
            List[str]: 图像路径列表
        """
        return self.pool_manager.get_pool_images()
    
    def get_pool_thumbnails(self):
        """
        获取图像池中的所有缩略图
        
        Returns:
            Dict[str, np.ndarray]: 文件路径到缩略图的映射
        """
        return self.pool_manager.get_pool_thumbnails()
    
    def add_pool_items_to_job(self, job_id: str, item_indices: List[int]) -> int:
        """
        将图像池中的项添加到作业
        
        Args:
            job_id: 目标作业ID
            item_indices: 图像池中项的索引列表
            
        Returns:
            int: 成功添加的项数量
        """
        count = self.pool_manager.add_pool_items_to_job(job_id, item_indices)
        
        # 如果成功添加了文件且作业有操作，将状态设置为待处理
        if count > 0:
            job = self.job_manager.get_job(job_id)
            if job and job.operations:
                self.job_manager.update_job_status(job_id, BatchJobStatus.PENDING, 0)
            
        return count
    
    def remove_items_from_job(self, job_id: str, item_indices: List[int]) -> int:
        """
        从作业中移除项
        
        Args:
            job_id: 目标作业ID
            item_indices: 作业中项的索引列表
            
        Returns:
            int: 成功移除的项数量
        """
        return self.job_manager.remove_sources_from_job(job_id, item_indices)
    
    def clear_job_items(self, job_id: str) -> int:
        """
        清空作业中的所有图像项目
        
        Args:
            job_id: 目标作业ID
            
        Returns:
            int: 清除的项目数量
        """
        return self.job_manager.clear_job_sources(job_id)
    
    # --- 作业选择管理方法 (委托给JobSelectionManager) ---
    
    def get_selected_job(self) -> Optional[BatchJob]:
        """
        获取当前选中的作业
        
        Returns:
            Optional[BatchJob]: 当前选中的作业，如果没有选中则返回None
        """
        return self.job_selection_manager.get_selected_job()
    
    def set_selected_job(self, job_id: str) -> bool:
        """
        设置选中的作业
        
        Args:
            job_id: 作业ID
            
        Returns:
            bool: 是否成功设置
        """
        return self.job_selection_manager.set_selected_job(job_id)
    
    def can_add_to_job(self) -> bool:
        """
        检查是否可以添加图像到作业
        
        Returns:
            bool: 如果图像池不为空且有选中的作业则返回True
        """
        return self.pool_manager.can_add_to_job()
    
    # --- 作业效果管理方法 (委托给JobEffectsManager) ---
    
    def apply_main_pipeline_to_job(self, job_id: str) -> int:
        """
        将当前主窗口的操作流水线应用到作业
        
        Args:
            job_id: 目标作业ID
            
        Returns:
            int: 操作数量
        """
        return self.job_effects_manager.apply_current_effects_to_job(job_id)
    
    def clear_job_effects(self, job_id: str) -> bool:
        """
        清除指定作业的所有效果
        
        Args:
            job_id: 目标作业ID
            
        Returns:
            bool: 是否成功清除
        """
        return self.job_effects_manager.clear_job_effects(job_id)
    
    def get_job_effects(self, job_id: str) -> List:
        """
        获取指定作业的效果列表
        
        Args:
            job_id: 作业ID
            
        Returns:
            List: 效果列表
        """
        return self.job_effects_manager.get_job_effects(job_id)
    
    # --- 导出配置管理 (委托给BatchExportConfigManager) ---
    
    def get_export_config(self) -> ExportConfig:
        """
        获取当前的导出配置
        
        Returns:
            ExportConfig: 导出配置
        """
        return self.config_manager.get_export_config()
    
    def update_export_config(self, config_updates: Dict) -> None:
        """
        更新导出配置
        
        Args:
            config_updates: 包含要更新的配置项的字典
        """
        self.config_manager.update_export_config(config_updates)
    
    # --- 作业处理方法 (委托给JobExecutionManager) ---
    
    def start_processing(self) -> bool:
        """
        开始处理所有待处理作业
        
        Returns:
            bool: 是否成功启动处理
        """
        return self.job_execution_manager.start_processing()
    
    def cancel_processing(self, job_id: str) -> None:
        """
        取消处理指定作业
        
        Args:
            job_id: 作业ID
        """
        self.job_execution_manager.cancel_processing(job_id)
    
    def cancel_all_processing(self) -> None:
        """取消所有正在处理的作业"""
        self.job_execution_manager.cancel_all_processing()
    
            # --- 文件夹导入 (委托给PoolManager) ---
    
    def import_folder(self, folder_path: str, recursive: bool = False, 
                     file_types: Optional[List[str]] = None) -> int:
        """
        导入文件夹中的图像到图像池
        
        Args:
            folder_path: 文件夹路径
            recursive: 是否递归搜索子文件夹
            file_types: 要导入的文件类型列表，如 [".jpg", ".png"]
            
        Returns:
            int: 成功导入的图像数量
        """
        return self.pool_manager.import_folder(folder_path, recursive, file_types)
    
    def show_import_folder_dialog(self, parent_widget: Optional[QWidget] = None) -> int:
        """
        显示文件夹选择对话框，并导入选中的文件夹中的图像到图像池
        
        Args:
            parent_widget: 父窗口部件
            
        Returns:
            int: 成功导入的图像数量
        """
        return self.pool_manager.show_import_folder_dialog(parent_widget)
    
    # --- 自动添加到作业 ---
    
    def add_all_pool_items_to_selected_job(self) -> Optional[BatchJob]:
        """
        将图像池中的所有图像添加到当前选中的作业
        
        Returns:
            Optional[BatchJob]: 成功操作的作业对象，如果没有选中作业或图像池为空则返回None
        """
        return self.pool_manager.add_all_pool_items_to_selected_job()
    
    # --- 带进度显示的批处理方法 (委托给BatchProgressManager) ---
    
    def start_processing_with_progress(self, parent_widget: Optional[QWidget] = None) -> bool:
        """
        启动带进度显示的批处理
        
        Args:
            parent_widget: 父窗口部件，用于进度对话框的父窗口
            
        Returns:
            bool: 是否成功启动处理
        """
        return self.progress_manager.start_processing_with_progress(parent_widget)
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """
        获取进度摘要信息
        
        Returns:
            Dict[str, Any]: 包含进度摘要的字典
        """
        return self.progress_manager.get_progress_summary()
    
    def is_processing_cancelled(self) -> bool:
        """
        检查批处理是否已被取消
        
        Returns:
            bool: 如果已取消返回True，否则返回False
        """
        return self.progress_manager.is_processing_cancelled()
    
    def get_active_jobs_count(self) -> int:
        """
        获取当前活跃作业数量
        
        Returns:
            int: 活跃作业数量
        """
        return len(self.job_execution_manager.workers)
    
    def force_cleanup_all_jobs(self) -> None:
        """
        强制清理所有作业资源（紧急情况使用）
        """
        # 强制取消所有作业
        self.job_execution_manager.cancel_all_processing()
        
        # 清理所有工作线程
        for job_id in list(self.job_execution_manager.worker_threads.keys()):
            self.job_execution_manager._cleanup_job_resources(job_id)
        
        # 清理状态
        self.job_execution_manager.cancelled_jobs.clear()
        self.job_execution_manager.is_cancelling_all = False
        
        # 重置进度状态
        self.progress_manager._reset_progress_state()
    

    
    def ensure_data_consistency_on_job_deletion(self, job_id: str) -> None:
        """
        确保作业删除时的数据一致性
        
        Args:
            job_id: 被删除的作业ID
        """
        # 清理作业效果
        self.job_effects_manager.cleanup_job_effects(job_id)
        
        # 处理选择状态
        self.job_selection_manager.handle_job_deletion(job_id)
    
    # === 新增接口方法实现 ===
    
    def get_job_by_name(self, job_name: str) -> Optional[BatchJob]:
        """
        根据名称获取作业
        
        Args:
            job_name: 作业名称
            
        Returns:
            作业对象，不存在返回None
        """
        return self.job_manager.get_job_by_name(job_name)
    
    def apply_preset_to_job(self, job_id: str, preset_operations: List[Dict]) -> bool:
        """
        将预设操作应用到指定作业
        
        Args:
            job_id: 作业ID
            preset_operations: 预设操作列表（从PresetModel.operations转换而来）
            
        Returns:
            是否应用成功
        """
        try:
            # 获取作业
            job = self.job_manager.get_job(job_id)
            if not job:
                self.show_error_message.emit(f"作业 {job_id} 不存在")
                return False
            
            # 清除现有效果
            self.job_effects_manager.clear_job_effects(job_id)
            
            # 将预设操作转换为ImageOperation对象列表
            from app.core.operations.registry import get_operation_class
            operations = []
            
            for operation_data in preset_operations:
                if 'operation_id' in operation_data and 'parameters' in operation_data:
                    operation_id = operation_data['operation_id']
                    parameters = operation_data['parameters']
                    
                    # 获取操作类并创建实例
                    operation_class = get_operation_class(operation_id)
                    if operation_class:
                        operation = operation_class()
                        # 设置操作参数
                        for param_name, param_value in parameters.items():
                            if hasattr(operation, param_name):
                                setattr(operation, param_name, param_value)
                        operations.append(operation)
                    else:
                        self.show_error_message.emit(f"未知的操作类型: {operation_id}")
                        return False
            
            # 设置作业的操作流水线
            if self.job_manager.set_job_operations(job_id, operations):
                # 更新作业状态为待处理
                from .batch_job_models import BatchJobStatus
                self.job_manager.update_job_status(job_id, BatchJobStatus.PENDING, 0)
                
                self.show_info_message.emit(
                    f"预设已成功应用到作业: {job.name} ({len(operations)} 个操作)")
                return True
            else:
                self.show_error_message.emit(f"设置作业操作失败: {job.name}")
                return False
            
        except Exception as e:
            self.show_error_message.emit(f"应用预设失败: {str(e)}")
            return False
    
    def apply_preset_to_jobs(self, job_ids: List[str], preset_operations: List[Dict]) -> Dict[str, bool]:
        """
        将预设操作应用到多个作业
        
        Args:
            job_ids: 作业ID列表
            preset_operations: 预设操作列表
            
        Returns:
            作业ID到成功状态的映射
        """
        results = {}
        success_count = 0
        
        for job_id in job_ids:
            success = self.apply_preset_to_job(job_id, preset_operations)
            results[job_id] = success
            if success:
                success_count += 1
        
        # 显示总体结果
        total_jobs = len(job_ids)
        if success_count == total_jobs:
            self.show_info_message.emit(f"预设已成功应用到所有 {total_jobs} 个作业")
        elif success_count > 0:
            self.show_info_message.emit(f"预设已应用到 {success_count}/{total_jobs} 个作业")
        else:
            self.show_error_message.emit("预设应用失败，没有作业被成功处理")
        
        return results
    
    # 路径管理方法
    def get_last_image_folder_path(self) -> Optional[str]:
        """获取上次使用的图像文件夹路径"""
        if self.config_service:
            try:
                config = self.config_service.get_config()
                return config.last_image_folder_path
            except Exception:
                pass
        return None
    
    def save_last_image_folder_path(self, path: str) -> None:
        """保存图像文件夹路径"""
        if self.config_service and path:
            try:
                self.config_service.update_config(last_image_folder_path=path)
            except Exception:
                pass