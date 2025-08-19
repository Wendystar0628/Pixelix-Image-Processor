"""专门检查架构违反的脚本"""
import os
from .compliance_checker import ArchitectureComplianceChecker


def check_specific_violations():
    """检查特定的架构违反"""
    checker = ArchitectureComplianceChecker()
    
    print("正在分析项目依赖关系...")
    checker.analyzer.build_dependency_graph()
    
    print("检查核心层向上依赖...")
    upward_violations = checker.analyzer.find_upward_dependencies()
    
    print("检查循环依赖...")
    circular_deps = checker.detect_circular_dependencies()
    
    print("\n" + "="*60)
    print("架构违反详细报告")
    print("="*60)
    
    if upward_violations:
        print(f"\n发现 {len(upward_violations)} 个向上依赖违反:")
        print("-" * 40)
        for i, violation in enumerate(upward_violations, 1):
            print(f"{i}. {violation.source_file}:{violation.line_number}")
            print(f"   {violation.source_layer.value} -> {violation.target_layer.value}")
            print(f"   导入: {violation.import_statement}")
            print(f"   问题: {violation.description}")
            if violation.suggestion:
                print(f"   建议: {violation.suggestion}")
            print()
    else:
        print("\n✓ 未发现向上依赖违反")
    
    if circular_deps:
        print(f"\n发现 {len(circular_deps)} 个循环依赖:")
        print("-" * 40)
        for i, circular_dep in enumerate(circular_deps, 1):
            print(f"{i}. 循环长度: {circular_dep.cycle_length}")
            print(f"   路径: {' -> '.join(circular_dep.cycle_path)}")
            print()
    else:
        print("\n✓ 未发现循环依赖")
    
    # 检查特定的问题文件
    print("\n检查已知问题文件:")
    print("-" * 40)
    
    problem_files = [
        "app/core/initialization/direct_service_initializer.py",
        "app/core/dependency_injection/service_builder.py",
        "app/ui/main_window.py",
        "app/handlers/app_controller.py"
    ]
    
    for file_path in problem_files:
        if file_path in checker.analyzer.dependencies:
            deps = checker.analyzer.dependencies[file_path]
            layer = checker.analyzer.get_file_layer(file_path)
            
            print(f"\n{file_path} ({layer.value}层):")
            
            # 检查是否有向上依赖
            has_upward_deps = False
            for dep in deps:
                dep_layer = checker.analyzer.get_file_layer(dep)
                if _is_upward_dependency(layer, dep_layer):
                    print(f"  ⚠️  向上依赖: {dep} ({dep_layer.value}层)")
                    has_upward_deps = True
            
            if not has_upward_deps:
                print(f"  ✓ 无向上依赖问题")
        else:
            print(f"\n{file_path}: 文件不存在或无法分析")
    
    return len(upward_violations) + len(circular_deps)


def _is_upward_dependency(source_layer, target_layer):
    """判断是否为向上依赖"""
    from .violation_models import LayerType
    
    layer_hierarchy = {
        LayerType.INFRASTRUCTURE: 0,
        LayerType.SHARED: 1,
        LayerType.BUSINESS: 2,
        LayerType.CONTROLLER: 3,
        LayerType.PRESENTATION: 4,
        LayerType.APPLICATION: 5,
        LayerType.LEGACY: 6
    }
    
    source_level = layer_hierarchy.get(source_layer, 999)
    target_level = layer_hierarchy.get(target_layer, 999)
    
    return source_level < target_level


if __name__ == "__main__":
    violation_count = check_specific_violations()
    print(f"\n总违反数: {violation_count}")
    exit(0 if violation_count == 0 else 1)