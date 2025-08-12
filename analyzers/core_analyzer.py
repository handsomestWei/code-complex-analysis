#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心分析器模块
包含GenericComplexityAnalyzer类的核心功能
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time

from .analyzer_config import get_config
from .language_analyzer_manager import get_analyzer_manager
from .project_detector import get_project_detector
from .module_analyzer import analyze_module, analyze_module_complexity
from .effort_analyzer import calculate_work_effort_estimate
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class GenericComplexityAnalyzer:
    """通用项目复杂度分析器"""

    def __init__(self, project_path: str):
        """
        初始化分析器

        Args:
            project_path: 项目根路径
        """
        self.project_path = Path(project_path)
        self.config = get_config()

        # 验证项目路径
        if not self.project_path.exists():
            raise FileNotFoundError(f"项目路径不存在: {project_path}")
        if not self.project_path.is_dir():
            raise NotADirectoryError(f"项目路径不是目录: {project_path}")

        logger.info(f"初始化分析器，项目路径: {self.project_path}")

        # 初始化结果存储
        self.results = self._initialize_results()

        # 技术栈分类
        self.tech_stacks = self.config.tech_stack_categories

        # 获取语言分析器管理器
        self.analyzer_manager = get_analyzer_manager()

        # 获取项目检测器
        self.project_detector = get_project_detector()

        # 动态获取支持的语言扩展名
        self.language_extensions = {}
        for language, analyzer in self.analyzer_manager.analyzers.items():
            self.language_extensions[language] = analyzer.file_extensions

        # 从配置获取忽略模式
        self.ignore_patterns = self.config.skip_patterns

        # 统计信息
        self.stats = {
            'files_processed': 0,
            'files_skipped': 0,
            'errors_encountered': 0,
            'start_time': datetime.now(),
            'analysis_duration': 0,
            'memory_usage': 0,
            'retry_attempts': 0
        }

        # 性能监控配置
        self.performance_monitoring = self.config.performance_monitoring
        self.analysis_timeout = self.config.analysis_timeout
        self.max_retry_attempts = self.config.max_retry_attempts

        # 初始化线程池用于并行处理
        if self.config.parallel_processing.get('enabled', True):
            self.executor = ThreadPoolExecutor(
                max_workers=self.config.parallel_processing['max_workers'],
                thread_name_prefix="ComplexityAnalyzer"
            )
            self.parallel_enabled = True
            logger.info(f"并行处理已启用，最大工作线程数: {self.config.parallel_processing['max_workers']}")
        else:
            self.executor = None
            self.parallel_enabled = False
            logger.info("并行处理已禁用，将使用串行处理")

    def __del__(self):
        """析构函数，确保线程池正确关闭"""
        self.cleanup()

    def cleanup(self):
        """清理资源，关闭线程池"""
        if hasattr(self, 'executor') and self.executor is not None:
            try:
                self.executor.shutdown(wait=True)
                logger.info("线程池已关闭")
            except Exception as e:
                logger.warning(f"关闭线程池时出错: {e}")
            finally:
                self.executor = None
                self.parallel_enabled = False

    def _initialize_results(self) -> Dict[str, Any]:
        """初始化结果存储结构"""
        return {
            'project_info': {},
            'module_analysis': {},
            'language_analysis': {},
            'architecture_analysis': {
                'total_sql_tables': 0
            },
            'effort_estimate': None,
            'recommendations': [],
            'analysis_timestamp': datetime.now().isoformat()
        }

    def _create_dynamic_language_metrics(self) -> Dict[str, Any]:
        """创建动态语言指标结构"""
        metrics = {
            'total_complexity': 0
        }

        # 动态添加支持的语言类型
        for language, analyzer in self.analyzer_manager.analyzers.items():
            # 为每种语言创建文件列表和统计
            file_key = f'{language}_files'
            metrics[file_key] = []

            # 为特定语言添加额外的统计字段
            if language == 'java':
                metrics['total_java_lines'] = 0
                metrics['total_java_files'] = 0
            elif language == 'sql':
                metrics['total_sql_lines'] = 0
                metrics['total_sql_tables'] = 0
            elif language in ['typescript', 'javascript', 'vue']:
                # 前端语言可以共享一些统计
                if 'total_frontend_files' not in metrics:
                    metrics['total_frontend_files'] = 0

        return metrics

    def _get_language_file_key(self, file_extension: str) -> str:
        """根据文件扩展名获取语言文件键名"""
        analyzer = self.analyzer_manager.get_analyzer_for_file(Path(f"dummy{file_extension}"))
        if analyzer:
            return f'{analyzer.language_name}_files'
        return 'unknown_files'

    def _get_language_stats_key(self, language_name: str, stat_type: str) -> str:
        """根据语言名称和统计类型获取统计键名"""
        return f'total_{language_name}_{stat_type}'

    def _update_language_stats(self, project_stats: Dict[str, Any], language_name: str,
                              file_count: int, lines: int = 0, **kwargs):
        """更新语言统计信息"""
        # 更新文件数量
        file_key = self._get_language_stats_key(language_name, 'files')
        if file_key not in project_stats:
            project_stats[file_key] = 0
        project_stats[file_key] += file_count

        # 更新代码行数
        if lines > 0:
            lines_key = self._get_language_stats_key(language_name, 'lines')
            if lines_key not in project_stats:
                project_stats[lines_key] = 0
            project_stats[lines_key] += lines

        # 更新其他统计信息
        for key, value in kwargs.items():
            if value > 0:
                stat_key = self._get_language_stats_key(language_name, key)
                if stat_key not in project_stats:
                    project_stats[stat_key] = 0
                project_stats[stat_key] += value

    def _calculate_tech_stack_diversity(self, project_stats: Dict[str, Any]) -> int:
        """计算技术栈多样性"""
        diversity_count = 0
        for key in project_stats.keys():
            if key.startswith('total_') and key.endswith('_files'):
                if project_stats[key] > 0:
                    diversity_count += 1
        return diversity_count

    def _get_language_complexity(self, analysis_result: Dict[str, Any], language_name: str) -> int:
        """获取特定语言的复杂度"""
        language_stats = analysis_result.get('language_stats', {})
        if language_name in language_stats:
            return language_stats[language_name].get('complexity', 0)
        return 0

    def _get_language_specific_stats(self, analysis_result: Dict[str, Any], language_name: str) -> Dict[str, int]:
        """获取特定语言的统计信息"""
        language_stats = analysis_result.get('language_stats', {})
        if language_name in language_stats:
            return language_stats[language_name]
        return {}

    def scan_project(self):
        """扫描整个项目"""
        print("开始扫描项目...")
        start_time = time()

        try:
            module_count = 0
            for module_path in self.project_path.iterdir():
                if module_path.is_dir():
                    module_name = module_path.name
                    print(f"分析模块: {module_name}")

                    try:
                        self.analyze_module(module_path, module_name)
                        module_count += 1
                    except Exception as e:
                        logger.error(f"分析模块失败 {module_name}: {e}")
                        self.stats['errors_encountered'] += 1
                        continue

            # 生成语言分析数据
            self._generate_language_analysis()

            self.generate_recommendations()

            analysis_duration = time() - start_time
            self.stats['analysis_duration'] = analysis_duration

            if self.performance_monitoring.get('collect_timing', True):
                logger.info(f"项目分析完成，耗时: {analysis_duration:.2f}秒")

            if self.performance_monitoring.get('collect_memory', False):
                try:
                    import psutil
                    process = psutil.Process()
                    memory_info = process.memory_info()
                    self.stats['memory_usage'] = memory_info.rss / 1024 / 1024  # MB
                    logger.info(f"内存使用: {self.stats['memory_usage']:.2f} MB")
                except ImportError:
                    logger.debug("psutil未安装，跳过内存监控")

            print(f"项目扫描完成，共分析 {module_count} 个模块")

        except Exception as e:
            logger.error(f"项目扫描失败: {e}")
            raise
        finally:
            self.cleanup()

    def _generate_language_analysis(self):
        """生成语言分析数据"""
        try:
            language_analysis = {}

            # 遍历所有模块，收集语言统计信息
            for module_name, module_data in self.results['module_analysis'].items():
                if 'error' not in module_data:
                    complexity_data = module_data.get('complexity', {})
                    language_stats = complexity_data.get('language_stats', {})

                    for language, stats in language_stats.items():
                        if language not in language_analysis:
                            language_analysis[language] = {
                                'files': 0,
                                'lines': 0,
                                'complexity': 0
                            }

                        language_analysis[language]['files'] += stats.get('files', 0)
                        language_analysis[language]['lines'] += stats.get('lines', 0)
                        language_analysis[language]['complexity'] += stats.get('complexity', 0)

            self.results['language_analysis'] = language_analysis
            logger.info(f"生成语言分析数据: {list(language_analysis.keys())}")

        except Exception as e:
            logger.error(f"生成语言分析数据失败: {e}")
            self.results['language_analysis'] = {}

    def analyze_module(self, module_path: Path, module_name: str):
        """分析单个模块"""
        try:
            # 检测模块类型
            module_type = self.project_detector.detect_module_type(module_path)

            # 分析模块（包含复杂度分析）
            module_analysis = analyze_module(module_path, self.ignore_patterns)

            # 合并结果
            module_result = {
                'name': module_name,
                'path': str(module_path),
                'type': module_type,
                'analysis': module_analysis,
                'complexity': module_analysis.get('complexity', {})
            }

            # 更新统计信息
            complexity_analysis = module_analysis.get('complexity', {})
            if 'error' not in complexity_analysis:
                self.stats['files_processed'] += complexity_analysis.get('total_files', 0)
            else:
                self.stats['errors_encountered'] += 1

            # 存储结果
            self.results['module_analysis'][module_name] = module_result

        except Exception as e:
            logger.error(f"分析模块失败 {module_name}: {e}")
            self.results['module_analysis'][module_name] = {
                'name': module_name,
                'path': str(module_path),
                'error': f"分析失败: {str(e)}"
            }
            self.stats['errors_encountered'] += 1

    def analyze_module_complexity(self, module_path: Path) -> Dict[str, Any]:
        """分析模块复杂度，根据配置选择串行或并行处理"""
        if self.parallel_enabled and self.executor:
            return self._analyze_module_complexity_parallel(module_path)
        else:
            return self._analyze_module_complexity_serial(module_path)

    def _analyze_module_complexity_parallel(self, module_path: Path) -> Dict[str, Any]:
        """并行分析模块复杂度"""
        if self.parallel_enabled and self.executor:
            return analyze_module_complexity(module_path, self.ignore_patterns)
        else:
            return analyze_module_complexity(module_path, self.ignore_patterns)

    def _analyze_module_complexity_serial(self, module_path: Path) -> Dict[str, Any]:
        """串行分析模块复杂度"""
        return analyze_module_complexity(module_path, self.ignore_patterns)

    def _create_module_error_result(self, module_path: Path, error_message: str) -> Dict[str, Any]:
        """创建模块分析错误结果"""
        return {
            'error': error_message,
            'module_path': str(module_path),
            'total_complexity': 0,
            'file_stats': {},
            'complexity_metrics': {}
        }

    def generate_recommendations(self):
        """生成开发建议"""
        try:
            # 基于分析结果生成建议
            recommendations = []

            # 复杂度建议
            total_complexity = sum(
                module_data.get('complexity', {}).get('total_complexity', 0)
                for module_data in self.results['module_analysis'].values()
                if 'error' not in module_data
            )

            if total_complexity > self.config.complexity_thresholds['HIGH']:
                recommendations.append("项目整体复杂度较高，建议进行代码重构和模块拆分")

            # 技术栈建议
            tech_diversity = self._calculate_tech_stack_diversity(self.results)
            if tech_diversity > self.config.tech_diversity_thresholds['HIGH']:
                recommendations.append("技术栈多样性较高，建议统一技术选型，减少维护成本")

            # 文件大小建议
            large_files = []
            for module_name, module_data in self.results['module_analysis'].items():
                if 'error' not in module_data:
                    complexity = module_data.get('complexity', {})
                    for file_path, file_data in complexity.get('file_complexity', {}).items():
                        if file_data.get('total_complexity', 0) > self.config.complexity_thresholds['MEDIUM']:
                            large_files.append(f"{module_name}: {file_path}")

            if large_files:
                recommendations.append(f"发现 {len(large_files)} 个复杂度较高的文件，建议进行重构")

            self.results['recommendations'] = recommendations

        except Exception as e:
            logger.error(f"生成建议失败: {e}")
            self.results['recommendations'] = ["生成建议时发生错误"]

    def generate_report(self, output_file: str = None):
        """生成分析报告"""
        try:
            # 创建报告生成器
            report_generator = ReportGenerator(self.results, self.stats, self.config)

            # 生成报告
            output_file = report_generator.generate_report(output_file)

            # 打印摘要
            report_generator.print_summary()

            return output_file

        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            raise
