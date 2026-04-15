# 快速开始指南

## 🚀 三步启动应用

### 方法一：使用启动脚本（推荐）

```bash
# 1. 赋予执行权限
chmod +x run.sh

# 2. 运行
./run.sh
```

### 方法二：手动启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
streamlit run app.py
```

### 方法三：在IDE中运行

直接在IDE中运行 `app.py` 文件

---

## 📋 使用步骤

### 1️⃣ 获取API Key（推荐国内大模型）

**选项A: DeepSeek（推荐⭐）**
1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的API Key
5. 复制保存（只显示一次）
6. 性价比高，中文理解能力强

**选项B: 通义千问**
1. 访问 https://dashscope.aliyuncs.com/
2. 注册阿里云账号
3. 开通DashScope服务
4. 创建API Key
5. 复制保存

**选项C: 豆包**
1. 访问 https://www.volcengine.com/product/doubao
2. 注册火山引擎账号
3. 开通豆包服务
4. 获取API Key

详见 [API配置指南](API_CONFIG_GUIDE.md) 了解更多详情。

### 2️⃣ 启动应用

按照上面的方法启动应用后，浏览器会自动打开 http://localhost:8501

### 3️⃣ 配置API

1. 在左侧边栏选择 **API提供商**（DeepSeek / 豆包 / 通义千问）
2. Base URL会自动填充（也可以手动修改）
3. 选择 **模型**（不同提供商有不同模型可选）
4. 在 "API Key" 输入框中粘贴你的API Key

### 4️⃣ 选择或输入需求

**选项A：使用示例案例**
- 在侧边栏选择 "会议纪要AI功能"、"智能客服系统" 或 "个性化推荐引擎"
- 查看示例内容

**选项B：自定义输入**
- 选择 "自定义输入"
- 在主区域文本框中输入你的产品需求

### 5️⃣ 开始转译

点击 "🚀 开始需求转译" 按钮

### 6️⃣ 查看结果

等待所有Agent处理完成后，你会看到：

- **Step 2**: 需求解析结果（目标、用户、功能点等）
- **Step 3**: 各部门转译进度
- **Step 4**: 完整结果汇总
  - 🔧 研发版本
  - 🎨 设计版本
  - 🤖 算法/AI版本
  - 🧪 测试版本
  - 📈 运营/业务版本
  - ⚠️ 风险提醒

### 7️⃣ 下载结果

每个标签页都有下载按钮，可以保存为Markdown文件

---

## 💡 使用技巧

### 写出好的需求描述

✅ **好的示例**:
```
我们希望做一个会议纪要AI功能，用户上传录音后，系统可以自动转写、
提炼重点、输出待办事项。支持mp3/wav格式，能识别多人说话，
生成详细版和简版总结。目标用户是企业白领，用于周会和项目评审会。
```

❌ **不好的示例**:
```
做个会议功能，要好用。
```

### 关键要素 Checklist

- [ ] 功能描述清楚
- [ ] 目标用户明确
- [ ] 使用场景说明
- [ ] 核心功能点列出
- [ ] 约束条件提及（如性能、格式等）
- [ ] 业务价值说明（可选）

### 优化结果

如果第一次结果不理想：

1. **补充更多细节** - 在原始需求中添加更多信息
2. **调整模型** - 尝试切换到gpt-4（效果更好但更贵）
3. **修改Prompt** - 编辑 `agents.py` 中对应Agent的prompt
4. **多次尝试** - LLM有一定随机性，可以重新生成

---

## 🔧 常见问题

### Q: 报错 "ModuleNotFoundError: No module named 'streamlit'"

**A**: 依赖未安装，运行：
```bash
pip install -r requirements.txt
```

### Q: 报错 "API key not provided"

**A**: 请在侧边栏输入你的API Key

### Q: 结果生成很慢

**A**: 
- 检查网络连接
- 尝试切换其他模型（如从deepseek-reasoner切换到deepseek-chat）
- 确认API Key有效且有余额
- 国内模型通常响应更快

### Q: 生成的内容不准确

**A**:
- 提供更详细的需求描述
- 尝试切换其他模型（如qwen-max或doubao-pro-128k）
- 手动编辑agents.py中的prompt进行优化

### Q: 如何节省API费用？

**A**:
- 使用DeepSeek或通义千问（性价比最高）
- 减少不必要的重新生成
- 缩短需求描述长度
- 查看各平台后台的使用情况
- 利用免费额度

### Q: 可以离线使用吗？

**A**: 可以！使用Ollama本地部署：
```bash
# 安装Ollama
brew install ollama

# 下载模型
ollama pull qwen2.5:7b

# 启动服务
ollama serve

# 在应用中选择"自定义OpenAI兼容API"
# Base URL: http://localhost:11434/v1
# 模型名称: qwen2.5:7b
```

---

## 📊 成本估算

以“会议纪要AI功能”为例：

**国内模型**:
- **DeepSeek (deepseek-chat)**: 约¥0.05-0.1/次 ⭐推荐
- **通义千问 (qwen-plus)**: 约¥0.05-0.15/次 ⭐推荐
- **豆包 (doubao-pro-32k)**: 约¥0.1-0.3/次

**国外模型**:
- **GPT-3.5-turbo**: 约$0.03-0.05/次
- **GPT-4**: 约$0.50-0.80/次

**建议**: 优先使用DeepSeek或通义千问，性价比最高！

---

## 🎓 学习资源

- **Streamlit文档**: https://docs.streamlit.io/
- **OpenAI API文档**: https://platform.openai.com/docs
- **Prompt工程指南**: https://platform.openai.com/docs/guides/prompt-engineering

---

## 🆘 需要帮助？

遇到问题可以：
1. 查看README.md的详细文档
2. 检查控制台错误信息
3. 提交Issue到项目仓库

祝使用愉快！🎉
