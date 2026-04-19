import re
from typing import Dict, List

import streamlit as st

from agents import RequirementAnalyzer, EngineeringAgent, DesignAgent, AIAgent, QAAgent, OperationAgent, RiskAnalyzer
from utils import format_output, create_example_cases, extract_text_from_docx


st.set_page_config(
    page_title="需求转译 AI Workspace",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css():
    st.markdown(
        """
        <style>
        :root {
            --bg: #f7f8fc;
            --card: rgba(255,255,255,0.88);
            --line: rgba(15, 23, 42, 0.08);
            --text: #111827;
            --muted: #6b7280;
            --accent: #5b55eb;
            --accent-soft: rgba(91,85,235,0.08);
            --ok: #16a34a;
            --warn: #d97706;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(99,102,241,0.10), transparent 26%),
                linear-gradient(180deg, #fafbff 0%, #f5f7fb 100%);
        }
        .block-container {
            max-width: 1280px;
            padding-top: 1.1rem;
            padding-bottom: 2rem;
        }
        .hero {
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(255,255,255,0.65);
            backdrop-filter: blur(8px);
            border-radius: 24px;
            padding: 1.2rem 1.35rem;
            box-shadow: 0 18px 48px rgba(15,23,42,0.06);
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 1.72rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: var(--text);
        }
        .hero p {
            margin: 0.45rem 0 0 0;
            color: var(--muted);
            font-size: 0.96rem;
        }
        .stage-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.34rem 0.7rem;
            border-radius: 999px;
            background: var(--accent-soft);
            color: #4338ca;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }
        .card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 1.05rem 1.1rem;
            box-shadow: 0 12px 30px rgba(15,23,42,0.05);
            margin-bottom: 1rem;
        }
        .card h3 {
            margin: 0 0 0.3rem 0;
            color: var(--text);
            font-size: 1.04rem;
        }
        .card p {
            margin: 0;
            color: var(--muted);
            font-size: 0.92rem;
        }
        .assistant {
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.95));
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1rem;
            box-shadow: 0 10px 24px rgba(15,23,42,0.05);
        }
        .assistant-tag {
            display: inline-block;
            padding: 0.18rem 0.58rem;
            border-radius: 999px;
            background: var(--accent-soft);
            color: #4338ca;
            font-size: 0.75rem;
            font-weight: 700;
            margin-bottom: 0.55rem;
        }
        .assistant h4 {
            margin: 0 0 0.4rem 0;
            color: var(--text);
            font-size: 1rem;
        }
        .assistant-body {
            color: #475467;
            font-size: 0.93rem;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.7rem;
            margin-top: 0.9rem;
        }
        .kv {
            background: rgba(248,250,252,0.92);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.8rem 0.9rem;
        }
        .kv .label {
            font-size: 0.8rem;
            color: var(--muted);
            margin-bottom: 0.28rem;
        }
        .kv .value {
            font-size: 0.92rem;
            color: var(--text);
            font-weight: 600;
            line-height: 1.55;
            white-space: pre-wrap;
        }
        .soft-note {
            color: var(--muted);
            font-size: 0.86rem;
            margin-top: 0.45rem;
        }
        .result-shell {
            background: rgba(255,255,255,0.88);
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 0.35rem 0.5rem 0.8rem 0.5rem;
            box-shadow: 0 12px 30px rgba(15,23,42,0.05);
            margin-top: 0.8rem;
        }
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextInput"] input {
            border-radius: 16px !important;
            border: 1px solid rgba(15,23,42,0.10) !important;
            background: rgba(255,255,255,0.98) !important;
        }
        .stButton > button {
            border-radius: 14px !important;
            font-weight: 700 !important;
            box-shadow: 0 8px 20px rgba(15,23,42,0.05);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="hero">
            <div class="stage-pill">需求转译工作台</div>
            <h1>先让 AI 帮你补全，再确认分发</h1>
            <p>不平铺所有信息。先输入需求，AI 生成一份建议交接单；你确认无误后，再生成研发、设计、算法、测试、运营文档。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ensure_state():
    defaults = {
        "raw_requirement": "",
        "uploaded_name": "",
        "final_requirement": "",
        "analysis_result": None,
        "results": None,
        "analysis_done": False,
        "generation_done": False,
        "handoff_confirmed": False,
        "recommended_handoff_text": "",
        "api_key": "",
        "base_url": "https://api.deepseek.com/v1",
        "model_choice": "deepseek-chat",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


ensure_state()
inject_css()
render_hero()

examples = create_example_cases()


# ---------- helper functions ----------
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


def normalize_list(value) -> List[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


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


def generate_recommended_handoff_text(analysis: Dict) -> str:
    ready, missing = get_gate_status(analysis)

    def fmt_lines(items, missing_name=None):
        items = normalize_list(items)
        if items:
            return "\n".join([f"- {item}" for item in items])
        if missing_name:
            return f"【请补充：{missing_name}】"
        return "【无】"

    goal = analysis.get("goal", "未明确") or "未明确"
    unclear = normalize_list(analysis.get("unclear_points", []))
    unclear_text = "\n".join([f"- {item}" for item in unclear]) if unclear else "【无】"

    draft = f"""需求目标：
{goal}

目标用户：
{fmt_lines(analysis.get('users', []), '目标用户')}

核心场景：
{fmt_lines(analysis.get('core_scenarios', []), '核心场景')}

核心功能：
{fmt_lines(analysis.get('core_features', []), '核心功能')}

成功标准：
{fmt_lines(analysis.get('success_criteria', []), '成功标准')}

约束条件：
{fmt_lines(analysis.get('constraints', []), '约束条件')}

依赖条件：
{fmt_lines(analysis.get('dependencies', []), '依赖条件')}

不明确点：
{unclear_text}
"""
    if not ready and missing:
        draft += "\nAI 提示：\n" + "\n".join([f"- 还缺：{item}" for item in missing])
    return draft.strip()


SECTION_MAP = {
    "需求目标": "goal",
    "目标用户": "users",
    "核心场景": "core_scenarios",
    "核心功能": "core_features",
    "成功标准": "success_criteria",
    "约束条件": "constraints",
    "依赖条件": "dependencies",
    "不明确点": "unclear_points",
}


def parse_recommended_handoff_text(text: str, raw_requirement: str) -> Dict:
    pattern = r"(?ms)^(需求目标|目标用户|核心场景|核心功能|成功标准|约束条件|依赖条件|不明确点|AI 提示)：\s*\n(.*?)(?=^(?:需求目标|目标用户|核心场景|核心功能|成功标准|约束条件|依赖条件|不明确点|AI 提示)：|\Z)"
    matches = re.findall(pattern, text.strip())
    parsed = {
        "goal": raw_requirement[:100] if raw_requirement else "未明确",
        "users": [],
        "core_scenarios": [],
        "core_features": [],
        "success_criteria": [],
        "constraints": [],
        "dependencies": [],
        "unclear_points": [],
    }

    for section, content in matches:
        content = content.strip()
        if section == "AI 提示":
            continue
        field = SECTION_MAP[section]
        if field == "goal":
            cleaned = " ".join([line.strip("- ").strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("【请补充")])
            parsed[field] = cleaned or "未明确"
        else:
            lines = []
            for line in content.splitlines():
                cleaned = line.strip().strip("- ").strip()
                if not cleaned:
                    continue
                if cleaned.startswith("【请补充") or cleaned == "【无】":
                    continue
                lines.append(cleaned)
            parsed[field] = lines

    ready, missing = get_gate_status(parsed)
    parsed["missing_common_info"] = missing
    suggestion_map = {
        "目标用户": "请补充这项需求的目标用户是谁。",
        "核心场景": "请补充这项需求的核心使用场景。",
        "核心功能": "请补充这项需求的核心功能内容。",
        "成功标准": "请补充这项需求的成功标准或验收口径。",
        "约束条件": "请补充这项需求的约束条件，例如时间、资源、合规或平台限制。",
        "依赖条件": "请补充这项需求的依赖条件，例如系统、数据或第三方服务依赖。",
    }
    parsed["supplement_suggestions"] = [suggestion_map[item] for item in missing if item in suggestion_map]

    analyzer = RequirementAnalyzer(api_key=st.session_state.api_key, model=st.session_state.model_choice, base_url=st.session_state.base_url)
    parsed["handoff_packet"] = analyzer.build_handoff_packet(raw_requirement, parsed)
    parsed["handoff_packet"]["ready_for_handoff"] = ready
    return parsed


def run_analysis(final_requirement: str):
    analyzer = RequirementAnalyzer(
        api_key=st.session_state.api_key,
        model=st.session_state.model_choice,
        base_url=st.session_state.base_url,
    )
    analysis_result = analyzer.analyze(final_requirement)
    st.session_state.analysis_result = analysis_result
    st.session_state.recommended_handoff_text = generate_recommended_handoff_text(analysis_result)
    st.session_state.analysis_done = True
    st.session_state.handoff_confirmed = False
    st.session_state.generation_done = False
    st.session_state.results = None



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


# ---------- sidebar ----------
with st.sidebar:
    st.markdown("### 控制台")
    api_provider = st.selectbox(
        "模型提供商",
        ["DeepSeek", "豆包(Doubao)", "通义千问(Qwen)", "自定义 OpenAI 兼容 API"],
        index=0,
    )

    st.session_state.api_key = st.text_input("API Key", type="password", value=st.session_state.api_key)

    if api_provider == "DeepSeek":
        st.session_state.base_url = st.text_input("Base URL", value=st.session_state.base_url or "https://api.deepseek.com/v1")
        st.session_state.model_choice = st.selectbox("模型", ["deepseek-chat", "deepseek-reasoner"], index=0)
    elif api_provider == "豆包(Doubao)":
        st.session_state.base_url = st.text_input("Base URL", value="https://ark.cn-beijing.volces.com/api/v3")
        st.session_state.model_choice = st.selectbox("模型", ["doubao-pro-32k", "doubao-lite-32k", "doubao-pro-128k"], index=0)
    elif api_provider == "通义千问(Qwen)":
        st.session_state.base_url = st.text_input("Base URL", value="https://dashscope.aliyuncs.com/compatible-mode/v1")
        st.session_state.model_choice = st.selectbox("模型", ["qwen-plus", "qwen-turbo", "qwen-max"], index=0)
    else:
        st.session_state.base_url = st.text_input("Base URL", value="https://api.openai.com/v1")
        st.session_state.model_choice = st.text_input("模型", value="gpt-4o-mini")

    st.divider()
    selected_example = st.selectbox("示例需求", ["自定义输入"] + list(examples.keys()), index=0)
    if st.button("载入示例", use_container_width=True):
        st.session_state.raw_requirement = "" if selected_example == "自定义输入" else examples[selected_example]
        st.session_state.analysis_result = None
        st.session_state.recommended_handoff_text = ""
        st.session_state.results = None
        st.session_state.analysis_done = False
        st.session_state.generation_done = False
        st.session_state.handoff_confirmed = False
        st.rerun()

    if st.button("清空", use_container_width=True):
        for key in [
            "raw_requirement", "uploaded_name", "final_requirement", "analysis_result", "results",
            "analysis_done", "generation_done", "handoff_confirmed", "recommended_handoff_text"
        ]:
            st.session_state[key] = "" if isinstance(st.session_state.get(key), str) else False if isinstance(st.session_state.get(key), bool) else None
        st.session_state.raw_requirement = ""
        st.session_state.analysis_done = False
        st.session_state.generation_done = False
        st.session_state.handoff_confirmed = False
        st.rerun()


# ---------- stage 1 ----------
if not st.session_state.analysis_done:
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown('<div class="card"><h3>输入原始需求</h3><p>支持粘贴想法，或上传 Word 文档。</p></div>', unsafe_allow_html=True)
        raw_requirement = st.text_area(
            "产品经理原始需求",
            value=st.session_state.raw_requirement,
            height=300,
            placeholder="例如：我们希望做一个会议纪要 AI 功能，用户上传录音后，系统可以自动转写、提炼重点、输出待办事项……",
        )
        st.session_state.raw_requirement = raw_requirement

        uploaded_requirement = st.file_uploader("上传 Word 需求文档（.docx）", type=["docx"])
        final_requirement, uploaded_requirement_error, uploaded_name = prepare_requirement_text(uploaded_requirement, raw_requirement)
        st.session_state.final_requirement = final_requirement
        st.session_state.uploaded_name = uploaded_name

        if uploaded_requirement_error:
            st.error(uploaded_requirement_error)
        elif uploaded_name:
            st.success(f"已读取文档：{uploaded_name}")

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("开始解析", type="primary", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("请先在左侧填写 API Key。")
                elif not final_requirement.strip():
                    st.error("请输入需求内容或上传有效文档。")
                elif uploaded_requirement_error:
                    st.error("请先修复文档解析问题。")
                else:
                    with st.spinner("AI 正在整理需求…"):
                        run_analysis(final_requirement)
                    st.rerun()
        with c2:
            st.button("等待 AI 建议", use_container_width=True, disabled=True)

    with right:
        st.markdown(
            '''
            <div class="assistant">
                <div class="assistant-tag">AI 助理</div>
                <h4>我会先帮你生成一份建议交接单</h4>
                <div class="assistant-body">解析后，我不会把所有信息都摊开。
我会先给你一份可编辑的 AI 推荐文本，你只需要确认、微调、点击采用，然后再生成各部门需求文档。</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="soft-note">这一步只有输入，不会直接进入复杂结果页。</div>', unsafe_allow_html=True)


# ---------- stage 2 ----------
elif st.session_state.analysis_done and not st.session_state.handoff_confirmed:
    analysis = st.session_state.analysis_result
    ready, missing = get_gate_status(analysis)

    left, right = st.columns([0.86, 1.14], gap="large")

    with left:
        st.markdown('<div class="card"><h3>当前解析摘要</h3><p>这里只展示最关键的信息，避免页面过重。</p></div>', unsafe_allow_html=True)
        def kv(label, value):
            return f'<div class="kv"><div class="label">{label}</div><div class="value">{value}</div></div>'

        goal_text = format_output(analysis.get("goal", "未明确"))
        users_text = format_output(analysis.get("users", []))
        scene_text = format_output(analysis.get("core_scenarios", []))
        feature_text = format_output(analysis.get("core_features", []))
        st.markdown(
            f'<div class="summary-grid">{kv("需求目标", goal_text)}{kv("目标用户", users_text)}{kv("核心场景", scene_text)}{kv("核心功能", feature_text)}</div>',
            unsafe_allow_html=True,
        )

        if missing:
            st.warning("还缺这些通用信息：" + "、".join(missing))
        else:
            st.success("基础信息已齐全。你可以直接确认这份交接单。")

        if st.button("返回重新输入", use_container_width=True):
            st.session_state.analysis_done = False
            st.session_state.handoff_confirmed = False
            st.session_state.results = None
            st.session_state.generation_done = False
            st.rerun()

    with right:
        ai_msg = "我已经根据你的原始需求整理出一份建议交接单。你可以直接在下面修改文本，再点击确认采用。"
        if missing:
            ai_msg += "\n\n我已经把缺失项用【请补充】标出来了。"
        st.markdown(
            f'''
            <div class="assistant">
                <div class="assistant-tag">AI 助理</div>
                <h4>请确认这份 AI 推荐内容</h4>
                <div class="assistant-body">{ai_msg}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        recommended_text = st.text_area(
            "AI 推荐交接单",
            value=st.session_state.recommended_handoff_text,
            height=420,
            key="recommended_handoff_area",
            help="你可以直接修改这段文本。确认后，系统会把它作为五个角色的统一输入依据。",
        )

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("确认采用这份交接单", type="primary", use_container_width=True):
                parsed = parse_recommended_handoff_text(recommended_text, st.session_state.final_requirement)
                st.session_state.analysis_result = parsed
                st.session_state.recommended_handoff_text = recommended_text
                st.session_state.handoff_confirmed = True
                st.session_state.generation_done = False
                st.session_state.results = None
                st.rerun()
        with c2:
            if st.button("重新生成 AI 建议", use_container_width=True):
                st.session_state.recommended_handoff_text = generate_recommended_handoff_text(st.session_state.analysis_result)
                st.rerun()


# ---------- stage 3 ----------
else:
    analysis = st.session_state.analysis_result
    ready, missing = get_gate_status(analysis)

    top_left, top_right = st.columns([1.0, 0.9], gap="large")
    with top_left:
        st.markdown('<div class="card"><h3>交接单已确认</h3><p>现在这份内容会作为五个角色的统一输入基础。</p></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="summary-grid">'
            f'<div class="kv"><div class="label">需求目标</div><div class="value">{format_output(analysis.get("goal", "未明确"))}</div></div>'
            f'<div class="kv"><div class="label">目标用户</div><div class="value">{format_output(analysis.get("users", []))}</div></div>'
            f'<div class="kv"><div class="label">核心场景</div><div class="value">{format_output(analysis.get("core_scenarios", []))}</div></div>'
            f'<div class="kv"><div class="label">核心功能</div><div class="value">{format_output(analysis.get("core_features", []))}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with top_right:
        next_text = "你可以现在生成各部门文档。"
        if missing:
            next_text = "当前仍有缺失项，但你也可以继续生成；各角色输出会保留【需产品补充确认】提示。"
        st.markdown(
            f'''
            <div class="assistant">
                <div class="assistant-tag">AI 助理</div>
                <h4>下一步</h4>
                <div class="assistant-body">{next_text}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("生成各部门需求文档", type="primary", use_container_width=True):
                with st.spinner("各角色 Agent 正在协作输出…"):
                    run_generation(st.session_state.final_requirement, analysis)
                st.rerun()
        with c2:
            if st.button("返回修改交接单", use_container_width=True):
                st.session_state.handoff_confirmed = False
                st.rerun()

    if st.session_state.generation_done and st.session_state.results:
        st.markdown('<div class="result-shell">', unsafe_allow_html=True)
        st.markdown("### 各部门需求文档")
        results = st.session_state.results
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["研发", "设计", "算法", "测试", "运营", "风险"])

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
