#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目复杂度分析器包
包含各种分析器模块
"""

__version__ = "1.0.0"
__author__ = "https://github.com/handsomestWei/"

# 导出主要的类和函数
from .analyzer_config import get_config, AnalyzerConfig

from .core_analyzer import GenericComplexityAnalyzer
from .project_detector import get_project_detector, detect_module_type
from .report_generator import ReportGenerator, generate_report, print_summary

__all__ = [
    'get_config',
    'AnalyzerConfig',

    'GenericComplexityAnalyzer',
    'get_project_detector',
    'detect_module_type',
    'ReportGenerator',
    'generate_report',
    'print_summary'
]
