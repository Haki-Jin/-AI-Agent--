import json
from typing import Dict, List

import streamlit as st

from agents import RequirementAnalyzer, EngineeringAgent, DesignAgent, AIAgent, QAAgent, OperationAgent, RiskAnalyzer
from utils import format_output, create_example_cases, extract_text_from_docx


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="需求转译 AI Workspace",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# UI helpers
# -----------------------------
def inject_css():
    st.markdown(
        """
        <style>
        :root {
            --bg: #f7f8fc;
            --card: rgba(255,255,255,0.82);
            --line: rgba(15, 23, 42, 0.08);
            --text: #0f172a;
            --muted: #667085;
            --accent: #4f46e5;
            --accent-2: #7c3aed;
            --ok: #16a34a;
            --warn: #d97706;
            --danger: #dc2626;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(99,102,241,0.12), transparent 28%),
                radial-gradient(circle at top right, rgba(168,85,247,0.10), transparent 24%),
                linear-gradient(180deg, #f8faff 0%, #f5f7fb 100%);
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }

        .hero {
            background: linear-gradient(135deg, rgba(79,70,229,0.95), rgba(124,58,237,0.92));
            color: white;
            padding: 1.35rem 1.5rem;
            border-radius: 24px;
            border: 1px solid rgba(255,255,255,0.18);
            box-shadow: 0 18px 60px rgba(79,70,229,0.18);
            margin-bottom: 1rem;
        }

        .hero h1 {
            margin: 0;
            font-size: 1.8rem;
            line-height: 1.2;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .hero p {
            margin: 0.55rem 0 0 0;
            opacity: 0.92;
            font-size: 0.96rem;
        }

        .glass-card {
            background: var(--card);
            border: 1px solid var(--line);
            backdrop-filter: blur(10px);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 32px rgba(15,23,42,0.06);
            margin-bottom: 0.9rem;
        }

        .section-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.7rem;
        }

        .section-title h3 {
            margin: 0;
            font-size: 1.05rem;
            color: var(--text);
            letter-spacing: -0.01em;
        }

        .subtle {
            color: var(--muted);
            font-size: 0.92rem;
        }

        .metric-card {
            background: rgba(255,255,255,0.92);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            min-height: 94px;
            box-shadow: 0 8px 24px rgba(15,23,42,0.05);
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.82rem;
            margin-bottom: 0.25rem;
        }

        .metric-value {
            color: var(--text);
            font-weight: 800;
            font-size: 1.5rem;
            line-height: 1.1;
        }

        .metric-desc {
            margin-top: 0.35rem;
            color: var(--muted);
            font-size: 0.82rem;
        }

        .chip-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.45rem;
        }

        .chip {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.36rem 0.68rem;
            border-radius: 999px;
            background: rgba(79,70,229,0.08);
            color: #4338ca;
            border: 1px solid rgba(79,70,229,0.12);
            font-size: 0.83rem;
            font-weight: 600;
        }

        .chip.warn {
            background: rgba(245, 158, 11, 0.10);
            color: #b45309;
            border-color: rgba(245,158,11,0.18);
        }

        .chip.ok {
            background: rgba(34,197,94,0.09);
            color: #15803d;
            border-color: rgba(34,197,94,0.18);
        }

        .assistant-bubble {
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,252,0.92));
            border: 1px solid var(--line);
            border-radius: 20px 20px 20px 8px;
            padding: 0.95rem 1rem;
            box-shadow: 0 10px 24px rgba(15,23,42,0.05);
            margin-bottom: 0.75rem;
        }

        .assistant-tag {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            background: rgba(79,70,229,0.10);
            color: #4338ca;
            font-size: 0.74rem;
            font-weight: 700;
            margin-bottom: 0.55rem;
        }

        .stepper {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.65rem;
            margin: 0.8rem 0 1.1rem 0;
        }

        .step {
            border-radius: 18px;
            padding: 0.8rem 0.9rem;
            border: 1px solid var(--line);
            background: rgba(255,255,255,0.80);
            min-height: 82px;
        }

        .step.active {
            border-color: rgba(79,70,229,0.20);
            background: linear-gradient(180deg, rgba(79,70,229,0.08), rgba(255,255,255,0.94));
            box-shadow: 0 10px 24px rgba(79,70,229,0.10);
        }

        .step.done {
            background: linear-gradient(180deg, rgba(34,197,94,0.08), rgba(255,255,255,0.96));
        }

        .step-num {
            font-weight: 800;
            font-size: 0.8rem;
            color: var(--muted);
            margin-bottom: 0.18rem;
        }

        .step-title {
            font-weight: 700;
            color: var(--text);
            margin-bottom: 0.14rem;
        }

        .step-desc {
            color: var(--muted);
            font-size: 0.8rem;
            line-height: 1.35;
        }

        .mini-kv {
            background: rgba(248,250,252,0.9);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 0.75rem 0.85rem;
            height: 100%;
        }

        .mini-kv-title {
            font-size: 0.8rem;
            color: var(--muted);
            margin-bottom: 0.25rem;
        }

        .mini-kv-content {
            color: var(--text);
            font-size: 0.9rem;
            line-height: 1.5;
            font-weight: 600;
            white-space: pre-wrap;
        }

        .result-shell {
            background: rgba(255,255,255,0.88);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 0.2rem 0.4rem 0.7rem 0.4rem;
            box-shadow: 0 12px 32px rgba(15,23,42,0.06);
        }

        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextInput"] input {
            border-radius: 16px !important;
            border: 1px solid rgba(15,23,42,0.10) !important;
            background: rgba(255,255,255,0.96) !important;
        }

        .stButton > button {
            border-radius: 14px !important;
            font-weight: 700 !important;
            border: 1px solid rgba(15,23,42,0.08) !important;
            box-shadow: 0 8px 20px rgba(15,23,42,0.05);
        }

        .footer-note {
            color: var(--muted);
            font-size: 0.85rem;
            text-align: center;
            padding: 0.6rem 0 0 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="hero">
            <h1>需求转译 AI Workspace</h1>
            <p>把产品经理的自然语言需求，收敛成结构化交接单，再分发给研发、设计、算法、测试、运营五个角色。更像工作台，而不是一次性表单。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stepper(step: int):
    steps = [
        ("01", "录入需求", "输入原始想法或上传文档"),
        ("02", "结构化解析", "总控 Agent 提炼交接单"),
        ("03", "补充与校准", "补齐缺失信息后确认"),
        ("04", "角色分发", "生成五个部门版本与风险提醒"),
    ]
    html = ['<div class="stepper">']
    for idx, (num, title, desc) in enumerate(steps, start=1):
        cls = "step"
        if idx < step:
            cls += " done"
        elif idx == step:
            cls += " active"
        html.append(
            f'<div class="{cls}"><div class="step-num">STEP {num}</div><div class="step-title">{title}</div><div class="step-desc">{desc}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def metric_card(label: str, value: str, desc: str = ""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_open(title: str, desc: str = ""):
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-title">
                <h3>{title}</h3>
                <span class="subtle">{desc}</span>
            </div>
        """,
        unsafe_allow_html=True,
    )


def section_close():
    st.markdown("</div>", unsafe_allow_html=True)


def assistant_bubble(title: str, content: str):
    st.markdown(
        f"""
        <div class="assistant-bubble">
            <div class="assistant-tag">AI 助理</div>
            <div style="font-weight:700;color:#0f172a;margin-bottom:0.35rem;">{title}</div>
            <div style="color:#475467;font-size:0.93rem;line-height:1.55;white-space:pre-wrap;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chips(items: List[str], kind: str = "default"):
    if not items:
        st.caption("暂无")
        return
    cls = "chip" if kind == "default" else f"chip {kind}"
    html = ['<div class="chip-wrap">']
    for item in items:
        safe = str(item).replace("<", "&lt;").replace(">", "&gt;")
        html.append(f'<span class="{cls}">{safe}</span>')
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def get_gate_status(analysis_result: Dict) -> tuple[bool, List[str]]:
    common_missing = []
    if not analysis_result.get("users"):
        common_missing.append("目标用户")
    if not analysis_result.get("core_scenarios"):
        common_missing.append("核心场景")
    if not analysis_result.get("core_features"):
        common_missing.append("核心功能")
    if not analysis_result.get("success_criteria"):
        common_missing.append("成功标准")
    if not analysis_result.get("constraints"):
        common_missing.append("约束条件")
    if not analysis_result.get("dependencies"):
        common_missing.append("依赖条件")
    return (len(common_missing) == 0), common_missing


def ensure_state():
    defaults = {
        "raw_requirement": "",
        "uploaded_name": "",
        "final_requirement": "",
        "analysis_result": None,
        "results": None,
        "example_case": "自定义输入",
        "analysis_done": False,
        "generation_done": False,
        "current_step": 1,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def parse_multiline(text: str) -> List[str]:
    lines = []
    for line in (text or "").splitlines():
        cleaned = line.strip().strip("- ").strip()
        if cleaned:
            lines.append(cleaned)
    return lines


def merge_manual_fields(base_analysis: Dict, raw_requirement: str) -> Dict:
    analysis = dict(base_analysis)
    analysis["goal"] = st.session_state.get("edit_goal", "").strip() or analysis.get("goal", "未明确")
    analysis["users"] = parse_multiline(st.session_state.get("edit_users", ""))
    analysis["core_scenarios"] = parse_multiline(st.session_state.get("edit_scenarios", ""))
    analysis["core_features"] = parse_multiline(st.session_state.get("edit_features", ""))
    analysis["success_criteria"] = parse_multiline(st.session_state.get("edit_success", ""))
    analysis["constraints"] = parse_multiline(st.session_state.get("edit_constraints", ""))
    analysis["dependencies"] = parse_multiline(st.session_state.get("edit_dependencies", ""))
    analysis["unclear_points"] = parse_multiline(st.session_state.get("edit_unclear", ""))

    is_ready, common_missing = get_gate_status(analysis)
    analysis["missing_common_info"] = common_missing

    suggestions = []
    mapping = {
        "目标用户": "请补充这项需求的目标用户是谁。",
        "核心场景": "请补充这项需求的核心使用场景。",
        "核心功能": "请补充这项需求的核心功能内容。",
        "成功标准": "请补充这项需求的成功标准或验收口径。",
        "约束条件": "请补充这项需求的约束条件，例如时间、资源、合规或平台限制。",
        "依赖条件": "请补充这项需求的依赖条件，例如系统、数据或第三方服务依赖。",
    }
    for item in common_missing:
        if item in mapping:
            suggestions.append(mapping[item])
    analysis["supplement_suggestions"] = suggestions

    analyzer = RequirementAnalyzer(api_key=st.session_state.api_key, model=st.session_state.model_choice, base_url=st.session_state.base_url)
    analysis["handoff_packet"] = analyzer.build_handoff_packet(raw_requirement, analysis)
    analysis["handoff_packet"]["ready_for_handoff"] = is_ready
    return analysis


def fill_edit_state_from_analysis(analysis: Dict):
    st.session_state.edit_goal = analysis.get("goal", "")
    st.session_state.edit_users = "\n".join(analysis.get("users", []))
    st.session_state.edit_scenarios = "\n".join(analysis.get("core_scenarios", []))
    st.session_state.edit_features = "\n".join(analysis.get("core_features", []))
    st.session_state.edit_success = "\n".join(analysis.get("success_criteria", []))
    st.session_state.edit_constraints = "\n".join(analysis.get("constraints", []))
    st.session_state.edit_dependencies = "\n".join(analysis.get("dependencies", []))
    st.session_state.edit_unclear = "\n".join(analysis.get("unclear_points", []))


def prepare_requirement_text(uploaded_requirement, text_requirement: str) -> tuple[str, str, str]:
    uploaded_requirement_text = ""
    uploaded_requirement_error = ""
    uploaded_name = ""

    if uploaded_requirement is not None:
        uploaded_name = uploaded_requirement.name
        try:
            uploaded_requirement_text = extract_text_from_docx(uploaded_requirement)
            if not uploaded_requirement_text:
                uploaded_requirement_error = "Word 文档中未提取到有效文本，请检查文档内容。"
        except Exception as exc:
            uploaded_requirement_error = f"Word 文档解析失败：{exc}"

    final_requirement = uploaded_requirement_text if uploaded_requirement_text else text_requirement
    return final_requirement, uploaded_requirement_error, uploaded_name


def run_analysis(final_requirement: str):
    analyzer = RequirementAnalyzer(
        api_key=st.session_state.api_key,
        model=st.session_state.model_choice,
        base_url=st.session_state.base_url,
    )
    analysis_result = analyzer.analyze(final_requirement)
    st.session_state.analysis_result = analysis_result
    st.session_state.analysis_done = True
    st.session_state.generation_done = False
    st.session_state.results = None
    st.session_state.current_step = 2
    fill_edit_state_from_analysis(analysis_result)


def run_generation(final_requirement: str, analysis_result: Dict):
    results = {}
    engineering_agent = EngineeringAgent(st.session_state.api_key, st.session_state.model_choice, st.session_state.base_url)
    design_agent = DesignAgent(st.session_state.api_key, st.session_state.model_choice, st.session_state.base_url)
    ai_agent = AIAgent(st.session_state.api_key, st.session_state.model_choice, st.session_state.base_url)
    qa_agent = QAAgent(st.session_state.api_key, st.session_state.model_choice, st.session_state.base_url)
    operation_agent = OperationAgent(st.session_state.api_key, st.session_state.model_choice, st.session_state.base_url)
    risk_analyzer = RiskAnalyzer(st.session_state.api_key, st.session_state.model_choice, st.session_state.base_url)

    progress = st.progress(0)
    status = st.empty()

    status.info("正在生成研发版本…")
    results["engineering"] = engineering_agent.generate(final_requirement, analysis_result)
    progress.progress(16)

    status.info("正在生成设计版本…")
    results["design"] = design_agent.generate(final_requirement, analysis_result)
    progress.progress(32)

    status.info("正在生成算法版本…")
    results["ai"] = ai_agent.generate(final_requirement, analysis_result)
    progress.progress(48)

    status.info("正在生成测试版本…")
    results["qa"] = qa_agent.generate(final_requirement, analysis_result)
    progress.progress(64)

    status.info("正在生成运营版本…")
    results["operation"] = operation_agent.generate(final_requirement, analysis_result)
    progress.progress(80)

    status.info("正在生成风险分析…")
    results["risk"] = risk_analyzer.analyze(final_requirement, analysis_result, results)
    progress.progress(100)
    status.success("全部角色版本已生成。")

    st.session_state.results = results
    st.session_state.generation_done = True
    st.session_state.current_step = 4


# -----------------------------
# Main app
# -----------------------------
ensure_state()
inject_css()
render_hero()

examples = create_example_cases()

with st.sidebar:
    st.markdown("### 控制台")
    api_provider = st.selectbox(
        "模型提供商",
        ["DeepSeek", "豆包(Doubao)", "通义千问(Qwen)", "自定义 OpenAI 兼容 API"],
        index=0,
    )

    api_key = st.text_input("API Key", type="password", value=st.session_state.get("api_key", ""))
    st.session_state.api_key = api_key

    if api_provider == "DeepSeek":
        base_url = st.text_input("Base URL", value="https://api.deepseek.com/v1")
        model_choice = st.selectbox("模型", ["deepseek-chat", "deepseek-reasoner"], index=0)
    elif api_provider == "豆包(Doubao)":
        base_url = st.text_input("Base URL", value="https://ark.cn-beijing.volces.com/api/v3")
        model_choice = st.selectbox("模型", ["doubao-pro-32k", "doubao-lite-32k", "doubao-pro-128k"], index=0)
    elif api_provider == "通义千问(Qwen)":
        base_url = st.text_input("Base URL", value="https://dashscope.aliyuncs.com/compatible-mode/v1")
        model_choice = st.selectbox("模型", ["qwen-plus", "qwen-turbo", "qwen-max"], index=0)
    else:
        base_url = st.text_input("Base URL", value="https://api.openai.com/v1")
        model_choice = st.text_input("模型", value="gpt-4o-mini")

    st.session_state.base_url = base_url
    st.session_state.model_choice = model_choice

    st.divider()
    selected_example = st.selectbox(
        "示例需求",
        ["自定义输入"] + list(examples.keys()),
        index=0,
        key="example_selector",
    )

    if st.button("载入示例", use_container_width=True):
        if selected_example != "自定义输入":
            st.session_state.raw_requirement = examples[selected_example]
            st.session_state.example_case = selected_example
        else:
            st.session_state.raw_requirement = ""
            st.session_state.example_case = selected_example
        st.session_state.analysis_result = None
        st.session_state.results = None
        st.session_state.analysis_done = False
        st.session_state.generation_done = False
        st.session_state.current_step = 1
        st.rerun()

    if selected_example != "自定义输入":
        st.caption("当前示例预览")
        st.info(examples[selected_example][:300] + ("..." if len(examples[selected_example]) > 300 else ""))

    st.divider()
    if st.button("清空工作台", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("edit_"):
                del st.session_state[key]
        st.session_state.raw_requirement = ""
        st.session_state.analysis_result = None
        st.session_state.results = None
        st.session_state.analysis_done = False
        st.session_state.generation_done = False
        st.session_state.current_step = 1
        st.rerun()


render_stepper(st.session_state.current_step)

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("输入源", "文本 / Word", "支持粘贴原始需求或上传 .docx")
with m2:
    metric_card("总控状态", "已就绪" if st.session_state.analysis_done else "待解析", "先结构化再分发")
with m3:
    metric_card("分发角色", "5 + 1", "研发 / 设计 / 算法 / 测试 / 运营 / 风险")
with m4:
    metric_card("交互模式", "工作台", "可补充信息后再生成")

left, right = st.columns([1.15, 0.95], gap="large")

with left:
    section_open("需求输入区", "像 PM 在工作台里整理需求")
    raw_requirement = st.text_area(
        "产品原始需求",
        value=st.session_state.raw_requirement,
        height=240,
        placeholder="例如：我们希望做一个会议纪要 AI 功能，用户上传录音后，系统可以自动转写、提炼重点、输出待办事项……",
    )
    st.session_state.raw_requirement = raw_requirement

    uploaded_requirement = st.file_uploader(
        "上传 Word 需求文档（.docx）",
        type=["docx"],
        help="上传后优先使用 Word 文本作为需求输入。",
    )

    final_requirement, uploaded_requirement_error, uploaded_name = prepare_requirement_text(uploaded_requirement, raw_requirement)
    st.session_state.final_requirement = final_requirement
    st.session_state.uploaded_name = uploaded_name

    if uploaded_requirement_error:
        st.error(uploaded_requirement_error)
    elif uploaded_name:
        st.success(f"已读取文档：{uploaded_name}")
        with st.expander("查看提取后的文档文本"):
            st.text_area("文档文本预览", value=final_requirement, height=220, disabled=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("解析需求", type="primary", use_container_width=True):
            if not st.session_state.api_key:
                st.error("请先在左侧配置 API Key。")
            elif not final_requirement.strip():
                st.error("请输入需求内容或上传有效文档。")
            elif uploaded_requirement_error:
                st.error("请先修复文档解析问题。")
            else:
                with st.spinner("总控 Agent 正在解析需求…"):
                    run_analysis(final_requirement)
                st.rerun()
    with c2:
        if st.button("更新交接单", use_container_width=True, disabled=not st.session_state.analysis_done):
            merged = merge_manual_fields(st.session_state.analysis_result, st.session_state.final_requirement)
            st.session_state.analysis_result = merged
            st.session_state.current_step = 3
            st.success("已根据你补充的内容更新交接单。")
            st.rerun()
    with c3:
        can_generate = bool(st.session_state.analysis_result) and not get_gate_status(st.session_state.analysis_result)[1]
        if st.button("生成全部角色文档", use_container_width=True, disabled=not can_generate):
            with st.spinner("各角色 Agent 正在协作输出…"):
                run_generation(st.session_state.final_requirement, st.session_state.analysis_result)
            st.rerun()
    section_close()

    if st.session_state.analysis_done and st.session_state.analysis_result:
        analysis = st.session_state.analysis_result
        section_open("结构化摘要", "总控 Agent 提炼后的核心信息")
        a1, a2, a3 = st.columns(3)
        with a1:
            st.markdown('<div class="mini-kv"><div class="mini-kv-title">需求目标</div><div class="mini-kv-content">' + format_output(analysis.get("goal", "未明确")) + '</div></div>', unsafe_allow_html=True)
        with a2:
            st.markdown('<div class="mini-kv"><div class="mini-kv-title">目标用户</div><div class="mini-kv-content">' + format_output(analysis.get("users", [])) + '</div></div>', unsafe_allow_html=True)
        with a3:
            st.markdown('<div class="mini-kv"><div class="mini-kv-title">核心功能</div><div class="mini-kv-content">' + format_output(analysis.get("core_features", [])) + '</div></div>', unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown('<div class="mini-kv"><div class="mini-kv-title">核心场景</div><div class="mini-kv-content">' + format_output(analysis.get("core_scenarios", [])) + '</div></div>', unsafe_allow_html=True)
        with b2:
            st.markdown('<div class="mini-kv"><div class="mini-kv-title">成功标准</div><div class="mini-kv-content">' + format_output(analysis.get("success_criteria", [])) + '</div></div>', unsafe_allow_html=True)
        with b3:
            st.markdown('<div class="mini-kv"><div class="mini-kv-title">约束条件</div><div class="mini-kv-content">' + format_output(analysis.get("constraints", [])) + '</div></div>', unsafe_allow_html=True)
        section_close()

with right:
    section_open("AI 协作面板", "更像对话式 PM 助手")
    if not st.session_state.analysis_done:
        assistant_bubble(
            "先让我帮你收敛需求",
            "你先在左侧输入原始需求，我会先做结构化解析，提炼目标、用户、场景、功能、成功标准和依赖。解析完之后，你可以直接在右侧补充缺失信息，再一键分发给五个部门。",
        )
        render_chips(["结构化解析", "可手动补充", "五角色分发", "风险提醒"], kind="default")
    else:
        analysis = st.session_state.analysis_result
        ready, common_missing = get_gate_status(analysis)
        summary_text = f"目标：{analysis.get('goal', '未明确')}\n\n"
        if common_missing:
            summary_text += "我发现还缺这些通用信息：" + "、".join(common_missing) + "。你可以直接在下面补充。"
        else:
            summary_text += "基础信息已经齐全，可以直接生成五个角色版本。"
        assistant_bubble("当前判断", summary_text)

        st.markdown("**通用缺失项**")
        if common_missing:
            render_chips(common_missing, kind="warn")
        else:
            render_chips(["交接单已满足分发条件"], kind="ok")

        with st.expander("补充 / 编辑交接单", expanded=True):
            st.text_input("需求目标", key="edit_goal")
            st.text_area("目标用户（每行一条）", key="edit_users", height=90)
            st.text_area("核心场景（每行一条）", key="edit_scenarios", height=90)
            st.text_area("核心功能（每行一条）", key="edit_features", height=110)
            st.text_area("成功标准（每行一条）", key="edit_success", height=90)
            st.text_area("约束条件（每行一条）", key="edit_constraints", height=90)
            st.text_area("依赖条件（每行一条）", key="edit_dependencies", height=90)
            st.text_area("不明确点（每行一条）", key="edit_unclear", height=90)

        with st.expander("查看结构化交接单 JSON"):
            st.json(analysis.get("handoff_packet", {}))

        if analysis.get("supplement_suggestions"):
            st.markdown("**补充建议**")
            for item in analysis.get("supplement_suggestions", []):
                st.write(f"- {item}")
    section_close()


if st.session_state.generation_done and st.session_state.results:
    st.markdown('<div class="result-shell">', unsafe_allow_html=True)
    st.markdown("### 结果面板")

    results = st.session_state.results
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "研发", "设计", "算法", "测试", "运营", "风险"
    ])

    with tab1:
        content = format_output(results.get("engineering"))
        st.markdown(content)
        st.download_button("下载研发版本", data=content, file_name="engineering_requirement.md", mime="text/markdown")
    with tab2:
        content = format_output(results.get("design"))
        st.markdown(content)
        st.download_button("下载设计版本", data=content, file_name="design_requirement.md", mime="text/markdown")
    with tab3:
        content = format_output(results.get("ai"))
        st.markdown(content)
        st.download_button("下载算法版本", data=content, file_name="ai_requirement.md", mime="text/markdown")
    with tab4:
        content = format_output(results.get("qa"))
        st.markdown(content)
        st.download_button("下载测试版本", data=content, file_name="qa_requirement.md", mime="text/markdown")
    with tab5:
        content = format_output(results.get("operation"))
        st.markdown(content)
        st.download_button("下载运营版本", data=content, file_name="operation_requirement.md", mime="text/markdown")
    with tab6:
        risk = results.get("risk", {})
        if isinstance(risk, dict):
            if risk.get("unclear_expressions"):
                st.warning("表达不够明确")
                for item in risk["unclear_expressions"]:
                    st.write(f"- {item}")
            if risk.get("needs_supplement"):
                st.info("需要补充的信息")
                for item in risk["needs_supplement"]:
                    st.write(f"- {item}")
            if risk.get("cross_dept_risks"):
                st.error("跨部门理解偏差风险")
                for item in risk["cross_dept_risks"]:
                    st.write(f"- {item}")
            if risk.get("next_steps"):
                st.success("建议的下一步")
                for item in risk["next_steps"]:
                    st.write(f"- {item}")
            st.markdown("---")
            st.markdown(format_output(risk))
            st.download_button("下载风险分析", data=format_output(risk), file_name="risk_analysis.md", mime="text/markdown")
        else:
            st.markdown(format_output(risk))

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='footer-note'>Streamlit × Multi-Agent Workflow · 先解析，再补充，再分发。这个版本重点强化了界面层次、可编辑交接单和工作台式交互感。</div>",
    unsafe_allow_html=True,
)
