# HTML报告生成器模块化架构

本目录包含HTML报告生成器，按功能模块进行拆分。

## 文件结构

```
report/
├── __init__.py                    # 包初始化文件
├── README.md                      # 本说明文档
├── gen_html_overview.py          # 项目概览模块
├── gen_html_module.py            # 模块分析主模块
├── gen_html_module_core.py       # 模块分析核心功能模块
├── gen_html_module_structure.py  # 项目结构详情模块
├── gen_html_module_complexity.py # 复杂度分析详情模块
├── gen_html_tech.py              # 技术栈分布模块
├── gen_html_complexity.py        # 复杂度分析模块
├── gen_html_effort.py            # 二次开发新模块工作量估算模块
├── gen_html_recommend.py         # 开发建议模块
└── gen_html_main.py              # 统一入口模块
```

## 模块说明

### 1. gen_html_overview.py - 项目概览模块
- **功能**: 生成项目概览部分的HTML内容
- **主要方法**: `generate_overview_metrics()`
- **输出**: 项目概览指标卡片HTML

### 2. gen_html_module.py - 模块分析主模块
- **功能**: 整合所有子模块，完成模块分析部分的HTML生成
- **主要方法**: `generate_module_table()`
- **输出**: 完整的模块分析表格HTML

### 3. gen_html_module_core.py - 模块分析核心功能模块
- **功能**: 包含主要的表格生成逻辑
- **主要方法**: `generate_module_table()`
- **输出**: 基础表格HTML和模块数据

### 4. gen_html_module_structure.py - 项目结构详情模块
- **功能**: 包含各种项目类型的详情生成功能
- **主要方法**: `generate_project_structure_details()`
- **输出**: Maven、Node.js、Vue等项目的结构详情HTML

### 5. gen_html_module_complexity.py - 复杂度分析详情模块
- **功能**: 包含行数统计、深度分析、结构复杂度等功能
- **主要方法**:
  - `generate_lines_statistics()`
  - `generate_depth_analysis()`
  - `generate_structure_complexity()`
- **输出**: 复杂度分析详情HTML

### 6. gen_html_tech.py - 技术栈分布模块
- **功能**: 生成技术栈分布图表
- **主要方法**: `generate_tech_stack_chart()`
- **输出**: 技术栈分布图表的JavaScript代码

### 7. gen_html_complexity.py - 复杂度分析模块
- **功能**: 生成复杂度分析图表
- **主要方法**: `generate_complexity_chart()`
- **输出**: 复杂度分析图表的JavaScript代码

### 8. gen_html_effort.py - 二次开发新模块工作量估算模块
- **功能**: 生成工作量分析部分的HTML内容
- **主要方法**: `generate_effort_analysis()`
- **输出**: 工作量估算表格和指标HTML

### 9. gen_html_recommend.py - 开发建议模块
- **功能**: 生成建议和风险部分的HTML内容
- **主要方法**:
  - `generate_recommendations()`
  - `generate_risk_factors()`
  - `generate_development_recommendations()`
- **输出**: 开发建议和风险因素HTML

### 10. gen_html_main.py - 统一入口模块
- **功能**: 整合所有模块，完成整个HTML报告生成
- **主要方法**: `generate_html_report()`
- **输出**: 完整的HTML报告

## 模块分析子模块架构

模块分析部分采用了分层架构设计：

```
ModuleGenerator (主模块)
├── ModuleCoreGenerator (核心功能)
│   ├── 表格生成逻辑
│   ├── 文件类型统计
│   └── 基础数据结构
├── ModuleStructureGenerator (项目结构)
│   ├── Maven项目详情
│   ├── Node.js项目详情
│   ├── Vue项目详情
│   └── 通用项目详情
└── ModuleComplexityGenerator (复杂度分析)
    ├── 行数统计
    ├── 深度分析
    └── 结构复杂度
```

## 使用方法

### 从项目根目录调用
```bash
python gen_html_report.py analysis_report.json
```

### 从report目录调用
```bash
cd report
python gen_html_main.py ../analysis_report.json
```

### 作为模块导入
```python
from report.gen_html_main import HTMLReportGenerator

generator = HTMLReportGenerator('analysis_report.json')
generator.generate_html_report('output.html')
```

### 单独使用模块分析功能
```python
from report.gen_html_module import ModuleGenerator

module_generator = ModuleGenerator(data, language_manager, config)
module_table = module_generator.generate_module_table()
```
