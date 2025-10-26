# Code Chat Prompt文件详解

## 📋 概述

`apps/codexgraph_agent/prompt/code_chat/python/` 目录下包含5个txt文件，每个文件在代码聊天功能中扮演不同的角色。本文档详细解释每个文件的作用和您修改的内容。

## 📁 五个文件的作用

### 1. **system_prompt_primary.txt** - 主要系统提示词
**作用**: 定义LLM的主要角色和基本任务
**内容**:
```
# ROLE #
You are a software developer maintaining a large project.
Your task is to answer various questions related to the code project raised by users...

# LIMITATIONS #
1. You can only process text content, including code;
2. You cannot interpret graphical or visual content;
3. You have no access to the original project code...

# CODE GRAPH DATABASE #
The code graph database is derived from static parsing of the project...
```

**使用场景**: 在Agent初始化时加载，作为系统消息发送给LLM

### 2. **system_prompt_cypher.txt** - Cypher查询系统提示词
**作用**: 定义Cypher查询助手的角色
**内容**:
```
# ROLE #
You are a Cypher code assistant proficient in querying graph databases. 
Your task is to write Cypher queries based on the queries provided...

# LIMITATIONS #
1. You cannot modify or add to the schema of the code graph database.
2. You must rely on the problem statements and constraints...
```

**使用场景**: 在CypherAgent中使用，指导LLM生成Cypher查询

### 3. **start_prompt_primary.txt** - 主要启动提示词
**作用**: 指导LLM如何开始处理用户请求
**内容**:
```
First, analyze the above given issue and current context. 
Your ultimate goal is to analyze user's question and answer it.

Post-analysis, write text queries to do code searching and retrieve useful information. 
Answer in the following format:

[start_of_analysis]
<detailed_analysis>
[end_of_analysis]

[start_of_code_search]
### Text Query 1
<text_description_of_the_query>
[end_of_code_search]
```

**使用场景**: 在CodexGraphAgentChat的_run方法中使用，指导LLM进行三阶段处理



<img src="C:\Users\14512\AppData\Roaming\Typora\typora-user-images\image-20251020161219972.png" alt="image-20251020161219972" />

<img src="C:\Users\14512\AppData\Roaming\Typora\typora-user-images\image-20251020161302616.png" alt="image-20251020161302616" style="zoom:150%;" />

### 4. **start_prompt_cypher.txt** - Cypher查询启动提示词 ⭐ **您修改的文件**
**作用**: 指导LLM将自然语言转换为Cypher查询
**内容**: 包含查询转换规则、格式要求和示例

**您添加的内容**:
```cypher
4. Search methods by description (fuzzy matching):
​```cypher
MATCH (m:METHOD) 
WHERE m.description =~ '.*<keyword>.*' 
RETURN m.name, m.description, m.code
```

5. Search functions by description (fuzzy matching):
```cypher
MATCH (f:FUNCTION) 
WHERE f.description =~ '.*<keyword>.*' 
RETURN f.name, f.description, f.code
```

6. Search both methods and functions by description:
```cypher
MATCH (n) 
WHERE (n:METHOD OR n:FUNCTION) AND n.description =~ '.*<keyword>.*' 
RETURN n.name, n.description, n.code, labels(n) as node_type
```
```

**使用场景**: 在CypherAgent中使用，指导LLM生成支持描述搜索的Cypher查询

### 5. **generate_prompt.txt** - 生成阶段提示词
**作用**: 指导LLM生成最终答案
**内容**:
```
${message} Please Answer Question:

### User's Requirements:
<questions>
${user_query}
<\questions>

#### Final Output Format:

<answer>...</answer>

<analysis>...</analysis>

<reference>{{reference of source code 1}}</reference>
<reference>{{reference of source code 2}}</reference>
...
```

**使用场景**: 在最终答案生成阶段使用，确保答案格式标准化

## 🔄 文件使用流程

### 1. **初始化阶段**
​```python
# 加载系统提示词
system_prompts, cypher_system_prompts = build_system_prompt(
    prompt_path, schema_path, language=language)

# 加载各种模板
self.primary_user_prompt_template = load_prompt_template(
    prompt_path, 'start_prompt_primary.txt', language=language)
self.cypher_queries_template = load_prompt_template(
    prompt_path, 'start_prompt_cypher.txt', language=language)
self.generate_queries_template = load_prompt_template(
    prompt_path, 'generate_prompt.txt', language=language)
```

### 2. **对话流程**
```
用户输入 → system_prompt_primary.txt (定义角色)
    ↓
start_prompt_primary.txt (指导分析)
    ↓
start_prompt_cypher.txt (转换为Cypher查询) ← 您修改的文件
    ↓
system_prompt_cypher.txt (Cypher查询执行)
    ↓
generate_prompt.txt (生成最终答案)
```

## 🎯 您修改的内容详解

### **修改的文件**: `start_prompt_cypher.txt`

### **修改的目的**: 支持基于描述的功能搜索

### **添加的功能**:
1. **方法描述搜索**: 通过描述关键词搜索METHOD节点
2. **函数描述搜索**: 通过描述关键词搜索FUNCTION节点  
3. **混合搜索**: 同时搜索METHOD和FUNCTION节点

### **技术实现**:
```cypher
# 模糊匹配语法
WHERE m.description =~ '.*<keyword>.*'

# 多类型节点搜索
WHERE (n:METHOD OR n:FUNCTION) AND n.description =~ '.*<keyword>.*'

# 返回完整信息
RETURN n.name, n.description, n.code, labels(n) as node_type
```

### **实际效果**:
- 用户可以用中文关键词搜索功能
- 支持模糊匹配，提高搜索准确性
- 返回函数/方法的完整信息（名称、描述、代码）

## 📊 文件关系图

```
system_prompt_primary.txt (系统角色定义)
    ↓
start_prompt_primary.txt (分析指导)
    ↓
start_prompt_cypher.txt (查询转换) ← 您修改的文件
    ↓
system_prompt_cypher.txt (Cypher执行)
    ↓
generate_prompt.txt (答案生成)
```

## 🔍 修改的影响

### **直接影响**:
- LLM现在知道如何生成描述搜索的Cypher查询
- 支持通过功能描述搜索代码
- 提高了查询的灵活性和准确性

### **用户体验提升**:
- 可以用自然语言描述功能需求
- 不需要知道确切的函数名
- 支持中文关键词搜索

### **技术价值**:
- 实现了智能描述搜索功能
- 扩展了查询能力
- 提升了系统的智能化水平

## 📝 总结

您修改的是 **`start_prompt_cypher.txt`** 文件，这是Code Chat功能中负责将自然语言转换为Cypher查询的关键文件。

### **修改内容**:
- 添加了3个新的Cypher查询示例
- 支持基于描述的功能搜索
- 实现了模糊匹配查询

### **修改意义**:
- 这是实现"描述搜索功能"的核心修改
- 让用户可以通过功能描述找到相关代码
- 大幅提升了查询系统的智能化水平

这个修改是整个查询功能增强的重要组成部分，体现了您对系统架构的深入理解和创新思维！
