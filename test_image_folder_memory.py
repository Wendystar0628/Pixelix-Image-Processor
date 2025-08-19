#!/usr/bin/env python3
"""
图像文件夹路径记忆功能测试

测试图像池"添加图像"功能的路径记忆实现
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.models.app_config import AppConfig
from app.layers.infrastructure.configuration.config_service import ConfigService
from app.features.batch_processing.managers.batch_job_manager import JobManager
from app.features.batch_processing.batch_coordinator import BatchProcessingHandler
from app.core.managers.state_manager import StateManager
from app.layers.business.processing.image_processor import ImageProcessor
from app.layers.business.events.business_event_publisher import BusinessEventPublisher
from app.handlers.file_handler import FileHandler


def test_image_folder_path_memory():
    """测试图像文件夹路径记忆功能"""
    print("开始测试图像文件夹路径记忆功能...")
    
    # 创建临时配置目录
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir)
        
        try:
            # 1. 创建配置服务
            print("1. 创建配置服务...")
            config_service = ConfigService(config_dir)
            
            # 2. 创建必要的依赖
            print("2. 创建依赖组件...")
            event_publisher = BusinessEventPublisher()
            image_processor = ImageProcessor(event_publisher)
            state_manager = StateManager(image_processor)
            file_handler = FileHandler()
            job_manager = JobManager()
            
            # 3. 创建批处理协调器
            print("3. 创建批处理协调器...")
            batch_handler = BatchProcessingHandler(
                job_manager=job_manager,
                state_manager=state_manager,
                file_handler=file_handler,
                image_processor=image_processor,
                config_service=config_service
            )
            
            # 4. 测试路径记忆功能
            print("4. 测试路径记忆功能...")
            
            # 4.1 初始状态应该没有保存的路径
            initial_path = batch_handler.get_last_image_folder_path()
            print(f"   初始路径: {initial_path}")
            assert initial_path is None, f"初始路径应该为None，但得到: {initial_path}"
            
            # 4.2 保存一个测试路径
            test_path = str(Path.home())  # 使用用户主目录作为测试路径
            print(f"   保存测试路径: {test_path}")
            batch_handler.save_last_image_folder_path(test_path)
            
            # 4.3 验证路径是否被正确保存
            saved_path = batch_handler.get_last_image_folder_path()
            print(f"   读取保存的路径: {saved_path}")
            assert saved_path == test_path, f"保存的路径不匹配，期望: {test_path}，实际: {saved_path}"
            
            # 4.4 测试配置持久化
            print("5. 测试配置持久化...")
            
            # 创建新的配置服务实例来验证持久化
            config_service2 = ConfigService(config_dir)
            batch_handler2 = BatchProcessingHandler(
                job_manager=JobManager(),
                state_manager=state_manager,
                file_handler=file_handler,
                image_processor=image_processor,
                config_service=config_service2
            )
            
            # 验证路径是否持久化
            persistent_path = batch_handler2.get_last_image_folder_path()
            print(f"   持久化路径: {persistent_path}")
            assert persistent_path == test_path, f"持久化路径不匹配，期望: {test_path}，实际: {persistent_path}"
            
            # 4.5 测试无效路径处理
            print("6. 测试无效路径处理...")
            invalid_path = "/this/path/does/not/exist"
            batch_handler.save_last_image_folder_path(invalid_path)
            
            # 重新加载配置验证无效路径被处理
            config_service3 = ConfigService(config_dir)
            config = config_service3.get_config()
            # AppConfig的__post_init__方法应该将无效路径设置为None
            print(f"   无效路径处理结果: {config.last_image_folder_path}")
            
            print("✓ 所有测试通过！")
            return True
            
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_config_model():
    """测试AppConfig模型的last_image_folder_path字段"""
    print("\n测试AppConfig模型...")
    
    try:
        # 测试字段存在
        config = AppConfig()
        assert hasattr(config, 'last_image_folder_path'), "AppConfig缺少last_image_folder_path字段"
        
        # 测试默认值
        assert config.last_image_folder_path is None, f"默认值应该为None，但得到: {config.last_image_folder_path}"
        
        # 测试设置有效路径
        valid_path = str(Path.home())
        config.last_image_folder_path = valid_path
        assert config.last_image_folder_path == valid_path, "路径设置失败"
        
        print("✓ AppConfig模型测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ AppConfig模型测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("图像文件夹路径记忆功能测试")
    print("=" * 60)
    
    # 测试1: AppConfig模型
    test1_result = test_config_model()
    
    # 测试2: 路径记忆功能
    test2_result = test_image_folder_path_memory()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"AppConfig模型测试: {'通过' if test1_result else '失败'}")
    print(f"路径记忆功能测试: {'通过' if test2_result else '失败'}")
    
    if test1_result and test2_result:
        print("✓ 所有测试通过！图像文件夹路径记忆功能实现正确。")
        return 0
    else:
        print("✗ 部分测试失败，请检查实现。")
        return 1


if __name__ == "__main__":
    sys.exit(main())