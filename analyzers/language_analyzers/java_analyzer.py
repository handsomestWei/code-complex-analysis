#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Java代码复杂度分析器
专门分析Java代码的复杂度、结构和质量指标
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
import logging
from ..language_analyzer_manager import LanguageAnalyzer

logger = logging.getLogger(__name__)


class JavaAnalyzer(LanguageAnalyzer):
    """Java语言分析器"""

    @property
    def language_name(self) -> str:
        return "java"

    @property
    def file_extensions(self) -> List[str]:
        return ['.java']

    @property
    def analyzer_name(self) -> str:
        return "Java复杂度分析器"

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
        return file_path.suffix.lower() == '.java'

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """分析Java文件复杂度"""
        return analyze_java_complexity_detailed(file_path)


def analyze_java_complexity_detailed(file_path: Path) -> Dict[str, Any]:
    """详细分析Java代码复杂度"""
    result = {
        'file_path': str(file_path),
        'file_type': 'java',
        'lines': 0,
        'code_lines': 0,
        'comment_lines': 0,
        'blank_lines': 0,
        'classes': 0,
        'interfaces': 0,
        'enums': 0,
        'methods': 0,
        'complexity': 0,
        'imports': 0,
        'annotations': 0,
        'nested_levels': 0,
        'max_nested_level': 0,
        'package_declaration': '',
        'class_details': [],
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
        current_method = None

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

            # 检测包声明
            if line.startswith('package '):
                result['package_declaration'] = line.replace('package ', '').replace(';', '').strip()

            # 统计imports
            if line.startswith('import '):
                result['imports'] += 1

            # 统计注解
            if line.startswith('@'):
                result['annotations'] += 1

            # 统计类、接口和枚举
            class_match = re.search(r'\b(public|private|protected|static|abstract|final|strictfp)?\s*(abstract\s+)?(final\s+)?(strictfp\s+)?(class|interface|enum)\s+(\w+)', line)
            if class_match:
                class_type = class_match.group(5)  # class, interface, 或 enum
                class_name = class_match.group(6)

                if class_type == 'class':
                    result['classes'] += 1
                elif class_type == 'interface':
                    result['interfaces'] = result.get('interfaces', 0) + 1
                elif class_type == 'enum':
                    result['enums'] = result.get('enums', 0) + 1

                # 收集修饰符
                modifiers = []
                if 'public' in line: modifiers.append('public')
                if 'private' in line: modifiers.append('private')
                if 'protected' in line: modifiers.append('protected')
                if 'abstract' in line: modifiers.append('abstract')
                if 'final' in line: modifiers.append('final')
                if 'static' in line: modifiers.append('static')
                if 'strictfp' in line: modifiers.append('strictfp')

                current_class = {
                    'name': class_name,
                    'type': class_type,
                    'modifiers': modifiers,
                    'line': line_num,
                    'nested_level': current_nested_level
                }
                result['class_details'].append(current_class)

            # 统计方法
            method_match = re.search(r'\b(public|private|protected|static|final|abstract|synchronized|native|strictfp)?\s*(\w+)\s+(\w+)\s*\([^)]*\)\s*\{?', line)
            if method_match:
                result['methods'] += 1
                method_name = method_match.group(3)
                modifiers = []
                if 'public' in line: modifiers.append('public')
                if 'private' in line: modifiers.append('private')
                if 'protected' in line: modifiers.append('protected')
                if 'static' in line: modifiers.append('static')
                if 'final' in line: modifiers.append('final')
                if 'abstract' in line: modifiers.append('abstract')
                if 'synchronized' in line: modifiers.append('synchronized')
                if 'native' in line: modifiers.append('native')
                if 'strictfp' in line: modifiers.append('strictfp')

                current_method = {
                    'name': method_name,
                    'modifiers': modifiers,
                    'line': line_num,
                    'class': current_class['name'] if current_class else None,
                    'nested_level': current_nested_level
                }
                result['method_details'].append(current_method)

            # 统计嵌套级别
            if '{' in line:
                current_nested_level += 1
                result['max_nested_level'] = max(result['max_nested_level'], current_nested_level)
            if '}' in line:
                current_nested_level = max(0, current_nested_level - 1)

        # 计算复杂度
        result['complexity'] = _calculate_java_complexity(result)

        # 检测代码异味
        result['code_smells'] = _detect_java_code_smells(result)

        # 添加圈复杂度
        result['cyclomatic_complexity'] = result['complexity']

    except Exception as e:
        logger.error(f"分析Java文件失败 {file_path}: {e}")
        result['error'] = f"分析失败: {str(e)}"

    return result


def _calculate_java_complexity(analysis_result: Dict[str, Any]) -> int:
    """计算Java代码复杂度"""
    complexity = 1  # 基础复杂度

    # 基于类、接口和枚举数量
    complexity += analysis_result['classes'] * 2
    complexity += analysis_result.get('interfaces', 0) * 1.5  # 接口复杂度较低
    complexity += analysis_result.get('enums', 0) * 1.0      # 枚举复杂度最低
    complexity += analysis_result['methods'] * 3

    # 基于嵌套级别
    complexity += analysis_result['max_nested_level'] * 2

    # 基于imports数量
    complexity += analysis_result['imports'] // 5

    return complexity


def _detect_java_code_smells(analysis_result: Dict[str, Any]) -> List[str]:
    """检测Java代码异味"""
    smells = []

    # 检查类数量过多
    total_classes = analysis_result['classes'] + analysis_result.get('interfaces', 0) + analysis_result.get('enums', 0)
    if total_classes > 15:
        smells.append("类/接口/枚举数量过多，可能存在职责分散问题")
    elif total_classes > 10:
        smells.append("类/接口/枚举数量较多，建议关注模块划分")

    # 检查方法数量过多
    if analysis_result['methods'] > 50:
        smells.append("方法数量过多，可能存在职责分散问题")
    elif analysis_result['methods'] > 30:
        smells.append("方法数量较多，建议关注类的职责")

    # 检查嵌套级别过深
    if analysis_result['max_nested_level'] > 5:
        smells.append("嵌套级别过深，可能存在可读性问题")
    elif analysis_result['max_nested_level'] > 3:
        smells.append("嵌套级别较深，建议优化代码结构")

    # 检查imports过多
    if analysis_result['imports'] > 30:
        smells.append("依赖过多，可能存在耦合问题")
    elif analysis_result['imports'] > 20:
        smells.append("依赖较多，建议关注模块间耦合")

    return smells


def analyze_java_architecture(file_path: Path) -> Dict[str, Any]:
    """分析Java代码架构"""
    complexity_result = analyze_java_complexity_detailed(file_path)

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
    total_classes = complexity_result['classes'] + complexity_result.get('interfaces', 0) + complexity_result.get('enums', 0)
    if total_classes == 1:
        architecture_result['architecture_type'] = 'single_class'
    elif total_classes <= 3:
        architecture_result['architecture_type'] = 'simple_class_structure'
    elif total_classes <= 10:
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
    if complexity_result['methods'] <= 5:
        architecture_result['cohesion_level'] = 'high'
    elif complexity_result['methods'] <= 15:
        architecture_result['cohesion_level'] = 'medium'
    else:
        architecture_result['cohesion_level'] = 'low'

    # 生成建议
    if architecture_result['coupling_level'] == 'high':
        architecture_result['recommendations'].append("考虑减少外部依赖，降低耦合度")

    if architecture_result['cohesion_level'] == 'low':
        architecture_result['recommendations'].append("考虑将大类拆分为多个职责单一的小类")

    return architecture_result
