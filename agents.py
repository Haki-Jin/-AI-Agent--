from __future__ import annotations

import json
import re
from typing import Dict, List

import openai


class BaseAgent:
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

    def call_llm(self, prompt: str, system_prompt: str = "", temperature: float = 0.2, max_tokens: int = 3200) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=120,
            )
            content = response.choices[0].message.content if response and response.choices else ""
            return self._sanitize_output(content or "")
        except Exception as e:
            return f"❌ API调用失败: {e}"

    @staticmethod
    def _sanitize_output(text: str) -> str:
        if not text:
            return ""
        cleaned = text.strip()
        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"```(?:thinking|reasoning|thoughts?)\n.*?```", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"^(思考过程|推理过程|Reasoning|Thoughts?)[:：].*?(?=\n#|\n##|\n\d+\.|$)", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        lines = cleaned.splitlines()
        drop_prefixes = ("思考过程", "推理过程", "Reasoning", "Thought", "Let me think")
        kept = []
        for line in lines:
            if any(line.strip().startswith(p) for p in drop_prefixes):
                continue
            kept.append(line)
        cleaned = "\n".join(kept).strip()
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned

    @staticmethod
    def _norm_text(value, default: str = "未明确") -> str:
        if isinstance(value, str) and value.strip():
            return value.strip()
        return default

    @staticmethod
    def _norm_list(value) -> List[str]:
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip() and str(v).strip() not in {"【待补充】", "待补充"}]
        if isinstance(value, str) and value.strip() and value.strip() not in {"未明确", "无", "【待补充】", "待补充"}:
            parts = re.split(r"[\n；;]", value)
            return [p.strip("- •").strip() for p in parts if p.strip("- •\t \n")]
        return []


class RequirementAnalyzer(BaseAgent):
    FIELD_ORDER = [
        ("需求目标", "goal"),
        ("目标用户", "users"),
        ("核心场景", "core_scenarios"),
        ("核心功能", "core_features"),
        ("成功标准", "success_criteria"),
        ("约束条件", "constraints"),
        ("依赖条件", "dependencies"),
        ("非目标/本期不做", "non_goals"),
        ("MVP范围", "mvp_scope"),
        ("风险与合规点", "risks_and_compliance"),
        ("待确认问题", "unclear_points"),
    ]

    def analyze(self, raw_requirement: str) -> Dict:
        system_prompt = """
你是资深产品经理助手，擅长把模糊想法整理成一份“可继续讨论、可直接修改”的推荐交接单。
要求：
1. 尽量主动拆解，不要把大部分内容都留给用户补充。
2. 允许在明显合理的范围内做“保守推断”，但不要编造具体数值、具体接口、具体技术方案。
3. 输出要有产品思考深度：除了需求目标、目标用户、场景、功能，还要补出 MVP 范围、非目标、风险与合规点。
4. 不明确的地方放入待确认问题，不要在正文中反复写“待补充”。
5. 只输出合法 JSON，不输出解释，不输出代码块，不输出思考过程。
""".strip()
        prompt = f"""
请基于下面的原始需求，生成一份推荐交接单。

【原始需求】
{raw_requirement}

【输出 JSON 结构】
{{
  "goal": "一句话需求目标",
  "users": ["目标用户1", "目标用户2"],
  "core_scenarios": ["核心场景1", "核心场景2"],
  "core_features": ["核心功能1", "核心功能2", "核心功能3"],
  "success_criteria": ["建议成功标准1", "建议成功标准2"],
  "constraints": ["约束条件1", "约束条件2"],
  "dependencies": ["依赖条件1", "依赖条件2"],
  "non_goals": ["本期不做1", "本期不做2"],
  "mvp_scope": ["MVP范围1", "MVP范围2"],
  "risks_and_compliance": ["风险或合规点1", "风险或合规点2"],
  "unclear_points": ["待确认问题1", "待确认问题2"],
  "supplement_suggestions": ["建议补充内容1", "建议补充内容2"],
  "recommended_handoff_markdown": "完整 Markdown 交接单"
}}

要求：
- 尽量从原始需求中主动提炼内容，不要让多数栏目空着。
- 对“成功标准”可以给出建议性的验证口径，但不要乱写精确 KPI 数值。
- 对“依赖条件”可以写成能力依赖或资源依赖，例如用户画像、内容库、对话能力、审核机制、埋点能力。
- “非目标/本期不做”和“MVP范围”必须给出，帮助收紧范围。
- “待确认问题”控制在 3-6 条，问最关键的问题。
- 输出的 recommended_handoff_markdown 要严格按以下顺序：
  需求目标 / 目标用户 / 核心场景 / 核心功能 / 成功标准 / 约束条件 / 依赖条件 / 非目标/本期不做 / MVP范围 / 风险与合规点 / 待确认问题
""".strip()
        raw = self.call_llm(prompt, system_prompt, temperature=0.2, max_tokens=2800)
        data = self._parse_json(raw)
        normalized = self._normalize_result(data, raw_requirement)
        normalized["handoff_packet"] = self.build_handoff_packet(raw_requirement, normalized)
        return normalized

    def _parse_json(self, text: str) -> Dict:
        text = text.strip()
        if text.startswith("❌"):
            return {}
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text).strip()
            text = re.sub(r"```$", "", text).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
        try:
            return json.loads(text)
        except Exception:
            return {}

    def _normalize_result(self, result: Dict, raw_requirement: str) -> Dict:
        normalized = {
            "goal": self._norm_text(result.get("goal"), raw_requirement[:80] if raw_requirement else "未明确"),
            "users": self._norm_list(result.get("users")),
            "core_scenarios": self._norm_list(result.get("core_scenarios")),
            "core_features": self._norm_list(result.get("core_features")),
            "success_criteria": self._norm_list(result.get("success_criteria")),
            "constraints": self._norm_list(result.get("constraints")),
            "dependencies": self._norm_list(result.get("dependencies")),
            "non_goals": self._norm_list(result.get("non_goals")),
            "mvp_scope": self._norm_list(result.get("mvp_scope")),
            "risks_and_compliance": self._norm_list(result.get("risks_and_compliance")),
            "unclear_points": self._norm_list(result.get("unclear_points")),
            "supplement_suggestions": self._norm_list(result.get("supplement_suggestions")),
            "recommended_handoff_markdown": self._norm_text(result.get("recommended_handoff_markdown"), ""),
        }
        normalized["missing_common_info"] = self._build_missing_info(normalized)
        if not normalized["supplement_suggestions"]:
            normalized["supplement_suggestions"] = self._build_supplement_suggestions(normalized["missing_common_info"])
        if not normalized["recommended_handoff_markdown"]:
            normalized["recommended_handoff_markdown"] = self.to_markdown(normalized)
        return normalized

    def _build_missing_info(self, d: Dict) -> List[str]:
        mapping = [
            ("users", "目标用户"),
            ("core_scenarios", "核心场景"),
            ("core_features", "核心功能"),
            ("success_criteria", "成功标准"),
            ("constraints", "约束条件"),
            ("dependencies", "依赖条件"),
        ]
        return [label for key, label in mapping if not d.get(key)]

    def _build_supplement_suggestions(self, missing: List[str]) -> List[str]:
        suggestion_map = {
            "目标用户": "请补充目标用户的年龄段、典型状态、使用动机与敏感程度。",
            "核心场景": "请补充用户在什么触发情境下会打开这个产品，频次如何。",
            "核心功能": "请补充 MVP 必须具备的关键功能和优先级。",
            "成功标准": "请补充你希望看哪些结果来判断产品初步有效，例如完成率、留存、满意度、使用时长等。",
            "约束条件": "请补充时间、合规、内容边界、数据安全、资源约束。",
            "依赖条件": "请补充依赖的数据、系统、模型能力、审核机制或人工协同能力。",
        }
        return [suggestion_map[item] for item in missing if item in suggestion_map]

    def to_markdown(self, d: Dict) -> str:
        def block(title: str, value) -> str:
            if isinstance(value, list):
                body = "\n".join([f"- {x}" for x in value]) if value else "- 【待补充】"
            else:
                body = value or "【待补充】"
            return f"## {title}\n{body}"

        sections = []
        for title, key in self.FIELD_ORDER:
            sections.append(block(title, d.get(key, [] if key != "goal" else "")))
        return "\n\n".join(sections)

    def build_handoff_packet(self, raw_requirement: str, analysis: Dict) -> Dict:
        missing = self._build_missing_info(analysis)
        return {
            "source_requirement": raw_requirement,
            "goal": analysis.get("goal", "未明确"),
            "users": analysis.get("users", []),
            "core_scenarios": analysis.get("core_scenarios", []),
            "core_features": analysis.get("core_features", []),
            "success_criteria": analysis.get("success_criteria", []),
            "constraints": analysis.get("constraints", []),
            "dependencies": analysis.get("dependencies", []),
            "non_goals": analysis.get("non_goals", []),
            "mvp_scope": analysis.get("mvp_scope", []),
            "risks_and_compliance": analysis.get("risks_and_compliance", []),
            "unclear_points": analysis.get("unclear_points", []),
            "missing_common_info": missing,
            "ready_for_handoff": len(missing) == 0,
        }


class DepartmentAgent(BaseAgent):
    role_name = "部门"
    system_prompt = ""
    user_template = ""

    def _handoff_markdown(self, handoff: Dict) -> str:
        analyzer = RequirementAnalyzer(self.api_key, self.model, self.base_url)
        return analyzer.to_markdown(handoff)

    def generate(self, analysis: Dict) -> str:
        handoff = analysis.get("handoff_packet", analysis)
        prompt = self.user_template.format(handoff_markdown=self._handoff_markdown(handoff))
        return self.call_llm(prompt, self.system_prompt, temperature=0.25, max_tokens=3400)

    def revise(self, analysis: Dict, current_doc: str, user_feedback: str) -> str:
        handoff = analysis.get("handoff_packet", analysis)
        prompt = f"""
请基于下面的交接单、当前文档和产品经理反馈，输出修订后的完整文档。
不要解释修改过程，不要输出思考过程，只输出最终修订稿。

【交接单】
{self._handoff_markdown(handoff)}

【当前文档】
{current_doc}

【产品经理反馈】
{user_feedback}
""".strip()
        return self.call_llm(prompt, self.system_prompt, temperature=0.2, max_tokens=3600)

    def suggest_revision(self, analysis: Dict, current_doc: str, user_feedback: str) -> str:
        handoff = analysis.get("handoff_packet", analysis)
        prompt = f"""
你正在协助产品经理审阅{self.role_name}文档。请输出：
1. 问题判断
2. 建议修改点
3. 推荐替换文本
不要输出思考过程。

【交接单】
{self._handoff_markdown(handoff)}

【当前文档】
{current_doc}

【产品经理反馈】
{user_feedback}
""".strip()
        return self.call_llm(prompt, self.system_prompt, temperature=0.3, max_tokens=1800)


class EngineeringAgent(DepartmentAgent):
    role_name = "研发"
    system_prompt = "你是资深后端研发工程师。只输出工程化、可直接开发的需求文档。不输出思考过程，不写代码，不写伪代码，不写SQL。"
    user_template = """
基于以下产品交接单，输出研发侧需求文档。
严格基于交接单，不编造未给出的接口、表结构、技术方案；不明确处标注【需产品补充确认】。
不要输出思考过程。

【产品交接单】
{handoff_markdown}

请固定按以下结构输出：
# 1. 需求目标
# 2. 核心功能模块拆解
# 3. 输入定义
# 4. 输出定义
# 5. 标准执行流程
# 6. 业务与数据规则
# 7. 边界场景处理
# 8. 异常场景处理
# 9. 开发范围
# 10. 前置依赖与约束
""".strip()


class DesignAgent(DepartmentAgent):
    role_name = "设计"
    system_prompt = "你是资深 UI/UX 设计专家。只输出设计视角文档，不混入研发、算法、测试信息。不输出思考过程。"
    user_template = """
基于以下产品交接单，输出设计侧需求文档。
严格依据交接单，不新增需求，不臆造功能。信息不足处标注【需产品补充确认】。
不要输出思考过程。

【产品交接单】
{handoff_markdown}

请按以下结构输出：
# 一、用户任务流程
# 二、页面/界面清单
# 三、页面状态设计
# 四、关键交互点
# 五、异常反馈建议
# 六、视觉层级建议
# 七、设计注意事项
""".strip()


class AIAgent(DepartmentAgent):
    role_name = "算法"
    system_prompt = "你是专业 AI/算法工程师。仅输出算法视角文档，不输出思考过程。"
    user_template = """
基于以下产品交接单，输出算法侧需求文档。
严格依据交接单，不编造不存在的技术能力与数据来源。信息不足处标注【需产品补充确认】。
不要输出思考过程。

【产品交接单】
{handoff_markdown}

请按以下结构输出：
# 1. 算法核心能力定义
# 2. 模型任务与 Prompt 要求
# 3. 评测指标与验收标准
# 4. 输入边界与异常处理
# 5. Fallback 兜底策略
# 6. 算法依赖与资源预估
# 7. 算法假设与风险提示
""".strip()


class QAAgent(DepartmentAgent):
    role_name = "测试"
    system_prompt = "你是资深测试专家。只输出测试视角文档，不输出思考过程，不混入研发实现。"
    user_template = """
基于以下产品交接单，输出测试侧需求文档。
严格依据交接单，不编造功能，不脑补逻辑。信息不足处标注【需产品补充确认】。
不要输出思考过程。

【产品交接单】
{handoff_markdown}

请按以下结构输出：
# 1. 测试目标
# 2. 核心测试点（功能主流程）
# 3. 边界测试场景
# 4. 异常输入与异常场景
# 5. 成功/失败判定标准
# 6. 测试风险与需求模糊点
""".strip()


class OperationAgent(DepartmentAgent):
    role_name = "运营"
    system_prompt = "你是企业级产品运营专家。只输出运营视角文档，不输出思考过程。"
    user_template = """
基于以下产品交接单，输出运营侧需求文档。
严格依据交接单，不夸大价值，不虚构能力。信息不足处标注【需产品补充确认】。
不要输出思考过程。

【产品交接单】
{handoff_markdown}

请按以下结构输出：
# 1. 核心业务价值
# 2. 目标用户与适用场景
# 3. 产品核心卖点
# 4. 上线运营准备事项
# 5. 常见 FAQ（用户 & 内部）
# 6. 运营风险与注意点
""".strip()


class RiskAnalyzer(BaseAgent):
    def analyze(self, analysis: Dict, results: Dict) -> Dict:
        prompt = f"""
你是项目风险分析助手。请根据下面的交接单和各部门文档，输出风险分析。
不要输出思考过程。

【交接单】
{json.dumps(analysis.get('handoff_packet', analysis), ensure_ascii=False, indent=2)}

【部门文档摘要】
- 研发：{results.get('engineering', '')[:600]}
- 设计：{results.get('design', '')[:600]}
- 算法：{results.get('ai', '')[:600]}
- 测试：{results.get('qa', '')[:600]}
- 运营：{results.get('operation', '')[:600]}

请按 JSON 输出：
{{
  "unclear_expressions": ["..."],
  "needs_supplement": ["..."],
  "cross_dept_risks": ["..."],
  "hidden_dependencies": ["..."],
  "feasibility_risks": ["..."],
  "next_steps": ["..."]
}}
""".strip()
        raw = self.call_llm(prompt, "你是资深项目风险分析助手。只输出 JSON，不输出思考过程。", temperature=0.2, max_tokens=1800)
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            parsed = json.loads(raw[start:end + 1]) if start != -1 and end != -1 else {}
        except Exception:
            parsed = {}
        return {
            "unclear_expressions": BaseAgent._norm_list(parsed.get("unclear_expressions")),
            "needs_supplement": BaseAgent._norm_list(parsed.get("needs_supplement")),
            "cross_dept_risks": BaseAgent._norm_list(parsed.get("cross_dept_risks")),
            "hidden_dependencies": BaseAgent._norm_list(parsed.get("hidden_dependencies")),
            "feasibility_risks": BaseAgent._norm_list(parsed.get("feasibility_risks")),
            "next_steps": BaseAgent._norm_list(parsed.get("next_steps")),
            "raw_analysis": raw,
        }
