"""调试依赖关系的脚本"""
from .dependency_analyzer import DependencyAnalyzer


def debug_specific_file(file_path: str):
    """调试特定文件的依赖关系"""
    analyzer = DependencyAnalyzer()
    
    print(f"分析文件: {file_path}")
    print(f"文件层级: {analyzer.get_file_layer(file_path)}")
    
    # 提取导入语句
    imports = analyzer.extract_imports(file_path)
    print(f"\n导入语句 ({len(imports)} 个):")
    for import_name, line_no, import_stmt in imports:
        resolved_file = analyzer.resolve_import_to_file(import_name, file_path)
        if resolved_file:
            target_layer = analyzer.get_file_layer(resolved_file)
            print(f"  {line_no:3d}: {import_stmt}")
            print(f"       -> {resolved_file} ({target_layer.value}层)")
        else:
            print(f"  {line_no:3d}: {import_stmt} (外部模块)")
    
    print()


def main():
    """主函数"""
    problem_files = [
        "app/core/initialization/direct_service_initializer.py",
        "app/core/dependency_injection/service_builder.py",
        "app/ui/main_window.py",
        "app/handlers/app_controller.py"
    ]
    
    for file_path in problem_files:
        try:
            debug_specific_file(file_path)
        except Exception as e:
            print(f"无法分析 {file_path}: {e}")
        print("-" * 60)


if __name__ == "__main__":
    main()