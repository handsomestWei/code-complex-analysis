#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发建议模块
生成建议和风险部分的HTML内容
"""

class RecommendationGenerator:
    def __init__(self, data, language_manager=None, config=None):
        self.data = data
        self.language_manager = language_manager
        self.config = config

    def generate_recommendations(self) -> str:
        """生成建议和风险"""
        recommendations = self.data.get('recommendations', [])

        html = ""

        if recommendations and isinstance(recommendations, list):
            html += """
            <div class="recommendations">
                <h3>开发建议</h3>
                <ul>
            """
            for recommendation in recommendations:
                html += f"<li>{recommendation}</li>"
            html += "</ul></div>"

        return html

    def generate_risk_factors(self) -> str:
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

    def generate_development_recommendations(self) -> str:
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
