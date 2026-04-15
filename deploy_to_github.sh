#!/bin/bash

# GitHub上传和部署脚本

echo "======================================"
echo "  准备上传到GitHub"
echo "======================================"
echo ""

# 检查是否在git仓库中
if [ ! -d ".git" ]; then
    echo "⚠️  检测到这不是一个Git仓库"
    echo ""
    read -p "是否初始化Git仓库? (y/n): " init_git
    
    if [ "$init_git" = "y" ] || [ "$init_git" = "Y" ]; then
        git init
        echo "✅ Git仓库已初始化"
    else
        echo "❌ 取消操作"
        exit 1
    fi
fi

echo ""
echo "📝 请输入commit信息:"
read commit_message

if [ -z "$commit_message" ]; then
    commit_message="Update: $(date '+%Y-%m-%d %H:%M:%S')"
fi

echo ""
echo "📦 添加文件..."
git add .

echo ""
echo "💾 提交更改..."
git commit -m "$commit_message"

echo ""
echo "📤 推送到GitHub..."

# 检查是否有远程仓库
if ! git remote | grep -q "origin"; then
    echo "⚠️  未配置远程仓库"
    echo ""
    read -p "请输入GitHub仓库URL (例如: https://github.com/用户名/仓库名.git): " repo_url
    
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo "✅ 远程仓库已添加"
    else
        echo "❌ 取消操作"
        exit 1
    fi
fi

# 获取当前分支
current_branch=$(git branch --show-current)
if [ -z "$current_branch" ]; then
    current_branch="main"
    git branch -M main
fi

echo ""
echo "🚀 推送到 $current_branch 分支..."
git push -u origin "$current_branch"

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "  ✅ 推送成功!"
    echo "======================================"
    echo ""
    echo "下一步:"
    echo "1. 访问 https://streamlit.io/cloud"
    echo "2. 使用GitHub登录"
    echo "3. 点击 'New app'"
    echo "4. 选择你的仓库"
    echo "5. 选择 app.py"
    echo "6. 点击 'Deploy!'"
    echo ""
else
    echo ""
    echo "======================================"
    echo "  ❌ 推送失败"
    echo "======================================"
    echo ""
    echo "可能的原因:"
    echo "1. 网络连接问题"
    echo "2. 没有权限"
    echo "3. 需要先pull远程更改"
    echo ""
    echo "尝试: git pull origin $current_branch"
    echo ""
fi
