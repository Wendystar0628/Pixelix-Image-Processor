#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分析导出路径记忆功能验证脚本

此脚本验证数据分析导出对话框的路径记忆功能是否正常工作。
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from unittest.mock import Mock, MagicMock
from PyQt6.QtWidgets import QApplication
from app.core.configuration.config_data_transfer import ConfigDataTransferObject
from app.core.configuration.config_data_accessor import ConfigDataAccessor
from app.ui.dialogs.analysis_export_dialog import AnalysisExportDialog

# 初始化QApplication
app = None
if not QApplication.instance():
    app = QApplication(sys.argv)

def test_analysis_export_path_memory():
    """
    测试数据分析导出路径记忆功能
    """
    print("\n=== 数据分析导出路径记忆功能验证 ===")
    
    # 1. 创建配置数据对象，设置上次分析导出路径
    config_data = ConfigDataTransferObject()
    config_data.last_analysis_export_path = "C:/Users/Test/Documents/AnalysisExports"
    
    # 2. 创建配置访问器
    config_accessor = ConfigDataAccessor(config_data)
    
    # 3. 创建模拟的app_controller
    mock_app_controller = Mock()
    mock_config_service = Mock()
    mock_app_controller.get_config_service.return_value = mock_config_service
    
    # 4. 创建模拟的批处理协调器
    mock_batch_coordinator = Mock()
    mock_batch_coordinator.get_all_jobs.return_value = {
        "测试作业1": ["image1.jpg", "image2.jpg"],
        "测试作业2": ["image3.jpg", "image4.jpg"]
    }
    
    print("✓ 创建测试环境完成")
    
    try:
        # 5. 创建数据分析导出对话框
        dialog = AnalysisExportDialog(
            parent=None,
            batch_coordinator=mock_batch_coordinator,
            config_accessor=config_accessor,
            app_controller=mock_app_controller
        )
        
        print("✓ 数据分析导出对话框创建成功")
        
        # 6. 验证路径是否被正确加载
        expected_path = "C:/Users/Test/Documents/AnalysisExports"
        actual_path = dialog.path_edit.text()
        
        if actual_path == expected_path:
            print(f"✓ 路径记忆功能正常：{actual_path}")
        else:
            print(f"✗ 路径记忆功能异常：期望 {expected_path}，实际 {actual_path}")
            return False
        
        # 7. 模拟用户更改路径并保存
        new_path = "D:/NewAnalysisExports"
        dialog.path_edit.setText(new_path)
        
        # 8. 调用保存路径方法
        dialog._save_export_path(new_path)
        
        # 9. 验证配置服务的update_config方法是否被调用
        mock_config_service.update_config.assert_called_with(last_analysis_export_path=new_path)
        print(f"✓ 路径保存功能正常：{new_path}")
        
        print("\n=== 数据分析导出路径记忆功能验证通过 ===")
        return True
        
    except Exception as e:
        print(f"✗ 测试过程中发生错误：{e}")
        import traceback
        traceback.print_exc()
        return False

def test_analysis_export_path_memory_without_previous_path():
    """
    测试没有历史路径时的情况
    """
    print("\n=== 测试无历史路径情况 ===")
    
    # 1. 创建空的配置数据对象
    config_data = ConfigDataTransferObject()
    # 不设置 last_analysis_export_path
    
    # 2. 创建配置访问器
    config_accessor = ConfigDataAccessor(config_data)
    
    # 3. 创建模拟的app_controller
    mock_app_controller = Mock()
    mock_config_service = Mock()
    mock_app_controller.get_config_service.return_value = mock_config_service
    
    # 4. 创建模拟的批处理协调器
    mock_batch_coordinator = Mock()
    mock_batch_coordinator.get_all_jobs.return_value = {}
    
    try:
        # 5. 创建数据分析导出对话框
        dialog = AnalysisExportDialog(
            parent=None,
            batch_coordinator=mock_batch_coordinator,
            config_accessor=config_accessor,
            app_controller=mock_app_controller
        )
        
        # 6. 验证路径输入框为空（因为没有历史路径）
        actual_path = dialog.path_edit.text()
        if actual_path == "":
            print("✓ 无历史路径时路径输入框为空，符合预期")
        else:
            print(f"✗ 无历史路径时路径输入框应为空，实际为：{actual_path}")
            return False
        
        print("✓ 无历史路径情况测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 测试过程中发生错误：{e}")
        return False

def main():
    """
    主测试函数
    """
    print("数据分析导出路径记忆功能验证开始...")
    
    success = True
    
    # 测试有历史路径的情况
    if not test_analysis_export_path_memory():
        success = False
    
    # 测试无历史路径的情况
    if not test_analysis_export_path_memory_without_previous_path():
        success = False
    
    if success:
        print("\n🎉 所有测试通过！数据分析导出路径记忆功能工作正常。")
    else:
        print("\n❌ 部分测试失败，请检查实现。")
    
    return success

if __name__ == "__main__":
    main()