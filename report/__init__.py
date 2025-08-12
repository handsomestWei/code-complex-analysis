#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML报告生成器包
包含各个模块的HTML生成功能
"""

from .gen_html_overview import OverviewGenerator
from .gen_html_module import ModuleGenerator
from .gen_html_module_core import ModuleCoreGenerator
from .gen_html_module_structure import ModuleStructureGenerator
from .gen_html_module_complexity import ModuleComplexityGenerator
from .gen_html_tech import TechStackGenerator
from .gen_html_complexity import ComplexityGenerator
from .gen_html_effort import EffortGenerator
from .gen_html_recommend import RecommendationGenerator
from .gen_html_main import HTMLReportGenerator

__all__ = [
    'OverviewGenerator',
    'ModuleGenerator',
    'ModuleCoreGenerator',
    'ModuleStructureGenerator',
    'ModuleComplexityGenerator',
    'TechStackGenerator',
    'ComplexityGenerator',
    'EffortGenerator',
    'RecommendationGenerator',
    'HTMLReportGenerator'
]
