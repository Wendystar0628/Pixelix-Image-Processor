"""架构合规性检查器"""
import os
from typing import List, Dict
from .dependency_analyzer import DependencyAnalyzer
from .violation_models import (
    ArchitectureViolation, CircularDependency, InterfaceViolation,
    ArchitectureReport, ViolationType
)


class ArchitectureComplianceChecker:
    """架构合规性检查器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.analyzer = DependencyAnalyzer(project_root)
    
    def check_dependencies(self) -> List[ArchitectureViolation]:
        """检查依赖关系违反"""
        # 构建依赖关系图
        self.analyzer.build_dependency_graph()
        
        # 查找向上依赖
        upward_violations = self.analyzer.find_upward_dependencies()
        
        return upward_violations
    
    def detect_violations(self) -> List[ArchitectureViolation]:
        """检测所有架构违反"""
        violations = []
        
        # 检查依赖关系违反
        dependency_violations = self.check_dependencies()
        violations.extend(dependency_violations)
        
        # 检查跨层依赖（跳过中间层的依赖）
        cross_layer_violations = self._check_cross_layer_dependencies()
        violations.extend(cross_layer_violations)
        
        return violations
    
    def detect_circular_dependencies(self) -> List[CircularDependency]:
        """检测循环依赖"""
        cycles = self.analyzer.find_circular_dependencies()
        circular_deps = []
        
        for cycle in cycles:
            if len(cycle) > 1:  # 过滤掉自循环
                circular_dep = CircularDependency(
                    cycle_path=cycle,
                    cycle_length=len(cycle) - 1,  # 减去重复的起始节点
                    description=f"检测到循环依赖: {' -> '.join(cycle)}",
                    affected_files=list(set(cycle))
                )
                circular_deps.append(circular_dep)
        
        return circular_deps
    
    def check_interface_compliance(self) -> List[InterfaceViolation]:
        """检查接口合规性"""
        # 这里可以实现接口合规性检查
        # 暂时返回空列表
        return []
    
    def _check_cross_layer_dependencies(self) -> List[ArchitectureViolation]:
        """检查跨层依赖违反"""
        violations = []
        
        # 定义不允许的跨层依赖
        forbidden_dependencies = [
            # UI层不应该直接依赖业务层（应该通过控制器）
            ("presentation", "business"),
            # 应用层不应该直接依赖表示层
            ("application", "presentation"),
            # 业务层不应该直接依赖控制器层
            ("business", "controller"),
        ]
        
        for source_file, deps in self.analyzer.dependencies.items():
            source_layer = self.analyzer.get_file_layer(source_file)
            
            for target_file in deps:
                target_layer = self.analyzer.get_file_layer(target_file)
                
                # 检查是否存在禁止的跨层依赖
                layer_pair = (source_layer.value, target_layer.value)
                if layer_pair in forbidden_dependencies:
                    # 获取具体的导入语句
                    imports = self.analyzer.extract_imports(source_file)
                    for import_name, line_no, import_stmt in imports:
                        resolved_file = self.analyzer.resolve_import_to_file(import_name)
                        if resolved_file == target_file:
                            violation = ArchitectureViolation(
                                violation_type=ViolationType.CROSS_LAYER_DEPENDENCY,
                                source_file=source_file,
                                target_file=target_file,
                                source_layer=source_layer,
                                target_layer=target_layer,
                                line_number=line_no,
                                import_statement=import_stmt,
                                severity="warning",
                                description=f"{source_layer.value}层不应该跨层依赖{target_layer.value}层",
                                suggestion="考虑通过中间层或接口来访问目标功能"
                            )
                            violations.append(violation)
                            break
        
        return violations
    
    def generate_report(self) -> ArchitectureReport:
        """生成架构检查报告"""
        violations = self.detect_violations()
        circular_deps = self.detect_circular_dependencies()
        interface_violations = self.check_interface_compliance()
        
        # 统计信息
        error_count = sum(1 for v in violations if v.severity == "error")
        warning_count = sum(1 for v in violations if v.severity == "warning")
        total_violations = len(violations) + len(circular_deps) + len(interface_violations)
        
        # 判断是否合规
        is_compliant = error_count == 0 and len(circular_deps) == 0
        
        return ArchitectureReport(
            violations=violations,
            circular_dependencies=circular_deps,
            interface_violations=interface_violations,
            total_files_checked=len(self.analyzer.dependencies),
            violation_count=total_violations,
            error_count=error_count,
            warning_count=warning_count,
            is_compliant=is_compliant
        )
    
    def check_all_violations(self) -> List[ArchitectureViolation]:
        """检查所有违反（用于测试）"""
        return self.detect_violations()


def main():
    """命令行入口"""
    checker = ArchitectureComplianceChecker()
    report = checker.generate_report()
    
    print("=" * 60)
    print("架构合规性检查报告")
    print("=" * 60)
    print(f"检查文件数: {report.total_files_checked}")
    print(f"违反总数: {report.violation_count}")
    print(f"错误数: {report.error_count}")
    print(f"警告数: {report.warning_count}")
    print(f"是否合规: {'是' if report.is_compliant else '否'}")
    print()
    
    if report.violations:
        print("依赖关系违反:")
        print("-" * 40)
        for violation in report.violations:
            print(f"[{violation.severity.upper()}] {violation.source_file}:{violation.line_number}")
            print(f"  {violation.description}")
            print(f"  导入语句: {violation.import_statement}")
            if violation.suggestion:
                print(f"  建议: {violation.suggestion}")
            print()
    
    if report.circular_dependencies:
        print("循环依赖:")
        print("-" * 40)
        for circular_dep in report.circular_dependencies:
            print(f"循环长度: {circular_dep.cycle_length}")
            print(f"循环路径: {circular_dep.description}")
            print()
    
    return 0 if report.is_compliant else 1


if __name__ == "__main__":
    exit(main())