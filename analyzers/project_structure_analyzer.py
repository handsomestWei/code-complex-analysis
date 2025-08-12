#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目结构分析模块
包含Maven项目、Package.json、Vue项目结构等分析功能
"""

import json
from pathlib import Path
from typing import Dict, Any, List


def analyze_maven_project(module_path: Path) -> Dict[str, Any]:
    """分析Maven项目结构"""
    result = {
        'type': 'Java/Maven项目',
        'build_tool': 'Maven',
        'dependencies': [],
        'plugins': [],
        'properties': {}
    }

    pom_path = module_path / 'pom.xml'
    if pom_path.exists():
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(pom_path)
            root = tree.getroot()

            # 提取依赖信息
            dependencies = root.findall('.//{http://maven.apache.org/POM/4.0.0}dependency')
            for dep in dependencies:
                group_id = dep.find('{http://maven.apache.org/POM/4.0.0}groupId')
                artifact_id = dep.find('{http://maven.apache.org/POM/4.0.0}artifactId')
                version = dep.find('{http://maven.apache.org/POM/4.0.0}version')

                if group_id is not None and artifact_id is not None:
                    dep_info = {
                        'group_id': group_id.text,
                        'artifact_id': artifact_id.text,
                        'version': version.text if version is not None else 'N/A'
                    }
                    result['dependencies'].append(dep_info)

            # 提取插件信息
            plugins = root.findall('.//{http://maven.apache.org/POM/4.0.0}plugin')
            for plugin in plugins:
                group_id = plugin.find('{http://maven.apache.org/POM/4.0.0}groupId')
                artifact_id = plugin.find('{http://maven.apache.org/POM/4.0.0}artifactId')
                version = plugin.find('{http://maven.apache.org/POM/4.0.0}version')

                if group_id is not None and artifact_id is not None:
                    plugin_info = {
                        'group_id': group_id.text,
                        'artifact_id': artifact_id.text,
                        'version': version.text if version is not None else 'N/A'
                    }
                    result['plugins'].append(plugin_info)

            # 提取属性信息
            properties = root.find('.//{http://maven.apache.org/POM/4.0.0}properties')
            if properties is not None:
                for prop in properties:
                    if prop.tag.endswith('}java.version'):
                        result['properties']['java_version'] = prop.text
                    elif prop.tag.endswith('}maven.compiler.source'):
                        result['properties']['maven_compiler_source'] = prop.text
                    elif prop.tag.endswith('}maven.compiler.target'):
                        result['properties']['maven_compiler_target'] = prop.text

        except Exception as e:
            result['error'] = f"解析POM文件失败: {str(e)}"

    return result


def analyze_package_json(module_path: Path) -> Dict[str, Any]:
    """分析Package.json文件"""
    result = {
        'type': 'Node.js项目',
        'dependencies': {},
        'dev_dependencies': {},
        'scripts': {},
        'engines': {},
        'metadata': {}
    }

    package_path = module_path / 'package.json'
    if package_path.exists():
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)

            # 基本信息
            result['metadata'] = {
                'name': package_data.get('name', 'N/A'),
                'version': package_data.get('version', 'N/A'),
                'description': package_data.get('description', 'N/A'),
                'main': package_data.get('main', 'N/A'),
                'author': package_data.get('author', 'N/A')
            }

            # 依赖信息
            result['dependencies'] = package_data.get('dependencies', {})
            result['dev_dependencies'] = package_data.get('devDependencies', {})
            result['scripts'] = package_data.get('scripts', {})
            result['engines'] = package_data.get('engines', {})

            # 判断项目类型
            dependencies = result['dependencies']
            dev_dependencies = result['dev_dependencies']

            if 'vue' in dependencies or 'vue' in dev_dependencies:
                result['type'] = 'Vue前端项目'
            elif 'react' in dependencies or 'react' in dev_dependencies:
                result['type'] = 'React前端项目'
            elif 'angular' in dependencies or 'angular' in dev_dependencies:
                result['type'] = 'Angular前端项目'
            elif 'express' in dependencies or 'koa' in dependencies:
                result['type'] = 'Node.js后端项目'
            else:
                result['type'] = 'Node.js项目'

        except Exception as e:
            result['error'] = f"解析Package.json失败: {str(e)}"

    return result


def analyze_vue_project_structure(module_path: Path) -> Dict[str, Any]:
    """分析Vue项目结构"""
    result = {
        'type': 'Vue前端项目',
        'structure': {},
        'config_files': [],
        'build_tools': []
    }

    # 检查配置文件
    config_files = [
        'vue.config.js', 'vite.config.js', 'webpack.config.js',
        'nuxt.config.js', 'quasar.config.js'
    ]

    for config_file in config_files:
        if (module_path / config_file).exists():
            result['config_files'].append(config_file)

    # 检查构建工具
    if (module_path / 'package.json').exists():
        try:
            with open(module_path / 'package.json', 'r', encoding='utf-8') as f:
                package_data = json.load(f)

            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})

            if 'vite' in dev_dependencies:
                result['build_tools'].append('Vite')
            if 'webpack' in dev_dependencies:
                result['build_tools'].append('Webpack')
            if 'nuxt' in dependencies:
                result['build_tools'].append('Nuxt.js')
            if 'quasar' in dependencies:
                result['build_tools'].append('Quasar')

        except Exception as e:
            result['error'] = f"解析Package.json失败: {str(e)}"

    # 检查目录结构
    common_dirs = ['src', 'public', 'components', 'views', 'router', 'store', 'assets']
    for dir_name in common_dirs:
        dir_path = module_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            result['structure'][dir_name] = {
                'exists': True,
                'file_count': len(list(dir_path.rglob('*'))),
                'sub_dirs': [d.name for d in dir_path.iterdir() if d.is_dir()]
            }
        else:
            result['structure'][dir_name] = {'exists': False}

    return result
