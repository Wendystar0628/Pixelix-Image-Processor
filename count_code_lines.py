#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码行数统计脚本
统计指定目录下所有Python文件的有效代码行数（排除空行和注释行）
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class CodeLineCounter:
    """代码行数统计器"""
    
    def __init__(self):
        # 匹配注释行的正则表达式
        self.comment_patterns = [
            re.compile(r'^\s*#.*$'),  # 单行注释
            re.compile(r'^\s*""".*"""\s*$'),  # 单行三引号注释
            re.compile(r"^\s*'''.*'''\s*$"),  # 单行三引号注释
        ]
        
        # 多行注释状态
        self.in_multiline_comment = False
        self.multiline_quote_type = None
    
    def is_empty_line(self, line: str) -> bool:
        """判断是否为空行"""
        return line.strip() == ''
    
    def is_comment_line(self, line: str) -> bool:
        """判断是否为注释行"""
        stripped_line = line.strip()
        
        # 检查多行注释状态
        if self.in_multiline_comment:
            if ('"""' in stripped_line and self.multiline_quote_type == '"""') or \
               ("'''" in stripped_line and self.multiline_quote_type == "'''"):
                self.in_multiline_comment = False
                self.multiline_quote_type = None
            return True
        
        # 检查多行注释开始
        if stripped_line.startswith('"""') and not stripped_line.endswith('"""'):
            self.in_multiline_comment = True
            self.multiline_quote_type = '"""'
            return True
        elif stripped_line.startswith("'''") and not stripped_line.endswith("'''"):
            self.in_multiline_comment = True
            self.multiline_quote_type = "'''"
            return True
        
        # 检查单行注释
        for pattern in self.comment_patterns:
            if pattern.match(line):
                return True
        
        # 检查行内注释（但不是字符串中的#）
        if '#' in stripped_line:
            # 简单检查：如果#前面没有引号，认为是注释
            hash_pos = stripped_line.find('#')
            before_hash = stripped_line[:hash_pos]
            # 简单判断：如果#前面的引号数量是偶数，则#是注释
            single_quotes = before_hash.count("'")
            double_quotes = before_hash.count('"')
            if single_quotes % 2 == 0 and double_quotes % 2 == 0:
                return stripped_line[:hash_pos].strip() == ''
        
        return False
    
    def count_file_lines(self, file_path: Path) -> Tuple[int, int, int]:
        """统计单个文件的行数
        
        Returns:
            Tuple[int, int, int]: (总行数, 有效代码行数, 注释和空行数)
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return 0, 0, 0
        
        # 重置多行注释状态
        self.in_multiline_comment = False
        self.multiline_quote_type = None
        
        total_lines = len(lines)
        effective_lines = 0
        
        for line in lines:
            if not self.is_empty_line(line) and not self.is_comment_line(line):
                effective_lines += 1
        
        non_effective_lines = total_lines - effective_lines
        return total_lines, effective_lines, non_effective_lines
    
    def count_directory_lines(self, directory: Path, file_extensions: List[str] = None) -> Dict[str, any]:
        """统计目录下所有指定扩展名文件的行数
        
        Args:
            directory: 目标目录
            file_extensions: 文件扩展名列表，默认为['.py']
        
        Returns:
            Dict: 统计结果
        """
        if file_extensions is None:
            file_extensions = ['.py']
        
        results = {
            'total_files': 0,
            'total_lines': 0,
            'effective_lines': 0,
            'non_effective_lines': 0,
            'file_details': []
        }
        
        # 递归遍历目录
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in file_extensions:
                total, effective, non_effective = self.count_file_lines(file_path)
                
                results['total_files'] += 1
                results['total_lines'] += total
                results['effective_lines'] += effective
                results['non_effective_lines'] += non_effective
                
                # 记录文件详情
                relative_path = file_path.relative_to(directory)
                results['file_details'].append({
                    'file': str(relative_path),
                    'total_lines': total,
                    'effective_lines': effective,
                    'non_effective_lines': non_effective
                })
        
        return results
    
    def print_results(self, results: Dict[str, any], show_details: bool = False):
        """打印统计结果"""
        print("\n" + "="*60)
        print("代码行数统计结果")
        print("="*60)
        print(f"统计文件数量: {results['total_files']}")
        print(f"总行数: {results['total_lines']}")
        print(f"有效代码行数: {results['effective_lines']}")
        print(f"注释和空行数: {results['non_effective_lines']}")
        
        if results['total_lines'] > 0:
            effective_ratio = (results['effective_lines'] / results['total_lines']) * 100
            print(f"有效代码比例: {effective_ratio:.1f}%")
        
        if show_details and results['file_details']:
            print("\n" + "-"*60)
            print("文件详情:")
            print("-"*60)
            print(f"{'文件路径':<40} {'总行数':<8} {'有效行数':<8} {'注释/空行':<10}")
            print("-"*60)
            
            # 按有效行数排序
            sorted_files = sorted(results['file_details'], 
                                key=lambda x: x['effective_lines'], 
                                reverse=True)
            
            for file_info in sorted_files:
                print(f"{file_info['file']:<40} {file_info['total_lines']:<8} "
                      f"{file_info['effective_lines']:<8} {file_info['non_effective_lines']:<10}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='统计代码行数')
    parser.add_argument('path', nargs='?', default='.', 
                       help='要统计的文件或目录路径（默认为当前目录）')
    parser.add_argument('--extensions', '-e', nargs='+', default=['.py'],
                       help='要统计的文件扩展名（默认为.py）')
    parser.add_argument('--details', '-d', action='store_true',
                       help='显示每个文件的详细信息')
    
    args = parser.parse_args()
    
    path = Path(args.path).resolve()
    
    if not path.exists():
        print(f"错误: 路径 '{path}' 不存在")
        return 1
    
    counter = CodeLineCounter()
    
    if path.is_file():
        # 统计单个文件
        if path.suffix not in args.extensions:
            print(f"警告: 文件扩展名 '{path.suffix}' 不在指定的扩展名列表中")
            print(f"指定的扩展名: {', '.join(args.extensions)}")
            return 1
        
        print(f"正在统计文件: {path}")
        total, effective, non_effective = counter.count_file_lines(path)
        
        print("\n" + "="*60)
        print("单文件代码行数统计结果")
        print("="*60)
        print(f"文件路径: {path}")
        print(f"总行数: {total}")
        print(f"有效代码行数: {effective}")
        print(f"注释和空行数: {non_effective}")
        
        if total > 0:
            effective_ratio = (effective / total) * 100
            print(f"有效代码比例: {effective_ratio:.1f}%")
    
    elif path.is_dir():
        # 统计目录
        print(f"正在统计目录: {path}")
        print(f"文件扩展名: {', '.join(args.extensions)}")
        
        results = counter.count_directory_lines(path, args.extensions)
        counter.print_results(results, args.details)
    
    else:
        print(f"错误: '{path}' 既不是文件也不是目录")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())