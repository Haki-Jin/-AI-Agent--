#!/usr/bin/env python3
"""
创建干净的项目副本(不包含Git历史和敏感文件)
"""
import os
import shutil
from pathlib import Path

# 源目录和目标目录
source_dir = Path("/Users/haki/Desktop/深度学习")
target_dir = Path("/Users/haki/Desktop/需求解析AI-Agent-干净版")

# 需要排除的文件和目录
exclude_patterns = {
    # Git相关
    '.git',
    '.gitignore',
    
    # IDE配置
    '.idea',
    '.vscode',
    '*.swp',
    '*.swo',
    '.DS_Store',
    
    # Streamlit配置(可能包含本地配置)
    '.streamlit',
    
    # 临时文件
    'tempfile_*.bash',
    '*.tmp',
    
    # 数据和模型文件(太大且不需要上传到GitHub)
    'MNIST',
    'C:\\code',
    '*.pth',
    '*.png',
    '*.pdf',
    '*.docx',
    '__pycache__',
    '*.pyc',
    '*.ipynb_checkpoints',
    
    # Python环境
    'venv',
    'env',
    'ENV',
    '.venv',
    
    # 日志文件
    '*.log',
}

# 需要包含的核心文件
include_files = [
    # 核心代码
    'agents.py',
    'app.py',
    'utils.py',
    
    # 配置文件
    'requirements.txt',
    'setup.py',
    
    # 文档
    'README.md',
    'QUICKSTART.md',
    'DEPLOYMENT.md',
    'API_CONFIG_GUIDE.md',
    'API_EXAMPLES.md',
    'ARCHITECTURE.md',
    'PROJECT_SUMMARY.md',
    'DELIVERY_CHECKLIST.md',
    'DEMO_SCRIPT.md',
    'DEPLOYMENT_CHECKLIST.md',
    'FILE_OVERVIEW.md',
    
    # 脚本
    'deploy_to_github.sh',
    'run.sh',
]

def should_exclude(path: Path) -> bool:
    """判断是否应该排除该文件/目录"""
    name = path.name
    
    # 检查是否在排除列表中
    for pattern in exclude_patterns:
        if '*' in pattern:
            # 通配符匹配
            import fnmatch
            if fnmatch.fnmatch(name, pattern):
                return True
        else:
            if name == pattern:
                return True
    
    return False

def create_clean_copy():
    """创建干净的项目副本"""
    print(f"📁 源目录: {source_dir}")
    print(f"📁 目标目录: {target_dir}")
    print()
    
    # 如果目标目录已存在,先删除
    if target_dir.exists():
        print(f"⚠️  目标目录已存在,正在清理...")
        shutil.rmtree(target_dir)
    
    # 创建目标目录
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 创建目标目录: {target_dir}")
    print()
    
    # 复制文件
    copied_count = 0
    skipped_count = 0
    
    print("📋 开始复制文件...")
    print("-" * 60)
    
    for item in source_dir.iterdir():
        if should_exclude(item):
            print(f"⏭️  跳过: {item.name}")
            skipped_count += 1
            continue
        
        if item.is_file():
            # 只复制需要的文件
            if item.name in include_files or (item.suffix == '.py' and item.name not in ['main.py']):
                target_file = target_dir / item.name
                shutil.copy2(item, target_file)
                print(f"✅ 复制: {item.name}")
                copied_count += 1
            elif item.name.endswith('.md'):
                # 复制所有markdown文档
                target_file = target_dir / item.name
                shutil.copy2(item, target_file)
                print(f"✅ 复制: {item.name}")
                copied_count += 1
        elif item.is_dir():
            # 跳过排除的目录
            if item.name not in ['.git', '.idea', '.streamlit', 'MNIST', '__pycache__']:
                print(f"⏭️  跳过目录: {item.name}")
                skipped_count += 1
    
    print("-" * 60)
    print()
    print(f"✅ 完成!")
    print(f"   已复制: {copied_count} 个文件")
    print(f"   已跳过: {skipped_count} 个文件/目录")
    print()
    print(f"📂 干净副本位置: {target_dir}")
    print()
    print("💡 下一步:")
    print(f"   1. 前往 {target_dir}")
    print("   2. 初始化新的Git仓库: git init")
    print("   3. 添加文件: git add .")
    print("   4. 提交: git commit -m 'Initial commit'")
    print("   5. 关联远程仓库并推送")

if __name__ == "__main__":
    create_clean_copy()
