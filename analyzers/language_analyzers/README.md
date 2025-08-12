# 语言分析器

## 概述

语言分析器是项目复杂度分析工具的核心组件，负责分析不同编程语言的源代码文件，计算复杂度指标，并提供语言特定的统计信息。

实现了插件化架构。新增语言分析器时，无需修改任何核心代码，系统完全动态化。

## 🎯 核心设计原则

### **1. 零硬编码**
- ❌ 没有硬编码的语言名称判断
- ❌ 没有硬编码的阈值映射
- ❌ 没有硬编码的导入语句
- ✅ 完全基于动态发现和智能推断

### **2. 语言分析器自己声明能力**
- 通过 `can_analyze()` 方法声明能处理哪些文件
- 通过 `file_extensions` 属性声明支持的文件扩展名
- 通过 `threshold_coefficient` 声明复杂度阈值系数
- 通过 `default_thresholds` 声明默认阈值

### **3. 智能推断机制**
- 基于语言名称和特性智能推断阈值系数
- 动态计算默认阈值
- 多层级后备机制确保系统稳定性

## 🔧 实现方式

### **方式1: 类接口（推荐）**

```python
class MyLanguageAnalyzer:
    # 声明支持的文件扩展名
    file_extensions = ['.my', '.mylang', '.ml']

    # 声明阈值系数（可选）
    threshold_coefficient = 20  # 中等复杂度语言

    # 声明默认阈值（可选）
    default_thresholds = {
        'low': 5, 'medium': 15, 'high': 25, 'very_high': 50
    }

    def can_analyze(self, file_path: Path) -> bool:
        """智能判断是否能处理指定文件"""
        # 扩展名判断
        if file_path.suffix.lower() in self.file_extensions:
            return True

        # 内容判断（更智能）
        try:
            with open(file_path, 'r') as f:
                content = f.read(1000)
                if 'my_language_keyword' in content:
                    return True
        except:
            pass

        return False

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """分析文件复杂度"""
        # 实现复杂度分析逻辑
        pass
```

### **方式2: 函数接口（兼容性）**

```python
def analyze_mylang_complexity_detailed(file_path: Path) -> Dict[str, Any]:
    """函数接口的复杂度分析"""
    # 实现复杂度分析逻辑
    pass
```

## 📁 文件结构

```
analyzers/
├── language_analyzers/
│   ├── java_analyzer.py          # Java分析器
│   ├── python_analyzer.py        # Python分析器
│   ├── example_analyzer.py       # 示例分析器
│   └── my_new_language.py        # 新增语言分析器
├── complexity_analyzer.py        # 核心复杂度分析器
└── language_analyzer_manager.py  # 语言分析器管理器
```

## 🚀 新增语言分析器步骤

### **步骤1: 创建分析器文件**

在 `analyzers/language_analyzers/` 目录下创建 `my_language_analyzer.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Dict, Any

class MyLanguageAnalyzer:
    file_extensions = ['.ml', '.mylang']
    threshold_coefficient = 25  # 脚本语言，复杂度较低

    def can_analyze(self, file_path: Path) -> bool:
        # 实现文件识别逻辑
        return file_path.suffix.lower() in self.file_extensions

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        # 实现复杂度分析逻辑
        pass

# 函数接口（可选）
def analyze_mylang_complexity_detailed(file_path: Path) -> Dict[str, Any]:
    analyzer = MyLanguageAnalyzer()
    return analyzer.analyze(file_path)
```

### **步骤2: 完成！**

新语言分析器现在会自动：
- 被系统识别
- 处理对应的文件类型
- 参与复杂度分析
- 出现在支持语言列表中
- **自动获得合适的阈值配置**

## 🔍 智能文件识别

### **扩展名识别**
```python
file_extensions = ['.java', '.ts', '.tsx', '.js', '.jsx']
```

### **内容识别**
```python
def can_analyze(self, file_path: Path) -> bool:
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline()
            if first_line.startswith('#!') and 'python' in first_line:
                return True

            content = f.read(1000)
            if 'import java' in content or 'public class' in content:
                return True
    except:
        pass
    return False
```

### **混合识别**
```python
def can_analyze(self, file_path: Path) -> bool:
    # 优先检查扩展名
    if file_path.suffix.lower() in self.file_extensions:
        return True

    # 扩展名不匹配时，检查内容
    return self._check_file_content(file_path)
```

## 📊 系统架构

```
文件 → 遍历所有分析器 → 调用 can_analyze() → 选择匹配的分析器 → 调用 analyze()
```

## 🧠 智能推断机制

### **阈值系数智能推断**
系统会根据语言名称和特性自动推断合适的阈值系数：

```python
def _infer_language_threshold_coefficient(lang: str) -> int:
    # 标记语言（复杂度很低）
    if any(marker in lang_lower for marker in ['html', 'xml', 'markdown']):
        return 50

    # 数据格式（复杂度很低）
    if any(marker in lang_lower for marker in ['json', 'yaml', 'toml']):
        return 40

    # 样式语言（复杂度较低）
    if any(marker in lang_lower for marker in ['css', 'scss', 'sass']):
        return 30

    # 脚本语言（复杂度中等）
    if any(marker in lang_lower for marker in ['python', 'ruby', 'perl']):
        return 20

    # 编译语言（复杂度较高）
    if any(marker in lang_lower for marker in ['java', 'c', 'cpp', 'go']):
        return 15

    # 默认值
    return 20
```

### **动态阈值计算**
```python
# 基于系数动态计算阈值
thresholds[lang] = {
    'low': base_thresholds['LOW'] // threshold_coefficient,
    'medium': base_thresholds['MEDIUM'] // threshold_coefficient,
    'high': base_thresholds['HIGH'] // threshold_coefficient,
    'very_high': base_thresholds['VERY_HIGH'] // threshold_coefficient
}
```

## 支持的语言

### 后端语言

#### Java 分析器 (`java_analyzer.py`)
- **文件扩展名**: `.java`
- **特性**:
  - Maven/Gradle 项目支持
  - 类和方法复杂度分析
  - 继承关系检测
  - 注解和泛型支持
- **复杂度计算**: 基于控制流图的圈复杂度

#### Python 分析器 (`python_analyzer.py`)
- **文件扩展名**: `.py`
- **特性**:
  - 函数和类复杂度分析
  - 装饰器支持
  - 异常处理分析
  - 导入依赖统计
- **复杂度计算**: 基于 AST 的复杂度分析

#### SQL 分析器 (`sql_analyzer.py`)
- **文件扩展名**: `.sql`
- **特性**:
  - 查询复杂度分析
  - 表结构统计
  - 存储过程分析
  - 索引使用分析
- **复杂度计算**: 基于 SQL 语句结构的复杂度

### 前端语言

#### TypeScript 分析器 (`typescript_analyzer.py`)
- **文件扩展名**: `.ts`, `.tsx`
- **特性**:
  - 类型系统复杂度
  - 接口和泛型分析
  - 模块依赖分析
  - 装饰器支持
- **复杂度计算**: 结合类型复杂度的圈复杂度

#### JavaScript 分析器 (`javascript_analyzer.py`)
- **文件扩展名**: `.js`, `.jsx`
- **特性**:
  - ES6+ 语法支持
  - 函数复杂度分析
  - 异步代码分析
  - 模块系统支持
- **复杂度计算**: 标准圈复杂度算法

#### Vue 分析器 (`vue_analyzer.py`)
- **文件扩展名**: `.vue`
- **特性**:
  - 单文件组件分析
  - 模板复杂度计算
  - 组件生命周期分析
  - 响应式数据复杂度
- **复杂度计算**: 综合模板和脚本的复杂度

## 分析器接口

所有语言分析器都继承自 `LanguageAnalyzer` 基类，必须实现以下接口：

### 必需属性

```python
@property
def language_name(self) -> str:
    """语言名称，用于标识分析器"""
    pass

@property
def file_extensions(self) -> List[str]:
    """支持的文件扩展名列表"""
    pass

@property
def analyzer_name(self) -> str:
    """分析器显示名称"""
    pass
```

### 必需方法

```python
def can_analyze(self, file_path: Path) -> bool:
    """判断是否可以分析指定文件"""
    pass

def analyze(self, file_path: Path) -> Dict[str, Any]:
    """分析文件并返回结果"""
    pass
```

## 分析结果格式

每个分析器返回的结果都遵循统一的格式：

```python
{
    'language': 'java',                    # 语言标识
    'file_path': str,                      # 文件路径
    'file_size': int,                      # 文件大小（字节）
    'total_lines': int,                    # 总行数
    'code_lines': int,                     # 代码行数
    'comment_lines': int,                  # 注释行数
    'blank_lines': int,                    # 空行数
    'complexity': {                        # 复杂度信息
        'total_complexity': int,           # 总复杂度
        'function_complexity': Dict,       # 函数复杂度
        'class_complexity': Dict,          # 类复杂度
        'average_complexity': float        # 平均复杂度
    },
    'structure': {                         # 结构信息
        'classes': int,                    # 类数量
        'functions': int,                  # 函数数量
        'interfaces': int,                 # 接口数量
        'imports': int                     # 导入数量
    },
    'metrics': {                           # 其他指标
        'nesting_depth': int,              # 最大嵌套深度
        'parameter_count': int,            # 参数数量
        'return_statements': int           # 返回语句数量
    },
    'analysis_time': float,                # 分析耗时
    'errors': List[str]                    # 分析过程中的错误
}
```

## 🔧 配置和自定义

### **阈值系数配置**
语言分析器可以声明自己的阈值系数：

```python
class MyLanguageAnalyzer:
    threshold_coefficient = 25  # 自定义系数
```

### **默认阈值配置**
语言分析器可以声明自己的默认阈值：

```python
class MyLanguageAnalyzer:
    default_thresholds = {
        'low': 3, 'medium': 10, 'high': 20, 'very_high': 40
    }
```

### **配置文件支持**
系统也支持从配置文件读取：

```yaml
# analyzer_config.yaml
language_threshold_coefficients:
  mylang: 25
  newlang: 30

language_default_thresholds:
  mylang:
    low: 3
    medium: 10
    high: 20
    very_high: 40
```

## 扩展新语言支持

### 1. 创建分析器文件

在 `language_analyzers/` 目录下创建新的 Python 文件，例如 `rust_analyzer.py`，实现参考[分析器接口](#分析器接口)

### 2. 注册分析器

分析器会自动被系统发现和加载，无需手动注册。系统会扫描 `language_analyzers/` 目录下的所有 Python 文件，自动加载继承自 `LanguageAnalyzer` 的类。

### 3. 配置分析器

可以在配置文件中为新的分析器添加特定配置：

```yaml
# analyzer_config.yaml
custom_analyzers:
  rust:
    enabled: true
    max_file_size: 5242880  # 5MB
    complexity_threshold: 100
    ignore_patterns:
      - "*.test.rs"
      - "*.bench.rs"
```
```python
from analyzers.analyzer_config import get_config_manager

config_manager = get_config_manager()
config_manager.add_custom_analyzer('rust', {
    'enabled': True,
    'max_file_size': 5 * 1024 * 1024,
    'complexity_threshold': 100
})
```

## 性能优化

### 并行处理

分析器管理器支持并行处理多个文件：

```python
from analyzers.language_analyzer_manager import get_analyzer_manager

manager = get_analyzer_manager()
# 并行分析多个文件
results = manager.analyze_files_parallel(file_paths)
```
