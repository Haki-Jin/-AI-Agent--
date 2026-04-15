"""
工具函数模块
"""


def format_output(text: str) -> str:
    """格式化输出文本，确保Markdown格式正确"""
    if not text:
        return "暂无内容"
    
    # 清理多余的空行
    lines = text.split('\n')
    cleaned_lines = []
    prev_empty = False
    
    for line in lines:
        is_empty = line.strip() == ''
        if is_empty and prev_empty:
            continue
        cleaned_lines.append(line)
        prev_empty = is_empty
    
    return '\n'.join(cleaned_lines)


def create_example_cases() -> dict:
    """创建示例需求案例"""
    return {
        "会议纪要AI功能": """我们希望做一个会议纪要 AI 功能，用户上传录音后，系统可以自动转写、提炼重点、输出待办事项，还可以生成适合发给老板的简版总结。

核心需求：
1. 支持上传音频文件（mp3, wav, m4a等格式）
2. 自动将语音转为文字
3. 智能识别会议中的关键信息和决策点
4. 自动提取待办事项（谁、做什么、何时完成）
5. 生成不同版本的总结：详细版（给参会者）、简版（给老板）、行动项版（给执行者）
6. 支持多人说话者识别
7. 可以搜索历史会议纪要
8. 支持导出为Word、PDF等格式

目标用户：企业白领、项目经理、团队Leader
使用场景：周会、项目评审会、客户沟通会、脑暴会等""",

        "智能客服系统": """我们需要构建一个智能客服系统，能够自动回答用户的常见问题，减轻人工客服压力。

核心需求：
1. 7x24小时在线，即时响应用户咨询
2. 能理解自然语言问题，不只是关键词匹配
3. 基于产品文档、FAQ、历史对话进行学习
4. 对于无法回答的问题，平滑转接人工客服
5. 支持多轮对话，能记住上下文
6. 能识别用户情绪，对愤怒用户优先转人工
7. 提供客服数据分析：常见问题、满意度、解决率等
8. 支持文字、图片（如截图报错）多种输入方式
9. 可以主动推送相关信息（如订单状态更新）

目标用户：电商平台用户、SaaS产品用户
业务指标：自动化解决率>70%，用户满意度>4.5/5，平均响应时间<3秒""",

        "个性化推荐引擎": """我们要为内容平台打造一个个性化推荐引擎，根据用户兴趣和行为，推荐最合适的内容。

核心需求：
1. 基于用户历史行为（浏览、点赞、收藏、分享、评论）建模
2. 考虑内容特征（标签、分类、热度、发布时间等）
3. 实时推荐：用户当前浏览时即时推荐相关内容
4. 离线推荐：每日生成个性化首页推荐列表
5. 冷启动策略：新用户/新内容的推荐方案
6. 多样性控制：避免信息茧房，保证推荐内容丰富度
7. A/B测试框架：支持不同推荐算法的效果对比
8. 可解释性：能告诉用户"为什么推荐这个"
9. 性能要求：推荐接口响应时间<100ms

目标用户：内容消费者（阅读文章、观看视频的用户）
业务指标：点击率提升30%，停留时长提升20%，次日留存提升15%""",
    }


def save_to_markdown(filename: str, content: str):
    """保存内容为Markdown文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


def calculate_token_usage(text: str) -> int:
    """估算token数量（粗略估算：1个中文约1.5个token，1个英文单词约1.3个token）"""
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    english_words = len(text.split())
    return int(chinese_chars * 1.5 + english_words * 1.3)
