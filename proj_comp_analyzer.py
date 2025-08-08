#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用项目代码复杂度分析工具
专门针对多模块、多技术栈的复杂项目进行分析
"""

import os
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any, Optional
import argparse
from datetime import datetime
import subprocess
import sys

class GenericComplexityAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results = {
            'project_info': {},
            'module_analysis': {},
            'language_analysis': {},
            'complexity_metrics': {},
            'architecture_analysis': {},
            'dependency_analysis': {},
            'frontend_analysis': {},
            'backend_analysis': {},
            'mobile_analysis': {},
            'scada_analysis': {},
            'view_analysis': {},
            'recommendations': {}
        }

        # 技术栈分类
        self.tech_stacks = {
            'backend': ['java', 'xml', 'properties', 'sql', 'sh'],
            'frontend': ['typescript', 'javascript', 'vue', 'scss', 'css', 'html'],
            'mobile': ['vue', 'javascript', 'json'],
            'config': ['yaml', 'json', 'xml', 'properties'],
            'docs': ['markdown', 'html']
        }

        # 语言扩展名映射
        self.language_extensions = {
            'java': ['.java'],
            'typescript': ['.ts', '.tsx'],
            'javascript': ['.js', '.jsx'],
            'vue': ['.vue'],
            'scss': ['.scss', '.sass'],
            'css': ['.css'],
            'html': ['.html', '.htm'],
            'xml': ['.xml'],
            'json': ['.json'],
            'yaml': ['.yml', '.yaml'],
            'properties': ['.properties'],
            'sql': ['.sql'],
            'sh': ['.sh', '.bash'],
            'dockerfile': ['Dockerfile'],
            'markdown': ['.md'],
            'python': ['.py']
        }

        # 忽略模式
        self.ignore_patterns = [
            'node_modules', '.git', 'target', 'dist', 'build',
            '.idea', '.vscode', 'coverage', '.nyc_output',
            '*.min.js', '*.min.css', '*.map'
        ]

    def detect_module_type(self, module_path: Path) -> str:
        """检测模块类型"""
        if (module_path / 'pom.xml').exists():
            return 'Java/Maven项目'
        elif (module_path / 'package.json').exists():
            package_path = module_path / 'package.json'
            try:
                with open(package_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                dependencies = package_data.get('dependencies', {})
                dev_dependencies = package_data.get('devDependencies', {})

                # 检查是否是Vue项目
                if 'vue' in dependencies or 'vue' in dev_dependencies:
                    return 'Vue前端项目'
                elif 'react' in dependencies or 'react' in dev_dependencies:
                    return 'React前端项目'
                elif 'angular' in dependencies or 'angular' in dev_dependencies:
                    return 'Angular前端项目'
                else:
                    return 'Node.js项目'
            except:
                return 'Node.js项目'
        elif (module_path / 'build.gradle').exists():
            return 'Java/Gradle项目'
        elif (module_path / 'requirements.txt').exists() or (module_path / 'setup.py').exists():
            return 'Python项目'
        elif (module_path / 'Cargo.toml').exists():
            return 'Rust项目'
        elif (module_path / 'go.mod').exists():
            return 'Go项目'
        else:
            # 检查文件类型来推断
            java_files = len(list(module_path.rglob('*.java')))
            ts_files = len(list(module_path.rglob('*.ts')))
            js_files = len(list(module_path.rglob('*.js')))
            vue_files = len(list(module_path.rglob('*.vue')))

            if java_files > 0:
                return 'Java项目'
            elif vue_files > 0:
                return 'Vue项目'
            elif ts_files > 0:
                return 'TypeScript项目'
            elif js_files > 0:
                return 'JavaScript项目'
            else:
                return '通用项目'

    def is_vue_project(self, module_path: Path) -> bool:
        """判断是否是Vue项目"""
        # 检查package.json中的Vue依赖
        package_path = module_path / 'package.json'
        if package_path.exists():
            try:
                with open(package_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                dependencies = package_data.get('dependencies', {})
                dev_dependencies = package_data.get('devDependencies', {})
                return 'vue' in dependencies or 'vue' in dev_dependencies
            except:
                pass

        # 检查是否有.vue文件
        vue_files = list(module_path.rglob('*.vue'))
        return len(vue_files) > 0

    def analyze_maven_project(self, module_path: Path) -> Dict[str, Any]:
        """分析Maven项目结构"""
        pom_path = module_path / 'pom.xml'
        if not pom_path.exists():
            return {}

        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()

            # 提取项目信息
            group_id = root.find('.//{http://maven.apache.org/POM/4.0.0}groupId')
            artifact_id = root.find('.//{http://maven.apache.org/POM/4.0.0}artifactId')
            version = root.find('.//{http://maven.apache.org/POM/4.0.0}version')

            # 统计依赖
            dependencies = root.findall('.//{http://maven.apache.org/POM/4.0.0}dependency')
            dependency_count = len(dependencies)

            # 统计子模块
            modules = root.findall('.//{http://maven.apache.org/POM/4.0.0}module')
            module_count = len(modules)

            return {
                'group_id': group_id.text if group_id is not None else 'unknown',
                'artifact_id': artifact_id.text if artifact_id is not None else 'unknown',
                'version': version.text if version is not None else 'unknown',
                'dependencies': dependency_count,
                'sub_modules': module_count,
                'has_pom': True
            }
        except Exception as e:
            print(f"Error parsing pom.xml in {module_path}: {e}")
            return {'has_pom': False}

    def analyze_package_json(self, module_path: Path) -> Dict[str, Any]:
        """分析Node.js项目结构"""
        package_path = module_path / 'package.json'
        if not package_path.exists():
            return {}

        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)

            dependencies = len(package_data.get('dependencies', {}))
            dev_dependencies = len(package_data.get('devDependencies', {}))

            return {
                'name': package_data.get('name', 'unknown'),
                'version': package_data.get('version', 'unknown'),
                'dependencies': dependencies,
                'dev_dependencies': dev_dependencies,
                'scripts': len(package_data.get('scripts', {})),
                'has_package_json': True
            }
        except Exception as e:
            print(f"Error parsing package.json in {module_path}: {e}")
            return {'has_package_json': False}

    def analyze_vue_project_structure(self, module_path: Path) -> Dict[str, Any]:
        """分析Vue项目结构"""
        vue_analysis = {
            'components': 0,
            'views': 0,
            'stores': 0,
            'utils': 0,
            'api': 0,
            'assets': 0,
            'router_files': 0
        }

        # 统计目录结构
        for root, dirs, files in os.walk(module_path):
            rel_path = Path(root).relative_to(module_path)

            for file in files:
                if file.endswith('.vue'):
                    if 'components' in str(rel_path):
                        vue_analysis['components'] += 1
                    elif 'views' in str(rel_path):
                        vue_analysis['views'] += 1
                elif file.endswith('.ts') or file.endswith('.js'):
                    if 'store' in str(rel_path):
                        vue_analysis['stores'] += 1
                    elif 'utils' in str(rel_path):
                        vue_analysis['utils'] += 1
                    elif 'api' in str(rel_path):
                        vue_analysis['api'] += 1
                    elif 'router' in str(rel_path):
                        vue_analysis['router_files'] += 1

        return vue_analysis

    def analyze_java_complexity_detailed(self, file_path: Path) -> Dict[str, Any]:
        """详细分析Java文件复杂度"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 基础统计
            lines = content.split('\n')
            total_lines = len(lines)

            # 类分析
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?'
            classes = re.findall(class_pattern, content)

            # 方法分析
            method_pattern = r'(public|private|protected)?\s*(static\s+)?(\w+)\s+(\w+)\s*\([^)]*\)\s*\{'
            methods = re.findall(method_pattern, content)

            # 字段分析
            field_pattern = r'(public|private|protected)?\s*(static\s+)?(\w+)\s+(\w+)\s*;'
            fields = re.findall(field_pattern, content)

            # 圈复杂度计算
            complexity = 1
            complexity += len(re.findall(r'\bif\b', content))
            complexity += len(re.findall(r'\bfor\b', content))
            complexity += len(re.findall(r'\bwhile\b', content))
            complexity += len(re.findall(r'\bcase\b', content))
            complexity += len(re.findall(r'\bcatch\b', content))
            complexity += len(re.findall(r'\|\||&&', content))
            complexity += len(re.findall(r'\?', content))  # 三元运算符

            # 依赖注入分析
            annotations = len(re.findall(r'@\w+', content))

            # 异常处理
            try_catch_blocks = len(re.findall(r'try\s*\{', content))

            return {
                'classes': len(classes),
                'methods': len(methods),
                'fields': len(fields),
                'cyclomatic_complexity': complexity,
                'annotations': annotations,
                'try_catch_blocks': try_catch_blocks,
                'total_lines': total_lines,
                'class_details': [{'name': c[0], 'extends': c[1], 'implements': c[2]} for c in classes]
            }
        except Exception as e:
            print(f"Error analyzing Java file {file_path}: {e}")
            return {}

    def analyze_typescript_complexity_detailed(self, file_path: Path) -> Dict[str, Any]:
        """详细分析TypeScript文件复杂度"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 基础统计
            lines = content.split('\n')
            total_lines = len(lines)

            # 函数分析
            function_pattern = r'function\s+(\w+)'
            arrow_function_pattern = r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
            async_function_pattern = r'async\s+function\s+(\w+)'

            functions = re.findall(function_pattern, content)
            arrow_functions = re.findall(arrow_function_pattern, content)
            async_functions = re.findall(async_function_pattern, content)

            # 类分析
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?'
            classes = re.findall(class_pattern, content)

            # 接口分析
            interface_pattern = r'interface\s+(\w+)'
            interfaces = re.findall(interface_pattern, content)

            # 类型定义
            type_pattern = r'type\s+(\w+)'
            types = re.findall(type_pattern, content)

            # 圈复杂度
            complexity = 1
            complexity += len(re.findall(r'\bif\b', content))
            complexity += len(re.findall(r'\bfor\b', content))
            complexity += len(re.findall(r'\bwhile\b', content))
            complexity += len(re.findall(r'\bcase\b', content))
            complexity += len(re.findall(r'\bcatch\b', content))
            complexity += len(re.findall(r'\|\||&&', content))
            complexity += len(re.findall(r'\?', content))

            # 导入导出分析
            imports = len(re.findall(r'import\s+', content))
            exports = len(re.findall(r'export\s+', content))

            return {
                'functions': len(functions) + len(arrow_functions) + len(async_functions),
                'classes': len(classes),
                'interfaces': len(interfaces),
                'types': len(types),
                'cyclomatic_complexity': complexity,
                'imports': imports,
                'exports': exports,
                'async_functions': len(async_functions),
                'total_lines': total_lines
            }
        except Exception as e:
            print(f"Error analyzing TypeScript file {file_path}: {e}")
            return {}

    def analyze_javascript_complexity_detailed(self, file_path: Path) -> Dict[str, Any]:
        """详细分析JavaScript文件复杂度"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 基础统计
            lines = content.split('\n')
            total_lines = len(lines)

            # 函数分析
            function_pattern = r'function\s+(\w+)'
            arrow_function_pattern = r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
            async_function_pattern = r'async\s+function\s+(\w+)'

            functions = re.findall(function_pattern, content)
            arrow_functions = re.findall(arrow_function_pattern, content)
            async_functions = re.findall(async_function_pattern, content)

            # 类分析
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
            classes = re.findall(class_pattern, content)

            # 圈复杂度
            complexity = 1
            complexity += len(re.findall(r'\bif\b', content))
            complexity += len(re.findall(r'\bfor\b', content))
            complexity += len(re.findall(r'\bwhile\b', content))
            complexity += len(re.findall(r'\bcase\b', content))
            complexity += len(re.findall(r'\bcatch\b', content))
            complexity += len(re.findall(r'\|\||&&', content))
            complexity += len(re.findall(r'\?', content))

            # 导入导出分析
            imports = len(re.findall(r'import\s+', content))
            exports = len(re.findall(r'export\s+', content))

            # 回调函数
            callbacks = len(re.findall(r'\.then\(', content)) + len(re.findall(r'\.catch\(', content))

            return {
                'functions': len(functions) + len(arrow_functions) + len(async_functions),
                'classes': len(classes),
                'cyclomatic_complexity': complexity,
                'imports': imports,
                'exports': exports,
                'async_functions': len(async_functions),
                'callbacks': callbacks,
                'total_lines': total_lines
            }
        except Exception as e:
            print(f"Error analyzing JavaScript file {file_path}: {e}")
            return {}

    def analyze_sql_complexity_detailed(self, file_path: Path) -> Dict[str, Any]:
        """详细分析SQL文件复杂度"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 基础统计
            lines = content.split('\n')
            total_lines = len(lines)
            non_empty_lines = len([line for line in lines if line.strip()])

            # 表分析
            create_table_pattern = r'CREATE\s+(?:TEMPORARY\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)'
            tables = re.findall(create_table_pattern, content, re.IGNORECASE)

            # 视图分析
            create_view_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMPORARY\s+)?VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)'
            views = re.findall(create_view_pattern, content, re.IGNORECASE)

            # 索引分析
            create_index_pattern = r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)'
            indexes = re.findall(create_index_pattern, content, re.IGNORECASE)

            # 存储过程分析
            create_procedure_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+([^\s(]+)'
            procedures = re.findall(create_procedure_pattern, content, re.IGNORECASE)

            # 函数分析
            create_function_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+([^\s(]+)'
            functions = re.findall(create_function_pattern, content, re.IGNORECASE)

            # 触发器分析
            create_trigger_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER\s+([^\s(]+)'
            triggers = re.findall(create_trigger_pattern, content, re.IGNORECASE)

            # 查询复杂度分析
            select_count = len(re.findall(r'\bSELECT\s+', content, re.IGNORECASE))
            insert_count = len(re.findall(r'\bINSERT\s+', content, re.IGNORECASE))
            update_count = len(re.findall(r'\bUPDATE\s+', content, re.IGNORECASE))
            delete_count = len(re.findall(r'\bDELETE\s+', content, re.IGNORECASE))

            # JOIN复杂度
            join_count = len(re.findall(r'\bJOIN\s+', content, re.IGNORECASE))
            left_join_count = len(re.findall(r'\bLEFT\s+JOIN\s+', content, re.IGNORECASE))
            right_join_count = len(re.findall(r'\bRIGHT\s+JOIN\s+', content, re.IGNORECASE))
            inner_join_count = len(re.findall(r'\bINNER\s+JOIN\s+', content, re.IGNORECASE))

            # 子查询分析
            subquery_count = len(re.findall(r'\(\s*SELECT\s+', content, re.IGNORECASE))

            # 条件复杂度
            where_count = len(re.findall(r'\bWHERE\s+', content, re.IGNORECASE))
            group_by_count = len(re.findall(r'\bGROUP\s+BY\s+', content, re.IGNORECASE))
            having_count = len(re.findall(r'\bHAVING\s+', content, re.IGNORECASE))
            order_by_count = len(re.findall(r'\bORDER\s+BY\s+', content, re.IGNORECASE))

            # 事务分析
            transaction_count = len(re.findall(r'\bBEGIN\s+TRANSACTION\b', content, re.IGNORECASE))
            commit_count = len(re.findall(r'\bCOMMIT\b', content, re.IGNORECASE))
            rollback_count = len(re.findall(r'\bROLLBACK\b', content, re.IGNORECASE))

            # 计算SQL复杂度分数
            complexity_score = 1
            complexity_score += len(tables) * 2  # 每个表增加2分
            complexity_score += len(views) * 1.5  # 每个视图增加1.5分
            complexity_score += len(procedures) * 3  # 每个存储过程增加3分
            complexity_score += len(functions) * 2  # 每个函数增加2分
            complexity_score += len(triggers) * 2.5  # 每个触发器增加2.5分
            complexity_score += join_count * 0.5  # 每个JOIN增加0.5分
            complexity_score += subquery_count * 1  # 每个子查询增加1分
            complexity_score += (where_count + group_by_count + having_count) * 0.3  # 每个条件子句增加0.3分

            return {
                'total_lines': total_lines,
                'non_empty_lines': non_empty_lines,
                'tables': len(tables),
                'views': len(views),
                'indexes': len(indexes),
                'procedures': len(procedures),
                'functions': len(functions),
                'triggers': len(triggers),
                'select_queries': select_count,
                'insert_queries': insert_count,
                'update_queries': update_count,
                'delete_queries': delete_count,
                'joins': join_count,
                'left_joins': left_join_count,
                'right_joins': right_join_count,
                'inner_joins': inner_join_count,
                'subqueries': subquery_count,
                'where_clauses': where_count,
                'group_by_clauses': group_by_count,
                'having_clauses': having_count,
                'order_by_clauses': order_by_count,
                'transactions': transaction_count,
                'commits': commit_count,
                'rollbacks': rollback_count,
                'complexity_score': complexity_score,
                'table_names': tables,
                'view_names': views,
                'procedure_names': procedures,
                'function_names': functions,
                'trigger_names': triggers
            }
        except Exception as e:
            print(f"Error analyzing SQL file {file_path}: {e}")
            return {}

    def analyze_vue_complexity_detailed(self, file_path: Path) -> Dict[str, Any]:
        """详细分析Vue文件复杂度"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 基础统计
            lines = content.split('\n')
            total_lines = len(lines)

            # 模板分析
            template_match = re.search(r'<template[^>]*>(.*?)</template>', content, re.DOTALL)
            template_complexity = 0
            if template_match:
                template_content = template_match.group(1)
                template_complexity = len(re.findall(r'<[a-zA-Z][^>]*>', template_content))

            # Script分析
            script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            script_analysis = {}
            total_functions = 0
            total_classes = 0
            cyclomatic_complexity = 1

            if script_match:
                script_content = script_match.group(1)

                # Vue组件选项
                script_analysis['methods'] = len(re.findall(r'methods\s*:\s*\{', script_content))
                script_analysis['computed'] = len(re.findall(r'computed\s*:\s*\{', script_content))
                script_analysis['watchers'] = len(re.findall(r'watch\s*:\s*\{', script_content))
                script_analysis['props'] = len(re.findall(r'props\s*:\s*\{', script_content))
                script_analysis['emits'] = len(re.findall(r'emits\s*:\s*\[', script_content))

                # 组合式API
                script_analysis['refs'] = len(re.findall(r'ref\(', script_content))
                script_analysis['reactives'] = len(re.findall(r'reactive\(', script_content))
                script_analysis['computed_props'] = len(re.findall(r'computed\(', script_content))
                script_analysis['watchers_comp'] = len(re.findall(r'watch\(', script_content))

                # 函数和类分析（用于与其他文件类型保持一致）
                function_pattern = r'function\s+(\w+)|(\w+)\s*:\s*function|\(\s*\)\s*=>'
                total_functions = len(re.findall(function_pattern, script_content))

                class_pattern = r'class\s+(\w+)'
                total_classes = len(re.findall(class_pattern, script_content))

                # 简单的圈复杂度计算
                cyclomatic_complexity += len(re.findall(r'\bif\b', script_content))
                cyclomatic_complexity += len(re.findall(r'\bfor\b', script_content))
                cyclomatic_complexity += len(re.findall(r'\bwhile\b', script_content))
                cyclomatic_complexity += len(re.findall(r'\bcase\b', script_content))
                cyclomatic_complexity += len(re.findall(r'\bcatch\b', script_content))

            # Style分析
            style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
            style_lines = 0
            if style_match:
                style_content = style_match.group(1)
                style_lines = len(style_content.split('\n'))

            return {
                'template_elements': template_complexity,
                'script_analysis': script_analysis,
                'style_lines': style_lines,
                'total_lines': total_lines,
                'functions': total_functions,
                'classes': total_classes,
                'cyclomatic_complexity': cyclomatic_complexity
            }
        except Exception as e:
            print(f"Error analyzing Vue file {file_path}: {e}")
            return {}

    def calculate_work_effort_estimate(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """基于现有项目分析结果估算二次开发新模块的工作量"""
        effort_estimate = {
            'new_module_efforts': {},  # 新模块的工作量估算
            'project_context': {},  # 项目上下文信息
            'understanding_cost': 0,
            'risk_factors': [],
            'development_recommendations': []
        }

        # 从模块分析中统计项目整体情况
        project_stats = {
            'total_java_lines': 0,
            'total_java_files': 0,
            'total_ts_files': 0,
            'total_vue_files': 0,
            'total_js_files': 0,
            'total_sql_lines': 0,
            'total_sql_tables': 0,
            'total_sql_views': 0,
            'total_complexity': 0,
            'module_count': 0,
            'tech_stack_diversity': 0
        }

        # 统计项目整体情况
        for module_name, module_analysis in analysis_results.get('module_analysis', {}).items():
            complexity_metrics = module_analysis.get('complexity_metrics', {})

            # Java文件统计
            java_files = complexity_metrics.get('java_files', [])
            java_lines = sum(java_file.get('analysis', {}).get('total_lines', 0) for java_file in java_files)
            project_stats['total_java_lines'] += java_lines
            project_stats['total_java_files'] += len(java_files)

            # TypeScript文件统计
            ts_files = complexity_metrics.get('typescript_files', [])
            project_stats['total_ts_files'] += len(ts_files)

            # Vue文件统计
            vue_files = complexity_metrics.get('vue_files', [])
            project_stats['total_vue_files'] += len(vue_files)

            # JavaScript文件统计
            js_files = complexity_metrics.get('javascript_files', [])
            project_stats['total_js_files'] += len(js_files)

            # SQL文件统计
            sql_files = complexity_metrics.get('sql_files', [])
            sql_lines = sum(sql_file.get('analysis', {}).get('total_lines', 0) for sql_file in sql_files)
            sql_tables = sum(sql_file.get('analysis', {}).get('tables', 0) for sql_file in sql_files)
            sql_views = sum(sql_file.get('analysis', {}).get('views', 0) for sql_file in sql_files)
            project_stats['total_sql_lines'] += sql_lines
            project_stats['total_sql_tables'] += sql_tables
            project_stats['total_sql_views'] += sql_views

            project_stats['total_complexity'] += complexity_metrics.get('total_complexity', 0)
            project_stats['module_count'] += 1

        # 计算技术栈多样性
        tech_stack_count = 0
        if project_stats['total_java_files'] > 0: tech_stack_count += 1
        if project_stats['total_ts_files'] > 0: tech_stack_count += 1
        if project_stats['total_vue_files'] > 0: tech_stack_count += 1
        if project_stats['total_js_files'] > 0: tech_stack_count += 1
        if project_stats['total_sql_lines'] > 0: tech_stack_count += 1
        project_stats['tech_stack_diversity'] = tech_stack_count

        effort_estimate['project_context'] = project_stats

        # 估算新模块的工作量
        new_module_efforts = self._estimate_new_module_efforts(project_stats)
        effort_estimate['new_module_efforts'] = new_module_efforts

        # 计算理解成本
        understanding_cost = self._calculate_understanding_cost_for_new_modules(project_stats)
        effort_estimate['understanding_cost'] = understanding_cost

        # 风险因素识别
        effort_estimate['risk_factors'] = self._identify_risk_factors_for_new_modules(project_stats)

        # 开发建议
        effort_estimate['development_recommendations'] = self._generate_development_recommendations_for_new_modules(project_stats)

        return effort_estimate

    def _calculate_module_effort(self, module_name: str, stats: Dict[str, Any], all_module_stats: Dict[str, Any]) -> Dict[str, Any]:
        """计算单个模块的二次开发工作量"""

        # 基础开发工作量（基于代码行数）
        backend_base_effort = stats['java_lines'] / 100  # 每天100行Java代码
        sql_base_effort = stats['sql_lines'] / 50  # 每天50行SQL代码
        frontend_base_effort = (stats['ts_files'] + stats['vue_files']) * 0.5  # 每个文件0.5天

        # 复杂度系数计算
        complexity_factor = self._calculate_complexity_factor(stats)

        # 理解成本系数
        understanding_factor = self._calculate_understanding_factor(module_name, stats, all_module_stats)

        # 风险系数
        risk_factor = self._calculate_risk_factor(stats)

        # 模块规模系数
        size_factor = self._calculate_size_factor(stats)

        # 二次开发特殊系数
        secondary_dev_factor = 1.2  # 二次开发通常比新开发需要更多时间理解现有代码

        # 计算最终工作量
        backend_effort = (backend_base_effort + sql_base_effort) * complexity_factor * understanding_factor * risk_factor * size_factor * secondary_dev_factor
        frontend_effort = frontend_base_effort * complexity_factor * understanding_factor * risk_factor * size_factor * secondary_dev_factor

        # 确定模块规模
        module_size = self._determine_module_size(stats)

        return {
            'module_size': module_size,
            'backend_effort': round(backend_effort, 1),
            'frontend_effort': round(frontend_effort, 1),
            'total_effort': round(backend_effort + frontend_effort, 1),
            'complexity_factor': round(complexity_factor, 2),
            'understanding_factor': round(understanding_factor, 2),
            'risk_factor': round(risk_factor, 2),
            'size_factor': round(size_factor, 2),
            'factors_breakdown': {
                'backend_base': round(backend_base_effort + sql_base_effort, 1),
                'frontend_base': round(frontend_base_effort, 1),
                'complexity_impact': round(complexity_factor, 2),
                'understanding_impact': round(understanding_factor, 2),
                'risk_impact': round(risk_factor, 2),
                'size_impact': round(size_factor, 2)
            }
        }

    def _calculate_complexity_factor(self, stats: Dict[str, Any]) -> float:
        """计算复杂度系数"""
        total_complexity = stats['total_complexity']

        if total_complexity > 1000:
            return 1.8  # 高复杂度
        elif total_complexity > 500:
            return 1.4  # 中复杂度
        elif total_complexity > 100:
            return 1.2  # 低复杂度
        else:
            return 1.0  # 简单

    def _calculate_understanding_factor(self, module_name: str, stats: Dict[str, Any], all_module_stats: Dict[str, Any]) -> float:
        """计算理解成本系数"""
        factor = 1.0

        # 基于代码量的理解成本
        total_lines = stats['java_lines'] + stats['sql_lines']
        if total_lines > 10000:
            factor += 0.5  # 代码量大，需要更多理解时间
        elif total_lines > 5000:
            factor += 0.3
        elif total_lines > 1000:
            factor += 0.1

        # 基于技术栈多样性的理解成本
        tech_stack_count = sum([
            1 if stats['java_files'] > 0 else 0,
            1 if stats['ts_files'] > 0 else 0,
            1 if stats['vue_files'] > 0 else 0,
            1 if stats['js_files'] > 0 else 0,
            1 if stats['sql_files'] > 0 else 0
        ])

        if tech_stack_count > 3:
            factor += 0.3  # 多技术栈，需要更多学习时间
        elif tech_stack_count > 2:
            factor += 0.2

        # 基于数据库复杂度的理解成本
        if stats['sql_tables'] > 50:
            factor += 0.4  # 数据库结构复杂
        elif stats['sql_tables'] > 20:
            factor += 0.2

        return factor

    def _calculate_risk_factor(self, stats: Dict[str, Any]) -> float:
        """计算风险系数"""
        factor = 1.0

        # 基于代码复杂度的风险
        if stats['total_complexity'] > 1000:
            factor += 0.3

        # 基于SQL复杂度的风险
        if stats['sql_complexity'] > 100:
            factor += 0.2

        # 基于文件数量的风险
        total_files = stats['java_files'] + stats['ts_files'] + stats['vue_files'] + stats['js_files']
        if total_files > 100:
            factor += 0.2

        return factor

    def _calculate_size_factor(self, stats: Dict[str, Any]) -> float:
        """计算模块规模系数"""
        total_files = stats['java_files'] + stats['ts_files'] + stats['vue_files'] + stats['js_files'] + stats['sql_files']

        if total_files > 200:
            return 1.3  # 大型模块
        elif total_files > 50:
            return 1.1  # 中型模块
        else:
            return 1.0  # 小型模块

    def _determine_module_size(self, stats: Dict[str, Any]) -> str:
        """确定模块规模"""
        total_files = stats['java_files'] + stats['ts_files'] + stats['vue_files'] + stats['js_files'] + stats['sql_files']
        total_lines = stats['java_lines'] + stats['sql_lines']

        if total_files > 200 or total_lines > 10000:
            return '大型模块'
        elif total_files > 50 or total_lines > 5000:
            return '中型模块'
        else:
            return '小型模块'

    def _calculate_understanding_cost(self, module_stats: Dict[str, Any], total_java_lines: int, total_sql_lines: int) -> float:
        """计算总体理解成本"""
        understanding_cost = 0

        # 基础理解成本
        if total_java_lines > 0:
            understanding_cost += total_java_lines / 200  # 每天理解200行Java代码

        if total_sql_lines > 0:
            understanding_cost += total_sql_lines / 100  # 每天理解100行SQL代码

        # 模块数量影响
        module_count = len(module_stats)
        if module_count > 5:
            understanding_cost *= 1.5  # 多模块项目需要更多理解时间
        elif module_count > 3:
            understanding_cost *= 1.2

        return round(understanding_cost, 1)

    def _identify_risk_factors(self, module_stats: Dict[str, Any], total_java_lines: int, total_sql_lines: int, total_sql_tables: int) -> List[str]:
        """识别风险因素"""
        risk_factors = []

        if total_java_lines > 100000:
            risk_factors.append('后端代码量巨大，需要深入了解业务逻辑和架构设计')
        elif total_java_lines > 50000:
            risk_factors.append('后端代码量较大，需要充分理解现有业务逻辑')

        if total_sql_lines > 10000:
            risk_factors.append('SQL代码量较大，需要数据库设计和优化经验')

        if total_sql_tables > 100:
            risk_factors.append('数据库表结构复杂，需要深入了解数据模型和关系')

        # 检查各模块的复杂度
        for module_name, stats in module_stats.items():
            if stats['total_complexity'] > 1000:
                risk_factors.append(f'模块 {module_name} 复杂度极高，需要资深开发人员')
            elif stats['total_complexity'] > 500:
                risk_factors.append(f'模块 {module_name} 复杂度较高，需要充分测试')

        return risk_factors

    def _generate_development_recommendations(self, module_stats: Dict[str, Any], total_effort: float) -> List[str]:
        """生成开发建议"""
        recommendations = []

        if total_effort > 100:
            recommendations.append('项目规模较大，建议采用敏捷开发方法，分阶段交付')
            recommendations.append('需要建立完善的代码审查和测试机制')
            recommendations.append('建议安排资深开发人员负责架构设计和代码审查')

        elif total_effort > 50:
            recommendations.append('项目规模中等，建议采用迭代开发方式')
            recommendations.append('需要建立基本的代码规范和测试流程')

        # 基于技术栈的建议
        has_java = any(stats['java_files'] > 0 for stats in module_stats.values())
        has_frontend = any(stats['ts_files'] > 0 or stats['vue_files'] > 0 for stats in module_stats.values())
        has_sql = any(stats['sql_files'] > 0 for stats in module_stats.values())

        if has_java and has_frontend:
            recommendations.append('前后端分离架构，建议前后端并行开发')

        if has_sql:
            recommendations.append('涉及数据库操作，建议进行充分的数据库设计和优化')

        return recommendations

    def _estimate_new_module_efforts(self, project_stats: Dict[str, Any]) -> Dict[str, Any]:
        """估算新模块的工作量"""
        new_module_efforts = {
            'small_module': {
                'description': '小型模块 (基础功能，简单业务逻辑)',
                'backend_effort': 0,
                'frontend_effort': 0,
                'total_effort': 0,
                'factors': {}
            },
            'medium_module': {
                'description': '中型模块 (中等复杂度，包含多个功能点)',
                'backend_effort': 0,
                'frontend_effort': 0,
                'total_effort': 0,
                'factors': {}
            },
            'large_module': {
                'description': '大型模块 (复杂业务逻辑，多模块集成)',
                'backend_effort': 0,
                'frontend_effort': 0,
                'total_effort': 0,
                'factors': {}
            }
        }

        # 基于项目复杂度计算基础工作量
        project_complexity_factor = self._calculate_project_complexity_factor(project_stats)
        understanding_factor = self._calculate_project_understanding_factor(project_stats)
        integration_factor = self._calculate_integration_factor(project_stats)

        # 小型模块估算
        small_backend_base = 3.0  # 基础CRUD操作
        small_frontend_base = 2.0  # 简单页面
        new_module_efforts['small_module']['backend_effort'] = round(
            small_backend_base * project_complexity_factor * understanding_factor * integration_factor, 1
        )
        new_module_efforts['small_module']['frontend_effort'] = round(
            small_frontend_base * project_complexity_factor * understanding_factor * integration_factor, 1
        )
        new_module_efforts['small_module']['total_effort'] = round(
            new_module_efforts['small_module']['backend_effort'] + new_module_efforts['small_module']['frontend_effort'], 1
        )
        new_module_efforts['small_module']['factors'] = {
            'project_complexity_factor': round(project_complexity_factor, 2),
            'understanding_factor': round(understanding_factor, 2),
            'integration_factor': round(integration_factor, 2)
        }

        # 中型模块估算
        medium_backend_base = 8.0  # 包含业务逻辑
        medium_frontend_base = 6.0  # 多个页面和组件
        new_module_efforts['medium_module']['backend_effort'] = round(
            medium_backend_base * project_complexity_factor * understanding_factor * integration_factor, 1
        )
        new_module_efforts['medium_module']['frontend_effort'] = round(
            medium_frontend_base * project_complexity_factor * understanding_factor * integration_factor, 1
        )
        new_module_efforts['medium_module']['total_effort'] = round(
            new_module_efforts['medium_module']['backend_effort'] + new_module_efforts['medium_module']['frontend_effort'], 1
        )
        new_module_efforts['medium_module']['factors'] = {
            'project_complexity_factor': round(project_complexity_factor, 2),
            'understanding_factor': round(understanding_factor, 2),
            'integration_factor': round(integration_factor, 2)
        }

        # 大型模块估算
        large_backend_base = 15.0  # 复杂业务逻辑
        large_frontend_base = 12.0  # 复杂UI和交互
        new_module_efforts['large_module']['backend_effort'] = round(
            large_backend_base * project_complexity_factor * understanding_factor * integration_factor, 1
        )
        new_module_efforts['large_module']['frontend_effort'] = round(
            large_frontend_base * project_complexity_factor * understanding_factor * integration_factor, 1
        )
        new_module_efforts['large_module']['total_effort'] = round(
            new_module_efforts['large_module']['backend_effort'] + new_module_efforts['large_module']['frontend_effort'], 1
        )
        new_module_efforts['large_module']['factors'] = {
            'project_complexity_factor': round(project_complexity_factor, 2),
            'understanding_factor': round(understanding_factor, 2),
            'integration_factor': round(integration_factor, 2)
        }

        return new_module_efforts

    def _calculate_project_complexity_factor(self, project_stats: Dict[str, Any]) -> float:
        """计算项目复杂度因子"""
        # 基于代码行数、文件数量、技术栈多样性计算
        total_lines = project_stats['total_java_lines'] + project_stats['total_sql_lines']
        total_files = (project_stats['total_java_files'] + project_stats['total_ts_files'] +
                      project_stats['total_vue_files'] + project_stats['total_js_files'])

        # 基础复杂度因子
        complexity_factor = 1.0

        # 代码量影响
        if total_lines > 50000:
            complexity_factor += 0.4
        elif total_lines > 20000:
            complexity_factor += 0.2
        elif total_lines > 10000:
            complexity_factor += 0.1

        # 文件数量影响
        if total_files > 200:
            complexity_factor += 0.3
        elif total_files > 100:
            complexity_factor += 0.15
        elif total_files > 50:
            complexity_factor += 0.05

        # 技术栈多样性影响
        tech_diversity = project_stats['tech_stack_diversity']
        if tech_diversity >= 4:
            complexity_factor += 0.3
        elif tech_diversity >= 3:
            complexity_factor += 0.2
        elif tech_diversity >= 2:
            complexity_factor += 0.1

        return min(complexity_factor, 2.0)  # 最大不超过2.0

    def _calculate_project_understanding_factor(self, project_stats: Dict[str, Any]) -> float:
        """计算项目理解成本因子"""
        understanding_factor = 1.0

        # 模块数量影响
        module_count = project_stats['module_count']
        if module_count > 10:
            understanding_factor += 0.4
        elif module_count > 5:
            understanding_factor += 0.2
        elif module_count > 2:
            understanding_factor += 0.1

        # 技术栈多样性影响
        tech_diversity = project_stats['tech_stack_diversity']
        if tech_diversity >= 4:
            understanding_factor += 0.3
        elif tech_diversity >= 3:
            understanding_factor += 0.2
        elif tech_diversity >= 2:
            understanding_factor += 0.1

        # 数据库复杂度影响
        if project_stats['total_sql_tables'] > 50:
            understanding_factor += 0.3
        elif project_stats['total_sql_tables'] > 20:
            understanding_factor += 0.2
        elif project_stats['total_sql_tables'] > 10:
            understanding_factor += 0.1

        return min(understanding_factor, 2.0)  # 最大不超过2.0

    def _calculate_integration_factor(self, project_stats: Dict[str, Any]) -> float:
        """计算集成复杂度因子"""
        integration_factor = 1.0

        # 前后端分离程度
        has_backend = project_stats['total_java_files'] > 0
        has_frontend = (project_stats['total_ts_files'] > 0 or
                       project_stats['total_vue_files'] > 0 or
                       project_stats['total_js_files'] > 0)

        if has_backend and has_frontend:
            integration_factor += 0.2  # 前后端分离需要额外集成工作

        # 数据库集成
        if project_stats['total_sql_tables'] > 0:
            integration_factor += 0.1

        # 模块数量影响
        if project_stats['module_count'] > 5:
            integration_factor += 0.2
        elif project_stats['module_count'] > 2:
            integration_factor += 0.1

        return min(integration_factor, 1.5)  # 最大不超过1.5

    def _calculate_understanding_cost_for_new_modules(self, project_stats: Dict[str, Any]) -> float:
        """计算新模块开发的理解成本"""
        base_cost = 2.0  # 基础理解成本

        # 项目规模影响
        total_lines = project_stats['total_java_lines'] + project_stats['total_sql_lines']
        if total_lines > 50000:
            base_cost += 3.0
        elif total_lines > 20000:
            base_cost += 2.0
        elif total_lines > 10000:
            base_cost += 1.0

        # 技术栈多样性影响
        tech_diversity = project_stats['tech_stack_diversity']
        if tech_diversity >= 4:
            base_cost += 2.0
        elif tech_diversity >= 3:
            base_cost += 1.5
        elif tech_diversity >= 2:
            base_cost += 1.0

        # 模块数量影响
        if project_stats['module_count'] > 5:
            base_cost += 1.5
        elif project_stats['module_count'] > 2:
            base_cost += 1.0

        return round(base_cost, 1)

    def _identify_risk_factors_for_new_modules(self, project_stats: Dict[str, Any]) -> List[str]:
        """识别新模块开发的风险因素"""
        risk_factors = []

        # 技术栈风险
        tech_diversity = project_stats['tech_stack_diversity']
        if tech_diversity >= 4:
            risk_factors.append('技术栈复杂，需要多技术栈开发人员')
        elif tech_diversity >= 3:
            risk_factors.append('技术栈较多，需要跨技术栈集成')

        # 项目规模风险
        total_lines = project_stats['total_java_lines'] + project_stats['total_sql_lines']
        if total_lines > 50000:
            risk_factors.append('项目规模庞大，理解成本高')
        elif total_lines > 20000:
            risk_factors.append('项目规模较大，需要充分了解现有架构')

        # 模块复杂度风险
        if project_stats['module_count'] > 5:
            risk_factors.append('模块数量多，集成复杂度高')

        # 数据库复杂度风险
        if project_stats['total_sql_tables'] > 50:
            risk_factors.append('数据库表结构复杂，需要深入了解数据模型')
        elif project_stats['total_sql_tables'] > 20:
            risk_factors.append('数据库表较多，需要理解数据关系')

        # 代码质量风险
        if project_stats['total_complexity'] > 1000:
            risk_factors.append('代码复杂度高，可能存在技术债务')

        return risk_factors

    def _generate_development_recommendations_for_new_modules(self, project_stats: Dict[str, Any]) -> List[str]:
        """生成新模块开发的建议"""
        recommendations = []

        # 团队配置建议
        tech_diversity = project_stats['tech_stack_diversity']
        if tech_diversity >= 4:
            recommendations.append('建议配置全栈开发人员或前后端分离的团队')
        elif tech_diversity >= 3:
            recommendations.append('建议配置具备多技术栈经验的开发人员')

        # 开发流程建议
        if project_stats['module_count'] > 5:
            recommendations.append('建议采用模块化开发，明确模块间接口')
            recommendations.append('建议建立完善的集成测试流程')

        # 技术建议
        if project_stats['total_sql_tables'] > 20:
            recommendations.append('建议深入了解现有数据库设计和业务逻辑')
            recommendations.append('建议进行数据库性能优化和索引设计')

        # 质量保证建议
        if project_stats['total_complexity'] > 500:
            recommendations.append('建议进行充分的代码审查和测试')
            recommendations.append('建议建立代码规范和最佳实践')

        # 通用建议
        recommendations.append('建议先进行现有代码的深入学习和理解')
        recommendations.append('建议与现有开发团队进行充分的技术交流')
        recommendations.append('建议制定详细的开发计划和里程碑')

        return recommendations

    def scan_project(self):
        """扫描整个项目"""
        print("开始扫描项目...")

        # 分析项目结构
        for module_path in self.project_path.iterdir():
            if module_path.is_dir():
                module_name = module_path.name
                print(f"分析模块: {module_name}")
                self.analyze_module(module_path, module_name)

        # 生成建议
        self.generate_recommendations()

    def analyze_module(self, module_path: Path, module_name: str):
        """分析单个模块"""
        module_analysis = {
            'path': str(module_path),
            'type': self.detect_module_type(module_path),
            'maven_info': {},
            'package_info': {},
            'vue_structure': {},
            'file_stats': {},
            'complexity_metrics': {}
        }

        # Maven项目分析
        if (module_path / 'pom.xml').exists():
            module_analysis['maven_info'] = self.analyze_maven_project(module_path)

        # Node.js项目分析
        if (module_path / 'package.json').exists():
            module_analysis['package_info'] = self.analyze_package_json(module_path)

        # Vue项目结构分析
        if self.is_vue_project(module_path):
            module_analysis['vue_structure'] = self.analyze_vue_project_structure(module_path)

        # 文件统计
        file_stats = self.count_files_by_type(module_path)
        module_analysis['file_stats'] = file_stats

        # 复杂度分析
        complexity_metrics = self.analyze_module_complexity(module_path)
        module_analysis['complexity_metrics'] = complexity_metrics

        self.results['module_analysis'][module_name] = module_analysis

    def count_files_by_type(self, module_path: Path) -> Dict[str, int]:
        """统计模块中的文件类型"""
        file_counts = defaultdict(int)

        for root, dirs, files in os.walk(module_path):
            # 跳过忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]

            for file in files:
                ext = Path(file).suffix.lower()
                if ext:
                    file_counts[ext] += 1
                else:
                    file_counts['no_extension'] += 1

        return dict(file_counts)

    def analyze_module_complexity(self, module_path: Path) -> Dict[str, Any]:
        """分析模块复杂度"""
        complexity_metrics = {
            'java_files': [],
            'typescript_files': [],
            'javascript_files': [],
            'vue_files': [],
            'sql_files': [],
            'total_complexity': 0
        }

        for root, dirs, files in os.walk(module_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]

            for file in files:
                file_path = Path(root) / file

                if file.endswith('.java'):
                    analysis = self.analyze_java_complexity_detailed(file_path)
                    if analysis:
                        complexity_metrics['java_files'].append({
                            'file': str(file_path.relative_to(module_path)),
                            'analysis': analysis
                        })
                        complexity_metrics['total_complexity'] += analysis.get('cyclomatic_complexity', 0)

                elif file.endswith('.ts') or file.endswith('.tsx'):
                    analysis = self.analyze_typescript_complexity_detailed(file_path)
                    if analysis:
                        complexity_metrics['typescript_files'].append({
                            'file': str(file_path.relative_to(module_path)),
                            'analysis': analysis
                        })
                        complexity_metrics['total_complexity'] += analysis.get('cyclomatic_complexity', 0)

                elif file.endswith('.js') or file.endswith('.jsx'):
                    analysis = self.analyze_javascript_complexity_detailed(file_path)
                    if analysis:
                        complexity_metrics['javascript_files'].append({
                            'file': str(file_path.relative_to(module_path)),
                            'analysis': analysis
                        })
                        complexity_metrics['total_complexity'] += analysis.get('cyclomatic_complexity', 0)

                elif file.endswith('.vue'):
                    analysis = self.analyze_vue_complexity_detailed(file_path)
                    if analysis:
                        complexity_metrics['vue_files'].append({
                            'file': str(file_path.relative_to(module_path)),
                            'analysis': analysis
                        })

                elif file.endswith('.sql'):
                    analysis = self.analyze_sql_complexity_detailed(file_path)
                    if analysis:
                        complexity_metrics['sql_files'].append({
                            'file': str(file_path.relative_to(module_path)),
                            'analysis': analysis
                        })
                        complexity_metrics['total_complexity'] += analysis.get('complexity_score', 0)

        return complexity_metrics

    def generate_recommendations(self):
        """生成开发建议"""
        recommendations = {
            'learning_priorities': [],
            'development_risks': [],
            'architecture_insights': [],
            'team_requirements': []
        }

        # 基于分析结果生成建议
        total_java_files = sum(
            len(module.get('complexity_metrics', {}).get('java_files', []))
            for module in self.results['module_analysis'].values()
        )

        total_ts_files = sum(
            len(module.get('complexity_metrics', {}).get('typescript_files', []))
            for module in self.results['module_analysis'].values()
        )

        total_vue_files = sum(
            len(module.get('complexity_metrics', {}).get('vue_files', []))
            for module in self.results['module_analysis'].values()
        )

        total_js_files = sum(
            len(module.get('complexity_metrics', {}).get('javascript_files', []))
            for module in self.results['module_analysis'].values()
        )

        total_sql_files = sum(
            len(module.get('complexity_metrics', {}).get('sql_files', []))
            for module in self.results['module_analysis'].values()
        )

        # 学习优先级建议
        if total_java_files > 100:
            recommendations['learning_priorities'].append('优先学习Java框架和微服务架构')
        elif total_java_files > 50:
            recommendations['learning_priorities'].append('学习Java开发基础')

        if total_ts_files > 50:
            recommendations['learning_priorities'].append('深入学习TypeScript和现代前端开发模式')
        elif total_ts_files > 20:
            recommendations['learning_priorities'].append('学习TypeScript基础语法')

        if total_vue_files > 30:
            recommendations['learning_priorities'].append('掌握Vue框架和组件设计模式')
        elif total_vue_files > 10:
            recommendations['learning_priorities'].append('学习Vue基础语法')

        if total_js_files > 50:
            recommendations['learning_priorities'].append('深入学习JavaScript和前端开发')

        if total_sql_files > 20:
            recommendations['learning_priorities'].append('深入学习SQL和数据库设计')
        elif total_sql_files > 5:
            recommendations['learning_priorities'].append('学习SQL基础语法和数据库操作')

        # 开发风险
        if total_java_files > 200:
            recommendations['development_risks'].append('后端代码量大，需要充分理解业务逻辑和架构设计')
        elif total_java_files > 100:
            recommendations['development_risks'].append('后端复杂度较高，需要熟悉框架特性')

        if total_ts_files > 100:
            recommendations['development_risks'].append('前端复杂度高，需要熟悉状态管理和组件通信')
        elif total_ts_files > 50:
            recommendations['development_risks'].append('前端代码较多，需要良好的代码组织能力')

        if total_vue_files > 50:
            recommendations['development_risks'].append('Vue组件众多，需要熟悉组件架构和通信机制')

        if total_sql_files > 50:
            recommendations['development_risks'].append('SQL文件众多，需要数据库设计和优化经验')
        elif total_sql_files > 20:
            recommendations['development_risks'].append('SQL复杂度较高，需要良好的数据库设计能力')

        # 架构洞察
        module_count = len(self.results['module_analysis'])
        if module_count > 3:
            recommendations['architecture_insights'].append('这是一个多模块的复杂项目，需要理解模块间依赖关系')
        elif module_count > 1:
            recommendations['architecture_insights'].append('项目包含多个模块，需要统一的设计规范')

        if total_java_files > 0 and (total_ts_files > 0 or total_vue_files > 0):
            recommendations['architecture_insights'].append('这是一个典型的前后端分离架构项目')

        # 团队要求
        if total_java_files > 50:
            recommendations['team_requirements'].append('需要Java后端开发人员')
        if total_ts_files > 20 or total_vue_files > 10:
            recommendations['team_requirements'].append('需要前端开发人员')
        if total_js_files > 30:
            recommendations['team_requirements'].append('需要JavaScript开发人员')
        if total_sql_files > 10:
            recommendations['team_requirements'].append('需要数据库开发人员')

        self.results['recommendations'] = recommendations

    def generate_report(self, output_file: str = None):
        """生成分析报告"""
        if not output_file:
            output_file = f"project_complexity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # 计算工作量估算
        effort_estimate = self.calculate_work_effort_estimate(self.results)
        self.results['effort_estimate'] = effort_estimate

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"报告已生成: {output_file}")
        self.print_summary()

    def print_summary(self):
        """打印分析摘要"""
        print("\n" + "="*80)
        print("项目复杂度分析摘要")
        print("="*80)

        # 模块概览
        print("\n项目模块概览:")
        print("-" * 50)
        for module_name, analysis in self.results['module_analysis'].items():
            file_stats = analysis.get('file_stats', {})
            total_files = sum(file_stats.values())
            print(f"{module_name:20} | 文件数: {total_files:4d} | 类型: {analysis.get('type', '未知')}")

        # 技术栈分析
        print("\n技术栈分析:")
        print("-" * 50)
        java_files = sum(len(m.get('complexity_metrics', {}).get('java_files', [])) for m in self.results['module_analysis'].values())
        ts_files = sum(len(m.get('complexity_metrics', {}).get('typescript_files', [])) for m in self.results['module_analysis'].values())
        js_files = sum(len(m.get('complexity_metrics', {}).get('javascript_files', [])) for m in self.results['module_analysis'].values())
        vue_files = sum(len(m.get('complexity_metrics', {}).get('vue_files', [])) for m in self.results['module_analysis'].values())
        sql_files = sum(len(m.get('complexity_metrics', {}).get('sql_files', [])) for m in self.results['module_analysis'].values())

        print(f"Java文件: {java_files}")
        print(f"TypeScript文件: {ts_files}")
        print(f"JavaScript文件: {js_files}")
        print(f"Vue文件: {vue_files}")
        print(f"SQL文件: {sql_files}")

        # 二次开发新模块工作量估算
        effort = self.results.get('effort_estimate', {})
        print(f"\n二次开发新模块工作量估算:")
        print("-" * 50)

        # 项目上下文信息
        project_context = effort.get('project_context', {})
        if project_context:
            print(f"\n项目上下文信息:")
            print("-" * 50)
            print(f"Java文件数: {project_context.get('total_java_files', 0)}")
            print(f"TypeScript文件数: {project_context.get('total_ts_files', 0)}")
            print(f"Vue文件数: {project_context.get('total_vue_files', 0)}")
            print(f"JavaScript文件数: {project_context.get('total_js_files', 0)}")
            print(f"SQL文件数: {project_context.get('total_sql_lines', 0) > 0 and '有' or '无'}")
            print(f"模块数量: {project_context.get('module_count', 0)}")
            print(f"技术栈多样性: {project_context.get('tech_stack_diversity', 0)}")

        # 新模块工作量估算
        new_module_efforts = effort.get('new_module_efforts', {})
        if new_module_efforts:
            print(f"\n新模块工作量估算:")
            print("-" * 80)
            print(f"{'模块类型':<20} {'描述':<40} {'后端(人天)':<12} {'前端(人天)':<12} {'总计(人天)':<12}")
            print("-" * 80)

            for module_type, module_effort in new_module_efforts.items():
                print(f"{module_type:<20} {module_effort['description']:<40} "
                      f"{module_effort['backend_effort']:<12.1f} "
                      f"{module_effort['frontend_effort']:<12.1f} "
                      f"{module_effort['total_effort']:<12.1f}")

            # 显示影响因子
            print(f"\n影响因子详情:")
            print("-" * 50)
            for module_type, module_effort in new_module_efforts.items():
                factors = module_effort.get('factors', {})
                print(f"{module_type}:")
                print(f"  项目复杂度因子: {factors.get('project_complexity_factor', 0):.2f}")
                print(f"  理解成本因子: {factors.get('understanding_factor', 0):.2f}")
                print(f"  集成复杂度因子: {factors.get('integration_factor', 0):.2f}")

        # 理解成本
        understanding_cost = effort.get('understanding_cost', 0)
        if understanding_cost > 0:
            print(f"\n代码理解成本: {understanding_cost:.1f} 人天")

        # 风险因素
        risk_factors = effort.get('risk_factors', [])
        if risk_factors:
            print(f"\n开发风险因素:")
            print("-" * 50)
            for risk in risk_factors:
                print(f"• {risk}")

        # 开发建议
        development_recommendations = effort.get('development_recommendations', [])
        if development_recommendations:
            print(f"\n开发建议:")
            print("-" * 50)
            for recommendation in development_recommendations:
                print(f"• {recommendation}")

        # 原有建议
        recommendations = self.results.get('recommendations', {})
        if recommendations.get('learning_priorities'):
            print(f"\n学习优先级:")
            print("-" * 50)
            for priority in recommendations['learning_priorities']:
                print(f"• {priority}")

        if recommendations.get('development_risks'):
            print(f"\n开发风险:")
            print("-" * 50)
            for risk in recommendations['development_risks']:
                print(f"• {risk}")

def main():
    parser = argparse.ArgumentParser(description='通用项目代码复杂度分析工具')
    parser.add_argument('project_path', help='项目根路径')
    parser.add_argument('-o', '--output', help='输出文件路径')

    args = parser.parse_args()

    analyzer = GenericComplexityAnalyzer(args.project_path)
    analyzer.scan_project()
    analyzer.generate_report(args.output)

if __name__ == '__main__':
    main()
