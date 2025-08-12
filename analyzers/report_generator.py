#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成模块
包含报告生成、摘要打印等功能
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器"""

    def __init__(self, results: Dict[str, Any], stats: Dict[str, Any], config: Any):
        """
        初始化报告生成器

        Args:
            results: 分析结果
            stats: 统计信息
            config: 配置对象
        """
        self.results = results
        self.stats = stats
        self.config = config

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        生成分析报告

        Args:
            output_file: 输出文件路径，如果为None则使用默认路径

        Returns:
            输出文件路径
        """
        try:
            # 添加工作量估算
            if 'effort_estimate' not in self.results or self.results['effort_estimate'] is None:
                try:
                    from .effort_analyzer import calculate_work_effort_estimate

                    effort_result = calculate_work_effort_estimate(self.results)

                    if effort_result and 'error' not in effort_result:
                        self.results['effort_estimate'] = effort_result
                    else:
                        error_msg = effort_result.get('error', '未知错误') if effort_result else '返回结果为空'
                        self.results['effort_estimate'] = {'error': error_msg}
                except ImportError as e:
                    logger.error(f"导入 effort_analyzer 模块失败: {e}")
                    self.results['effort_estimate'] = {'error': f'模块导入失败: {e}'}
                except Exception as e:
                    logger.error(f"计算工作量估算时发生异常: {e}")
                    self.results['effort_estimate'] = {'error': f'计算失败: {e}'}
            else:
                pass

            # 添加统计信息
            self.results['statistics'] = {
                'analysis_stats': self.stats,
                'performance_metrics': self._calculate_performance_metrics(),
                'configuration': self._get_configuration_summary()
            }

            # 添加分析摘要
            self.results['summary'] = self._generate_summary()

            # 确定输出文件路径
            if output_file is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f"analysis_report_{timestamp}.json"

            # 写入文件
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)

                logger.info(f"报告已生成: {output_file}")
                return output_file

            except Exception as e:
                logger.error(f"生成报告失败: {e}")
                raise

        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            raise

    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """计算性能指标"""
        metrics = {
            'analysis_duration': self.stats.get('analysis_duration', 0),
            'memory_usage_mb': self.stats.get('memory_usage', 0),
            'files_per_second': 0,
            'error_rate': 0
        }

        # 计算文件处理速度
        total_files = self.stats.get('files_processed', 0) + self.stats.get('files_skipped', 0)
        if total_files > 0 and metrics['analysis_duration'] > 0:
            metrics['files_per_second'] = total_files / metrics['analysis_duration']

        # 计算错误率
        if total_files > 0:
            metrics['error_rate'] = self.stats.get('errors_encountered', 0) / total_files

        return metrics

    def _get_configuration_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            'parallel_processing': self.config.parallel_processing,

            'max_file_size_mb': self.config.max_file_size / 1024 / 1024
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """生成分析摘要"""
        return {
            'total_modules': len(self.results.get('module_analysis', {})),
            'total_files': self.stats.get('files_processed', 0) + self.stats.get('files_skipped', 0),
            'successful_files': self.stats.get('files_processed', 0),
            'skipped_files': self.stats.get('files_skipped', 0),
            'error_files': self.stats.get('errors_encountered', 0),
            'analysis_timestamp': self.stats.get('start_time', datetime.now()).isoformat(),
            'analysis_duration_seconds': self.stats.get('analysis_duration', 0)
        }

    def print_summary(self):
        """打印分析摘要"""
        print("="*80)
        print("项目复杂度分析报告")
        print("="*80)

        # 项目信息
        if 'project_info' in self.results:
            project_info = self.results['project_info']
            print(f"\n项目信息:")
            print("-" * 50)
            if 'name' in project_info:
                print(f"项目名称: {project_info['name']}")
            if 'path' in project_info:
                print(f"项目路径: {project_info['path']}")
            if 'type' in project_info:
                print(f"项目类型: {project_info['type']}")

        # 模块分析结果
        if 'module_analysis' in self.results:
            module_analysis = self.results['module_analysis']
            print(f"\n模块分析结果:")
            print("-" * 50)
            for module_name, module_data in module_analysis.items():
                if 'error' in module_data:
                    print(f"• {module_name}: 分析失败 - {module_data['error']}")
                else:
                    complexity = module_data.get('complexity', {})
                    total_complexity = complexity.get('total_complexity', 0)
                    total_lines = complexity.get('total_lines', 0)
                    print(f"• {module_name}: 复杂度 {total_complexity}, 代码行数 {total_lines}")

        # 工作量估算
        if 'effort_estimate' in self.results and self.results['effort_estimate'] is not None:
            effort_estimate = self.results['effort_estimate']
            if 'error' not in effort_estimate:
                print(f"\n工作量估算:")
                print("-" * 50)
                total_effort = effort_estimate.get('total_effort', 0)
                print(f"总工作量: {total_effort:.1f} 人天")

                if 'new_module_efforts' in effort_estimate:
                    new_module_efforts = effort_estimate['new_module_efforts']
                    if 'error' not in new_module_efforts:
                        print(f"新模块开发工作量: {new_module_efforts.get('total_effort', 0):.1f} 人天")

        # 推荐和建议
        if 'recommendations' in self.results:
            recommendations = self.results['recommendations']
            if recommendations:
                print(f"\n开发建议:")
                print("-" * 50)
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. {rec}")

        # 分析统计
        if 'summary' in self.results:
            summary = self.results['summary']
            print(f"\n分析统计:")
            print("-" * 50)
            print(f"总模块数: {summary.get('total_modules', 0)}")
            print(f"总文件数: {summary.get('total_files', 0)}")
            print(f"成功分析: {summary.get('successful_files', 0)}")
            print(f"跳过文件: {summary.get('skipped_files', 0)}")
            print(f"错误文件: {summary.get('error_files', 0)}")
            print(f"分析耗时: {summary.get('analysis_duration_seconds', 0):.2f}秒")

        # 性能指标
        if 'statistics' in self.results and 'performance_metrics' in self.results['statistics']:
            perf_metrics = self.results['statistics']['performance_metrics']
            print(f"\n性能指标:")
            print("-" * 50)
            print(f"分析速度: {perf_metrics.get('files_per_second', 0):.2f} 文件/秒")
            if perf_metrics.get('memory_usage_mb', 0) > 0:
                print(f"内存使用: {perf_metrics.get('memory_usage_mb', 0):.2f} MB")
            print(f"错误率: {perf_metrics.get('error_rate', 0):.2%}")

        # 配置信息
        if 'statistics' in self.results and 'configuration' in self.results['statistics']:
            config = self.results['statistics']['configuration']
            print(f"\n分析配置:")
            print("-" * 50)
            print(f"并行处理: {'启用' if config.get('parallel_processing', {}).get('enabled', True) else '禁用'}")

            print(f"最大文件大小: {config.get('max_file_size_mb', 0):.1f} MB")

        print("="*80)


def generate_report(results: Dict[str, Any], stats: Dict[str, Any], config: Any,
                   output_file: Optional[str] = None) -> str:
    """
    生成报告的便捷函数

    Args:
        results: 分析结果
        stats: 统计信息
        config: 配置对象
        output_file: 输出文件路径

    Returns:
        输出文件路径
    """
    generator = ReportGenerator(results, stats, config)
    return generator.generate_report(output_file)


def print_summary(results: Dict[str, Any], stats: Dict[str, Any], config: Any):
    """
    打印摘要的便捷函数

    Args:
        results: 分析结果
        stats: 统计信息
        config: 配置对象
    """
    generator = ReportGenerator(results, stats, config)
    generator.print_summary()
