"""配置管理器实现 - 纯基础设施组件"""
import json
import logging
from pathlib import Path
from typing import Optional
from dataclasses import asdict

from .config_service_interface import ConfigServiceInterface
from app.models.app_config import AppConfig

logger = logging.getLogger(__name__)


class ConfigManager(ConfigServiceInterface):
    """配置管理器实现 - 纯基础设施组件"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """初始化配置管理器
        
        Args:
            config_dir: 配置目录路径，默认为用户主目录下的.digital_image_processing
        """
        if config_dir is None:
            config_dir = Path.home() / ".digital_image_processing"
        
        self.config_dir = config_dir
        self.config_file = self.config_dir / "config.json"
        self.config = AppConfig()
        
        # 确保配置目录存在
        self._ensure_config_directory()
        
        # 加载配置
        self.load_config()
    
    def _ensure_config_directory(self) -> None:
        """确保配置目录存在"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"创建配置目录失败: {e}")
            raise
    
    def get_config(self) -> AppConfig:
        """获取当前配置"""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """更新配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    logger.debug(f"配置项 {key} 已更新为 {value}")
                else:
                    logger.warning(f"未知的配置项: {key}")
            
            self.save_config()
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            raise
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            config_data = asdict(self.config)
            
            # 确保配置目录存在
            self._ensure_config_directory()
            
            # 写入配置文件
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"配置已保存到 {self.config_file}")
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            raise
    
    def load_config(self) -> None:
        """从文件加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                
                # 更新配置对象
                for key, value in config_data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                    else:
                        logger.warning(f"配置文件中包含未知配置项: {key}")
                
                logger.info(f"配置已从 {self.config_file} 加载")
                
            else:
                logger.info("配置文件不存在，使用默认配置")
                self.save_config()
                
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            logger.info("使用默认配置")
            self._backup_corrupted_config()
            self.save_config()
            
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            logger.info("使用默认配置")
    
    def _backup_corrupted_config(self) -> None:
        """备份损坏的配置文件"""
        try:
            if self.config_file.exists():
                backup_file = self.config_file.with_suffix('.json.backup')
                self.config_file.rename(backup_file)
                logger.info(f"损坏的配置文件已备份为 {backup_file}")
        except Exception as e:
            logger.error(f"备份配置文件失败: {e}")
    
    def reset_to_defaults(self) -> None:
        """重置为默认配置"""
        try:
            self.config = AppConfig()
            self.save_config()
            logger.info("配置已重置为默认值")
        except Exception as e:
            logger.error(f"重置配置失败: {e}")
            raise
    
    def get_config_file_path(self) -> Path:
        """获取配置文件路径"""
        return self.config_file