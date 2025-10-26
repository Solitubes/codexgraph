"""
增强的图数据库构建示例 - 包含方法描述生成
"""
import os
import sys
import json
from my_graph_db import GraphDatabaseHandler
from method_description_generator import MethodDescriptionGenerator, set_description_generator


def enhanced_build_graph_database(repo_path: str, task_id: str, llm_config: dict = None):
    """
    增强的图数据库构建函数，包含方法描述生成
    
    Args:
        repo_path: 代码仓库路径
        task_id: 任务ID
        llm_config: 大模型配置
    """
    
    # 1. 初始化图数据库连接
    graph_db = GraphDatabaseHandler(
        uri='bolt://localhost:7687',
        user='neo4j',
        password='your_password',
        database_name='neo4j',
        task_id=task_id,
        use_lock=True,
    )
    
    # 2. 配置大模型描述生成器
    if llm_config:
        description_generator = MethodDescriptionGenerator(llm_config)
    else:
        # 使用默认配置
        description_generator = MethodDescriptionGenerator()
    
    set_description_generator(description_generator)
    
    # 3. 加载现有缓存（如果有）
    cache_file = f"method_descriptions_cache_{task_id}.json"
    if os.path.exists(cache_file):
        description_generator.load_cache(cache_file)
        print(f"已加载缓存文件: {cache_file}")
    
    # 4. 执行原有的图数据库构建流程
    # 这里会调用原有的 build_graph_database 函数
    # 在构建过程中，METHOD节点会自动生成描述
    
    print("开始构建增强的图数据库...")
    print(f"仓库路径: {repo_path}")
    print(f"任务ID: {task_id}")
    print(f"大模型配置: {llm_config}")
    
    # 5. 保存描述缓存
    description_generator.save_cache(cache_file)
    print(f"描述缓存已保存到: {cache_file}")
    
    return graph_db


def query_methods_with_descriptions(graph_db: GraphDatabaseHandler, task_id: str):
    """
    查询带有描述的方法节点
    
    Args:
        graph_db: 图数据库连接
        task_id: 任务ID
    """
    
    # 查询所有METHOD节点及其描述
    query = f"""
    MATCH (m:METHOD:`{task_id}`)
    WHERE exists(m.description)
    RETURN m.name as method_name, 
           m.class as class_name,
           m.description as description,
           m.file_path as file_path
    ORDER BY m.class, m.name
    """
    
    results = graph_db.execute_query(query)
    
    print(f"\n找到 {len(results)} 个带有描述的方法:")
    print("=" * 80)
    
    for result in results:
        print(f"类: {result['class_name']}")
        print(f"方法: {result['method_name']}")
        print(f"文件: {result['file_path']}")
        print(f"描述: {result['description']}")
        print("-" * 40)


def update_existing_methods_with_descriptions(graph_db: GraphDatabaseHandler, task_id: str, llm_config: dict = None):
    """
    为现有的METHOD节点添加描述
    
    Args:
        graph_db: 图数据库连接
        task_id: 任务ID
        llm_config: 大模型配置
    """
    
    # 查询所有没有描述的METHOD节点
    query = f"""
    MATCH (m:METHOD:`{task_id}`)
    WHERE NOT exists(m.description)
    RETURN m.full_name as full_name,
           m.name as method_name,
           m.class as class_name,
           m.code as method_code,
           m.file_path as file_path
    """
    
    results = graph_db.execute_query(query)
    
    if not results:
        print("所有METHOD节点都已经有描述了")
        return
    
    print(f"找到 {len(results)} 个需要添加描述的METHOD节点")
    
    # 配置描述生成器
    if llm_config:
        description_generator = MethodDescriptionGenerator(llm_config)
    else:
        description_generator = MethodDescriptionGenerator()
    
    # 批量生成描述
    methods_to_process = []
    for result in results:
        methods_to_process.append({
            'method_name': result['method_name'],
            'method_code': result['method_code'],
            'class_name': result['class_name'],
            'file_path': result['file_path']
        })
    
    print("开始批量生成描述...")
    descriptions = description_generator.batch_generate_descriptions(methods_to_process)
    
    # 更新图数据库
    updated_count = 0
    for result in results:
        full_name = result['full_name']
        method_name = result['method_name']
        
        if method_name in descriptions:
            description = descriptions[method_name]
            
            # 更新节点
            graph_db.update_node(
                full_name=full_name,
                parms={'description': description}
            )
            updated_count += 1
            print(f"已更新: {full_name} -> {description}")
    
    print(f"\n成功更新了 {updated_count} 个METHOD节点的描述")


def main():
    """主函数 - 演示完整的使用流程"""
    
    # 配置参数
    repo_path = "/path/to/your/code/repo"  # 替换为实际的代码仓库路径
    task_id = "enhanced_test_001"
    
    # 大模型配置
    llm_config = {
        'model_name': 'deepseek-coder',
        'api_key': os.getenv('OPENAI_API_KEY', ''),
        'base_url': os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
        'max_tokens': 200,
        'temperature': 0.3
    }
    
    print("CodexGraph 增强构建示例")
    print("=" * 50)
    
    try:
        # 1. 构建增强的图数据库
        graph_db = enhanced_build_graph_database(repo_path, task_id, llm_config)
        
        # 2. 查询带有描述的方法
        query_methods_with_descriptions(graph_db, task_id)
        
        # 3. 为现有方法添加描述（如果需要）
        # update_existing_methods_with_descriptions(graph_db, task_id, llm_config)
        
        print("\n增强构建完成！")
        
    except Exception as e:
        print(f"构建过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
