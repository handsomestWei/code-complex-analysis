#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vue代码复杂度分析器
专门分析Vue代码的复杂度、结构和质量指标
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
import logging
from ..language_analyzer_manager import LanguageAnalyzer

logger = logging.getLogger(__name__)


class VueAnalyzer(LanguageAnalyzer):
    """Vue语言分析器"""

    @property
    def language_name(self) -> str:
        return "vue"

    @property
    def file_extensions(self) -> List[str]:
        return ['.vue']

    @property
    def analyzer_name(self) -> str:
        return "Vue复杂度分析器"

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
        return file_path.suffix.lower() == '.vue'

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """分析Vue文件复杂度"""
        return analyze_vue_complexity_detailed(file_path)


def analyze_vue_complexity_detailed(file_path: Path) -> Dict[str, Any]:
    """详细分析Vue代码复杂度"""
    result = {
        'file_path': str(file_path),
        'file_type': 'vue',
        'lines': 0,
        'code_lines': 0,
        'comment_lines': 0,
        'blank_lines': 0,
        'template_lines': 0,
        'script_lines': 0,
        'style_lines': 0,
        'components': 0,
        'props': 0,
        'events': 0,
        'computed': 0,
        'watchers': 0,
        'methods': 0,
        'complexity': 0,
        'nested_levels': 0,
        'max_nested_level': 0,
        'component_details': [],
        'prop_details': [],
        'event_details': [],
        'computed_details': [],
        'watcher_details': [],
        'method_details': [],
        'code_smells': []
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = content.split('\n')
        result['lines'] = len(lines)

        # 分离Vue文件的三个部分
        template_match = re.search(r'<template[^>]*>(.*?)</template>', content, re.DOTALL | re.IGNORECASE)
        script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
        style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL | re.IGNORECASE)

        # 分析模板部分
        if template_match:
            template_content = template_match.group(1)
            template_lines = template_content.split('\n')
            result['template_lines'] = len([line for line in template_lines if line.strip()])

            # 统计组件使用
            component_matches = re.findall(r'<(\w+)[^>]*>', template_content)
            result['components'] = len(set(component_matches))

            # 统计事件绑定
            event_matches = re.findall(r'@(\w+)=', template_content)
            result['events'] = len(event_matches)

            # 统计属性绑定
            prop_matches = re.findall(r':(\w+)=', template_content)
            result['props'] = len(prop_matches)

            # 计算模板嵌套级别
            template_nesting = 0
            for char in template_content:
                if char == '<' and not template_content.startswith('</', template_content.find(char)):
                    template_nesting += 1
                elif char == '>':
                    template_nesting = max(0, template_nesting - 1)
                result['max_nested_level'] = max(result['max_nested_level'], template_nesting)

        # 分析脚本部分
        if script_match:
            script_content = script_match.group(1)
            script_lines = script_content.split('\n')
            result['script_lines'] = len([line for line in script_lines if line.strip()])

            # 统计计算属性
            computed_matches = re.findall(r'computed\s*:\s*{([^}]+)}', script_content, re.DOTALL)
            if computed_matches:
                computed_props = re.findall(r'(\w+)\s*\([^)]*\)\s*{', computed_matches[0])
                result['computed'] = len(computed_props)
                for prop in computed_props:
                    result['computed_details'].append({
                        'name': prop,
                        'type': 'computed'
                    })

            # 统计监听器
            watch_matches = re.findall(r'watch\s*:\s*{([^}]+)}', script_content, re.DOTALL)
            if watch_matches:
                watch_props = re.findall(r'(\w+)\s*\([^)]*\)\s*{', watch_matches[0])
                result['watchers'] = len(watch_props)
                for prop in watch_props:
                    result['watcher_details'].append({
                        'name': prop,
                        'type': 'watcher'
                    })

            # 统计方法
            method_matches = re.findall(r'methods\s*:\s*{([^}]+)}', script_content, re.DOTALL)
            if method_matches:
                method_names = re.findall(r'(\w+)\s*\([^)]*\)\s*{', method_matches[0])
                result['methods'] = len(method_names)
                for name in method_names:
                    result['method_details'].append({
                        'name': name,
                        'type': 'method'
                    })

            # 统计组件注册
            component_matches = re.findall(r'components\s*:\s*{([^}]+)}', script_content, re.DOTALL)
            if component_matches:
                component_names = re.findall(r'(\w+)\s*:', component_matches[0])
                for name in component_names:
                    result['component_details'].append({
                        'name': name,
                        'type': 'imported_component'
                    })

        # 分析样式部分
        if style_match:
            style_content = style_match.group(1)
            style_lines = style_content.split('\n')
            result['style_lines'] = len([line for line in style_lines if line.strip()])

        # 统计注释和空行
        for line in lines:
            line = line.strip()
            if not line:
                result['blank_lines'] += 1
            elif line.startswith('<!--') or line.startswith('//') or line.startswith('/*'):
                result['comment_lines'] += 1

        result['code_lines'] = result['lines'] - result['blank_lines'] - result['comment_lines']

        # 计算复杂度
        result['complexity'] = _calculate_vue_complexity(result)

        # 检测代码异味
        result['code_smells'] = _detect_vue_code_smells(result)

    except Exception as e:
        logger.error(f"分析Vue文件失败 {file_path}: {e}")
        result['error'] = f"分析失败: {str(e)}"

    return result


def _calculate_vue_complexity(analysis_result: Dict[str, Any]) -> int:
    """计算Vue代码复杂度"""
    complexity = 1  # 基础复杂度

    # 基于组件数量
    complexity += analysis_result['components'] * 2

    # 基于方法数量
    complexity += analysis_result['methods'] * 3

    # 基于计算属性数量
    complexity += analysis_result['computed'] * 2

    # 基于监听器数量
    complexity += analysis_result['watchers'] * 2

    # 基于事件数量
    complexity += analysis_result['events'] * 1

    # 基于属性数量
    complexity += analysis_result['props'] * 1

    # 基于嵌套级别
    complexity += analysis_result['max_nested_level'] * 2

    return complexity


def _detect_vue_code_smells(analysis_result: Dict[str, Any]) -> List[str]:
    """检测Vue代码异味"""
    smells = []

    # 检查组件数量过多
    if analysis_result['components'] > 15:
        smells.append("组件数量过多，可能存在职责分散问题")

    # 检查方法数量过多
    if analysis_result['methods'] > 20:
        smells.append("方法数量过多，可能存在职责分散问题")

    # 检查计算属性数量过多
    if analysis_result['computed'] > 10:
        smells.append("计算属性数量过多，可能存在过度计算问题")

    # 检查监听器数量过多
    if analysis_result['watchers'] > 8:
        smells.append("监听器数量过多，可能存在性能问题")

    # 检查事件数量过多
    if analysis_result['events'] > 15:
        smells.append("事件数量过多，可能存在过度绑定问题")

    # 检查属性数量过多
    if analysis_result['props'] > 20:
        smells.append("属性数量过多，可能存在接口复杂问题")

    # 检查嵌套级别过深
    if analysis_result['max_nested_level'] > 5:
        smells.append("嵌套级别过深，可能存在可读性问题")

    # 检查模板行数过多
    if analysis_result['template_lines'] > 80:
        smells.append("模板行数过多，可能存在可读性问题")

    return smells


def analyze_vue_architecture(file_path: Path) -> Dict[str, Any]:
    """分析Vue代码架构"""
    complexity_result = analyze_vue_complexity_detailed(file_path)

    if 'error' in complexity_result:
        return complexity_result

    architecture_result = {
        'file_path': str(file_path),
        'architecture_type': 'unknown',
        'component_pattern': 'unknown',
        'state_management': 'local',
        'coupling_level': 'low',
        'cohesion_level': 'high',
        'recommendations': []
    }

    # 分析架构类型
    if complexity_result['components'] == 0:
        architecture_result['architecture_type'] = 'single_file'
    elif complexity_result['components'] <= 5:
        architecture_result['architecture_type'] = 'simple_component'
    elif complexity_result['components'] <= 12:
        architecture_result['architecture_type'] = 'moderate_component'
    else:
        architecture_result['architecture_type'] = 'complex_component'

    # 分析组件模式
    if complexity_result['methods'] > 15 and complexity_result['computed'] > 5:
        architecture_result['component_pattern'] = 'smart_component'
    elif complexity_result['methods'] <= 5 and complexity_result['computed'] <= 2:
        architecture_result['component_pattern'] = 'presentational_component'
    else:
        architecture_result['component_pattern'] = 'mixed_component'

    # 分析状态管理
    if complexity_result['watchers'] > 5 or complexity_result['computed'] > 8:
        architecture_result['state_management'] = 'complex_local'
    elif complexity_result['watchers'] <= 2 and complexity_result['computed'] <= 3:
        architecture_result['state_management'] = 'simple_local'
    else:
        architecture_result['state_management'] = 'moderate_local'

    # 分析耦合度
    if complexity_result['props'] <= 5:
        architecture_result['coupling_level'] = 'low'
    elif complexity_result['props'] <= 12:
        architecture_result['coupling_level'] = 'medium'
    else:
        architecture_result['coupling_level'] = 'high'

    # 分析内聚度
    total_methods = complexity_result['methods'] + complexity_result['computed'] + complexity_result['watchers']
    if total_methods <= 8:
        architecture_result['cohesion_level'] = 'high'
    elif total_methods <= 20:
        architecture_result['cohesion_level'] = 'medium'
    else:
        architecture_result['cohesion_level'] = 'low'

    # 生成建议
    if architecture_result['coupling_level'] == 'high':
        architecture_result['recommendations'].append("考虑减少props数量，降低组件间耦合度")

    if architecture_result['cohesion_level'] == 'low':
        architecture_result['recommendations'].append("考虑将大组件拆分为多个职责单一的小组件")

    if complexity_result['template_lines'] > 80:
        architecture_result['recommendations'].append("考虑将大模板拆分为多个子组件")

    if complexity_result['watchers'] > 6:
        architecture_result['recommendations'].append("考虑使用Vuex等状态管理工具，减少本地状态复杂度")

    return architecture_result


def analyze_vue_accessibility(file_path: Path) -> Dict[str, Any]:
    """分析Vue代码可访问性"""
    result = {
        'accessibility_issues': [],
        'accessibility_score': 100,
        'recommendations': []
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 检测可访问性问题
        if 'v-for' in content and 'key' not in content:
            result['accessibility_issues'].append('缺少key属性')
            result['accessibility_score'] -= 10

        if 'v-if' in content and 'v-else' not in content:
            result['accessibility_issues'].append('条件渲染不完整')
            result['accessibility_score'] -= 5

        if 'alt=' not in content and 'img' in content:
            result['accessibility_issues'].append('图片缺少alt属性')
            result['accessibility_score'] -= 15

        if 'aria-' not in content and 'role=' not in content:
            result['accessibility_issues'].append('缺少ARIA属性')
            result['accessibility_score'] -= 10

        # 生成建议
        if result['accessibility_score'] < 80:
            result['recommendations'].append('添加适当的ARIA标签')
            result['recommendations'].append('确保所有交互元素都有键盘支持')
            result['recommendations'].append('使用语义化HTML标签')

    except Exception as e:
        result['error'] = f"分析Vue可访问性失败: {str(e)}"

    return result
