#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML报告生成器主入口
整合所有模块，完成整个HTML报告生成
"""

import json
import os
from pathlib import Path
from datetime import datetime
import argparse

# 导入各个模块
from .gen_html_overview import OverviewGenerator
from .gen_html_module import ModuleGenerator
from .gen_html_tech import TechStackGenerator
from .gen_html_complexity import ComplexityGenerator
from .gen_html_effort import EffortGenerator
from .gen_html_recommend import RecommendationGenerator

# 导入分析器相关模块
try:
    from analyzers.language_analyzer_manager import get_analyzer_manager
    from analyzers.analyzer_config import get_config
    DYNAMIC_LANGUAGE_SUPPORT = True
except ImportError:
    DYNAMIC_LANGUAGE_SUPPORT = False
    print("警告: 无法导入动态语言支持模块，将使用默认配置")

class HTMLReportGenerator:
    def __init__(self, analysis_file: str):
        self.analysis_file = Path(analysis_file)
        with open(self.analysis_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        # 初始化动态语言支持
        self.language_manager = None
        self.config = None
        self.dynamic_support_enabled = DYNAMIC_LANGUAGE_SUPPORT

        if self.dynamic_support_enabled:
            try:
                self.language_manager = get_analyzer_manager()
                self.config = get_config()
            except Exception as e:
                print(f"警告: 初始化动态语言支持失败: {e}")
                self.dynamic_support_enabled = False

        # 初始化各个生成器模块
        self.overview_generator = OverviewGenerator(self.data, self.language_manager, self.config)
        self.module_generator = ModuleGenerator(self.data, self.language_manager, self.config)
        self.tech_generator = TechStackGenerator(self.data, self.language_manager, self.config)
        self.complexity_generator = ComplexityGenerator(self.data, self.language_manager, self.config)
        self.effort_generator = EffortGenerator(self.data, self.language_manager, self.config)
        self.recommendation_generator = RecommendationGenerator(self.data, self.language_manager, self.config)

    def generate_html_report(self, output_file: str = None):
        """生成HTML报告"""
        if not output_file:
            output_file = f"project_complexity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        html_content = self._generate_html_content()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML报告已生成: {output_file}")

    def _generate_html_content(self) -> str:
        """生成HTML内容"""
        # 直接生成HTML内容，不使用模板替换
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>项目复杂度分析报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .section {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}

        .section h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}

        .metric-card h3 {{
            font-size: 2em;
            margin-bottom: 5px;
        }}

        .metric-card p {{
            opacity: 0.9;
        }}

        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}

        .module-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .module-table th,
        .module-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}

        .module-table th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}

        .module-table tr:hover {{
            background-color: #f5f5f5;
        }}

        .complexity-high {{
            color: #e74c3c;
            font-weight: bold;
        }}

        .complexity-medium {{
            color: #f39c12;
            font-weight: bold;
        }}

        .complexity-low {{
            color: #27ae60;
            font-weight: bold;
        }}

        .recommendations {{
            background: linear-gradient(135deg, #a8e6cf 0%, #88d8c0 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}

        .recommendations h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}

        .recommendations ul {{
            list-style: none;
        }}

        .recommendations li {{
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.3);
        }}

        .recommendations li:before {{
            content: "✓";
            color: #27ae60;
            font-weight: bold;
            margin-right: 10px;
        }}

        .risk-factors {{
            background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}

        .risk-factors h3 {{
            margin-bottom: 15px;
        }}

        .risk-factors ul {{
            list-style: none;
        }}

        .risk-factors li {{
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.3);
        }}

        .risk-factors li:before {{
            content: "⚠";
            margin-right: 10px;
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}

        /* 详细模块分析样式 */
        .module-detail {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 25px;
            overflow: hidden;
        }}

        .module-detail-header {{
            background: linear-gradient(135deg, #495057 0%, #343a40 100%);
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            position: relative;
        }}

        .module-detail-header:hover {{
            background: linear-gradient(135deg, #343a40 0%, #212529 100%);
        }}

        .module-detail-header h3 {{
            margin: 0;
            font-size: 1.2em;
        }}

        .module-detail-header h4 {{
            margin: 0;
            font-size: 1.1em;
        }}

        .module-detail-header .toggle-icon {{
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.2em;
        }}

        /* 移除冲突的CSS规则 - 这些规则会阻止模块展开 */
        /* .module-detail-content {{
            padding: 20px;
            display: none;
        }}

        .module-detail-content.active {{
            display: block;
        }} */

        .detail-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .detail-card {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
        }}

        .detail-card h4 {{
            color: #495057;
            margin-bottom: 10px;
            font-size: 1.1em;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 5px;
        }}

        .detail-list {{
            list-style: none;
            margin: 0;
            padding: 0;
        }}

        .detail-list li {{
            padding: 3px 0;
            border-bottom: 1px solid #f8f9fa;
            display: flex;
            justify-content: space-between;
        }}

        .detail-list li:last-child {{
            border-bottom: none;
        }}

        .detail-label {{
            color: #6c757d;
            font-weight: 500;
        }}

        .detail-value {{
            color: #495057;
            font-weight: bold;
        }}

        .complexity-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}

        .complexity-badge.low {{
            background: #d4edda;
            color: #155724;
        }}

        .complexity-badge.medium {{
            background: #fff3cd;
            color: #856404;
        }}

        .complexity-badge.high {{
            background: #f8d7da;
            color: #721c24;
        }}

        .error {{
            color: #dc3545;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            font-size: 0.9em;
        }}

        .file-list {{
            max-height: 200px;
            overflow-y: auto;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 10px;
            margin-top: 10px;
        }}

        .file-item {{
            padding: 5px 0;
            border-bottom: 1px solid #e9ecef;
            font-size: 0.9em;
            color: #6c757d;
        }}

        .file-item:last-child {{
            border-bottom: none;
        }}

        /* 模块表格展开/折叠样式 */
        .module-name-cell {{
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
        }}

        .toggle-icon {{
            cursor: pointer;
            font-size: 1.2em;
            color: #007bff;
            transition: transform 0.3s ease;
            user-select: none;
            padding: 4px;
            border-radius: 4px;
            display: inline-block;
        }}

        .toggle-icon:hover {{
            color: #0056b3;
            background-color: rgba(0, 123, 255, 0.1);
        }}

        .toggle-icon.expanded {{
            transform: rotate(180deg);
        }}

        .module-detail-row {{
            background-color: #f8f9fa;
        }}

        .module-detail-row .module-detail-content {{
            padding: 20px;
            background: white;
            border-radius: 8px;
            margin: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}

        /* 确保详情行在展开时正确显示 */
        .module-detail-row.expanded {{
            display: table-row !important;
        }}

        .module-detail-row.collapsed {{
            display: none !important;
        }}

        .module-row:hover {{
            background-color: #f5f5f5;
        }}

        .detail-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .detail-card {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
        }}

        .detail-card h4 {{
            color: #495057;
            margin-bottom: 10px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
        }}

        .detail-list {{
            list-style: none;
            padding: 0;
        }}

        .detail-list li {{
            padding: 8px 0;
            border-bottom: 1px solid #f1f3f4;
            display: flex;
            justify-content: space-between;
        }}

        .detail-list li:last-child {{
            border-bottom: none;
        }}

        .detail-label {{
            font-weight: 500;
            color: #6c757d;
        }}

        .detail-value {{
            color: #495057;
            font-weight: 600;
        }}

        .dependency-item {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 8px 12px;
            margin: 5px 0;
            font-size: 0.9em;
        }}

        .structure-item {{
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 4px;
            padding: 10px;
            margin: 8px 0;
        }}

        .structure-item.exists {{
            background: #e8f5e8;
            border-color: #a5d6a7;
        }}

        .structure-item.not-exists {{
            background: #ffebee;
            border-color: #ef9a9a;
        }}
    </style>
</head>

<body>
    <div class="container">
        <div class="header">
            <h1>项目复杂度分析报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <!-- 项目概览 -->
        <div class="section">
            <h2>项目概览</h2>
            <div class="metrics-grid">
                {self.overview_generator.generate_overview_metrics()}
            </div>
        </div>

        <!-- 模块分析 -->
        <div class="section">
            <h2>模块分析</h2>
            {self.module_generator.generate_module_table()}
        </div>

        <!-- 技术栈分布 -->
        <div class="section">
            <h2>技术栈分布</h2>
            <div class="chart-container">
                <canvas id="techStackChart"></canvas>
            </div>
        </div>

        <!-- 复杂度分析 -->
        <div class="section">
            <h2>复杂度分析</h2>
            <div class="chart-container">
                <canvas id="complexityChart"></canvas>
            </div>
        </div>

        <!-- 二次开发新模块工作量估算 -->
        <div class="section">
            <h2>二次开发新模块工作量估算</h2>
            {self.effort_generator.generate_effort_analysis()}
        </div>

        <!-- 建议和风险 -->
        <div class="section">
            <h2>开发建议</h2>
            {self.recommendation_generator.generate_recommendations()}
        </div>

        <div class="footer">
            <p>本报告由通用项目复杂度分析工具生成</p>
        </div>
    </div>

    <script>
        // 模块表格展开/折叠功能
        document.addEventListener('DOMContentLoaded', function () {{
            console.log('DOM loaded, initializing module toggle functionality...');

            // 为所有模块名称单元格添加点击事件
            const moduleNameCells = document.querySelectorAll('.module-name-cell');
            console.log('Found', moduleNameCells.length, 'module name cells');

            moduleNameCells.forEach(cell => {{
                cell.addEventListener('click', function (e) {{
                    e.preventDefault();
                    e.stopPropagation();

                    console.log('Module cell clicked:', this);

                    const row = this.closest('tr');
                    const moduleName = row.getAttribute('data-module');
                    const detailRow = document.getElementById(`detail-${{moduleName}}`);
                    const toggleIcon = this.querySelector('.toggle-icon');

                    console.log('Module name:', moduleName);
                    console.log('Detail row:', detailRow);
                    console.log('Toggle icon:', toggleIcon);

                    if (detailRow) {{
                        const isCurrentlyVisible = detailRow.style.display !== 'none' && detailRow.style.display !== '';

                        if (!isCurrentlyVisible) {{
                            // 展开模块
                            detailRow.style.display = 'table-row';
                            if (toggleIcon) {{
                                toggleIcon.textContent = '▲';
                                toggleIcon.classList.add('expanded');
                            }}
                            console.log('Module expanded:', moduleName);
                        }} else {{
                            // 折叠模块
                            detailRow.style.display = 'none';
                            if (toggleIcon) {{
                                toggleIcon.textContent = '▼';
                                toggleIcon.classList.remove('expanded');
                            }}
                            console.log('Module collapsed:', moduleName);
                        }}
                    }} else {{
                        console.error('Detail row not found for module:', moduleName);
                    }}
                }});
            }});

            // 初始化图表
            console.log('Initializing charts...');
        }});

        {self._generate_chart_scripts()}
    </script>
</body>

</html>"""

        return html_content

    def _generate_chart_scripts(self) -> str:
        """生成图表脚本"""
        try:
            tech_chart_script = self.tech_generator.generate_tech_stack_chart()

            complexity_chart_script = self.complexity_generator.generate_complexity_chart()

            combined_script = tech_chart_script + complexity_chart_script

            return combined_script
        except Exception as e:
            print(f"生成图表脚本时出错: {e}")
            import traceback
            traceback.print_exc()
            # 返回一个基本的图表脚本作为回退
            return """
        // 图表脚本生成失败，显示错误信息
        document.addEventListener('DOMContentLoaded', function() {
            const techChart = document.getElementById('techStackChart');
            const complexityChart = document.getElementById('complexityChart');

            if (techChart) {
                techChart.innerHTML = '<p style="color: red;">技术栈图表生成失败</p>';
            }
            if (complexityChart) {
                complexityChart.innerHTML = '<p style="color: red;">复杂度图表生成失败</p>';
            }
        });
            """

def main():
    parser = argparse.ArgumentParser(description='通用项目复杂度分析报告生成器')
    parser.add_argument('analysis_file', help='分析结果JSON文件路径')
    parser.add_argument('-o', '--output', help='输出HTML文件路径')

    args = parser.parse_args()

    generator = HTMLReportGenerator(args.analysis_file)
    generator.generate_html_report(args.output)

if __name__ == '__main__':
    main()
