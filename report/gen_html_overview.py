#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目概览模块
生成项目概览部分的HTML内容
"""

class OverviewGenerator:
    def __init__(self, data, language_manager=None, config=None):
        self.data = data
        self.language_manager = language_manager
        self.config = config

    def generate_overview_metrics(self) -> str:
        """生成概览指标"""
        meaningful_file_types = {}
        total_files = 0
        total_lines = 0
        total_complexity = 0
        total_sql_tables = 0
        total_sql_views = 0

        supported_extensions = self._get_meaningful_file_extensions()

        for module in self.data.get('module_analysis', {}).values():
            complexity_data = module.get('complexity', {})
            if complexity_data and 'error' not in complexity_data:
                total_files += complexity_data.get('total_files', 0)
                total_lines += complexity_data.get('total_lines', 0)
                total_complexity += complexity_data.get('total_complexity', 0)

            complexity_metrics = module.get('complexity', {})
            if complexity_metrics and 'error' not in complexity_metrics:
                for file_type_key, file_list in complexity_metrics.get('file_complexity', {}).items():
                    if isinstance(file_list, dict) and 'file_extension' in file_list:
                        file_ext = file_list['file_extension'].lower()
                        if file_ext.startswith('.'):
                            file_type = file_ext[1:]
                        else:
                            file_type = file_ext

                        if file_type in supported_extensions:
                            if file_type not in meaningful_file_types:
                                meaningful_file_types[file_type] = 0
                            meaningful_file_types[file_type] += 1

            sql_files = complexity_metrics.get('file_complexity', {})
            for file_path, file_data in sql_files.items():
                if isinstance(file_data, dict) and self._is_sql_file(file_data.get('file_extension', '')):
                    total_sql_tables += file_data.get('tables', 0)
                    total_sql_views += file_data.get('views', 0)

        type_display_info = {}
        priorities = self._get_language_priorities()
        display_names = self._get_language_display_names()

        for lang, priority in priorities.items():
            type_display_info[lang] = {
                'name': display_names.get(lang, f'{lang.title()}文件'),
                'priority': priority
            }

        filtered_file_types = []
        for file_type, count in meaningful_file_types.items():
            percentage = (count / total_files * 100) if total_files > 0 else 0
            if percentage >= 3.0 or count >= 5:
                filtered_file_types.append((file_type, count))

        sorted_file_types = sorted(
            filtered_file_types,
            key=lambda x: type_display_info.get(x[0], {'priority': 999})['priority']
        )

        metrics_html = f"""
            <div class="metric-card">
                <h3>{total_files:,}</h3>
                <p>总文件数</p>
            </div>
            <div class="metric-card">
                <h3>{total_lines:,}</h3>
                <p>总代码行数</p>
            </div>
            <div class="metric-card">
                <h3>{total_complexity:,}</h3>
                <p>总复杂度</p>
            </div>
        """

        for file_type, count in sorted_file_types:
            display_info = type_display_info.get(file_type, {'name': f'{file_type.title()}文件'})
            display_name = display_info['name']
            metrics_html += f"""
            <div class="metric-card">
                <h3>{count}</h3>
                <p>{display_name}</p>
            </div>
            """

        db_extensions = self._get_database_extensions()
        has_db_files = any(ext[1:] in meaningful_file_types for ext in db_extensions)

        if has_db_files and 'sql' in meaningful_file_types:
            metrics_html += f"""
            <div class="metric-card">
                <h3>{total_sql_tables}</h3>
                <p>数据库表</p>
            </div>
            <div class="metric-card">
                <h3>{total_sql_views}</h3>
                <p>数据库视图</p>
            </div>
            """

        return metrics_html

    def _get_language_priorities(self) -> dict:
        return {
            'java': 1, 'typescript': 2, 'javascript': 3, 'vue': 4,
            'python': 5, 'sql': 6, 'css': 7, 'html': 8
        }

    def _get_language_display_names(self) -> dict:
        return {
            'java': 'Java文件', 'typescript': 'TypeScript文件', 'javascript': 'JavaScript文件',
            'vue': 'Vue文件', 'python': 'Python文件', 'sql': 'SQL文件', 'css': 'CSS文件',
            'html': 'HTML文件', 'scss': 'SCSS文件', 'sass': 'Sass文件', 'ts': 'TypeScript文件',
            'tsx': 'TypeScript React文件', 'js': 'JavaScript文件', 'jsx': 'JavaScript React文件',
            'py': 'Python文件', 'htm': 'HTML文件', 'xml': 'XML文件', 'json': 'JSON文件',
            'yaml': 'YAML文件', 'yml': 'YAML文件', 'md': 'Markdown文件', 'sh': 'Shell脚本',
            'bash': 'Bash脚本', 'properties': 'Properties文件'
        }

    def _get_tech_stack_categories(self):
        if self.config:
            try:
                return self.config.tech_stack_categories
            except Exception:
                pass
        return {
            'backend': ['java', 'xml', 'properties', 'sql', 'sh', 'python'],
            'frontend': ['typescript', 'javascript', 'vue', 'scss', 'css', 'html'],
            'mobile': ['vue', 'javascript', 'json'],
            'config': ['yaml', 'json', 'xml', 'properties'],
            'docs': ['markdown', 'html']
        }

    def _is_sql_file(self, file_extension: str) -> bool:
        try:
            if self.language_manager:
                if 'sql' in self.language_manager.get_available_analyzers():
                    analyzer_info = self.language_manager.get_available_analyzers()['sql']
                    if hasattr(analyzer_info, 'file_extensions'):
                        if file_extension.lower() in analyzer_info.file_extensions:
                            return True
        except Exception:
            pass
        sql_extensions = {'.sql', '.db', '.sqlite', '.mysql', '.postgresql'}
        return file_extension.lower() in sql_extensions

    def _get_database_extensions(self) -> list:
        try:
            if self.language_manager:
                if 'sql' in self.language_manager.get_available_analyzers():
                    analyzer_info = self.language_manager.get_available_analyzers()['sql']
                    if hasattr(analyzer_info, 'file_extensions'):
                        return list(analyzer_info.file_extensions)
        except Exception:
            pass
        return ['.sql', '.db', '.sqlite', '.mysql', '.postgresql']

    def _get_meaningful_file_extensions(self) -> set:
        try:
            if self.language_manager:
                extensions = set()
                analyzers = self.language_manager.get_available_analyzers()
                for analyzer_name, analyzer_info in analyzers.items():
                    if hasattr(analyzer_info, 'file_extensions'):
                        for ext in analyzer_info.file_extensions:
                            extensions.add(ext.lstrip('.'))
                return extensions
        except Exception:
            pass
        return {
            'java', 'ts', 'tsx', 'js', 'jsx', 'vue', 'py', 'sql', 'scss', 'sass', 'css', 'html', 'htm',
            'xml', 'json', 'yaml', 'yml', 'md', 'sh', 'bash', 'properties'
        }
