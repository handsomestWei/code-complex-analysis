#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL代码复杂度分析器
专门分析SQL代码的复杂度、结构和质量指标
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
import logging
from ..language_analyzer_manager import LanguageAnalyzer

logger = logging.getLogger(__name__)


class SQLAnalyzer(LanguageAnalyzer):
    """SQL语言分析器"""

    @property
    def language_name(self) -> str:
        return "sql"

    @property
    def file_extensions(self) -> List[str]:
        return ['.sql']

    @property
    def analyzer_name(self) -> str:
        return "SQL复杂度分析器"

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
        return file_path.suffix.lower() == '.sql'

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """分析SQL文件复杂度"""
        return analyze_sql_complexity_detailed(file_path)


def analyze_sql_complexity_detailed(file_path: Path) -> Dict[str, Any]:
    """详细分析SQL代码复杂度"""
    result = {
        'file_path': str(file_path),
        'file_type': 'sql',
        'lines': 0,
        'code_lines': 0,
        'comment_lines': 0,
        'blank_lines': 0,
        'statements': 0,
        'queries': 0,
        'tables': 0,
        'views': 0,
        'procedures': 0,
        'joins': 0,
        'subqueries': 0,
        'functions': 0,
        'complexity': 0,
        'complexity_score': 0,
        'nested_levels': 0,
        'max_nested_level': 0,
        'statement_details': [],
        'table_details': [],
        'code_smells': []
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = content.split('\n')
        result['lines'] = len(lines)

        # 统计空行和注释行
        for line in lines:
            line = line.strip()
            if not line:
                result['blank_lines'] += 1
            elif line.startswith('--') or line.startswith('/*') or line.startswith('*'):
                result['comment_lines'] += 1

        result['code_lines'] = result['lines'] - result['blank_lines'] - result['comment_lines']

        # 分析SQL语句
        sql_statements = re.split(r';\s*\n', content, flags=re.IGNORECASE)

        for statement in sql_statements:
            statement = statement.strip()
            if not statement:
                continue

            result['statements'] += 1

            # 初始化变量
            table_matches = []
            join_matches = []
            subquery_matches = []
            function_matches = []
            nested_level = 0

            # 检测查询类型
            if re.search(r'\bSELECT\b', statement, re.IGNORECASE):
                result['queries'] += 1

                # 统计表数量
                table_matches = re.findall(r'\bFROM\s+(\w+)', statement, re.IGNORECASE)
                result['tables'] += len(table_matches)

                # 统计JOIN数量
                join_matches = re.findall(r'\bJOIN\s+(\w+)', statement, re.IGNORECASE)
                result['joins'] += len(join_matches)

                # 统计子查询数量
                subquery_matches = re.findall(r'\(\s*SELECT', statement, re.IGNORECASE)
                result['subqueries'] += len(subquery_matches)

                # 统计函数数量
                function_matches = re.findall(r'\b(\w+)\s*\(', statement, re.IGNORECASE)
                result['functions'] += len(function_matches)

                # 计算嵌套级别
                nested_level = statement.count('(') - statement.count(')')
                result['max_nested_level'] = max(result['max_nested_level'], nested_level)

            # 检测视图定义
            if re.search(r'\bCREATE\s+VIEW\b', statement, re.IGNORECASE):
                result['views'] += 1

            # 检测存储过程定义
            if re.search(r'\bCREATE\s+PROCEDURE\b', statement, re.IGNORECASE):
                result['procedures'] += 1

            # 检测表定义
            if re.search(r'\bCREATE\s+TABLE\b', statement, re.IGNORECASE):
                result['tables'] += 1

                # 记录语句详情
                statement_type = 'SELECT'
                if re.search(r'\bINSERT\b', statement, re.IGNORECASE):
                    statement_type = 'INSERT'
                elif re.search(r'\bUPDATE\b', statement, re.IGNORECASE):
                    statement_type = 'UPDATE'
                elif re.search(r'\bDELETE\b', statement, re.IGNORECASE):
                    statement_type = 'DELETE'
                elif re.search(r'\bCREATE\b', statement, re.IGNORECASE):
                    statement_type = 'CREATE'
                elif re.search(r'\bALTER\b', statement, re.IGNORECASE):
                    statement_type = 'ALTER'
                elif re.search(r'\bDROP\b', statement, re.IGNORECASE):
                    statement_type = 'DROP'

                result['statement_details'].append({
                    'type': statement_type,
                    'tables': table_matches,
                    'joins': join_matches,
                    'subqueries': subquery_matches,
                    'functions': function_matches,
                    'nested_level': nested_level
                })

        # 计算复杂度
        result['complexity'] = _calculate_sql_complexity(result)
        result['complexity_score'] = result['complexity']

        # 检测代码异味
        result['code_smells'] = _detect_sql_code_smells(result)

    except Exception as e:
        logger.error(f"分析SQL文件失败 {file_path}: {e}")
        result['error'] = f"分析失败: {str(e)}"

    return result


def _calculate_sql_complexity(analysis_result: Dict[str, Any]) -> int:
    """计算SQL代码复杂度"""
    complexity = 1  # 基础复杂度

    # 基于查询数量
    complexity += analysis_result['queries'] * 2

    # 基于表数量
    complexity += analysis_result['tables'] * 1

    # 基于JOIN数量
    complexity += analysis_result['joins'] * 2

    # 基于子查询数量
    complexity += analysis_result['subqueries'] * 3

    # 基于函数数量
    complexity += analysis_result['functions'] // 2

    # 基于嵌套级别
    complexity += analysis_result['max_nested_level'] * 2

    return complexity


def _detect_sql_code_smells(analysis_result: Dict[str, Any]) -> List[str]:
    """检测SQL代码异味"""
    smells = []

    # 检查查询数量过多
    if analysis_result['queries'] > 20:
        smells.append("查询数量过多，可能存在性能问题")

    # 检查表数量过多
    if analysis_result['tables'] > 10:
        smells.append("涉及表数量过多，可能存在设计问题")

    # 检查JOIN数量过多
    if analysis_result['joins'] > 8:
        smells.append("JOIN数量过多，可能存在性能问题")

    # 检查子查询数量过多
    if analysis_result['subqueries'] > 5:
        smells.append("子查询数量过多，可能存在性能问题")

    # 检查嵌套级别过深
    if analysis_result['max_nested_level'] > 3:
        smells.append("嵌套级别过深，可能存在可读性问题")

    # 检查函数数量过多
    if analysis_result['functions'] > 20:
        smells.append("函数调用过多，可能存在性能问题")

    return smells


def analyze_sql_architecture(file_path: Path) -> Dict[str, Any]:
    """分析SQL代码架构"""
    complexity_result = analyze_sql_complexity_detailed(file_path)

    if 'error' in complexity_result:
        return complexity_result

    architecture_result = {
        'file_path': str(file_path),
        'architecture_type': 'unknown',
        'query_patterns': [],
        'performance_level': 'good',
        'maintainability_level': 'high',
        'recommendations': []
    }

    # 分析架构类型
    if complexity_result['queries'] == 0:
        architecture_result['architecture_type'] = 'ddl_only'
    elif complexity_result['queries'] <= 5:
        architecture_result['architecture_type'] = 'simple_queries'
    elif complexity_result['queries'] <= 15:
        architecture_result['architecture_type'] = 'moderate_queries'
    else:
        architecture_result['architecture_type'] = 'complex_queries'

    # 分析性能级别
    if complexity_result['joins'] <= 3 and complexity_result['subqueries'] <= 2:
        architecture_result['performance_level'] = 'excellent'
    elif complexity_result['joins'] <= 6 and complexity_result['subqueries'] <= 4:
        architecture_result['performance_level'] = 'good'
    elif complexity_result['joins'] <= 10 and complexity_result['subqueries'] <= 6:
        architecture_result['performance_level'] = 'fair'
    else:
        architecture_result['performance_level'] = 'poor'

    # 分析可维护性级别
    if complexity_result['max_nested_level'] <= 2 and complexity_result['statements'] <= 10:
        architecture_result['maintainability_level'] = 'excellent'
    elif complexity_result['max_nested_level'] <= 3 and complexity_result['statements'] <= 20:
        architecture_result['maintainability_level'] = 'good'
    elif complexity_result['max_nested_level'] <= 4 and complexity_result['statements'] <= 30:
        architecture_result['maintainability_level'] = 'fair'
    else:
        architecture_result['maintainability_level'] = 'poor'

    # 生成建议
    if architecture_result['performance_level'] in ['fair', 'poor']:
        architecture_result['recommendations'].append("考虑优化JOIN和子查询，提高查询性能")

    if architecture_result['maintainability_level'] in ['fair', 'poor']:
        architecture_result['recommendations'].append("考虑简化复杂查询，提高可维护性")

    if complexity_result['tables'] > 8:
        architecture_result['recommendations'].append("考虑是否所有表都是必需的，减少不必要的表关联")

    return architecture_result


def analyze_sql_security(file_path: Path) -> Dict[str, Any]:
    """分析SQL代码安全性"""
    result = {
        'security_issues': [],
        'vulnerability_level': 'low',
        'recommendations': []
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 检测SQL注入风险
        if 'EXEC(' in content.upper() or 'EXECUTE(' in content.upper():
            result['security_issues'].append('动态SQL执行 (EXEC/EXECUTE)')
            result['vulnerability_level'] = 'high'

        if 'sp_executesql' in content.lower():
            result['security_issues'].append('动态SQL执行 (sp_executesql)')
            result['vulnerability_level'] = 'medium'

        # 检测权限问题
        if 'GRANT ALL' in content.upper():
            result['security_issues'].append('过度授权 (GRANT ALL)')
            result['vulnerability_level'] = 'medium'

        # 生成安全建议
        if result['vulnerability_level'] == 'high':
            result['recommendations'].append('使用参数化查询替代动态SQL')
            result['recommendations'].append('实施最小权限原则')

        if result['vulnerability_level'] == 'medium':
            result['recommendations'].append('审查动态SQL的使用')
            result['recommendations'].append('限制数据库用户权限')

    except Exception as e:
        result['error'] = f"分析SQL安全性失败: {str(e)}"

    return result
