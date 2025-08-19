"""
菜单管理器模块
"""
import os
from typing import Optional, cast, Dict, List
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QMenu, QMenuBar, QWidget




class MenuManager(QObject):  # 继承自 QObject 以支持信号
    """
    负责创建和管理主窗口的菜单。
    解耦后的MenuManager通过信号与外部通信，不再直接调用MainWindow的方法。
    """
    # --- 文件菜单信号 ---
    open_file_triggered = pyqtSignal()
    import_folder_triggered = pyqtSignal()
    save_file_triggered = pyqtSignal()
    # 删除了 save_file_as_triggered 信号
    open_recent_file_triggered = pyqtSignal(str)
    exit_app_triggered = pyqtSignal()

    # --- 编辑菜单信号 ---
    undo_triggered = pyqtSignal()
    redo_triggered = pyqtSignal()
    clear_effects_triggered = pyqtSignal()

    # --- 操作信号 ---
    # 参数: 对话框/操作的字符串标识符 (e.g., "brightness_contrast")
    show_dialog_triggered = pyqtSignal(str)
    apply_simple_operation_triggered = pyqtSignal(str)
    
    # --- 工具菜单信号 ---
    set_proxy_quality_triggered = pyqtSignal(float)  # 新增：设置代理图像质量信号

    
    # --- 预设菜单信号 ---
    apply_preset_triggered = pyqtSignal()
    save_as_preset_triggered = pyqtSignal()
    delete_preset_triggered = pyqtSignal()
    
    # --- 帮助菜单信号 ---
    help_triggered = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        # 注意：parent必须是QWidget类型，所以我们需要进行类型转换
        self.parent_widget = cast(QWidget, parent)  # 将parent转换为QWidget
        
        # 直接访问MainWindow注入的依赖
        self.state_manager = getattr(parent, 'state_manager', None)
        self.file_handler = getattr(parent, 'file_handler', None)
        self.recent_files_menu = None
        self.proxy_quality_menu = None  # 新增：代理质量子菜单
        self.proxy_quality_actions = {}  # 存储代理质量菜单项，用于更新选中状态
        
        # 存储需要图像状态管理的actions
        self._image_dependent_actions: List[QAction] = []
        
        # 存储特定actions的引用，用于状态管理
        self.undo_action: Optional[QAction] = None
        self.redo_action: Optional[QAction] = None
        self.clear_effects_action: Optional[QAction] = None

    def create_menus(self, menu_bar: QMenuBar):
        """创建所有菜单。"""
        assert menu_bar is not None, "A valid menu_bar must be provided"

        # 在菜单栏最左边添加"Alt+"提示
        alt_hint_action = QAction("Alt+以导航", self.parent_widget)
        alt_hint_action.setEnabled(False)  # 设置为不可点击
        menu_bar.addAction(alt_hint_action)

        self._create_file_menu(menu_bar)
        self._create_edit_menu(menu_bar)
        self._create_presets_menu(menu_bar)
        self._create_tools_menu(menu_bar)
        self._create_point_op_menu(menu_bar)
        self._create_spatial_filtering_menu(menu_bar)
        self._create_regular_filters_menu(menu_bar)
        self._create_transform_menu(menu_bar)
        self._create_help_menu(menu_bar)

    def _create_file_menu(self, menu_bar: QMenuBar):
        """创建文件菜单。"""
        file_menu = menu_bar.addMenu("文件(&F)")
        assert file_menu is not None, "QMenuBar.addMenu() should return a valid QMenu"

        # 删除了"添加图像"菜单项

        import_folder_action = QAction("导入文件夹...", self.parent_widget)
        import_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        import_folder_action.triggered.connect(lambda: self.import_folder_triggered.emit())
        file_menu.addAction(import_folder_action)

        file_menu.addSeparator()

        save_action = QAction("保存", self.parent_widget)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(lambda: self.save_file_triggered.emit())
        file_menu.addAction(save_action)
        # 保存功能需要图像加载
        self._image_dependent_actions.append(save_action)

        # 删除了"另存为"菜单项

        self.recent_files_menu = QMenu("最近打开的文件", self.parent_widget)
        file_menu.addMenu(self.recent_files_menu)

        if self.file_handler is not None and hasattr(self.file_handler, 'recent_files_changed'):
            self.file_handler.recent_files_changed.connect(self.update_recent_files_menu)
            recent_files = self.file_handler.recent_files if hasattr(self.file_handler, 'recent_files') else []
            self.update_recent_files_menu(recent_files)

        file_menu.addSeparator()

        exit_action = QAction("退出", self.parent_widget)
        exit_action.triggered.connect(lambda: self.exit_app_triggered.emit())
        file_menu.addAction(exit_action)

    def _create_edit_menu(self, menu_bar: QMenuBar):
        """创建编辑菜单。"""
        edit_menu = menu_bar.addMenu("编辑(&E)")
        assert edit_menu is not None, "QMenuBar.addMenu() should return a valid QMenu"
        
        # 添加撤销/重做操作
        self.undo_action = QAction("撤销", self.parent_widget)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(lambda: self.undo_triggered.emit())
        edit_menu.addAction(self.undo_action)
        # 撤销功能需要图像加载
        self._image_dependent_actions.append(self.undo_action)
        
        self.redo_action = QAction("重做", self.parent_widget)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(lambda: self.redo_triggered.emit())
        edit_menu.addAction(self.redo_action)
        # 重做功能需要图像加载
        self._image_dependent_actions.append(self.redo_action)
        
        edit_menu.addSeparator()
        
        # 添加清除所有效果菜单项
        self.clear_effects_action = QAction("清除所有效果", self.parent_widget)
        self.clear_effects_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        self.clear_effects_action.triggered.connect(lambda: self.clear_effects_triggered.emit())
        edit_menu.addAction(self.clear_effects_action)
        # 清除效果功能需要图像加载
        self._image_dependent_actions.append(self.clear_effects_action)
        
    def _create_presets_menu(self, menu_bar: QMenuBar):
        """创建预设菜单。"""
        presets_menu = menu_bar.addMenu("预设(&P)")
        assert presets_menu is not None, "QMenuBar.addMenu() should return a valid QMenu"
        
        # 添加"快速应用预设"菜单项
        apply_preset_action = QAction("快速应用预设...(&Q)", self.parent_widget)
        apply_preset_action.triggered.connect(lambda: self.apply_preset_triggered.emit())
        presets_menu.addAction(apply_preset_action)
        # 应用预设功能需要图像加载
        self._image_dependent_actions.append(apply_preset_action)
        
        # 添加"将当前效果另存为预设"菜单项
        save_as_preset_action = QAction("将当前效果另存为预设...(&S)", self.parent_widget)
        save_as_preset_action.triggered.connect(lambda: self.save_as_preset_triggered.emit())
        presets_menu.addAction(save_as_preset_action)
        # 保存预设功能需要图像加载
        self._image_dependent_actions.append(save_as_preset_action)

        # 添加"删除预设"菜单项
        delete_preset_action = QAction("删除预设...(&D)", self.parent_widget)
        delete_preset_action.triggered.connect(lambda: self.delete_preset_triggered.emit())
        presets_menu.addAction(delete_preset_action)
        # 删除预设功能需要图像加载
        self._image_dependent_actions.append(delete_preset_action)

    def _create_tools_menu(self, menu_bar: QMenuBar):
        """创建工具菜单。"""
        tools_menu = menu_bar.addMenu("工具(&T)")
        assert tools_menu is not None, "QMenuBar.addMenu() should return a valid QMenu"
        
        # 添加代理图像质量设置子菜单
        self.proxy_quality_menu = QMenu("代理图像质量", self.parent_widget)
        tools_menu.addMenu(self.proxy_quality_menu)
        
        # 创建质量等级选项
        quality_levels = [
            ("极低 (最快)", 0.1),
            ("低", 0.25),
            ("中", 0.5),
            ("高", 0.75),
            ("极高 (最慢)", 1.0)
        ]
        
        # 添加质量等级菜单项
        for name, value in quality_levels:
            action = QAction(name, self.parent_widget)
            action.setCheckable(True)  # 使菜单项可选中
            action.setData(value)
            action.triggered.connect(lambda checked, v=value: self.set_proxy_quality_triggered.emit(v))
            self.proxy_quality_menu.addAction(action)
            self.proxy_quality_actions[value] = action  # 存储动作引用以便更新选中状态
            
        # 初始化选中状态
        self.update_proxy_quality_menu()
        
        # 添加分隔符
        tools_menu.addSeparator()
        




    def _create_point_op_menu(self, menu_bar: QMenuBar):
        """创建点运算菜单。"""
        point_op_menu = menu_bar.addMenu("点运算(&O)")
        assert point_op_menu is not None, "QMenuBar.addMenu() should return a valid QMenu"

        # 辅助函数，减少重复代码
        def add_dialog_action(text: str, op_id: str):
            action = QAction(text, self.parent_widget)
            action.triggered.connect(lambda: self.show_dialog_triggered.emit(op_id))
            point_op_menu.addAction(action)
            # 所有图像处理操作都需要图像加载
            self._image_dependent_actions.append(action)

        def add_simple_op_action(text: str, op_id: str):
            action = QAction(text, self.parent_widget)
            action.triggered.connect(lambda: self.apply_simple_operation_triggered.emit(op_id))
            point_op_menu.addAction(action)
            # 所有图像处理操作都需要图像加载
            self._image_dependent_actions.append(action)

        add_dialog_action("亮度/对比度...", "brightness_contrast")
        add_dialog_action("色彩平衡...", "color_balance")
        add_dialog_action("色相/饱和度...", "hue_saturation")
        add_dialog_action("曲线...", "curves")
        add_dialog_action("色阶...", "levels")
        point_op_menu.addSeparator()
        add_simple_op_action("灰度转换", "grayscale")
        add_simple_op_action("反相", "invert")
        point_op_menu.addSeparator()
        add_dialog_action("阈值...", "threshold")
        add_simple_op_action("大津法自动阈值", "otsu_threshold")
        add_simple_op_action("直方图均衡化", "histogram_equalization")

    def update_recent_files_menu(self, recent_files: list):
        """更新最近打开的文件菜单。"""
        # 清空菜单
        if self.recent_files_menu is not None:
            self.recent_files_menu.clear()
            
            # 如果没有最近的文件，添加一个禁用的项目
            if not recent_files:
                action = QAction("(无最近文件)", self.parent_widget)
                action.setEnabled(False)
                self.recent_files_menu.addAction(action)
                return
            
            # 添加最近的文件
            for file_path in recent_files:
                file_name = os.path.basename(file_path)
                action = QAction(file_name, self.parent_widget)
                action.setData(file_path)
                action.triggered.connect(lambda checked, path=file_path: self.open_recent_file_triggered.emit(path))
                self.recent_files_menu.addAction(action)
                
    def update_proxy_quality_menu(self):
        """更新代理图像质量菜单的选中状态"""
        if not self.proxy_quality_actions:
            return
            
        # 获取当前代理质量因子
        current_quality = 0.75  # 默认高质量
        if self.state_manager and hasattr(self.state_manager, 'get_proxy_quality'):
            current_quality = self.state_manager.get_proxy_quality()
            
        # 更新所有菜单项的选中状态
        for value, action in self.proxy_quality_actions.items():
            action.setChecked(abs(value - current_quality) < 0.01)  # 浮点数比较，使用近似值
    
    def _create_spatial_filtering_menu(self, menu_bar: QMenuBar):
        """创建空间滤波菜单。"""
        spatial_menu = menu_bar.addMenu("空间滤波(&S)")
        assert spatial_menu is not None, "QMenuBar.addMenu() should return a valid QMenu"

        # 辅助函数，减少重复代码
        def add_dialog_action(text: str, op_id: str):
            action = QAction(text, self.parent_widget)
            action.triggered.connect(lambda: self.show_dialog_triggered.emit(op_id))
            spatial_menu.addAction(action)
            # 所有图像处理操作都需要图像加载
            self._image_dependent_actions.append(action)
        
        add_dialog_action("高斯模糊...", "gaussian_blur")
        add_dialog_action("拉普拉斯边缘检测...", "laplacian_edge")
        add_dialog_action("Sobel边缘检测...", "sobel_edge")
        add_dialog_action("锐化滤波...", "sharpen")
        add_dialog_action("均值滤波...", "mean_filter")

    def _create_regular_filters_menu(self, menu_bar: QMenuBar):
        """创建常规滤镜菜单。"""
        regular_menu = menu_bar.addMenu("常规滤镜(&R)")
        assert regular_menu is not None, "QMenuBar.addMenu() should return a valid QMenu"

        # 辅助函数，减少重复代码
        def add_dialog_action(text: str, op_id: str):
            action = QAction(text, self.parent_widget)
            action.triggered.connect(lambda: self.show_dialog_triggered.emit(op_id))
            regular_menu.addAction(action)
            # 所有图像处理操作都需要图像加载
            self._image_dependent_actions.append(action)
        
        # 原有滤镜
        add_dialog_action("浮雕滤镜...", "emboss")
        add_dialog_action("马赛克滤镜...", "mosaic")
        add_dialog_action("油画滤镜...", "oil_painting")
        add_dialog_action("素描滤镜...", "sketch")
        add_dialog_action("怀旧滤镜...", "vintage")
        
        # 分隔符
        regular_menu.addSeparator()
        
        # 新增滤镜
        add_dialog_action("水彩画滤镜...", "watercolor")
        add_dialog_action("铅笔画滤镜...", "pencil_sketch")
        add_dialog_action("卡通化滤镜...", "cartoon")
        add_dialog_action("暖色调滤镜...", "warm_tone")
        add_dialog_action("冷色调滤镜...", "cool_tone")
        add_dialog_action("黑白胶片滤镜...", "film_grain")
        add_dialog_action("噪点滤镜...", "noise")
        add_dialog_action("磨砂玻璃滤镜...", "frosted_glass")
        add_dialog_action("织物纹理滤镜...", "fabric_texture")
        add_dialog_action("暗角滤镜...", "vignette")

    def _create_transform_menu(self, menu_bar: QMenuBar):
        """创建图像变换菜单。"""
        transform_menu = menu_bar.addMenu("图像变换(&I)")
        assert transform_menu is not None, "QMenuBar.addMenu() should return a valid QMenu"

        # 创建图像放大子菜单
        scale_up_menu = transform_menu.addMenu("图像放大")
        
        # 辅助函数，减少重复代码
        def add_scale_up_action(text: str, op_id: str):
            action = QAction(text, self.parent_widget)
            action.triggered.connect(lambda: self.show_dialog_triggered.emit(op_id))
            scale_up_menu.addAction(action)
            # 所有图像处理操作都需要图像加载
            self._image_dependent_actions.append(action)
        
        add_scale_up_action("最近邻放大...", "nearest_scale_up")
        add_scale_up_action("双线性放大...", "bilinear_scale_up")
        add_scale_up_action("双三次放大...", "bicubic_scale_up")
        add_scale_up_action("Lanczos放大...", "lanczos_scale_up")
        add_scale_up_action("边缘保持放大...", "edge_preserving_scale_up")

        # 创建图像缩小子菜单
        scale_down_menu = transform_menu.addMenu("图像缩小")
        
        def add_scale_down_action(text: str, op_id: str):
            action = QAction(text, self.parent_widget)
            action.triggered.connect(lambda: self.show_dialog_triggered.emit(op_id))
            scale_down_menu.addAction(action)
            # 所有图像处理操作都需要图像加载
            self._image_dependent_actions.append(action)
        
        add_scale_down_action("最近邻缩小...", "nearest_scale_down")
        add_scale_down_action("双线性缩小...", "bilinear_scale_down")
        add_scale_down_action("区域平均缩小...", "area_average_scale_down")
        add_scale_down_action("高斯缩小...", "gaussian_scale_down")
        add_scale_down_action("抗锯齿缩小...", "anti_alias_scale_down")

        # 创建图像压缩子菜单
        compression_menu = transform_menu.addMenu("图像压缩")
        
        def add_compression_action(text: str, op_id: str):
            action = QAction(text, self.parent_widget)
            action.triggered.connect(lambda: self.show_dialog_triggered.emit(op_id))
            compression_menu.addAction(action)
            # 所有图像处理操作都需要图像加载
            self._image_dependent_actions.append(action)
        
        add_compression_action("JPEG压缩...", "jpeg_compression")
        add_compression_action("PNG压缩...", "png_compression")
        add_compression_action("WebP压缩...", "webp_compression")
        add_compression_action("颜色量化...", "color_quantization")
        add_compression_action("智能优化...", "lossy_optimization")

    def _create_help_menu(self, menu_bar: QMenuBar):
        """创建帮助菜单"""
        help_menu = menu_bar.addMenu("帮助(&H)")
        assert help_menu is not None, "QMenuBar.addMenu() should return a valid QMenu"
        
        # 使用说明菜单项
        help_action = QAction("使用说明", self.parent_widget)
        help_action.setShortcut(QKeySequence("F1"))
        help_action.triggered.connect(lambda: self.help_triggered.emit())
        help_menu.addAction(help_action)

    def get_image_dependent_actions(self) -> List[QAction]:
        """
        获取所有依赖图像加载状态的菜单actions
        
        Returns:
            List[QAction]: 需要图像状态管理的actions列表
        """
        return self._image_dependent_actions.copy()  # 返回副本以防止外部修改
