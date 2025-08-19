"""更新目录结构脚本"""
import os
import shutil
from pathlib import Path


def create_directory_structure():
    """创建新的分层目录结构"""
    base_path = Path("app/layers")
    
    # 定义目录结构
    directories = [
        # 应用层
        "application",
        
        # 表示层
        "presentation/interfaces",
        "presentation/windows", 
        "presentation/dialogs",
        "presentation/panels/batch",
        
        # 控制器层
        "controller/interfaces",
        
        # 业务层
        "business/interfaces",
        "business/processing",
        "business/state", 
        "business/events",
        "business/batch/interfaces",
        "business/batch/models",
        "business/batch/services",
        "business/batch/events",
        
        # 基础设施层
        "infrastructure/configuration",
        "infrastructure/filesystem",
        "infrastructure/logging",
        "infrastructure/batch/storage",
        "infrastructure/batch/workers",
    ]
    
    # 创建目录
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # 创建__init__.py文件
        init_file = dir_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text(f'"""{directory.split("/")[-1]}模块"""')
    
    print("目录结构创建完成")


def update_imports_in_file(file_path: Path, old_import: str, new_import: str):
    """更新文件中的导入语句"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_import in content:
            updated_content = content.replace(old_import, new_import)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"更新了 {file_path} 中的导入: {old_import} -> {new_import}")
    
    except Exception as e:
        print(f"更新文件 {file_path} 失败: {e}")


def update_imports():
    """更新导入语句"""
    # 定义需要更新的导入映射
    import_mappings = {
        "from app.core.engines.image_processor import": "from app.layers.business.processing.image_processor import",
        "from app.core.managers.state_manager import": "from app.layers.business.state.state_manager import",
        "from app.handlers.app_controller import": "from app.layers.controller.application_controller import",
        "from app.ui.main_window import": "from app.layers.presentation.windows.main_window import",
    }
    
    # 遍历所有Python文件
    for py_file in Path("app").rglob("*.py"):
        for old_import, new_import in import_mappings.items():
            update_imports_in_file(py_file, old_import, new_import)


def validate_structure():
    """验证目录结构"""
    required_paths = [
        "app/layers/application",
        "app/layers/presentation/windows",
        "app/layers/controller",
        "app/layers/business/processing",
        "app/layers/infrastructure/configuration",
        "app/layers/infrastructure/logging",
    ]
    
    missing_paths = []
    for path in required_paths:
        if not Path(path).exists():
            missing_paths.append(path)
    
    if missing_paths:
        print("缺少以下目录:")
        for path in missing_paths:
            print(f"  - {path}")
        return False
    else:
        print("目录结构验证通过")
        return True


def main():
    """主函数"""
    print("开始更新目录结构...")
    
    # 1. 创建新的目录结构
    create_directory_structure()
    
    # 2. 验证结构
    if validate_structure():
        print("目录结构更新完成")
    else:
        print("目录结构更新失败")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())