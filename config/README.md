# 配置文件说明

## 配置文件格式

项目复杂度分析器现在支持两种配置文件格式：

### 1. YAML 格式（推荐）
- 文件：`analyzer_config.yaml`
- 优点：支持注释，可读性更好，语法简洁
- 要求：需要安装 `PyYAML` 包

### 2. JSON 格式（兼容）
- 文件：`analyzer_config.json`
- 优点：标准格式，所有工具都支持
- 缺点：不支持注释

## 配置文件优先级

系统会按以下优先级查找配置文件：
1. `analyzer_config.yaml`（如果存在）
2. `analyzer_config.json`（如果存在）
3. 使用默认配置（如果都不存在）

## 安装依赖

要使用 YAML 配置文件，请安装 PyYAML：

```bash
pip install PyYAML
```

或者使用项目提供的 requirements.txt：

```bash
pip install -r requirements.txt
```

## 配置文件结构

配置文件包含以下主要部分：

### 基础配置
- `enabled_analyzers`: 启用的语言分析器列表
- `max_file_size`: 最大文件大小限制
- `skip_patterns`: 跳过的文件模式

### 性能配置
- `parallel_processing`: 并行处理设置
- `caching`: 缓存配置
- `analysis_timeout`: 分析超时时间

### 阈值配置
- `complexity_thresholds`: 复杂度阈值
- `line_thresholds`: 代码行数阈值
- `file_thresholds`: 文件数量阈值
- `module_thresholds`: 模块数量阈值

### 工作量估算
- `effort_base_values`: 工作量基础值
- `factor_limits`: 因子限制
- `language_productivity_rates`: 语言生产力比率

### 技术栈分类
- `tech_stack_categories`: 按功能分类的技术栈
- `tech_diversity_thresholds`: 技术栈多样性阈值

### 输出配置
- `output`: 输出格式和内容
- `report_generation`: 报告生成选项
- `logging`: 日志配置

## 配置转换

如果使用 JSON 配置文件，可以：

1. 将 JSON 转换为 YAML 格式以获得更好的可读性
2. 使用配置管理器的 `save_to_file` 方法自动转换

## 示例用法

```python
from analyzers.analyzer_config import get_config, update_config

# 获取配置
config = get_config()

# 更新配置
update_config({
    'max_file_size': 20 * 1024 * 1024,  # 20MB
    'parallel_processing': {
        'max_workers': 8
    }
})
```

## 注意事项

1. YAML 文件中的注释以 `#` 开头
2. 缩进使用空格，不要使用制表符
3. 字符串值可以用引号包围，也可以不用
4. 布尔值：`true`/`false` 或 `True`/`False`
5. 数值：支持整数和浮点数
