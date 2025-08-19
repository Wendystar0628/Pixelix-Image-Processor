"""事件总线 - 处理事件发布订阅"""
import asyncio
import logging
from typing import Dict, List, Callable, Any
from collections import defaultdict
from .event_models import Event

logger = logging.getLogger(__name__)


class EventHandler:
    """事件处理器接口"""
    def handle(self, event: Event) -> None:
        """处理事件"""
        raise NotImplementedError


class EventBus:
    """事件总线 - 处理事件发布订阅"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = defaultdict(list)
        self._async_subscribers: Dict[str, List[Callable[[Event], Any]]] = defaultdict(list)
    
    def publish(self, event: Event) -> None:
        """发布事件到所有订阅者"""
        try:
            # 同步处理器
            for handler in self._subscribers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"事件处理失败: {e}")
            
            # 异步处理器
            if self._async_subscribers[event.event_type]:
                asyncio.create_task(self._publish_async(event))
                
        except Exception as e:
            logger.error(f"事件发布失败: {e}")
    
    async def _publish_async(self, event: Event) -> None:
        """异步发布事件"""
        tasks = []
        for handler in self._async_subscribers[event.event_type]:
            tasks.append(asyncio.create_task(handler(event)))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """订阅特定类型事件"""
        self._subscribers[event_type].append(handler)
    
    def subscribe_async(self, event_type: str, handler: Callable[[Event], Any]) -> None:
        """订阅特定类型事件（异步）"""
        self._async_subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """取消订阅"""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
    
    def unsubscribe_async(self, event_type: str, handler: Callable[[Event], Any]) -> None:
        """取消异步订阅"""
        if handler in self._async_subscribers[event_type]:
            self._async_subscribers[event_type].remove(handler)
    
    def clear_subscribers(self, event_type: str = None) -> None:
        """清除订阅者"""
        if event_type:
            self._subscribers[event_type].clear()
            self._async_subscribers[event_type].clear()
        else:
            self._subscribers.clear()
            self._async_subscribers.clear()


# 全局事件总线实例
_global_event_bus = None


def get_event_bus() -> EventBus:
    """获取全局事件总线实例"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus