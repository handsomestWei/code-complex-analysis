#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块分析核心功能模块
包含主要的表格生成逻辑
"""

class ModuleCoreGenerator:
    def __init__(self, data, language_manager=None, config=None):
        self.data = data
        self.language_manager = language_manager
        self.config = config

    def generate_module_table(self) -> str:
        """生成模块分析表格（包含展开/折叠的详细分析）"""
        module_analysis = self.data.get('module_analysis', {})

        if not module_analysis:
            return "<p>暂无模块分析数据</p>"

        all_file_types = set()
        file_type_counts = {}  # 统计每种文件类型的总数
        module_data = []

        # 动态获取有意义的文件类型
        meaningful_extensions = self._get_meaningful_file_extensions()

        for module_name, analysis in module_analysis.items():
            # 从complexity字段获取数据
            complexity_data = analysis.get('complexity', {})

            # 收集模块数据
            module_info = {
                'name': module_name,
                'type': analysis.get('type', '未知'),
                'total_files': complexity_data.get('total_files', 0) if complexity_data and 'error' not in complexity_data else 0,
                'complexity': complexity_data.get('total_complexity', 0) if complexity_data and 'error' not in complexity_data else 0,
                'analysis': analysis  # 保存完整分析数据用于详细分析
            }

            # 动态检测文件类型（只统计有意义的类型）
            if complexity_data and 'error' not in complexity_data:
                for file_path, file_data in complexity_data.get('file_complexity', {}).items():
                    if isinstance(file_data, dict) and 'file_extension' in file_data:
                        file_ext = file_data['file_extension'].lower()
                        if file_ext.startswith('.'):
                            file_type = file_ext[1:]  # 去掉点号
                        else:
                            file_type = file_ext

                        # 只统计有意义的文件类型
                        if file_type in meaningful_extensions:
                            if file_type not in all_file_types:
                                all_file_types.add(file_type)
                            if file_type not in module_info:
                                module_info[file_type] = 0
                            module_info[file_type] += 1

                        # 统计全局文件类型数量
                        if file_type not in file_type_counts:
                            file_type_counts[file_type] = 0
                        file_type_counts[file_type] += 1

            module_data.append(module_info)

        # 如果没有找到任何文件类型，使用动态获取的支持语言
        if not all_file_types:
            all_file_types = set(self._get_supported_languages())

        # 计算总文件数
        total_files = sum(file_type_counts.values()) if file_type_counts else 0

        # 过滤文件类型：只显示占比超过2%的文件类型，或者数量超过10个的文件类型
        filtered_file_types = set()
        for file_type in all_file_types:
            count = file_type_counts.get(file_type, 0)
            percentage = (count / total_files * 100) if total_files > 0 else 0
            if percentage >= 2.0 or count >= 10:  # 占比2%以上或数量10个以上
                filtered_file_types.add(file_type)

        # 如果没有符合条件的文件类型，使用所有类型
        if not filtered_file_types:
            filtered_file_types = all_file_types

        # 限制文件类型列数，避免表格过宽
        max_file_type_columns = 8  # 最多显示8个文件类型列
        if len(filtered_file_types) > max_file_type_columns:
            # 按优先级和数量排序，只保留最重要的类型
            priority_types = list(self._get_language_priorities().keys())
            sorted_by_importance = []

            # 先添加优先类型
            for ptype in priority_types:
                if ptype in filtered_file_types:
                    sorted_by_importance.append((ptype, file_type_counts.get(ptype, 0)))
                    filtered_file_types.remove(ptype)

            # 再按数量排序其他类型
            other_sorted = sorted(filtered_file_types, key=lambda x: file_type_counts.get(x, 0), reverse=True)
            sorted_by_importance.extend([(ft, file_type_counts.get(ft, 0)) for ft in other_sorted])

            # 只保留前N个最重要的类型
            filtered_file_types = {ft for ft, _ in sorted_by_importance[:max_file_type_columns]}

        # 按优先级排序文件类型，使用动态获取的优先级
        priority_types = list(self._get_language_priorities().keys())
        sorted_file_types = []

        # 先添加优先类型（如果存在且符合过滤条件）
        for ptype in priority_types:
            if ptype in filtered_file_types:
                sorted_file_types.append(ptype)
                filtered_file_types.remove(ptype)

        # 再添加其他类型（按字母顺序）
        sorted_file_types.extend(sorted(filtered_file_types))

        # 动态获取文件类型显示名称映射
        type_display_names = self._get_language_display_names()

        # 生成表头
        table_html = """
        <table class="module-table">
            <thead>
                <tr>
                    <th>模块名称</th>
                    <th>类型</th>
                    <th>文件数</th>
        """

        # 动态添加文件类型列
        for file_type in sorted_file_types:
            display_name = type_display_names.get(file_type, f'{file_type.title()}文件')
            table_html += f"                    <th>{display_name}</th>\n"

        # 添加"其他文件类型"列
        other_file_types = all_file_types - set(sorted_file_types)
        if other_file_types:
            table_html += "                    <th>其他文件</th>\n"

        table_html += """                    <th>复杂度</th>
                </tr>
            </thead>
            <tbody>
        """

        # 计算实际列数：基础列(3) + 文件类型列数 + 其他文件列(可选) + 复杂度列(1)
        actual_header_columns = 3 + len(sorted_file_types) + (1 if other_file_types else 0) + 1

        # 生成数据行和详细分析
        for module_info in module_data:
            complexity = module_info['complexity']
            complexity_class = 'complexity-low'
            complexity_text = '低'
            if complexity > 1000:
                complexity_class = 'complexity-high'
                complexity_text = '高'
            elif complexity > 500:
                complexity_class = 'complexity-medium'
                complexity_text = '中'

            # 生成主行
            # 清理模块名称，确保ID唯一且安全
            safe_module_name = module_info['name'].replace(' ', '_').replace('-', '_').replace('.', '_').replace('/', '_').replace('\\', '_')

            table_html += f"""
                <tr class="module-row" data-module="{safe_module_name}">
                    <td>
                        <div class="module-name-cell">
                            <span class="toggle-icon">▼</span>
                            {module_info['name']}
                        </div>
                    </td>
                    <td>{module_info['type']}</td>
                    <td>{module_info['total_files']}</td>
            """

            # 动态添加文件类型数据
            for file_type in sorted_file_types:
                count = module_info.get(file_type, 0)
                table_html += f"                    <td>{count}</td>\n"

            # 添加"其他文件类型"统计
            if other_file_types:
                other_count = sum(module_info.get(ft, 0) for ft in other_file_types)
                table_html += f"                    <td>{other_count}</td>\n"

            table_html += f"""                    <td class="{complexity_class}">{complexity}</td>
                </tr>
            """

            # 计算列数：使用表头计算出的准确列数
            # 确保列数计算准确
            actual_columns = actual_header_columns

            # 直接在这里生成详细分析内容，而不是使用占位符
            detail_content = self._generate_detail_content(module_info, safe_module_name)

            table_html += f"""
                <tr class="module-detail-row" id="detail-{safe_module_name}" style="display: none;">
                    <td colspan="{actual_columns}">
                        {detail_content}
                    </td>
                </tr>
            """

        table_html += """
            </tbody>
        </table>
        """

        return table_html, module_data, sorted_file_types, other_file_types

    def _generate_detail_content(self, module_info: dict, safe_module_name: str) -> str:
        """生成模块的详细分析内容"""
        try:
            # 导入必要的模块
            from .gen_html_module_complexity import ModuleComplexityGenerator
            from .gen_html_module_structure import ModuleStructureGenerator

            # 初始化生成器
            complexity_generator = ModuleComplexityGenerator(self.data, self.language_manager, self.config)
            structure_generator = ModuleStructureGenerator(self.data, self.language_manager, self.config)

            # 获取分析数据
            analysis = module_info['analysis']
            complexity_metrics = analysis.get('complexity', {})

            # 生成各个部分的HTML
            lines_stats_html = complexity_generator.generate_lines_statistics(complexity_metrics)
            depth_analysis_html = complexity_generator.generate_depth_analysis(complexity_metrics)
            structure_complexity_html = complexity_generator.generate_structure_complexity(complexity_metrics)
            project_structure_html = structure_generator.generate_project_structure_details(analysis)

            # 组合所有内容，确保HTML结构正确，直接在td内放置内容
            return f"""<div class="module-detail-content">
    <div class="detail-grid">
        {lines_stats_html}
        {depth_analysis_html}
        {structure_complexity_html}
        {project_structure_html}
    </div>
</div>"""
        except Exception as e:
            # 如果生成失败，返回错误信息
            return f"""<div class="detail-card">
    <h4>错误</h4>
    <p>生成详细分析内容时出错: {str(e)}</p>
</div>"""

    def _get_language_priorities(self) -> dict:
        """获取语言优先级"""
        return {
            'java': 1, 'typescript': 2, 'javascript': 3, 'vue': 4,
            'python': 5, 'sql': 6, 'css': 7, 'html': 8
        }

    def _get_language_display_names(self) -> dict:
        """获取语言显示名称"""
        return {
            'java': 'Java文件', 'typescript': 'TypeScript文件', 'javascript': 'JavaScript文件',
            'vue': 'Vue文件', 'python': 'Python文件', 'sql': 'SQL文件', 'css': 'CSS文件',
            'html': 'HTML文件', 'scss': 'SCSS文件', 'sass': 'Sass文件', 'ts': 'TypeScript文件',
            'tsx': 'TypeScript React文件', 'js': 'JavaScript文件', 'jsx': 'JavaScript React文件',
            'py': 'Python文件', 'htm': 'HTML文件', 'xml': 'XML文件', 'json': 'JSON文件',
            'yaml': 'YAML文件', 'yml': 'YAML文件', 'md': 'Markdown文件', 'sh': 'Shell脚本',
            'bash': 'Bash脚本', 'properties': 'Properties文件'
        }

    def _get_meaningful_file_extensions(self) -> set:
        """获取有意义的文件类型扩展名"""
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

    def _get_supported_languages(self) -> list:
        """获取支持的语言列表"""
        try:
            if self.language_manager:
                return self.language_manager.get_supported_languages()
        except Exception:
            pass
        return ['java', 'typescript', 'javascript', 'vue', 'python', 'sql', 'css', 'html']
