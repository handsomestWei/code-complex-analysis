#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析器配置文件
支持动态配置和扩展
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnalyzerConfig:
    """分析器配置类"""

    # 基础配置
    enabled_analyzers: List[str] = field(default_factory=lambda: [
        'java', 'typescript', 'javascript', 'python', 'sql', 'vue'
    ])

    # 文件大小限制
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # 跳过的文件模式
    skip_patterns: List[str] = field(default_factory=lambda: [
        '*.log', '*.tmp', '*.cache', '*.min.js', '*.min.css',
        'node_modules', '.git', '.svn', '.hg', '__pycache__',
        'target', 'build', 'dist', 'out', 'bin', 'obj'
    ])

    # 并行处理配置
    parallel_processing: Dict[str, Any] = field(default_factory=lambda: {
        'max_workers': 4,
        'chunk_size': 100,
        'enabled': True
    })



    # 输出配置
    output: Dict[str, Any] = field(default_factory=lambda: {
        'format': 'json',  # json, xml, html, markdown
        'include_details': True,
        'include_statistics': True
    })

    # 自定义分析器配置
    custom_analyzers: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # 复杂度阈值配置
    complexity_thresholds: Dict[str, int] = field(default_factory=lambda: {
        'LOW': 100,
        'MEDIUM': 500,
        'HIGH': 1000,
        'VERY_HIGH': 2000
    })

    # 代码行数阈值
    line_thresholds: Dict[str, int] = field(default_factory=lambda: {
        'MICRO': 1000,
        'SMALL': 5000,
        'MEDIUM': 20000,
        'LARGE': 50000,
        'VERY_LARGE': 100000
    })

    # 文件数量阈值
    file_thresholds: Dict[str, int] = field(default_factory=lambda: {
        'FEW': 20,
        'SOME': 50,
        'MANY': 100,
        'LOTS': 200,
        'MANY_LOTS': 500
    })

    # 数据库表数量阈值
    table_thresholds: Dict[str, int] = field(default_factory=lambda: {
        'SIMPLE': 5,
        'BASIC': 10,
        'MEDIUM': 20,
        'COMPLEX': 50,
        'VERY_COMPLEX': 100
    })

    # 模块数量阈值
    module_thresholds: Dict[str, int] = field(default_factory=lambda: {
        'SINGLE': 1,
        'FEW': 2,
        'SOME': 5,
        'MANY': 10,
        'LOTS': 15
    })

    # 技术栈多样性阈值
    tech_diversity_thresholds: Dict[str, int] = field(default_factory=lambda: {
        'LOW': 2,
        'MEDIUM': 3,
        'HIGH': 4,
        'VERY_HIGH': 5
    })

    # 工作量估算基础值（人天）
    effort_base_values: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        'SMALL_MODULE': {
            'BACKEND': 2.0,
            'FRONTEND': 1.5
        },
        'MEDIUM_MODULE': {
            'BACKEND': 6.0,
            'FRONTEND': 4.5
        },
        'LARGE_MODULE': {
            'BACKEND': 12.0,
            'FRONTEND': 9.0
        }
    })

    # 复杂度因子上限
    factor_limits: Dict[str, float] = field(default_factory=lambda: {
        'COMPLEXITY': 4.0,
        'UNDERSTANDING': 3.0,
        'INTEGRATION': 2.5
    })

    # 技术栈分类
    tech_stack_categories: Dict[str, List[str]] = field(default_factory=lambda: {
        'backend': ['java', 'xml', 'properties', 'sql', 'sh', 'python'],
        'frontend': ['typescript', 'javascript', 'vue', 'scss', 'css', 'html'],
        'mobile': ['vue', 'javascript', 'json'],
        'config': ['yaml', 'json', 'xml', 'properties'],
        'docs': ['markdown', 'html']
    })

    # 语言生产力比率
    language_productivity_rates: Dict[str, int] = field(default_factory=lambda: {
        'java': 100,
        'python': 120,
        'sql': 50,
        'typescript': 80,
        'javascript': 80,
        'vue': 60
    })

    # 日志配置
    logging_level: str = 'INFO'
    logging_format: str = '%(asctime)s - %(levelname)s - %(message)s'
    logging_file: Optional[str] = None

    # 分析超时和重试配置
    analysis_timeout: int = 300  # 5分钟
    max_retry_attempts: int = 3

    # 性能监控配置
    performance_monitoring: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'collect_timing': True,
        'collect_memory': False
    })

    # 报告生成配置
    report_generation: Dict[str, Any] = field(default_factory=lambda: {
        'include_charts': True,
        'include_recommendations': True,
        'include_risk_analysis': True,
        'chart_theme': 'default'
    })

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalyzerConfig':
        """从字典创建配置"""
        return cls(**data)

    @classmethod
    def from_file(cls, config_file: str) -> 'AnalyzerConfig':
        """从配置文件加载"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                # 根据文件扩展名选择解析方式
                if config_file.lower().endswith('.yaml') or config_file.lower().endswith('.yml'):
                    try:
                        import yaml
                        data = yaml.safe_load(f)
                    except ImportError:
                        logger.warning("PyYAML未安装，尝试使用JSON格式")
                        data = json.load(f)
                else:
                    data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            logger.warning(f"加载配置文件失败: {e}，使用默认配置")
            return cls()

    def save_to_file(self, config_file: str):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                # 根据文件扩展名选择保存格式
                if config_file.lower().endswith('.yaml') or config_file.lower().endswith('.yml'):
                    try:
                        import yaml
                        yaml.dump(self.to_dict(), f, default_flow_style=False,
                                 allow_unicode=True, sort_keys=False)
                    except ImportError:
                        logger.warning("PyYAML未安装，使用JSON格式保存")
                        json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
                else:
                    json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"配置已保存到: {config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str = None):
        """
        初始化配置管理器

        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), '..', 'config')

        # 优先使用YAML配置文件，如果没有则使用JSON
        yaml_config = os.path.join(self.config_dir, 'analyzer_config.yaml')
        json_config = os.path.join(self.config_dir, 'analyzer_config.json')

        if os.path.exists(yaml_config):
            self.config_file = yaml_config
        else:
            self.config_file = json_config

        self._config = None

    def _load_config(self) -> AnalyzerConfig:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                return AnalyzerConfig.from_file(self.config_file)
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}，使用默认配置")
                return AnalyzerConfig()
        else:
            # 创建默认配置文件
            default_config = AnalyzerConfig()
            self._save_default_config(default_config)
            return default_config

    def _save_default_config(self, config: AnalyzerConfig):
        """保存默认配置"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            config.save_to_file(self.config_file)
            logger.info(f"默认配置文件已创建: {self.config_file}")
        except Exception as e:
            logger.error(f"创建默认配置文件失败: {e}")

    def get_config(self) -> AnalyzerConfig:
        """获取配置"""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def update_config(self, updates: Dict[str, Any]):
        """更新配置"""
        config = self.get_config()

        # 递归更新嵌套字典
        def update_nested_dict(target: dict, source: dict):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    update_nested_dict(target[key], value)
                else:
                    target[key] = value

        update_nested_dict(config.__dict__, updates)

        # 保存到文件
        config.save_to_file(self.config_file)
        logger.info("配置已更新")

    def reset_to_default(self):
        """重置为默认配置"""
        self._config = AnalyzerConfig()
        self._save_default_config(self._config)
        logger.info("配置已重置为默认值")

    def add_custom_analyzer(self, name: str, config: Dict[str, Any]):
        """添加自定义分析器配置"""
        analyzer_config = self.get_config()
        analyzer_config.custom_analyzers[name] = config
        self.update_config({'custom_analyzers': analyzer_config.custom_analyzers})

    def remove_custom_analyzer(self, name: str):
        """移除自定义分析器配置"""
        analyzer_config = self.get_config()
        if name in analyzer_config.custom_analyzers:
            del analyzer_config.custom_analyzers[name]
            self.update_config({'custom_analyzers': analyzer_config.custom_analyzers})

    def get_analyzer_config(self, analyzer_name: str) -> Optional[Dict[str, Any]]:
        """获取特定分析器的配置"""
        analyzer_config = self.get_config()
        return analyzer_config.custom_analyzers.get(analyzer_name)


# 全局配置管理器实例
_config_manager = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AnalyzerConfig:
    """获取配置"""
    return get_config_manager().get_config()


def update_config(updates: Dict[str, Any]):
    """更新配置"""
    get_config_manager().update_config(updates)
