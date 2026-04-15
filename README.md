# 跨部门协作需求转译AI Agent

## 📖 项目简介

这是一个基于LLM和多Agent工作流的AI辅助需求转译器，能够将产品经理的原始需求自动转译为不同部门的专属版本。

### 解决的问题

在真实工作中，同一份原始需求不能直接原封不动发给所有人：
- **研发**关心功能逻辑、接口、异常情况、开发边界
- **设计**关心用户流程、页面状态、交互反馈、视觉层级
- **算法/AI**关心输入输出、模型能力边界、评测标准、兜底策略
- **测试**关心测试用例、边界情况、异常场景
- **运营/业务**关心上线价值、用户收益、指标变化、FAQ

本工具通过AI自动完成这个"翻译"工作，提升跨部门协作效率。

## 🚀 快速开始

### 本地运行

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 获取API Key(推荐国内大模型)

**选项A: DeepSeek(推荐⭐)**
- 注册: https://platform.deepseek.com/
- 性价比高,中文理解能力强
- 单次成本约¥0.05-0.1

**选项B: 通义千问**
- 注册: https://dashscope.aliyuncs.com/
- 阿里云出品,稳定可靠
- 单次成本约¥0.05-0.15

**选项C: 豆包**
- 注册: https://www.volcengine.com/product/doubao
- 字节跳动出品,长文本支持好

详见 [API配置指南](API_CONFIG_GUIDE.md)

#### 3. 运行应用

```bash
streamlit run app.py
```

#### 4. 使用步骤

1. 在侧边栏选择API提供商(DeepSeek/豆包/通义千问)
2. 输入API Key
3. 选择示例案例或自定义输入需求
4. 点击“开始需求转译”按钮
5. 查看各部门的转译结果和风险分析

---

## 🌐 在线体验

不想本地部署?可以直接访问在线版本:

**Streamlit Cloud**: (部署后填写你的链接)  
**Hugging Face Spaces**: (部署后填写你的链接)

详见 [部署指南](DEPLOYMENT.md) 了解如何部署自己的版本。

## 🏗️ 技术架构

### 核心组件

- **Streamlit**: Web界面框架
- **国内大模型**: DeepSeek / 豆包 / 通义千问（也支持OpenAI）
- **Multi-Agent System**: 7个专用Agent协同工作

### Agent架构

```
总控Agent (RequirementAnalyzer)
    ↓ 需求解析
    ├─→ Engineering Agent (研发)
    ├─→ Design Agent (设计)
    ├─→ AI/Algorithm Agent (算法)
    ├─→ QA Agent (测试)
    ├─→ Operation Agent (运营)
    └─→ Risk Analyzer (风险分析)
```

### 工作机制

1. **输入**: 产品经理的自然语言需求描述
2. **解析**: 总控Agent提取关键信息（目标、用户、功能点等）
3. **分发**: 并行调用5个部门专属Agent
4. **汇总**: 统一展示 + 风险分析 + 下一步建议

## 📁 项目结构

```
深度学习/
├── app.py              # Streamlit主应用
├── agents.py           # 多Agent系统核心
├── utils.py            # 工具函数
├── requirements.txt    # 依赖包
└── README.md          # 项目说明
```

## 🎯 功能特性

### ✅ 已实现

- [x] 6个专用Agent（总控+5部门+风险）
- [x] 结构化需求解析
- [x] 多部门视角转译
- [x] 风险识别和提醒
- [x] 示例案例库
- [x] 结果下载功能
- [x] 响应式Web界面

### 🔧 可扩展

- [ ] 支持更多LLM提供商（Claude、文心一言等）
- [ ] Prompt版本管理和A/B测试
- [ ] 历史需求数据库
- [ ] 团队协作功能
- [ ] 导出为Word/PDF
- [ ] 自定义Agent角色

## 💡 使用示例

### 示例1: 会议纪要AI功能

**输入**:
> 我们希望做一个会议纪要 AI 功能，用户上传录音后，系统可以自动转写、提炼重点、输出待办事项...

**输出**:
- 🔧 研发版本: 功能模块拆解、API设计、异常处理
- 🎨 设计版本: 用户流程、页面状态、交互反馈
- 🤖 算法版本: 模型选型、Prompt设计、评测指标
- 🧪 测试版本: 测试用例、边界场景、验收标准
- 📈 运营版本: 用户价值、卖点话术、关键指标
- ⚠️ 风险分析: 不明确点、补充建议、偏差风险

## 🧪 实验设计（选做）

可以准备2-3个需求案例，对比：
- 原始需求 vs 转译结果的质量
- 第一版Prompt vs 改进版Prompt的效果
- 有无风险模块时的差异

## 💭 批判性思考

### 当前局限性

1. **LLM可能"编造研发约束"** - 生成的技术细节可能不准确
2. **语气模板化** - 不同部门语气可能不够贴近真实团队
3. **隐性依赖遗漏** - 风险提示可能漏掉某些隐性依赖
4. **依赖总控质量** - 多Agent效果依赖需求解析的准确性

### 改进方向

- 引入领域知识库验证技术可行性
- 收集真实团队反馈优化Prompt
- 增加人工审核环节
- 建立历史需求数据库进行对比学习
- 结合RAG技术检索类似需求

## 🔑 API配置

本项目支持多种大模型API，推荐使用国内模型：

### 推荐：DeepSeek
1. 注册: https://platform.deepseek.com/
2. 获取API Key
3. 在应用中选择 "DeepSeek"，粘贴API Key

### 其他选项
- **通义千问**: https://dashscope.aliyuncs.com/
- **豆包**: https://www.volcengine.com/product/doubao
- **OpenAI**: 也可使用，但需要海外网络

详见 [API配置指南](API_CONFIG_GUIDE.md) 获取详细配置说明。

**注意**: API调用会产生费用，请合理使用。国内模型性价比更高！

## 📝 开发说明

### 添加新的Agent

1. 在`agents.py`中创建新Agent类，继承`BaseAgent`
2. 实现`generate()`或`analyze()`方法
3. 在`app.py`中实例化并调用

### 修改Prompt

每个Agent的Prompt都在对应类的`generate()`方法中，可以直接修改优化。

### 自定义模型

在侧边栏可以选择不同的GPT模型，也可以修改代码支持其他LLM提供商。

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 License

MIT License

---

**技术栈**: Python + Streamlit + OpenAI GPT + Multi-Agent Workflow  
**适用场景**: 产品需求文档自动化分发、跨部门协作效率提升
