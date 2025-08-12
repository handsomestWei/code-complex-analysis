#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript代码复杂度分析器
专门分析JavaScript代码的复杂度、结构和质量指标
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
import logging
from ..language_analyzer_manager import LanguageAnalyzer

logger = logging.getLogger(__name__)


class JavaScriptAnalyzer(LanguageAnalyzer):
    """JavaScript语言分析器"""

    @property
    def language_name(self) -> str:
        return "javascript"

    @property
    def file_extensions(self) -> List[str]:
        return ['.js', '.jsx']

    @property
    def analyzer_name(self) -> str:
        return "JavaScript复杂度分析器"

    def can_analyze(self, file_path: Path) -> bool:
        """检查是否可以分析此文件"""
        if not file_path.exists() or not file_path.is_file():
            return False

        # 检查文件大小
        try:
            file_size = file_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB
                return False
        except OSError:
            return False

        # 检查文件扩展名
        return file_path.suffix.lower() in ['.js', '.jsx']

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """分析JavaScript文件复杂度"""
        return analyze_javascript_complexity_detailed(file_path)


def analyze_javascript_complexity_detailed(file_path: Path) -> Dict[str, Any]:
    """详细分析JavaScript代码复杂度"""
    result = {
        'file_path': str(file_path),
        'file_type': 'javascript',
        'lines': 0,
        'code_lines': 0,
        'comment_lines': 0,
        'blank_lines': 0,
        'classes': 0,
        'functions': 0,
        'methods': 0,
        'imports': 0,
        'exports': 0,
        'variables': 0,
        'complexity': 0,
        'nested_levels': 0,
        'max_nested_level': 0,
        'class_details': [],
        'function_details': [],
        'method_details': [],
        'code_smells': []
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        result['lines'] = len(lines)
        in_multiline_comment = False
        current_nested_level = 0
        current_class = None
        current_function = None

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # 跳过空行
            if not line:
                result['blank_lines'] += 1
                continue

            # 处理多行注释
            if '/*' in line and '*/' not in line:
                in_multiline_comment = True
                result['comment_lines'] += 1
                continue
            elif '*/' in line:
                in_multiline_comment = False
                result['comment_lines'] += 1
                continue
            elif in_multiline_comment:
                result['comment_lines'] += 1
                continue

            # 单行注释
            if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                result['comment_lines'] += 1
                continue

            # 统计代码行
            result['code_lines'] += 1

            # 检测imports
            if line.startswith('import '):
                result['imports'] += 1

            # 检测exports
            if line.startswith('export ') or 'export default' in line:
                result['exports'] += 1

            # 检测变量声明
            if re.search(r'\b(const|let|var)\s+\w+', line):
                result['variables'] += 1

            # 统计类
            class_match = re.search(r'\b(export\s+)?class\s+(\w+)', line)
            if class_match:
                result['classes'] += 1
                class_name = class_match.group(2)
                modifiers = []
                if 'export' in line: modifiers.append('export')

                current_class = {
                    'name': class_name,
                    'modifiers': modifiers,
                    'line': line_num,
                    'nested_level': current_nested_level
                }
                result['class_details'].append(current_class)

            # 统计函数
            function_match = re.search(r'\b(export\s+)?(function|const|let)\s+(\w+)', line)
            if function_match:
                result['functions'] += 1
                function_name = function_match.group(3)
                result['function_details'].append({
                    'name': function_name,
                    'line': line_num,
                    'type': 'function',
                    'class': current_class['name'] if current_class else None
                })

            # 统计方法（类内的函数）
            method_match = re.search(r'\b(\w+)\s*\([^)]*\)\s*[:{=]', line)
            if current_class and method_match and not line.startswith('if') and not line.startswith('for'):
                result['methods'] += 1
                method_name = method_match.group(1)
                result['method_details'].append({
                    'name': method_name,
                    'line': line_num,
                    'type': 'method',
                    'class': current_class['name']
                })

            # 统计嵌套级别
            if '{' in line:
                current_nested_level += 1
                result['max_nested_level'] = max(result['max_nested_level'], current_nested_level)
            if '}' in line:
                current_nested_level = max(0, current_nested_level - 1)

        # 计算复杂度
        result['complexity'] = _calculate_javascript_complexity(result)

        # 检测代码异味
        result['code_smells'] = _detect_javascript_code_smells(result)

        # 添加圈复杂度
        result['cyclomatic_complexity'] = result['complexity']

    except Exception as e:
        logger.error(f"分析JavaScript文件失败 {file_path}: {e}")
        result['error'] = f"分析失败: {str(e)}"

    return result


def _calculate_javascript_complexity(analysis_result: Dict[str, Any]) -> int:
    """计算JavaScript代码复杂度"""
    complexity = 1  # 基础复杂度

    # 基于类和方法数量
    complexity += analysis_result['classes'] * 2
    complexity += analysis_result['methods'] * 3
    complexity += analysis_result['functions'] * 2

    # 基于嵌套级别
    complexity += analysis_result['max_nested_level'] * 2

    # 基于imports数量
    complexity += analysis_result['imports'] // 5

    # 基于变量数量
    complexity += analysis_result['variables'] // 10

    return complexity


def _detect_javascript_code_smells(analysis_result: Dict[str, Any]) -> List[str]:
    """检测JavaScript代码异味"""
    smells = []

    # 检查类数量过多
    if analysis_result['classes'] > 10:
        smells.append("类数量过多，可能存在职责分散问题")

    # 检查函数数量过多
    if analysis_result['functions'] > 50:
        smells.append("函数数量过多，可能存在职责分散问题")

    # 检查嵌套级别过深
    if analysis_result['max_nested_level'] > 5:
        smells.append("嵌套级别过深，可能存在可读性问题")

    # 检查imports过多
    if analysis_result['imports'] > 30:
        smells.append("依赖过多，可能存在耦合问题")

    # 检查变量数量过多
    if analysis_result['variables'] > 100:
        smells.append("变量数量过多，可能存在作用域混乱问题")

    return smells


def analyze_javascript_architecture(file_path: Path) -> Dict[str, Any]:
    """分析JavaScript代码架构"""
    complexity_result = analyze_javascript_complexity_detailed(file_path)

    if 'error' in complexity_result:
        return complexity_result

    architecture_result = {
        'file_path': str(file_path),
        'architecture_type': 'unknown',
        'design_patterns': [],
        'coupling_level': 'low',
        'cohesion_level': 'high',
        'recommendations': []
    }

    # 分析架构类型
    if complexity_result['classes'] == 0:
        architecture_result['architecture_type'] = 'procedural'
    elif complexity_result['classes'] <= 3:
        architecture_result['architecture_type'] = 'simple_oop'
    elif complexity_result['classes'] <= 8:
        architecture_result['architecture_type'] = 'moderate_oop'
    else:
        architecture_result['architecture_type'] = 'complex_oop'

    # 分析耦合度
    if complexity_result['imports'] <= 10:
        architecture_result['coupling_level'] = 'low'
    elif complexity_result['imports'] <= 20:
        architecture_result['coupling_level'] = 'medium'
    else:
        architecture_result['coupling_level'] = 'high'

    # 分析内聚度
    total_methods = complexity_result['methods'] + complexity_result['functions']
    if total_methods <= 5:
        architecture_result['cohesion_level'] = 'high'
    elif total_methods <= 15:
        architecture_result['cohesion_level'] = 'medium'
    else:
        architecture_result['cohesion_level'] = 'low'

    # 生成建议
    if architecture_result['coupling_level'] == 'high':
        architecture_result['recommendations'].append("考虑减少外部依赖，降低耦合度")

    if architecture_result['cohesion_level'] == 'low':
        architecture_result['recommendations'].append("考虑将大类拆分为多个职责单一的小类")

    if complexity_result['variables'] > 50:
        architecture_result['recommendations'].append("考虑使用模块化方式组织变量，减少全局作用域污染")

    return architecture_result
