#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术栈分布模块
生成技术栈分布图表的HTML内容
"""

class TechStackGenerator:
    def __init__(self, data, language_manager=None, config=None):
        self.data = data
        self.language_manager = language_manager
        self.config = config

    def generate_tech_stack_chart(self) -> str:
        """生成技术栈分布图表脚本"""
        tech_data = {}
        display_names = self._get_language_display_names()
        language_priorities = self._get_language_priorities()

        # 统计主要技术栈
        module_analysis = self.data.get('module_analysis', {})

        for module_name, module in module_analysis.items():
            complexity_data = module.get('complexity', {})

            if isinstance(complexity_data, dict) and 'error' not in complexity_data:
                file_complexity = complexity_data.get('file_complexity', {})

                if file_complexity:
                    for file_path, file_data in file_complexity.items():
                        if isinstance(file_data, dict) and 'file_extension' in file_data:
                            file_ext = file_data['file_extension'].lower()
                            if file_ext.startswith('.'):
                                file_type = file_ext[1:]  # 去掉点号
                            else:
                                file_type = file_ext

                            # 只统计主要技术栈
                            if file_type in display_names:
                                tech_data[file_type] = tech_data.get(file_type, 0) + 1

        # 按优先级排序，只取前10个主要技术栈
        if tech_data:
            # 按优先级排序
            sorted_tech = sorted(tech_data.items(),
                               key=lambda x: (language_priorities.get(x[0], 999), -x[1]))

            # 只取前10个
            top_tech = dict(sorted_tech[:10])

            # 计算总数用于百分比计算
            total_files = sum(top_tech.values())

            # 动态生成足够的颜色
            base_colors = [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                '#FF9F40', '#FF6B8A', '#4BC0C0', '#36A2EB', '#FF6384'
            ]

            # 如果技术栈数量超过预定义颜色，生成更多颜色
            colors = base_colors[:len(top_tech)]
            if len(top_tech) > len(base_colors):
                import random
                random.seed(42)  # 固定种子确保颜色一致
                for i in range(len(top_tech) - len(base_colors)):
                    colors.append(f'#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}')

            return f"""
        // 技术栈分布图
        const techCtx = document.getElementById('techStackChart').getContext('2d');
        new Chart(techCtx, {{
            type: 'doughnut',
            data: {{
                labels: {[display_names.get(k, k) for k in top_tech.keys()]},
                datasets: [{{
                    data: {list(top_tech.values())},
                    backgroundColor: {colors}
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            generateLabels: function(chart) {{
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {{
                                    return data.labels.map((label, i) => {{
                                        const value = data.datasets[0].data[i];
                                        const percentage = ((value / {total_files}) * 100).toFixed(1);
                                        return {{
                                            text: `${{label}} (${{value}} - ${{percentage}}%)`,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            strokeStyle: data.datasets[0].backgroundColor[i],
                                            lineWidth: 0,
                                            hidden: false,
                                            index: i
                                        }};
                                    }});
                                }}
                                return [];
                            }}
                        }}
                    }},
                    title: {{
                        display: true,
                        text: '主要技术栈文件分布'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const label = context.label || '';
                                const value = context.parsed;
                                const percentage = ((value / {total_files}) * 100).toFixed(1);
                                return `${{label}}: ${{value}} 文件 (${{percentage}}%)`;
                            }}
                        }}
                    }}
                }}
            }}
        }});
            """
        else:
            return """
        // 技术栈分布图 - 无数据
        document.addEventListener('DOMContentLoaded', function() {
            const techChart = document.getElementById('techStackChart');
            if (techChart) {
                techChart.style.display = 'flex';
                techChart.style.alignItems = 'center';
                techChart.style.justifyContent = 'center';
                techChart.style.fontSize = '16px';
                techChart.style.color = '#666';
                techChart.innerHTML = '暂无技术栈数据';
            }
        });
            """

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
            'html': 'HTML文件',
            'scss': 'SCSS文件',
            'sass': 'Sass文件',
            'ts': 'TypeScript文件',
            'tsx': 'TypeScript React文件',
            'js': 'JavaScript文件',
            'jsx': 'JavaScript React文件',
            'py': 'Python文件',
            'htm': 'HTML文件',
            'xml': 'XML文件',
            'json': 'JSON文件',
            'yaml': 'YAML文件',
            'yml': 'YAML文件',
            'md': 'Markdown文件',
            'sh': 'Shell脚本',
            'bash': 'Bash脚本',
            'properties': 'Properties文件'
        }

    def _get_language_priorities(self) -> dict:
        """获取语言优先级"""
        return {
            'java': 1,
            'typescript': 2,
            'javascript': 3,
            'vue': 4,
            'python': 5,
            'sql': 6,
            'css': 7,
            'html': 8,
            'scss': 9,
            'xml': 10,
            'json': 11,
            'yaml': 12,
            'md': 13,
            'sh': 14,
            'properties': 15
        }
