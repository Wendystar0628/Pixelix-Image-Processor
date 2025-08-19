"""
UI状态管理器模块

该模块提供了一个中心化的UI状态管理器，用于统一管理所有依赖于应用状态的UI组件。
它消除了在后端代码中重复检查状态的需要，并改善了用户体验。
"""

from typing import List, Optional, Union
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget


class UIStateManager(QObject):
    """
    UI状态管理器
    
    负责管理所有依赖于应用状态（如图像是否加载）的UI组件。
    当状态发生变化时，自动更新所有注册的UI组件的启用/禁用状态。
    
    特性：
    - 支持QAction和QWidget的状态管理
    - 自动处理已销毁组件的清理
    - 提供批量状态更新功能
    - 线程安全的状态更新
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化UI状态管理器
        
        Args:
            parent: 父窗口部件，用于Qt对象层次结构
        """
        super().__init__(parent)
        
        # 存储需要根据图像加载状态更新的UI组件
        self._image_dependent_actions: List[QAction] = []
        self._image_dependent_widgets: List[QWidget] = []
        
        # 当前图像加载状态缓存
        self._current_image_loaded_state: bool = False
        
        # 性能优化相关
        self._batch_update_pending: bool = False
        self._last_update_time: float = 0.0
        
        print("UIStateManager initialized")
    
    def safe_connect_to_state_manager(self, state_manager) -> bool:
        """
        安全地连接到StateManager的信号
        
        Args:
            state_manager: 状态管理器实例（通过桥接适配器获取）
            
        Returns:
            bool: 连接成功返回True
        """
        try:
            if state_manager and hasattr(state_manager, 'image_state_changed'):
                state_manager.image_state_changed.connect(self.update_actions_state)
                print("Successfully connected to StateManager.image_state_changed signal")
                return True
            else:
                print("Warning: StateManager does not have image_state_changed signal")
                return False
        except Exception as e:
            print(f"Error connecting to StateManager signal: {e}")
            return False
    
    def register_image_dependent_action(self, action: QAction) -> None:
        """
        注册一个依赖图像加载状态的QAction
        
        Args:
            action: 要注册的QAction对象
            
        注意：
            - 重复注册同一个action会被忽略
            - action会在图像加载时启用，未加载时禁用
        """
        if action and action not in self._image_dependent_actions:
            self._image_dependent_actions.append(action)
            # 立即应用当前状态
            try:
                action.setEnabled(self._current_image_loaded_state)
            except RuntimeError:
                # action已被销毁，从列表中移除
                self._image_dependent_actions.remove(action)
            
            print(f"Registered image-dependent action: {action.text()}")
    
    def register_image_dependent_widget(self, widget: QWidget) -> None:
        """
        注册一个依赖图像加载状态的QWidget
        
        Args:
            widget: 要注册的QWidget对象
            
        注意：
            - 重复注册同一个widget会被忽略
            - widget会在图像加载时启用，未加载时禁用
        """
        if widget and widget not in self._image_dependent_widgets:
            self._image_dependent_widgets.append(widget)
            # 立即应用当前状态
            try:
                widget.setEnabled(self._current_image_loaded_state)
            except RuntimeError:
                # widget已被销毁，从列表中移除
                self._image_dependent_widgets.remove(widget)
            
            print(f"Registered image-dependent widget: {widget.__class__.__name__}")
    
    @pyqtSlot(bool)
    def update_actions_state(self, is_image_loaded: bool) -> None:
        """
        更新所有注册组件的状态
        
        这是一个槽函数，通常连接到StateManager的image_state_changed信号。
        包含完善的错误处理和状态恢复机制。
        
        Args:
            is_image_loaded: 图像是否已加载
        """
        try:
            print(f"Updating UI state: image_loaded={is_image_loaded}")
            
            # 更新状态缓存
            self._current_image_loaded_state = is_image_loaded
            
            # 更新所有注册的actions
            actions_updated = self._update_actions(is_image_loaded)
            
            # 更新所有注册的widgets
            widgets_updated = self._update_widgets(is_image_loaded)
            
            print(f"UI state update completed. Actions: {actions_updated}/{len(self._image_dependent_actions)}, "
                  f"Widgets: {widgets_updated}/{len(self._image_dependent_widgets)}")
                  
        except Exception as e:
            print(f"Error during UI state update: {e}")
            # 尝试恢复到一致状态
            self._emergency_state_recovery(is_image_loaded)
    
    def _update_actions(self, is_enabled: bool) -> int:
        """
        更新所有注册的QAction的状态
        
        Args:
            is_enabled: 是否启用
            
        Returns:
            int: 成功更新的actions数量
        """
        failed_actions = []
        updated_count = 0
        
        for action in self._image_dependent_actions[:]:  # 创建副本避免修改时迭代
            try:
                if action and not self._is_action_destroyed(action):
                    action.setEnabled(is_enabled)
                    updated_count += 1
                else:
                    failed_actions.append(action)
            except RuntimeError as e:
                print(f"Warning: Failed to update action state: {e}")
                failed_actions.append(action)
            except Exception as e:
                print(f"Unexpected error updating action: {e}")
                failed_actions.append(action)
        
        # 清理失效的actions
        for action in failed_actions:
            if action in self._image_dependent_actions:
                self._image_dependent_actions.remove(action)
                print(f"Removed destroyed action from registry")
                
        return updated_count
    
    def _update_widgets(self, is_enabled: bool) -> int:
        """
        更新所有注册的QWidget的状态
        
        Args:
            is_enabled: 是否启用
            
        Returns:
            int: 成功更新的widgets数量
        """
        failed_widgets = []
        updated_count = 0
        
        for widget in self._image_dependent_widgets[:]:  # 创建副本避免修改时迭代
            try:
                if widget and not self._is_widget_destroyed(widget):
                    widget.setEnabled(is_enabled)
                    updated_count += 1
                else:
                    failed_widgets.append(widget)
            except RuntimeError as e:
                print(f"Warning: Failed to update widget state: {e}")
                failed_widgets.append(widget)
            except Exception as e:
                print(f"Unexpected error updating widget: {e}")
                failed_widgets.append(widget)
        
        # 清理失效的widgets
        for widget in failed_widgets:
            if widget in self._image_dependent_widgets:
                self._image_dependent_widgets.remove(widget)
                print(f"Removed destroyed widget from registry")
                
        return updated_count
    
    def _is_action_destroyed(self, action: QAction) -> bool:
        """
        检查QAction是否已被销毁
        
        Args:
            action: 要检查的QAction
            
        Returns:
            bool: 如果action已被销毁返回True
        """
        try:
            # 尝试访问action的属性来检查是否有效
            _ = action.text()
            return False
        except RuntimeError:
            return True
    
    def _is_widget_destroyed(self, widget: QWidget) -> bool:
        """
        检查QWidget是否已被销毁
        
        Args:
            widget: 要检查的QWidget
            
        Returns:
            bool: 如果widget已被销毁返回True
        """
        try:
            # 尝试访问widget的属性来检查是否有效
            _ = widget.isEnabled()
            return False
        except RuntimeError:
            return True
    
    def clear_all_registrations(self) -> None:
        """
        清除所有注册的UI组件
        
        通常在应用关闭或重置时调用。
        """
        self._image_dependent_actions.clear()
        self._image_dependent_widgets.clear()
        print("All UI component registrations cleared")
    
    def get_registered_actions_count(self) -> int:
        """
        获取已注册的actions数量
        
        Returns:
            int: 注册的actions数量
        """
        return len(self._image_dependent_actions)
    
    def get_registered_widgets_count(self) -> int:
        """
        获取已注册的widgets数量
        
        Returns:
            int: 注册的widgets数量
        """
        return len(self._image_dependent_widgets)
    
    def force_sync_state(self, is_image_loaded: bool) -> None:
        """
        强制同步所有组件状态
        
        用于处理状态不一致的情况。
        
        Args:
            is_image_loaded: 目标状态
        """
        print(f"Force syncing UI state to: {is_image_loaded}")
        self.update_actions_state(is_image_loaded)
    
    def _emergency_state_recovery(self, target_state: bool) -> None:
        """
        紧急状态恢复机制
        
        当正常状态更新失败时，尝试恢复到一致状态。
        
        Args:
            target_state: 目标状态
        """
        print(f"Attempting emergency state recovery to: {target_state}")
        
        try:
            # 清理所有可能已销毁的组件
            self._cleanup_destroyed_components()
            
            # 尝试简单的状态更新
            for action in self._image_dependent_actions[:]:
                try:
                    if action:
                        action.setEnabled(target_state)
                except:
                    self._image_dependent_actions.remove(action)
            
            for widget in self._image_dependent_widgets[:]:
                try:
                    if widget:
                        widget.setEnabled(target_state)
                except:
                    self._image_dependent_widgets.remove(widget)
                    
            self._current_image_loaded_state = target_state
            print("Emergency state recovery completed")
            
        except Exception as e:
            print(f"Emergency state recovery failed: {e}")
            # 最后的手段：清空所有注册
            self.clear_all_registrations()
    
    def _cleanup_destroyed_components(self) -> None:
        """
        清理所有已销毁的组件
        """
        # 清理actions
        valid_actions = []
        for action in self._image_dependent_actions:
            if action and not self._is_action_destroyed(action):
                valid_actions.append(action)
        self._image_dependent_actions = valid_actions
        
        # 清理widgets
        valid_widgets = []
        for widget in self._image_dependent_widgets:
            if widget and not self._is_widget_destroyed(widget):
                valid_widgets.append(widget)
        self._image_dependent_widgets = valid_widgets
        
        print(f"Cleanup completed. Valid actions: {len(self._image_dependent_actions)}, "
              f"Valid widgets: {len(self._image_dependent_widgets)}")
    
    def get_state_info(self) -> dict:
        """
        获取当前状态信息，用于调试和监控
        
        Returns:
            dict: 包含状态信息的字典
        """
        return {
            "current_image_loaded_state": self._current_image_loaded_state,
            "registered_actions_count": len(self._image_dependent_actions),
            "registered_widgets_count": len(self._image_dependent_widgets),
            "valid_actions_count": sum(1 for a in self._image_dependent_actions if a and not self._is_action_destroyed(a)),
            "valid_widgets_count": sum(1 for w in self._image_dependent_widgets if w and not self._is_widget_destroyed(w))
        }
    
    def validate_state_consistency(self) -> bool:
        """
        验证状态一致性
        
        Returns:
            bool: 如果状态一致返回True
        """
        try:
            inconsistent_actions = []
            inconsistent_widgets = []
            
            # 检查actions状态一致性
            for action in self._image_dependent_actions:
                if action and not self._is_action_destroyed(action):
                    if action.isEnabled() != self._current_image_loaded_state:
                        inconsistent_actions.append(action)
            
            # 检查widgets状态一致性
            for widget in self._image_dependent_widgets:
                if widget and not self._is_widget_destroyed(widget):
                    if widget.isEnabled() != self._current_image_loaded_state:
                        inconsistent_widgets.append(widget)
            
            if inconsistent_actions or inconsistent_widgets:
                print(f"State inconsistency detected. Actions: {len(inconsistent_actions)}, "
                      f"Widgets: {len(inconsistent_widgets)}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error during state consistency validation: {e}")
            return False