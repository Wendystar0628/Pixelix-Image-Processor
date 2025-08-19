"""
预设处理器模块

处理预设的保存、加载和应用等操作。
"""
import os
from typing import List, Optional, Dict

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QInputDialog, QMessageBox

from app.core.commands.base_command import BaseCommand
from app.core.commands.operation_commands import AddOperationCommand, ClearPipelineCommand
from app.core.operations.registry import get_operation_class
from app.core.managers.preset_manager import PresetManager
from app.core.models import PresetModel
from app.core.managers.state_manager import StateManager
from app.core.interfaces import StateManagerInterface
from app.features.batch_processing.interfaces import BatchProcessingInterface
from app.core.interfaces.preset_handler_interface import PresetHandlerInterface


class PresetHandler(PresetHandlerInterface):
    """
    预设处理器，负责处理预设的保存、加载和应用等操作。
    """
    
    # 信号
    show_error_message = pyqtSignal(str)
    show_info_message = pyqtSignal(str)
    preset_applied = pyqtSignal(str)  # 预设名称
    preset_saved = pyqtSignal(str)    # 预设名称
    preset_deleted = pyqtSignal(str)  # 预设名称
    
    def __init__(self, state_manager: StateManagerInterface, 
                 batch_processor: Optional[BatchProcessingInterface] = None):
        """
        初始化预设处理器。
        
        Args:
            state_manager: 状态管理器
            batch_processor: 批处理处理器（可选，用于批处理功能）
        """
        super().__init__()
        self.state_manager = state_manager
        self.batch_processor = batch_processor
        
        # 创建预设管理器
        self.preset_manager = PresetManager()
        
    def save_current_as_preset(self, parent_widget: QWidget) -> None:
        """
        将当前操作流水线保存为预设。
        
        Args:
            parent_widget: 父窗口部件
        """
        # 注意：此方法假设调用时已有图像加载，UI层负责确保这一前置条件。
            
        # 获取当前操作流水线
        pipeline = self.state_manager.get_pipeline()
        
        # 检查流水线是否为空
        if not pipeline:
            self.show_error_message.emit("当前没有应用任何操作，无法保存预设。")
            return
            
        # 弹出对话框，让用户输入预设名称
        preset_name, ok = QInputDialog.getText(
            parent_widget,
            "保存预设",
            "请输入预设名称:"
        )
        
        if not ok or not preset_name:
            return  # 用户取消或未输入名称
            
        # 序列化操作流水线
        operations = []
        for op in pipeline:
            operations.append(op.serialize())
            
        # 创建预设对象
        preset = PresetModel(name=preset_name, operations=operations)
        
        # 保存预设
        if self.preset_manager.save_preset(preset):
            self.preset_saved.emit(preset_name)
        else:
            self.show_error_message.emit(f"保存预设 '{preset_name}' 失败。")
    
    def delete_preset(self, parent_widget: QWidget) -> None:
        """
        删除指定的预设。
        
        Args:
            parent_widget: 父窗口部件
        """
        # 获取所有预设名称
        preset_names = self.preset_manager.get_all_presets()
        
        # 检查是否有可用的预设
        if not preset_names:
            self.show_error_message.emit("没有可用的预设。")
            return
            
        # 弹出对话框，让用户选择要删除的预设
        preset_name, ok = QInputDialog.getItem(
            parent_widget,
            "删除预设",
            "请选择要删除的预设:",
            preset_names,
            0,  # 默认选择第一项
            False  # 不可编辑
        )
        
        if not ok or not preset_name:
            return  # 用户取消或未选择
            
        # 确认删除
        reply = QMessageBox.question(
            parent_widget,
            "确认删除",
            f"确定要删除预设 '{preset_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return  # 用户取消
            
        # 删除预设
        if self.preset_manager.delete_preset(preset_name):
            self.preset_deleted.emit(preset_name)
        else:
            self.show_error_message.emit(f"删除预设 '{preset_name}' 失败。")
            
    def apply_preset_to_jobs(self, preset_name: str, apply_to_job1: bool, apply_to_job2: bool) -> None:
        """
        将预设应用到指定的作业。
        
        Args:
            preset_name: 预设名称
            apply_to_job1: 是否应用到作业1
            apply_to_job2: 是否应用到作业2
        """
        if not self.batch_processor:
            self.show_error_message.emit("批处理功能不可用，未注入批处理处理器。")
            return
            
        # 加载预设
        preset = self.preset_manager.load_preset(preset_name)
        if not preset:
            self.show_error_message.emit(f"加载预设 '{preset_name}' 失败。")
            return
        
        # 获取所有作业
        jobs = self.batch_processor.get_all_jobs()
        if not jobs:
            self.show_error_message.emit("没有可用的批处理作业。")
            return
        
        # 转换预设操作为字典格式
        preset_operations = []
        for operation in preset.operations:
            op_dict = {
                'operation_id': operation.operation_id,
                'parameters': operation.parameters
            }
            preset_operations.append(op_dict)
        
        # 应用到指定作业
        applied_count = 0
        job_ids_to_apply = []
        
        if apply_to_job1 and len(jobs) >= 1:
            job_ids_to_apply.append(jobs[0].job_id)
            
        if apply_to_job2 and len(jobs) >= 2:
            job_ids_to_apply.append(jobs[1].job_id)
        
        if not job_ids_to_apply:
            self.show_error_message.emit("没有选择要应用的作业。")
            return
        
        # 批量应用预设
        results = self.batch_processor.apply_preset_to_jobs(job_ids_to_apply, preset_operations)
        
        # 统计成功数量
        applied_count = sum(1 for success in results.values() if success)
        
        if applied_count > 0:
            self.preset_applied.emit(preset_name)
    
    def apply_preset_to_named_jobs(self, preset_name: str, job_names: List[str]) -> None:
        """
        将预设应用到指定名称的作业。
        
        Args:
            preset_name: 预设名称
            job_names: 作业名称列表
        """
        if not self.batch_processor:
            self.show_error_message.emit("批处理功能不可用，未注入批处理处理器。")
            return
            
        # 加载预设
        preset = self.preset_manager.load_preset(preset_name)
        if not preset:
            self.show_error_message.emit(f"加载预设 '{preset_name}' 失败。")
            return
        
        # 转换预设操作为字典格式
        preset_operations = []
        for operation in preset.operations:
            op_dict = {
                'operation_id': operation.operation_id,
                'parameters': operation.parameters
            }
            preset_operations.append(op_dict)
        
        # 根据作业名称查找作业ID
        job_ids_to_apply = []
        not_found_jobs = []
        
        for job_name in job_names:
            job = self.batch_processor.get_job_by_name(job_name)
            if job:
                job_ids_to_apply.append(job.job_id)
            else:
                not_found_jobs.append(job_name)
        
        # 如果有找不到的作业，显示警告
        if not_found_jobs:
            self.show_error_message.emit(f"未找到以下作业: {', '.join(not_found_jobs)}")
        
        # 如果没有可应用的作业，退出
        if not job_ids_to_apply:
            self.show_error_message.emit("没有找到可应用的作业。")
            return
        
        # 批量应用预设
        results = self.batch_processor.apply_preset_to_jobs(job_ids_to_apply, preset_operations)
        
        # 统计成功数量
        applied_count = sum(1 for success in results.values() if success)
        
        if applied_count > 0:
            self.preset_applied.emit(preset_name)
            
    def _apply_preset_to_current_job(self, preset: PresetModel) -> None:
        """
        将预设应用到当前作业。
        
        Args:
            preset: 预设对象
        """
        if not self.state_manager:
            self.show_error_message.emit("状态管理器未初始化。")
            return
            
        # 创建并执行清空流水线的命令
        clear_cmd = ClearPipelineCommand(self.state_manager.pipeline_manager)
        self.state_manager.pipeline_manager.execute_command(clear_cmd)
        
        # 遍历预设中的操作
        for op_dict in preset.operations:
            try:
                # 获取操作名称和参数
                op_name = op_dict.get("operation_name", "")
                if not op_name:
                    raise ValueError("操作名称为空")
                    
                op_params = op_dict.get("parameters", {})
                
                # 获取操作类
                op_class = get_operation_class(op_name)
                
                # 创建操作实例
                operation = op_class(**op_params)
                
                # 创建并执行添加操作的命令
                add_cmd = AddOperationCommand(operation, self.state_manager.pipeline_manager)
                self.state_manager.pipeline_manager.execute_command(add_cmd)
                
            except Exception as e:
                self.show_error_message.emit(f"应用操作失败: {e}")
                
    def get_all_preset_names(self) -> List[str]:
        """
        获取所有预设名称。
        
        Returns:
            List[str]: 预设名称列表
        """
        return self.preset_manager.get_all_presets()
    
    def load_preset(self, preset_name: str) -> bool:
        """
        加载预设（接口方法）
        
        Args:
            preset_name: 预设名称
            
        Returns:
            是否加载成功
        """
        try:
            # 加载预设
            preset = self.preset_manager.load_preset(preset_name)
            if not preset:
                self.show_error_message.emit(f"加载预设 '{preset_name}' 失败。")
                return False
            
            # 应用预设到当前作业
            self._apply_preset_to_current_job(preset)
            
            self.preset_applied.emit(preset_name)
            return True
            
        except Exception as e:
            self.show_error_message.emit(f"加载预设失败: {str(e)}")
            return False