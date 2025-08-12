#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用项目代码复杂度分析工具
专门针对多模块、多技术栈的复杂项目进行分析

重构后的主文件，使用模块化架构
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# 导入重构后的模块
from analyzers.analyzer_config import get_config



def create_argument_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='通用项目代码复杂度分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python proj_comp_analyzer.py /path/to/project                    # 分析项目
  python proj_comp_analyzer.py /path/to/project -o report.json     # 指定输出文件
  python proj_comp_analyzer.py /path/to/project -v                 # 详细输出
  python proj_comp_analyzer.py /path/to/project --no-parallel      # 禁用并行处理

        """
    )

    # 必需参数
    parser.add_argument(
        'project_path',
        help='项目根路径'
    )

    # 可选参数
    parser.add_argument(
        '-o', '--output',
        help='输出文件路径'
    )

    parser.add_argument(
        '-c', '--config',
        help='配置文件路径'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出模式'
    )

    parser.add_argument(
        '--no-parallel',
        action='store_true',
        help='禁用并行处理'
    )



    parser.add_argument(
        '--timeout',
        type=int,
        help='分析超时时间（秒）'
    )

    parser.add_argument(
        '--max-file-size',
        type=int,
        help='最大文件大小（MB）'
    )



    return parser


def validate_project_path(project_path: str) -> Path:
    """
    验证项目路径

    Args:
        project_path: 项目路径字符串

    Returns:
        验证后的Path对象

    Raises:
        FileNotFoundError: 项目路径不存在
        NotADirectoryError: 项目路径不是目录
    """
    path = Path(project_path)

    if not path.exists():
        raise FileNotFoundError(f"项目路径不存在: {project_path}")

    if not path.is_dir():
        raise NotADirectoryError(f"项目路径不是目录: {project_path}")

    return path


def setup_logging(verbose: bool = False, config_file: Optional[str] = None):
    """
    设置日志配置

    Args:
        verbose: 是否启用详细输出
        config_file: 配置文件路径
    """
    if verbose:
        log_level = logging.DEBUG
    else:
        # 从配置文件获取日志级别
        try:
            config = get_config()
            log_level = getattr(logging, config.logging_level.upper(), logging.INFO)
        except Exception:
            log_level = logging.INFO

    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[]
    )

    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # 如果指定了配置文件，尝试从配置获取日志文件设置
    if config_file:
        try:
            config = get_config()
            if config.logging_file:
                try:
                    file_handler = logging.FileHandler(config.logging_file, encoding='utf-8')
                    file_handler.setLevel(log_level)
                    file_formatter = logging.Formatter(log_format)
                    file_handler.setFormatter(file_formatter)
                    root_logger.addHandler(file_handler)
                    logging.info(f"日志文件处理器已添加到: {config.logging_file}")
                except Exception as e:
                    logging.warning(f"无法创建日志文件处理器 {config.logging_file}: {e}")
        except Exception:
            pass

    # 设置第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

    if verbose:
        logging.info("详细输出模式已启用")


def apply_command_line_overrides(args: argparse.Namespace):
    """
    应用命令行参数覆盖配置

    Args:
        args: 命令行参数
    """
    try:
        config = get_config()

        # 覆盖并行处理配置
        if args.no_parallel:
            config.parallel_processing['enabled'] = False
            print("并行处理已禁用")



        # 覆盖超时配置
        if args.timeout:
            config.analysis_timeout = args.timeout
            print(f"分析超时时间设置为: {args.timeout}秒")

        # 覆盖最大文件大小配置
        if args.max_file_size:
            max_size_bytes = args.max_file_size * 1024 * 1024
            config.max_file_size = max_size_bytes
            print(f"最大文件大小设置为: {args.max_file_size}MB")



    except Exception as e:
        print(f"应用命令行覆盖配置失败: {e}")





def main():
    """主函数"""
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        # 验证项目路径
        project_path = validate_project_path(args.project_path)

        # 设置日志
        setup_logging(args.verbose, args.config)
        logger = logging.getLogger(__name__)



        # 应用命令行参数覆盖
        apply_command_line_overrides(args)

        # 导入并创建分析器（避免循环导入）
        from analyzers.core_analyzer import GenericComplexityAnalyzer

        # 创建分析器
        analyzer = GenericComplexityAnalyzer(str(project_path))

        # 开始分析
        logger.info("开始分析项目...")
        analyzer.scan_project()

        # 生成报告
        output_file = args.output
        if output_file:
            analyzer.generate_report(output_file)
        else:
            analyzer.generate_report()

        print("\n分析完成！")
        return 0

    except KeyboardInterrupt:
        print("\n分析被用户中断")
        return 130

    except FileNotFoundError as e:
        print(f"错误: {e}")
        return 1

    except NotADirectoryError as e:
        print(f"错误: {e}")
        return 1

    except Exception as e:
        print(f"分析失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    finally:
        # 确保资源被清理
        if 'analyzer' in locals():
            try:
                analyzer.cleanup()
            except Exception:
                pass


if __name__ == '__main__':
    exit(main())
