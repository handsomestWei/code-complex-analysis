#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复杂度分析模块
生成复杂度分析图表的HTML内容
"""

class ComplexityGenerator:
    def __init__(self, data, language_manager=None, config=None):
        self.data = data
        self.language_manager = language_manager
        self.config = config

    def generate_complexity_chart(self) -> str:
        """生成复杂度分析图表脚本"""
        complexity_data = {}

        for module_name, analysis in self.data.get('module_analysis', {}).items():
            # 检查模块是否有complexity字段且是对象类型
            complexity_data_inner = analysis.get('complexity', {})
            if isinstance(complexity_data_inner, dict) and 'error' not in complexity_data_inner:
                complexity = complexity_data_inner.get('total_complexity', 0)
                # 确保复杂度值有效
                if complexity and complexity > 0:
                    complexity_data[module_name] = complexity
                else:
                    # 如果没有total_complexity，尝试从其他字段获取
                    file_complexity = complexity_data_inner.get('file_complexity', {})
                    if file_complexity:
                        total_complexity = sum(
                            file_data.get('total_complexity', 0)
                            for file_data in file_complexity.values()
                            if isinstance(file_data, dict)
                        )
                        if total_complexity > 0:
                            complexity_data[module_name] = total_complexity

        # 生成复杂度图表脚本
        if complexity_data:
            return f"""
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
        else:
            return """
        // 显示提示信息
        document.addEventListener('DOMContentLoaded', function() {
            const complexityChart = document.getElementById('complexityChart');
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
