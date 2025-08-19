"""应用入口点"""
import sys
import os

# 抑制 Qt 警告
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false;qt.gui.*=false'

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QtMsgType, qInstallMessageHandler
from PyQt6.QtGui import QIcon
from app.application_startup import ApplicationStartup


def _qt_message_handler(mode, context, message):
    """过滤特定 Qt 警告"""
    if mode == QtMsgType.QtWarningMsg and message.startswith("QPainter"):
        return
    sys.__stderr__.write(message + "\n")


def main():
    """应用主入口"""
    qInstallMessageHandler(_qt_message_handler)
    app = QApplication(sys.argv)
    
    # 设置应用程序图标
    _set_application_icon(app)
    
    startup = ApplicationStartup(app)
    return startup.start_application()


def _set_application_icon(app: QApplication):
    """设置应用程序图标"""
    try:
        # 获取图标文件路径
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icons', 'LOGO.ico')
        
        # 检查图标文件是否存在
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            app.setWindowIcon(icon)
            print(f"应用程序图标设置成功: {icon_path}")
        else:
            print(f"警告: 应用程序图标文件不存在: {icon_path}")
    except Exception as e:
        print(f"设置应用程序图标时出错: {e}")


if __name__ == "__main__":
    sys.exit(main())