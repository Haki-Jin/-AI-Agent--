# 部署指南 - 将应用发布为公共网站

本指南介绍如何将需求转译AI Agent部署为公共网站,让任何人都可以访问使用。

---

## 🌐 推荐部署方案

### 方案对比

| 平台 | 难度 | 成本 | 域名 | 特点 | 推荐度 |
|------|------|------|------|------|--------|
| **Streamlit Cloud** | ⭐简单 | 免费 | xxx.streamlit.app | 官方支持,最简单 | ⭐⭐⭐⭐⭐ |
| **Hugging Face Spaces** | ⭐⭐中等 | 免费 | xxx.hf.space | 社区活跃,功能强 | ⭐⭐⭐⭐ |
| **Render** | ⭐⭐⭐较复杂 | 免费额度 | xxx.onrender.com | 灵活度高 | ⭐⭐⭐ |

**推荐**: Streamlit Cloud(最简单)或 Hugging Face Spaces(功能更强)

---

## 🚀 方案一:Streamlit Cloud(最简单,5分钟部署)

### 优点
- ✅ 完全免费
- ✅ 5分钟快速部署
- ✅ 自动HTTPS
- ✅ 官方支持Streamlit
- ✅ 自动更新

### 缺点
- ❌ 需要GitHub仓库
- ❌ 免费版有资源限制
- ❌ 30分钟无活动会休眠

### 部署步骤

#### Step 1: 准备GitHub仓库

```bash
# 1. 在GitHub创建新仓库
# 访问: https://github.com/new
# 仓库名: requirement-translator-agent
# 设为公开(Public)

# 2. 初始化本地git(如果还没有)
cd /Users/haki/Desktop/深度学习
git init

# 3. 添加所有文件
git add .

# 4. 提交
git commit -m "Initial commit: 需求转译AI Agent"

# 5. 关联远程仓库
git remote add origin https://github.com/你的用户名/requirement-translator-agent.git

# 6. 推送
git push -u origin main
```

#### Step 2: 清理不必要的文件

确保 `.gitignore` 包含以下内容(已配置好):
```
.idea/
MNIST/
*.pth
*.png
*.pdf
*.docx
*.ipynb_checkpoints/
.env
```

#### Step 3: 在Streamlit Cloud部署

1. **访问**: https://streamlit.io/cloud
2. **登录**: 使用GitHub账号登录
3. **点击**: "New app"
4. **配置**:
   - Repository: 选择你的仓库 `requirement-translator-agent`
   - Branch: `main`
   - Main file path: `app.py`
5. **点击**: "Deploy!"

#### Step 4: 等待部署完成

- 首次部署约2-5分钟
- 部署成功后会获得一个URL: `https://xxx.streamlit.app`
- 任何人都可以访问这个URL使用你的应用!

#### Step 5: 分享给别人

复制你的应用URL,例如:
```
https://requirement-translator-agent.streamlit.app
```

发送给任何人,他们都可以直接使用!

### 更新应用

```bash
# 修改代码后
git add .
git commit -m "Update: 描述你的改动"
git push

# Streamlit Cloud会自动检测并重新部署(约1-2分钟)
```

---

## 🤗 方案二:Hugging Face Spaces(推荐,更稳定)

### 优点
- ✅ 完全免费
- ✅ 资源更充足
- ✅ 不会休眠
- ✅ 支持GPU(付费)
- ✅ 社区活跃
- ✅ 可以设置密码保护

### 缺点
- ❌ 需要Hugging Face账号
- ❌ 国内访问可能稍慢

### 部署步骤

#### Step 1: 创建Hugging Face账号

1. 访问: https://huggingface.co/
2. 注册账号
3. 验证邮箱

#### Step 2: 创建Space

1. 访问: https://huggingface.co/spaces
2. 点击 "Create new Space"
3. 配置:
   - Space name: `requirement-translator-agent`
   - License: MIT
   - SDK: **Streamlit**
   - Visibility: **Public** (公开)
4. 点击 "Create Space"

#### Step 3: 上传文件

**方法A: 通过Git上传(推荐)**

```bash
# 1. 克隆Space仓库
git clone https://huggingface.co/spaces/你的用户名/requirement-translator-agent
cd requirement-translator-agent

# 2. 复制项目文件
cp /Users/haki/Desktop/深度学习/app.py .
cp /Users/haki/Desktop/深度学习/agents.py .
cp /Users/haki/Desktop/深度学习/utils.py .
cp /Users/haki/Desktop/深度学习/requirements.txt .
cp -r /Users/haki/Desktop/深度学习/.streamlit .

# 3. 创建README.md
# (在Space页面直接编辑即可)

# 4. 提交
git add .
git commit -m "Initial commit"
git push
```

**方法B: 通过Web界面上传**

1. 在Space页面点击 "Files"
2. 点击 "Add file" → "Upload files"
3. 上传以下文件:
   - `app.py`
   - `agents.py`
   - `utils.py`
   - `requirements.txt`
   - `.streamlit/config.toml`

#### Step 4: 等待部署

- 首次部署约3-5分钟
- 部署成功后获得URL: `https://huggingface.co/spaces/你的用户名/requirement-translator-agent`

---

## 💡 重要提示

### 关于API Key的安全问题

**当前实现**: 用户在UI中输入自己的API Key
- ✅ 安全: API Key不会被保存
- ✅ 灵活: 用户可以使用自己的账号
- ❌ 不便: 每个用户都需要有自己的API Key

**改进方案**(可选): 如果你想提供免费的API调用

⚠️ **注意**: 这会消耗你的API额度,需要谨慎!

如果确实需要,可以:
1. 在Streamlit Cloud/HF Spaces设置Secrets
2. 修改代码优先使用预设的API Key
3. 设置使用限制(如每日次数限制)

**建议**: 保持当前设计,让用户输入自己的API Key更安全、更可持续。

### 优化用户体验

#### 1. 添加示例按钮

在应用中已经提供了3个示例案例,用户可以一键体验。

#### 2. 添加帮助文档

在侧边栏添加了使用提示,帮助用户快速上手。

#### 3. 响应式设计

Streamlit自动适配手机和电脑屏幕。

---

## 📊 部署后测试清单

部署完成后,请测试:

- [ ] 应用能否正常打开
- [ ] 页面加载是否正常
- [ ] 能否选择API提供商
- [ ] 能否输入API Key
- [ ] 能否选择示例案例
- [ ] 能否生成转译结果
- [ ] 下载功能是否正常
- [ ] 手机端显示是否正常

---

## 🎯 分享推广

### 获取访问链接

部署成功后,你会获得类似这样的链接:
- Streamlit Cloud: `https://xxx.streamlit.app`
- Hugging Face: `https://huggingface.co/spaces/xxx/xxx`

### 分享给别人

1. **直接发送链接**
   ```
   试试这个工具: https://xxx.streamlit.app
   可以把产品需求自动转译成各部门版本!
   ```

2. **制作演示视频**
   - 录制屏幕演示
   - 上传到B站/YouTube
   - 在描述中放上链接

3. **写篇文章**
   - 介绍项目背景
   - 展示使用效果
   - 附上在线demo链接

4. **社交媒体**
   - 朋友圈分享
   - 技术社区发帖
   - LinkedIn/Twitter

### 收集反馈

在应用底部可以添加:
```python
st.markdown("""
---
💬 **反馈与建议**: 
如果有问题或建议,欢迎联系: your-email@example.com
""")
```

---

## 🔧 常见问题

### Q: 部署后访问很慢?

**A**: 
- Streamlit Cloud免费版可能有延迟
- 考虑升级到付费计划
- 或使用Hugging Face Spaces

### Q: 应用经常休眠?

**A**: 
- Streamlit Cloud免费版30分钟无活动会休眠
- 下次访问需要重新加载(约30秒)
- 这是正常现象

### Q: 如何自定义域名?

**A**: 
- Streamlit Cloud: 付费计划支持
- Hugging Face: 暂不支持
- Render/Vercel: 支持自定义域名

### Q: 有人滥用怎么办?

**A**: 
- 当前设计用户需自备API Key,无法滥用你的额度
- 如需限制,可添加简单的频率限制

### Q: 如何查看使用统计?

**A**: 
- Streamlit Cloud: 控制台有基本统计
- Hugging Face: 提供更详细的使用数据

---

## 🚀 快速开始(推荐Streamlit Cloud)

```bash
# 1. 确保代码已推送到GitHub
git push

# 2. 访问 https://streamlit.io/cloud

# 3. 用GitHub登录

# 4. 点击 "New app"

# 5. 选择你的仓库和app.py

# 6. 点击 "Deploy!"

# 7. 等待2-5分钟

# 8. 获得链接,分享给朋友!
```

---

## 📝 下一步

部署成功后:

1. ✅ 测试所有功能
2. ✅ 分享给朋友试用
3. ✅ 收集反馈意见
4. ✅ 持续优化改进
5. ✅ 考虑添加更多功能

---

**祝部署顺利!** 🎉

如有问题,欢迎查阅:
- Streamlit Cloud文档: https://docs.streamlit.io/streamlit-community-cloud
- Hugging Face Spaces文档: https://huggingface.co/docs/hub/spaces
