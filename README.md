# code-complex-analysis

## 工具概述

这是一个通用的项目代码复杂度分析工具，专门针对多模块、多技术栈的复杂项目进行分析。工具采用插件化架构，支持多种编程语言，提供详细的复杂度分析、工作量估算和开发建议。

### 主要特点

- **模块化架构**：清晰的模块分离，易于维护和扩展
- **多语言支持**：Java、TypeScript、JavaScript、Vue、SQL、Python等
- **智能项目检测**：自动识别项目类型和技术栈
- **复杂度计算**：基于圈复杂度的科学评估
- **工作量估算**：针对二次开发场景的专业评估
- **可视化报告**：生成交互式HTML报告
- **风险识别**：自动识别开发风险点
- **建议生成**：提供具体的开发建议
- **性能优化**：并行处理、内存监控

---

## 系统架构

### 主程序入口

- **`proj_comp_analyzer.py`**
  - 统一的命令行接口
  - 完整的参数解析和验证
  - 集成了所有核心功能

### 核心模块

1. **核心分析器** (`analyzers/core_analyzer.py`)
   - 项目整体分析协调
   - 模块级分析管理
   - 性能监控和资源管理

2. **语言分析器管理器** (`analyzers/language_analyzer_manager.py`)
   - 动态加载语言分析器
   - 文件类型识别和分发
   - 分析器生命周期管理

3. **配置管理** (`analyzers/analyzer_config.py`)
   - 支持 YAML 和 JSON 配置文件
   - 动态配置更新
   - 配置验证和默认值管理

4. **项目检测器** (`analyzers/project_detector.py`)
   - 自动识别项目类型
   - 支持多种技术栈
   - 智能模块分类

5. **报告生成器** (`analyzers/report_generator.py`)
   - 多种输出格式
   - 性能指标统计
   - 开发建议生成

### 目录结构

```
├── analyzers/                     # 核心分析器模块
│   ├── __init__.py               # 包初始化文件
│   ├── core_analyzer.py          # 核心分析器
│   ├── language_analyzer_manager.py # 语言分析器管理器
│   ├── analyzer_config.py        # 配置管理

│   ├── project_detector.py       # 项目类型检测
│   ├── module_analyzer.py        # 模块分析器
│   ├── effort_analyzer.py        # 工作量估算
│   ├── report_generator.py       # 报告生成

│   ├── complexity_analyzer.py    # 复杂度分析
│   ├── project_structure_analyzer.py # 项目结构分析
│   ├── language_analyzers/       # 语言分析器目录
│   │   ├── java_analyzer.py      # Java 分析器
│   │   ├── typescript_analyzer.py # TypeScript 分析器
│   │   ├── javascript_analyzer.py # JavaScript 分析器
│   │   ├── python_analyzer.py    # Python 分析器
│   │   ├── sql_analyzer.py       # SQL 分析器
│   │   └── vue_analyzer.py       # Vue 分析器
│   └── README.md                 # 分析器文档
├── config/                       # 配置文件目录
│   ├── analyzer_config.yaml      # YAML 配置文件
│   └── README.md                 # 配置说明文档
├── report/                       # HTML报告生成器模块
│   ├── __init__.py               # 包初始化文件
│   ├── gen_html_main.py          # 主HTML生成器入口
│   ├── gen_html_overview.py      # 项目概览章节生成
│   ├── gen_html_module.py        # 模块分析章节生成
│   │   ├── gen_html_module_core.py      # 模块表格核心逻辑
│   │   ├── gen_html_module_complexity.py # 复杂度详情生成
│   │   └── gen_html_module_structure.py # 项目结构详情生成
│   ├── gen_html_tech.py          # 技术栈分布图表生成
│   ├── gen_html_complexity.py    # 复杂度分析图表生成
│   ├── gen_html_effort.py        # 工作量估算章节生成
│   ├── gen_html_recommend.py     # 开发建议章节生成
│   └── README.md                 # 报告生成器文档
├── proj_comp_analyzer.py         # 主程序入口
├── gen_html_report.py            # HTML 报告生成器
├── requirements.txt               # Python 依赖包
└── README.md                     # 本文档
```

### 分析数据流
```text
语言分析器 → 字段标准化 → 模块分析器 → 核心分析器 → 报告生成器
   ↓              ↓           ↓           ↓           ↓
lines → total_lines    → 统计汇总 → 结果存储 → HTML/JSON报告
complexity → total_complexity
```
---

## 核心功能

### 1. 代码复杂度分析
- **文件统计**：统计各种类型文件的数量和行数
- **圈复杂度计算**：计算代码的逻辑复杂度
- **深度分析**：分析代码嵌套深度
- **技术栈识别**：自动识别项目使用的技术栈

### 2. 二次开发工作量评估
- **新模块估算**：估算开发新的小、中、大模块所需工时
- **影响因子分析**：考虑项目复杂度、理解成本、集成难度
- **前后端分离**：分别估算前端和后端开发工时
- **理解成本计算**：评估学习现有代码所需时间

### 3. SQL数据库分析
- **表结构分析**：统计数据库表、视图、索引数量
- **SQL复杂度**：分析SQL语句的复杂程度
- **关系识别**：识别表之间的关联关系

### 4. 风险识别与建议
- **开发风险**：识别可能的技术难点和风险
- **团队建议**：推荐合适的团队配置
- **技术建议**：提供技术选型和架构建议

---

## 使用方法

### 安装依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 或单独安装
pip install PyYAML psutil
```

### 命令行使用

```bash
# 基本分析
python proj_comp_analyzer.py /path/to/project

# 指定输出文件
python proj_comp_analyzer.py /path/to/project -o report.json

# 详细输出模式
python proj_comp_analyzer.py /path/to/project -v

# 禁用并行处理
python proj_comp_analyzer.py /path/to/project --no-parallel

# 设置超时时间
python proj_comp_analyzer.py /path/to/project --timeout 600

# 设置最大文件大小
python proj_comp_analyzer.py /path/to/project --max-file-size 50
```

### 编程接口使用

```python
from analyzers import GenericComplexityAnalyzer, get_config

# 创建分析器
analyzer = GenericComplexityAnalyzer('/path/to/project')

# 开始分析
analyzer.scan_project()

# 生成报告
analyzer.generate_report('output.json')

# 获取配置
config = get_config()
print(f"最大文件大小: {config.max_file_size}")
```

### 生成HTML可视化报告

分析完成后，可以使用 `gen_html_report.py` 脚本将JSON报告转换为美观的HTML可视化报告：

```bash
# 基本用法：将JSON报告转换为HTML
python gen_html_report.py analysis_report.json

# 指定输出文件名
python gen_html_report.py analysis_report.json -o project_report.html

# 使用时间戳自动生成文件名
python gen_html_report.py analysis_report.json
```

---

## 配置管理
参考：[配置文件说明](config/README.md)

---

## 扩展开发
支持添加新语言支持，参考：[自定义语言分析器开发](analyzers/language_analyzers/README.md)
