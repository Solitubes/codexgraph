"""
测试方法描述生成功能
"""
import os
import sys
import json
from method_description_generator import MethodDescriptionGenerator, set_description_generator


def test_method_description_generator():
    """测试方法描述生成器"""
    
    # 创建测试配置
    test_config = {
        'model_name': 'deepseek-coder',
        'api_key': os.getenv('OPENAI_API_KEY', ''),
        'base_url': os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
        'max_tokens': 200,
        'temperature': 0.3
    }
    
    # 创建描述生成器
    generator = MethodDescriptionGenerator(test_config)
    set_description_generator(generator)
    
    # 测试用例
    test_methods = [
        {
            'method_name': 'add',
            'method_code': '''def add(self, amount):
    """Add amount to the current value"""
    self.value += amount
    return self.value''',
            'class_name': 'Calculator',
            'file_path': 'calculator.py'
        },
        {
            'method_name': '__init__',
            'method_code': '''def __init__(self, initial_value=0):
    """Initialize calculator with initial value"""
    self.value = initial_value''',
            'class_name': 'Calculator',
            'file_path': 'calculator.py'
        },
        {
            'method_name': 'calculate_circle_area',
            'method_code': '''def calculate_circle_area(self, radius):
    """Calculate the area of a circle"""
    return 3.14159 * radius * radius''',
            'class_name': 'MathUtils',
            'file_path': 'math_utils.py'
        }
    ]
    
    print("开始测试方法描述生成...")
    
    for i, method in enumerate(test_methods, 1):
        print(f"\n测试用例 {i}:")
        print(f"方法名: {method['method_name']}")
        print(f"类名: {method['class_name']}")
        print(f"代码:\n{method['method_code']}")
        
        # 生成描述
        description = generator.generate_method_description(
            method_code=method['method_code'],
            method_name=method['method_name'],
            class_name=method['class_name'],
            file_path=method['file_path']
        )
        
        print(f"生成的描述: {description}")
        print("-" * 50)
    
    # 测试批量生成
    print("\n测试批量生成...")
    descriptions = generator.batch_generate_descriptions(test_methods)
    
    print("批量生成结果:")
    for method_name, description in descriptions.items():
        print(f"{method_name}: {description}")
    
    # 保存缓存
    generator.save_cache("test_method_descriptions_cache.json")
    print("\n缓存已保存到 test_method_descriptions_cache.json")


def test_with_real_code():
    """使用真实代码测试"""
    
    # 模拟一个真实的Python类
    real_code = '''
class AdvancedCalculator:
    def __init__(self, initial_value=0):
        self.value = initial_value
        self.history = []
    
    def add(self, amount):
        """Add amount to current value and record in history"""
        self.value += amount
        self.history.append(f"Added {amount}")
        return self.value
    
    def multiply(self, factor):
        """Multiply current value by factor"""
        self.value *= factor
        self.history.append(f"Multiplied by {factor}")
        return self.value
    
    def get_history(self):
        """Get calculation history"""
        return self.history.copy()
    
    def reset(self):
        """Reset calculator to initial state"""
        self.value = 0
        self.history.clear()
'''
    
    # 提取方法进行测试
    import ast
    
    tree = ast.parse(real_code)
    methods = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # 获取方法的源代码行
            method_code = ast.get_source_segment(real_code, node)
            if method_code:
                methods.append({
                    'method_name': node.name,
                    'method_code': method_code,
                    'class_name': 'AdvancedCalculator',
                    'file_path': 'advanced_calculator.py'
                })
    
    print("使用真实代码测试:")
    print("=" * 60)
    
    generator = MethodDescriptionGenerator()
    
    for method in methods:
        print(f"\n方法: {method['method_name']}")
        print(f"代码:\n{method['method_code']}")
        
        description = generator.generate_method_description(
            method_code=method['method_code'],
            method_name=method['method_name'],
            class_name=method['class_name'],
            file_path=method['file_path']
        )
        
        print(f"描述: {description}")
        print("-" * 40)


if __name__ == "__main__":
    print("CodexGraph 方法描述生成测试")
    print("=" * 50)
    
    # 基础测试
    test_method_description_generator()
    
    print("\n" + "=" * 50)
    
    # 真实代码测试
    test_with_real_code()
    
    print("\n测试完成！")
