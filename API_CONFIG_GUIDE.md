# 国内大模型API配置指南

本demo支持多种国内大模型API，包括DeepSeek、豆包、通义千问等。

---

## 🎯 支持的模型提供商

### 1. DeepSeek（推荐）⭐

**特点**: 
- 性价比高
- 中文理解能力强
- API稳定

**配置步骤**:

1. **注册账号**
   - 访问: https://platform.deepseek.com/
   - 注册并登录

2. **获取API Key**
   - 进入控制台
   - 点击 "API Keys"
   - 创建新的API Key
   - 复制保存

3. **在应用中使用**
   - API提供商: 选择 "DeepSeek"
   - Base URL: `https://api.deepseek.com/v1` (默认已填)
   - 模型选择: 
     - `deepseek-chat` (通用对话，推荐)
     - `deepseek-reasoner` (推理能力更强)
   - 粘贴API Key

4. **价格参考**
   - deepseek-chat: ¥2/百万tokens (输入), ¥8/百万tokens (输出)
   - 单次转译成本: 约¥0.05-0.1

---

### 2. 豆包 (Doubao) - 字节跳动

**特点**:
- 字节跳动出品
- 长文本支持好
- 适合企业级应用

**配置步骤**:

1. **注册账号**
   - 访问: https://www.volcengine.com/product/doubao
   - 注册火山引擎账号
   - 开通豆包大模型服务

2. **获取API Key**
   - 进入控制台
   - 创建应用
   - 获取API Key和Endpoint

3. **在应用中使用**
   - API提供商: 选择 "豆包(Doubao)"
   - Base URL: `https://ark.cn-beijing.volces.com/api/v3` (默认已填)
   - 模型选择:
     - `doubao-pro-32k` (专业版，32k上下文)
     - `doubao-lite-32k` (轻量版)
     - `doubao-pro-128k` (超长上下文)
   - 粘贴API Key

4. **价格参考**
   - doubao-pro-32k: ¥0.8/千tokens (输入), ¥2.0/千tokens (输出)
   - 单次转译成本: 约¥0.1-0.3

---

### 3. 通义千问 (Qwen) - 阿里云

**特点**:
- 阿里云出品
- 多语言支持好
- 生态完善

**配置步骤**:

1. **注册账号**
   - 访问: https://dashscope.aliyun.com/
   - 注册阿里云账号
   - 开通DashScope服务

2. **获取API Key**
   - 进入控制台
   - 创建API Key
   - 复制保存

3. **在应用中使用**
   - API提供商: 选择 "通义千问(Qwen)"
   - Base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1` (默认已填)
   - 模型选择:
     - `qwen-plus` (均衡型，推荐)
     - `qwen-turbo` (快速型)
     - `qwen-max` (最强性能)
   - 粘贴API Key

4. **价格参考**
   - qwen-plus: ¥0.008/千tokens (输入), ¥0.02/千tokens (输出)
   - 单次转译成本: 约¥0.05-0.15

---

### 4. 自定义OpenAI兼容API

如果你有其他OpenAI兼容的API服务，可以选择此项。

**配置步骤**:

1. **填写信息**
   - API提供商: 选择 "自定义OpenAI兼容API"
   - Base URL: 输入你的API地址 (例如: `http://localhost:8000/v1`)
   - 模型名称: 输入模型名称
   - API Key: 输入你的API Key

2. **常见兼容服务**
   - Ollama (本地部署): `http://localhost:11434/v1`
   - LM Studio: `http://localhost:1234/v1`
   - 其他兼容OpenAI格式的服务

---

## 💰 成本对比

| 模型提供商 | 模型名称 | 输入价格 | 输出价格 | 单次成本估算 |
|-----------|---------|---------|---------|------------|
| DeepSeek | deepseek-chat | ¥2/M tokens | ¥8/M tokens | ¥0.05-0.1 |
| 豆包 | doubao-pro-32k | ¥0.8/K tokens | ¥2.0/K tokens | ¥0.1-0.3 |
| 通义千问 | qwen-plus | ¥0.008/K tokens | ¥0.02/K tokens | ¥0.05-0.15 |
| OpenAI | gpt-3.5-turbo | $0.0015/K | $0.002/K | $0.03-0.05 |
| OpenAI | gpt-4 | $0.03/K | $0.06/K | $0.5-0.8 |

**推荐**: DeepSeek 或 通义千问，性价比最高！

---

## 🔧 常见问题

### Q1: 如何选择最适合的模型？

**A**: 
- **性价比优先**: DeepSeek (deepseek-chat)
- **中文理解**: DeepSeek 或 通义千问
- **长文本需求**: 豆包 (doubao-pro-128k)
- **企业级应用**: 豆包 或 通义千问
- **本地部署**: Ollama + 自定义API

### Q2: API Key在哪里获取？

**A**: 
每个提供商都需要在其官网注册账号后获取：
- DeepSeek: https://platform.deepseek.com/
- 豆包: https://www.volcengine.com/product/doubao
- 通义千问: https://dashscope.aliyuncs.com/

### Q3: 国内模型和GPT相比怎么样？

**A**:
- **中文能力**: 国内模型通常更好
- **响应速度**: 国内访问更快
- **成本**: 国内模型更便宜
- **稳定性**: 国内网络更稳定
- **综合能力**: GPT-4仍然略强，但差距在缩小

对于本demo的需求转译任务，国内模型完全够用！

### Q4: 如何节省API费用？

**A**:
1. 使用DeepSeek或通义千问（性价比高）
2. 精简需求描述，避免过长
3. 先用小模型测试，满意后再用大模型
4. 缓存相同需求的結果
5. 查看各平台的免费额度

### Q5: 可以本地部署模型吗？

**A**: 可以！使用Ollama：

```bash
# 1. 安装Ollama
brew install ollama  # macOS
# 或访问 https://ollama.ai/

# 2. 下载模型
ollama pull qwen2.5:7b

# 3. 启动API服务
ollama serve

# 4. 在应用中选择"自定义OpenAI兼容API"
# Base URL: http://localhost:11434/v1
# 模型名称: qwen2.5:7b
```

### Q6: 遇到API调用失败怎么办？

**A**:
1. 检查API Key是否正确
2. 检查网络连接
3. 确认账户余额充足
4. 查看控制台错误信息
5. 尝试切换其他模型或提供商

---

## 📝 配置示例

### DeepSeek配置示例

```
API提供商: DeepSeek
Base URL: https://api.deepseek.com/v1
模型: deepseek-chat
API Key: sk-xxxxxxxxxxxxxxxx
```

### 豆包配置示例

```
API提供商: 豆包(Doubao)
Base URL: https://ark.cn-beijing.volces.com/api/v3
模型: doubao-pro-32k
API Key: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 通义千问配置示例

```
API提供商: 通义千问(Qwen)
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
模型: qwen-plus
API Key: sk-xxxxxxxxxxxxxxxx
```

---

## 🚀 快速开始

### 推荐配置（DeepSeek）

1. 注册DeepSeek: https://platform.deepseek.com/
2. 获取API Key
3. 在应用中选择:
   - API提供商: DeepSeek
   - 模型: deepseek-chat
   - 粘贴API Key
4. 开始使用！

### 备选配置（通义千问）

1. 注册阿里云DashScope: https://dashscope.aliyuncs.com/
2. 获取API Key
3. 在应用中选择:
   - API提供商: 通义千问(Qwen)
   - 模型: qwen-plus
   - 粘贴API Key
4. 开始使用！

---

## 📊 性能对比

根据实际测试（需求转译任务）：

| 模型 | 响应时间 | 内容质量 | 稳定性 | 推荐度 |
|------|---------|---------|--------|--------|
| deepseek-chat | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| doubao-pro-32k | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| qwen-plus | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| gpt-3.5-turbo | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| gpt-4 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**结论**: 对于需求转译任务，DeepSeek和通义千问的表现已经非常好，完全可以使用！

---

## 🔐 安全提示

1. **不要泄露API Key**
   - 不要在代码中硬编码
   - 不要上传到GitHub
   - 定期更换API Key

2. **设置使用限额**
   - 在各平台控制台设置月度限额
   - 监控使用情况
   - 开启用量提醒

3. **使用环境变量** (可选)
   ```bash
   export API_KEY="your-api-key"
   export BASE_URL="https://api.deepseek.com/v1"
   ```

---

## 📞 获取帮助

遇到问题可以：
1. 查看各平台官方文档
2. 检查API状态页面
3. 联系平台客服
4. 查看本项目Issues

---

**祝使用愉快！** 🎉

*最后更新: 2026年4月14日*
