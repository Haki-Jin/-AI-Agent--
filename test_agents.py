"""
简单测试脚本 - 验证Agent基本功能
注意: 需要有效的OpenAI API Key才能运行
"""

import os
from agents import RequirementAnalyzer, EngineeringAgent, RiskAnalyzer


def test_basic_import():
    """测试模块导入"""
    print("✅ 测试1: 模块导入")
    try:
        from agents import (
            BaseAgent,
            RequirementAnalyzer,
            EngineeringAgent,
            DesignAgent,
            AIAgent,
            QAAgent,
            OperationAgent,
            RiskAnalyzer
        )
        print("   ✓ 所有Agent类导入成功")
        return True
    except Exception as e:
        print(f"   ✗ 导入失败: {e}")
        return False


def test_agent_initialization(api_key):
    """测试Agent初始化"""
    print("\n✅ 测试2: Agent初始化")
    try:
        analyzer = RequirementAnalyzer(api_key, "gpt-3.5-turbo")
        eng_agent = EngineeringAgent(api_key, "gpt-3.5-turbo")
        risk_agent = RiskAnalyzer(api_key, "gpt-3.5-turbo")
        print("   ✓ Agent初始化成功")
        return True
    except Exception as e:
        print(f"   ✗ 初始化失败: {e}")
        return False


def test_requirement_analysis(api_key):
    """测试需求解析功能"""
    print("\n✅ 测试3: 需求解析")
    try:
        analyzer = RequirementAnalyzer(api_key, "gpt-3.5-turbo")
        
        test_requirement = "做一个待办事项应用，用户可以添加、删除、标记完成的任务"
        result = analyzer.analyze(test_requirement)
        
        print(f"   ✓ 解析成功")
        print(f"   - 目标: {result.get('goal', 'N/A')[:50]}...")
        print(f"   - 用户: {result.get('users', 'N/A')[:50]}...")
        print(f"   - 功能点: {result.get('core_features', 'N/A')[:50]}...")
        return True
    except Exception as e:
        print(f"   ✗ 解析失败: {e}")
        return False


def test_engineering_generation(api_key):
    """测试研发版本生成"""
    print("\n✅ 测试4: 研发版本生成")
    try:
        analyzer = RequirementAnalyzer(api_key, "gpt-3.5-turbo")
        eng_agent = EngineeringAgent(api_key, "gpt-3.5-turbo")
        
        test_requirement = "做一个待办事项应用"
        analysis = analyzer.analyze(test_requirement)
        result = eng_agent.generate(test_requirement, analysis)
        
        print(f"   ✓ 生成成功")
        print(f"   - 长度: {len(result)} 字符")
        print(f"   - 前100字符: {result[:100]}...")
        return True
    except Exception as e:
        print(f"   ✗ 生成失败: {e}")
        return False


def test_utils():
    """测试工具函数"""
    print("\n✅ 测试5: 工具函数")
    try:
        from utils import format_output, create_example_cases, calculate_token_usage
        
        # 测试format_output
        formatted = format_output("测试文本")
        assert formatted == "测试文本"
        
        # 测试create_example_cases
        cases = create_example_cases()
        assert len(cases) == 3
        
        # 测试calculate_token_usage
        tokens = calculate_token_usage("这是一个测试")
        assert tokens > 0
        
        print("   ✓ 所有工具函数正常")
        return True
    except Exception as e:
        print(f"   ✗ 工具函数测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("  需求转译AI Agent - 测试套件")
    print("=" * 60)
    
    # 测试1: 导入
    if not test_basic_import():
        print("\n❌ 基础导入失败，终止测试")
        return False
    
    # 测试5: 工具函数（不需要API Key）
    if not test_utils():
        print("\n⚠️  工具函数测试失败，但不影响主要功能")
    
    # 获取API Key
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print("\n⚠️  未检测到OPENAI_API_KEY环境变量")
        api_key = input("请输入OpenAI API Key以继续测试（直接回车跳过）: ").strip()
    
    if not api_key:
        print("\n⚠️  跳过需要API Key的测试")
        print("\n" + "=" * 60)
        print("  测试完成（部分测试已跳过）")
        print("=" * 60)
        return True
    
    # 测试2-4: 需要API Key
    results = []
    results.append(test_agent_initialization(api_key))
    results.append(test_requirement_analysis(api_key))
    results.append(test_engineering_generation(api_key))
    
    print("\n" + "=" * 60)
    if all(results):
        print("  ✅ 所有测试通过！")
    else:
        print("  ⚠️  部分测试失败，请检查API Key和网络连接")
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    run_all_tests()
