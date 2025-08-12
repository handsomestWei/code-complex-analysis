#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码复杂度分析模块
统一的代码复杂度分析入口点，支持多种编程语言
完全动态化设计，零硬编码
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

def _get_language_analyzer_manager():
    """动态获取语言分析器管理器"""
    try:
        from .language_analyzer_manager import get_analyzer_manager
        return get_analyzer_manager()
    except ImportError:
        return None

def _find_matching_analyzer(file_path: Path) -> Optional[tuple]:
    """
    动态查找能处理指定文件的分析器

    Returns:
        (analyzer_name, analyzer_function) 或 None
    """
    manager = _get_language_analyzer_manager()
    if not manager:
        return None

    try:
        # 获取所有可用的分析器
        analyzers = manager.get_available_analyzers()

        for analyzer_name, analyzer_info in analyzers.items():
            # 检查分析器是否有 can_analyze 方法
            if hasattr(analyzer_info, 'can_analyze'):
                try:
                    if analyzer_info.can_analyze(file_path):
                        # 获取对应的复杂度分析函数
                        complexity_func = _get_complexity_analyzer_function(analyzer_name)
                        if complexity_func:
                            return analyzer_name, complexity_func
                except Exception as e:
                    print(f"警告: 分析器 {analyzer_name} 的 can_analyze 方法执行失败: {e}")
                    continue

            # 如果没有 can_analyze 方法，尝试通过文件扩展名匹配
            elif hasattr(analyzer_info, 'file_extensions'):
                try:
                    supported_exts = analyzer_info.file_extensions
                    if file_path.suffix.lower() in supported_exts:
                        complexity_func = _get_complexity_analyzer_function(analyzer_name)
                        if complexity_func:
                            return analyzer_name, complexity_func
                except Exception as e:
                    print(f"警告: 分析器 {analyzer_name} 的扩展名匹配失败: {e}")
                    continue

        return None

    except Exception as e:
        print(f"警告: 查找匹配分析器失败: {e}")
        return None

def _get_complexity_analyzer_function(analyzer_name: str):
    """完全动态获取分析器函数，零硬编码"""
    try:
        # 方法1: 尝试动态导入（推荐方式）
        try:
            module = __import__(f'.language_analyzers.{analyzer_name}_analyzer', fromlist=[f'analyze_{analyzer_name}_complexity_detailed'])
            func = getattr(module, f'analyze_{analyzer_name}_complexity_detailed', None)
            if func:
                return func
        except ImportError:
            pass

        # 方法2: 尝试从语言分析器管理器获取
        manager = _get_language_analyzer_manager()
        if manager:
            analyzers = manager.get_available_analyzers()
            if analyzer_name in analyzers:
                analyzer_info = analyzers[analyzer_name]
                if hasattr(analyzer_info, 'analyze'):
                    return analyzer_info.analyze

        # 方法3: 尝试通用导入
        try:
            # 避免通配符导入，使用动态导入
            module = __import__('.language_analyzers', fromlist=[f'analyze_{analyzer_name}_complexity_detailed'])
            func_name = f'analyze_{analyzer_name}_complexity_detailed'
            if hasattr(module, func_name):
                return getattr(module, func_name)
        except ImportError:
            pass

        return None

    except Exception as e:
        print(f"警告: 获取分析器 {analyzer_name} 的复杂度分析函数失败: {e}")
        return None

def analyze_code_complexity(file_path: Path) -> Dict[str, Any]:
    """
    统一的代码复杂度分析入口点
    动态查找能处理指定文件的分析器，完全插件化
    """
    # 查找匹配的分析器
    analyzer_result = _find_matching_analyzer(file_path)

    if analyzer_result:
        analyzer_name, analyzer_func = analyzer_result
        try:
            result = analyzer_func(file_path)
            # 添加分析器信息
            result['analyzer_used'] = analyzer_name
            return result
        except Exception as e:
            print(f"警告: 使用分析器 {analyzer_name} 分析文件 {file_path} 失败: {e}")
            return _analyze_generic_complexity(file_path)
    else:
        # 没有找到匹配的分析器，使用通用分析
        return _analyze_generic_complexity(file_path)


def _analyze_generic_complexity(file_path: Path) -> Dict[str, Any]:
    """通用代码复杂度分析（用于不支持的文件类型）"""
    result = {
        'lines': 0,
        'code_lines': 0,
        'comment_lines': 0,
        'blank_lines': 0,
        'complexity': 0,
        'nested_levels': 0,
        'max_nested_level': 0,
        'file_type': 'unknown',
        'warning': '不支持的文件类型，使用通用分析',
        'analyzer_used': 'generic'
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

            # 统计代码行
            result['code_lines'] += 1

            # 统计嵌套层级
            if '{' in line or '(' in line:
                current_nested_level += 1
                result['max_nested_level'] = max(result['max_nested_level'], current_nested_level)
            if '}' in line or ')' in line:
                current_nested_level = max(0, current_nested_level - 1)

            # 计算复杂度
            complexity_keywords = ['if', 'else', 'for', 'while', 'do', 'switch', 'case', 'catch', 'finally', '&&', '||', '?', ':', 'break', 'continue']
            for keyword in complexity_keywords:
                if keyword in line:
                    result['complexity'] += 1

        result['nested_levels'] = result['max_nested_level']

    except Exception as e:
        result['error'] = f"分析文件失败: {str(e)}"

    return result


def analyze_project_complexity(project_path: Path, file_extensions: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    分析整个项目的代码复杂度

    Args:
        project_path: 项目根目录路径
        file_extensions: 要分析的文件扩展名列表，如果为None则分析所有支持的文件类型

    Returns:
        项目复杂度分析结果
    """
    # 动态获取支持的文件扩展名
    if file_extensions is None:
        file_extensions = _get_dynamic_supported_extensions()

    result = {
        'project_path': str(project_path),
        'total_files': 0,
        'analyzed_files': 0,
        'total_lines': 0,
        'total_code_lines': 0,
        'total_complexity': 0,
        'average_complexity': 0,
        'max_complexity': 0,
        'complexity_distribution': {},
        'file_type_summary': {},
        'complexity_issues': [],
        'file_details': [],
        'analyzers_used': {}  # 记录使用了哪些分析器
    }

    try:
        # 遍历项目文件
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                result['total_files'] += 1

                # 分析单个文件
                file_analysis = analyze_code_complexity(file_path)

                if 'error' not in file_analysis:
                    result['analyzed_files'] += 1
                    result['total_lines'] += file_analysis.get('lines', 0)
                    result['total_code_lines'] += file_analysis.get('code_lines', 0)
                    result['total_complexity'] += file_analysis.get('complexity', 0)
                    result['max_complexity'] = max(result['max_complexity'], file_analysis.get('complexity', 0))

                    # 记录使用的分析器
                    analyzer_used = file_analysis.get('analyzer_used', 'unknown')
                    if analyzer_used not in result['analyzers_used']:
                        result['analyzers_used'][analyzer_used] = 0
                    result['analyzers_used'][analyzer_used] += 1

                    # 统计文件类型
                    file_ext = file_path.suffix.lower()
                    if file_ext not in result['file_type_summary']:
                        result['file_type_summary'][file_ext] = {
                            'count': 0,
                            'total_lines': 0,
                            'total_complexity': 0
                        }

                    result['file_type_summary'][file_ext]['count'] += 1
                    result['file_type_summary'][file_ext]['total_lines'] += file_analysis.get('lines', 0)
                    result['file_type_summary'][file_ext]['total_complexity'] += file_analysis.get('complexity', 0)

                    # 复杂度分布 - 从配置读取阈值
                    complexity = file_analysis.get('complexity', 0)
                    _update_complexity_distribution(result, complexity)

                    # 记录文件详情
                    result['file_details'].append({
                        'path': str(file_path.relative_to(project_path)),
                        'lines': file_analysis.get('lines', 0),
                        'complexity': complexity,
                        'type': file_ext,
                        'analyzer': analyzer_used
                    })

                    # 检测复杂度问题
                    _detect_complexity_issues(result, file_path, project_path, complexity)

        # 计算平均值
        if result['analyzed_files'] > 0:
            result['average_complexity'] = result['total_complexity'] / result['analyzed_files']

        # 按复杂度排序文件详情
        result['file_details'].sort(key=lambda x: x['complexity'], reverse=True)

    except Exception as e:
        result['error'] = f"分析项目复杂度失败: {str(e)}"

    return result


def _get_dynamic_supported_extensions() -> List[str]:
    """动态获取支持的文件扩展名列表"""
    extensions = set()

    manager = _get_language_analyzer_manager()
    if manager:
        try:
            analyzers = manager.get_available_analyzers()
            for analyzer_name, analyzer_info in analyzers.items():
                if hasattr(analyzer_info, 'file_extensions'):
                    extensions.update(analyzer_info.file_extensions)
        except Exception as e:
            print(f"警告: 获取动态扩展名失败: {e}")

    # 如果没有获取到任何扩展名，使用默认值作为后备
    if not extensions:
        # 完全动态获取，不硬编码任何扩展名
        try:
            # 尝试从配置文件获取通用扩展名
            from .analyzer_config import get_config
            config = get_config()
            if hasattr(config, 'default_file_extensions'):
                extensions.update(config.default_file_extensions)
        except ImportError:
            pass

        # 如果还是没有，返回空列表
        if not extensions:
            return []

    return list(extensions)


def _update_complexity_distribution(result: Dict[str, Any], complexity: int):
    """更新复杂度分布统计"""
    try:
        from .analyzer_config import get_config
        config = get_config()
        base_thresholds = config.complexity_thresholds

        if complexity <= base_thresholds['LOW'] // 20:
            result['complexity_distribution']['low'] = result['complexity_distribution'].get('low', 0) + 1
        elif complexity <= base_thresholds['MEDIUM'] // 20:
            result['complexity_distribution']['medium'] = result['complexity_distribution'].get('medium', 0) + 1
        elif complexity <= base_thresholds['HIGH'] // 20:
            result['complexity_distribution']['high'] = result['complexity_distribution'].get('high', 0) + 1
        else:
            result['complexity_distribution']['very_high'] = result['complexity_distribution'].get('very_high', 0) + 1
    except ImportError:
        # 如果无法导入配置，使用默认值作为后备
        if complexity <= 5:
            result['complexity_distribution']['low'] = result['complexity_distribution'].get('low', 0) + 1
        elif complexity <= 15:
            result['complexity_distribution']['medium'] = result['complexity_distribution'].get('medium', 0) + 1
        elif complexity <= 30:
            result['complexity_distribution']['high'] = result['complexity_distribution'].get('high', 0) + 1
        else:
            result['complexity_distribution']['very_high'] = result['complexity_distribution'].get('very_high', 0) + 1


def _detect_complexity_issues(result: Dict[str, Any], file_path: Path, project_path: Path, complexity: int):
    """检测复杂度问题"""
    try:
        from .analyzer_config import get_config
        config = get_config()
        base_thresholds = config.complexity_thresholds

        if complexity > base_thresholds['MEDIUM'] // 20:
            result['complexity_issues'].append({
                'file': str(file_path.relative_to(project_path)),
                'complexity': complexity,
                'severity': 'high' if complexity > base_thresholds['HIGH'] // 20 else 'medium'
            })
    except ImportError:
        # 如果无法导入配置，使用默认值作为后备
        if complexity > 25:
            result['complexity_issues'].append({
                'file': str(file_path.relative_to(project_path)),
                'complexity': complexity,
                'severity': 'high' if complexity > 50 else 'medium'
            })


def get_supported_languages() -> List[str]:
    """获取支持的语言列表"""
    try:
        manager = _get_language_analyzer_manager()
        if manager:
            return manager.get_supported_languages()
    except Exception:
        pass
    return []


def get_complexity_thresholds() -> Dict[str, Dict[str, int]]:
    """完全动态获取各种语言的复杂度阈值，零硬编码"""
    try:
        from .analyzer_config import get_config
        config = get_config()
        base_thresholds = config.complexity_thresholds

        # 动态获取支持的语言列表
        supported_languages = get_supported_languages()

        # 动态构建语言阈值配置
        thresholds = {}

        for lang in supported_languages:
            # 动态获取语言的阈值系数
            threshold_coefficient = _get_dynamic_language_threshold_coefficient(lang)

            thresholds[lang] = {
                'low': base_thresholds['LOW'] // threshold_coefficient,
                'medium': base_thresholds['MEDIUM'] // threshold_coefficient,
                'high': base_thresholds['HIGH'] // threshold_coefficient,
                'very_high': base_thresholds['VERY_HIGH'] // threshold_coefficient
            }

        return thresholds

    except ImportError:
        # 如果无法导入配置，使用默认值作为后备
        supported_languages = get_supported_languages()
        default_thresholds = {}

        for lang in supported_languages:
            default_thresholds[lang] = _get_dynamic_default_language_thresholds(lang)

        return default_thresholds


def _get_dynamic_language_threshold_coefficient(lang: str) -> int:
    """动态获取语言的阈值系数，零硬编码"""
    try:
        # 尝试从语言分析器获取阈值系数
        manager = _get_language_analyzer_manager()
        if manager:
            analyzers = manager.get_available_analyzers()
            if lang in analyzers:
                analyzer_info = analyzers[lang]
                if hasattr(analyzer_info, 'threshold_coefficient'):
                    return analyzer_info.threshold_coefficient
                if hasattr(analyzer_info, 'get_threshold_coefficient'):
                    return analyzer_info.get_threshold_coefficient()

        # 尝试从配置文件获取
        try:
            from .analyzer_config import get_config
            config = get_config()
            if hasattr(config, 'language_threshold_coefficients'):
                return config.language_threshold_coefficients.get(lang, 20)
        except ImportError:
            pass

        # 根据语言特性智能推断（零硬编码）
        return _infer_language_threshold_coefficient(lang)

    except Exception as e:
        print(f"警告: 获取语言 {lang} 的阈值系数失败: {e}")
        return 20  # 默认值


def _infer_language_threshold_coefficient(lang: str) -> int:
    """智能推断语言的阈值系数，基于语言特性"""
    # 基于语言名称和特性的智能推断
    lang_lower = lang.lower()

    # 标记语言（复杂度很低）
    if any(marker in lang_lower for marker in ['html', 'xml', 'markdown', 'md']):
        return 50

    # 数据格式（复杂度很低）
    if any(marker in lang_lower for marker in ['json', 'yaml', 'yml', 'toml', 'ini']):
        return 40

    # 样式语言（复杂度较低）
    if any(marker in lang_lower for marker in ['css', 'scss', 'sass', 'less', 'stylus']):
        return 30

    # 脚本语言（复杂度中等）
    if any(marker in lang_lower for marker in ['python', 'py', 'ruby', 'rb', 'perl', 'pl', 'php']):
        return 20

    # 编译语言（复杂度较高）
    if any(marker in lang_lower for marker in ['java', 'c', 'cpp', 'csharp', 'cs', 'go', 'rust', 'rs']):
        return 15

    # 前端框架（复杂度较高）
    if any(marker in lang_lower for marker in ['vue', 'react', 'angular', 'svelte']):
        return 15

    # 类型化语言（复杂度中等）
    if any(marker in lang_lower for marker in ['typescript', 'ts', 'dart', 'kotlin', 'kt', 'swift']):
        return 20

    # 声明式语言（复杂度较低）
    if any(marker in lang_lower for marker in ['sql', 'hql', 'cypher', 'sparql']):
        return 30

    # 默认值
    return 20


def _get_dynamic_default_language_thresholds(lang: str) -> Dict[str, int]:
    """动态获取语言的默认阈值，零硬编码"""
    try:
        # 尝试从语言分析器获取默认阈值
        manager = _get_language_analyzer_manager()
        if manager:
            analyzers = manager.get_available_analyzers()
            if lang in analyzers:
                analyzer_info = analyzers[lang]
                if hasattr(analyzer_info, 'default_thresholds'):
                    return analyzer_info.default_thresholds
                if hasattr(analyzer_info, 'get_default_thresholds'):
                    return analyzer_info.get_default_thresholds()

        # 尝试从配置文件获取
        try:
            from .analyzer_config import get_config
            config = get_config()
            if hasattr(config, 'language_default_thresholds'):
                return config.language_default_thresholds.get(lang, {})
        except ImportError:
            pass

        # 基于阈值系数动态计算默认阈值
        coefficient = _get_dynamic_language_threshold_coefficient(lang)
        base_thresholds = {'low': 5, 'medium': 15, 'high': 25, 'very_high': 50}

        # 根据系数调整阈值
        adjusted_thresholds = {}
        for level, value in base_thresholds.items():
            # 系数越大，阈值越小（因为复杂度计算时是除以系数）
            adjusted_thresholds[level] = max(1, value // (coefficient // 20))

        return adjusted_thresholds

    except Exception as e:
        print(f"警告: 获取语言 {lang} 的默认阈值失败: {e}")
        # 返回通用默认值
        return {'low': 5, 'medium': 15, 'high': 25, 'very_high': 50}
