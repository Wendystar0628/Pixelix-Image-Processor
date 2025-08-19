"""配置服务接口"""
from abc import ABC, abstractmethod
from app.models.app_config import AppConfig


class ConfigServiceInterface(ABC):
    """配置服务抽象接口"""
    
    @abstractmethod
    def get_config(self) -> AppConfig:
        """获取配置"""
        pass
    
    @abstractmethod
    def update_config(self, **kwargs) -> None:
        """更新配置"""
        pass
    
    @abstractmethod
    def save_config(self) -> None:
        """保存配置"""
        pass
    
    @abstractmethod
    def load_config(self) -> None:
        """加载配置"""
        pass