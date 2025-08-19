"""
测试导出路径记忆功能
"""
import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TestExportPathMemory(unittest.TestCase):
    """测试导出路径记忆功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_path = os.path.join(self.temp_dir, "test_export")
        os.makedirs(self.test_path, exist_ok=True)
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_app_config_has_export_path_fields(self):
        """测试AppConfig是否包含导出路径字段"""
        from app.models.app_config import AppConfig
        
        config = AppConfig()
        
        # 检查是否有批处理导出路径字段
        self.assertTrue(hasattr(config, 'last_batch_export_path'),
                       "AppConfig应该包含last_batch_export_path字段")
        
        # 检查是否有分析导出路径字段
        self.assertTrue(hasattr(config, 'last_analysis_export_path'),
                       "AppConfig应该包含last_analysis_export_path字段")
    
    def test_config_data_accessor_has_export_path_methods(self):
        """测试ConfigDataAccessor是否包含导出路径相关方法"""
        from app.core.configuration.config_data_accessor import ConfigDataAccessor
        from app.core.configuration.config_data_transfer import ConfigDataTransferObject
        
        # 创建配置数据传输对象
        config_data = ConfigDataTransferObject()
        config_data.last_batch_export_path = ""
        config_data.last_analysis_export_path = ""
        
        accessor = ConfigDataAccessor(config_data)
        
        # 检查是否有获取批处理导出路径的方法
        self.assertTrue(hasattr(accessor, 'get_last_batch_export_path'),
                       "ConfigDataAccessor应该包含get_last_batch_export_path方法")
        
        # 检查是否有获取分析导出路径的方法
        self.assertTrue(hasattr(accessor, 'get_last_analysis_export_path'),
                       "ConfigDataAccessor应该包含get_last_analysis_export_path方法")
    
    def test_export_options_dialog_has_config_accessor_and_app_controller(self):
        """测试ExportOptionsDialog是否包含config_accessor和app_controller参数"""
        from app.ui.dialogs.export_options.export_options_dialog import ExportOptionsDialog
        import inspect
        
        # 获取构造函数签名
        sig = inspect.signature(ExportOptionsDialog.__init__)
        params = list(sig.parameters.keys())
        
        # 检查是否包含config_accessor和app_controller参数
        self.assertIn('config_accessor', params, 
                     "ExportOptionsDialog构造函数应该包含config_accessor参数")
        self.assertIn('app_controller', params, 
                     "ExportOptionsDialog构造函数应该包含app_controller参数")
    
    def test_analysis_export_dialog_has_config_accessor_and_app_controller(self):
        """测试AnalysisExportDialog是否包含config_accessor和app_controller参数"""
        from app.ui.dialogs.analysis_export_dialog import AnalysisExportDialog
        import inspect
        
        # 获取构造函数签名
        sig = inspect.signature(AnalysisExportDialog.__init__)
        params = list(sig.parameters.keys())
        
        # 检查是否包含config_accessor和app_controller参数
        self.assertIn('config_accessor', params, 
                     "AnalysisExportDialog构造函数应该包含config_accessor参数")
        self.assertIn('app_controller', params, 
                     "AnalysisExportDialog构造函数应该包含app_controller参数")
    
    def test_export_path_memory_functionality(self):
        """测试导出路径记忆功能的完整流程"""
        from app.core.configuration.config_data_accessor import ConfigDataAccessor
        from app.core.configuration.config_data_transfer import ConfigDataTransferObject
        
        # 创建配置数据传输对象
        config_data = ConfigDataTransferObject()
        config_data.last_batch_export_path = ""
        config_data.last_analysis_export_path = ""
        
        # 创建配置访问器
        accessor = ConfigDataAccessor(config_data)
        
        # 测试初始状态（应该为空）
        self.assertEqual(accessor.get_last_batch_export_path(), "")
        self.assertEqual(accessor.get_last_analysis_export_path(), "")
        
        # 模拟保存导出路径
        config_data.last_batch_export_path = self.test_path
        config_data.last_analysis_export_path = self.test_path
        
        # 测试路径是否被正确记忆
        self.assertEqual(accessor.get_last_batch_export_path(), self.test_path)
        self.assertEqual(accessor.get_last_analysis_export_path(), self.test_path)
    
    def test_config_data_accessor_methods_return_correct_values(self):
        """测试ConfigDataAccessor方法返回正确的值"""
        from app.core.configuration.config_data_accessor import ConfigDataAccessor
        from app.core.configuration.config_data_transfer import ConfigDataTransferObject
        
        # 创建配置数据传输对象
        config_data = ConfigDataTransferObject()
        config_data.last_batch_export_path = "/test/batch/path"
        config_data.last_analysis_export_path = "/test/analysis/path"
        
        accessor = ConfigDataAccessor(config_data)
        
        # 测试方法返回正确的值
        self.assertEqual(accessor.get_last_batch_export_path(), "/test/batch/path")
        self.assertEqual(accessor.get_last_analysis_export_path(), "/test/analysis/path")


if __name__ == '__main__':
    unittest.main()