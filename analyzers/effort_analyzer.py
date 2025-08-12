#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工时评估分析模块
包含工时计算、复杂度因子计算、理解成本计算等功能
"""

from typing import Dict, Any, List, Tuple


def calculate_work_effort_estimate(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """计算工作投入评估"""
    result = {
        'module_efforts': {},
        'new_module_efforts': {},
        'total_effort': 0,
        'risk_factors': [],
        'recommendations': []
    }

    try:
        # 计算各模块的工时
        module_analysis = analysis_results.get('module_analysis', {})
        all_module_stats = {}

        for module_name, module_data in module_analysis.items():
            stats = module_data.get('complexity', {})
            all_module_stats[module_name] = stats

            # 计算模块工时
            module_effort = _calculate_module_effort(module_name, stats, all_module_stats)
            result['module_efforts'][module_name] = module_effort

            result['total_effort'] += module_effort.get('total_effort', 0)

        # 计算新模块开发工时
        project_stats = {
            'total_lines': sum(stats.get('total_lines', 0) for stats in all_module_stats.values()),
            'total_files': sum(stats.get('total_files', 0) for stats in all_module_stats.values()),
            'total_complexity': sum(stats.get('total_complexity', 0) for stats in all_module_stats.values()),
            'module_count': len(module_analysis),
            'tech_stack_diversity': len(analysis_results.get('language_analysis', {})),
            'total_sql_tables': analysis_results.get('architecture_analysis', {}).get('total_sql_tables', 0),
            'average_complexity': sum(stats.get('total_complexity', 0) for stats in all_module_stats.values()) / max(len(all_module_stats), 1)
        }

        # 计算前后端文件数量
        backend_files = 0
        frontend_files = 0
        language_analysis = analysis_results.get('language_analysis', {})

        for language, stats in language_analysis.items():
            if language in ['java', 'python', 'c#', 'go', 'php']:
                backend_files += stats.get('files', 0)
            elif language in ['javascript', 'typescript', 'vue', 'react', 'html', 'css']:
                frontend_files += stats.get('files', 0)

        project_stats['backend_files'] = backend_files
        project_stats['frontend_files'] = frontend_files

        result['new_module_efforts'] = _estimate_new_module_efforts(project_stats)

        # 计算理解成本
        result['understanding_cost'] = _calculate_understanding_cost_for_new_modules(project_stats)

        # 生成项目上下文信息
        result['project_context'] = {
            'module_count': project_stats['module_count'],
            'tech_stack_diversity': project_stats['tech_stack_diversity'],
            'total_lines': project_stats['total_lines'],
            'total_files': project_stats['total_files'],
            'total_complexity': project_stats['total_complexity']
        }

        # 识别风险因素
        result['risk_factors'] = _identify_risk_factors_for_new_modules(project_stats)

        # 生成开发建议
        result['recommendations'] = _generate_development_recommendations_for_new_modules(project_stats)

    except Exception as e:
        result['error'] = f"计算工时评估失败: {str(e)}"

    return result


def _calculate_module_effort(module_name: str, stats: Dict[str, Any], all_module_stats: Dict[str, Any]) -> Dict[str, Any]:
    """计算单个模块的工时"""
    result = {
        'module_name': module_name,
        'size_factor': 0,
        'complexity_factor': 0,
        'understanding_factor': 0,
        'risk_factor': 0,
        'total_effort': 0,
        'size_category': '',
        'risk_factors': [],
        'recommendations': []
    }

    try:
        # 计算各种因子
        result['size_factor'] = _calculate_size_factor(stats)
        result['complexity_factor'] = _calculate_complexity_factor(stats)
        result['understanding_factor'] = _calculate_understanding_factor(module_name, stats, all_module_stats)
        result['risk_factor'] = _calculate_risk_factor(stats)

        # 确定模块大小类别
        result['size_category'] = _determine_module_size(stats)

        # 计算总工时
        base_effort = 5.0  # 基础工时
        result['total_effort'] = base_effort * (1 + result['size_factor']) * (1 + result['complexity_factor']) * (1 + result['understanding_factor']) * (1 + result['risk_factor'])

        # 识别风险因素
        total_java_lines = 0
        total_sql_lines = 0
        total_sql_tables = 0  # 这里需要从架构分析中获取

        # 安全地计算语言统计
        for s in all_module_stats.values():
            if isinstance(s, dict):
                language_stats = s.get('language_stats', {})
                if isinstance(language_stats, dict):
                    java_stats = language_stats.get('java', {})
                    if isinstance(java_stats, dict):
                        total_java_lines += java_stats.get('lines', 0)

                    sql_stats = language_stats.get('sql', {})
                    if isinstance(sql_stats, dict):
                        total_sql_lines += sql_stats.get('lines', 0)

        result['risk_factors'] = _identify_risk_factors(stats, total_java_lines, total_sql_lines, total_sql_tables)

        # 生成开发建议
        result['recommendations'] = _generate_development_recommendations(stats, result['total_effort'])

    except Exception as e:
        result['error'] = f"计算模块工时失败: {str(e)}"

    return result


def _calculate_complexity_factor(stats: Dict[str, Any]) -> float:
    """计算复杂度因子"""
    complexity = stats.get('total_complexity', 0)
    lines = stats.get('total_lines', 0)

    if lines == 0:
        return 0.0

    # 基于圈复杂度和代码行数的复杂度因子
    complexity_per_line = complexity / lines

    if complexity_per_line < 0.1:
        return 0.1
    elif complexity_per_line < 0.3:
        return 0.3
    elif complexity_per_line < 0.5:
        return 0.5
    elif complexity_per_line < 0.8:
        return 0.8
    else:
        return 1.2


def _calculate_understanding_factor(module_name: str, stats: Dict[str, Any], all_module_stats: Dict[str, Any]) -> float:
    """计算理解因子"""
    # 基于模块大小和复杂度的理解因子
    lines = stats.get('total_lines', 0)
    complexity = stats.get('total_complexity', 0)

    factor = 0.0

    # 代码行数影响
    if lines > 10000:
        factor += 0.8
    elif lines > 5000:
        factor += 0.5
    elif lines > 1000:
        factor += 0.3
    elif lines > 100:
        factor += 0.1

    # 复杂度影响
    if complexity > 1000:
        factor += 0.6
    elif complexity > 500:
        factor += 0.4
    elif complexity > 100:
        factor += 0.2
    elif complexity > 50:
        factor += 0.1

    # 模块数量影响
    module_count = len(all_module_stats)
    if module_count > 10:
        factor += 0.3
    elif module_count > 5:
        factor += 0.2
    elif module_count > 2:
        factor += 0.1

    return min(factor, 2.0)


def _calculate_risk_factor(stats: Dict[str, Any]) -> float:
    """计算风险因子"""
    # 基于代码质量和复杂度的风险因子
    complexity = stats.get('total_complexity', 0)
    lines = stats.get('total_lines', 0)

    if lines == 0:
        return 0.0

    complexity_per_line = complexity / lines

    if complexity_per_line > 1.0:
        return 0.8
    elif complexity_per_line > 0.7:
        return 0.6
    elif complexity_per_line > 0.5:
        return 0.4
    elif complexity_per_line > 0.3:
        return 0.2
    else:
        return 0.1


def _calculate_size_factor(stats: Dict[str, Any]) -> float:
    """计算大小因子"""
    lines = stats.get('total_lines', 0)

    if lines > 10000:
        return 2.0
    elif lines > 5000:
        return 1.5
    elif lines > 1000:
        return 1.0
    elif lines > 500:
        return 0.7
    elif lines > 100:
        return 0.4
    else:
        return 0.2


def _determine_module_size(stats: Dict[str, Any]) -> str:
    """确定模块大小类别"""
    lines = stats.get('total_lines', 0)

    if lines > 10000:
        return '大型模块'
    elif lines > 5000:
        return '中型模块'
    elif lines > 1000:
        return '小型模块'
    else:
        return '微型模块'


def _calculate_understanding_cost(module_stats: Dict[str, Any], total_java_lines: int, total_sql_lines: int) -> float:
    """计算理解成本"""
    # 基于模块复杂度和项目规模的理解成本
    complexity = module_stats.get('total_complexity', 0)
    lines = module_stats.get('total_lines', 0)

    base_cost = 2.0

    # 复杂度影响
    if complexity > 1000:
        base_cost += 3.0
    elif complexity > 500:
        base_cost += 2.0
    elif complexity > 100:
        base_cost += 1.0

    # 代码行数影响
    if lines > 10000:
        base_cost += 2.0
    elif lines > 5000:
        base_cost += 1.5
    elif lines > 1000:
        base_cost += 1.0

    # 项目规模影响
    if total_java_lines > 100000:
        base_cost += 1.5
    elif total_java_lines > 50000:
        base_cost += 1.0

    if total_sql_lines > 10000:
        base_cost += 1.0

    return base_cost


def _identify_risk_factors(module_stats: Dict[str, Any], total_java_lines: int, total_sql_lines: int, total_sql_tables: int) -> List[str]:
    """识别风险因素"""
    risk_factors = []

    complexity = module_stats.get('total_complexity', 0)
    lines = module_stats.get('total_lines', 0)

    if complexity > 1000:
        risk_factors.append('代码复杂度极高，维护困难')
    elif complexity > 500:
        risk_factors.append('代码复杂度较高，需要重构')

    if lines > 10000:
        risk_factors.append('模块过大，建议拆分')
    elif lines > 5000:
        risk_factors.append('模块较大，需要关注')

    if complexity > 0 and lines > 0:
        complexity_per_line = complexity / lines
        if complexity_per_line > 1.0:
            risk_factors.append('圈复杂度密度过高，存在质量风险')
        elif complexity_per_line > 0.7:
            risk_factors.append('圈复杂度密度较高，建议优化')

    return risk_factors


def _generate_development_recommendations(module_stats: Dict[str, Any], total_effort: float) -> List[str]:
    """生成开发建议"""
    recommendations = []

    complexity = module_stats.get('total_complexity', 0)
    lines = module_stats.get('total_lines', 0)

    if complexity > 1000:
        recommendations.append('建议进行代码重构，降低复杂度')
        recommendations.append('考虑将复杂逻辑拆分为多个小函数')

    if lines > 10000:
        recommendations.append('建议将大模块拆分为多个小模块')
        recommendations.append('实施模块化设计，提高可维护性')

    if total_effort > 50:
        recommendations.append('开发周期较长，建议分阶段实施')
        recommendations.append('考虑并行开发，缩短交付时间')

    if complexity > 0 and lines > 0:
        complexity_per_line = complexity / lines
        if complexity_per_line > 0.8:
            recommendations.append('建议增加单元测试覆盖率')
            recommendations.append('考虑使用设计模式简化逻辑')

    return recommendations


def _estimate_new_module_efforts(project_stats: Dict[str, Any]) -> Dict[str, Any]:
    """估算新模块开发工时"""
    result = {
        'small_module': {},
        'medium_module': {},
        'large_module': {}
    }

    try:
        # 从配置文件读取基础工时（人天）
        try:
            from .analyzer_config import AnalyzerConfig
            config = AnalyzerConfig()
            effort_base_values = config.effort_base_values

            small_backend_base = effort_base_values.get('SMALL_MODULE', {}).get('BACKEND', 2.0)
            small_frontend_base = effort_base_values.get('SMALL_MODULE', {}).get('FRONTEND', 1.5)
            medium_backend_base = effort_base_values.get('MEDIUM_MODULE', {}).get('BACKEND', 6.0)
            medium_frontend_base = effort_base_values.get('MEDIUM_MODULE', {}).get('FRONTEND', 4.5)
            large_backend_base = effort_base_values.get('LARGE_MODULE', {}).get('BACKEND', 12.0)
            large_frontend_base = effort_base_values.get('LARGE_MODULE', {}).get('FRONTEND', 9.0)
        except ImportError:
            # 如果无法导入配置，使用默认值
            small_backend_base = 2.0
            small_frontend_base = 1.5
            medium_backend_base = 6.0
            medium_frontend_base = 4.5
            large_backend_base = 12.0
            large_frontend_base = 9.0

        # 计算项目复杂度因子
        complexity_factor = _calculate_project_complexity_factor(project_stats)

        # 计算项目理解因子
        understanding_factor = _calculate_project_understanding_factor(project_stats)

        # 计算集成因子
        integration_factor = _calculate_integration_factor(project_stats)

        # 小型模块
        result['small_module'] = {
            'backend': round(small_backend_base * complexity_factor * understanding_factor * integration_factor, 1),
            'frontend': round(small_frontend_base * complexity_factor * understanding_factor * integration_factor, 1),
            'total': round((small_backend_base + small_frontend_base) * complexity_factor * understanding_factor * integration_factor, 1)
        }

        # 中型模块
        result['medium_module'] = {
            'backend': round(medium_backend_base * complexity_factor * understanding_factor * integration_factor, 1),
            'frontend': round(medium_frontend_base * complexity_factor * understanding_factor * integration_factor, 1),
            'total': round((medium_backend_base + medium_frontend_base) * complexity_factor * understanding_factor * integration_factor, 1)
        }

        # 大型模块
        result['large_module'] = {
            'backend': round(large_backend_base * complexity_factor * understanding_factor * integration_factor, 1),
            'frontend': round(large_frontend_base * complexity_factor * understanding_factor * integration_factor, 1),
            'total': round((large_backend_base + large_frontend_base) * complexity_factor * understanding_factor * integration_factor, 1)
        }

    except Exception as e:
        result['error'] = f"估算新模块工时失败: {str(e)}"

    return result


def _calculate_project_complexity_factor(project_stats: Dict[str, Any]) -> float:
    """计算项目复杂度因子"""
    factor = 1.0

    total_lines = project_stats.get('total_lines', 0)
    total_files = project_stats.get('total_files', 0)
    tech_stack_diversity = project_stats.get('tech_stack_diversity', 0)
    module_count = project_stats.get('module_count', 0)
    total_sql_tables = project_stats.get('total_sql_tables', 0)
    average_complexity = project_stats.get('average_complexity', 0)

    # 代码行数影响
    if total_lines > 100000:
        factor += 0.4
    elif total_lines > 50000:
        factor += 0.3
    elif total_lines > 20000:
        factor += 0.2
    elif total_lines > 10000:
        factor += 0.15
    elif total_lines > 5000:
        factor += 0.1
    elif total_lines > 2000:
        factor += 0.05
    elif total_lines > 500:
        factor += 0.02

    # 文件数量影响
    if total_files > 500:
        factor += 0.3
    elif total_files > 200:
        factor += 0.2
    elif total_files > 100:
        factor += 0.15
    elif total_files > 50:
        factor += 0.1
    elif total_files > 20:
        factor += 0.05
    elif total_files > 10:
        factor += 0.02

    # 技术栈多样性影响
    if tech_stack_diversity >= 6:
        factor += 0.3
    elif tech_stack_diversity >= 5:
        factor += 0.2
    elif tech_stack_diversity >= 4:
        factor += 0.15
    elif tech_stack_diversity >= 3:
        factor += 0.1
    elif tech_stack_diversity >= 2:
        factor += 0.05
    elif tech_stack_diversity >= 1:
        factor += 0.02

    # 模块数量影响
    if module_count > 15:
        factor += 0.25
    elif module_count > 10:
        factor += 0.2
    elif module_count > 5:
        factor += 0.15
    elif module_count > 3:
        factor += 0.1
    elif module_count > 1:
        factor += 0.05

    # 数据库表数量影响
    if total_sql_tables > 200:
        factor += 0.2
    elif total_sql_tables > 100:
        factor += 0.15
    elif total_sql_tables > 50:
        factor += 0.1
    elif total_sql_tables > 20:
        factor += 0.05
    elif total_sql_tables > 10:
        factor += 0.02

    # 平均复杂度影响
    if average_complexity > 1000:
        factor += 0.25
    elif average_complexity > 500:
        factor += 0.2
    elif average_complexity > 200:
        factor += 0.15
    elif average_complexity > 100:
        factor += 0.1
    elif average_complexity > 50:
        factor += 0.05

    # 从配置文件读取复杂度因子最大值
    try:
        from .analyzer_config import AnalyzerConfig
        config = AnalyzerConfig()
        max_factor = config.factor_limits.get('COMPLEXITY', 2.0)
    except ImportError:
        max_factor = 2.0

    return min(factor, max_factor)


def _calculate_project_understanding_factor(project_stats: Dict[str, Any]) -> float:
    """计算项目理解因子"""
    factor = 1.0

    total_lines = project_stats.get('total_lines', 0)
    total_files = project_stats.get('total_files', 0)
    tech_stack_diversity = project_stats.get('tech_stack_diversity', 0)
    module_count = project_stats.get('module_count', 0)
    total_sql_tables = project_stats.get('total_sql_tables', 0)

    # 代码行数影响
    if total_lines > 500000:
        factor += 0.4
    elif total_lines > 300000:
        factor += 0.3
    elif total_lines > 200000:
        factor += 0.25
    elif total_lines > 100000:
        factor += 0.2
    elif total_lines > 50000:
        factor += 0.15
    elif total_lines > 10000:
        factor += 0.1
    elif total_lines > 5000:
        factor += 0.05
    elif total_lines > 2000:
        factor += 0.02

    # 文件数量影响
    if total_files > 1000:
        factor += 0.3
    elif total_files > 500:
        factor += 0.2
    elif total_files > 200:
        factor += 0.15
    elif total_files > 100:
        factor += 0.1
    elif total_files > 50:
        factor += 0.05
    elif total_files > 20:
        factor += 0.02

    # 技术栈多样性影响
    if tech_stack_diversity >= 8:
        factor += 0.3
    elif tech_stack_diversity >= 6:
        factor += 0.2
    elif tech_stack_diversity >= 5:
        factor += 0.15
    elif tech_stack_diversity >= 4:
        factor += 0.1
    elif tech_stack_diversity >= 3:
        factor += 0.05
    elif tech_stack_diversity >= 2:
        factor += 0.02

    # 模块数量影响
    if module_count > 20:
        factor += 0.3
    elif module_count > 15:
        factor += 0.2
    elif module_count > 10:
        factor += 0.15
    elif module_count > 5:
        factor += 0.1
    elif module_count > 2:
        factor += 0.05

    # 数据库复杂度影响
    if total_sql_tables > 200:
        factor += 0.25
    elif total_sql_tables > 100:
        factor += 0.2
    elif total_sql_tables > 50:
        factor += 0.15
    elif total_sql_tables > 20:
        factor += 0.1
    elif total_sql_tables > 10:
        factor += 0.05

    # 从配置文件读取理解因子最大值
    try:
        from .analyzer_config import AnalyzerConfig
        config = AnalyzerConfig()
        max_factor = config.factor_limits.get('UNDERSTANDING', 1.8)
    except ImportError:
        max_factor = 1.8

    return min(factor, max_factor)


def _calculate_integration_factor(project_stats: Dict[str, Any]) -> float:
    """计算集成因子"""
    factor = 1.0

    tech_stack_diversity = project_stats.get('tech_stack_diversity', 0)
    module_count = project_stats.get('module_count', 0)
    total_sql_tables = project_stats.get('total_sql_tables', 0)
    average_complexity = project_stats.get('average_complexity', 0)

    # 前后端分离影响
    backend_files = project_stats.get('backend_files', 0)
    frontend_files = project_stats.get('frontend_files', 0)

    # 前后端文件比例影响
    if backend_files > 0 and frontend_files > 0:
        total_files = backend_files + frontend_files
        backend_ratio = backend_files / total_files
        frontend_ratio = frontend_files / total_files

        # 如果前后端文件数量相对均衡，增加集成复杂度
        if 0.3 <= backend_ratio <= 0.7:
            factor += 0.1
        elif 0.2 <= backend_ratio <= 0.8:
            factor += 0.05
        else:
            factor += 0.02

    # 技术栈多样性影响
    if tech_stack_diversity >= 8:
        factor += 0.25
    elif tech_stack_diversity >= 6:
        factor += 0.2
    elif tech_stack_diversity >= 5:
        factor += 0.15
    elif tech_stack_diversity >= 4:
        factor += 0.1
    elif tech_stack_diversity >= 3:
        factor += 0.05
    elif tech_stack_diversity >= 2:
        factor += 0.02

    # 模块数量影响
    if module_count > 20:
        factor += 0.25
    elif module_count > 15:
        factor += 0.2
    elif module_count > 10:
        factor += 0.15
    elif module_count > 5:
        factor += 0.1
    elif module_count > 2:
        factor += 0.05

    # 数据库复杂度影响
    if total_sql_tables > 200:
        factor += 0.2
    elif total_sql_tables > 100:
        factor += 0.15
    elif total_sql_tables > 50:
        factor += 0.1
    elif total_sql_tables > 20:
        factor += 0.05
    elif total_sql_tables > 10:
        factor += 0.02

    # 平均复杂度影响
    if average_complexity > 1000:
        factor += 0.2
    elif average_complexity > 500:
        factor += 0.15
    elif average_complexity > 200:
        factor += 0.1
    elif average_complexity > 100:
        factor += 0.05
    elif average_complexity > 50:
        factor += 0.02

    # 从配置文件读取集成因子最大值
    try:
        from .analyzer_config import AnalyzerConfig
        config = AnalyzerConfig()
        max_factor = config.factor_limits.get('INTEGRATION', 1.5)
    except ImportError:
        max_factor = 1.5

    return min(factor, max_factor)


def _calculate_understanding_cost_for_new_modules(project_stats: Dict[str, Any]) -> float:
    """计算新模块的理解成本"""
    base_cost = 1.5

    total_lines = project_stats.get('total_lines', 0)
    total_files = project_stats.get('total_files', 0)
    tech_stack_diversity = project_stats.get('tech_stack_diversity', 0)
    module_count = project_stats.get('module_count', 0)
    total_sql_tables = project_stats.get('total_sql_tables', 0)
    average_complexity = project_stats.get('average_complexity', 0)

    # 项目规模影响
    if total_lines > 500000:
        base_cost += 6.0
    elif total_lines > 300000:
        base_cost += 5.0
    elif total_lines > 200000:
        base_cost += 4.0
    elif total_lines > 100000:
        base_cost += 3.0
    elif total_lines > 50000:
        base_cost += 2.0
    elif total_lines > 10000:
        base_cost += 1.0

    # 技术栈多样性影响
    if tech_stack_diversity >= 8:
        base_cost += 4.0
    elif tech_stack_diversity >= 6:
        base_cost += 3.0
    elif tech_stack_diversity >= 5:
        base_cost += 2.5
    elif tech_stack_diversity >= 4:
        base_cost += 2.0
    elif tech_stack_diversity >= 3:
        base_cost += 1.5
    elif tech_stack_diversity >= 2:
        base_cost += 1.0

    # 模块数量影响
    if module_count > 20:
        base_cost += 4.0
    elif module_count > 15:
        base_cost += 3.0
    elif module_count > 10:
        base_cost += 2.5
    elif module_count > 5:
        base_cost += 1.5
    elif module_count > 2:
        base_cost += 1.0

    # 数据库复杂度影响
    if total_sql_tables > 200:
        base_cost += 3.0
    elif total_sql_tables > 100:
        base_cost += 2.0
    elif total_sql_tables > 50:
        base_cost += 1.5
    elif total_sql_tables > 20:
        base_cost += 1.0
    elif total_sql_tables > 10:
        base_cost += 0.5

    # 文件数量影响
    if total_files > 1000:
        base_cost += 2.0
    elif total_files > 500:
        base_cost += 1.5
    elif total_files > 200:
        base_cost += 1.0
    elif total_files > 100:
        base_cost += 0.5

    # 代码复杂度影响
    if average_complexity > 1000:
        base_cost += 2.0
    elif average_complexity > 500:
        base_cost += 1.5
    elif average_complexity > 200:
        base_cost += 1.0
    elif average_complexity > 100:
        base_cost += 0.5

    return base_cost


def _identify_risk_factors_for_new_modules(project_stats: Dict[str, Any]) -> List[str]:
    """识别新模块开发的风险因素"""
    risk_factors = []

    total_lines = project_stats.get('total_lines', 0)
    total_files = project_stats.get('total_files', 0)
    tech_stack_diversity = project_stats.get('tech_stack_diversity', 0)
    module_count = project_stats.get('module_count', 0)
    total_sql_tables = project_stats.get('total_sql_tables', 0)
    average_complexity = project_stats.get('average_complexity', 0)

    # 项目规模风险
    if total_lines > 500000:
        risk_factors.append('项目规模极大，新模块集成风险高')
    elif total_lines > 300000:
        risk_factors.append('项目规模很大，需要充分了解现有架构')

    # 技术栈风险
    if tech_stack_diversity >= 8:
        risk_factors.append('技术栈极其复杂，学习成本高')
    elif tech_stack_diversity >= 6:
        risk_factors.append('技术栈复杂，需要多技能开发人员')

    # 模块数量风险
    if module_count > 20:
        risk_factors.append('模块数量过多，依赖关系复杂')
    elif module_count > 15:
        risk_factors.append('模块数量较多，需要梳理依赖关系')

    # 数据库复杂度风险
    if total_sql_tables > 200:
        risk_factors.append('数据库表数量过多，数据模型复杂')
    elif total_sql_tables > 100:
        risk_factors.append('数据库表数量较多，需要了解数据关系')

    # 代码复杂度风险
    if average_complexity > 1000:
        risk_factors.append('代码复杂度极高，维护困难')
    elif average_complexity > 500:
        risk_factors.append('代码复杂度较高，需要重构')

    return risk_factors


def _generate_development_recommendations_for_new_modules(project_stats: Dict[str, Any]) -> List[str]:
    """生成新模块开发的建议"""
    recommendations = []

    total_lines = project_stats.get('total_lines', 0)
    total_files = project_stats.get('total_files', 0)
    tech_stack_diversity = project_stats.get('tech_stack_diversity', 0)
    module_count = project_stats.get('module_count', 0)
    total_sql_tables = project_stats.get('total_sql_tables', 0)
    average_complexity = project_stats.get('average_complexity', 0)

    # 项目规模建议
    if total_lines > 500000:
        recommendations.append('建议分阶段开发，先实现核心功能')
        recommendations.append('考虑使用微服务架构，降低集成复杂度')
    elif total_lines > 300000:
        recommendations.append('建议采用增量开发方式，逐步集成')

    # 技术栈建议
    if tech_stack_diversity >= 8:
        recommendations.append('建议使用统一的技术栈，降低学习成本')
        recommendations.append('考虑引入技术架构师，统一技术决策')
    elif tech_stack_diversity >= 6:
        recommendations.append('建议制定技术规范，统一开发标准')

    # 模块化建议
    if module_count > 20:
        recommendations.append('建议重构模块结构，降低耦合度')
        recommendations.append('考虑使用领域驱动设计，明确模块边界')
    elif module_count > 15:
        recommendations.append('建议梳理模块依赖关系，优化架构')

    # 数据库建议
    if total_sql_tables > 200:
        recommendations.append('建议优化数据库设计，减少表数量')
        recommendations.append('考虑使用数据库设计工具，管理表关系')
    elif total_sql_tables > 100:
        recommendations.append('建议建立数据库文档，明确表结构')

    # 代码质量建议
    if average_complexity > 1000:
        recommendations.append('建议重构复杂代码，降低圈复杂度')
        recommendations.append('考虑使用设计模式，简化业务逻辑')
    elif average_complexity > 500:
        recommendations.append('建议优化代码结构，提高可读性')

    return recommendations
