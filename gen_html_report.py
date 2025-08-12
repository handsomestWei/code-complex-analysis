#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用项目复杂度分析报告生成器
使用模块化架构，从report包调用各个功能模块
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from report.gen_html_main import HTMLReportGenerator
except ImportError as e:
    print(f"错误: 无法导入report包: {e}")
    print("请确保report目录存在且包含所有必要的模块文件")
    sys.exit(1)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='通用项目复杂度分析报告生成器')
    parser.add_argument('analysis_file', help='分析结果JSON文件路径')
    parser.add_argument('-o', '--output', help='输出HTML文件路径')

    args = parser.parse_args()

    try:
        generator = HTMLReportGenerator(args.analysis_file)
        generator.generate_html_report(args.output)
        print("✅ HTML报告生成成功！")
    except Exception as e:
        print(f"❌ 生成HTML报告时发生错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
