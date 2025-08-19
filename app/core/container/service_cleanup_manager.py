"""
服务清理管理器 - 专门处理服务清理逻辑
"""

import logging
from typing import Dict, Any


class ServiceCleanupManager:
    """服务清理管理器 - 从ApplicationBootstrap.cleanup_services()迁移而来"""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    def cleanup_all_services(self, services: Dict[str, Any]) -> None:
        """清理所有服务"""
        self._logger.info("开始清理所有服务...")
        
        try:
            self.cleanup_analysis_services(services)
            self.cleanup_batch_services(services)
            self._logger.info("所有服务清理完成")
        except Exception as e:
            self._logger.error(f"服务清理过程中出错: {e}")
    
    def cleanup_analysis_services(self, services: Dict[str, Any]) -> None:
        """清理分析相关服务"""
        try:
            analysis_thread = services.get('analysis_thread')
            if analysis_thread and analysis_thread.isRunning():
                self._logger.debug("正在停止分析线程...")
                analysis_thread.quit()
                analysis_thread.wait()
                self._logger.debug("分析线程已停止")
        except Exception as e:
            self._logger.error(f"清理分析服务时出错: {e}")
    
    def cleanup_batch_services(self, services: Dict[str, Any]) -> None:
        """清理批处理相关服务"""
        try:
            batch_handler = services.get('batch_processing_handler')
            if batch_handler and hasattr(batch_handler, 'force_cleanup_all_jobs'):
                self._logger.debug("正在清理批处理作业...")
                batch_handler.force_cleanup_all_jobs()
                self._logger.debug("批处理作业清理完成")
        except Exception as e:
            self._logger.error(f"清理批处理服务时出错: {e}")