"""
快速测试脚本 - 验证方法签名修复
"""

import sys
from agents import (
    RequirementAnalyzer, 
    EngineeringAgent, 
    DesignAgent, 
    AIAgent, 
    QAAgent, 
    OperationAgent, 
    RiskAnalyzer
)

def test_method_signatures():
    """测试方法签名是否正确"""
    print("=" * 60)
    print("测试方法签名修复")
    print("=" * 60)
    
    # 创建模拟的API key（不需要真实key，只测试签名）
    mock_api_key = "test_key"
    
    try:
        # 测试DepartmentAgent子类的generate方法签名
        eng_agent = EngineeringAgent(mock_api_key, "test-model", "http://test.com")
        
        # 检查generate方法是否接受2个参数（raw_requirement, analysis）
        import inspect
        sig = inspect.signature(eng_agent.generate)
        params = list(sig.parameters.keys())
        print(f"\n✅ EngineeringAgent.generate 参数: {params}")
        assert 'raw_requirement' in params, "缺少 raw_requirement 参数"
        assert 'analysis' in params, "缺少 analysis 参数"
        print("   ✓ generate 方法签名正确")
        
        # 测试RiskAnalyzer.analyze方法签名
        risk_analyzer = RiskAnalyzer(mock_api_key, "test-model", "http://test.com")
        sig = inspect.signature(risk_analyzer.analyze)
        params = list(sig.parameters.keys())
        print(f"\n✅ RiskAnalyzer.analyze 参数: {params}")
        assert 'raw_requirement' in params, "缺少 raw_requirement 参数"
        assert 'analysis' in params, "缺少 analysis 参数"
        assert 'results' in params, "缺少 results 参数"
        print("   ✓ analyze 方法签名正确")
        
        print("\n" + "=" * 60)
        print("✅ 所有方法签名测试通过！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_method_signatures()
    sys.exit(0 if success else 1)
