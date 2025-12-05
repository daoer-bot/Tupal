"""
图片生成工具函数
提供通用的图片处理和格式转换功能
"""
import re
from typing import Optional


def clean_base64(data: str) -> str:
    """
    清理 base64 字符串，移除空白字符
    
    Args:
        data: base64 字符串（可能包含 data URI 前缀）
        
    Returns:
        清理后的 base64 字符串
    """
    if data.startswith('data:image'):
        if ',' in data:
            prefix, base64_data = data.split(',', 1)
            base64_data = re.sub(r'\s+', '', base64_data)
            return f"{prefix},{base64_data}"
    return re.sub(r'\s+', '', data)


def calculate_aspect_ratio(width: int, height: int) -> str:
    """
    计算标准宽高比
    
    Args:
        width: 宽度
        height: 高度
        
    Returns:
        宽高比字符串（如 "16:9", "4:3", "1:1"）
    """
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    divisor = gcd(width, height)
    ratio_w = width // divisor
    ratio_h = height // divisor
    
    # 匹配常见宽高比
    ratio = width / height
    if abs(ratio - 16/9) < 0.1:
        return "16:9"
    elif abs(ratio - 9/16) < 0.1:
        return "9:16"
    elif abs(ratio - 4/3) < 0.1:
        return "4:3"
    elif abs(ratio - 3/4) < 0.1:
        return "3:4"
    elif abs(ratio - 1) < 0.1:
        return "1:1"
    else:
        return f"{ratio_w}:{ratio_h}"


def calculate_image_size(width: int, height: int) -> str:
    """
    根据像素总数计算图片尺寸等级
    
    Args:
        width: 宽度
        height: 高度
        
    Returns:
        尺寸等级（"1K", "2K", "4K"）
    """
    total_pixels = width * height
    
    if total_pixels <= 1_500_000:
        return "1K"
    elif total_pixels <= 5_000_000:
        return "2K"
    else:
        return "4K"


def get_dalle_size(width: int, height: int) -> str:
    """
    将任意尺寸转换为 DALL-E 支持的标准尺寸
    
    Args:
        width: 宽度
        height: 高度
        
    Returns:
        DALL-E 标准尺寸字符串（"1024x1024", "1536x1024", "1024x1536"）
    """
    ratio = width / height
    
    if ratio > 1.2:  # 横向
        return "1792x1024"
    elif ratio < 0.8:  # 纵向
        return "1024x1792"
    else:  # 方形
        return "1024x1024"


def extract_url_from_markdown(text: str) -> Optional[str]:
    """
    从 Markdown 格式中提取 URL
    
    Args:
        text: 可能包含 Markdown 图片链接的文本
        
    Returns:
        提取的 URL，如果没有则返回 None
    """
    if '![' in text and '](' in text:
        match = re.search(r'!\[.*?\]\((.*?)\)', text)
        if match:
            return match.group(1)
    return None