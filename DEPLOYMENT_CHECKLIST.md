# 部署检查清单

在部署到公共平台之前,请确保完成以下检查:

---

## ✅ 代码检查

- [ ] 应用能本地正常运行
- [ ] 所有功能测试通过
- [ ] 没有硬编码的API Key
- [ ] 错误处理完善
- [ ] 代码已格式化

---

## ✅ 文件检查

### 必需文件

- [ ] `app.py` - 主应用文件
- [ ] `agents.py` - Agent逻辑
- [ ] `utils.py` - 工具函数
- [ ] `requirements.txt` - 依赖列表
- [ ] `.streamlit/config.toml` - Streamlit配置

### 推荐文件

- [ ] `README.md` - 项目说明
- [ ] `.gitignore` - Git忽略配置
- [ ] `LICENSE` - 开源协议(可选)

### 不应上传的文件

- [ ] `.env` 文件(包含敏感信息)
- [ ] API Key文件
- [ ] 大型数据文件(MNIST等)
- [ ] 模型文件(.pth)
- [ ] IDE配置(.idea/)

---

## ✅ requirements.txt 检查

确保包含所有依赖:

```txt
streamlit==1.31.0
openai>=1.0.0
python-dotenv>=1.0.0
```

运行测试:
```bash
pip install -r requirements.txt
```

---

## ✅ 安全检查

- [ ] 没有硬编码的密码或Key
- [ ] `.gitignore` 配置正确
- [ ] 敏感文件未被提交
- [ ] 使用环境变量或用户输入

检查是否有敏感信息:
```bash
# 搜索可能的API Key
grep -r "sk-" . --exclude-dir=.git
grep -r "api_key" . --exclude-dir=.git
```

---

## ✅ 功能测试

### 基本功能

- [ ] 页面能正常加载
- [ ] 可以选择API提供商
- [ ] 可以输入API Key
- [ ] 可以选择示例案例
- [ ] 可以自定义输入需求

### 核心功能

- [ ] 点击"开始需求转译"按钮有效
- [ ] 需求解析正常工作
- [ ] 5个部门Agent都能生成结果
- [ ] 风险分析模块正常工作
- [ ] 进度条显示正常

### 用户体验

- [ ] 下载功能正常
- [ ] 标签页切换流畅
- [ ] 错误提示友好
- [ ] 移动端显示正常

---

## ✅ 性能优化

- [ ] 移除了不必要的打印语句
- [ ] 图片等资源已压缩
- [ ] 没有大型文件
- [ ] 缓存策略合理

检查文件大小:
```bash
# 查看大文件
find . -type f -size +1M -not -path "./.git/*" -not -path "./MNIST/*"
```

---

## ✅ Git准备

### 初始化Git(如果还没有)

```bash
git init
git add .
git commit -m "Initial commit"
```

### 创建.gitignore

确保包含:
```
.idea/
MNIST/
*.pth
*.png
*.pdf
*.docx
*.ipynb_checkpoints/
.env
__pycache__/
*.pyc
```

### 清理Git历史(可选)

如果有敏感信息被提交过:
```bash
# 警告:这会重写历史
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path-to-file' \
  --prune-empty --tag-name-filter cat -- --all
```

---

## ✅ GitHub准备

- [ ] 已注册GitHub账号
- [ ] 已创建新仓库
- [ ] 仓库设为Public(公开)
- [ ] 添加了README.md
- [ ] 选择了开源License(推荐MIT)

### 创建仓库步骤

1. 访问 https://github.com/new
2. Repository name: `requirement-translator-agent`
3. Description: "面向跨部门协作的需求转译AI Agent"
4. Public (公开)
5. Initialize with README (可选)
6. Add .gitignore: Python
7. Choose license: MIT License
8. 点击 "Create repository"

---

## ✅ Streamlit Cloud准备

- [ ] 已有GitHub账号
- [ ] 代码已推送到GitHub
- [ ] 访问 https://streamlit.io/cloud
- [ ] 了解部署流程

### 部署信息

准备好以下信息:
- Repository: 你的GitHub用户名/仓库名
- Branch: main (或 master)
- Main file path: app.py

---

## ✅ Hugging Face准备(备选)

- [ ] 已注册Hugging Face账号
- [ ] 验证了邮箱
- [ ] 访问 https://huggingface.co/spaces
- [ ] 了解Space创建流程

---

## ✅ 文档检查

- [ ] README.md 清晰易懂
- [ ] 包含部署后的在线链接
- [ ] 有使用说明
- [ ] 有API配置指南
- [ ] 有常见问题解答

---

## ✅ 最终测试

在另一台电脑或浏览器中测试:

- [ ] 从GitHub克隆仓库
- [ ] 安装依赖
- [ ] 运行应用
- [ ] 完整测试一遍流程

```bash
# 模拟新用户体验
git clone https://github.com/你的用户名/requirement-translator-agent.git
cd requirement-translator-agent
pip install -r requirements.txt
streamlit run app.py
```

---

## 🚀 部署执行

### 方案A: Streamlit Cloud

```bash
# 1. 推送代码到GitHub
./deploy_to_github.sh

# 2. 访问 https://streamlit.io/cloud

# 3. 登录GitHub

# 4. New app → 选择仓库 → Deploy!

# 5. 等待2-5分钟

# 6. 获得URL,测试访问
```

### 方案B: Hugging Face Spaces

```bash
# 1. 创建Space
# 访问: https://huggingface.co/spaces/new

# 2. 上传文件
git clone https://huggingface.co/spaces/用户名/空间名
cp *.py 空间名/
cp requirements.txt 空间名/
cp -r .streamlit 空间名/
cd 空间名
git add .
git commit -m "Deploy"
git push

# 3. 等待3-5分钟

# 4. 获得URL,测试访问
```

---

## 📊 部署后验证

部署完成后,立即测试:

- [ ] URL可以访问
- [ ] 页面加载正常
- [ ] 所有功能可用
- [ ] 手机端显示正常
- [ ] 分享给朋友测试

### 测试清单

邀请3-5个朋友测试:
- [ ] 他们能否独立使用?
- [ ] 是否遇到任何问题?
- [ ] 有什么改进建议?

---

## 📝 分享准备

部署成功后:

### 更新README

在README.md中添加:

```markdown
## 🌐 在线体验

访问: https://你的应用链接

无需安装,打开即用!
```

### 准备介绍文案

```
🤖 我开发了一个需求转译AI Agent!

✨ 功能:
- 自动将产品需求转译为研发/设计/算法/测试/运营版本
- 支持DeepSeek、通义千问、豆包等多种大模型
- 风险识别和建议

🔗 在线体验: https://你的应用链接

欢迎试用和反馈!
```

### 收集反馈

添加反馈渠道:
- 邮箱
- GitHub Issues
- 微信群/QQ群

---

## 🎯 后续优化

根据用户反馈:

- [ ] 修复发现的问题
- [ ] 优化用户体验
- [ ] 添加新功能
- [ ] 完善文档
- [ ] 考虑付费升级

---

## 💡 提示

1. **先小范围测试**: 先分享给几个朋友,收集反馈
2. **监控使用情况**: 定期查看使用统计
3. **及时响应问题**: 快速响应用户反馈
4. **持续改进**: 根据反馈不断优化

---

**祝部署顺利!** 🎉

完成以上检查后,你就可以自信地部署和分享了!
