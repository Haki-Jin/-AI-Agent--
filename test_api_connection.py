"""
测试国内大模型API连接
支持: DeepSeek, 豆包, 通义千问等
"""

import openai


def test_api_connection(api_key: str, base_url: str, model: str, provider_name: str):
    """测试API连接"""
    print(f"\n{'='*60}")
    print(f"  测试 {provider_name} API 连接")
    print(f"{'='*60}")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print(f"{'='*60}\n")
    
    try:
        # 创建客户端
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        
        # 发送测试请求
        print("📤 发送测试请求...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个助手，请用简短的语言回复。"},
                {"role": "user", "content": "你好，请回复'连接成功'"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        # 获取回复
        reply = response.choices[0].message.content.strip()
        
        print(f"✅ 连接成功！")
        print(f"📥 AI回复: {reply}")
        
        # 显示使用信息
        if hasattr(response, 'usage'):
            print(f"\n📊 使用情况:")
            print(f"   Prompt Tokens: {response.usage.prompt_tokens}")
            print(f"   Completion Tokens: {response.usage.completion_tokens}")
            print(f"   Total Tokens: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ 连接失败！")
        print(f"错误信息: {str(e)}")
        print("\n可能的原因:")
        print("1. API Key不正确或已过期")
        print("2. Base URL地址错误")
        print("3. 网络连接问题")
        print("4. 账户余额不足")
        print("5. 模型名称不正确")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  国内大模型API连接测试工具")
    print("="*60)
    
    # 选择提供商
    print("\n请选择API提供商:")
    print("1. DeepSeek")
    print("2. 豆包 (Doubao)")
    print("3. 通义千问 (Qwen)")
    print("4. 自定义")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    # 配置参数
    configs = {
        "1": {
            "name": "DeepSeek",
            "base_url": "https://api.deepseek.com/v1",
            "models": ["deepseek-chat", "deepseek-reasoner"]
        },
        "2": {
            "name": "豆包 (Doubao)",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "models": ["doubao-pro-32k", "doubao-lite-32k", "doubao-pro-128k"]
        },
        "3": {
            "name": "通义千问 (Qwen)",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "models": ["qwen-plus", "qwen-turbo", "qwen-max"]
        },
        "4": {
            "name": "自定义",
            "base_url": None,
            "models": []
        }
    }
    
    if choice not in configs:
        print("❌ 无效选项")
        return
    
    config = configs[choice]
    
    # 获取配置
    api_key = input("请输入API Key: ").strip()
    
    if config["base_url"]:
        base_url_input = input(f"Base URL (默认: {config['base_url']}): ").strip()
        base_url = base_url_input if base_url_input else config["base_url"]
    else:
        base_url = input("请输入Base URL: ").strip()
    
    if config["models"]:
        print(f"\n可用模型:")
        for i, model in enumerate(config["models"], 1):
            print(f"{i}. {model}")
        model_choice = input(f"\n选择模型 (1-{len(config['models'])}, 默认: 1): ").strip()
        if model_choice.isdigit() and 1 <= int(model_choice) <= len(config["models"]):
            model = config["models"][int(model_choice) - 1]
        else:
            model = config["models"][0]
    else:
        model = input("请输入模型名称: ").strip()
    
    # 测试连接
    success = test_api_connection(api_key, base_url, model, config["name"])
    
    if success:
        print("\n" + "="*60)
        print("  ✅ 测试通过！可以正常使用该API")
        print("="*60)
        print("\n在Streamlit应用中配置:")
        print(f"  - API提供商: {config['name']}")
        print(f"  - Base URL: {base_url}")
        print(f"  - 模型: {model}")
        print(f"  - API Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("\n" + "="*60)
        print("  ❌ 测试失败，请检查配置")
        print("="*60)


if __name__ == "__main__":
    main()
