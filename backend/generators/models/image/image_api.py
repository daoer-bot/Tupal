"""
通用图片 API 模型调用
支持多种图片生成 API（如 nano-banana 等）
"""
import logging
import requests
import re
from typing import Optional

logger = logging.getLogger(__name__)


class ImageAPIModel:
    """通用图片 API 模型调用类"""
    
    def __init__(self, api_key: str, api_url: str, model: str = "nano-banana", api_format: str = "chat"):
        """
        初始化图片 API 模型
        
        Args:
            api_key: API 密钥
            api_url: API URL
            model: 模型名称
            api_format: API 格式 (chat/generations/official)
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.model = model
        self.api_format = api_format
        
        logger.info(f"图片 API 模型初始化: URL={self.api_url}, Model={self.model}, Format={self.api_format}")
    
    def generate(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1440,
        reference_image: Optional[str] = None
    ) -> str:
        """
        调用图片 API 生成图片
        
        Args:
            prompt: 图片描述
            width: 宽度
            height: 高度
            reference_image: 参考图片（base64 或 URL）
            
        Returns:
            图片 URL
        """
        if self.api_format == 'chat':
            return self._generate_chat(prompt, width, height, reference_image)
        elif self.api_format == 'generations':
            return self._generate_generations(prompt, width, height, reference_image)
        elif self.api_format == 'official':
            return self._generate_official(prompt, width, height, reference_image)
        else:
            raise ValueError(f"不支持的 API 格式: {self.api_format}")
    
    def _generate_chat(self, prompt: str, width: int, height: int, reference_image: Optional[str]) -> str:
        """使用 Chat 格式生成图片"""
        api_endpoint = f"{self.api_url}/v1/chat/completions" if not self.api_url.endswith('/v1/chat/completions') else self.api_url
        
        content = [{"type": "text", "text": prompt}]
        
        if reference_image:
            cleaned_reference = self._clean_base64(reference_image)
            content.append({
                "type": "image_url",
                "image_url": {"url": cleaned_reference}
            })
        
        payload = {
            'model': self.model,
            'messages': [{'role': 'user', 'content': content}],
            'max_tokens': 4096
        }
        
        response = requests.post(
            api_endpoint,
            json=payload,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            timeout=120
        )
        
        response.raise_for_status()
        result = response.json()
        
        return self._extract_image_url_from_chat(result)
    
    def _generate_generations(self, prompt: str, width: int, height: int, reference_image: Optional[str]) -> str:
        """使用 Generations 格式生成图片"""
        api_endpoint = f"{self.api_url}/v1/images/generations" if not self.api_url.endswith('/v1/images/generations') else self.api_url
        
        size = f"{width}x{height}"
        aspect_ratio = self._calculate_aspect_ratio(width, height)
        
        payload = {
            'model': self.model,
            'prompt': prompt,
            'size': size,
            'n': 1,
            'response_format': 'url'
        }
        
        if aspect_ratio:
            payload['aspect_ratio'] = aspect_ratio
        
        if reference_image:
            cleaned_reference = self._clean_base64(reference_image)
            payload['image'] = [cleaned_reference]
        
        response = requests.post(
            api_endpoint,
            json=payload,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            timeout=120
        )
        
        response.raise_for_status()
        result = response.json()
        
        return self._extract_image_url_from_generations(result)
    
    def _generate_official(self, prompt: str, width: int, height: int, reference_image: Optional[str]) -> str:
        """使用 Official 格式生成图片（Gemini 等）"""
        api_endpoint = self.api_url
        if '?' in api_endpoint:
            api_endpoint = f"{api_endpoint}&key={self.api_key}"
        else:
            api_endpoint = f"{api_endpoint}?key={self.api_key}"
        
        parts = [{"text": prompt}]
        
        if reference_image and reference_image.startswith('data:image'):
            mime_type = reference_image.split(';')[0].split(':')[1]
            base64_data = self._clean_base64(reference_image.split(',')[1])
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64_data
                }
            })
        
        aspect_ratio = self._calculate_aspect_ratio(width, height)
        image_size = self._calculate_image_size(width, height)
        
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio,
                    "imageSize": image_size
                }
            }
        }
        
        response = requests.post(
            api_endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        response.raise_for_status()
        result = response.json()
        
        return self._extract_image_url_from_official(result)
    
    @staticmethod
    def _clean_base64(data: str) -> str:
        """清理 base64 字符串"""
        if data.startswith('data:image'):
            if ',' in data:
                prefix, base64_data = data.split(',', 1)
                base64_data = re.sub(r'\s+', '', base64_data)
                return f"{prefix},{base64_data}"
        return re.sub(r'\s+', '', data)
    
    @staticmethod
    def _extract_image_url_from_chat(result: dict) -> str:
        """从 Chat 响应中提取图片 URL"""
        if 'choices' in result and len(result['choices']) > 0:
            message = result['choices'][0].get('message', {})
            content = message.get('content', '')
            
            if content.startswith('http') or content.startswith('data:image'):
                return content.strip()
            
            if '![' in content and '](' in content:
                match = re.search(r'!\[.*?\]\((.*?)\)', content)
                if match:
                    return match.group(1)
        
        if 'image_url' in result:
            return result['image_url']
        if 'url' in result:
            return result['url']
        
        raise ValueError(f"无法从响应中获取图片URL: {result}")
    
    @staticmethod
    def _extract_image_url_from_generations(result: dict) -> str:
        """从 Generations 响应中提取图片 URL"""
        if 'data' in result and isinstance(result['data'], list) and len(result['data']) > 0:
            if 'url' in result['data'][0]:
                return result['data'][0]['url']
            if 'b64_json' in result['data'][0]:
                return f"data:image/png;base64,{result['data'][0]['b64_json']}"
        
        if 'image_url' in result:
            return result['image_url']
        if 'url' in result:
            return result['url']
        
        raise ValueError(f"无法从响应中获取图片URL: {result}")
    
    @staticmethod
    def _extract_image_url_from_official(result: dict) -> str:
        """从 Official 响应中提取图片 URL"""
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                for part in candidate['content']['parts']:
                    if 'inline_data' in part:
                        mime_type = part['inline_data'].get('mime_type', 'image/png')
                        data = part['inline_data'].get('data', '')
                        return f"data:{mime_type};base64,{data}"
        
        raise ValueError(f"无法从响应中获取图片数据: {result}")
    
    @staticmethod
    def _calculate_aspect_ratio(width: int, height: int) -> str:
        """计算宽高比"""
        import math
        
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        
        divisor = gcd(width, height)
        ratio_w = width // divisor
        ratio_h = height // divisor
        
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
    
    @staticmethod
    def _calculate_image_size(width: int, height: int) -> str:
        """计算图片尺寸等级"""
        total_pixels = width * height
        
        if total_pixels <= 1_500_000:
            return "1K"
        elif total_pixels <= 5_000_000:
            return "2K"
        else:
            return "4K"