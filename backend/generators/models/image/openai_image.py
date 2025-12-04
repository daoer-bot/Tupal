"""
OpenAI 图片模型调用（DALL-E）
纯粹的 API 调用，不包含业务逻辑
"""
import logging
import requests
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)


class OpenAIImageModel:
    """OpenAI 图片模型调用类"""
    
    def __init__(self, api_key: str, base_url: str = None, model: str = "dall-e-3"):
        """
        初始化 OpenAI 图片模型
        
        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            model: 模型名称
        """
        if OpenAI is None:
            raise ImportError("openai 未安装，请运行: pip install openai")
        
        # 处理 base_url
        if base_url:
            base_url = base_url.rstrip('/')
            if not base_url.endswith('/v1'):
                base_url = f"{base_url}/v1"
        
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=self.base_url)
        
        logger.info(f"OpenAI 图片模型初始化: base_url={self.base_url}, model={self.model}")
    
    def generate(self, prompt: str, size: str = "1024x1024") -> str:
        """
        调用 OpenAI API 生成图片
        
        Args:
            prompt: 图片描述
            size: 图片尺寸
            
        Returns:
            图片 URL
        """
        # 限制提示词长度
        if len(prompt) > 4000:
            logger.warning(f"提示词过长 ({len(prompt)} 字符)，截断到 4000 字符")
            prompt = prompt[:4000]
        
        logger.info(f"使用 {self.model} 生成图片，尺寸: {size}")
        
        # 检查是否是非标准模型
        if self.model not in ['dall-e-3', 'dall-e-2']:
            return self._generate_http(prompt, size)
        
        # 标准 DALL-E API 调用
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=size,
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        logger.info(f"图片生成成功: {image_url[:100]}...")
        
        return image_url
    
    def _generate_http(self, prompt: str, size: str) -> str:
        """
        使用 HTTP 请求生成图片（支持非标准模型）
        
        Args:
            prompt: 图片描述
            size: 图片尺寸
            
        Returns:
            图片 URL
        """
        logger.info(f"使用 HTTP 请求生成图片: {self.model}")
        
        response = requests.post(
            f"{self.base_url}/images/generations",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "prompt": prompt,
                "size": size,
                "n": 1
            },
            timeout=60
        )
        
        response.raise_for_status()
        result = response.json()
        
        if 'data' in result and len(result['data']) > 0:
            image_url = result['data'][0].get('url')
            if image_url:
                logger.info(f"图片生成成功: {image_url[:100]}...")
                return image_url
        
        raise ValueError("响应中没有图片 URL")
    
    @staticmethod
    def get_dalle_size(width: int, height: int) -> str:
        """
        将尺寸转换为 DALL-E 支持的格式
        
        Args:
            width: 宽度
            height: 高度
            
        Returns:
            DALL-E 尺寸字符串
        """
        ratio = width / height
        
        if ratio > 1.2:
            return "1536x1024"
        elif ratio < 0.8:
            return "1024x1536"
        else:
            return "1024x1024"
    
    @staticmethod
    def calculate_aspect_ratio(width: int, height: int) -> Optional[str]:
        """
        计算标准的宽高比
        
        Args:
            width: 宽度
            height: 高度
            
        Returns:
            宽高比字符串
        """
        supported_ratios = [
            (1, 1), (2, 3), (3, 2), (3, 4), (4, 3),
            (4, 5), (5, 4), (9, 16), (16, 9), (21, 9)
        ]
        
        ratio = width / height
        best_match = None
        min_diff = float('inf')
        
        for w, h in supported_ratios:
            standard_ratio = w / h
            diff = abs(ratio - standard_ratio)
            if diff < min_diff:
                min_diff = diff
                best_match = (w, h)
        
        if best_match:
            return f"{best_match[0]}:{best_match[1]}"
        
        return None