"""
MainWindow布局管理器

负责创建和管理主窗口的UI布局，包括面板组装和动态布局调整。
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QLabel


class MainWindowLayoutManager:
    """主窗口布局管理器"""
    
    def __init__(self, main_window):
        """
        初始化布局管理器
        
        Args:
            main_window: MainWindow实例
        """
        self.main_window = main_window
        self.main_layout = None
        
    def create_central_widget(self):
        """创建中央窗口部件"""
        main_widget = self._create_main_widget()
        main_splitter = self._create_main_splitter()
        self._assemble_main_layout(main_widget, main_splitter)
        return main_widget
        
    def _create_main_widget(self):
        """创建主容器部件"""
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        return main_widget
        
    def _create_main_splitter(self):
        """创建主分割器"""
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        top_splitter = self._create_top_splitter()
        bottom_panel = self._create_bottom_panel()
        
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_panel)
        main_splitter.setSizes([700, 300])
        return main_splitter
        
    def _create_top_splitter(self):
        """创建顶部分割器"""
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        if self.main_window.batch_processing_panel:
            self._setup_three_column_layout(top_splitter)
        else:
            self._setup_two_column_layout(top_splitter)
            
        return top_splitter
        
    def _setup_three_column_layout(self, splitter):
        """设置三栏布局"""
        # 批处理面板
        left_panel = self._create_batch_panel_widget()
        splitter.addWidget(left_panel)
        
        # 图像显示面板
        splitter.addWidget(self.main_window.image_view_panel)
        
        # 分析面板
        splitter.addWidget(self.main_window.analysis_panel)
        
        splitter.setSizes([200, 700, 300])
        
    def _setup_two_column_layout(self, splitter):
        """设置两栏布局"""
        splitter.addWidget(self.main_window.image_view_panel)
        splitter.addWidget(self.main_window.analysis_panel)
        splitter.setSizes([700, 300])
        
    def _create_batch_panel_widget(self):
        """创建批处理面板容器"""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.addWidget(self.main_window.batch_processing_panel.job_list_panel)
        left_layout.addWidget(self.main_window.batch_processing_panel.job_detail_panel)
        return left_panel
        
    def _create_bottom_panel(self):
        """创建底部面板"""
        bottom_panel = QWidget()
        bottom_layout = QVBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(5, 5, 5, 5)
        
        if self.main_window.batch_processing_panel:
            self._setup_full_bottom_layout(bottom_layout)
        else:
            self._setup_placeholder_bottom_layout(bottom_layout)
            
        return bottom_panel
        
    def _setup_full_bottom_layout(self, layout):
        """设置完整的底部布局"""
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        bottom_splitter.addWidget(self.main_window.batch_processing_panel.image_pool_panel)
        bottom_splitter.addWidget(self.main_window.batch_processing_panel.export_settings_panel)
        bottom_splitter.setSizes([800, 200])
        layout.addWidget(bottom_splitter)
        
    def _setup_placeholder_bottom_layout(self, layout):
        """设置占位符底部布局"""
        placeholder_label = QLabel("图像池将在批处理功能加载后显示")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(placeholder_label)
        
    def _assemble_main_layout(self, main_widget, main_splitter):
        """组装主布局"""
        self.main_layout.addWidget(main_splitter)
        
    def add_batch_processing_panel(self, batch_panel):
        """添加批处理面板到布局"""
        # 存储批处理面板引用
        self.main_window.batch_processing_panel = batch_panel
        # 更新布局以包含批处理面板
        self.update_layout_for_batch_panel()
        
    def update_layout_for_batch_panel(self):
        """根据批处理面板状态更新布局"""
        # 重新创建中央部件以反映批处理面板状态变化
        central_widget = self.create_central_widget()
        self.main_window.setCentralWidget(central_widget)
    
    def is_batch_panel_visible(self) -> bool:
        """检查批处理面板是否可见"""
        return (hasattr(self.main_window, 'batch_processing_panel') and 
                self.main_window.batch_processing_panel is not None)
    
    def get_batch_panel_status(self) -> dict:
        """获取批处理面板状态信息"""
        if not self.is_batch_panel_visible():
            return {"visible": False, "components": {}}
        
        batch_panel = self.main_window.batch_processing_panel
        return {
            "visible": True,
            "components": {
                "job_list_panel": hasattr(batch_panel, 'job_list_panel') and batch_panel.job_list_panel is not None,
                "job_detail_panel": hasattr(batch_panel, 'job_detail_panel') and batch_panel.job_detail_panel is not None,
                "image_pool_panel": hasattr(batch_panel, 'image_pool_panel') and batch_panel.image_pool_panel is not None,
                "export_settings_panel": hasattr(batch_panel, 'export_settings_panel') and batch_panel.export_settings_panel is not None,
            }
        }