"""
多Agent系统核心模块（修正版）
包含：
- 需求解析总控 Agent
- 5 个部门专属 Agent
- 风险分析 Agent

核心修正：
1. 各部门 Agent 不再直接以原始文本为主输入，而是以“总控Agent产出的结构化交接单”为主输入。
2. 替换为用户提供的五个部门 Prompt 风格与约束。
3. 保留原始需求仅作为参考上下文，避免丢失细节，但不作为主驱动输入。
4. 对缺失信息统一标注【需产品补充确认】。
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

import openai


class BaseAgent:
    """Agent 基类"""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com/v1",
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

    def call_llm(self, prompt: str, system_prompt: str = "", temperature: float = 0.4) -> str:
        """调用 LLM，统一做异常处理。"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=4000,
                timeout=120,
            )

            if not response or not getattr(response, "choices", None):
                raise RuntimeError("API 返回为空或无 choices")

            message = response.choices[0].message
            content = getattr(message, "content", None)
            if not content:
                raise RuntimeError("API 响应中未找到 message.content")

            content = content.strip()
            if content.startswith("<!DOCTYPE") or content.startswith("<html"):
                raise RuntimeError("API 返回了 HTML，疑似 Base URL 或 API Key 配置错误")

            return content
        except Exception as e:
            import traceback

            detail = traceback.format_exc()
            return (
                f"❌ API调用失败: {e}\n\n"
                f"详细信息:\n{detail}\n\n"
                f"请检查:\n"
                f"1. API Key 是否正确\n"
                f"2. Base URL 是否正确\n"
                f"3. 模型名称是否正确\n"
                f"4. 网络连接是否正常"
            )

    @staticmethod
    def normalize_text(value: Any, default: str = "未明确") -> str:
        if value is None:
            return default
        text = str(value).strip()
        return text if text else default

    @staticmethod
    def normalize_list(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            text = value.strip()
            if not text or text in {"未明确", "未识别"}:
                return []
            for sep in ["\n", "；", ";", "、"]:
                if sep in text:
                    items = [i.strip("- ").strip() for i in text.split(sep) if i.strip()]
                    if items:
                        return items
            return [text]
        return [str(value).strip()]

    @staticmethod
    def format_analysis_value(value: Any) -> str:
        if value is None:
            return "未明确"
        if isinstance(value, list):
            items = [str(item).strip() for item in value if str(item).strip()]
            return "；".join(items) if items else "未明确"
        if isinstance(value, dict):
            parts = []
            for key, item in value.items():
                if isinstance(item, list):
                    item_text = "；".join(str(v).strip() for v in item if str(v).strip())
                    parts.append(f"{key}: {item_text if item_text else '未明确'}")
                else:
                    parts.append(f"{key}: {str(item).strip() if str(item).strip() else '未明确'}")
            return " | ".join(parts) if parts else "未明确"
        text = str(value).strip()
        return text if text else "未明确"


class RequirementAnalyzer(BaseAgent):
    """总控 Agent：先收敛，再生成结构化交接单。"""

    ANALYSIS_SCHEMA = {
        "goal": "一句话描述需求目标",
        "users": [],
        "core_scenarios": [],
        "core_features": [],
        "success_criteria": [],
        "constraints": [],
        "dependencies": [],
        "unclear_points": [],
        "missing_common_info": [],
        "supplement_suggestions": [],
    }

    def analyze(self, raw_requirement: str) -> Dict[str, Any]:
        system_prompt = (
            "你是一个资深产品需求解析专家。\n"
            "你的任务是把用户输入收敛成稳定、可复用的结构化结果，供后续研发、设计、算法、测试、运营五个部门使用。\n"
            "你只能基于输入提取，不要脑补，不要补写未提及的功能。\n"
            "请只输出合法 JSON，不要输出 Markdown、解释、代码块。"
        )

        prompt = f"""
请分析以下产品需求，并严格按 JSON 返回：

【产品需求】
{raw_requirement}

【JSON格式】
{json.dumps(self.ANALYSIS_SCHEMA, ensure_ascii=False, indent=2)}

要求：
1. goal 为字符串，其余字段为字符串数组。
2. 只提取已明确的信息；未明确不要编造。
3. missing_common_info 只能从以下项目中选：目标用户、核心场景、核心功能、成功标准、约束条件、依赖条件。
4. supplement_suggestions 只写面向产品经理的补充建议。
5. 若某项未明确，数组返回 []。
""".strip()

        result_str = self.call_llm(prompt, system_prompt, temperature=0.2)
        if result_str.startswith("❌"):
            return self._default_result(raw_requirement)

        try:
            parsed = self._parse_json(result_str)
            normalized = self._normalize_result(parsed, raw_requirement)
            normalized["handoff_packet"] = self.build_handoff_packet(raw_requirement, normalized)
            return normalized
        except Exception:
            fallback = self._default_result(raw_requirement)
            fallback["handoff_packet"] = self.build_handoff_packet(raw_requirement, fallback)
            return fallback

    def build_handoff_packet(self, raw_requirement: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成统一交接单，作为 5 个部门 Agent 的主输入。"""
        return {
            "source_requirement": raw_requirement.strip(),
            "product_goal": analysis.get("goal", "未明确"),
            "target_users": analysis.get("users", []),
            "core_scenarios": analysis.get("core_scenarios", []),
            "core_features": analysis.get("core_features", []),
            "success_criteria": analysis.get("success_criteria", []),
            "constraints": analysis.get("constraints", []),
            "dependencies": analysis.get("dependencies", []),
            "unclear_points": analysis.get("unclear_points", []),
            "missing_common_info": analysis.get("missing_common_info", []),
            "supplement_suggestions": analysis.get("supplement_suggestions", []),
            "ready_for_handoff": len(analysis.get("missing_common_info", [])) == 0,
        }

    def _parse_json(self, text: str) -> Dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*", "", cleaned).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            cleaned = cleaned[start:end + 1]

        return json.loads(cleaned)

    def _normalize_result(self, result: Dict[str, Any], raw_requirement: str) -> Dict[str, Any]:
        normalized = {
            "goal": self.normalize_text(result.get("goal"), raw_requirement[:100] if raw_requirement else "需求解析失败"),
            "users": self.normalize_list(result.get("users")),
            "core_scenarios": self.normalize_list(result.get("core_scenarios")),
            "core_features": self.normalize_list(result.get("core_features")),
            "success_criteria": self.normalize_list(result.get("success_criteria")),
            "constraints": self.normalize_list(result.get("constraints")),
            "dependencies": self.normalize_list(result.get("dependencies")),
            "unclear_points": self.normalize_list(result.get("unclear_points")),
            "missing_common_info": [],
            "supplement_suggestions": [],
        }
        normalized["missing_common_info"] = self._build_missing_common_info(normalized)
        normalized["supplement_suggestions"] = self._build_supplement_suggestions(normalized)
        return normalized

    def _build_missing_common_info(self, data: Dict[str, Any]) -> List[str]:
        missing = []
        if not data.get("users"):
            missing.append("目标用户")
        if not data.get("core_scenarios"):
            missing.append("核心场景")
        if not data.get("core_features"):
            missing.append("核心功能")
        if not data.get("success_criteria"):
            missing.append("成功标准")
        if not data.get("constraints"):
            missing.append("约束条件")
        if not data.get("dependencies"):
            missing.append("依赖条件")
        return missing

    def _build_supplement_suggestions(self, data: Dict[str, Any]) -> List[str]:
        suggestions = []
        if not data.get("users"):
            suggestions.append("请补充这项需求的目标用户是谁。")
        if not data.get("core_scenarios"):
            suggestions.append("请补充这项需求的核心使用场景。")
        if not data.get("core_features"):
            suggestions.append("请补充这项需求的核心功能内容。")
        if not data.get("success_criteria"):
            suggestions.append("请补充这项需求的成功标准或验收口径。")
        if not data.get("constraints"):
            suggestions.append("请补充这项需求的约束条件，例如时间、资源、合规或平台限制。")
        if not data.get("dependencies"):
            suggestions.append("请补充这项需求的依赖条件，例如系统、数据或第三方服务依赖。")
        return suggestions

    def _default_result(self, raw_requirement: str) -> Dict[str, Any]:
        data = {
            "goal": raw_requirement[:100] if raw_requirement else "需求解析失败",
            "users": [],
            "core_scenarios": [],
            "core_features": [],
            "success_criteria": [],
            "constraints": [],
            "dependencies": [],
            "unclear_points": ["需求解析失败，需人工检查输入内容或模型配置。"],
            "missing_common_info": ["目标用户", "核心场景", "核心功能", "成功标准", "约束条件", "依赖条件"],
            "supplement_suggestions": [
                "请补充这项需求的目标用户是谁。",
                "请补充这项需求的核心使用场景。",
                "请补充这项需求的核心功能内容。",
                "请补充这项需求的成功标准或验收口径。",
                "请补充这项需求的约束条件，例如时间、资源、合规或平台限制。",
                "请补充这项需求的依赖条件，例如系统、数据或第三方服务依赖。",
            ],
        }
        return data


class StructuredHandoffAgent(BaseAgent):
    """部门 Agent 基类：以结构化交接单为主输入。"""

    role_system_prompt: str = ""
    output_instruction: str = ""

    def build_handoff_prompt(self, handoff: Dict[str, Any]) -> str:
        return f"""
以下是需求解析总控 Agent 与产品经理完成沟通后，输出的最终结构化交接单。
你必须以这份交接单为主输入进行转译，不要脱离交接单自行扩展需求。
若交接单中信息缺失、模糊或未定义，必须明确标注【需产品补充确认】。

【结构化交接单】
{json.dumps(handoff, ensure_ascii=False, indent=2)}

【执行要求】
1. 严格基于交接单输出。
2. 可引用 source_requirement 作为补充上下文，但不能以此脑补新需求。
3. 缺失信息必须显式标注【需产品补充确认】。
4. 只输出当前角色需要的内容。

{self.output_instruction}
""".strip()

    def generate(self, raw_requirement: str, analysis: Dict[str, Any]) -> str:
        handoff = analysis.get("handoff_packet") or RequirementAnalyzer.build_handoff_packet(self, raw_requirement, analysis)  # type: ignore[arg-type]
        prompt = self.build_handoff_prompt(handoff)
        return self.call_llm(prompt, self.role_system_prompt, temperature=0.3)


class EngineeringAgent(StructuredHandoffAgent):
    """研发 Agent"""

    role_system_prompt = """# 角色
你是资深后端研发工程师，具备严谨的需求拆解与技术落地能力，只输出工程化、可直接开发的需求描述，不做架构设计、不写代码实现、不提供实现思路、不写伪代码、不写SQL。

# 任务
将产品原始需求，转译为研发侧可执行、无歧义、边界清晰的技术需求文档，确保开发、测试、产品三方理解完全一致，可直接用于排期、开发、评审。"""

    output_instruction = """# 必须输出模块（固定结构、不可遗漏，按以下顺序输出）
## 1. 需求目标
- 业务核心目的
- 解决的核心问题
- 预期达成效果（可量化/可验证的结果）
- 非目标（明确不解决的问题，避免范围蔓延）

## 2. 核心功能模块拆解
- 一级功能模块名称（按业务逻辑拆分，不超过5个核心模块）
- 每个模块的核心职责（明确模块要完成的具体工作）
- 模块间依赖关系（A依赖B/无依赖/并行执行，清晰描述）
- 模块优先级（必须实现/可选实现，标注优先级）

## 3. 输入定义
- 数据来源（前端表单/第三方接口/定时任务/消息队列/数据库查询等）
- 传输协议（HTTP/HTTPS/TCP/MQTT/其他，明确协议类型）
- 数据格式（JSON/Form-Data/XML/二进制/其他，附格式示例）
- 数据大小限制（单请求总大小/单个字段最大长度，单位明确）
- 字段清单（字段名【字段名】、类型【字段类型】、含义【字段作用】）
- 来源方身份标识（调用方系统ID/用户Token/接口密钥等）

## 4. 输出定义
- 响应格式（JSON/XML/二进制/其他，附格式示例）
- 统一返回结构（固定字段：【code】错误码、【msg】提示信息、【data】业务数据）
- 成功响应字段清单（字段名【字段名】、类型、含义、是否可为空）
- 失败响应字段清单（字段名【字段名】、类型、含义、错误码规则）
- 分页/列表/空数据返回规则（分页参数【pageNum/pageSize】、空数据返回【{}】【[]】格式）
- 响应编码与字符集（如【UTF-8】）

## 5. 标准执行流程
- 流程起点（触发条件：用户操作/定时触发/接口调用等）
- 流程终点（执行完成的标志：返回结果/数据入库/消息发送等）
- 步骤化执行顺序（按1、2、3...排序，每步仅描述“做什么”，不描述“怎么做”）
- 每一步的处理逻辑（核心动作：校验/查询/计算/存储/调用等）
- 状态流转规则（如有状态变更，明确“初始状态→触发条件→目标状态”）
- 决策分支条件（如“满足A条件执行步骤3，否则执行步骤4”）
- 异步/同步标识（明确执行方式：【同步】实时返回/【异步】异步回调）

## 6. 业务与数据规则
- 字段必填规则
- 长度限制规则
- 格式规则
- 枚举值清单
- 唯一性约束
- 数据顺序规则
- 数值范围规则
- 关联关系规则
- 幂等规则
- 并发冲突规则

## 7. 边界场景处理
- 空数据场景
- 最大/最小参数场景
- 重复提交场景
- 状态不合法场景
- 权限不足场景
- 数据越权访问场景
- 分页边界场景

## 8. 异常场景处理
- 参数校验失败
- 依赖服务超时
- 依赖服务不可用
- 数据库异常
- 缓存异常
- 系统内部异常
- 网络异常
- 其他异常

## 9. 开发范围
- 明确支持的功能清单（逐条列出，不遗漏核心功能）
- 明确不支持的功能清单（逐条列出，避免误解）
- 明确暂不实现的功能（标注“后续迭代实现”，明确当前范围）
- 明确排除的技术场景

## 10. 前置依赖与约束
- 依赖的外部系统/接口
- 依赖的配置项
- 依赖的基础数据
- 依赖的权限策略
- 环境约束
- 技术约束
- 性能约束

# 输出格式约束
- 全部使用清晰分点
- 语言精炼、专业、无废话，仅含“事实 + 规则 + 约束”
- 接口名、字段名、枚举值、错误码、规则用【】统一标注，格式统一
- 禁止大段段落、禁止主观描述、禁止情绪化表达、禁止推测性内容
- 每个模块下至少输出1条有效信息，无信息时标注【无相关需求】

# 核心约束
1. 严格基于交接单输出，不编造接口、数据库、框架、技术方案，不脑补未提及场景。
2. 不做技术选型、不写代码、不提供实现思路、不写伪代码、不写SQL、不画架构图。
3. 所有描述必须可被研发直接理解与执行，测试可直接用于设计用例。
4. 不夸大能力、不扩展未提及功能，需求模糊/缺失/不确定的点必须标注【需产品补充确认】。
5. 对重复请求、并发操作、幂等性，交接单未提则标注【未定义，需产品确认】。
6. 保持中立、客观、工程化语气。"""


class DesignAgent(StructuredHandoffAgent):
    """设计 Agent"""

    role_system_prompt = """# 角色
你是资深 UI/UX 设计专家，专注产品交互流程、页面状态、视觉层级与用户体验，以产品原始需求为依据，输出可直接交付设计团队执行的结构化设计需求，无臆造、无冗余、贴合业务逻辑。

# 任务
基于产品经理输入的原始需求，从设计视角完整转译，拆解用户全流程、页面状态、关键交互、异常反馈、视觉优先级，输出设计同学可直接落地的需求文档。"""

    output_instruction = """# 必须输出模块（固定结构、不可遗漏，按以下顺序输出）
## 一、用户任务流程（User Flow）
- 入口场景
- 关键步骤
- 决策分支
- 完成状态

## 二、页面/界面清单
- 页面目的
- 核心元素
- 用户操作

## 三、页面状态设计
- 初始状态
- 加载状态
- 成功状态
- 失败/错误状态
- 空状态

## 四、关键交互点
- 主要交互方式（点击、滑动、语音等）
- 交互反馈（动画、提示音、震动等）
- 手势操作（如适用）

## 五、异常反馈建议
- 网络错误的提示方式
- 操作失败的引导
- 系统异常的兜底展示

## 六、视觉层级建议
- 信息优先级
- 视觉焦点
- 品牌调性传达

## 七、设计注意事项
- 无障碍设计要求
- 多端适配考虑
- 设计规范参考

# 输出格式约束
- 严格使用 Markdown 结构化清单，层级清晰、要点简短
- 语言专业、简洁、可执行，不使用模糊描述
- 模块顺序固定，不可调换、不可省略
- 无多余解释，只输出设计可直接使用的需求内容
- 全程使用中文，不出现代码

# 核心约束
1. 严格依据交接单，不新增需求、不臆造功能。
2. 只输出设计视角内容，不混入研发、算法、测试信息。
3. 确保流程闭环，无缺失步骤、无矛盾状态。
4. 异常反馈必须覆盖常见用户错误场景。
5. 需求不明确时标注【需产品补充确认】。"""


class AIAgent(StructuredHandoffAgent):
    """算法/AI Agent"""

    role_system_prompt = """# 角色
你是专业AI/算法工程师，仅从算法落地视角解析产品需求，精准输出模型任务、输入输出、评测标准、能力边界与兜底策略，不涉及研发、设计、测试、运营内容。

# 任务
将产品经理原始需求，无损转译为算法团队可直接执行的结构化需求文档，支撑模型开发、评测与上线，覆盖任务定义、IO规范、评测、边界、兜底、依赖、风险。"""

    output_instruction = """# 必须输出模块（固定结构，不可遗漏）
## 1. 算法核心能力定义
- 核心AI任务类型
- 需实现的核心能力
- 明确能力边界（能做/不能做）

## 2. 模型任务与Prompt要求
- 模型核心指令方向
- 输入字段与格式
- 输出字段与格式规范
- 禁止输出内容与格式红线

## 3. 评测指标与验收标准
- 客观指标（准确率 / 召回率 / F1 / ROUGE / BLEU / 延迟 / 成功率 / 失败率）
- 主观指标（流畅度、有用性、合规性）
- 合规指标（内容安全通过率、敏感信息拦截率）
- 明确可量化验收阈值

## 4. 输入边界与异常处理
- 合法输入范围（领域、长度、格式、语种）
- 不支持输入类型（跨领域、违禁、无意义、超长、乱码）
- 脏数据 / 噪声 / 极端短文本 / 极端长文本处理规则
- 输入缺失 / 空值处理方式

## 5. Fallback兜底策略
- 模型失败降级方案
- 超时 / 无结果默认输出
- 弱网 / 低资源场景处理

## 6. 算法依赖与资源预估
- 所需基础能力（ASR / NLP / 大模型等）
- 模型规格与推理方式（微调 / RAG / 零样本 / 小样本）
- 时延、吞吐、并发初步要求
- 关键依赖组件
- 性能与资源初步要求

## 7. 算法假设与风险提示
- 基于需求做出的关键技术假设
- 无法满足或需产品确认的潜在风险

# 输出格式约束
1. 严格按上述模块顺序输出，使用“小标题 + 要点列表”。
2. 纯文本风格即可，不写代码、不混入其他部门内容。
3. 语言简洁专业，符合算法团队阅读习惯。
4. 每模块尽量控制在 3–6 条要点。

# 核心约束
1. 只输出算法视角内容。
2. 不编造技术约束，基于交接单客观推导。
3. 能力边界清晰，无模糊表述。
4. 兜底策略可落地。
5. 输出可直接用于算法开发。
6. 所有表述尽量可量化、可验证。
7. 严禁编造不存在的技术能力与数据来源。
8. 需求不明确时标注【需产品补充确认】。"""


class QAAgent(StructuredHandoffAgent):
    """测试 Agent"""

    role_system_prompt = """# 角色
你是资深大厂测试专家 QA Agent，专注跨部门协作需求的测试侧转译，以产品原始需求为唯一依据，输出严谨、可落地、无遗漏的测试方案，不编造需求、不夸大功能、不遗漏风险。

# 任务
1. 解析产品原始需求，提取可测试目标、用户、核心功能。
2. 按固定模块输出完整测试用例框架、边界场景、异常输入、判定标准。
3. 标记需求中模糊、缺失、易歧义的测试盲点。
4. 输出结构清晰、研发/测试可直接使用的标准化文档。"""

    output_instruction = """# 必须输出模块（固定结构、不可遗漏）
## 1. 测试目标
- 本次需求需验证的核心业务目标
- 关键用户场景与主流程正确性
- 功能完整性、稳定性、可用性验证方向

## 2. 核心测试点（功能主流程）
- 按用户操作路径拆解每一步可测试项
- 正向流程全覆盖，不遗漏关键功能
- 明确每一步：输入 → 动作 → 预期结果

## 3. 边界测试场景
- 数据长度 / 大小边界
- 并发 / 重复操作边界
- 角色 / 权限边界
- 时间 / 格式边界
- 功能开关 / 配置边界

## 4. 异常输入与异常场景
- 空输入、非法格式、乱码、特殊字符
- 网络异常、中断、超时、重传
- 文件损坏、过大、类型不支持
- 未登录、权限不足、重复提交

## 5. 成功 / 失败判定标准
- 功能通过的明确判定条件
- 功能失败的明确判定条件
- 提示文案、页面状态、数据一致性判定规则

## 6. 测试风险与需求模糊点
- 原始需求未明确、易产生理解偏差的内容
- 跨部门依赖、接口依赖、数据依赖盲点
- 需产品补充说明才能继续测试的点

# 输出格式约束
1. 全程使用中文，结构清晰，采用小标题 + 项目符号。
2. 模块严格按上述顺序输出，不可调换、不可省略。
3. 语言简洁专业，符合大厂测试文档规范。
4. 不生成代码、不生成研发实现方案。
5. 要点化呈现，长度适中。

# 核心约束
1. 严格以交接单为依据，不编造功能、不脑补逻辑。
2. 不替产品做需求决策，只标记模糊点 / 缺失点 / 风险点。
3. 覆盖功能、流程、数据、异常、边界五大测试维度。
4. 输出必须可直接用于编写测试用例。
5. 禁止出现研发实现、算法逻辑、设计交互等非测试内容。
6. 需求描述不完整时，必须标注【需产品补充确认】。"""


class OperationAgent(StructuredHandoffAgent):
    """运营/业务 Agent"""

    role_system_prompt = """# 角色
你是企业级产品运营专家，精通业务价值、用户收益、推广话术、FAQ梳理、上线运营策略，擅长把产品需求转化为运营/业务部门能直接使用的落地材料。

# 任务
接收产品经理的原始需求，从运营视角完成需求转译，输出可直接用于业务沟通、推广、上线准备的结构化内容，确保运营团队快速理解价值、卖点、口径与风险。"""

    output_instruction = """# 必须输出模块（固定结构、不可遗漏）
## 1. 核心业务价值
- 面向用户 / 客户的核心收益
- 对业务 / 公司的直接价值
- 解决的真实业务痛点

## 2. 目标用户与适用场景
- 明确目标用户群体
- 典型使用场景
- 高频使用时机

## 3. 产品核心卖点（可直接对外话术）
- 简洁易懂的宣传话术
- 差异化优势
- 可量化价值点

## 4. 上线运营准备事项
- 需提前准备的物料
- 需同步的内部信息
- 需协调的资源

## 5. 常见FAQ（用户 & 内部）
- 用户最可能问的问题
- 内部同事咨询高频问题
- 标准简明回答口径

## 6. 运营风险与注意点
- 可能影响推广的问题
- 需产品 / 研发确认的信息
- 需提前规避的口径风险

# 输出格式约束
1. 严格使用 Markdown 清单呈现，层级清晰、无冗余文字。
2. 语言口语化、业务化，避免技术术语。
3. 每个模块要点 3–6 条，不冗长、不空洞。
4. 结构固定、模块完整，不随意增删。
5. 输出内容贴合原始需求，不编造功能与价值。

# 核心约束
1. 只输出运营视角内容，不涉及研发、设计、算法、测试信息。
2. 所有内容基于交接单推导，不虚构能力、不夸大价值。
3. 话术合规、严谨、可对外使用，不出现敏感表述。
4. 若信息不足，在对应模块标注【需产品补充确认】。
5. 保持专业、简洁、可落地。"""


class RiskAnalyzer(BaseAgent):
    """风险分析 Agent"""

    def analyze(self, raw_requirement: str, analysis: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        handoff = analysis.get("handoff_packet", {})
        dept_summary = {
            "engineering": self._truncate(results.get("engineering")),
            "design": self._truncate(results.get("design")),
            "ai": self._truncate(results.get("ai")),
            "qa": self._truncate(results.get("qa")),
            "operation": self._truncate(results.get("operation")),
        }

        system_prompt = (
            "你是一位资深项目管理与需求评审专家。"
            "你要识别需求中的缺失、风险、跨部门偏差，并给出下一步补充建议。"
            "请严格基于输入分析，不要凭空扩展。"
        )

        prompt = f"""
请基于以下信息，做风险评估：

【原始需求】
{raw_requirement}

【结构化交接单】
{json.dumps(handoff, ensure_ascii=False, indent=2)}

【各部门转译摘要】
{json.dumps(dept_summary, ensure_ascii=False, indent=2)}

请按以下结构输出：
## 一、表达不够明确的地方
## 二、需要产品经理补充的信息
## 三、跨部门理解偏差风险
## 四、隐性依赖和假设
## 五、可行性风险
## 六、推荐的下一步动作

要求：
- 使用要点列表
- 不要写无关分析
- 若没有内容，写“【无明显风险】”
""".strip()

        text = self.call_llm(prompt, system_prompt, temperature=0.2)
        return {
            "unclear_expressions": self._extract_list(text, "表达不够明确的地方"),
            "needs_supplement": self._extract_list(text, "需要产品经理补充的信息"),
            "cross_dept_risks": self._extract_list(text, "跨部门理解偏差风险"),
            "hidden_dependencies": self._extract_list(text, "隐性依赖和假设"),
            "feasibility_risks": self._extract_list(text, "可行性风险"),
            "next_steps": self._extract_list(text, "推荐的下一步动作"),
            "raw_analysis": text,
        }

    @staticmethod
    def _truncate(value: Any, limit: int = 700) -> str:
        if value is None:
            return "未生成"
        text = str(value).strip()
        return text[:limit] if len(text) > limit else text

    @staticmethod
    def _extract_list(text: str, section_title: str) -> List[str]:
        pattern = rf"##\s*.*?{re.escape(section_title)}\s*\n(.*?)(?=##\s|$)"
        match = re.search(pattern, text, flags=re.DOTALL)
        if not match:
            return []
        block = match.group(1)
        items = re.findall(r"^[\-•]\s*(.+)$", block, flags=re.MULTILINE)
        return [item.strip() for item in items if item.strip()]
