"""
Mock 文本 API 客户端
用于开发测试
"""
import logging
import time

logger = logging.getLogger(__name__)


class MockTextClient:
    """Mock 文本 API 客户端"""
    
    def __init__(self):
        """初始化 Mock 文本客户端"""
        logger.info("使用 Mock 文本客户端")
    
    def generate(self, prompt: str, temperature: float = 0.7) -> dict:
        """
        模拟生成文本
        
        Args:
            prompt: 提示词
            temperature: 温度参数（未使用）
            
        Returns:
            模拟的 JSON 数据
        """
        logger.info(f"Mock 文本生成，提示词长度: {len(prompt)}")
        
        # 模拟 API 延迟
        time.sleep(0.5)
        
        # 从提示词中提取主题
        topic = "主题"
        if "用户的要求以及说明：" in prompt:
            lines = prompt.split("\n")
            for i, line in enumerate(lines):
                if "用户的要求以及说明：" in line and i + 1 < len(lines):
                    topic = lines[i + 1].strip()
                    break
        
        return {
            "xiaohongshu_content": f"📱✨ {topic} 完整指南\n\n这是一份关于{topic}的详细教程，帮助你快速掌握核心要点！\n\n💡 记得点赞收藏哦~",
            "image_prompts": [
                {
                    "page_number": 1,
                    "title": "封面页",
                    "description": f"关于「{topic}」的完整指南 - 吸引眼球的封面设计"
                },
                {
                    "page_number": 2,
                    "title": "问题引入",
                    "description": "为什么这个话题值得关注？痛点分析和场景描述"
                },
                {
                    "page_number": 3,
                    "title": "核心要点1",
                    "description": "第一个重要知识点，配合实用案例说明"
                },
                {
                    "page_number": 4,
                    "title": "核心要点2",
                    "description": "第二个关键技巧，提供具体操作步骤"
                },
                {
                    "page_number": 5,
                    "title": "核心要点3",
                    "description": "第三个实用方法，展示前后对比效果"
                },
                {
                    "page_number": 6,
                    "title": "进阶技巧",
                    "description": "更深入的应用场景和高级技巧分享"
                },
                {
                    "page_number": 7,
                    "title": "常见误区",
                    "description": "避坑指南：需要注意的常见错误和解决方案"
                },
                {
                    "page_number": 8,
                    "title": "总结与行动",
                    "description": "总结核心要点，提供可执行的行动清单"
                }
            ]
        }