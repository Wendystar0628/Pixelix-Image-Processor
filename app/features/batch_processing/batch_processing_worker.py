"""
批处理工作线程模块

该模块定义了BatchProcessingWorker类，它是一个无状态的工作线程，负责执行单个批处理作业。
它不管理作业队列或状态，只负责处理传递给它的单个作业，并通过信号报告进度和结果。
"""

import os
from typing import List, Dict, Optional, Any

import numpy as np
import cv2
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from .batch_job_models import BatchJob, BatchJobStatus
from app.layers.business.processing.image_processor import ImageProcessor
from app.core.operations.base_operation import ImageOperation
from app.handlers.file_handler import FileHandler
from app.core.models.export_config import ExportConfig, OutputDirectoryMode
from app.utils.image_utils import load_image_safely


class BatchProcessingWorker(QObject):
    """
    批处理工作线程类，负责执行单个批处理作业。
    
    这个类不管理作业状态或队列，它只接收一个作业及其相关数据，
    然后在单独的线程中执行处理过程，并通过信号报告进度和结果。
    """
    
    # 信号：作业进度更新
    progress_updated = pyqtSignal(str, int)  # job_id, percentage
    
    # 信号：作业完成
    job_finished = pyqtSignal(str, bool, str)  # job_id, success, message
    
    # 信号：单个文件处理进度
    file_progress = pyqtSignal(str, str, int, int)  # job_id, file_name, current, total
    
    # 信号：处理结果信息
    processing_info = pyqtSignal(str, str)  # job_id, info_message
    
    def __init__(self):
        """初始化批处理工作线程"""
        super().__init__()
        self._cancel_requested = False
    
    @pyqtSlot(str, str, list, list, ExportConfig, FileHandler, ImageProcessor)
    def process_job(self, job_id: str, job_name: str, source_paths: List[str], 
                   operations: List[ImageOperation],
                   export_config: ExportConfig, 
                   file_handler: FileHandler, 
                   image_processor: ImageProcessor):
        """
        处理单个批处理作业
        
        Args:
            job_id: 作业ID
            job_name: 作业名称（用于创建子文件夹）
            source_paths: 源文件路径列表
            operations: 操作流水线
            export_config: 导出配置
            file_handler: 文件处理器
            image_processor: 图像处理器
        """
        # 重置取消标志
        self._cancel_requested = False
        
        # 初始化处理结果
        success_count = 0
        failed_count = 0
        skipped_count = 0
        results = {}
        total_files = len(source_paths)
        
        # 发出初始进度信号
        self.progress_updated.emit(job_id, 0)
        
        # 处理每个文件
        for i, file_path in enumerate(source_paths):
            # 检查是否已请求取消
            if self._cancel_requested:
                self.processing_info.emit(job_id, f"处理已取消，已处理 {i}/{total_files} 个文件")
                # 发出取消完成信号
                self.job_finished.emit(job_id, False, f"用户取消，已处理 {i}/{total_files} 个文件")
                return
            
            # 更新文件进度
            file_name = os.path.basename(file_path)
            self.file_progress.emit(job_id, file_name, i + 1, total_files)
            
            try:
                # 加载图像
                image = load_image_safely(file_path)
                if image is None:
                    error_msg = f"图像加载失败: {file_name} - 文件可能损坏或格式不支持"
                    self.processing_info.emit(job_id, error_msg)
                    failed_count += 1
                    results[file_path] = False
                    continue
                
                # 应用操作流水线
                if operations:
                    processed_image = image_processor.render_pipeline(image, operations)
                    if processed_image is None:
                        error_msg = f"图像处理失败: {file_name} - 操作流水线执行出错"
                        self.processing_info.emit(job_id, error_msg)
                        failed_count += 1
                        results[file_path] = False
                        continue
                else:
                    # 没有操作，使用原始图像
                    processed_image = image
                
                # 构建输出路径
                try:
                    output_path = export_config.get_output_path(file_name, file_path, i, job_name)
                    
                except ValueError as e:
                    error_msg = f"输出路径配置错误: {str(e)}"
                    self.processing_info.emit(job_id, error_msg)
                    failed_count += 1
                    results[file_path] = False
                    continue
                except Exception as e:
                    error_msg = f"输出路径生成异常: {file_name} - {str(e)}"
                    self.processing_info.emit(job_id, error_msg)
                    failed_count += 1
                    results[file_path] = False
                    continue
                
                if output_path is None:  # 冲突解决策略返回None表示跳过
                    self.processing_info.emit(job_id, f"跳过已存在的文件: {file_name}")
                    skipped_count += 1
                    results[file_path] = "skipped"
                    continue
                    
                # 确保输出路径有效
                if not output_path:
                    error_msg = f"输出路径生成失败: {file_name} - 检查导出配置"
                    self.processing_info.emit(job_id, error_msg)
                    failed_count += 1
                    results[file_path] = False
                    continue
                    
                # 规范化输出路径
                output_path = os.path.normpath(output_path)
                
                # 确保输出目录存在
                output_dir = os.path.dirname(output_path)
                try:
                    if output_dir:  # 只有当目录非空时才创建
                        os.makedirs(output_dir, exist_ok=True)
                except Exception as e:
                    error_msg = f"创建输出目录失败: {output_dir} - {str(e)}"
                    self.processing_info.emit(job_id, error_msg)
                    failed_count += 1
                    results[file_path] = False
                    continue
                
                # 保存图像
                success = file_handler.save_image_headless(
                    processed_image, output_path, export_config)
                
                if success:
                    success_count += 1
                    results[output_path] = True
                    self.processing_info.emit(job_id, f"成功保存: {os.path.basename(output_path)}")
                    

                else:
                    failed_count += 1
                    results[output_path] = False
                    error_msg = f"文件保存失败: {os.path.basename(output_path)} - 检查磁盘空间和权限"
                    self.processing_info.emit(job_id, error_msg)
                
            except Exception as e:
                failed_count += 1
                results[file_path] = False
                error_msg = f"处理异常: {file_name} - {type(e).__name__}: {str(e)}"
                self.processing_info.emit(job_id, error_msg)
            
            # 更新总体进度
            progress_percentage = min(100, int((i + 1) * 100 / total_files))
            self.progress_updated.emit(job_id, progress_percentage)
            
        # 构建详细的结果消息
        if self._cancel_requested:
            result_message = f"作业已取消。已处理: {success_count + failed_count}/{total_files}, 成功: {success_count}, 失败: {failed_count}"
            overall_success = False
        else:
            result_message = (
                f"处理完成。总计: {total_files}, "
                f"成功: {success_count}, "
                f"失败: {failed_count}, "
                f"跳过: {skipped_count}"
            )
            
            # 添加成功率信息
            if total_files > 0:
                success_rate = (success_count / total_files) * 100
                result_message += f" (成功率: {success_rate:.1f}%)"
            
            # 判断作业是否成功
            overall_success = failed_count == 0 and not self._cancel_requested
        
        # 发出作业完成信号
        self.job_finished.emit(job_id, overall_success, result_message)
    

    
    def cancel(self):
        """请求取消当前处理任务"""
        self._cancel_requested = True