#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目结构详情模块
包含各种项目类型的详情生成功能
"""

class ModuleStructureGenerator:
    def __init__(self, data, language_manager=None, config=None):
        self.data = data
        self.language_manager = language_manager
        self.config = config

    def generate_project_structure_details(self, analysis: dict) -> str:
        """生成项目结构详情HTML"""
        # 根据正确的JSON层级结构获取项目结构分析数据
        # 层级：module_analysis -> backend -> analysis -> project_structure
        analysis_data = analysis.get('analysis', {})
        project_structure = analysis_data.get('project_structure', {}) if analysis_data else {}

        if not project_structure or 'type' not in project_structure:
            return ""

        details_html = '<div class="detail-card">'
        details_html += '<h4>项目结构详情</h4>'

        # 根据项目结构类型显示详细信息
        if project_structure['type'] == 'Java/Maven项目':
            details_html += self._generate_maven_details(project_structure)
        elif 'Node.js' in project_structure['type']:
            details_html += self._generate_nodejs_details(project_structure)
        elif 'Vue' in project_structure['type']:
            details_html += self._generate_vue_details(project_structure)
        else:
            details_html += self._generate_generic_details(analysis)

        details_html += '</div>'
        return details_html

    def _generate_maven_details(self, project_structure: dict) -> str:
        """生成Maven项目详情HTML"""
        html = f'''
                        <div class="detail-card">
                            <h4>Maven项目详情</h4>
                            <ul class="detail-list">
                                <li><span class="detail-label">项目类型</span><span class="detail-value">{project_structure.get('type', 'N/A')}</span></li>
                                <li><span class="detail-label">构建工具</span><span class="detail-value">{project_structure.get('build_tool', 'N/A')}</span></li>
                                <li><span class="detail-label">依赖数量</span><span class="detail-value">{len(project_structure.get('dependencies', []))}</span></li>
                                <li><span class="detail-label">插件数量</span><span class="detail-value">{len(project_structure.get('plugins', []))}</span></li>
                            </ul>
                        </div>
        '''

        # 显示所有依赖信息
        if project_structure.get('dependencies'):
            html += '''
                        <div class="detail-card">
                            <h4>依赖列表</h4>
            '''
            for dep in project_structure.get('dependencies', []):
                html += f'''
                            <div class="dependency-item">
                                <strong>{dep.get('artifact_id', 'N/A')}</strong>
                                <br><small>Group: {dep.get('group_id', 'N/A')} | Version: {dep.get('version', 'N/A')}</small>
                            </div>
                '''
            html += '</div>'

        # 显示所有插件信息
        if project_structure.get('plugins'):
            html += '''
                        <div class="detail-card">
                            <h4>插件列表</h4>
            '''
            for plugin in project_structure.get('plugins', []):
                html += f'''
                            <div class="dependency-item">
                                <strong>{plugin.get('artifact_id', 'N/A')}</strong>
                                <br><small>Group: {plugin.get('group_id', 'N/A')} | Version: {plugin.get('version', 'N/A')}</small>
                            </div>
                '''
            html += '</div>'

        # 显示所有属性信息
        if project_structure.get('properties'):
            html += '''
                        <div class="detail-card">
                            <h4>项目属性</h4>
                            <ul class="detail-list">
            '''
            for key, value in project_structure.get('properties', {}).items():
                html += f'<li><span class="detail-label">{key}</span><span class="detail-value">{value}</span></li>'
            html += '</ul></div>'

        # 显示错误信息（如果有）
        if project_structure.get('error'):
            html += f'''
                        <div class="detail-card">
                            <h4>错误信息</h4>
                            <p class="error">{project_structure.get('error')}</p>
                        </div>
            '''

        return html

    def _generate_nodejs_details(self, project_structure: dict) -> str:
        """生成Node.js项目详情HTML"""
        html = f'''
                        <div class="detail-card">
                            <h4>Node.js项目详情</h4>
                            <ul class="detail-list">
                                <li><span class="detail-label">项目类型</span><span class="detail-value">{project_structure.get('type', 'N/A')}</span></li>
                                <li><span class="detail-label">项目名称</span><span class="detail-value">{project_structure.get('metadata', {}).get('name', 'N/A')}</span></li>
                                <li><span class="detail-label">版本</span><span class="detail-value">{project_structure.get('metadata', {}).get('version', 'N/A')}</span></li>
                                <li><span class="detail-label">描述</span><span class="detail-value">{project_structure.get('metadata', {}).get('description', 'N/A')}</span></li>
                                <li><span class="detail-label">主入口</span><span class="detail-value">{project_structure.get('metadata', {}).get('main', 'N/A')}</span></li>
                                <li><span class="detail-label">作者</span><span class="detail-value">{project_structure.get('metadata', {}).get('author', 'N/A')}</span></li>
                                <li><span class="detail-label">依赖数量</span><span class="detail-value">{len(project_structure.get('dependencies', {}))}</span></li>
                                <li><span class="detail-label">开发依赖数量</span><span class="detail-value">{len(project_structure.get('dev_dependencies', {}))}</span></li>
                                <li><span class="detail-label">脚本数量</span><span class="detail-value">{len(project_structure.get('scripts', {}))}</span></li>
                                <li><span class="detail-label">引擎要求</span><span class="detail-value">{len(project_structure.get('engines', {}))}</span></li>
                            </ul>
                        </div>
        '''

        # 显示所有依赖信息
        if project_structure.get('dependencies'):
            html += '''
                        <div class="detail-card">
                            <h4>生产依赖</h4>
                            <ul class="detail-list">
            '''
            for dep_name, dep_version in project_structure.get('dependencies', {}).items():
                html += f'<li><span class="detail-label">{dep_name}</span><span class="detail-value">{dep_version}</span></li>'
            html += '</ul></div>'

        # 显示所有开发依赖信息
        if project_structure.get('dev_dependencies'):
            html += '''
                        <div class="detail-card">
                            <h4>开发依赖</h4>
                            <ul class="detail-list">
            '''
            for dep_name, dep_version in project_structure.get('dev_dependencies', {}).items():
                html += f'<li><span class="detail-label">{dep_name}</span><span class="detail-value">{dep_version}</span></li>'
            html += '</ul></div>'

        # 显示所有脚本信息
        if project_structure.get('scripts'):
            html += '''
                        <div class="detail-card">
                            <h4>可用脚本</h4>
                            <ul class="detail-list">
            '''
            for script_name, script_cmd in project_structure.get('scripts', {}).items():
                html += f'<li><span class="detail-label">{script_name}</span><span class="detail-value">{script_cmd}</span></li>'
            html += '</ul></div>'

        # 显示所有引擎要求信息
        if project_structure.get('engines'):
            html += '''
                        <div class="detail-card">
                            <h4>引擎要求</h4>
                            <ul class="detail-list">
            '''
            for engine_name, engine_version in project_structure.get('engines', {}).items():
                html += f'<li><span class="detail-label">{engine_name}</span><span class="detail-value">{engine_version}</span></li>'
            html += '</ul></div>'

        # 显示错误信息（如果有）
        if project_structure.get('error'):
            html += f'''
                        <div class="detail-card">
                            <h4>错误信息</h4>
                            <p class="error">{project_structure.get('error')}</p>
                        </div>
            '''

        return html

    def _generate_vue_details(self, project_structure: dict) -> str:
        """生成Vue项目详情HTML"""
        html = f'''
                        <div class="detail-card">
                            <h4>Vue项目详情</h4>
                            <ul class="detail-list">
                                <li><span class="detail-label">项目类型</span><span class="detail-value">{project_structure.get('type', 'N/A')}</span></li>
                                <li><span class="detail-label">配置文件数量</span><span class="detail-value">{len(project_structure.get('config_files', []))}</span></li>
                                <li><span class="detail-label">构建工具数量</span><span class="detail-value">{len(project_structure.get('build_tools', []))}</span></li>
                            </ul>
                        </div>
        '''

        # 显示所有配置文件
        if project_structure.get('config_files'):
            html += '''
                        <div class="detail-card">
                            <h4>配置文件</h4>
                            <ul class="detail-list">
            '''
            for config_file in project_structure.get('config_files', []):
                html += f'<li><span class="detail-label">配置文件</span><span class="detail-value">{config_file}</span></li>'
            html += '</ul></div>'

        # 显示所有构建工具
        if project_structure.get('build_tools'):
            html += '''
                        <div class="detail-card">
                            <h4>构建工具</h4>
                            <ul class="detail-list">
            '''
            for build_tool in project_structure.get('build_tools', []):
                html += f'<li><span class="detail-label">构建工具</span><span class="detail-value">{build_tool}</span></li>'
            html += '</ul></div>'

        # 显示所有目录结构信息
        if project_structure.get('structure'):
            html += '''
                        <div class="detail-card">
                            <h4>目录结构</h4>
            '''
            for dir_name, dir_info in project_structure.get('structure', {}).items():
                if dir_info.get('exists'):
                    html += f'''
                            <div class="structure-item exists">
                                <strong>✓ {dir_name}</strong>
                                <br><small>文件数量: {dir_info.get('file_count', 0)} | 子目录: {", ".join(dir_info.get('sub_dirs', [])) or '无'}</small>
                            </div>
                    '''
                else:
                    html += f'''
                            <div class="structure-item not-exists">
                                <strong>✗ {dir_name}</strong>
                                <br><small>目录不存在</small>
                            </div>
                    '''
            html += '</div>'

        # 显示错误信息（如果有）
        if project_structure.get('error'):
            html += f'''
                        <div class="detail-card">
                            <h4>错误信息</h4>
                            <p class="error">{project_structure.get('error')}</p>
                        </div>
            '''

        return html

    def _generate_generic_details(self, analysis: dict) -> str:
        """生成通用模块详情HTML"""
        complexity_data = analysis.get('complexity', {})

        html = f'''
                        <div class="detail-card">
                            <h4>复杂度详情</h4>
                            <ul class="detail-list">
                                <li><span class="detail-label">文件数量</span><span class="detail-value">{complexity_data.get('total_files', 0)}</span></li>
                                <li><span class="detail-label">代码行数</span><span class="detail-value">{complexity_data.get('total_lines', 0)}</span></li>
                                <li><span class="detail-label">复杂度</span><span class="detail-value">{complexity_data.get('total_complexity', 0)}</span></li>
                            </ul>
                        </div>
        '''

        file_complexity = complexity_data.get('file_complexity', {})
        if file_complexity:
            file_types = {}
            for file_path, file_data in file_complexity.items():
                if isinstance(file_data, dict) and 'file_extension' in file_data:
                    ext = file_data['file_extension'].lower()
                    if ext not in file_types:
                        file_types[ext] = 0
                    file_types[ext] += 1

            if file_types:
                html += '''
                            <div class="detail-card">
                                <h4>文件类型分布</h4>
                                <ul class="detail-list">
                '''
                for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
                    html += f'<li><span class="detail-label">{ext}</span><span class="detail-value">{count}</span></li>'
                html += '</ul></div>'

        return html
