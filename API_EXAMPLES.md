# API配置示例

本文档提供各大模型平台的API配置示例，复制粘贴即可使用。

---

## 🎯 DeepSeek（推荐⭐）

### 注册和获取API Key

1. 访问: https://platform.deepseek.com/
2. 注册账号并登录
3. 进入控制台 → API Keys
4. 点击"创建API Key"
5. 复制保存（格式: `sk-xxxxxxxxxxxxxxxx`）

### 在应用中配置

```
API提供商: DeepSeek
Base URL: https://api.deepseek.com/v1
模型: deepseek-chat
API Key: sk-你的实际key
```

### 测试连接

```bash
python test_api_connection.py
# 选择 1 (DeepSeek)
# 输入API Key
# 使用默认配置
```

### 价格

- 输入: ¥2 / 百万tokens
- 输出: ¥8 / 百万tokens
- 单次转译: 约¥0.05-0.1

---

## 🎯 通义千问 Qwen（推荐⭐）

### 注册和获取API Key

1. 访问: https://dashscope.aliyun.com/
2. 注册阿里云账号
3. 开通DashScope服务
4. 进入控制台 → API-KEY管理
5. 创建API Key
6. 复制保存（格式: `sk-xxxxxxxxxxxxxxxx`）

### 在应用中配置

```
API提供商: 通义千问(Qwen)
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
模型: qwen-plus
API Key: sk-你的实际key
```

### 测试连接

```bash
python test_api_connection.py
# 选择 3 (通义千问)
# 输入API Key
# 选择模型: 1 (qwen-plus)
```

### 价格

- qwen-plus:
  - 输入: ¥0.008 / 千tokens
  - 输出: ¥0.02 / 千tokens
- 单次转译: 约¥0.05-0.15

---

## 🎯 豆包 Doubao

### 注册和获取API Key

1. 访问: https://www.volcengine.com/product/doubao
2. 注册火山引擎账号
3. 开通豆包大模型服务
4. 进入控制台 → 应用管理
5. 创建应用
6. 获取API Key（格式: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`）

### 在应用中配置

```
API提供商: 豆包(Doubao)
Base URL: https://ark.cn-beijing.volces.com/api/v3
模型: doubao-pro-32k
API Key: 你的实际key
```

### 测试连接

```bash
python test_api_connection.py
# 选择 2 (豆包)
# 输入API Key
# 选择模型: 1 (doubao-pro-32k)
```

### 价格

- doubao-pro-32k:
  - 输入: ¥0.8 / 千tokens
  - 输出: ¥2.0 / 千tokens
- 单次转译: 约¥0.1-0.3

---

## 🔧 本地部署 Ollama

### 安装Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
访问 https://ollama.ai/ 下载安装包

### 下载模型

```bash
# 推荐模型（7B参数，平衡性能和资源）
ollama pull qwen2.5:7b

# 其他可选模型
ollama pull qwen2.5:14b    # 更强但更慢
ollama pull llama3.1:8b    # Meta出品
ollama pull deepseek-coder:6.7b  # 代码能力强
```

### 启动服务

```bash
# 后台运行
ollama serve

# 或者前台运行（方便查看日志）
ollama run qwen2.5:7b
```

### 在应用中配置

```
API提供商: 自定义OpenAI兼容API
Base URL: http://localhost:11434/v1
模型: qwen2.5:7b
API Key: 任意字符串（本地不需要）
```

### 测试连接

```bash
python test_api_connection.py
# 选择 4 (自定义)
# Base URL: http://localhost:11434/v1
# 模型: qwen2.5:7b
# API Key: test（任意填写）
```

### 优势

- ✅ 完全免费
- ✅ 数据隐私安全
- ✅ 无需网络
- ❌ 需要较好的GPU
- ❌ 响应速度较慢

---

## 📊 配置对比表

| 平台 | Base URL | 推荐模型 | API Key格式 | 成本 |
|------|----------|---------|------------|------|
| DeepSeek | https://api.deepseek.com/v1 | deepseek-chat | sk-xxx | ¥0.05-0.1/次 |
| 通义千问 | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-plus | sk-xxx | ¥0.05-0.15/次 |
| 豆包 | https://ark.cn-beijing.volces.com/api/v3 | doubao-pro-32k | uuid格式 | ¥0.1-0.3/次 |
| Ollama | http://localhost:11434/v1 | qwen2.5:7b | 任意 | 免费 |

---

## ⚡ 快速开始（3步）

### 方案A: DeepSeek（最简单）

```bash
# 1. 注册获取Key
访问 https://platform.deepseek.com/

# 2. 启动应用
streamlit run app.py

# 3. 配置
- 选择: DeepSeek
- Base URL: https://api.deepseek.com/v1
- 模型: deepseek-chat
- 粘贴API Key
```

### 方案B: 通义千问

```bash
# 1. 注册获取Key
访问 https://dashscope.aliyuncs.com/

# 2. 启动应用
streamlit run app.py

# 3. 配置
- 选择: 通义千问(Qwen)
- Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
- 模型: qwen-plus
- 粘贴API Key
```

### 方案C: 本地Ollama（免费）

```bash
# 1. 安装Ollama
brew install ollama

# 2. 下载模型
ollama pull qwen2.5:7b

# 3. 启动服务
ollama serve

# 4. 启动应用
streamlit run app.py

# 5. 配置
- 选择: 自定义OpenAI兼容API
- Base URL: http://localhost:11434/v1
- 模型: qwen2.5:7b
- API Key: test
```

---

## 🔍 常见问题

### Q: 如何知道API Key是否正确？

**A**: 运行测试脚本
```bash
python test_api_connection.py
```

### Q: Base URL可以修改吗？

**A**: 可以！不同平台可能有不同的API版本，如果默认URL不工作，可以查看官方文档获取最新地址。

### Q: 模型名称在哪里查看？

**A**: 
- DeepSeek: https://platform.deepseek.com/docs
- 通义千问: https://help.aliyun.com/zh/dashscope/
- 豆包: https://www.volcengine.com/docs/

### Q: 可以同时配置多个API吗？

**A**: 当前版本一次只能使用一个API，但可以随时切换。未来可以支持多API负载均衡。

### Q: API Key泄露了怎么办？

**A**: 
1. 立即在原平台删除该Key
2. 创建新的API Key
3. 不要将Key上传到GitHub等公开场所
4. 使用环境变量存储Key（进阶）

---

## 💡 最佳实践

### 1. 开发阶段
使用 **DeepSeek** 或 **通义千问**
- 成本低
- 速度快
- 效果好

### 2. 演示阶段
使用 **DeepSeek** (deepseek-chat)
- 性价比高
- 中文理解好
- 稳定可靠

### 3. 生产环境
根据需求选择：
- 成本敏感: DeepSeek
- 长文本: 豆包 (128k)
- 企业级: 通义千问
- 数据安全: Ollama本地部署

### 4. 学习实验
使用 **Ollama**
- 完全免费
- 可以随意测试
- 了解底层原理

---

## 📞 获取帮助

遇到问题：
1. 查看 [API_CONFIG_GUIDE.md](API_CONFIG_GUIDE.md) 详细指南
2. 运行 `python test_api_connection.py` 测试连接
3. 查看各平台官方文档
4. 检查网络和余额

---

*最后更新: 2026年4月14日*
