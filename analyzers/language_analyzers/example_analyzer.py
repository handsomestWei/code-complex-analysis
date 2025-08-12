#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例语言分析器，插件化设计
"""

from pathlib import Path
from typing import Dict, Any, List

class ExampleLanguageAnalyzer:
    """示例语言分析器类"""

    # 声明支持的文件扩展名
    supported_extensions = ['.example', '.ex', '.exm']

    # 声明阈值系数（可选）
    threshold_coefficient = 25  # 脚本语言，复杂度较低

    # 声明默认阈值（可选）
    default_thresholds = {
        'low': 3,
        'medium': 10,
        'high': 20,
        'very_high': 40
    }

    def can_handle_file(self, file_path: Path) -> bool:
        """
        智能判断是否能处理指定文件

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否能处理该文件
        """
        # 方法1: 通过文件扩展名判断
        if file_path.suffix.lower() in self.supported_extensions:
            return True

        # 方法2: 通过文件内容判断（更智能的方式）
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()
                # 检查文件头部是否有特定的标识符
                if first_line.startswith('#!') and 'example' in first_line.lower():
                    return True
                # 检查文件内容是否包含特定的关键字
                content = f.read(1000)  # 读取前1000个字符
                if 'example_language' in content.lower() or 'example_syntax' in content.lower():
                    return True
        except Exception:
            pass

        return False

    def get_threshold_coefficient(self) -> int:
        """获取阈值系数（可选方法）"""
        return self.threshold_coefficient

    def get_default_thresholds(self) -> Dict[str, int]:
        """获取默认阈值（可选方法）"""
        return self.default_thresholds.copy()

    def analyze_complexity_detailed(self, file_path: Path) -> Dict[str, Any]:
        """
        分析文件复杂度

        Args:
            file_path: 文件路径

        Returns:
            Dict: 复杂度分析结果
        """
        result = {
            'lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'complexity': 0,
            'nested_levels': 0,
            'max_nested_level': 0,
            'file_type': 'example',
            'analyzer_used': 'example'
        }

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            result['lines'] = len(lines)
            current_nested_level = 0

            for line in lines:
                line = line.strip()

                # 跳过空行
                if not line:
                    result['blank_lines'] += 1
                    continue

                # 跳过注释行
                if line.startswith('#') or line.startswith('//'):
                    result['comment_lines'] += 1
                    continue

                # 统计代码行
                result['code_lines'] += 1

                # 统计嵌套层级（示例语言的特定语法）
                if '{' in line or '[' in line or '(' in line:
                    current_nested_level += 1
                    result['max_nested_level'] = max(result['max_nested_level'], current_nested_level)
                if '}' in line or ']' in line or ')' in line:
                    current_nested_level = max(0, current_nested_level - 1)

                # 计算复杂度（示例语言的特定关键字）
                complexity_keywords = [
                    'if', 'else', 'for', 'while', 'do', 'switch', 'case',
                    'example_if', 'example_loop', 'example_switch',
                    '&&', '||', '?', ':', 'break', 'continue'
                ]
                for keyword in complexity_keywords:
                    if keyword in line:
                        result['complexity'] += 1

            result['nested_levels'] = result['max_nested_level']

        except Exception as e:
            result['error'] = f"分析文件失败: {str(e)}"

        return result


# 为了兼容性，也可以直接提供函数接口
def analyze_example_complexity_detailed(file_path: Path) -> Dict[str, Any]:
    """示例语言复杂度分析函数接口"""
    analyzer = ExampleLanguageAnalyzer()
    return analyzer.analyze_complexity_detailed(file_path)


# 导出分析器类，供语言分析器管理器使用
__all__ = ['ExampleLanguageAnalyzer', 'analyze_example_complexity_detailed']
