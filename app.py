import streamlit as st
from agents import RequirementAnalyzer, EngineeringAgent, DesignAgent, AIAgent, QAAgent, OperationAgent, RiskAnalyzer
from utils import format_output, create_example_cases

# 页面配置
st.set_page_config(
    page_title="需求转译AI Agent",
    page_icon="🤖",
    layout="wide"
)

# 标题和介绍
st.title("🤖 面向跨部门协作的需求转译AI Agent")

# 添加简介卡片
st.markdown("""
<div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
<h3 style='margin-top: 0;'>💡 这是什么？</h3>
<p>这是一个AI辅助需求转译器，能将产品经理的原始需求自动转译为不同部门的专属版本。</p>
<p><strong>解决的问题：</strong>同一份需求，研发、设计、算法、测试、运营关注点完全不同。本工具自动为每个部门生成定制化文档。</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
### 解决什么问题？
同一份产品需求，不同部门关注点完全不同。本工具自动将原始需求转译为各部门专属版本。
""")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置/")
    
    # API配置
    api_provider = st.selectbox(
        "选择API提供商",
        ["DeepSeek", "豆包(Doubao)", "通义千问(Qwen)", "自定义OpenAI兼容API"],
        index=0
    )
    
    api_key = st.text_input("API Key", type="password", 
                           help="请输入你的API Key")
    
    # 根据不同提供商显示不同的base_url和模型选项
    if api_provider == "DeepSeek":
        base_url = st.text_input("Base URL", value="https://api.deepseek.com/v1", help="DeepSeek API地址")
        model_choice = st.selectbox(
            "选择模型",
            ["deepseek-chat", "deepseek-reasoner"],
            index=0
        )
    elif api_provider == "豆包(Doubao)":
        base_url = st.text_input("Base URL", value="https://ark.cn-beijing.volces.com/api/v3", help="豆包API地址")
        model_choice = st.selectbox(
            "选择模型",
            ["doubao-pro-32k", "doubao-lite-32k", "doubao-pro-128k"],
            index=0
        )
    elif api_provider == "通义千问(Qwen)":
        base_url = st.text_input("Base URL", value="https://dashscope.aliyuncs.com/compatible-mode/v1", help="通义千问API地址")
        model_choice = st.selectbox(
            "选择模型",
            ["qwen-plus", "qwen-turbo", "qwen-max"],
            index=0
        )
    else:  # 自定义
        base_url = st.text_input("Base URL", value="https://api.openai.com/v1", help="自定义API地址")
        model_choice = st.text_input("模型名称", value="gpt-4")
    
    st.divider()
    
    # 示例案例
    st.header("📋 示例案例")
    example_case = st.selectbox(
        "选择示例需求",
        ["自定义输入", "会议纪要AI功能", "智能客服系统", "个性化推荐引擎"]
    )
    
    if example_case != "自定义输入":
        examples = create_example_cases()
        st.info(f"**{example_case}**\n\n{examples[example_case]}")

# 主区域
st.divider()

# Step 1: 输入原始需求
st.header("📝 Step 1: 输入原始需求")
col1, col2 = st.columns([3, 1])

with col1:
    if example_case == "自定义输入":
        default_text = ""
    else:
        examples = create_example_cases()
        default_text = examples[example_case]
    
    raw_requirement = st.text_area(
        "产品经理的原始需求描述",
        value=default_text,
        height=150,
        placeholder="例如：我们希望做一个会议纪要 AI 功能，用户上传录音后，系统可以自动转写、提炼重点、输出待办事项..."
    )

with col2:
    st.markdown("### 💡 提示")
    st.markdown("""
    - 尽量详细描述功能
    - 包含目标用户
    - 说明核心价值
    - 提及关键约束
    """)

# Step 2: 开始分析按钮
st.divider()
if st.button("🚀 开始需求转译", type="primary", use_container_width=True):
    if not raw_requirement.strip():
        st.error("请输入原始需求描述！")
    elif not api_key:
        st.error("请在侧边栏输入OpenAI API Key！")
    else:
        with st.spinner("正在初始化Agent..."):
            # 初始化所有Agent
            analyzer = RequirementAnalyzer(api_key, model_choice, base_url)
            engineering_agent = EngineeringAgent(api_key, model_choice, base_url)
            design_agent = DesignAgent(api_key, model_choice, base_url)
            ai_agent = AIAgent(api_key, model_choice, base_url)
            qa_agent = QAAgent(api_key, model_choice, base_url)
            operation_agent = OperationAgent(api_key, model_choice, base_url)
            risk_analyzer = RiskAnalyzer(api_key, model_choice, base_url)
        
        # Step 2: 总控Agent解析需求
        st.header("🔍 Step 2: 需求解析结果")
        with st.spinner("总控Agent正在解析需求..."):
            analysis_result = analyzer.analyze(raw_requirement)
        
        # 展示解析结果
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**需求目标**\n\n{format_output(analysis_result.get('goal', 'N/A'))}")
        with col2:
            st.info(f"**目标用户**\n\n{format_output(analysis_result.get('users', 'N/A'))}")
        with col3:
            st.info(f"**核心功能点**\n\n{format_output(analysis_result.get('core_features', 'N/A'))}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.warning(f"**不明确点**\n\n{format_output(analysis_result.get('unclear_points', '无明显不明确点'))}")
        with col2:
            st.warning(f"**依赖模块**\n\n{format_output(analysis_result.get('dependencies', '无明显依赖'))}")
        
        st.success("✅ 需求解析完成！")
        
        # Step 3: 分发给不同角色Agent
        st.divider()
        st.header("🎯 Step 3: 各部门需求转译")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = {}
        
        # 研发版本
        status_text.text("正在生成研发版本...")
        with st.spinner("Engineering Agent 工作中..."):
            results['engineering'] = engineering_agent.generate(raw_requirement, analysis_result)
        progress_bar.progress(20)
        
        # 设计版本
        status_text.text("正在生成设计版本...")
        with st.spinner("Design Agent 工作中..."):
            results['design'] = design_agent.generate(raw_requirement, analysis_result)
        progress_bar.progress(40)
        
        # 算法/AI版本
        status_text.text("正在生成算法/AI版本...")
        with st.spinner("AI/Algorithm Agent 工作中..."):
            results['ai'] = ai_agent.generate(raw_requirement, analysis_result)
        progress_bar.progress(60)
        
        # 测试版本
        status_text.text("正在生成测试版本...")
        with st.spinner("QA Agent 工作中..."):
            results['qa'] = qa_agent.generate(raw_requirement, analysis_result)
        progress_bar.progress(80)
        
        # 运营/业务版本
        status_text.text("正在生成运营/业务版本...")
        with st.spinner("Operation Agent 工作中..."):
            results['operation'] = operation_agent.generate(raw_requirement, analysis_result)
        progress_bar.progress(90)
        
        # 风险分析
        status_text.text("正在进行风险评估...")
        with st.spinner("Risk Analyzer 工作中..."):
            results['risk'] = risk_analyzer.analyze(raw_requirement, analysis_result, results)
        progress_bar.progress(100)
        
        status_text.text("✅ 所有Agent工作完成！")
        
        # Step 4: 统一汇总展示
        st.divider()
        st.header("📊 Step 4: 转译结果汇总")
        
        # 使用标签页展示各部门版本
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🔧 研发版本",
            "🎨 设计版本",
            "🤖 算法/AI版本",
            "🧪 测试版本",
            "📈 运营/业务版本",
            "⚠️ 风险提醒"
        ])
        
        with tab1:
            st.subheader("给研发的版本")
            formatted_engineering = format_output(results['engineering'])
            st.markdown(formatted_engineering)
            st.download_button(
                label="📥 下载研发版本",
                data=formatted_engineering,
                file_name="engineering_requirement.md",
                mime="text/markdown"
            )
        
        with tab2:
            st.subheader("给设计的版本")
            formatted_design = format_output(results['design'])
            st.markdown(formatted_design)
            st.download_button(
                label="📥 下载设计版本",
                data=formatted_design,
                file_name="design_requirement.md",
                mime="text/markdown"
            )
        
        with tab3:
            st.subheader("给算法/AI的版本")
            formatted_ai = format_output(results['ai'])
            st.markdown(formatted_ai)
            st.download_button(
                label="📥 下载算法/AI版本",
                data=formatted_ai,
                file_name="ai_requirement.md",
                mime="text/markdown"
            )
        
        with tab4:
            st.subheader("给测试的版本")
            formatted_qa = format_output(results['qa'])
            st.markdown(formatted_qa)
            st.download_button(
                label="📥 下载测试版本",
                data=formatted_qa,
                file_name="qa_requirement.md",
                mime="text/markdown"
            )
        
        with tab5:
            st.subheader("给运营/业务的版本")
            formatted_operation = format_output(results['operation'])
            st.markdown(formatted_operation)
            st.download_button(
                label="📥 下载运营/业务版本",
                data=formatted_operation,
                file_name="operation_requirement.md",
                mime="text/markdown"
            )
        
        with tab6:
            st.subheader("风险提醒与建议")
            
            # 确保risk结果是字典类型
            if isinstance(results.get('risk'), dict):
                # 不明确表达
                if results['risk'].get('unclear_expressions'):
                    st.error("❌ 表达不够明确的地方")
                    for item in results['risk']['unclear_expressions']:
                        st.warning(f"- {item}")
                
                # 需要补充的信息
                if results['risk'].get('needs_supplement'):
                    st.warning("⚠️ 需要产品经理补充的信息")
                    for item in results['risk']['needs_supplement']:
                        st.info(f"- {item}")
                
                # 跨部门理解偏差风险
                if results['risk'].get('cross_dept_risks'):
                    st.error("🔴 跨部门理解偏差风险")
                    for item in results['risk']['cross_dept_risks']:
                        st.error(f"- {item}")
                
                # 推荐下一步动作
                if results['risk'].get('next_steps'):
                    st.success("✅ 推荐的下一步动作")
                    for item in results['risk']['next_steps']:
                        st.success(f"- {item}")
            else:
                st.warning("⚠️ 风险分析结果格式异常")
            
            st.download_button(
                label="📥 下载风险分析报告",
                data=format_output(results['risk']),
                file_name="risk_analysis.md",
                mime="text/markdown"
            )
        
        # 实验对比（可选）
        st.divider()
        st.header("🧪 实验对比（选做）")
        st.info("💡 提示：可以在这里添加不同Prompt版本的对比实验，或者展示多个需求案例的转译效果差异。")
        
        # 批判性思考
        st.divider()
        st.header("💭 批判性思考")
        st.markdown("""
        **当前实现的局限性：**
        
        1. ⚠️ LLM可能"编造研发约束" - 生成的技术细节可能不准确
        2. ⚠️ 不同部门语气模板化 - 未必贴近真实团队风格
        3. ⚠️ 风险提示可能漏掉隐性依赖 - 依赖完整的需求解析质量
        4. ⚠️ 多Agent看似专业，但本质仍依赖总控解析质量
        
        **改进方向：**
        - 引入领域知识库验证技术可行性
        - 收集真实团队反馈优化Prompt
        - 增加人工审核环节
        - 建立历史需求数据库进行对比学习
        """)

# 底部说明
st.divider()
st.markdown("""
---
**技术架构**: Streamlit + 国内大模型(DeepSeek/豆包/通义千问) + Multi-Agent Workflow  
**核心机制**: Prompt驱动的角色条件生成  
**适用场景**: 产品需求文档自动化分发、跨部门协作效率提升
""")
