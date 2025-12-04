"""
图片生成提示词构建
负责构建图片生成任务的提示词
"""
from typing import Optional


def build_image_prompt(
    title: str,
    description: str,
    reference_style: Optional[str] = None
) -> str:
    """
    构建图片生成提示词
    
    Args:
        title: 页面标题
        description: 页面描述
        reference_style: 参考风格描述
        
    Returns:
        完整的提示词
    """
    prompt = f"{title}. {description}"
    
    if reference_style:
        prompt += f" Style: {reference_style}"
    
    # 添加小红书风格提示
    prompt += " Social media style, clean and modern design, vibrant colors."
    
    return prompt