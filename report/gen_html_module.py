#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块分析主模块
整合所有子模块，完成模块分析部分的HTML生成
"""

from .gen_html_module_core import ModuleCoreGenerator
from .gen_html_module_structure import ModuleStructureGenerator
from .gen_html_module_complexity import ModuleComplexityGenerator

class ModuleGenerator:
    def __init__(self, data, language_manager=None, config=None):
        self.data = data
        self.language_manager = language_manager
        self.config = config

        # 初始化各个子模块
        self.core_generator = ModuleCoreGenerator(data, language_manager, config)
        self.structure_generator = ModuleStructureGenerator(data, language_manager, config)
        self.complexity_generator = ModuleComplexityGenerator(data, language_manager, config)

    def generate_module_table(self) -> str:
        """生成模块分析表格（包含展开/折叠的详细分析）"""
        # 使用核心模块生成完整的表格（包含详细分析）
        table_html, module_data, sorted_file_types, other_file_types = self.core_generator.generate_module_table()
        return table_html
