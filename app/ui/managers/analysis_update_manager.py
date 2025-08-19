"""
分析更新管理器

专门负责智能更新逻辑：stale标记管理、防抖机制、更新策略等。
职责单一：只处理"何时更新"和"更新状态管理"的逻辑。
"""

import logging
from typing import Set, Optional, Callable
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
# 移除核心层直接导入，通过桥接适配器访问
# from app.core.configuration.config_data_accessor import ConfigDataAccessor  # 已移除

# visibility_service 已移除，使用 Qt 原生 API
from app.core.strategies.update_strategies import (
    UpdateStrategyRegistry, UpdateContext, SmartUpdateStrategy
)


logger = logging.getLogger(__name__)


class AnalysisUpdateManager(QObject):
    """
    分析更新管理器
    
    专门负责智能更新逻辑，包括：
    - stale标记管理
    - 防抖机制
    - 更新策略判断
    - 可见性检测集成
    - 更新状态查询
    """
    
    # 信号：请求立即更新指定标签页
    immediate_update_requested = pyqtSignal(int)
    
    # 信号：请求更新当前标签页
    current_tab_update_requested = pyqtSignal()
    
    def __init__(self, analysis_tabs, config_registry, parent=None):  # 通过桥接适配器获取
        super().__init__(parent)
        
        # 标签页引用（只用于获取当前标签页和可见性检测）
        self.analysis_tabs = analysis_tabs
        
        # 智能更新相关属性
        self._stale_tabs: Set[int] = set()
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._process_pending_updates)
        self._pending_update = False
        
        # 使用配置注册表获取配置
        self.config_registry = config_registry
        analysis_config = self.config_registry.get_analysis_update_config()
        
        # 智能更新策略
        self.update_strategy = UpdateStrategyRegistry.get_strategy(
            analysis_config.get('default_strategy', 'smart'),
            debounce_delay=analysis_config.get('debounce_delay', 300),
            invisible_delay=analysis_config.get('invisible_delay', 1000)
        ) or SmartUpdateStrategy()
        
        logger.debug("分析更新管理器初始化完成")
    
    def request_analysis_update(self, tab_index=None):
        """
        请求更新分析数据（智能更新逻辑核心）
        根据策略决定是立即更新还是延迟更新。
        
        Args:
            tab_index: 要更新的标签页索引。如果为None，则使用当前选中的标签页。
        """
        logger.debug(f"收到分析更新请求，标签页索引: {tab_index}")
        
        try:
            # 获取目标标签页
            target_tab = tab_index if tab_index is not None else self.analysis_tabs.currentIndex()
            current_tab = self.analysis_tabs.currentIndex()
            
            # 创建更新上下文
            context = UpdateContext(
                component=self.analysis_tabs,
                tab_index=target_tab,
                is_visible=(target_tab == current_tab),
                user_triggered=(target_tab == current_tab),
                custom_data={'manager': self}
            )
            
            # 使用策略判断是否立即更新
            if self.update_strategy.should_update_now(context):
                logger.debug(f"策略决定立即更新标签页: {target_tab}")
                self.immediate_update_requested.emit(target_tab)
            else:
                # 延迟更新或标记为stale
                if target_tab == current_tab:
                    # 当前标签页使用防抖机制
                    delay = self.update_strategy.get_delay_ms(context)
                    if delay > 0:
                        logger.debug(f"策略决定延迟 {delay}ms 更新当前标签页: {target_tab}")
                        self._schedule_update(delay)
                    else:
                        self.immediate_update_requested.emit(target_tab)
                else:
                    # 非当前标签页标记为stale
                    logger.debug(f"标记隐藏标签页为stale: {target_tab}")
                    self._stale_tabs.add(target_tab)
                    
        except Exception as e:
            logger.error(f"智能更新请求失败: {e}")
            # 错误时回退到立即更新
            target_tab = tab_index if tab_index is not None else self.analysis_tabs.currentIndex()
            self.immediate_update_requested.emit(target_tab)
    
    def handle_tab_changed(self, index):
        """
        处理标签页切换事件
        
        Args:
            index: 新选中的标签页索引
        """
        logger.debug(f"标签页切换到: {index}, stale标签页: {self._stale_tabs}")
        
        try:
            # 如果切换到的标签页被标记为stale，则更新它
            if index in self._stale_tabs:
                logger.info(f"检测到stale标签页 {index}，立即更新")
                self._stale_tabs.remove(index)
                self.immediate_update_requested.emit(index)
            else:
                # 否则使用智能更新逻辑
                logger.debug(f"标签页 {index} 不是stale，使用智能更新逻辑")
                self.request_analysis_update(index)
                
        except Exception as e:
            logger.error(f"处理标签页切换失败: {e}")
            self.immediate_update_requested.emit(index)
    
    def handle_image_data_changed(self):
        """
        处理图像数据变化事件
        当图像数据发生变化时，使用防抖机制避免频繁更新。
        """
        logger.debug("检测到数据变化，启动防抖机制")
        
        try:
            # 设置待处理更新标志
            self._pending_update = True
            
            # 启动防抖定时器
            analysis_config = self.config_registry.get_analysis_update_config()
            self._debounce_timer.start(analysis_config.get('debounce_delay', 300))
            
        except Exception as e:
            logger.error(f"处理数据变化时发生错误: {e}")
            # 错误时立即更新当前标签页
            self.current_tab_update_requested.emit()
    
    def _schedule_update(self, delay_ms):
        """
        安排延迟更新
        
        Args:
            delay_ms: 延迟时间（毫秒）
        """
        logger.debug(f"安排 {delay_ms}ms 后更新")
        self._pending_update = True
        self._debounce_timer.start(delay_ms)
    
    def _process_pending_updates(self):
        """
        处理待处理的更新（防抖定时器回调）
        """
        if self._pending_update:
            logger.debug("处理待处理的更新")
            self._pending_update = False
            
            try:
                # 获取当前标签页并触发智能更新
                current_tab = self.analysis_tabs.currentIndex()
                self.immediate_update_requested.emit(current_tab)
                
                # 将所有其他标签页标记为stale
                total_tabs = self.analysis_tabs.count()
                for i in range(total_tabs):
                    if i != current_tab:
                        self._stale_tabs.add(i)
                        
                logger.debug(f"已处理数据变化更新，当前标签页: {current_tab}, stale标签页: {self._stale_tabs}")
                
            except Exception as e:
                logger.error(f"处理待处理更新时发生错误: {e}")
    
    # ==================== Stale 标签页管理 ====================
    
    def get_stale_tabs(self) -> Set[int]:
        """
        获取当前被标记为stale的标签页集合
        
        Returns:
            Set[int]: stale标签页索引的集合
        """
        return self._stale_tabs.copy()
    
    def clear_stale_tabs(self):
        """清除所有stale标签页标记"""
        logger.debug(f"清除所有stale标签页标记: {self._stale_tabs}")
        self._stale_tabs.clear()
    
    def is_tab_stale(self, tab_index: int) -> bool:
        """
        检查指定标签页是否为stale状态
        
        Args:
            tab_index: 标签页索引
            
        Returns:
            bool: 如果标签页为stale状态返回True，否则返回False
        """
        return tab_index in self._stale_tabs
    
    def mark_tab_stale(self, tab_index: int):
        """
        标记指定标签页为stale状态
        
        Args:
            tab_index: 标签页索引
        """
        self._stale_tabs.add(tab_index)
        logger.debug(f"标记标签页 {tab_index} 为stale")
    
    def mark_tab_fresh(self, tab_index: int):
        """
        移除指定标签页的stale标记
        
        Args:
            tab_index: 标签页索引
        """
        self._stale_tabs.discard(tab_index)
        logger.debug(f"移除标签页 {tab_index} 的stale标记")
    
    # ==================== 状态查询 ====================
    
    def get_update_status(self) -> dict:
        """
        获取当前更新状态信息
        
        Returns:
            dict: 包含当前更新状态的字典
        """
        try:
            current_tab = self.analysis_tabs.currentIndex()
            total_tabs = self.analysis_tabs.count()
            stale_tabs = self.get_stale_tabs()
            
            status = {
                'current_tab': current_tab,
                'total_tabs': total_tabs,
                'stale_tabs': list(stale_tabs),
                'stale_count': len(stale_tabs),
                'pending_update': self._pending_update,
                'debounce_active': self._debounce_timer.isActive(),
                'strategy_name': self.update_strategy.get_name()
            }
            
            logger.debug(f"当前更新状态: {status}")
            return status
            
        except Exception as e:
            logger.error(f"获取更新状态时发生错误: {e}")
            return {'error': str(e)}
    
    def configure_update_behavior(self):
        """基于配置提供者重新配置更新行为"""
        try:
            # 重新获取配置
            analysis_config = self.config_registry.get_analysis_update_config()
            
            # 重新创建更新策略
            self.update_strategy = UpdateStrategyRegistry.get_strategy(
                analysis_config.get('default_strategy', 'smart'),
                debounce_delay=analysis_config.get('debounce_delay', 300),
                invisible_delay=analysis_config.get('invisible_delay', 1000)
            ) or SmartUpdateStrategy()
            
            logger.info(f"更新行为已重新配置: 策略={analysis_config.get('default_strategy', 'smart')}")
            
        except Exception as e:
            logger.error(f"配置更新行为时发生错误: {e}")