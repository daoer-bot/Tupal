"""
Mock 图片模型
用于开发测试
"""
import logging
import time

logger = logging.getLogger(__name__)


class MockImageModel:
    """Mock 图片模型类"""
    
    def __init__(self):
        """初始化 Mock 图片模型"""
        logger.info("使用 Mock 图片模型")
    
    def generate(self, prompt: str, width: int = 1080, height: int = 1440, reference_image: str = None) -> str:
        """
        模拟生成图片
        
        Args:
            prompt: 图片描述
            width: 宽度
            height: 高度
            reference_image: 参考图片（未使用）
            
        Returns:
            图片 URL（base64 编码的 SVG）
        """
        logger.info(f"Mock 图片生成，尺寸: {width}x{height}")
        
        # 模拟 API 延迟
        time.sleep(0.3)
        
        # 返回 base64 编码的 SVG 占位图
        placeholder_url = (
            "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTA4MCIgaGVpZ2h0PSIxNDQwIiB4bWxucz0iaHR0cDov"
            "L3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0iZ3JhZCIgeDE9IjAlIiB5MT0iMCUi"
            "IHgyPSIwJSIgeTI9IjEwMCUiPjxzdG9wIG9mZnNldD0iMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiM2NjdlZWE7c3RvcC1v"
            "cGFjaXR5OjEiIC8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdHlsZT0ic3RvcC1jb2xvcjojNzY0YmE4O3N0b3Atb3BhY2l0"
            "eToxIiAvPjwvbGluZWFyR3JhZGllbnQ+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9"
            "InVybCgjZ3JhZCkiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBm"
            "b250LXNpemU9IjQ4IiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iIGZvbnQtd2VpZ2h0"
            "PSJib2xkIj5Nb2NrIEltYWdlPC90ZXh0Pjx0ZXh0IHg9IjUwJSIgeT0iNjAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNh"
            "bnMtc2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSIg"
            "b3BhY2l0eT0iMC44Ij57fXgge308L3RleHQ+PC9zdmc+"
        ).format(width, height)
        
        return placeholder_url