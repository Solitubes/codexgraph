# CodexGraph Agent Prompt系统详解

## 📋 概述

Prompt系统是CodexGraph Agent的核心组件，它通过精心设计的提示词模板来指导大语言模型(LLM)的行为，确保系统能够准确理解用户意图并执行相应的代码分析任务。

## 🎯 Prompt的作用

### 1. **指导LLM行为**
- 定义LLM的角色和职责
- 规范LLM的响应格式
- 确保LLM按照预期方式工作

### 2. **标准化交互流程**
- 统一不同任务的处理方式
- 确保输出格式的一致性
- 提供可预测的用户体验

### 3. **优化查询效果**
- 提高代码搜索的准确性
- 增强Cypher查询的生成质量
- 改善最终答案的完整性

## 🏗️ Prompt系统架构

### 目录结构
```
apps/codexgraph_agent/prompt/
├── code_chat/          # 代码聊天功能
├── code_commenter/     # 代码注释生成
├── code_debugger/      # 代码调试
├── code_generator/     # 代码生成
├── code_unittester/    # 单元测试生成
└── graph_database/     # 图数据库模式
```

### 文件类型
每个功能模块都包含以下类型的prompt文件：

1. **system_prompt_primary.txt** - 主要系统提示词
2. **system_prompt_cypher.txt** - Cypher查询系统提示词
3. **start_prompt_primary.txt** - 主要启动提示词
4. **start_prompt_cypher.txt** - Cypher查询启动提示词
5. **generate_prompt.txt** - 生成阶段提示词

## 🔍 各类型Prompt详解

### 1. 系统提示词 (System Prompts)

#### **system_prompt_primary.txt**
- **作用**: 定义LLM的主要角色和任务
- **内容**: 描述LLM作为代码分析专家的身份
- **示例**: "You are a software developer maintaining a large project..."

#### **system_prompt_cypher.txt**
- **作用**: 定义Cypher查询助手的角色
- **内容**: 指导LLM如何生成Cypher查询
- **示例**: "You are a Cypher code assistant proficient in querying graph databases..."

### 2. 启动提示词 (Start Prompts)

#### **start_prompt_primary.txt**
- **作用**: 指导LLM如何开始处理用户请求
- **内容**: 定义分析流程和输出格式
- **关键特性**:
  - 使用标记格式 `[start_of_xxx]` 和 `[end_of_xxx]`
  - 定义三阶段处理：分析→搜索→答案
  - 提供查询示例和最佳实践

#### **start_prompt_cypher.txt**
- **作用**: 指导LLM将自然语言转换为Cypher查询
- **内容**: 定义查询转换规则和格式
- **关键特性**:
  - 支持模糊匹配和精确匹配
  - 提供Cypher查询示例
  - 包含错误处理指导

### 3. 生成提示词 (Generate Prompts)

#### **generate_prompt.txt**
- **作用**: 指导LLM生成最终答案
- **内容**: 定义答案格式和结构
- **关键特性**:
  - 标准化答案格式
  - 包含分析、结论、引用等部分
  - 确保答案的完整性

## 🎨 不同功能的Prompt特点

### 1. Code Chat (代码聊天)
```markdown
# 特点
- 支持自然语言查询
- 三阶段处理流程
- 智能分析用户意图

# 关键标记
[start_of_analysis] ... [end_of_analysis]
[start_of_code_search] ... [end_of_code_search]
[start_of_answer] ... [end_of_answer]
```

### 2. Code Commenter (代码注释)
```markdown
# 特点
- JSON格式响应
- 支持两种动作：ADD_COMMENTS 和 TEXT_QUERIES
- 标准化注释格式

# 响应格式
{"thought": "...", "action": "ADD_COMMENTS", "action_input": "..."}
```

### 3. Code Debugger (代码调试)
```markdown
# 特点
- 生成代码补丁
- 支持多文件修改
- 标准化的补丁格式

# 输出格式
<file>...</file>
<original>...</original>
<patched>...</patched>
```

### 4. Code Generator (代码生成)
```markdown
# 特点
- 基于需求生成代码
- 支持多文件生成
- 遵循编码规范
```

### 5. Code Unittester (单元测试)
```markdown
# 特点
- 生成专业单元测试
- 支持多种测试场景
- 包含测试用例和断言
```

## 🔧 Prompt的技术实现

### 1. 模板变量替换
```python
# 在代码中使用模板
template = load_prompt_template(prompt_path, 'start_prompt_primary.txt')
user_prompt = template.substitute(
    file_path=file_path,
    user_query=user_query
)
```

### 2. 动态内容注入
```python
# 注入图数据库模式
system_prompt = system_prompt.replace('{{python_db_schema}}', schema_content)
```

### 3. 上下文管理
```python
# 构建消息历史
messages = [
    {'role': 'system', 'content': system_prompt},
    {'role': 'user', 'content': user_prompt}
]
```

## 📊 Prompt优化策略

### 1. **清晰的角色定义**
- 明确定义LLM的角色和职责
- 提供具体的任务指导
- 设置明确的边界和限制

### 2. **结构化的输出格式**
- 使用标记分隔不同部分
- 提供标准化的响应模板
- 确保输出的一致性

### 3. **丰富的示例和指导**
- 提供正面和负面示例
- 包含最佳实践指导
- 给出具体的查询模式

### 4. **错误处理和边界情况**
- 定义错误处理策略
- 提供降级方案
- 处理异常情况

## 🎯 Prompt的实际应用

### 1. **用户查询处理**
```
用户输入: "在仓库里实现计算功能的函数是哪一个？"
↓
start_prompt_primary.txt 指导分析
↓
LLM生成: [start_of_analysis] ... [end_of_analysis]
```

### 2. **Cypher查询生成**
```
文本查询: "查找所有描述中包含计算功能的函数"
↓
start_prompt_cypher.txt 指导转换
↓
LLM生成: MATCH (n) WHERE n.description =~ '.*计算.*' RETURN n
```

### 3. **最终答案生成**
```
查询结果: [查询到的函数信息]
↓
generate_prompt.txt 指导生成
↓
LLM生成: 格式化的最终答案
```

## 🔮 Prompt系统的优势

### 1. **灵活性**
- 支持多种任务类型
- 易于扩展和修改
- 适应不同的使用场景

### 2. **一致性**
- 标准化的输出格式
- 可预测的行为模式
- 统一的用户体验

### 3. **可维护性**
- 模块化的设计
- 清晰的职责分离
- 易于调试和优化

### 4. **可扩展性**
- 支持新功能的添加
- 灵活的模板系统
- 动态内容注入

## 📝 总结

Prompt系统是CodexGraph Agent的"大脑"，它通过精心设计的提示词模板来：

1. **指导LLM行为**: 确保AI按照预期方式工作
2. **标准化流程**: 提供一致的用户体验
3. **优化查询效果**: 提高代码分析的准确性
4. **支持多任务**: 适应不同的代码分析需求

通过这个系统，CodexGraph Agent能够理解用户的自然语言查询，生成准确的Cypher查询，并提供高质量的代码分析结果。Prompt系统的设计体现了现代AI系统中提示工程的最佳实践，是确保系统性能和用户体验的关键组件。
