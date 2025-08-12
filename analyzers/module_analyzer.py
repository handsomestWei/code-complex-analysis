#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块分析模块
包含模块扫描、复杂度分析等功能
"""

import os
import re
import logging
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Any, List, Tuple, Optional
from .complexity_analyzer import (
    analyze_code_complexity
)

logger = logging.getLogger(__name__)


def analyze_module(module_path: Path, ignore_patterns: List[str] = None) -> Dict[str, Any]:
    """分析模块"""
    result = {
        'module_name': module_path.name,
        'module_path': str(module_path),
        'type': '未知',
        'files': {},
        'complexity': {},
        'stats': {},
        'project_structure': {}  # 新增：项目结构分析结果
    }

    try:
        # 判断模块类型
        if (module_path / 'pom.xml').exists():
            result['type'] = 'Java/Maven项目'
            # 分析Maven项目结构
            try:
                from .project_structure_analyzer import analyze_maven_project
                result['project_structure'] = analyze_maven_project(module_path)
            except Exception as e:
                logger.warning(f"分析Maven项目结构失败: {e}")
                result['project_structure'] = {'error': f'分析失败: {str(e)}'}
        elif (module_path / 'build.gradle').exists():
            result['type'] = 'Java/Gradle项目'
        elif (module_path / 'package.json').exists():
            # 分析Node.js项目结构
            try:
                from .project_structure_analyzer import analyze_package_json
                package_result = analyze_package_json(module_path)
                result['type'] = package_result.get('type', 'Node.js项目')
                result['project_structure'] = package_result

                # 如果是Vue项目，进一步分析Vue项目结构
                if 'Vue' in package_result.get('type', ''):
                    try:
                        from .project_structure_analyzer import analyze_vue_project_structure
                        vue_result = analyze_vue_project_structure(module_path)
                        # 合并Vue特定的结构信息
                        result['project_structure'].update(vue_result)
                    except Exception as e:
                        logger.warning(f"分析Vue项目结构失败: {e}")
            except Exception as e:
                logger.warning(f"分析Package.json失败: {e}")
                result['project_structure'] = {'error': f'分析失败: {str(e)}'}
        elif (module_path / 'requirements.txt').exists() or (module_path / 'setup.py').exists():
            result['type'] = 'Python项目'

        # 统计文件
        result['files'] = count_files_by_type(module_path, ignore_patterns)

        # 分析复杂度
        result['complexity'] = analyze_module_complexity(module_path, ignore_patterns)

        # 统计信息
        result['stats'] = {
            'total_files': sum(result['files'].values()),
            'total_lines': result['complexity'].get('total_lines', 0),
            'total_complexity': result['complexity'].get('total_complexity', 0)
        }

    except Exception as e:
        result['error'] = f"分析模块失败: {str(e)}"

    return result


def analyze_file_complexity(file_path: Path, max_file_size: int = None) -> Dict[str, Any]:
    """
    分析单个文件的复杂度

    Args:
        file_path: 文件路径
        max_file_size: 最大文件大小（字节），如果为None则使用配置值

    Returns:
        文件分析结果字典
    """
    try:
        # 检查文件是否存在
        if not file_path.exists():
            return _create_error_result(file_path, "文件不存在")

        # 如果没有传入max_file_size，尝试从配置获取
        if max_file_size is None:
            try:
                from .analyzer_config import get_config
                config = get_config()
                max_file_size = config.max_file_size
            except ImportError:
                max_file_size = 10 * 1024 * 1024  # 默认10MB作为后备

        # 检查文件大小
        file_size = file_path.stat().st_size
        if file_size > max_file_size:
            logger.warning(f"文件过大，跳过分析: {file_path} ({file_size / 1024 / 1024:.1f}MB)")
            return _create_error_result(file_path, f"文件过大，跳过分析 (超过{max_file_size / 1024 / 1024:.1f}MB)")

        # 获取文件扩展名
        file_extension = file_path.suffix.lower()

        # 使用动态方式识别对应语言分析器
        result = _analyze_file_with_dynamic_analyzer(file_path, file_extension)

        # 标准化结果字段，确保字段名一致
        if 'error' not in result:
            # 映射字段名
            if 'lines' in result and 'total_lines' not in result:
                result['total_lines'] = result['lines']
            if 'complexity' in result and 'total_complexity' not in result:
                result['total_complexity'] = result['complexity']

            # 确保必要字段存在
            if 'total_lines' not in result:
                result['total_lines'] = result.get('lines', 0)
            if 'total_complexity' not in result:
                result['total_complexity'] = result.get('complexity', 0)

        # 添加文件信息
        result['file_path'] = str(file_path)
        result['file_size'] = file_size
        result['file_extension'] = file_extension

        return result

    except Exception as e:
        logger.error(f"分析文件失败 {file_path}: {e}")
        return _create_error_result(file_path, f"分析失败: {str(e)}")


def _create_error_result(file_path: Path, error_message: str) -> Dict[str, Any]:
    """创建文件分析错误结果"""
    return {
        'error': error_message,
        'file_path': str(file_path),
        'total_lines': 0,
        'total_complexity': 0,
        'complexity_metrics': {}
    }


def _analyze_generic_file(file_path: Path) -> Dict[str, Any]:
    """分析通用文件（只统计行数）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        total_lines = len(lines)

        return {
            'total_lines': total_lines,
            'total_complexity': 0,
            'complexity_metrics': {
                'lines_of_code': total_lines
            }
        }

    except Exception as e:
        logger.error(f"分析通用文件失败 {file_path}: {e}")
        return _create_error_result(file_path, f"通用分析失败: {str(e)}")


def analyze_module_complexity(module_path: Path, ignore_patterns: List[str] = None) -> Dict[str, Any]:
    """分析模块的复杂度"""
    result = {
        'module_name': module_path.name,
        'module_path': str(module_path),
        'total_files': 0,
        'total_lines': 0,
        'total_complexity': 0,
        'max_complexity': 0,
        'average_complexity': 0,
        'language_stats': {},
        'file_complexity': {},
        'complexity_distribution': {
            'LOW': 0,
            'MEDIUM': 0,
            'HIGH': 0,
            'VERY_HIGH': 0
        }
    }

    try:
        # 动态获取语言扩展名映射
        language_extensions = _get_dynamic_language_extensions()

        # 使用传入的忽略模式，如果没有传入则使用默认值
        if ignore_patterns is None:
            ignore_patterns = [
                'node_modules', '.git', 'target', 'dist', 'build',
                '__pycache__', '.pytest_cache', '.coverage', '.mypy_cache'
            ]

        # 遍历文件
        for file_path in module_path.rglob('*'):
            if file_path.is_file():
                # 检查是否应该忽略
                if any(pattern in str(file_path) for pattern in ignore_patterns):
                    continue

                # 分析文件复杂度
                file_result = analyze_file_complexity(file_path)

                if 'error' not in file_result:
                    # 更新统计信息
                    result['total_lines'] += file_result.get('total_lines', 0)
                    result['total_complexity'] += file_result.get('total_complexity', 0)

                    # 更新语言统计
                    file_ext = file_path.suffix.lower()
                    for lang, exts in language_extensions.items():
                        if file_ext in exts:
                            if lang not in result['language_stats']:
                                result['language_stats'][lang] = {
                                    'files': 0,
                                    'lines': 0,
                                    'complexity': 0
                                }
                            result['language_stats'][lang]['files'] += 1
                            result['language_stats'][lang]['lines'] += file_result.get('total_lines', 0)
                            result['language_stats'][lang]['complexity'] += file_result.get('total_complexity', 0)
                            break

                    # 记录文件复杂度
                    result['file_complexity'][str(file_path)] = file_result

                    # 更新最大复杂度
                    file_complexity = file_result.get('total_complexity', 0)
                    if file_complexity > result['max_complexity']:
                        result['max_complexity'] = file_complexity

        # 设置总文件数
        result['total_files'] = len(result['file_complexity'])

        # 计算平均复杂度
        if result['file_complexity']:
            result['average_complexity'] = result['total_complexity'] / len(result['file_complexity'])

        # 复杂度分布 - 从配置读取阈值
        try:
            from .analyzer_config import get_config
            config = get_config()
            base_thresholds = config.complexity_thresholds

            complexity_ranges = {
                'LOW': (0, base_thresholds['LOW'] // 10),
                'MEDIUM': (base_thresholds['LOW'] // 10 + 1, base_thresholds['MEDIUM'] // 10),
                'HIGH': (base_thresholds['MEDIUM'] // 10 + 1, base_thresholds['HIGH'] // 10),
                'VERY_HIGH': (base_thresholds['HIGH'] // 10 + 1, float('inf'))
            }
        except ImportError:
            # 如果无法导入配置，使用默认值作为后备
            complexity_ranges = {
                'LOW': (0, 10),
                'MEDIUM': (11, 50),
                'HIGH': (51, 100),
                'VERY_HIGH': (101, float('inf'))
            }

        for range_name, (min_val, max_val) in complexity_ranges.items():
            count = sum(1 for file_result in result['file_complexity'].values()
                       if min_val <= file_result.get('total_complexity', 0) <= max_val)
            result['complexity_distribution'][range_name] = count

    except Exception as e:
        logger.error(f"分析模块复杂度失败 {module_path}: {e}")
        result['error'] = f"分析失败: {str(e)}"

    return result


def count_files_by_type(module_path: Path, ignore_patterns: List[str] = None) -> Dict[str, int]:
    """统计模块中各种类型的文件数量"""
    file_counts = defaultdict(int)

    try:
        # 动态获取语言扩展名映射
        language_extensions = _get_dynamic_language_extensions()

        # 使用传入的忽略模式，如果没有传入则使用默认值
        if ignore_patterns is None:
            ignore_patterns = [
                'node_modules', '.git', 'target', 'dist', 'build',
                '__pycache__', '.pytest_cache', '.coverage', '.mypy_cache'
            ]

        # 遍历文件
        for file_path in module_path.rglob('*'):
            if file_path.is_file():
                # 检查是否应该忽略
                if any(pattern in str(file_path) for pattern in ignore_patterns):
                    continue

                # 统计文件类型
                file_ext = file_path.suffix.lower()
                counted = False

                for lang, exts in language_extensions.items():
                    if file_ext in exts:
                        file_counts[lang] += 1
                        counted = True
                        break

                if not counted:
                    file_counts['other'] += 1

    except Exception as e:
        logger.error(f"统计文件类型失败 {module_path}: {e}")

    return dict(file_counts)


def _analyze_file_with_dynamic_analyzer(file_path: Path, file_extension: str) -> Dict[str, Any]:
    """使用动态方式识别对应语言分析器"""
    try:
        # 尝试使用复杂度分析器的动态识别功能
        return analyze_code_complexity(file_path)
    except ImportError:
        # 如果无法导入复杂度分析器，使用后备方案
        return _analyze_file_with_fallback(file_path, file_extension)


def _analyze_file_with_fallback(file_path: Path, file_extension: str) -> Dict[str, Any]:
    """后备方案：基于文件扩展名的简单分析"""
    try:
        # 尝试动态导入对应的分析器
        analyzer_name = _get_analyzer_name_from_extension(file_extension)
        if analyzer_name:
            try:
                # 动态导入分析器模块
                module = __import__(f'.language_analyzers.{analyzer_name}_analyzer', fromlist=['analyze_complexity_detailed'])
                analyze_func = getattr(module, 'analyze_complexity_detailed', None)
                if analyze_func:
                    return analyze_func(file_path)
            except ImportError:
                pass

        # 如果动态导入失败，使用通用分析
        return _analyze_generic_file(file_path)

    except Exception as e:
        logger.warning(f"动态分析器识别失败，使用通用分析: {e}")
        return _analyze_generic_file(file_path)


def _get_analyzer_name_from_extension(file_extension: str) -> Optional[str]:
    """根据文件扩展名推断分析器名称"""
    try:
        # 动态获取扩展名到分析器的映射
        from .language_analyzer_manager import get_analyzer_manager
        manager = get_analyzer_manager()
        if manager:
            analyzers = manager.get_available_analyzers()
            for analyzer_name, analyzer_info in analyzers.items():
                if hasattr(analyzer_info, 'file_extensions'):
                    if file_extension.lower() in analyzer_info.file_extensions:
                        return analyzer_name
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"动态获取分析器名称失败: {e}")

    return None


def _get_dynamic_language_extensions() -> Dict[str, List[str]]:
    """动态获取语言扩展名映射，零硬编码"""
    language_extensions = {}

    try:
        # 尝试从语言分析器管理器获取
        from .language_analyzer_manager import get_analyzer_manager
        manager = get_analyzer_manager()
        if manager:
            analyzers = manager.get_available_analyzers()
            for analyzer_name, analyzer_info in analyzers.items():
                if hasattr(analyzer_info, 'file_extensions'):
                    language_extensions[analyzer_name] = analyzer_info.file_extensions
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"获取动态语言扩展名失败: {e}")

    return language_extensions

def _get_file_language_mapping(self) -> Dict[str, str]:
    """动态获取文件扩展名到语言的映射，零硬编码"""
    mapping = {}

    try:
        # 尝试从语言分析器管理器获取
        from .language_analyzer_manager import get_analyzer_manager
        manager = get_analyzer_manager()
        if manager:
            analyzers = manager.get_available_analyzers()
            for analyzer_name, analyzer_info in analyzers.items():
                if hasattr(analyzer_info, 'file_extensions'):
                    for ext in analyzer_info.file_extensions:
                        mapping[ext] = analyzer_name
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"获取文件语言映射失败: {e}")

    return mapping
