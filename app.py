from __future__ import annotations

import re
from typing import Dict, List

import pandas as pd
import streamlit as st

from agents import (
    AIAgent,
    DesignAgent,
    EngineeringAgent,
    OperationAgent,
    QAAgent,
    RequirementAnalyzer,
    RiskAnalyzer,
)
from utils import create_example_cases, extract_text_from_docx, format_output

st.set_page_config(page_title="需求协作工作台", page_icon="🧠", layout="wide")


st.markdown(
    """
    <style>
    .stApp { background: #f7f8fb; }
    .block-container { max-width: 1380px; padding-top: 1.2rem; padding-bottom: 2rem; }
    .small-muted { color: #6b7280; font-size: 0.92rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

ROLE_LABELS = {
    "engineering": "研发",
    "design": "设计",
    "ai": "算法",
    "qa": "测试",
    "operation": "运营",
}
FIELD_MAP = [
    ("需求目标", "goal", False),
    ("目标用户", "users", True),
    ("核心场景", "core_scenarios", True),
    ("核心功能", "core_features", True),
    ("成功标准", "success_criteria", True),
    ("约束条件", "constraints", True),
    ("依赖条件", "dependencies", True),
    ("非目标/本期不做", "non_goals", True),
    ("MVP范围", "mvp_scope", True),
    ("风险与合规点", "risks_and_compliance", True),
    ("待确认问题", "unclear_points", True),
]


# ---------- state ----------
def init_state() -> None:
    defaults = {
        "api_key": "",
        "base_url": "https://api.deepseek.com/v1",
        "model_choice": "deepseek-chat",
        "provider": "DeepSeek",
        "raw_requirement": "",
        "source_requirement": "",
        "analysis": None,
        "recommended_handoff_text": "",
        "handoff_confirmed": False,
        "docs_generated": False,
        "docs": {},
        "risk": {},
        "feedback_history": {r: [] for r in ROLE_LABELS},
        "task_table": pd.DataFrame([
            {"任务": "补全交接单", "负责人": "产品", "开始": "", "截止": "", "状态": "待开始", "备注": ""},
            {"任务": "需求评审", "负责人": "产品/研发/设计", "开始": "", "截止": "", "状态": "待开始", "备注": ""},
            {"任务": "开发与联调", "负责人": "研发", "开始": "", "截止": "", "状态": "待开始", "备注": ""},
            {"任务": "测试准备", "负责人": "测试", "开始": "", "截止": "", "状态": "待开始", "备注": ""},
            {"任务": "上线准备", "负责人": "运营", "开始": "", "截止": "", "状态": "待开始", "备注": ""},
        ]),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()
examples = create_example_cases()


# ---------- helpers ----------
def reset_generated_content() -> None:
    st.session_state.docs_generated = False
    st.session_state.docs = {}
    st.session_state.risk = {}
    st.session_state.feedback_history = {r: [] for r in ROLE_LABELS}


def build_agent(role: str):
    kwargs = dict(
        api_key=st.session_state.api_key,
        model=st.session_state.model_choice,
        base_url=st.session_state.base_url,
    )
    mapping = {
        "engineering": EngineeringAgent,
        "design": DesignAgent,
        "ai": AIAgent,
        "qa": QAAgent,
        "operation": OperationAgent,
    }
    return mapping[role](**kwargs)


def get_analyzer() -> RequirementAnalyzer:
    return RequirementAnalyzer(
        st.session_state.api_key,
        st.session_state.model_choice,
        st.session_state.base_url,
    )


def prepare_requirement(uploaded_file, raw_text: str):
    extracted = ""
    error = ""
    if uploaded_file is not None:
        try:
            extracted = extract_text_from_docx(uploaded_file)
            if not extracted:
                error = "Word 文档中没有提取到有效文本。"
        except Exception as exc:
            error = f"Word 文档解析失败：{exc}"
    return (extracted if extracted else raw_text).strip(), error


def build_handoff_markdown_from_analysis(analysis: Dict) -> str:
    analyzer = get_analyzer()
    return analyzer.to_markdown(analysis)


def _clean_line_value(value: str) -> str:
    return value.strip().strip("：:").strip()


def parse_handoff_text(text: str, raw_requirement: str) -> Dict:
    buckets = {
        "goal": "",
        "users": [],
        "core_scenarios": [],
        "core_features": [],
        "success_criteria": [],
        "constraints": [],
        "dependencies": [],
        "non_goals": [],
        "mvp_scope": [],
        "risks_and_compliance": [],
        "unclear_points": [],
    }
    title_map = {title: key for title, key, _ in FIELD_MAP}
    current = None

    def append_value(key: str, val: str):
        val = val.strip()
        if not val or val in {"【待补充】", "待补充"}:
            return
        if key == "goal":
            buckets[key] = val
        else:
            buckets[key].append(val)

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^#+\s*", "", line)
        line = line.replace("**", "")

        matched_title = None
        for title in title_map:
            if line == title or line.startswith(f"{title}:") or line.startswith(f"{title}："):
                matched_title = title
                break

        if matched_title:
            current = title_map[matched_title]
            if "：" in line or ":" in line:
                _, rest = re.split(r"[:：]", line, maxsplit=1)
                append_value(current, _clean_line_value(rest))
            continue

        value = line.lstrip("-• ").strip()
        if current:
            append_value(current, value)

    analyzer = get_analyzer()
    analysis = {**buckets}
    analysis["missing_common_info"] = analyzer._build_missing_info(analysis)
    analysis["supplement_suggestions"] = analyzer._build_supplement_suggestions(analysis["missing_common_info"])
    analysis["recommended_handoff_markdown"] = analyzer.to_markdown(analysis)
    analysis["handoff_packet"] = analyzer.build_handoff_packet(raw_requirement, analysis)
    return analysis


def render_analysis_summary(analysis: Dict) -> None:
    col1, col2 = st.columns(2)
    rows = [
        ("需求目标", analysis.get("goal", "未明确")),
        ("目标用户", format_output(analysis.get("users", []))),
        ("核心场景", format_output(analysis.get("core_scenarios", []))),
        ("核心功能", format_output(analysis.get("core_features", []))),
        ("成功标准", format_output(analysis.get("success_criteria", []))),
        ("约束条件", format_output(analysis.get("constraints", []))),
        ("依赖条件", format_output(analysis.get("dependencies", []))),
        ("非目标/本期不做", format_output(analysis.get("non_goals", []))),
        ("MVP范围", format_output(analysis.get("mvp_scope", []))),
        ("风险与合规点", format_output(analysis.get("risks_and_compliance", []))),
        ("待确认问题", format_output(analysis.get("unclear_points", []))),
    ]
    for i, (label, value) in enumerate(rows):
        container = col1 if i % 2 == 0 else col2
        with container:
            st.markdown(f"**{label}**")
            st.info(value if value and value != "暂无内容" else "暂无内容")


def generate_all_docs() -> None:
    analysis = st.session_state.analysis
    roles = ["engineering", "design", "ai", "qa", "operation"]
    docs = {}
    progress = st.progress(0)
    status = st.empty()
    for idx, role in enumerate(roles, start=1):
        status.write(f"正在生成{ROLE_LABELS[role]}文档...")
        docs[role] = build_agent(role).generate(analysis)
        progress.progress(int(idx / len(roles) * 100))
    status.write("正在生成风险提醒...")
    risk_agent = RiskAnalyzer(st.session_state.api_key, st.session_state.model_choice, st.session_state.base_url)
    risk = risk_agent.analyze(analysis, docs)
    st.session_state.docs = docs
    st.session_state.risk = risk
    st.session_state.docs_generated = True
    status.empty()


# ---------- UI ----------
st.title("需求协作工作台")
st.caption("AI 先自动拆解推荐交接单，你确认后再生成研发、设计、算法、测试、运营文档，并支持继续批注迭代。")

with st.sidebar:
    st.subheader("配置")
    provider = st.selectbox(
        "模型提供商",
        ["DeepSeek", "豆包(Doubao)", "通义千问(Qwen)", "自定义 OpenAI 兼容 API"],
        key="provider",
    )
    st.text_input("API Key", type="password", key="api_key")

    if provider == "DeepSeek":
        st.text_input("Base URL", value="https://api.deepseek.com/v1", key="base_url")
        st.selectbox("模型", ["deepseek-chat", "deepseek-reasoner"], index=0, key="model_choice")
    elif provider == "豆包(Doubao)":
        st.text_input("Base URL", value="https://ark.cn-beijing.volces.com/api/v3", key="base_url")
        st.selectbox("模型", ["doubao-pro-32k", "doubao-lite-32k", "doubao-pro-128k"], index=0, key="model_choice")
    elif provider == "通义千问(Qwen)":
        st.text_input("Base URL", value="https://dashscope.aliyuncs.com/compatible-mode/v1", key="base_url")
        st.selectbox("模型", ["qwen-plus", "qwen-turbo", "qwen-max"], index=0, key="model_choice")
    else:
        st.text_input("Base URL", key="base_url")
        st.text_input("模型", key="model_choice")

    st.divider()
    example_choice = st.selectbox("示例需求", ["自定义输入"] + list(examples.keys()))
    if st.button("载入示例", use_container_width=True):
        st.session_state.raw_requirement = "" if example_choice == "自定义输入" else examples[example_choice]
        st.session_state.source_requirement = st.session_state.raw_requirement
        st.session_state.analysis = None
        st.session_state.recommended_handoff_text = ""
        st.session_state.handoff_confirmed = False
        reset_generated_content()
        st.rerun()

    if st.button("清空当前状态", use_container_width=True):
        for key in ["raw_requirement", "source_requirement", "analysis", "recommended_handoff_text"]:
            st.session_state[key] = "" if key != "analysis" else None
        st.session_state.handoff_confirmed = False
        reset_generated_content()
        st.rerun()

left, right = st.columns([1.05, 1], gap="large")

with left:
    st.subheader("输入需求")
    st.caption("支持直接粘贴需求，也支持上传 Word 文档。")
    st.text_area(
        "产品原始需求",
        key="raw_requirement",
        height=260,
        label_visibility="collapsed",
        placeholder="例如：我想做一个情感陪伴 app，和用户交互生成镜像虚拟形象，陪伴用户做正念、冥想、CBT 等认知干预……",
    )
    uploaded = st.file_uploader("上传 .docx", type=["docx"])

    if st.button("开始解析", use_container_width=True, type="primary"):
        if not st.session_state.api_key:
            st.error("请先在左侧输入 API Key。")
        else:
            final_requirement, error = prepare_requirement(uploaded, st.session_state.raw_requirement)
            if error:
                st.error(error)
            elif not final_requirement:
                st.error("请先输入需求或上传 Word 文档。")
            else:
                st.session_state.source_requirement = final_requirement
                analyzer = get_analyzer()
                with st.spinner("AI 正在自动拆解需求并生成推荐交接单..."):
                    analysis = analyzer.analyze(final_requirement)
                st.session_state.analysis = analysis
                st.session_state.recommended_handoff_text = analysis.get("recommended_handoff_markdown", "")
                st.session_state.handoff_confirmed = False
                reset_generated_content()
                st.rerun()

with right:
    st.subheader("AI 推荐交接单")
    if st.session_state.analysis is None:
        st.info("点击左侧“开始解析”后，我会自动拆解需求目标、目标用户、核心场景、核心功能、成功标准、约束条件、依赖条件、MVP 范围、非目标与待确认问题。")
    else:
        analysis = st.session_state.analysis
        st.caption("你可以直接编辑下面的交接单文本。确认后，后续所有部门文档都会以这份内容为准。")

        missing = analysis.get("missing_common_info", [])
        if missing:
            st.warning("当前仍缺少这些共用信息：" + "、".join(missing))
        else:
            st.success("通用信息已较完整，可以直接进入部门文档生成。")

        if analysis.get("supplement_suggestions"):
            with st.expander("查看 AI 补充建议", expanded=False):
                for s in analysis["supplement_suggestions"]:
                    st.write(f"- {s}")

        # 使用不同的变量名来存储推荐的交接单文本
        if "recommended_handoff_value" not in st.session_state:
            st.session_state.recommended_handoff_value = st.session_state.recommended_handoff_text
        
        edited_handoff = st.text_area(
            "推荐交接单（可直接编辑）",
            value=st.session_state.recommended_handoff_value,
            key="recommended_handoff_editor",
            height=460,
            label_visibility="collapsed",
        )
        # 同步用户编辑的内容到 session_state
        st.session_state.recommended_handoff_text = edited_handoff

        c1, c2 = st.columns(2)
        with c1:
            if st.button("确认采用交接单", use_container_width=True, type="primary"):
                updated_analysis = parse_handoff_text(st.session_state.recommended_handoff_text, st.session_state.source_requirement or st.session_state.raw_requirement)
                st.session_state.analysis = updated_analysis
                # 更新推荐的交接单内容
                st.session_state.recommended_handoff_value = updated_analysis.get("recommended_handoff_markdown", st.session_state.recommended_handoff_text)
                st.session_state.recommended_handoff_text = st.session_state.recommended_handoff_value
                st.session_state.handoff_confirmed = True
                reset_generated_content()
                st.success("已更新并确认交接单。")
                st.rerun()
        with c2:
            if st.button("重新生成推荐交接单", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("请先输入 API Key。")
                else:
                    analyzer = get_analyzer()
                    source = st.session_state.source_requirement or st.session_state.raw_requirement
                    with st.spinner("正在重新生成推荐交接单..."):
                        analysis = analyzer.analyze(source)
                    st.session_state.analysis = analysis
                    # 更新推荐的交接单内容
                    st.session_state.recommended_handoff_value = analysis.get("recommended_handoff_markdown", "")
                    st.session_state.recommended_handoff_text = st.session_state.recommended_handoff_value
                    st.session_state.handoff_confirmed = False
                    reset_generated_content()
                    st.rerun()

if st.session_state.handoff_confirmed and st.session_state.analysis:
    st.divider()
    st.subheader("确认后的交接单摘要")
    render_analysis_summary(st.session_state.analysis)
    st.markdown("")
    if st.button("生成各部门需求文档", use_container_width=False, type="primary"):
        if not st.session_state.api_key:
            st.error("请先输入 API Key。")
        else:
            with st.spinner("正在生成部门文档..."):
                generate_all_docs()
            st.rerun()

if st.session_state.docs_generated:
    st.divider()
    tab1, tab2, tab3 = st.tabs(["部门文档", "批注与 AI 协作", "排期与任务"])

    with tab1:
        doc_tabs = st.tabs([f"{ROLE_LABELS[r]}文档" for r in ROLE_LABELS] + ["风险提醒"])
        for idx, role in enumerate(ROLE_LABELS):
            with doc_tabs[idx]:
                doc_text = st.session_state.docs.get(role, "")
                st.markdown(doc_text or "暂无内容")
                st.download_button(
                    f"下载{ROLE_LABELS[role]}文档",
                    data=doc_text,
                    file_name=f"{role}_requirement.md",
                    mime="text/markdown",
                    key=f"download_{role}",
                )
        with doc_tabs[-1]:
            risk = st.session_state.risk
            for title, key in [
                ("表达不明确", "unclear_expressions"),
                ("需补充信息", "needs_supplement"),
                ("跨部门偏差风险", "cross_dept_risks"),
                ("隐性依赖", "hidden_dependencies"),
                ("可行性风险", "feasibility_risks"),
                ("下一步建议", "next_steps"),
            ]:
                st.markdown(f"**{title}**")
                items = risk.get(key, [])
                if items:
                    for item in items:
                        st.write(f"- {item}")
                else:
                    st.write("- 暂无")

    with tab2:
        role = st.selectbox("选择要协作修改的角色文档", list(ROLE_LABELS.keys()), format_func=lambda x: ROLE_LABELS[x])
        current_doc = st.session_state.docs.get(role, "")
        st.text_area("当前文档", value=current_doc, height=320, key=f"current_doc_view_{role}")
        feedback = st.text_area(
            "你的批注 / 修改要求",
            height=140,
            key=f"feedback_{role}",
            placeholder="例如：研发文档里的输入定义太空了，请补充请求参数；成功标准写得太泛了，请收紧到可验收口径。",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("让 AI 先给修改建议", use_container_width=True, key=f"suggest_{role}"):
                with st.spinner("AI 正在生成修改建议..."):
                    result = build_agent(role).suggest_revision(st.session_state.analysis, current_doc, feedback)
                st.session_state.feedback_history[role].append({"type": "suggestion", "content": result})
                st.rerun()
        with c2:
            if st.button("直接按要求重写当前文档", use_container_width=True, key=f"revise_{role}"):
                with st.spinner("AI 正在重写文档..."):
                    result = build_agent(role).revise(st.session_state.analysis, current_doc, feedback)
                st.session_state.docs[role] = result
                st.session_state.feedback_history[role].append({"type": "revision", "content": f"已根据反馈重写 {ROLE_LABELS[role]} 文档。"})
                st.rerun()

        history = st.session_state.feedback_history.get(role, [])
        if history:
            st.markdown("**协作记录**")
            for item in history[::-1]:
                with st.expander("修改建议" if item["type"] == "suggestion" else "修订记录", expanded=False):
                    st.markdown(item["content"])

    with tab3:
        st.caption("你可以直接在表里编辑任务安排。")
        edited = st.data_editor(
            st.session_state.task_table,
            num_rows="dynamic",
            use_container_width=True,
            key="task_editor",
            column_config={
                "状态": st.column_config.SelectboxColumn("状态", options=["待开始", "进行中", "已完成", "阻塞"])
            },
        )
        st.session_state.task_table = edited
        st.download_button(
            "下载任务表 CSV",
            data=edited.to_csv(index=False).encode("utf-8-sig"),
            file_name="project_tasks.csv",
            mime="text/csv",
        )
