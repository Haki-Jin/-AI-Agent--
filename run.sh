#!/bin/bash

# 跨部门协作需求转译AI Agent 启动脚本cd "/Users/haki/Desktop/需求解析AI-Agent-干净版"
pkill -f streamlit
streamlit run app.py


echo "======================================"
echo "  需求转译AI Agent 启动中..."
echo "======================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"
echo ""

# 检查依赖是否安装
echo "📦 检查依赖..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  检测到缺少依赖，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
else
    echo "✅ 依赖已安装"
fi

echo ""
echo "🚀 启动Streamlit应用..."
echo ""
echo "======================================"
echo "  应用将在浏览器中自动打开"
echo "  如果未自动打开，请访问: http://localhost:8501"
echo "  按 Ctrl+C 停止服务"
echo "======================================"
echo ""

# 启动Streamlit
streamlit run app.py
