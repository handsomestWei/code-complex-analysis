#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语言分析器管理器
支持动态加载和注册语言分析器插件
"""

import os
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Type
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class LanguageAnalyzer(ABC):
    """语言分析器基类"""

    @property
    @abstractmethod
    def language_name(self) -> str:
        """语言名称"""
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> List[str]:
        """支持的文件扩展名列表"""
        pass

    @property
    @abstractmethod
    def analyzer_name(self) -> str:
        """分析器名称"""
        pass

    @abstractmethod
    def can_analyze(self, file_path: Path) -> bool:
        """判断是否可以分析指定文件"""
        pass

    @abstractmethod
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """分析文件复杂度"""
        pass


class LanguageAnalyzerManager:
    """语言分析器管理器"""

    def __init__(self, analyzers_dir: str = None):
        """
        初始化分析器管理器

        Args:
            analyzers_dir: 分析器目录路径，默认为当前目录下的language_analyzers
        """
        if analyzers_dir is None:
            # 默认使用当前文件所在目录的language_analyzers子目录
            current_dir = Path(__file__).parent
            analyzers_dir = current_dir / "language_analyzers"

        self.analyzers_dir = Path(analyzers_dir)
        self.analyzers: Dict[str, LanguageAnalyzer] = {}
        self.extension_map: Dict[str, LanguageAnalyzer] = {}
        self._load_analyzers()

    def _load_analyzers(self):
        """加载所有可用的语言分析器"""
        if not self.analyzers_dir.exists():
            logger.warning(f"分析器目录不存在: {self.analyzers_dir}")
            return

        # 获取启用的分析器列表
        enabled_analyzers = []
        try:
            from .analyzer_config import get_config
            config = get_config()
            enabled_analyzers = config.enabled_analyzers
            logger.info(f"从配置读取启用的分析器: {enabled_analyzers}")
        except ImportError:
            logger.warning("无法读取配置，将加载所有可用的分析器")
            enabled_analyzers = []

        # 遍历目录中的所有Python文件
        for py_file in self.analyzers_dir.glob("*.py"):
            if py_file.name.startswith("__") or py_file.name == "language_analyzer_manager.py":
                continue

            try:
                # 动态导入模块 - 修复导入路径
                if self.analyzers_dir.is_relative_to(Path(__file__).parent):
                    # 如果分析器目录是当前文件的子目录，使用相对导入
                    module_name = f".language_analyzers.{py_file.stem}"
                else:
                    # 否则使用绝对导入
                    module_name = f"analyzers.language_analyzers.{py_file.stem}"

                try:
                    module = importlib.import_module(module_name, package="analyzers")
                except ImportError:
                    # 如果相对导入失败，尝试绝对导入
                    try:
                        module = importlib.import_module(f"analyzers.language_analyzers.{py_file.stem}")
                    except ImportError:
                        continue

                # 查找模块中的分析器类
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and
                        issubclass(obj, LanguageAnalyzer) and
                        obj != LanguageAnalyzer):

                        try:
                            # 实例化分析器
                            analyzer = obj()

                            # 检查是否在启用的分析器列表中
                            if enabled_analyzers and analyzer.language_name not in enabled_analyzers:
                                logger.info(f"跳过禁用的分析器: {analyzer.analyzer_name} ({analyzer.language_name})")
                                continue

                            self._register_analyzer(analyzer)
                            logger.info(f"成功加载分析器: {analyzer.analyzer_name}")
                        except Exception as e:
                            logger.error(f"实例化分析器失败 {name}: {e}")

            except Exception as e:
                logger.error(f"加载分析器模块失败 {py_file.name}: {e}")

    def _register_analyzer(self, analyzer: LanguageAnalyzer):
        """注册分析器"""
        if analyzer.language_name in self.analyzers:
            logger.warning(f"分析器已存在，将被覆盖: {analyzer.language_name}")

        self.analyzers[analyzer.language_name] = analyzer

        # 注册文件扩展名映射
        for ext in analyzer.file_extensions:
            if ext in self.extension_map:
                logger.warning(f"文件扩展名 {ext} 已被 {self.extension_map[ext].language_name} 注册，将被 {analyzer.language_name} 覆盖")
            self.extension_map[ext] = analyzer

    def get_analyzer_for_file(self, file_path: Path) -> Optional[LanguageAnalyzer]:
        """根据文件路径获取对应的分析器"""
        file_extension = file_path.suffix.lower()
        return self.extension_map.get(file_extension)

    def get_analyzer_by_language(self, language_name: str) -> Optional[LanguageAnalyzer]:
        """根据语言名称获取分析器"""
        return self.analyzers.get(language_name)

    def get_supported_extensions(self) -> List[str]:
        """获取所有支持的文件扩展名"""
        return list(self.extension_map.keys())

    def get_supported_languages(self) -> List[str]:
        """获取所有支持的语言"""
        return list(self.analyzers.keys())

    def get_available_analyzers(self) -> Dict[str, Any]:
        """获取所有可用的分析器信息"""
        return self.analyzers

    def get_file_type_info(self, file_extension: str) -> Optional[Dict[str, Any]]:
        """根据文件扩展名获取文件类型信息"""
        if not file_extension:
            return None

        # 查找对应的分析器
        for analyzer_name, analyzer in self.analyzers.items():
            if hasattr(analyzer, 'file_extensions'):
                if file_extension.lower() in analyzer.file_extensions:
                    return {
                        'category': analyzer_name,
                        'analyzer': analyzer_name,
                        'supported_extensions': analyzer.file_extensions
                    }

        return None

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析文件，自动选择对应的分析器"""
        analyzer = self.get_analyzer_for_file(file_path)

        if analyzer is None:
            return {
                'error': f"不支持的文件类型: {file_path.suffix}",
                'file_path': str(file_path),
                'lines': 0,
                'complexity': 0,
                'file_type': 'unsupported'
            }

        try:
            if not analyzer.can_analyze(file_path):
                return {
                    'error': f"分析器无法处理此文件: {file_path}",
                    'file_path': str(file_path),
                    'lines': 0,
                    'complexity': 0,
                    'file_type': 'unprocessable'
                }

            return analyzer.analyze(file_path)

        except Exception as e:
            logger.error(f"分析文件失败 {file_path}: {e}")
            return {
                'error': f"分析失败: {str(e)}",
                'file_path': str(file_path),
                'lines': 0,
                'complexity': 0,
                'file_type': 'error'
            }

    def reload_analyzers(self):
        """重新加载所有分析器"""
        self.analyzers.clear()
        self.extension_map.clear()
        self._load_analyzers()
        logger.info("分析器已重新加载")

    def add_analyzer(self, analyzer: LanguageAnalyzer):
        """手动添加分析器"""
        self._register_analyzer(analyzer)
        logger.info(f"手动添加分析器: {analyzer.analyzer_name}")

    def remove_analyzer(self, language_name: str):
        """移除分析器"""
        if language_name in self.analyzers:
            analyzer = self.analyzers[language_name]
            # 从扩展名映射中移除
            for ext in list(self.extension_map.keys()):
                if self.extension_map[ext] == analyzer:
                    del self.extension_map[ext]

            del self.analyzers[language_name]
            logger.info(f"已移除分析器: {language_name}")
        else:
            logger.warning(f"分析器不存在: {language_name}")


# 全局分析器管理器实例
_analyzer_manager: Optional[LanguageAnalyzerManager] = None


def get_analyzer_manager() -> LanguageAnalyzerManager:
    """获取全局分析器管理器实例"""
    global _analyzer_manager
    if _analyzer_manager is None:
        _analyzer_manager = LanguageAnalyzerManager()
    return _analyzer_manager


def register_analyzer(analyzer: LanguageAnalyzer):
    """注册分析器到全局管理器"""
    manager = get_analyzer_manager()
    manager.add_analyzer(analyzer)


def analyze_file(file_path: Path) -> Dict[str, Any]:
    """使用全局管理器分析文件"""
    manager = get_analyzer_manager()
    return manager.analyze_file(file_path)
