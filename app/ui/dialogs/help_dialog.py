"""
帮助对话框模块
"""
import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class HelpDialog(QDialog):
    """帮助对话框，显示使用说明文档"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用说明")
        self.setModal(True)
        self.resize(800, 600)
        self.setMinimumSize(600, 400)
        
        # 居中显示
        if parent:
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - 800) // 2
            y = parent_geometry.y() + (parent_geometry.height() - 600) // 2
            self.move(x, y)
        
        self._setup_ui()
        self._load_help_content()
    
    def _setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        
        # 创建文本浏览器
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False)
        
        # 设置字体
        font = QFont()
        font.setPointSize(10)
        self.text_browser.setFont(font)
        
        layout.addWidget(self.text_browser)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        close_button.setMinimumWidth(80)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _load_help_content(self):
        """加载帮助内容"""
        try:
            # 获取帮助文件路径
            help_file_path = self._get_help_file_path()
            
            if os.path.exists(help_file_path):
                with open(help_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_browser.setHtml(content)
            else:
                self._show_default_content()
                
        except Exception as e:
            self._show_error_content(str(e))
    
    def _get_help_file_path(self):
        """获取帮助文件路径"""
        # 获取当前文件所在目录的上级目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(os.path.dirname(current_dir))
        return os.path.join(app_dir, 'resources', 'help_content.html')
    
    def _show_default_content(self):
        """显示默认帮助内容"""
        default_content = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
                h2 { color: #34495e; margin-top: 25px; }
                ul { margin-left: 20px; }
                li { margin: 5px 0; }
                .section { margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <h1>数字图像处理工坊 - 使用说明</h1>
            
            <div class="section">
                <h2>软件简介</h2>
                <p>数字图像处理工坊是一款基于Python的图像处理软件，提供丰富的图像处理功能和实时预览效果。</p>

            </div>
            
            <div class="section">
                <h2>主要功能</h2>
                <ul>
                    <li><strong>文件操作</strong>：支持导入单个图像文件或整个文件夹</li>
                    <li><strong>点运算</strong>：亮度/对比度调整、色彩平衡、曲线、色阶等</li>
                    <li><strong>空间滤波</strong>：高斯模糊、边缘检测、锐化等</li>
                    <li><strong>常规滤镜</strong>：艺术效果滤镜，如油画、素描、怀旧等</li>
                    <li><strong>图像变换</strong>：缩放、压缩等</li>
                    <li><strong>预设管理</strong>：保存和应用处理效果预设</li>
                    <li><strong>数据分析</strong>：直方图、色彩空间分析等</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>基本操作</h2>
                <ol>
                    <li>使用左下角的图像仓库导入图像或文件夹</li>
                    <li>在右侧面板查看图像分析数据</li>
                    <li>通过各种处理菜单应用效果</li>
                    <li>实时预览处理结果</li>
                    <li>保存处理后的图像</li>
                </ol>
            </div>
            
            <div class="section">
                <h2>快捷键</h2>
                <ul>
                    <li><strong>Ctrl+O</strong>：打开文件</li>
                    <li><strong>Ctrl+Shift+O</strong>：导入文件夹</li>
                    <li><strong>Ctrl+S</strong>：保存文件</li>
                    <li><strong>Ctrl+Z</strong>：撤销</li>
                    <li><strong>Ctrl+Y</strong>：重做</li>
                    <li><strong>Ctrl+Shift+C</strong>：清除所有效果</li>
                    <li><strong>F1</strong>：显示帮助</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>使用提示</h2>
                <ul>
                    <li>大多数处理操作支持实时预览，调整参数时可即时查看效果</li>
                    <li>可以通过"预设"菜单保存常用的处理效果组合</li>
                    <li>支持拖拽文件到窗口直接打开图像</li>
                    <li>在"工具"菜单中可调整预览质量以平衡性能和效果</li>
                </ul>
            </div>
        </body>
        </html>
        """
        self.text_browser.setHtml(default_content)
    
    def _show_error_content(self, error_msg):
        """显示错误内容"""
        error_content = f"""
        <html>
        <body>
            <h2>加载帮助内容时出错</h2>
            <p>无法加载帮助文档，错误信息：{error_msg}</p>
            <p>请联系技术支持或查看软件文档。</p>
        </body>
        </html>
        """
        self.text_browser.setHtml(error_content)