#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试数据分析导出路径记忆功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.models.app_config import AppConfig
from app.layers.infrastructure.configuration.config_manager import ConfigManager
from app.core.configuration.config_data_accessor import ConfigDataAccessor
from app.core.configuration.config_data_transfer import ConfigDataTransferObject
from app.layers.infrastructure.configuration.config_service import ConfigService
from app.handlers.app_controller import AppController

def test_config_chain():
    """测试配置链路"""
    print("=== 测试配置链路 ===")
    
    # 1. 创建临时配置目录
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    print(f"临时配置目录: {temp_dir}")
    
    try:
        # 2. 创建ConfigManager
        config_manager = ConfigManager(temp_dir)
        print("✓ ConfigManager创建成功")
        
        # 3. 创建ConfigService
        config_service = ConfigService(config_manager)
        print("✓ ConfigService创建成功")
        
        # 4. 创建AppController并设置配置服务
        app_controller = AppController()
        app_controller.set_config_service(config_service)
        print("✓ AppController设置配置服务成功")
        
        # 5. 创建ConfigDataAccessor
        config = config_manager.get_config()
        config_dto = ConfigDataTransferObject.from_app_config(config)
        config_accessor = ConfigDataAccessor(config_dto)
        app_controller.set_config_accessor(config_accessor)
        print("✓ ConfigDataAccessor创建成功")
        
        # 6. 测试获取初始路径
        initial_path = config_accessor.get_last_analysis_export_path()
        print(f"初始分析导出路径: {initial_path}")
        
        # 7. 测试保存路径
        test_path = "C:/TestAnalysisExport"
        config_service.update_config(last_analysis_export_path=test_path)
        print(f"✓ 保存路径成功: {test_path}")
        
        # 8. 重新创建ConfigDataAccessor验证路径是否保存
        updated_config = config_manager.get_config()
        updated_config_dto = ConfigDataTransferObject.from_app_config(updated_config)
        updated_config_accessor = ConfigDataAccessor(updated_config_dto)
        
        saved_path = updated_config_accessor.get_last_analysis_export_path()
        print(f"重新加载后的路径: {saved_path}")
        
        if saved_path == test_path:
            print("✓ 路径记忆功能正常")
            return True
        else:
            print(f"✗ 路径记忆功能异常: 期望 {test_path}, 实际 {saved_path}")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_dialog_integration():
    """测试对话框集成"""
    print("\n=== 测试对话框集成 ===")
    
    try:
        # 创建QApplication
        from PyQt5.QtWidgets import QApplication
        import sys
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建临时配置
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())
        
        # 设置配置链
        config_manager = ConfigManager(temp_dir)
        config_service = ConfigService(config_manager)
        app_controller = AppController()
        app_controller.set_config_service(config_service)
        
        config = config_manager.get_config()
        config_dto = ConfigDataTransferObject.from_app_config(config)
        config_accessor = ConfigDataAccessor(config_dto)
        app_controller.set_config_accessor(config_accessor)
        
        # 预设一个路径
        test_path = "D:/PresetAnalysisPath"
        config_service.update_config(last_analysis_export_path=test_path)
        
        # 重新创建config_accessor以获取最新配置
        updated_config = config_manager.get_config()
        updated_config_dto = ConfigDataTransferObject.from_app_config(updated_config)
        updated_config_accessor = ConfigDataAccessor(updated_config_dto)
        
        # 创建对话框
        from app.ui.dialogs.analysis_export_dialog import AnalysisExportDialog
        dialog = AnalysisExportDialog(
            parent=None,
            batch_coordinator=None,
            config_accessor=updated_config_accessor,
            app_controller=app_controller
        )
        
        # 检查路径是否正确加载
        loaded_path = dialog.path_edit.text()
        print(f"对话框加载的路径: {loaded_path}")
        
        if loaded_path == test_path:
            print("✓ 对话框路径加载正常")
            
            # 测试保存新路径
            new_path = "E:/NewAnalysisPath"
            dialog.path_edit.setText(new_path)
            dialog._save_export_path(new_path)
            print(f"✓ 对话框保存新路径: {new_path}")
            
            return True
        else:
            print(f"✗ 对话框路径加载异常: 期望 {test_path}, 实际 {loaded_path}")
            return False
            
    except Exception as e:
        print(f"✗ 对话框集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("开始调试数据分析导出路径记忆功能...\n")
    
    success1 = test_config_chain()
    success2 = test_dialog_integration()
    
    if success1 and success2:
        print("\n=== 所有测试通过，功能正常 ===")
    else:
        print("\n=== 存在问题，需要进一步调试 ===")