"""依赖关系分析器"""
import os
import ast
import re
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
from .violation_models import LayerType, ArchitectureViolation, ViolationType


class DependencyAnalyzer:
    """依赖关系分析器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.layer_mapping = self._build_layer_mapping()
        self.dependencies: Dict[str, Set[str]] = {}
    
    def _build_layer_mapping(self) -> Dict[str, LayerType]:
        """构建文件路径到层级的映射"""
        mapping = {}
        
        # 新的分层架构映射
        layer_patterns = {
            LayerType.APPLICATION: [
                r"app/layers/application/.*",
                r"app/main\.py",
                r"app/application_startup\.py"
            ],
            LayerType.PRESENTATION: [
                r"app/layers/presentation/.*",
                r"app/ui/.*"  # 兼容旧UI结构
            ],
            LayerType.CONTROLLER: [
                r"app/layers/controller/.*",
                r"app/handlers/.*"  # 兼容旧handlers结构
            ],
            LayerType.BUSINESS: [
                r"app/layers/business/.*",
                r"app/core/.*",  # 兼容旧core结构
                r"app/features/.*"  # 兼容旧features结构
            ],
            LayerType.INFRASTRUCTURE: [
                r"app/layers/infrastructure/.*",
                r"app/infrastructure/.*"  # 兼容旧infrastructure结构
            ],
            LayerType.SHARED: [
                r"app/shared/.*",
                r"app/utils/.*",
                r"app/models/.*"
            ],
            LayerType.LEGACY: [
                r"app/workers/.*",
                r"app/presets/.*"
            ]
        }
        
        return layer_patterns
    
    def get_file_layer(self, file_path: str) -> LayerType:
        """获取文件所属的层级"""
        normalized_path = file_path.replace("\\", "/")
        
        for layer, patterns in self.layer_mapping.items():
            for pattern in patterns:
                if re.match(pattern, normalized_path):
                    return layer
        
        return LayerType.LEGACY  # 默认为遗留层
    
    def extract_imports(self, file_path: str) -> List[Tuple[str, int, str]]:
        """提取文件中的导入语句"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append((alias.name, node.lineno, f"import {alias.name}"))
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module
                        for alias in node.names:
                            if alias.name == "*":
                                import_name = module
                                import_stmt = f"from {module} import *"
                            else:
                                import_name = module  # 只使用模块名，不包含具体导入的类/函数
                                import_stmt = f"from {module} import {alias.name}"
                            imports.append((import_name, node.lineno, import_stmt))
        
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError) as e:
            print(f"无法解析文件 {file_path}: {e}")
        
        return imports
    
    def resolve_import_to_file(self, import_name: str, current_file: str = None) -> Optional[str]:
        """将导入名称解析为文件路径"""
        # 处理相对导入
        if not import_name.startswith('app.') and current_file:
            # 相对导入，需要基于当前文件路径解析
            current_dir = os.path.dirname(current_file)
            
            # 尝试在当前目录查找
            possible_paths = [
                os.path.join(current_dir, import_name + ".py"),
                os.path.join(current_dir, import_name, "__init__.py")
            ]
            
            for path in possible_paths:
                full_path = self.project_root / path
                if full_path.exists():
                    return str(path).replace("\\", "/")
        
        # 只处理app模块的绝对导入
        if not import_name.startswith('app.'):
            return None
        
        # 转换导入路径为文件路径
        parts = import_name.split('.')
        
        # 尝试不同的文件扩展名
        possible_paths = [
            os.path.join(*parts) + ".py",
            os.path.join(*parts, "__init__.py")
        ]
        
        for path in possible_paths:
            full_path = self.project_root / path
            if full_path.exists():
                return str(path).replace("\\", "/")
        
        return None
    
    def analyze_file_dependencies(self, file_path: str) -> Set[str]:
        """分析单个文件的依赖关系"""
        dependencies = set()
        imports = self.extract_imports(file_path)
        
        for import_name, _, _ in imports:
            target_file = self.resolve_import_to_file(import_name, file_path)
            if target_file:
                dependencies.add(target_file)
        
        return dependencies
    
    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """构建整个项目的依赖关系图"""
        dependencies = {}
        
        # 遍历所有Python文件
        for py_file in self.project_root.rglob("*.py"):
            if "test" in str(py_file) or "__pycache__" in str(py_file):
                continue
            
            relative_path = str(py_file.relative_to(self.project_root)).replace("\\", "/")
            file_deps = self.analyze_file_dependencies(str(py_file))
            dependencies[relative_path] = file_deps
        
        self.dependencies = dependencies
        return dependencies
    
    def find_upward_dependencies(self) -> List[ArchitectureViolation]:
        """查找向上依赖违反"""
        violations = []
        
        # 定义层级顺序（数字越大层级越高）
        layer_hierarchy = {
            LayerType.INFRASTRUCTURE: 0,
            LayerType.SHARED: 1,
            LayerType.BUSINESS: 2,
            LayerType.CONTROLLER: 3,
            LayerType.PRESENTATION: 4,
            LayerType.APPLICATION: 5,
            LayerType.LEGACY: 6
        }
        
        for source_file, deps in self.dependencies.items():
            source_layer = self.get_file_layer(source_file)
            source_level = layer_hierarchy.get(source_layer, 999)
            
            for target_file in deps:
                target_layer = self.get_file_layer(target_file)
                target_level = layer_hierarchy.get(target_layer, 999)
                
                # 检查是否存在向上依赖
                if source_level < target_level:
                    # 获取具体的导入语句
                    imports = self.extract_imports(source_file)
                    for import_name, line_no, import_stmt in imports:
                        resolved_file = self.resolve_import_to_file(import_name)
                        if resolved_file == target_file:
                            violation = ArchitectureViolation(
                                violation_type=ViolationType.UPWARD_DEPENDENCY,
                                source_file=source_file,
                                target_file=target_file,
                                source_layer=source_layer,
                                target_layer=target_layer,
                                line_number=line_no,
                                import_statement=import_stmt,
                                severity="error",
                                description=f"{source_layer.value}层不应该依赖{target_layer.value}层",
                                suggestion=f"考虑使用事件机制或依赖注入来消除向上依赖"
                            )
                            violations.append(violation)
                            break
        
        return violations
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """查找循环依赖"""
        def dfs(node: str, path: List[str], visited: Set[str], rec_stack: Set[str]) -> List[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            cycles = []
            
            for neighbor in self.dependencies.get(node, set()):
                if neighbor not in visited:
                    cycles.extend(dfs(neighbor, path.copy(), visited, rec_stack))
                elif neighbor in rec_stack:
                    # 找到循环
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.remove(node)
            return cycles
        
        all_cycles = []
        visited = set()
        
        for node in self.dependencies:
            if node not in visited:
                cycles = dfs(node, [], visited, set())
                all_cycles.extend(cycles)
        
        return all_cycles