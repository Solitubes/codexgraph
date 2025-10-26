# CodexGraph 方法描述生成功能

## 概述

本功能为CodexGraph的METHOD节点添加了智能描述生成能力，使用大模型自动分析每个方法的功能和作用，为代码理解和导航提供更丰富的信息。

## 功能特点

- **智能分析**: 使用大模型分析方法的代码，生成简洁准确的功能描述
- **批量处理**: 支持批量生成方法描述，提高处理效率
- **缓存机制**: 内置缓存系统，避免重复生成相同方法的描述
- **灵活配置**: 支持多种大模型API，可自定义配置参数
- **增量更新**: 支持为现有图数据库添加描述信息

## 文件结构

```
indexer/
├── method_description_generator.py    # 核心描述生成器
├── my_client.py                       # 修改后的客户端（集成描述生成）
├── llm_config.json                    # 配置文件
├── test_method_description.py         # 测试脚本
├── enhanced_build_example.py          # 使用示例
└── README_METHOD_DESCRIPTION.md       # 本文档
```

## 安装依赖

```bash
# 安装大模型API客户端
pip install openai

# 或者使用其他大模型API
pip install anthropic  # 如果使用Claude
```

## 配置说明

### 1. 环境变量配置

```bash
# 设置API密钥
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选，默认值
```

### 2. 配置文件

编辑 `llm_config.json`:

```json
{
    "llm_config": {
        "model_name": "deepseek-coder",
        "api_key": "your-api-key",
        "base_url": "https://api.openai.com/v1",
        "max_tokens": 200,
        "temperature": 0.3
    },
    "description_settings": {
        "enable_description": true,
        "cache_descriptions": true,
        "cache_file": "method_descriptions_cache.json"
    }
}
```

## 使用方法

### 1. 基础使用

```python
from method_description_generator import MethodDescriptionGenerator

# 创建描述生成器
generator = MethodDescriptionGenerator()

# 为单个方法生成描述
description = generator.generate_method_description(
    method_code="def add(self, amount):\n    self.value += amount\n    return self.value",
    method_name="add",
    class_name="Calculator",
    file_path="calculator.py"
)

print(description)  # 输出: 该方法用于执行加法运算，将amount参数加到当前值上，并返回运算结果
```

### 2. 批量生成

```python
# 批量生成方法描述
methods = [
    {
        'method_name': 'add',
        'method_code': 'def add(self, amount): ...',
        'class_name': 'Calculator',
        'file_path': 'calculator.py'
    },
    # ... 更多方法
]

descriptions = generator.batch_generate_descriptions(methods)
```

### 3. 集成到图数据库构建

```python
from enhanced_build_example import enhanced_build_graph_database

# 构建包含方法描述的图数据库
graph_db = enhanced_build_graph_database(
    repo_path="/path/to/your/code",
    task_id="enhanced_001",
    llm_config={
        'model_name': 'deepseek-coder',
        'api_key': 'your-api-key'
    }
)
```

### 4. 为现有图数据库添加描述

```python
from enhanced_build_example import update_existing_methods_with_descriptions

# 为现有的METHOD节点添加描述
update_existing_methods_with_descriptions(
    graph_db=graph_db,
    task_id="enhanced_001",
    llm_config=llm_config
)
```

## 测试

### 运行测试脚本

```bash
cd modelscope_agent/environment/graph_database/indexer
python test_method_description.py
```

### 测试内容

- 基础描述生成功能
- 批量生成功能
- 缓存机制
- 真实代码分析

## 生成的描述示例

| 方法代码 | 生成的描述 |
|---------|-----------|
| `def __init__(self, value=0): self.value = value` | 该方法用于初始化对象实例，设置初始值为value参数，默认为0 |
| `def add(self, amount): return self.value + amount` | 该方法用于执行加法运算，将当前值与amount参数相加并返回结果 |
| `def get_value(self): return self.value` | 该方法用于获取当前存储的数值 |
| `def calculate_area(self, radius): return 3.14 * radius * radius` | 该方法用于计算圆的面积，根据半径参数计算并返回面积值 |

## 图数据库查询

### 查询带有描述的方法

```cypher
// 查询所有带有描述的METHOD节点
MATCH (m:METHOD {task_id: "your_task_id"})
WHERE exists(m.description)
RETURN m.name, m.class, m.description, m.file_path
ORDER BY m.class, m.name
```

### 按描述内容搜索

```cypher
// 搜索包含特定关键词的方法
MATCH (m:METHOD {task_id: "your_task_id"})
WHERE m.description CONTAINS "计算"
RETURN m.name, m.class, m.description
```

## 性能优化

### 1. 缓存机制

- 自动缓存已生成的描述
- 支持从文件加载/保存缓存
- 避免重复API调用

### 2. 批量处理

- 支持批量生成描述
- 可配置请求间隔
- 减少API调用次数

### 3. 错误处理

- 自动重试机制
- 降级到模拟描述
- 详细的错误日志

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 查看API配额是否充足

2. **描述质量不佳**
   - 调整temperature参数
   - 优化提示词模板
   - 检查代码质量

3. **性能问题**
   - 启用缓存机制
   - 使用批量处理
   - 调整请求间隔

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 使用模拟模式测试
generator = MethodDescriptionGenerator({
    'model_name': 'mock',  # 使用模拟模式
    'api_key': 'test'
})
```

## 扩展功能

### 1. 自定义提示词

可以修改 `method_description_generator.py` 中的 `_build_prompt` 方法来自定义提示词模板。

### 2. 支持其他节点类型

可以扩展功能为CLASS、FUNCTION等节点类型也生成描述。

### 3. 多语言支持

可以修改提示词模板支持生成英文或其他语言的描述。

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目遵循与CodexGraph相同的许可证。
