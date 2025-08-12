#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目类型检测模块
包含各种项目类型的检测逻辑
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ProjectDetector:
    """项目类型检测器"""

    def __init__(self):
        """初始化项目检测器"""
        pass

    def detect_module_type(self, module_path: Path) -> str:
        """
        检测模块类型

        Args:
            module_path: 模块路径

        Returns:
            项目类型字符串
        """
        if not module_path.exists() or not module_path.is_dir():
            return '未知项目'

        # 检查Java/Maven项目
        if (module_path / 'pom.xml').exists():
            logger.debug(f"检测到Maven项目: {module_path}")
            return 'Java/Maven项目'

        # 检查Java/Gradle项目
        if (module_path / 'build.gradle').exists():
            logger.debug(f"检测到Gradle项目: {module_path}")
            return 'Java/Gradle项目'

        # 检查Node.js项目
        if (module_path / 'package.json').exists():
            return self._detect_nodejs_project_type(module_path)

        # 检查Python项目
        if (module_path / 'requirements.txt').exists() or (module_path / 'setup.py').exists():
            logger.debug(f"检测到Python项目: {module_path}")
            return 'Python项目'

        # 检查Rust项目
        if (module_path / 'Cargo.toml').exists():
            logger.debug(f"检测到Rust项目: {module_path}")
            return 'Rust项目'

        # 检查Go项目
        if (module_path / 'go.mod').exists():
            logger.debug(f"检测到Go项目: {module_path}")
            return 'Go项目'

        # 检查Ruby项目
        if (module_path / 'Gemfile').exists():
            logger.debug(f"检测到Ruby项目: {module_path}")
            return 'Ruby项目'

        # 检查PHP项目
        if (module_path / 'composer.json').exists():
            logger.debug(f"检测到PHP项目: {module_path}")
            return 'PHP项目'

        # 检查Docker项目
        if (module_path / 'Dockerfile').exists() or (module_path / 'docker-compose.yml').exists():
            logger.debug(f"检测到Docker项目: {module_path}")
            return 'Docker项目'

        # 检查.NET项目
        if (module_path / '*.csproj').exists() or (module_path / '*.vbproj').exists():
            logger.debug(f"检测到.NET项目: {module_path}")
            return '.NET项目'

        # 检查Scala项目
        if (module_path / 'build.sbt').exists():
            logger.debug(f"检测到Scala项目: {module_path}")
            return 'Scala项目'

        # 检查Kotlin项目
        if (module_path / 'build.gradle.kts').exists():
            logger.debug(f"检测到Kotlin项目: {module_path}")
            return 'Kotlin项目'

        # 检查配置文件项目
        if self._is_config_project(module_path):
            logger.debug(f"检测到配置项目: {module_path}")
            return '配置项目'

        # 检查文档项目
        if self._is_documentation_project(module_path):
            logger.debug(f"检测到文档项目: {module_path}")
            return '文档项目'

        # 检查数据项目
        if self._is_data_project(module_path):
            logger.debug(f"检测到数据项目: {module_path}")
            return '数据项目'

        # 检查测试项目
        if self._is_test_project(module_path):
            logger.debug(f"检测到测试项目: {module_path}")
            return '测试项目'

        # 检查构建脚本项目
        if self._is_build_script_project(module_path):
            logger.debug(f"检测到构建脚本项目: {module_path}")
            return '构建脚本项目'

        # 检查Vue项目
        if self.is_vue_project(module_path):
            logger.debug(f"检测到Vue项目: {module_path}")
            return 'Vue项目'

        # 检查是否有源代码文件
        if self._has_source_code(module_path):
            logger.debug(f"检测到源代码项目: {module_path}")
            return '源代码项目'

        return '未知项目'

    def _detect_nodejs_project_type(self, module_path: Path) -> str:
        """检测Node.js项目类型"""
        package_path = module_path / 'package.json'
        if not package_path.exists():
            return 'Node.js项目'

        try:
            import json
            with open(package_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)

            # 检查Vue项目
            if self.is_vue_project(module_path):
                return 'Vue项目'

            # 检查React项目
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})

            if 'react' in dependencies or 'react' in dev_dependencies:
                return 'React项目'

            # 检查Angular项目
            if 'angular' in dependencies or 'angular' in dev_dependencies:
                return 'Angular项目'

            # 检查Express项目
            if 'express' in dependencies:
                return 'Express项目'

            # 检查Next.js项目
            if 'next' in dependencies or 'next' in dev_dependencies:
                return 'Next.js项目'

            # 检查Nuxt.js项目
            if 'nuxt' in dependencies or 'nuxt' in dev_dependencies:
                return 'Nuxt.js项目'

            return 'Node.js项目'

        except Exception as e:
            logger.warning(f"解析package.json失败: {e}")
            return 'Node.js项目'

    def _is_config_project(self, module_path: Path) -> bool:
        """检查是否为配置项目"""
        config_files = ['config', 'conf', 'settings', 'env', '.env']

        # 动态获取配置相关的文件扩展名
        config_extensions = self._get_config_extensions()

        # 检查配置目录
        for config_dir in config_files:
            if (module_path / config_dir).exists():
                return True

        # 检查配置文件
        for file in module_path.iterdir():
            if file.is_file():
                if file.name in config_files or file.suffix in config_extensions:
                    return True

        return False

    def _is_documentation_project(self, module_path: Path) -> bool:
        """检查是否为文档项目"""
        doc_files = ['docs', 'documentation', 'readme', 'README', 'guide', 'manual']

        # 动态获取文档相关的文件扩展名
        doc_extensions = self._get_documentation_extensions()

        # 检查文档目录
        for doc_dir in doc_files:
            if (module_path / doc_dir).exists():
                return True

        # 检查文档文件
        for file in module_path.iterdir():
            if file.is_file():
                if file.name.lower() in [f.lower() for f in doc_files] or file.suffix in doc_extensions:
                    return True

        return False

    def _is_data_project(self, module_path: Path) -> bool:
        """检查是否为数据项目"""
        data_files = ['data', 'dataset', 'raw', 'processed', 'input', 'output']

        # 动态获取数据相关的文件扩展名
        data_extensions = self._get_data_extensions()

        # 检查数据目录
        for data_dir in data_files:
            if (module_path / data_dir).exists():
                return True

        # 检查数据文件
        for file in module_path.iterdir():
            if file.is_file():
                if file.name.lower() in [f.lower() for f in data_files] or file.suffix in data_extensions:
                    return True

        return False

    def _is_test_project(self, module_path: Path) -> bool:
        """检查是否为测试项目"""
        test_files = ['test', 'tests', 'spec', 'specs', 'e2e', 'integration']

        # 动态获取测试相关的文件扩展名
        test_extensions = self._get_test_extensions()

        # 检查测试目录
        for test_dir in test_files:
            if (module_path / test_dir).exists():
                return True

        # 检查测试文件
        for file in module_path.iterdir():
            if file.is_file():
                if file.name.lower() in [f.lower() for f in test_files] or file.suffix in test_extensions:
                    return True

        return False

    def _is_build_script_project(self, module_path: Path) -> bool:
        """检查是否为构建脚本项目"""
        build_files = ['build', 'scripts', 'tools', 'ci', 'cd']

        # 动态获取构建相关的文件扩展名
        build_extensions = self._get_build_extensions()

        # 检查构建目录
        for build_dir in build_files:
            if (module_path / build_dir).exists():
                return True

        # 检查构建文件
        for file in module_path.iterdir():
            if file.is_file():
                if file.name.lower() in [f.lower() for f in build_files] or file.suffix in build_extensions:
                    return True

        return False

    def is_vue_project(self, module_path: Path) -> bool:
        """检查是否为Vue项目"""
        # 检查Vue相关文件
        vue_files = ['vue.config.js', 'vite.config.js', 'nuxt.config.js']
        for vue_file in vue_files:
            if (module_path / vue_file).exists():
                return True

        # 检查package.json中的Vue依赖
        package_path = module_path / 'package.json'
        if package_path.exists():
            try:
                import json
                with open(package_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)

                dependencies = package_data.get('dependencies', {})
                dev_dependencies = package_data.get('devDependencies', {})

                if 'vue' in dependencies or 'vue' in dev_dependencies:
                    return True

            except Exception:
                pass

        return False

    def _has_source_code(self, module_path: Path) -> bool:
        """检查是否包含源代码文件"""
        # 动态获取源代码相关的文件扩展名
        source_extensions = self._get_source_extensions()

        for file in module_path.rglob('*'):
            if file.is_file() and file.suffix in source_extensions:
                return True

        return False

    def _get_config_extensions(self) -> List[str]:
        """动态获取配置相关的文件扩展名"""
        try:
            if hasattr(self, 'language_manager') and self.language_manager:
                extensions = []
                analyzers = self.language_manager.get_available_analyzers()
                config_languages = ['json', 'yaml', 'xml', 'properties']
                for lang in config_languages:
                    if lang in analyzers:
                        analyzer_info = analyzers[lang]
                        if hasattr(analyzer_info, 'file_extensions'):
                            extensions.extend(analyzer_info.file_extensions)
                return extensions
        except Exception:
            pass

        # 后备方案
        return ['.yaml', '.yml', '.json', '.xml', '.properties', '.ini', '.toml']

    def _get_documentation_extensions(self) -> List[str]:
        """动态获取文档相关的文件扩展名"""
        try:
            if hasattr(self, 'language_manager') and self.language_manager:
                extensions = []
                analyzers = self.language_manager.get_available_analyzers()
                doc_languages = ['markdown', 'rst']
                for lang in doc_languages:
                    if lang in analyzers:
                        analyzer_info = analyzers[lang]
                        if hasattr(analyzer_info, 'file_extensions'):
                            extensions.extend(analyzer_info.file_extensions)
                return extensions
        except Exception:
            pass

        # 后备方案
        return ['.md', '.rst', '.txt', '.html', '.pdf']

    def _get_data_extensions(self) -> List[str]:
        """动态获取数据相关的文件扩展名"""
        try:
            if hasattr(self, 'language_manager') and self.language_manager:
                extensions = []
                analyzers = self.language_manager.get_available_analyzers()
                data_languages = ['csv', 'json', 'xml', 'yaml', 'sql']
                for lang in data_languages:
                    if lang in analyzers:
                        analyzer_info = analyzers[lang]
                        if hasattr(analyzer_info, 'file_extensions'):
                            extensions.extend(analyzer_info.file_extensions)
                return extensions
        except Exception:
            pass

        # 后备方案
        return ['.csv', '.json', '.xml', '.yaml', '.yml', '.sql', '.db', '.sqlite']

    def _get_test_extensions(self) -> List[str]:
        """动态获取测试相关的文件扩展名"""
        try:
            if hasattr(self, 'language_manager') and self.language_manager:
                extensions = []
                analyzers = self.language_manager.get_available_analyzers()
                test_languages = ['javascript', 'typescript', 'python']
                for lang in test_languages:
                    if lang in analyzers:
                        analyzer_info = analyzers[lang]
                        if hasattr(analyzer_info, 'file_extensions'):
                            # 添加测试文件后缀
                            for ext in analyzer_info.file_extensions:
                                base_ext = ext.replace('.', '')
                                extensions.extend([f'.test.{base_ext}', f'.spec.{base_ext}'])
                return extensions
        except Exception:
            pass

        # 后备方案
        return ['.test.js', '.spec.js', '.test.ts', '.spec.ts', '.test.py', '.spec.py']

    def _get_build_extensions(self) -> List[str]:
        """动态获取构建相关的文件扩展名"""
        try:
            if hasattr(self, 'language_manager') and self.language_manager:
                extensions = []
                analyzers = self.language_manager.get_available_analyzers()
                build_languages = ['shell', 'python', 'javascript', 'typescript']
                for lang in build_languages:
                    if lang in analyzers:
                        analyzer_info = analyzers[lang]
                        if hasattr(analyzer_info, 'file_extensions'):
                            extensions.extend(analyzer_info.file_extensions)
                return extensions
        except Exception:
            pass

        # 后备方案
        return ['.sh', '.bat', '.ps1', '.py', '.js', '.ts']

    def _get_source_extensions(self) -> List[str]:
        """动态获取源代码相关的文件扩展名"""
        try:
            if hasattr(self, 'language_manager') and self.language_manager:
                extensions = []
                analyzers = self.language_manager.get_available_analyzers()
                for analyzer_name, analyzer_info in analyzers.items():
                    if hasattr(analyzer_info, 'file_extensions'):
                        extensions.extend(analyzer_info.file_extensions)
                return extensions
        except Exception:
            pass

        # 后备方案
        return ['.java', '.py', '.js', '.ts', '.vue', '.cpp', '.c', '.h', '.cs', '.go', '.rs']


# 全局项目检测器实例
_project_detector = ProjectDetector()


def get_project_detector() -> ProjectDetector:
    """获取全局项目检测器实例"""
    return _project_detector


def detect_module_type(module_path: Path) -> str:
    """检测模块类型的便捷函数"""
    return get_project_detector().detect_module_type(module_path)
