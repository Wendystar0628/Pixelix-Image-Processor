#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出路径记忆功能测试

测试AppConfig模型的导出路径记忆字段和相关对话框功能
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.models.app_config import AppConfig
from app.layers.infrastructure.configuration.config_manager import ConfigManager


def test_app_config_export_paths():
    """测试AppConfig的导出路径字段"""
    print("测试AppConfig导出路径字段...")
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        # 创建配置管理器
        config_manager = ConfigManager(Path(config_file).parent)
        
        # 获取配置
        config = config_manager.get_config()
        
        # 测试默认值
        assert hasattr(config, 'last_batch_export_path'), "缺少last_batch_export_path字段"
        assert hasattr(config, 'last_analysis_export_path'), "缺少last_analysis_export_path字段"
        
        print(f"默认批处理导出路径: {config.last_batch_export_path}")
        print(f"默认数据分析导出路径: {config.last_analysis_export_path}")
        
        # 测试设置路径
        test_batch_path = "/test/batch/export"
        test_analysis_path = "/test/analysis/export"
        
        config_manager.update_config(
            last_batch_export_path=test_batch_path,
            last_analysis_export_path=test_analysis_path
        )
        
        # 重新获取配置验证保存
        updated_config = config_manager.get_config()
        assert updated_config.last_batch_export_path == test_batch_path, "批处理导出路径保存失败"
        assert updated_config.last_analysis_export_path == test_analysis_path, "数据分析导出路径保存失败"
        
        print(f"更新后批处理导出路径: {updated_config.last_batch_export_path}")
        print(f"更新后数据分析导出路径: {updated_config.last_analysis_export_path}")
        
        print("✓ AppConfig导出路径字段测试通过")
        
    finally:
        # 清理临时文件
        if os.path.exists(config_file):
            os.unlink(config_file)


def test_dialog_imports():
    """测试对话框类的导入和基本功能"""
    print("\n测试对话框类导入...")
    
    try:
        # 测试导入ExportOptionsDialog
        from app.ui.dialogs.export_options_dialog import ExportOptionsDialog
        print("✓ ExportOptionsDialog导入成功")
        
        # 检查构造函数参数
        import inspect
        sig = inspect.signature(ExportOptionsDialog.__init__)
        params = list(sig.parameters.keys())
        assert 'config_service' in params, "ExportOptionsDialog缺少config_service参数"
        print("✓ ExportOptionsDialog包含config_service参数")
        
        # 测试导入AnalysisExportDialog
        from app.ui.dialogs.analysis_export_dialog import AnalysisExportDialog
        print("✓ AnalysisExportDialog导入成功")
        
        # 检查构造函数参数
        sig = inspect.signature(AnalysisExportDialog.__init__)
        params = list(sig.parameters.keys())
        assert 'config_accessor' in params, "AnalysisExportDialog缺少config_accessor参数"
        assert 'app_controller' in params, "AnalysisExportDialog缺少app_controller参数"
        print("✓ AnalysisExportDialog包含config_accessor和app_controller参数")
        
        print("✓ 对话框类导入测试通过")
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False
    except AssertionError as e:
        print(f"✗ 断言失败: {e}")
        return False
    
    return True


def test_config_service_integration():
    """测试配置服务集成"""
    print("\n测试配置服务集成...")
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        # 创建配置管理器
        config_manager = ConfigManager(Path(config_file).parent)
        
        # 模拟对话框保存路径
        test_paths = {
            'last_batch_export_path': 'C:/Users/Test/Documents/BatchExport',
            'last_analysis_export_path': 'C:/Users/Test/Documents/AnalysisExport'
        }
        
        # 更新配置
        config_manager.update_config(**test_paths)
        
        # 验证配置已保存
        config = config_manager.get_config()
        for key, expected_value in test_paths.items():
            actual_value = getattr(config, key)
            assert actual_value == expected_value, f"{key}保存失败: 期望{expected_value}, 实际{actual_value}"
        
        print("✓ 配置服务集成测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 配置服务集成测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(config_file):
            os.unlink(config_file)


def main():
    """运行所有测试"""
    print("开始导出路径记忆功能测试...\n")
    
    tests = [
        test_app_config_export_paths,
        test_dialog_imports,
        test_config_service_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            result = test_func()
            if result is not False:
                passed += 1
        except Exception as e:
            print(f"✗ 测试 {test_func.__name__} 失败: {e}")
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！导出路径记忆功能实现正确。")
        return True
    else:
        print("❌ 部分测试失败，请检查实现。")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)