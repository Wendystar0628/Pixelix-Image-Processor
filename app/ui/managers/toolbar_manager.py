"""
工具栏管理器模块
"""
from typing import Optional, List
from PyQt6.QtCore import QSize, QObject, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QToolBar, QMainWindow

class ToolbarManager(QObject):
    """
    负责创建和管理主窗口的工具栏。
    通过信号与外部世界通信。
    """
    open_file_triggered = pyqtSignal()
    import_folder_triggered = pyqtSignal()
    save_file_triggered = pyqtSignal()
    clear_effects_triggered = pyqtSignal()
    # 删除了 save_file_as_triggered 信号

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        # 将 parent 转换为 QMainWindow 类型，因为我们知道它是主窗口
        self.parent_window = parent if isinstance(parent, QMainWindow) else None
        self.main_toolbar = None
        
        # 存储需要图像状态管理的actions
        self._image_dependent_actions: List[QAction] = []
        
        # 存储特定actions的引用，用于状态管理
        self.clear_effects_action: Optional[QAction] = None

    def create_toolbar(self) -> QToolBar:
        """创建主窗口工具栏。"""
        # 确保 parent_window 不为 None
        if self.parent_window is None:
            raise ValueError("父窗口不能为 None")
            
        # 创建主工具栏
        self.main_toolbar = QToolBar("主工具栏", self.parent_window)
        self.main_toolbar.setMovable(False)
        self.main_toolbar.setIconSize(QSize(24, 24))

        # 添加按钮
        self._add_action("导入文件夹", "导入文件夹中的所有图像到图像池", self.import_folder_triggered, image_dependent=False)
        self.main_toolbar.addSeparator()
        self._add_action("保存", "保存当前图像", self.save_file_triggered, image_dependent=True)
        self.clear_effects_action = self._add_action_with_return("清除效果", "清除当前图像的所有处理效果", self.clear_effects_triggered, image_dependent=True)
        # 删除了"另存为"按钮

        return self.main_toolbar
        
    def _add_action(self, text: str, tooltip: str, signal, image_dependent: bool = False):
        """
        添加一个动作到工具栏
        
        Args:
            text: 动作文本
            tooltip: 提示文本
            signal: 要连接的信号
            image_dependent: 是否依赖图像加载状态
        """
        # 确保 main_toolbar 和 parent_window 不为 None
        if self.main_toolbar is None or self.parent_window is None:
            return
            
        action = QAction(text, self.parent_window)
        action.setToolTip(tooltip)
        action.triggered.connect(lambda: signal.emit())
        self.main_toolbar.addAction(action)
        
        # 如果依赖图像状态，添加到管理列表
        if image_dependent:
            self._image_dependent_actions.append(action)

    def _add_action_with_return(self, text: str, tooltip: str, signal, image_dependent: bool = False) -> QAction:
        """
        添加一个动作到工具栏并返回action引用
        
        Args:
            text: 动作文本
            tooltip: 提示文本
            signal: 要连接的信号
            image_dependent: 是否依赖图像加载状态
        
        Returns:
            QAction: 创建的action
        """
        # 确保 main_toolbar 和 parent_window 不为 None
        if self.main_toolbar is None or self.parent_window is None:
            return None
            
        action = QAction(text, self.parent_window)
        action.setToolTip(tooltip)
        action.triggered.connect(lambda: signal.emit())
        self.main_toolbar.addAction(action)
        
        # 如果依赖图像状态，添加到管理列表
        if image_dependent:
            self._image_dependent_actions.append(action)
            
        return action
    
    def get_image_dependent_actions(self) -> List[QAction]:
        """
        获取所有依赖图像加载状态的工具栏actions
        
        Returns:
            List[QAction]: 需要图像状态管理的actions列表
        """
        return self._image_dependent_actions.copy()  # 返回副本以防止外部修改