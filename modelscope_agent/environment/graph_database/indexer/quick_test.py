"""
快速测试方法描述生成功能
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from method_description_generator import MethodDescriptionGenerator


def quick_test():
    """快速测试功能"""
    
    print("CodexGraph 方法描述生成 - 快速测试")
    print("=" * 50)
    
    # 创建描述生成器（使用模拟模式）
    generator = MethodDescriptionGenerator({
        'model_name': 'mock',  # 使用模拟模式，不需要真实API
        'api_key': 'test'
    })
    
    # 测试用例
    test_cases = [
        {
            'name': '构造函数',
            'code': '''def __init__(self, initial_value=0):
    """Initialize calculator with initial value"""
    self.value = initial_value
    self.history = []''',
            'class': 'Calculator'
        },
        {
            'name': '加法方法',
            'code': '''def add(self, amount):
    """Add amount to current value"""
    self.value += amount
    return self.value''',
            'class': 'Calculator'
        },
        {
            'name': '计算方法',
            'code': '''def calculate_area(self, radius):
    """Calculate circle area"""
    return 3.14159 * radius * radius''',
            'class': 'MathUtils'
        },
        {
            'name': '获取方法',
            'code': '''def get_value(self):
    """Get current value"""
    return self.value''',
            'class': 'Calculator'
        }
    ]
    
    print("开始测试...")
    print()
    
    for i, case in enumerate(test_cases, 1):
        print(f"测试 {i}: {case['name']}")
        print(f"类: {case['class']}")
        print(f"代码:\n{case['code']}")
        
        # 生成描述
        description = generator.generate_method_description(
            method_code=case['code'],
            method_name=case['name'],
            class_name=case['class'],
            file_path='test.py'
        )
        
        print(f"生成的描述: {description}")
        print("-" * 50)
        print()
    
    print("测试完成！")
    print("\n要使用真实的大模型API，请:")
    print("1. 设置环境变量: export OPENAI_API_KEY='your-api-key'")
    print("2. 修改配置使用真实的模型名称")
    print("3. 运行 python test_method_description.py")


if __name__ == "__main__":
    quick_test()
