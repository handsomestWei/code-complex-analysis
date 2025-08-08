#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用项目复杂度分析报告生成器
生成可视化的HTML报告
"""

import json
import os
from pathlib import Path
from datetime import datetime
import argparse

class ReportGenerator:
    def __init__(self, analysis_file: str):
        self.analysis_file = Path(analysis_file)
        with open(self.analysis_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def generate_html_report(self, output_file: str = None):
        """生成HTML报告"""
        if not output_file:
            output_file = f"project_complexity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        html_content = self._generate_html_content()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML报告已生成: {output_file}")

    def _load_template(self) -> str:
        """加载HTML模板"""
        template_path = Path(__file__).parent / "report_template.html"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise FileNotFoundError(f"模板文件不存在: {template_path}")

    def _generate_html_content(self) -> str:
        """生成HTML内容"""
        # 加载模板
        template = self._load_template()

        # 准备模板变量
        template_vars = {
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overview_metrics': self._generate_overview_metrics(),
            'module_table': self._generate_module_table(),
            'effort_analysis': self._generate_effort_analysis(),
            'recommendations': self._generate_recommendations(),
            'chart_scripts': self._generate_chart_scripts()
        }

        # 替换模板变量
        html_content = template
        for key, value in template_vars.items():
            html_content = html_content.replace(f'{{{{{key}}}}}', str(value))

        return html_content

    def _generate_overview_metrics(self) -> str:
        """生成概览指标"""

        # 自动统计所有文件类型
        file_type_counts = {}
        total_files = 0

        # 统计SQL特殊指标
        total_sql_tables = 0
        total_sql_views = 0
        total_sql_lines = 0

        for module in self.data.get('module_analysis', {}).values():
            # 统计总文件数
            file_stats = module.get('file_stats', {})
            total_files += sum(file_stats.values())

            # 统计各种类型文件数
            complexity_metrics = module.get('complexity_metrics', {})
            for file_type_key, file_list in complexity_metrics.items():
                if file_type_key.endswith('_files') and isinstance(file_list, list):
                    file_type = file_type_key.replace('_files', '')
                    file_count = len(file_list)

                    if file_count > 0:
                        file_type_counts[file_type] = file_type_counts.get(file_type, 0) + file_count

            # 特殊处理SQL统计
            sql_files = complexity_metrics.get('sql_files', [])
            for sql_file in sql_files:
                analysis = sql_file.get('analysis', {})
                total_sql_tables += analysis.get('tables', 0)
                total_sql_views += analysis.get('views', 0)
                total_sql_lines += analysis.get('total_lines', 0)

        # 文件类型显示名称和优先级
        type_display_info = {
            'java': {'name': 'Java文件', 'priority': 1},
            'typescript': {'name': 'TypeScript文件', 'priority': 2},
            'javascript': {'name': 'JavaScript文件', 'priority': 3},
            'vue': {'name': 'Vue文件', 'priority': 4},
            'sql': {'name': 'SQL文件', 'priority': 5},
            'html': {'name': 'HTML文件', 'priority': 6},
            'css': {'name': 'CSS文件', 'priority': 7},
            'scss': {'name': 'SCSS文件', 'priority': 8},
            'xml': {'name': 'XML文件', 'priority': 9},
            'json': {'name': 'JSON文件', 'priority': 10},
            'yaml': {'name': 'YAML文件', 'priority': 11},
            'markdown': {'name': 'Markdown文件', 'priority': 12},
            'python': {'name': 'Python文件', 'priority': 13},
            'shell': {'name': 'Shell文件', 'priority': 14}
        }

        # 按优先级排序文件类型
        sorted_file_types = sorted(
            file_type_counts.keys(),
            key=lambda x: type_display_info.get(x, {'priority': 999})['priority']
        )

        # 生成指标卡片HTML
        metrics_html = f"""
            <div class="metric-card">
                <h3>{total_files}</h3>
                <p>总文件数</p>
            </div>
        """

        # 动态生成文件类型指标卡片
        for file_type in sorted_file_types:
            count = file_type_counts[file_type]
            display_info = type_display_info.get(file_type, {'name': f'{file_type.title()}文件'})
            display_name = display_info['name']

            metrics_html += f"""
            <div class="metric-card">
                <h3>{count}</h3>
                <p>{display_name}</p>
            </div>
            """

        # 添加SQL特殊指标（如果有SQL文件）
        if 'sql' in file_type_counts:
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

    def _generate_module_table(self) -> str:
        """生成模块分析表格（包含展开/折叠的详细分析）"""
        module_analysis = self.data.get('module_analysis', {})

        if not module_analysis:
            return "<p>暂无模块分析数据</p>"

        # 自动检测所有可用的文件类型
        all_file_types = set()
        module_data = []

        for module_name, analysis in module_analysis.items():
            file_stats = analysis.get('file_stats', {})
            complexity_metrics = analysis.get('complexity_metrics', {})

            # 收集模块数据
            module_info = {
                'name': module_name,
                'type': analysis.get('type', '未知'),
                'total_files': sum(file_stats.values()),
                'complexity': complexity_metrics.get('total_complexity', 0),
                'analysis': analysis  # 保存完整分析数据用于详细分析
            }

            # 动态检测文件类型
            for file_type_key, file_list in complexity_metrics.items():
                if file_type_key.endswith('_files') and isinstance(file_list, list):
                    # 提取文件类型名称（去除_files后缀）
                    file_type = file_type_key.replace('_files', '')
                    file_count = len(file_list)

                    if file_count > 0:  # 只记录有文件的类型
                        all_file_types.add(file_type)
                        module_info[file_type] = file_count

            module_data.append(module_info)

        # 如果没有找到任何文件类型，使用默认的
        if not all_file_types:
            all_file_types = {'java', 'typescript', 'javascript', 'vue', 'sql'}

        # 按字母顺序排序文件类型，但保持常用类型在前
        priority_types = ['java', 'typescript', 'javascript', 'vue', 'sql']
        sorted_file_types = []

        # 先添加优先类型（如果存在）
        for ptype in priority_types:
            if ptype in all_file_types:
                sorted_file_types.append(ptype)
                all_file_types.remove(ptype)

        # 再添加其他类型（按字母顺序）
        sorted_file_types.extend(sorted(all_file_types))

        # 文件类型显示名称映射
        type_display_names = {
            'java': 'Java文件',
            'typescript': 'TS文件',
            'javascript': 'JS文件',
            'vue': 'Vue文件',
            'sql': 'SQL文件',
            'html': 'HTML文件',
            'css': 'CSS文件',
            'scss': 'SCSS文件',
            'xml': 'XML文件',
            'json': 'JSON文件',
            'yaml': 'YAML文件',
            'markdown': 'MD文件',
            'python': 'Python文件',
            'shell': 'Shell文件'
        }

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

        table_html += """                    <th>复杂度</th>
                </tr>
            </thead>
            <tbody>
        """

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

            table_html += f"""                    <td class="{complexity_class}">{complexity}</td>
                </tr>
            """

            # 生成详细分析行
            analysis = module_info['analysis']
            complexity_metrics = analysis.get('complexity_metrics', {})

            # 生成详细分析内容
            lines_stats_html = self._generate_lines_statistics(complexity_metrics)
            depth_analysis_html = self._generate_depth_analysis(complexity_metrics)
            structure_complexity_html = self._generate_structure_complexity(complexity_metrics)

            table_html += f"""
                <tr class="module-detail-row" id="detail-{safe_module_name}" style="display: none;">
                    <td colspan="{len(sorted_file_types) + 4}">
                        <div class="module-detail-content">
                            <div class="detail-grid">
                                {lines_stats_html}
                                {depth_analysis_html}
                                {structure_complexity_html}
                            </div>
                        </div>
                    </td>
                </tr>
            """

        table_html += """
            </tbody>
        </table>
        """

        return table_html



    def _generate_lines_statistics(self, complexity_metrics: dict) -> str:
        """生成行数统计"""
        # 从各个文件类型中收集行数统计
        total_lines = 0
        total_code_lines = 0
        total_comment_lines = 0
        total_blank_lines = 0

        # 从所有文件类型中汇总行数统计
        for file_type_key, file_list in complexity_metrics.items():
            if file_type_key.endswith('_files') and isinstance(file_list, list):
                for file_info in file_list:
                    if isinstance(file_info, dict) and 'analysis' in file_info:
                        analysis = file_info['analysis']
                        file_total_lines = analysis.get('total_lines', 0)

                        # 如果没有total_lines，基于其他指标估算行数
                        if file_total_lines == 0:
                            # 基于函数、类、接口等数量估算行数
                            if file_type_key == 'typescript_files' or file_type_key == 'javascript_files':
                                functions = analysis.get('functions', 0)
                                classes = analysis.get('classes', 0)
                                interfaces = analysis.get('interfaces', 0)
                                # 估算：每个函数约15行，每个类约25行，每个接口约8行
                                file_total_lines = functions * 15 + classes * 25 + interfaces * 8
                            elif file_type_key == 'vue_files':
                                # Vue文件通常比较复杂，基于复杂度估算
                                complexity = analysis.get('cyclomatic_complexity', 0)
                                functions = analysis.get('functions', 0)
                                # 估算：基于复杂度和函数数量
                                file_total_lines = max(complexity * 3, functions * 20, 50)  # 至少50行
                            elif file_type_key == 'java_files':
                                methods = analysis.get('methods', 0)
                                classes = analysis.get('classes', 0)
                                # 估算：每个方法约12行，每个类额外20行
                                file_total_lines = methods * 12 + classes * 20
                            elif file_type_key == 'sql_files':
                                # SQL文件基于表、视图、存储过程估算
                                tables = analysis.get('tables', 0) if isinstance(analysis.get('tables'), int) else len(analysis.get('tables', []))
                                views = analysis.get('views', 0) if isinstance(analysis.get('views'), int) else len(analysis.get('views', []))
                                procedures = analysis.get('procedures', 0) if isinstance(analysis.get('procedures'), int) else len(analysis.get('procedures', []))
                                file_total_lines = tables * 8 + views * 6 + procedures * 30
                            else:
                                # 其他文件类型的默认估算
                                file_total_lines = 100  # 默认100行

                        total_lines += file_total_lines

                        # 根据文件类型和总行数估算详细分布
                        if file_total_lines > 0:
                            # 对于Java文件，通常有较多注释
                            if file_type_key == 'java_files':
                                estimated_comments = int(file_total_lines * 0.15)  # 15%注释
                                estimated_blank = int(file_total_lines * 0.10)     # 10%空行
                                estimated_code = file_total_lines - estimated_comments - estimated_blank
                            # 对于前端文件，注释相对较少
                            elif file_type_key in ['typescript_files', 'javascript_files', 'vue_files']:
                                estimated_comments = int(file_total_lines * 0.08)  # 8%注释
                                estimated_blank = int(file_total_lines * 0.12)     # 12%空行
                                estimated_code = file_total_lines - estimated_comments - estimated_blank
                            # 对于SQL文件
                            elif file_type_key == 'sql_files':
                                estimated_comments = int(file_total_lines * 0.05)  # 5%注释
                                estimated_blank = int(file_total_lines * 0.15)     # 15%空行
                                estimated_code = file_total_lines - estimated_comments - estimated_blank
                            else:
                                # 其他文件类型的默认估算
                                estimated_comments = int(file_total_lines * 0.10)
                                estimated_blank = int(file_total_lines * 0.12)
                                estimated_code = file_total_lines - estimated_comments - estimated_blank

                            total_code_lines += max(estimated_code, 0)
                            total_comment_lines += estimated_comments
                            total_blank_lines += estimated_blank

        return f"""
        <div class="detail-card">
            <h4>行数统计</h4>
            <ul class="detail-list">
                <li><span class="detail-label">总行数</span><span class="detail-value">{total_lines:,}</span></li>
                <li><span class="detail-label">代码行数</span><span class="detail-value">{total_code_lines:,}</span></li>
                <li><span class="detail-label">注释行数</span><span class="detail-value">{total_comment_lines:,}</span></li>
                <li><span class="detail-label">空行数</span><span class="detail-value">{total_blank_lines:,}</span></li>
            </ul>
        </div>
        """

    def _count_total_files(self, complexity_metrics: dict) -> int:
        """计算总文件数"""
        total_files = 0
        for file_type_key, file_list in complexity_metrics.items():
            if file_type_key.endswith('_files') and isinstance(file_list, list):
                total_files += len(file_list)
        return total_files

    def _generate_depth_analysis(self, complexity_metrics: dict) -> str:
        """生成深度分析"""
        # 从文件分析中计算嵌套深度信息
        max_depth = 0
        total_depth = 0
        depth_count = 0

        # 遍历所有文件类型，收集深度信息
        for file_type_key, file_list in complexity_metrics.items():
            if file_type_key.endswith('_files') and isinstance(file_list, list):
                for file_info in file_list:
                    if isinstance(file_info, dict) and 'analysis' in file_info:
                        analysis = file_info['analysis']

                        # 对于Java文件，检查方法的嵌套深度（通过复杂度推算）
                        if file_type_key == 'java_files':
                            cyclomatic = analysis.get('cyclomatic_complexity', 0)
                            methods = analysis.get('methods', 0)
                            if methods > 0:
                                # 估算深度：复杂度越高，深度可能越深
                                estimated_depth = min(int(cyclomatic / methods) + 1, 10) if methods > 0 else 1
                                max_depth = max(max_depth, estimated_depth)
                                total_depth += estimated_depth
                                depth_count += 1

                        # 对于TypeScript/JavaScript/Vue文件，使用函数数量和复杂度估算
                        elif file_type_key in ['typescript_files', 'javascript_files', 'vue_files']:
                            functions = analysis.get('functions', 0)
                            classes = analysis.get('classes', 0)
                            if functions > 0 or classes > 0:
                                # 基于函数和类的数量估算嵌套深度
                                estimated_depth = min(2 + int((functions + classes) / 10), 8)
                                max_depth = max(max_depth, estimated_depth)
                                total_depth += estimated_depth
                                depth_count += 1

        # 计算平均深度
        avg_depth = round(total_depth / depth_count, 1) if depth_count > 0 else 0

        # 如果没有计算出深度，使用默认值
        if max_depth == 0:
            max_depth = 3  # 默认最大深度
            avg_depth = 2.5  # 默认平均深度

        return f"""
        <div class="detail-card">
            <h4>深度分析</h4>
            <ul class="detail-list">
                <li><span class="detail-label">最大嵌套深度</span><span class="detail-value">{max_depth}</span></li>
                <li><span class="detail-label">平均嵌套深度</span><span class="detail-value">{avg_depth}</span></li>
            </ul>
        </div>
        """

    def _generate_structure_complexity(self, complexity_metrics: dict) -> str:
        """生成结构复杂度"""
        # 统计各种结构元素
        total_classes = 0
        total_interfaces = 0
        total_methods = 0
        total_functions = 0

        for file_type_key, file_list in complexity_metrics.items():
            if file_type_key.endswith('_files') and isinstance(file_list, list):
                for file_info in file_list:
                    if isinstance(file_info, dict) and 'analysis' in file_info:
                        analysis = file_info['analysis']
                        # 处理可能是整数或列表的情况
                        classes = analysis.get('classes', [])
                        if isinstance(classes, list):
                            total_classes += len(classes)
                        elif isinstance(classes, int):
                            total_classes += classes

                        interfaces = analysis.get('interfaces', [])
                        if isinstance(interfaces, list):
                            total_interfaces += len(interfaces)
                        elif isinstance(interfaces, int):
                            total_interfaces += interfaces

                        methods = analysis.get('methods', [])
                        if isinstance(methods, list):
                            total_methods += len(methods)
                        elif isinstance(methods, int):
                            total_methods += methods

                        functions = analysis.get('functions', [])
                        if isinstance(functions, list):
                            total_functions += len(functions)
                        elif isinstance(functions, int):
                            total_functions += functions

        # 对于SQL文件，添加特殊统计
        sql_objects = {}
        sql_files = complexity_metrics.get('sql_files', [])
        for sql_file in sql_files:
            if isinstance(sql_file, dict) and 'analysis' in sql_file:
                analysis = sql_file['analysis']
                # 处理可能是整数或列表的情况
                tables = analysis.get('tables', [])
                if isinstance(tables, list):
                    sql_objects['tables'] = sql_objects.get('tables', 0) + len(tables)
                elif isinstance(tables, int):
                    sql_objects['tables'] = sql_objects.get('tables', 0) + tables

                views = analysis.get('views', [])
                if isinstance(views, list):
                    sql_objects['views'] = sql_objects.get('views', 0) + len(views)
                elif isinstance(views, int):
                    sql_objects['views'] = sql_objects.get('views', 0) + views

                procedures = analysis.get('procedures', [])
                if isinstance(procedures, list):
                    sql_objects['procedures'] = sql_objects.get('procedures', 0) + len(procedures)
                elif isinstance(procedures, int):
                    sql_objects['procedures'] = sql_objects.get('procedures', 0) + procedures

        structure_html = f"""
        <div class="detail-card">
            <h4>结构复杂度</h4>
            <ul class="detail-list">
                <li><span class="detail-label">类数量</span><span class="detail-value">{total_classes}</span></li>
                <li><span class="detail-label">接口数量</span><span class="detail-value">{total_interfaces}</span></li>
                <li><span class="detail-label">方法数量</span><span class="detail-value">{total_methods}</span></li>
                <li><span class="detail-label">函数数量</span><span class="detail-value">{total_functions}</span></li>
        """

        # 如果有SQL对象，添加到结构复杂度中
        if sql_objects:
            structure_html += f"""
                <li><span class="detail-label">数据库表</span><span class="detail-value">{sql_objects.get('tables', 0)}</span></li>
                <li><span class="detail-label">数据库视图</span><span class="detail-value">{sql_objects.get('views', 0)}</span></li>
                <li><span class="detail-label">存储过程</span><span class="detail-value">{sql_objects.get('procedures', 0)}</span></li>
            """

        structure_html += """
            </ul>
        </div>
        """

        return structure_html



    def _generate_effort_analysis(self) -> str:
        """生成二次开发新模块工作量分析"""
        effort = self.data.get('effort_estimate', {})
        new_module_efforts = effort.get('new_module_efforts', {})
        project_context = effort.get('project_context', {})

        # 生成新模块工作量表格
        module_efforts_html = ""
        if new_module_efforts:
            module_efforts_html = """
            <h3>新模块工作量估算</h3>
            <table class="module-table">
                <thead>
                    <tr>
                        <th>模块类型</th>
                        <th>描述</th>
                        <th>后端(人天)</th>
                        <th>前端(人天)</th>
                        <th>总计(人天)</th>
                    </tr>
                </thead>
                <tbody>
            """

            for module_type, module_effort in new_module_efforts.items():
                module_efforts_html += f"""
                    <tr>
                        <td>{module_type.replace('_', ' ').title()}</td>
                        <td>{module_effort['description']}</td>
                        <td>{module_effort['backend_effort']:.1f}</td>
                        <td>{module_effort['frontend_effort']:.1f}</td>
                        <td>{module_effort['total_effort']:.1f}</td>
                    </tr>
                """

            module_efforts_html += """
                </tbody>
            </table>
            """

        # 项目上下文信息
        context_html = ""
        if project_context:
            context_html = f"""
            <h3>项目上下文信息</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>{project_context.get('total_java_files', 0)}</h3>
                    <p>Java文件数</p>
                </div>
                <div class="metric-card">
                    <h3>{project_context.get('total_ts_files', 0)}</h3>
                    <p>TypeScript文件数</p>
                </div>
                <div class="metric-card">
                    <h3>{project_context.get('total_vue_files', 0)}</h3>
                    <p>Vue文件数</p>
                </div>
                <div class="metric-card">
                    <h3>{project_context.get('total_js_files', 0)}</h3>
                    <p>JavaScript文件数</p>
                </div>
                <div class="metric-card">
                    <h3>{project_context.get('module_count', 0)}</h3>
                    <p>模块数量</p>
                </div>
                <div class="metric-card">
                    <h3>{project_context.get('tech_stack_diversity', 0)}</h3>
                    <p>技术栈多样性</p>
                </div>
            </div>
            """

        # 理解成本
        understanding_cost_html = ""
        understanding_cost = effort.get('understanding_cost', 0)
        if understanding_cost > 0:
            understanding_cost_html = f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);">
                <h3>{understanding_cost:.1f}</h3>
                <p>代码理解成本(人天)</p>
            </div>
            """

        return f"""
        {context_html}
        {module_efforts_html}

        {understanding_cost_html}

        <!-- 风险因素 -->
        {self._generate_risk_factors()}

        <!-- 开发建议 -->
        {self._generate_development_recommendations()}
        """

    def _generate_recommendations(self) -> str:
        """生成建议和风险"""
        recommendations = self.data.get('recommendations', {})

        html = ""

        if recommendations.get('learning_priorities'):
            html += """
            <div class="recommendations">
                <h3>学习优先级</h3>
                <ul>
            """
            for priority in recommendations['learning_priorities']:
                html += f"<li>{priority}</li>"
            html += "</ul></div>"

        if recommendations.get('development_risks'):
            html += """
            <div class="risk-factors">
                <h3>开发风险</h3>
                <ul>
            """
            for risk in recommendations['development_risks']:
                html += f"<li>{risk}</li>"
            html += "</ul></div>"

        return html

    def _generate_risk_factors(self) -> str:
        """生成风险因素"""
        effort = self.data.get('effort_estimate', {})
        risk_factors = effort.get('risk_factors', [])

        if not risk_factors:
            return ""

        html = """
        <div class="risk-factors">
            <h3>开发风险因素</h3>
            <ul>
        """
        for risk in risk_factors:
            html += f"<li>{risk}</li>"
        html += "</ul></div>"

        return html

    def _generate_development_recommendations(self) -> str:
        """生成开发建议"""
        effort = self.data.get('effort_estimate', {})
        development_recommendations = effort.get('development_recommendations', [])

        if not development_recommendations:
            return ""

        html = """
        <div class="recommendations">
            <h3>开发建议</h3>
            <ul>
        """
        for recommendation in development_recommendations:
            html += f"<li>{recommendation}</li>"
        html += "</ul></div>"

        return html

    def _generate_chart_scripts(self) -> str:
        """生成图表脚本"""

        # 动态收集技术栈数据
        tech_data = {}

        # 技术栈显示名称映射
        tech_display_names = {
            'java': 'Java',
            'typescript': 'TypeScript',
            'javascript': 'JavaScript',
            'vue': 'Vue',
            'sql': 'SQL',
            'html': 'HTML',
            'css': 'CSS',
            'scss': 'SCSS',
            'xml': 'XML',
            'json': 'JSON',
            'yaml': 'YAML',
            'markdown': 'Markdown',
            'python': 'Python',
            'shell': 'Shell'
        }

        # 自动统计所有技术栈
        for module in self.data.get('module_analysis', {}).values():
            complexity_metrics = module.get('complexity_metrics', {})
            for file_type_key, file_list in complexity_metrics.items():
                if file_type_key.endswith('_files') and isinstance(file_list, list):
                    file_type = file_type_key.replace('_files', '')
                    file_count = len(file_list)

                    if file_count > 0:
                        display_name = tech_display_names.get(file_type, file_type.title())
                        tech_data[display_name] = tech_data.get(display_name, 0) + file_count

        # 复杂度数据
        complexity_data = {}
        for module_name, analysis in self.data.get('module_analysis', {}).items():
            complexity = analysis.get('complexity_metrics', {}).get('total_complexity', 0)
            if complexity > 0:
                complexity_data[module_name] = complexity

        # 生成技术栈图表脚本
        tech_chart_script = ""
        if tech_data:
            # 动态生成足够的颜色
            base_colors = [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                '#FF9F40', '#FF6B8A', '#4BC0C0', '#36A2EB', '#FF6384',
                '#C9CBCF', '#4BC0C0', '#FF6384', '#36A2EB', '#FFCE56'
            ]

            # 如果技术栈数量超过预定义颜色，生成更多颜色
            colors = base_colors[:len(tech_data)]
            if len(tech_data) > len(base_colors):
                import random
                random.seed(42)  # 固定种子确保颜色一致
                for i in range(len(tech_data) - len(base_colors)):
                    colors.append(f'#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}')

            tech_chart_script = f"""
        // 技术栈分布图
        const techCtx = document.getElementById('techStackChart').getContext('2d');
        new Chart(techCtx, {{
            type: 'doughnut',
            data: {{
                labels: {list(tech_data.keys())},
                datasets: [{{
                    data: {list(tech_data.values())},
                    backgroundColor: {colors}
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }},
                    title: {{
                        display: true,
                        text: '技术栈文件分布'
                    }}
                }}
            }}
        }});
            """

        # 生成复杂度图表脚本
        complexity_chart_script = ""
        if complexity_data:
            complexity_chart_script = f"""
        // 复杂度分析图
        const complexityCtx = document.getElementById('complexityChart').getContext('2d');
        new Chart(complexityCtx, {{
            type: 'bar',
            data: {{
                labels: {list(complexity_data.keys())},
                datasets: [{{
                    label: '圈复杂度',
                    data: {list(complexity_data.values())},
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: '模块复杂度分析'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '圈复杂度'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: '模块名称'
                        }}
                    }}
                }}
            }}
        }});
            """

        # 如果没有数据，显示提示信息
        if not tech_data and not complexity_data:
            return """
        // 显示提示信息
        document.addEventListener('DOMContentLoaded', function() {
            const techChart = document.getElementById('techStackChart');
            const complexityChart = document.getElementById('complexityChart');

            if (techChart) {
                techChart.style.display = 'flex';
                techChart.style.alignItems = 'center';
                techChart.style.justifyContent = 'center';
                techChart.style.fontSize = '16px';
                techChart.style.color = '#666';
                techChart.innerHTML = '暂无技术栈数据';
            }

            if (complexityChart) {
                complexityChart.style.display = 'flex';
                complexityChart.style.alignItems = 'center';
                complexityChart.style.justifyContent = 'center';
                complexityChart.style.fontSize = '16px';
                complexityChart.style.color = '#666';
                complexityChart.innerHTML = '暂无复杂度数据';
            }
        });
            """

        # 添加模块展开/折叠功能的JavaScript
        module_toggle_script = """
        // 模块详细分析展开/折叠功能
        function toggleModuleDetails(moduleName, toggleIcon) {
            const detailRow = document.getElementById('detail-' + moduleName);

            if (!detailRow) {
                console.error('Detail row not found for module:', moduleName);
                return;
            }

            const detailContent = detailRow.querySelector('.module-detail-content');
            if (!detailContent) {
                console.error('Detail content not found for module:', moduleName);
                return;
            }

            if (detailRow.style.display === 'none' || detailRow.style.display === '') {
                detailRow.style.display = 'table-row';
                detailContent.style.display = 'block'; // Make content visible
                toggleIcon.textContent = '▲';
                toggleIcon.classList.add('expanded');
            } else {
                detailRow.style.display = 'none';
                detailContent.style.display = 'none'; // Hide content
                toggleIcon.textContent = '▼';
                toggleIcon.classList.remove('expanded');
            }
        }

        // 页面加载完成后的初始化
        document.addEventListener('DOMContentLoaded', function() {
            // 直接绑定点击事件到所有toggle-icon元素
            const toggleIcons = document.querySelectorAll('.toggle-icon');
            console.log('Found', toggleIcons.length, 'toggle icons');

            toggleIcons.forEach(function(toggleIcon) {
                toggleIcon.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();

                    // 找到父级的module-row
                    let moduleRow = this;
                    while (moduleRow && !moduleRow.classList.contains('module-row')) {
                        moduleRow = moduleRow.parentElement;
                    }

                    if (moduleRow) {
                        const moduleName = moduleRow.getAttribute('data-module');
                        if (moduleName) {
                            console.log('Toggling module:', moduleName);
                            toggleModuleDetails(moduleName, this);
                        } else {
                            console.error('Module name not found for row:', moduleRow);
                        }
                    } else {
                        console.error('Module row not found for toggle icon:', this);
                    }
                });
            });
        });
        """

        return tech_chart_script + complexity_chart_script + module_toggle_script

def main():
    parser = argparse.ArgumentParser(description='通用项目复杂度分析报告生成器')
    parser.add_argument('analysis_file', help='分析结果JSON文件路径')
    parser.add_argument('-o', '--output', help='输出HTML文件路径')

    args = parser.parse_args()

    generator = ReportGenerator(args.analysis_file)
    generator.generate_html_report(args.output)

if __name__ == '__main__':
    main()
