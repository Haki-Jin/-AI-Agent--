"""
多Agent系统核心模块
包含：需求解析Agent + 5个部门专属Agent + 风险分析Agent
"""

import openai
from typing import Dict, List


class BaseAgent:
    """Agent基类"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
    
    def call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """调用LLM生成回复"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=4000,  # 增加token限制
                timeout=120
            )
            
            # 检查响应是否存在
            if not response:
                raise Exception("API返回空响应")
            
            # 尝试多种方式获取响应内容，兼容不同API格式
            content = None
            
            # 方式1: 标准OpenAI格式 response.choices[0].message.content
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                if hasattr(choice, 'message') and choice.message:
                    if hasattr(choice.message, 'content') and choice.message.content:
                        content = choice.message.content
            
            # 方式2: 某些API可能直接返回字符串
            if content is None and isinstance(response, str):
                content = response
            
            # 方式3: 检查是否有其他属性
            if content is None:
                if hasattr(response, 'data'):
                    content = str(response.data)
                elif hasattr(response, 'text'):
                    content = response.text
                elif hasattr(response, 'content'):
                    content = response.content
            
            if content is None:
                raise Exception(f"无法解析API响应。响应类型: {type(response).__name__}")
            
            content = content.strip()
            
            # 检查是否返回了HTML错误页面（常见于API配置错误）
            if content.startswith('<!DOCTYPE') or content.startswith('<html') or '<style>' in content[:500]:
                raise Exception("API返回了HTML错误页面，请检查Base URL和API Key是否正确")
            
            # 检查是否包含明显的错误信息
            if 'error' in content.lower() and len(content) < 500:
                print(f"[WARNING] API可能返回错误信息: {content[:200]}")
            
            return content
            
        except Exception as e:
            # 返回详细的错误信息
            import traceback
            error_detail = traceback.format_exc()
            error_msg = f"❌ API调用失败: {str(e)}\n\n详细信息:\n{error_detail}\n\n请检查:\n1. API Key是否正确\n2. Base URL是否正确\n3. 模型名称是否正确\n4. 网络连接是否正常"
            import sys
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            return error_msg


class RequirementAnalyzer(BaseAgent):
    """总控Agent：需求解析"""
    
    def analyze(self, raw_requirement: str) -> Dict:
        """解析原始需求，提取关键信息"""
        
        system_prompt = """你是一个资深产品专家，擅长分析产品需求文档。
请从以下维度解析需求：
1. 需求目标：这个功能要解决什么问题
2. 目标用户：谁会使用这个功能
3. 核心功能点：主要功能模块有哪些
4. 不明确点：哪些地方描述不够清晰
5. 依赖模块：需要哪些技术或业务支持

请严格按照JSON格式返回结果，不要添加任何其他文字说明。"""
        
        prompt = f"""请分析以下产品需求，并严格按照JSON格式返回：

【产品需求】
{raw_requirement}

【返回格式】
{{
    "goal": "需求目标描述",
    "users": "目标用户描述",
    "core_features": "核心功能点1；核心功能点2；核心功能点3",
    "unclear_points": "不明确点1；不明确点2",
    "dependencies": "依赖模块1；依赖模块2"
}}

请确保所有字段都有值，如果没有明确信息，请根据需求合理推断。"""
        
        try:
            result_str = self.call_llm(prompt, system_prompt)
            
            # 检查是否返回了错误信息
            if result_str.startswith("❌"):
                print(f"[ERROR] API返回错误: {result_str[:200]}")
                return self._get_default_result(raw_requirement)
            
            # 打印原始响应（调试用）
            print(f"[DEBUG] 原始API响应前200字符: {result_str[:200]}")
            
            # 尝试解析JSON
            import json
            try:
                # 清理可能的代码块标记
                cleaned_str = result_str.strip()
                
                # 移除可能的markdown代码块
                if cleaned_str.startswith("```"):
                    # 找到第一个换行后的内容
                    lines = cleaned_str.split('\n')
                    cleaned_str = '\n'.join(lines[1:])  # 跳过第一行 ```json
                
                if cleaned_str.endswith("```"):
                    lines = cleaned_str.split('\n')
                    cleaned_str = '\n'.join(lines[:-1])  # 移除最后一行 ```
                
                cleaned_str = cleaned_str.strip()
                
                # 尝试找到JSON对象的开始和结束
                start_idx = cleaned_str.find('{')
                end_idx = cleaned_str.rfind('}')
                
                if start_idx != -1 and end_idx != -1:
                    json_str = cleaned_str[start_idx:end_idx+1]
                else:
                    json_str = cleaned_str
                
                print(f"[DEBUG] 清理后的JSON字符串前200字符: {json_str[:200]}")
                
                result_dict = json.loads(json_str)
                print(f"[SUCCESS] JSON解析成功，字段: {list(result_dict.keys())}")
                
                return {
                    "goal": result_dict.get("goal", "未识别"),
                    "users": result_dict.get("users", "未识别"),
                    "core_features": result_dict.get("core_features", "未识别"),
                    "unclear_points": result_dict.get("unclear_points", "未识别"),
                    "dependencies": result_dict.get("dependencies", "未识别")
                }
            except (json.JSONDecodeError, AttributeError) as json_err:
                # JSON解析失败，使用正则提取
                print(f"[WARNING] JSON解析失败: {json_err}")
                print(f"[DEBUG] 尝试使用正则提取...")
                
                result = {
                    "goal": self._extract_field(result_str, "goal"),
                    "users": self._extract_field(result_str, "users"),
                    "core_features": self._extract_field(result_str, "core_features"),
                    "unclear_points": self._extract_field(result_str, "unclear_points"),
                    "dependencies": self._extract_field(result_str, "dependencies")
                }
                
                # 记录提取结果
                for key, value in result.items():
                    if value != "未识别":
                        print(f"[SUCCESS] 成功提取 {key}: {value[:50]}...")
                
                # 如果所有字段都是"未识别"，返回默认值
                if all(v == "未识别" for v in result.values()):
                    print(f"[WARNING] 所有字段均未识别，使用默认值")
                    return self._get_default_result(raw_requirement)
                
                return result
        except Exception as e:
            # 如果解析失败，返回基础结构
            print(f"[ERROR] analyze方法异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._get_default_result(raw_requirement)
    
    def _get_default_result(self, raw_requirement: str) -> Dict:
        """返回默认的解析结果"""
        return {
            "goal": raw_requirement[:100] if raw_requirement else "需求解析失败",
            "users": "未明确",
            "core_features": "待分析",
            "unclear_points": "需要进一步澄清",
            "dependencies": "待评估"
        }
    
    def _extract_field(self, text: str, field: str) -> str:
        """从文本中提取字段值（支持多种格式）"""
        import re
        
        # 定义字段名映射（英文key -> 中文名称）
        field_names = {
            "goal": ["需求目标"],
            "users": ["目标用户"],
            "core_features": ["核心功能点", "核心功能"],
            "unclear_points": ["不明确点", "不明确"],
            "dependencies": ["依赖模块", "依赖"]
        }
        
        # 尝试1: JSON格式 "field": "value" 或 "中文名称": "value"
        for name in [field] + field_names.get(field, []):
            pattern = rf'"{name}"\s*:\s*"([^"]+)"'
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # 尝试2: 中文名称：value 或 中文名称:value（支持多行）
        for name in field_names.get(field, []):
            # 匹配从名称到下一个字段或结尾的所有内容
            pattern = rf'{name}[：:]\s*([^\n]+?)(?="\w+"[：:]|$)'
            match = re.search(pattern, text)
            if match:
                result = match.group(1).strip().strip('"')
                if result:
                    return result
        
        # 尝试3: 英文field：value
        pattern = rf'{field}[：:]\s*"?([^"\n]+)"?'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        
        return "未识别"


class EngineeringAgent(BaseAgent):
    """研发Agent：关注功能逻辑、接口、异常、开发边界"""
    
    def generate(self, raw_requirement: str, analysis: Dict) -> str:
        """生成研发版本需求文档"""
        
        system_prompt = """你是一位资深技术负责人，擅长将产品需求转化为技术实现方案。
关注点：
- 功能模块拆解和技术实现
- API接口设计
- 数据流程和状态管理
- 异常处理和边界情况
- 技术选型建议和注意事项
- 性能和安全考虑

输出风格：专业、具体、可执行"""
        
        prompt = f"""基于以下产品需求和分析结果，生成给研发团队的需求文档：

【原始需求】
{raw_requirement}

【需求分析】
- 目标：{analysis.get('goal', '')}
- 用户：{analysis.get('users', '')}
- 核心功能：{analysis.get('core_features', '')}

请按照以下结构输出：

## 一、功能模块拆解
列出所有需要开发的功能模块，每个模块说明技术实现要点

## 二、核心流程
描述主要的业务流程和技术流程

## 三、输入输出定义
- 输入：数据类型、格式要求、限制条件
- 输出：数据结构、返回格式

## 四、API接口设计（初步）
列出关键接口及其职责

## 五、异常情况和边界处理
- 可能的异常情况
- 边界条件处理
- 降级策略

## 六、技术注意事项
- 性能要求
- 安全考虑
- 兼容性要求
- 技术债务风险

## 七、开发边界
明确什么要做，什么不做"""
        
        return self.call_llm(prompt, system_prompt)


class DesignAgent(BaseAgent):
    """设计Agent：关注用户流程、页面状态、交互反馈、视觉层级"""
    
    def generate(self, raw_requirement: str, analysis: Dict) -> str:
        """生成设计版本需求文档"""
        
        system_prompt = """你是一位资深UX/UI设计师，擅长从用户体验角度解读产品需求。
关注点：
- 用户任务流程和journey map
- 页面状态和状态转换
- 关键交互点和反馈机制
- 视觉层级和信息架构
- 可用性和无障碍考虑
- 设计规范和一致性

输出风格：用户中心、体验导向、可视化思维"""
        
        prompt = f"""基于以下产品需求和分析结果，生成给设计团队的需求文档：

【原始需求】
{raw_requirement}

【需求分析】
- 目标：{analysis.get('goal', '')}
- 用户：{analysis.get('users', '')}
- 核心功能：{analysis.get('core_features', '')}

请按照以下结构输出：

## 一、用户任务流程（User Flow）
描述用户完成核心任务的完整流程，包括：
- 入口场景
- 关键步骤
- 决策分支
- 完成状态

## 二、页面/界面清单
列出所有需要设计的页面或界面，说明：
- 页面目的
- 核心元素
- 用户操作

## 三、页面状态设计
对关键页面说明：
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
- 设计规范参考"""
        
        return self.call_llm(prompt, system_prompt)


class AIAgent(BaseAgent):
    """算法/AI Agent：关注输入输出、模型能力、评测标准、兜底策略"""
    
    def generate(self, raw_requirement: str, analysis: Dict) -> str:
        """生成算法/AI版本需求文档"""
        
        system_prompt = """你是一位资深AI算法工程师，擅长将产品需求转化为AI技术方案。
关注点：
- AI能力定义和边界
- 模型选择和Prompt工程
- 输入输出格式规范
- 评测指标和验收标准
- Fallback和兜底策略
- 数据需求和标注规范
- 性能和成本平衡

输出风格：技术严谨、量化指标、可评测"""
        
        prompt = f"""基于以下产品需求和分析结果，生成给算法/AI团队的需求文档：

【原始需求】
{raw_requirement}

【需求分析】
- 目标：{analysis.get('goal', '')}
- 用户：{analysis.get('users', '')}
- 核心功能：{analysis.get('core_features', '')}

请按照以下结构输出：

## 一、AI能力定义
明确哪些功能需要AI能力，哪些是传统开发：
- AI负责的功能模块
- 传统开发负责的功能模块
- 能力边界和限制

## 二、模型/算法任务拆解
对每个AI功能说明：
- 任务类型（分类、生成、抽取等）
- 推荐模型或技术方案
- 技术难点和风险

## 三、Prompt设计（如适用）
- System Prompt建议
- Few-shot示例
- 输出格式约束
- 温度等参数建议

## 四、输入输出规范
### 输入
- 数据类型和格式
- 预处理要求
- 长度/大小限制
- 质量要求

### 输出
- 输出格式（JSON/文本等）
- 字段定义
- 置信度要求
- 后处理逻辑

## 五、评测指标
- 核心指标（准确率、召回率、F1等）
- 业务指标（用户满意度、转化率等）
- 性能指标（响应时间、QPS等）
- 验收标准（具体数值）

## 六、Fallback策略
当AI效果不佳时的兜底方案：
- 规则引擎兜底
- 人工审核流程
- 降级展示方案
- 错误提示文案

## 七、数据需求
- 训练数据需求量和质量
- 标注规范和工具
- 数据隐私和合规
- 数据更新频率

## 八、性能和成本
- 推理延迟要求
- 并发处理能力
- Token消耗预估
- 成本优化建议"""
        
        return self.call_llm(prompt, system_prompt)


class QAAgent(BaseAgent):
    """测试Agent：关注测试用例、边界情况、异常场景"""
    
    def generate(self, raw_requirement: str, analysis: Dict) -> str:
        """生成测试版本需求文档"""
        
        system_prompt = """你是一位资深QA工程师，擅长从测试角度发现需求漏洞。
关注点：
- 功能测试点和测试用例
- 边界值和异常输入
- 成功/失败判定标准
- 自动化测试可行性
- 回归测试范围
- 性能和压力测试
- 兼容性和安全性测试

输出风格：全面、细致、可执行、可量化"""
        
        prompt = f"""基于以下产品需求和分析结果，生成给测试团队的需求文档：

【原始需求】
{raw_requirement}

【需求分析】
- 目标：{analysis.get('goal', '')}
- 用户：{analysis.get('users', '')}
- 核心功能：{analysis.get('core_features', '')}

请按照以下结构输出：

## 一、测试范围
- 需要测试的功能模块
- 不需要测试的范围
- 测试优先级划分

## 二、核心测试点
对每个功能模块列出：
- 正常流程测试
- 关键路径验证
- 业务规则校验

## 三、边界场景测试
- 输入边界（最大值、最小值、空值等）
- 状态边界（首次使用、极限状态等）
- 时间边界（超时、并发等）
- 数量边界（大量数据、高频操作等）

## 四、异常输入测试
- 非法格式输入
- 缺失必填项
- 超长/超短输入
- 特殊字符注入
- 网络异常场景
- 服务端异常

## 五、成功/失败判定标准
### 成功标准
- 功能层面的成功定义
- 性能层面的成功定义
- 用户体验层面的成功定义

### 失败标准
- 什么情况算Bug
- 什么情况需要回滚
- 什么情况可以接受

## 六、兼容性测试
- 浏览器/设备兼容
- 操作系统版本
- 屏幕分辨率
- 网络环境

## 七、性能测试
- 响应时间要求
- 并发用户数
- 吞吐量要求
- 资源占用限制

## 八、安全性测试
- 权限控制验证
- 数据加密检查
- 防注入测试
- 敏感信息保护

## 九、自动化测试建议
- 适合自动化的场景
- 自动化框架建议
- 测试数据准备
- CI/CD集成

## 十、回归测试范围
- 可能影响的已有功能
- 需要回归的模块
- 回归测试策略"""
        
        return self.call_llm(prompt, system_prompt)


class OperationAgent(BaseAgent):
    """运营/业务Agent：关注上线价值、用户收益、指标变化、FAQ"""
    
    def generate(self, raw_requirement: str, analysis: Dict) -> str:
        """生成运营/业务版本需求文档"""
        
        system_prompt = """你是一位资深运营专家，擅长从业务价值角度解读产品功能。
关注点：
- 用户价值和商业价值
- 目标人群和适用场景
- 卖点和营销话术
- 关键指标和预期变化
- 常见问题和用户教育
- 上线节奏和推广策略
- 竞品对比和差异化

输出风格：业务导向、用户视角、数据驱动"""
        
        prompt = f"""基于以下产品需求和分析结果，生成给运营/业务团队的需求文档：

【原始需求】
{raw_requirement}

【需求分析】
- 目标：{analysis.get('goal', '')}
- 用户：{analysis.get('users', '')}
- 核心功能：{analysis.get('core_features', '')}

请按照以下结构输出：

## 一、用户价值
- 解决了用户什么痛点
- 为用户带来什么收益
- 用户使用场景描述
- 用户故事（User Story）

## 二、商业价值
- 对业务的贡献
- 变现模式（如适用）
- ROI预估
- 战略意义

## 三、目标人群
- 核心用户画像
- 次要用户群体
- 不适用人群
- 用户规模预估

## 四、卖点话术
### 对外宣传
- 一句话介绍
- 核心卖点（3-5个）
- 应用场景举例
- 用户证言模板

### 对内培训
- 功能亮点
- 常见疑问解答
- 销售/客服话术

## 五、关键指标
### 北极星指标
- 核心成功指标
- 目标数值

### 过程指标
- 使用率/渗透率
- 活跃度
- 留存率
- 转化率

### 预期变化
- 上线前基线
- 上线后预期
- 达成时间

## 六、常见问题（FAQ）
### 用户侧
- 这是什么功能？
- 怎么用？
- 收费吗？
- 数据安全吗？
- 效果不好怎么办？

### 内部侧
- 技术原理是什么？
- 有什么限制？
- 出现问题找谁？

## 七、上线节奏建议
- MVP版本范围
- 灰度发布策略
- 全量上线时间
- 后续迭代计划

## 八、推广策略
- 渠道选择
- 内容营销
- 活动策划
- KOL合作（如适用）

## 九、竞品对比
- 市场上类似产品
- 我们的优势
- 我们的劣势
- 差异化策略

## 十、风险和应对
- 用户接受度风险
- 舆情风险
- 合规风险
- 应对预案"""
        
        return self.call_llm(prompt, system_prompt)


class RiskAnalyzer(BaseAgent):
    """风险分析Agent：识别不明确点、补充需求、跨部门偏差"""
    
    def analyze(self, raw_requirement: str, analysis: Dict, results: Dict) -> Dict:
        """分析需求中的风险和不确定性"""
        
        system_prompt = """你是一位资深项目管理专家，擅长识别需求中的风险和不确定性。
关注点：
- 表达不清晰的地方
- 需要补充的信息
- 跨部门理解偏差
- 隐性依赖和假设
- 可行性风险
- 下一步行动建议

输出风格：批判性思维、建设性意见、 actionable"""
        
        prompt = f"""基于以下产品需求、分析结果和各部门转译版本，进行风险评估：

【原始需求】
{raw_requirement}

【需求分析】
{analysis}

【各部门转译结果摘要】
- 研发版本：{results.get('engineering', '')[:500] if results.get('engineering') else '未生成'}
- 设计版本：{results.get('design', '')[:500] if results.get('design') else '未生成'}
- AI版本：{results.get('ai', '')[:500] if results.get('ai') else '未生成'}
- 测试版本：{results.get('qa', '')[:500] if results.get('qa') else '未生成'}
- 运营版本：{results.get('operation', '')[:500] if results.get('operation') else '未生成'}

请分析并回答以下问题：

## 一、表达不够明确的地方
列出需求中模糊、歧义或不具体的表述，例如：
- "快速响应" - 没有具体时间
- "用户友好" - 没有明确标准
- 等等

## 二、需要产品经理补充的信息
列出缺失的关键信息，例如：
- 目标用户的具体特征
- 性能指标的具体数值
- 预算和时间约束
- 等等

## 三、跨部门理解偏差风险
指出可能导致不同部门理解不一致的地方，例如：
- 研发和设计对某个功能的理解可能不同
- 算法和业务对效果的预期可能有差距
- 等等

## 四、隐性依赖和假设
识别未被明确说明但实际存在的依赖，例如：
- 依赖某个第三方服务
- 假设用户有某种使用习惯
- 等等

## 五、可行性风险
- 技术可行性风险
- 时间可行性风险
- 资源可行性风险
- 合规风险

## 六、推荐的下一步动作
给出具体、可执行的建议，例如：
- 与XX部门确认XX细节
- 补充XX数据
- 进行XX调研
- 等等

请用清晰的列表形式输出以上内容。"""
        
        try:
            result_text = self.call_llm(prompt, system_prompt)
            
            # 检查是否是错误信息
            if result_text.startswith("❌"):
                # 如果API调用失败，返回错误信息作为raw_analysis
                return {
                    "unclear_expressions": [],
                    "needs_supplement": [],
                    "cross_dept_risks": [],
                    "hidden_dependencies": [],
                    "feasibility_risks": [],
                    "next_steps": [],
                    "raw_analysis": result_text
                }
            
            # 解析结果为结构化数据
            return {
                "unclear_expressions": self._extract_list(result_text, "表达不够明确的地方"),
                "needs_supplement": self._extract_list(result_text, "需要产品经理补充的信息"),
                "cross_dept_risks": self._extract_list(result_text, "跨部门理解偏差风险"),
                "hidden_dependencies": self._extract_list(result_text, "隐性依赖和假设"),
                "feasibility_risks": self._extract_list(result_text, "可行性风险"),
                "next_steps": self._extract_list(result_text, "推荐的下一步动作"),
                "raw_analysis": result_text
            }
        except Exception as e:
            # 如果解析失败，返回基础结构
            return {
                "unclear_expressions": [],
                "needs_supplement": [],
                "cross_dept_risks": [],
                "hidden_dependencies": [],
                "feasibility_risks": [],
                "next_steps": [],
                "raw_analysis": f"风险分析失败: {str(e)}"
            }
    
    def _extract_list(self, text: str, section_title: str) -> List[str]:
        """从文本中提取某个章节的列表项"""
        import re
        
        # 查找章节
        pattern = rf"##.*?{section_title}.*?\n(.*?)(?=##|$)"
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            section_content = match.group(1)
            # 提取列表项（以 - 或 • 开头的行）
            items = re.findall(r'[-•]\s*(.+)', section_content)
            return [item.strip() for item in items if item.strip()]
        
        return []
