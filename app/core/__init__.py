"""
Core modules for the image processing application.
"""

# 核心接口 - 循环导入已解决
from .interfaces import *

# 核心抽象层 - 基础设施桥接接口
from .abstractions import *

# 引擎层 - 处理引擎（重构后使用业务层实现）
# ImageProcessor已迁移到业务层，避免循环导入
from .engines.image_analysis_engine import ImageAnalysisEngine

# 仓库层 - 数据访问
from .repositories.image_repository import ImageRepository

# 服务层 - 业务服务
from .services.persistence_service import PersistenceService

# 管理器层
from .managers.state_manager import StateManager

# 向后兼容导入（临时保留，计划在下个版本移除）
# 这些导入保证现有代码能继续工作
from .engines.image_analysis_engine import ImageAnalysisEngine as ImageAnalysisEngine

# ImageProcessor延迟导入函数，避免循环导入
def get_image_processor():
    """获取ImageProcessor实例，避免循环导入"""
    from app.layers.business.processing.image_processor import ImageProcessor
    return ImageProcessor

# 为了向后兼容，提供ImageProcessor的延迟导入
import sys
class ImageProcessorModule:
    def __getattr__(self, name):
        if name == 'ImageProcessor':
            from app.layers.business.processing.image_processor import ImageProcessor
            return ImageProcessor
        raise AttributeError(f"module has no attribute '{name}'")

# 将ImageProcessor作为模块属性提供
sys.modules[__name__ + '.ImageProcessor'] = ImageProcessorModule()

# 核心功能模块 - 已完成架构重组
