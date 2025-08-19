"""
更新策略注册表

统一管理所有更新策略，支持项目范围的复用。
提供策略注册机制，支持动态扩展。
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Type, Any, Optional
from dataclasses import dataclass
from PyQt6.QtCore import QTimer

logger = logging.getLogger(__name__)


@dataclass
class UpdateContext:
    """更新上下文数据类"""
    component: Any = None           # 要更新的组件
    tab_index: Optional[int] = None # 标签页索引
    is_visible: bool = True         # 是否可见
    last_update_time: float = 0     # 上次更新时间
    data_changed: bool = False      # 数据是否变化
    user_triggered: bool = False    # 是否用户触发
    force_update: bool = False      # 是否强制更新
    custom_data: Dict[str, Any] = None  # 自定义数据
    
    def __post_init__(self):
        if self.custom_data is None:
            self.custom_data = {}


class UpdateStrategy(ABC):
    """
    更新策略基类
    
    定义更新策略的标准接口，所有具体策略都应该继承此类。
    """
    
    @abstractmethod
    def should_update_now(self, context: UpdateContext) -> bool:
        """
        判断是否应该立即更新
        
        Args:
            context: 更新上下文信息
            
        Returns:
            bool: 如果应该立即更新返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def get_delay_ms(self, context: UpdateContext) -> int:
        """
        获取延迟更新的时间（毫秒）
        
        Args:
            context: 更新上下文信息
            
        Returns:
            int: 延迟时间（毫秒），0表示立即更新
        """
        pass
    
    def get_name(self) -> str:
        """获取策略名称"""
        return self.__class__.__name__
    
    def get_description(self) -> str:
        """获取策略描述"""
        return self.__doc__ or "无描述"


class ImmediateUpdateStrategy(UpdateStrategy):
    """
    立即更新策略
    
    无论任何情况都立即执行更新，适用于对实时性要求高的场景。
    """
    
    def should_update_now(self, context: UpdateContext) -> bool:
        """总是立即更新"""
        logger.debug("立即更新策略：总是立即更新")
        return True
    
    def get_delay_ms(self, context: UpdateContext) -> int:
        """立即更新，无延迟"""
        return 0


class DebouncedUpdateStrategy(UpdateStrategy):
    """
    防抖更新策略
    
    使用防抖机制避免频繁更新，适用于数据变化频繁的场景。
    在指定时间内如果有新的更新请求，则重置定时器。
    """
    
    def __init__(self, debounce_delay: int = 100):
        """
        初始化防抖策略
        
        Args:
            debounce_delay: 防抖延迟时间（毫秒）
        """
        self.debounce_delay = debounce_delay
        logger.debug(f"防抖更新策略初始化，延迟: {debounce_delay}ms")
    
    def should_update_now(self, context: UpdateContext) -> bool:
        """根据可见性和强制更新标志决定是否立即更新"""
        # 如果强制更新或组件可见，考虑立即更新
        if context.force_update:
            logger.debug("防抖策略：强制更新，立即执行")
            return True
        
        if context.is_visible and context.user_triggered:
            logger.debug("防抖策略：用户触发且可见，立即执行")
            return True
        
        logger.debug("防抖策略：延迟更新")
        return False
    
    def get_delay_ms(self, context: UpdateContext) -> int:
        """获取防抖延迟时间"""
        return self.debounce_delay


class VisibilityBasedUpdateStrategy(UpdateStrategy):
    """
    基于可见性的更新策略
    
    只有当组件可见时才立即更新，不可见时延迟或跳过更新。
    适用于有多个标签页或面板的界面。
    """
    
    def __init__(self, invisible_delay: int = 500):
        """
        初始化可见性策略
        
        Args:
            invisible_delay: 不可见时的延迟时间（毫秒）
        """
        self.invisible_delay = invisible_delay
        logger.debug(f"可见性更新策略初始化，不可见延迟: {invisible_delay}ms")
    
    def should_update_now(self, context: UpdateContext) -> bool:
        """只有可见或强制更新时才立即更新"""
        if context.force_update:
            logger.debug("可见性策略：强制更新，立即执行")
            return True
        
        if context.is_visible:
            logger.debug("可见性策略：组件可见，立即执行")
            return True
        
        logger.debug("可见性策略：组件不可见，延迟执行")
        return False
    
    def get_delay_ms(self, context: UpdateContext) -> int:
        """根据可见性返回延迟时间"""
        if context.is_visible or context.force_update:
            return 0
        return self.invisible_delay


class ThrottledUpdateStrategy(UpdateStrategy):
    """
    节流更新策略
    
    限制更新频率，在指定时间间隔内只允许一次更新。
    适用于性能敏感的场景。
    """
    
    def __init__(self, throttle_interval: int = 200):
        """
        初始化节流策略
        
        Args:
            throttle_interval: 节流间隔时间（毫秒）
        """
        self.throttle_interval = throttle_interval
        logger.debug(f"节流更新策略初始化，间隔: {throttle_interval}ms")
    
    def should_update_now(self, context: UpdateContext) -> bool:
        """根据上次更新时间和节流间隔决定是否更新"""
        import time
        current_time = time.time() * 1000  # 转换为毫秒
        
        if context.force_update:
            logger.debug("节流策略：强制更新，立即执行")
            return True
        
        if current_time - context.last_update_time >= self.throttle_interval:
            logger.debug("节流策略：超过节流间隔，立即执行")
            return True
        
        logger.debug("节流策略：在节流间隔内，跳过更新")
        return False
    
    def get_delay_ms(self, context: UpdateContext) -> int:
        """节流策略通常立即执行或跳过"""
        return 0


class SmartUpdateStrategy(UpdateStrategy):
    """
    智能更新策略
    
    综合考虑可见性、防抖和用户交互等因素的智能策略。
    这是智能更新系统的核心策略。
    """
    
    def __init__(self, debounce_delay: int = 100, invisible_delay: int = 300):
        """
        初始化智能策略
        
        Args:
            debounce_delay: 防抖延迟时间（毫秒）
            invisible_delay: 不可见时的延迟时间（毫秒）
        """
        self.debounce_delay = debounce_delay
        self.invisible_delay = invisible_delay
        logger.debug(f"智能更新策略初始化，防抖延迟: {debounce_delay}ms, 不可见延迟: {invisible_delay}ms")
    
    def should_update_now(self, context: UpdateContext) -> bool:
        """智能判断是否立即更新"""
        # 强制更新总是立即执行
        if context.force_update:
            logger.debug("智能策略：强制更新，立即执行")
            return True
        
        # 用户直接触发且可见时立即更新
        if context.user_triggered and context.is_visible:
            logger.debug("智能策略：用户触发且可见，立即执行")
            return True
        
        # 可见且数据变化不大时立即更新
        if context.is_visible and not context.data_changed:
            logger.debug("智能策略：可见且数据未变化，立即执行")
            return True
        
        logger.debug("智能策略：延迟执行")
        return False
    
    def get_delay_ms(self, context: UpdateContext) -> int:
        """根据上下文返回合适的延迟时间"""
        if context.force_update or (context.user_triggered and context.is_visible):
            return 0
        
        if context.is_visible:
            return self.debounce_delay
        
        return self.invisible_delay


class UpdateStrategyRegistry:
    """
    更新策略注册表
    
    使用注册表模式管理更新策略，支持策略的动态注册和获取。
    """
    
    _strategies: Dict[str, Type[UpdateStrategy]] = {}
    _instances: Dict[str, UpdateStrategy] = {}
    
    @classmethod
    def register(cls, name: str, strategy_class: Type[UpdateStrategy] = None):
        """
        注册更新策略
        
        可以作为装饰器使用或直接调用。
        
        Args:
            name: 策略名称
            strategy_class: 策略类（当作为装饰器使用时为None）
            
        Returns:
            装饰器函数或None
            
        Example:
            # 作为装饰器使用
            @UpdateStrategyRegistry.register('my_strategy')
            class MyStrategy(UpdateStrategy):
                pass
            
            # 直接调用
            UpdateStrategyRegistry.register('other_strategy', OtherStrategy)
        """
        def decorator(strategy_cls: Type[UpdateStrategy]):
            cls._strategies[name] = strategy_cls
            logger.debug(f"注册更新策略: {name} -> {strategy_cls.__name__}")
            return strategy_cls
        
        if strategy_class is not None:
            return decorator(strategy_class)
        return decorator
    
    @classmethod
    def get_strategy(cls, name: str, **kwargs) -> Optional[UpdateStrategy]:
        """
        获取策略实例
        
        Args:
            name: 策略名称
            **kwargs: 策略初始化参数
            
        Returns:
            UpdateStrategy: 策略实例，如果未找到返回None
            
        Example:
            strategy = UpdateStrategyRegistry.get_strategy('debounced', debounce_delay=200)
        """
        if name not in cls._strategies:
            logger.warning(f"未找到策略: {name}")
            return None
        
        # 为每次请求创建新实例，支持不同参数
        strategy_class = cls._strategies[name]
        try:
            instance = strategy_class(**kwargs)
            logger.debug(f"创建策略实例: {name}")
            return instance
        except Exception as e:
            logger.error(f"创建策略实例失败: {name}, 错误: {e}")
            return None
    
    @classmethod
    def get_singleton_strategy(cls, name: str, **kwargs) -> Optional[UpdateStrategy]:
        """
        获取策略单例实例
        
        Args:
            name: 策略名称
            **kwargs: 策略初始化参数（仅在首次创建时使用）
            
        Returns:
            UpdateStrategy: 策略单例实例
        """
        if name not in cls._instances:
            strategy = cls.get_strategy(name, **kwargs)
            if strategy:
                cls._instances[name] = strategy
        
        return cls._instances.get(name)
    
    @classmethod
    def list_strategies(cls) -> List[str]:
        """
        列出所有可用策略
        
        Returns:
            List[str]: 策略名称列表
        """
        return list(cls._strategies.keys())
    
    @classmethod
    def get_strategy_info(cls, name: str) -> Optional[Dict[str, str]]:
        """
        获取策略信息
        
        Args:
            name: 策略名称
            
        Returns:
            Dict: 策略信息字典
        """
        if name not in cls._strategies:
            return None
        
        strategy_class = cls._strategies[name]
        return {
            'name': name,
            'class_name': strategy_class.__name__,
            'description': strategy_class.__doc__ or "无描述"
        }
    
    @classmethod
    def clear_instances(cls):
        """清除所有单例实例"""
        cls._instances.clear()
        logger.debug("清除所有策略单例实例")


# 注册内置策略
UpdateStrategyRegistry.register('immediate', ImmediateUpdateStrategy)
UpdateStrategyRegistry.register('debounced', DebouncedUpdateStrategy)
UpdateStrategyRegistry.register('visibility', VisibilityBasedUpdateStrategy)
UpdateStrategyRegistry.register('throttled', ThrottledUpdateStrategy)
UpdateStrategyRegistry.register('smart', SmartUpdateStrategy)

logger.debug("内置更新策略注册完成")