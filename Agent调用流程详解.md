# CodexGraph Agent 调用流程详解

## 📋 概述

本文档详细解析CodexGraph Agent中用户ask的完整流程，对比原本流程和现在的流程，帮助理解整个系统的工作原理。

## 🔄 完整调用流程

### 1. 用户输入阶段
```
用户输入 → Streamlit界面 → CodeChatPage.run_agent()
```

**文件路径**: `apps/codexgraph_agent/pages/code_chat.py:65-109`

```python
def run_agent(self):
    user_input = st.session_state[self.page_name]['input_text']  # 获取用户输入
    
    # 创建或获取Agent实例
    if not self.agent:
        self.agent = self.get_agent()
    
    # 调用Agent的run方法
    try:
        answer = self.agent.run(user_input)  # 核心调用
    except Exception as e:
        answer = f"Sorry, I encountered an error: {str(e)}"
```

### 2. Agent初始化阶段
```
CodeChatPage.get_agent() → CodexGraphAgentChat.__init__()
```

**文件路径**: `apps/codexgraph_agent/pages/code_chat.py:24-63`

```python
def get_agent(self):
    # 获取图数据库连接
    graph_db = self.get_graph_db(st.session_state.shared['setting']['project_id'])
    
    # 获取LLM配置
    llm_config = get_llm_config(st.session_state.shared['setting']['llm_model_name'])
    
    # 创建CodexGraphAgentChat实例
    agent = CodexGraphAgentChat(
        llm=llm_config,
        prompt_path=prompt_path,
        schema_path=schema_path,
        task_id=st.session_state.shared['setting']['project_id'],
        graph_db=graph_db,
        max_iterations=max_iterations,
        message_callback=self.create_update_message()
    )
```

### 3. Agent执行阶段
```
CodexGraphAgentChat._run() → 多轮对话循环
```

**文件路径**: `modelscope_agent/agents/codexgraph_agent/task/code_chat.py:62-152`

## 🔍 原本流程 vs 现在流程对比

### 📊 原本流程 (CodexGraphAgentGeneral)

#### 流程特点:
1. **JSON格式驱动**: 使用JSON格式进行结构化响应
2. **固定动作类型**: 预定义的动作类型 (TEXT_QUERIES, ACTIONS等)
3. **单一循环**: 简单的查询-响应循环

#### 执行步骤:
```python
# 1. 初始化消息
messages = [
    {'role': 'system', 'content': self.system_prompts},
    {'role': 'user', 'content': primary_user_prompt}
]

# 2. 多轮对话循环
for iter in range(self.max_iterations):
    # 2.1 LLM调用
    response_text = self.llm_call(messages)
    
    # 2.2 解析JSON响应
    parsed_response, error_msg = extract_and_parse_json(response_text)
    thought, action, action_input = parsed_response.values()
    
    # 2.3 根据动作类型处理
    if action == 'TEXT_QUERIES':
        # 转换为Cypher查询
        cypher_queries = self.cypher_queries_template.substitute(text_queries=action_input)
        user_response = self.cypher_agent.run(cypher_queries)
    elif action == self.action_type:  # 如 'GENERATE_NEW_CODE'
        break  # 结束查询，开始生成
    
    # 2.4 更新消息历史
    messages.append({'role': 'user', 'content': user_response})

# 3. 最终生成
generate_queries = self.generate_queries_template.substitute(
    message=generate_msg, user_query=user_query)
answer = self.llm_call(messages)
```

#### 响应格式:
```json
{
    "thought": "分析用户问题...",
    "action": "TEXT_QUERIES",
    "action_input": "查找所有用户相关的方法"
}
```

### 🆕 现在流程 (CodexGraphAgentChat)

#### 流程特点:
1. **标记驱动**: 使用特殊标记进行内容提取
2. **灵活分析**: 支持分析、代码搜索、答案生成三个阶段
3. **智能判断**: 根据上下文智能决定是否需要继续搜索

#### 执行步骤:
```python
# 1. 初始化消息
user_query_issue = f'<questions>\n{user_query}\n<\\questions>\n'
messages = [
    {'role': 'system', 'content': self.system_prompts},
    {'role': 'user', 'content': user_query_issue},
    {'role': 'user', 'content': primary_user_prompt}
]

# 2. 多轮对话循环
for iter in range(self.max_iterations):
    # 2.1 LLM调用
    response_text = self.llm_call(messages)
    
    # 2.2 提取不同部分的内容
    extracted_analysis = extract_text_between_markers(
        response_text, '[start_of_analysis]', '[end_of_analysis]')
    extracted_code_search = extract_text_between_markers(
        response_text, '[start_of_code_search]', '[end_of_code_search]')
    answer_question = extract_text_between_markers(
        response_text, '[start_of_answer]', '[end_of_answer]')
    
    # 2.3 根据提取内容决定下一步
    if extracted_code_search:
        # 转换为Cypher查询并执行
        cypher_queries = self.cypher_queries_template.substitute(
            text_queries=extracted_code_search)
        user_response = self.cypher_agent.run(cypher_queries)
        messages.append({'role': 'user', 'content': user_response})
    elif answer_question:
        break  # 有答案了，结束循环
    
    # 2.4 继续分析或生成答案
    if iter < self.max_iterations - 1:
        msg = "Summarize your analysis first, and tell whether the current context is sufficient..."
        messages.append({'role': 'user', 'content': msg})

# 3. 最终答案生成
generate_queries = self.generate_queries_template.substitute(
    message='You are ready to do answer question.', user_query=user_query)
answer = self.generate(messages)
```

#### 响应格式:
```
[start_of_analysis]
详细分析用户问题...
[end_of_analysis]

[start_of_code_search]
### Text Query 1
查找所有用户认证相关的方法

### Text Query 2
获取用户模型的定义
[end_of_code_search]

[start_of_answer]
### Answer
- Analysis: 用户问题分析
- Conclusion: 结论
- Source code reference: 源代码引用
[end_of_answer]
```

## 🔧 核心组件详解

### 1. CypherAgent (图数据库查询代理)

**文件路径**: `modelscope_agent/agents/codexgraph_agent/cypher_agent.py`

#### 功能:
- 将自然语言查询转换为Cypher查询
- 执行图数据库查询
- 处理查询错误和重试

#### 工作流程:
```python
def _run(self, cypher_queries: str, retries: int = 5):
    # 1. 构建消息
    cypher_messages = [
        {'role': 'system', 'content': self.system_prompts},
        {'role': 'user', 'content': cypher_queries}
    ]
    
    # 2. 多轮重试循环
    while retry <= retries:
        # 2.1 LLM生成Cypher查询
        cypher_response = self.llm_call(cypher_messages)
        cyphers = extract_cypher_queries(cypher_response)
        
        # 2.2 执行每个Cypher查询
        for cypher in cyphers:
            cypher = add_label_to_nodes(cypher, f'`{self.task_id}`')
            cypher_response, flag = self.graph_db.execute_query_with_timeout(cypher)
            
            if not flag:  # 查询失败
                tmp_flag = False
        
        if tmp_flag:  # 所有查询成功
            break
        
        # 2.3 错误处理，要求重写查询
        cypher_messages.append({
            'role': 'user', 
            'content': 'Some Cypher statements may have syntax issues. Please correct them...'
        })
        retry += 1
```

### 2. 图数据库查询处理

#### 查询执行流程:
```python
# 1. 添加任务标签
cypher = add_label_to_nodes(cypher, f'`{task_id}`')

# 2. 执行查询
cypher_response, flag = self.graph_db.execute_query_with_timeout(cypher)

# 3. 处理响应
if cypher_response != 'cypher too complex, out of memory':
    cypher_response = [
        process_string(str(record)) for record in cypher_response
    ]
    if cypher_response:
        cypher_response = '\n\n'.join(cypher_response)
    else:
        cypher_response = 'Cypher query Return None'
```

### 3. 描述搜索功能 (新增)

#### 实现原理:
通过图数据库中的`description`属性进行模糊匹配搜索：

```cypher
// 搜索方法描述
MATCH (m:METHOD) 
WHERE m.description =~ '.*计算.*' 
RETURN m.name, m.description, m.code

// 搜索函数描述
MATCH (f:FUNCTION) 
WHERE f.description =~ '.*获取.*' 
RETURN f.name, f.description, f.code

// 搜索方法和函数
MATCH (n) 
WHERE (n:METHOD OR n:FUNCTION) AND n.description =~ '.*初始化.*' 
RETURN n.name, n.description, n.code, labels(n) as node_type
```

## 📈 流程对比总结

| 特性 | 原本流程 (General) | 现在流程 (Chat) |
|------|-------------------|-----------------|
| **响应格式** | JSON结构化 | 标记分隔 |
| **灵活性** | 固定动作类型 | 动态内容提取 |
| **分析能力** | 简单思考 | 详细分析+代码搜索+答案 |
| **错误处理** | 基础重试 | 智能判断+上下文感知 |
| **用户体验** | 技术导向 | 对话导向 |
| **扩展性** | 需要修改动作类型 | 通过标记轻松扩展 |

## 🎯 关键改进点

### 1. 更自然的对话流程
- **原本**: 严格的JSON格式，技术性强
- **现在**: 自然的标记格式，用户友好

### 2. 更智能的上下文管理
- **原本**: 简单的查询-响应循环
- **现在**: 分析-搜索-答案的三阶段处理

### 3. 更灵活的扩展机制
- **原本**: 需要修改代码添加新动作类型
- **现在**: 通过添加新标记即可扩展功能

### 4. 更好的错误恢复
- **原本**: 基础的重试机制
- **现在**: 智能判断是否需要继续搜索

## 💡 具体举例说明

### 场景：用户询问 "在仓库里实现计算功能的函数是哪一个？"

让我们通过一个完整的例子来展示整个调用流程：

#### 1. 用户输入阶段
```
用户输入: "在仓库里实现计算功能的函数是哪一个？"
↓
Streamlit界面接收输入
↓
CodeChatPage.run_agent() 被调用
```

#### 2. Agent初始化
```python
# 创建CodexGraphAgentChat实例
agent = CodexGraphAgentChat(
    llm=llm_config,  # DeepSeek-Coder模型
    graph_db=graph_db,  # Neo4j图数据库连接
    task_id="code_chat",
    max_iterations=5
)
```

#### 3. 第一轮对话 - 分析阶段

**输入消息**:
```
<questions>
在仓库里实现计算功能的函数是哪一个？
<\questions>

First, analyze the above given issue and current context. Your ultimate goal is to analyze user's question and answer it.
Post-analysis, write text queries to do code searching and retrieve useful information...
```

**LLM响应**:
```
[start_of_analysis]
用户询问仓库中实现计算功能的函数。需要搜索所有包含计算逻辑的函数，可能包括数学计算、数据处理、算法实现等。需要查找FUNCTION和METHOD节点中包含"计算"、"calculate"、"compute"等关键词的描述。
[end_of_analysis]

[start_of_code_search]
### Text Query 1
查找所有描述中包含"计算"关键词的函数和方法
[end_of_code_search]
```

#### 4. Cypher查询执行

**CypherAgent处理**:
```python
# 将文本查询转换为Cypher查询
cypher_queries = """
#### Text Queries:
查找所有描述中包含"计算"关键词的函数和方法

#### Task Instructions:
Your task is to decompose the given text queries into several simple ones...
"""

# 生成的Cypher查询
cypher_query = """
MATCH (n) 
WHERE (n:METHOD OR n:FUNCTION) AND n.description =~ '.*计算.*' 
RETURN n.name, n.description, n.code, labels(n) as node_type
"""
```

**图数据库执行结果**:
```
### Extracted Cypher query 0:
MATCH (n) 
WHERE (n:METHOD OR n:FUNCTION) AND n.description =~ '.*计算.*' 
RETURN n.name, n.description, n.code, labels(n) as node_type

### Response for Cypher query 0:
calculate_total_price|计算商品总价格，包括税费和折扣|def calculate_total_price(items, tax_rate, discount):\n    total = sum(item.price for item in items)\n    total_with_tax = total * (1 + tax_rate)\n    return total_with_tax * (1 - discount)|["FUNCTION"]

compute_statistics|计算数据统计信息，包括平均值、中位数等|def compute_statistics(data):\n    return {\n        'mean': sum(data) / len(data),\n        'median': sorted(data)[len(data)//2]\n    }|["FUNCTION"]
```

#### 5. 第二轮对话 - 答案生成

**输入消息** (包含查询结果):
```
Summarize your analysis first, and tell whether the current context is sufficient, 
write your summarization here: 
#### Concise Summarization:
通过搜索找到了2个包含计算功能的函数：calculate_total_price和compute_statistics。这些函数都包含"计算"关键词，符合用户需求。

Then if it's sufficient, please continue answering in the following format:
[start_of_answer]
### Answer
- Analysis: 用户询问仓库中实现计算功能的函数
- Conclusion: 找到了2个主要的计算函数
- Source code reference: calculate_total_price, compute_statistics
[end_of_answer]
```

**LLM最终响应**:
```
[start_of_answer]
### Answer
- Analysis: 用户询问仓库中实现计算功能的函数，通过描述搜索找到了相关的计算函数
- Conclusion: 仓库中主要有2个实现计算功能的函数：calculate_total_price（计算商品总价格）和compute_statistics（计算数据统计信息）
- Source code reference: 
  1. calculate_total_price: 计算商品总价格，包括税费和折扣
  2. compute_statistics: 计算数据统计信息，包括平均值、中位数等
[end_of_answer]
```

#### 6. 最终答案生成

**generate方法调用**:
```python
generate_queries = """
You are ready to do answer question. Please Answer Question:

### User's Requirements:
<questions>
在仓库里实现计算功能的函数是哪一个？
<\questions>

#### Final Output Format:
<answer>...</answer>
<analysis>...</analysis>
<reference>{{reference of source code 1}}</reference>
<reference>{{reference of source code 2}}</reference>
"""
```

**最终用户看到的答案**:
```
## answer: 
根据您的询问，我在仓库中找到了以下实现计算功能的函数：

1. **calculate_total_price** - 计算商品总价格
   - 功能：计算商品总价格，包括税费和折扣
   - 代码：`def calculate_total_price(items, tax_rate, discount): ...`

2. **compute_statistics** - 计算数据统计信息  
   - 功能：计算数据统计信息，包括平均值、中位数等
   - 代码：`def compute_statistics(data): ...`

## analysis: 
通过图数据库的描述搜索功能，我找到了所有描述中包含"计算"关键词的函数。这些函数都实现了不同的计算逻辑，满足您的需求。

## reference: 
calculate_total_price函数 - 位于utils/price_calculator.py
compute_statistics函数 - 位于utils/data_analyzer.py
```

### 🔍 流程关键点分析

#### 1. **智能分析阶段**
- LLM理解用户意图：寻找计算相关函数
- 生成搜索策略：通过描述关键词搜索

#### 2. **精确搜索阶段**  
- 将自然语言转换为Cypher查询
- 利用图数据库的模糊匹配能力
- 返回相关函数及其完整信息

#### 3. **智能判断阶段**
- 评估搜索结果是否充分
- 决定是否需要继续搜索或生成答案

#### 4. **答案生成阶段**
- 整合所有信息
- 生成用户友好的最终答案
- 提供源代码引用

### 🎯 这个例子的优势

1. **自然语言理解**: 用户用中文询问，系统能准确理解
2. **智能搜索**: 通过描述搜索找到相关函数，而不是依赖精确的函数名
3. **完整信息**: 返回函数名、描述、代码和位置信息
4. **用户友好**: 最终答案格式清晰，易于理解

## 🔮 未来发展方向

1. **多模态支持**: 支持图片、文档等多种输入
2. **实时协作**: 支持多用户同时使用
3. **个性化**: 根据用户习惯调整响应风格
4. **知识图谱**: 更丰富的代码关系建模
5. **自动化**: 更智能的代码分析和建议

## 📝 总结

CodexGraph Agent的调用流程经历了从**技术导向**到**用户导向**的转变：

- **原本流程**注重结构化和可预测性，适合技术用户
- **现在流程**注重自然对话和智能分析，适合普通用户

这种转变使得CodexGraph Agent能够更好地理解用户意图，提供更准确和有用的代码分析结果，同时保持了系统的可扩展性和稳定性。
