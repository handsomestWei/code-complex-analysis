#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二次开发新模块工作量估算模块
生成工作量分析部分的HTML内容
"""

class EffortGenerator:
    def __init__(self, data, language_manager=None, config=None):
        self.data = data
        self.language_manager = language_manager
        self.config = config

    def generate_effort_analysis(self) -> str:
        """生成二次开发新模块工作量分析"""
        effort = self.data.get('effort_estimate', {})
        new_module_efforts = effort.get('new_module_efforts', {})
        project_context = effort.get('project_context', {})

        # 生成新模块工作量表格
        module_efforts_html = ""
        if new_module_efforts:
            # 使用effort_analyzer.py的标准输出格式
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

            # 模块类型映射
            module_type_mapping = {
                'small_module': '小型模块',
                'medium_module': '中型模块',
                'large_module': '大型模块'
            }

            for module_type, module_effort in new_module_efforts.items():
                if isinstance(module_effort, dict):
                    # 使用effort_analyzer.py的数据结构
                    backend_effort = module_effort.get('backend', 0)
                    frontend_effort = module_effort.get('frontend', 0)
                    total_effort = module_effort.get('total', backend_effort + frontend_effort)

                    # 获取中文描述
                    description = module_type_mapping.get(module_type, module_type.replace('_', ' ').title())

                module_efforts_html += f"""
                    <tr>
                            <td>{description}</td>
                            <td>基于项目复杂度估算的{description}开发工作量</td>
                            <td>{backend_effort:.1f}</td>
                            <td>{frontend_effort:.1f}</td>
                            <td>{total_effort:.1f}</td>
                    </tr>
                """

            module_efforts_html += """
                </tbody>
            </table>
            """
        else:
            # 如果没有工作量估算数据，生成基于项目复杂度的估算
            total_complexity = 0
            total_files = 0
            total_lines = 0

            for module in self.data.get('module_analysis', {}).values():
                complexity_data = module.get('complexity', {})
                if complexity_data and 'error' not in complexity_data:
                    total_complexity += complexity_data.get('total_complexity', 0)
                    total_files += complexity_data.get('total_files', 0)
                    total_lines += complexity_data.get('total_lines', 0)

            if total_complexity > 0:
                # 基于复杂度和文件数估算工作量
                # 使用更合理的估算公式
                base_effort = total_files * 0.5  # 每个文件基础0.5人天
                complexity_effort = total_complexity * 0.05  # 每20复杂度约1人天
                lines_effort = total_lines * 0.001  # 每1000行约1人天

                estimated_effort = base_effort + complexity_effort + lines_effort

                # 按技术栈分类估算
                tech_stack = self._get_tech_stack_categories()
                backend_files = 0
                frontend_files = 0

                for module in self.data.get('module_analysis', {}).values():
                    complexity_data = module.get('complexity', {})
                    if complexity_data and 'error' not in complexity_data:
                        for file_path, file_data in complexity_data.get('file_complexity', {}).items():
                            if isinstance(file_data, dict):
                                file_ext = file_data.get('file_extension', '').lower()
                                if file_ext in tech_stack.get('backend', []):
                                    backend_files += 1
                                elif file_ext in tech_stack.get('frontend', []):
                                    frontend_files += 1

                backend_effort = estimated_effort * 0.6 if backend_files > frontend_files else estimated_effort * 0.4
                frontend_effort = estimated_effort - backend_effort

                module_efforts_html = f"""
                <h3>基于项目复杂度的工作量估算</h3>
                <div class="metrics-grid">
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
                    <div class="metric-card">
                        <h3>{estimated_effort:.1f}</h3>
                        <p>估算工作量(人天)</p>
                    </div>
                </div>

                <h4>工作量分布</h4>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>{backend_effort:.1f}</h3>
                        <p>后端开发(人天)</p>
                    </div>
                    <div class="metric-card">
                        <h3>{frontend_effort:.1f}</h3>
                        <p>前端开发(人天)</p>
                    </div>
                </div>
                """

        # 项目上下文信息
        context_html = ""
        if project_context:
            # 动态生成项目上下文信息
            context_html = """
            <h3>项目上下文信息</h3>
            <div class="metrics-grid">
            """

            # 动态添加语言文件数统计
            supported_languages = self._get_supported_languages()
            for lang in supported_languages:
                # 构建键名（例如：total_java_files, total_python_files）
                key_name = f'total_{lang}_files'
                count = project_context.get(key_name, 0)
                if count > 0:  # 只显示有文件的语言
                    display_name = self._get_language_display_names().get(lang, f'{lang.title()}文件')
                    context_html += f"""
                <div class="metric-card">
                    <h3>{count}</h3>
                    <p>{display_name}</p>
                </div>
                    """

            # 添加其他通用指标
            context_html += f"""
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
        else:
            # 如果没有项目上下文数据，从模块分析中生成
            module_count = len(self.data.get('module_analysis', {}))
            if module_count > 0:
                context_html = f"""
                <h3>项目基本信息</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>{module_count}</h3>
                        <p>模块数量</p>
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
        else:
            # 如果没有理解成本数据，基于项目复杂度估算
            total_complexity = sum(
                module.get('complexity', {}).get('total_complexity', 0)
                for module in self.data.get('module_analysis', {}).values()
                if module.get('complexity') and 'error' not in module.get('complexity', {})
            )
            if total_complexity > 0:
                estimated_understanding_cost = total_complexity * 0.02  # 每50复杂度约1人天理解成本
                understanding_cost_html = f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);">
                    <h3>{estimated_understanding_cost:.1f}</h3>
                    <p>估算理解成本(人天)</p>
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

    def _get_tech_stack_categories(self):
        """动态获取技术栈分类"""
        if self.config:
            try:
                return self.config.tech_stack_categories
            except Exception:
                pass

        # 回退到默认分类
        return {
            'backend': ['java', 'xml', 'properties', 'sql', 'sh', 'python'],
            'frontend': ['typescript', 'javascript', 'vue', 'scss', 'css', 'html'],
            'mobile': ['vue', 'javascript', 'json'],
            'config': ['yaml', 'json', 'xml', 'properties'],
            'docs': ['markdown', 'html']
        }

    def _get_supported_languages(self) -> list:
        """获取支持的语言列表"""
        try:
            if self.language_manager:
                return self.language_manager.get_supported_languages()
        except Exception:
            pass
        return ['java', 'typescript', 'javascript', 'vue', 'python', 'sql', 'css', 'html']

    def _get_language_display_names(self) -> dict:
        """获取语言显示名称"""
        return {
            'java': 'Java文件',
            'typescript': 'TypeScript文件',
            'javascript': 'JavaScript文件',
            'vue': 'Vue文件',
            'python': 'Python文件',
            'sql': 'SQL文件',
            'css': 'CSS文件',
            'html': 'HTML文件'
        }
