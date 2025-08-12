#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python代码复杂度分析器
专门分析Python代码的复杂度、结构和质量指标
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
import logging
from ..language_analyzer_manager import LanguageAnalyzer

logger = logging.getLogger(__name__)


class PythonAnalyzer(LanguageAnalyzer):
    """Python语言分析器"""

    @property
    def language_name(self) -> str:
        return "python"

    @property
    def file_extensions(self) -> List[str]:
        return ['.py']

    @property
    def analyzer_name(self) -> str:
        return "Python复杂度分析器"

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
        return file_path.suffix.lower() == '.py'

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """分析Python文件复杂度"""
        return analyze_python_complexity_detailed(file_path)


def analyze_python_complexity_detailed(file_path: Path) -> Dict[str, Any]:
    """详细分析Python代码复杂度"""
    result = {
        'file_path': str(file_path),
        'file_type': 'python',
        'lines': 0,
        'code_lines': 0,
        'comment_lines': 0,
        'blank_lines': 0,
        'classes': 0,
        'functions': 0,
        'methods': 0,
        'imports': 0,
        'decorators': 0,
        'complexity': 0,
        'nested_levels': 0,
        'max_nested_level': 0,
        'module_system': 'standard',
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
            if '"""' in line or "'''" in line:
                if line.count('"""') % 2 == 1 or line.count("'''") % 2 == 1:
                    in_multiline_comment = not in_multiline_comment
                result['comment_lines'] += 1
                continue
            elif in_multiline_comment:
                result['comment_lines'] += 1
                continue

            # 单行注释
            if line.startswith('#') or line.startswith('"""') or line.startswith("'''"):
                result['comment_lines'] += 1
                continue

            # 统计代码行
            result['code_lines'] += 1

            # 检测模块系统
            if line.startswith('import ') or line.startswith('from '):
                result['imports'] += 1
                if 'as ' in line:
                    result['module_system'] = 'aliased_imports'

            # 统计装饰器
            if line.startswith('@'):
                result['decorators'] += 1

            # 统计类
            class_match = re.search(r'^class\s+(\w+)', line)
            if class_match:
                result['classes'] += 1
                current_class = class_match.group(1)
                result['class_details'].append({
                    'name': current_class,
                    'line': line_num,
                    'type': 'class'
                })

            # 统计函数
            function_match = re.search(r'^def\s+(\w+)', line)
            if function_match:
                result['functions'] += 1
                current_function = function_match.group(1)
                result['function_details'].append({
                    'name': current_function,
                    'line': line_num,
                    'type': 'function',
                    'class': current_class
                })

            # 统计方法（类内的函数）
            if current_class and function_match:
                result['methods'] += 1
                result['method_details'].append({
                    'name': current_function,
                    'line': line_num,
                    'type': 'method',
                    'class': current_class
                })

            # 统计嵌套级别
            if line.endswith(':'):
                current_nested_level += 1
                result['max_nested_level'] = max(result['max_nested_level'], current_nested_level)
            elif line.startswith('return') or line.startswith('break') or line.startswith('continue'):
                current_nested_level = max(0, current_nested_level - 1)

        # 计算复杂度
        result['complexity'] = _calculate_python_complexity(result)

        # 检测代码异味
        result['code_smells'] = _detect_python_code_smells(result)

    except Exception as e:
        logger.error(f"分析Python文件失败 {file_path}: {e}")
        result['error'] = f"分析失败: {str(e)}"

    return result


def _calculate_python_complexity(analysis_result: Dict[str, Any]) -> int:
    """计算Python代码复杂度"""
    complexity = 1  # 基础复杂度

    # 基于类和方法数量
    complexity += analysis_result['classes'] * 2
    complexity += analysis_result['methods'] * 3
    complexity += analysis_result['functions'] * 2

    # 基于嵌套级别
    complexity += analysis_result['max_nested_level'] * 2

    # 基于imports数量
    complexity += analysis_result['imports'] // 5

    # 基于装饰器数量
    complexity += analysis_result['decorators'] * 1

    return complexity


def _detect_python_code_smells(analysis_result: Dict[str, Any]) -> List[str]:
    """检测Python代码异味"""
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

    # 检查装饰器过多
    if analysis_result['decorators'] > 10:
        smells.append("装饰器过多，可能存在过度抽象问题")

    return smells


def analyze_python_architecture(file_path: Path) -> Dict[str, Any]:
    """分析Python代码架构"""
    complexity_result = analyze_python_complexity_detailed(file_path)

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
    elif complexity_result['classes'] == 1:
        architecture_result['architecture_type'] = 'single_class'
    elif complexity_result['classes'] <= 3:
        architecture_result['architecture_type'] = 'simple_class_structure'
    elif complexity_result['classes'] <= 10:
        architecture_result['architecture_type'] = 'moderate_class_structure'
    else:
        architecture_result['architecture_type'] = 'complex_class_structure'

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

    if complexity_result['decorators'] > 5:
        architecture_result['recommendations'].append("考虑简化装饰器使用，避免过度抽象")

    return architecture_result


def analyze_python_style(file_path: Path) -> Dict[str, Any]:
    """分析Python代码风格"""
    complexity_result = analyze_python_complexity_detailed(file_path)

    if 'error' in complexity_result:
        return complexity_result

    style_result = {
        'file_path': str(file_path),
        'style_score': 100,
        'style_issues': [],
        'pep8_compliance': 'unknown',
        'recommendations': []
    }

    # 检查代码行长度
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        long_lines = [i+1 for i, line in enumerate(lines) if len(line.rstrip()) > 79]
        if long_lines:
            style_result['style_score'] -= len(long_lines) * 2
            style_result['style_issues'].append(f"第{', '.join(map(str, long_lines))}行超过79字符")

        # 检查空行使用
        consecutive_blank_lines = 0
        for i, line in enumerate(lines):
            if not line.strip():
                consecutive_blank_lines += 1
            else:
                if consecutive_blank_lines > 2:
                    style_result['style_score'] -= 1
                    style_result['style_issues'].append(f"第{i}行附近存在过多连续空行")
                consecutive_blank_lines = 0

        # 检查导入语句位置
        import_lines = []
        code_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                import_lines.append(i+1)
            elif line.strip() and not line.strip().startswith('#'):
                code_lines.append(i+1)

        if code_lines and import_lines and min(code_lines) < max(import_lines):
            style_result['style_score'] -= 5
            style_result['style_issues'].append("导入语句应该放在文件开头")

        # 评估PEP8合规性
        if style_result['style_score'] >= 90:
            style_result['pep8_compliance'] = 'excellent'
        elif style_result['style_score'] >= 80:
            style_result['pep8_compliance'] = 'good'
        elif style_result['style_score'] >= 70:
            style_result['pep8_compliance'] = 'fair'
        else:
            style_result['pep8_compliance'] = 'poor'

        # 生成建议
        if long_lines:
            style_result['recommendations'].append("将长行拆分为多行，提高可读性")

        if style_result['pep8_compliance'] in ['fair', 'poor']:
            style_result['recommendations'].append("使用工具如flake8或pylint检查代码风格")

    except Exception as e:
        logger.error(f"分析Python代码风格失败 {file_path}: {e}")
        style_result['error'] = f"风格分析失败: {str(e)}"

    return style_result
