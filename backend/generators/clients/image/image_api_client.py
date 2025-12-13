"""
通用图片 API 客户端
支持多种图片生成 API 格式：
- openai_chat: OpenAI Chat API 兼容格式
- openai_dalle: OpenAI DALL-E API 格式
- gemini: Google Gemini API 格式
"""
import logging
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout
from typing import Optional

from .image_utils import (
    clean_base64,
    calculate_aspect_ratio,
    calculate_image_size,
    extract_url_from_markdown
)

logger = logging.getLogger(__name__)


class ImageAPIClient:
    """通用图片 API 客户端"""
    
    # 支持的 API 格式
    SUPPORTED_FORMATS = ['openai_chat', 'openai_dalle', 'gemini']
    
    def __init__(self, api_key: str, api_url: str, model: str = "dall-e-3", api_format: str = "openai_dalle"):
        """
        初始化图片 API 客户端
        
        Args:
            api_key: API 密钥
            api_url: API URL
            model: 模型名称
            api_format: API 格式 (openai_chat/openai_dalle/gemini)
        """
        if api_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的 API 格式: {api_format}，支持的格式: {self.SUPPORTED_FORMATS}")
        
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.model = model
        self.api_format = api_format
        
        logger.info(f"图片 API 客户端初始化: URL={self.api_url}, Model={self.model}, Format={self.api_format}")
    
    def generate(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
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
            图片 URL 或 base64 数据
        """
        if self.api_format == 'openai_chat':
            return self._generate_openai_chat(prompt, width, height, reference_image)
        elif self.api_format == 'openai_dalle':
            return self._generate_openai_dalle(prompt, width, height, reference_image)
        elif self.api_format == 'gemini':
            return self._generate_gemini(prompt, width, height, reference_image)
    
    def _generate_openai_chat(self, prompt: str, width: int, height: int, reference_image: Optional[str]) -> str:
        """使用 OpenAI Chat API 格式生成图片"""
        api_endpoint = f"{self.api_url}/v1/chat/completions" if not self.api_url.endswith('/v1/chat/completions') else self.api_url
        
        content = [{"type": "text", "text": prompt}]
        
        if reference_image:
            content.append({
                "type": "image_url",
                "image_url": {"url": clean_base64(reference_image)}
            })
        
        payload = {
            'model': self.model,
            'messages': [{'role': 'user', 'content': content}],
            'max_tokens': 4096
        }
        
        try:
            response = requests.post(
                api_endpoint,
                json=payload,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                },
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            return self._extract_from_chat_response(result)
        except HTTPError as e:
            raise self._create_friendly_error(e, api_endpoint)
        except ConnectionError:
            raise ConnectionError(f"无法连接到图片生成服务，请检查网络连接或 API 地址是否正确: {api_endpoint}")
        except Timeout:
            raise Timeout("图片生成请求超时，请稍后重试")
    
    def _generate_openai_dalle(self, prompt: str, width: int, height: int, reference_image: Optional[str]) -> str:
        """使用 OpenAI DALL-E API 格式生成图片"""
        api_endpoint = f"{self.api_url}/v1/images/generations" if not self.api_url.endswith('/v1/images/generations') else self.api_url
        
        payload = {
            'model': self.model,
            'prompt': prompt,
            'size': f"{width}x{height}",
            'n': 1,
            'response_format': 'url'
        }
        
        # 添加宽高比（某些服务支持）
        aspect_ratio = calculate_aspect_ratio(width, height)
        if aspect_ratio:
            payload['aspect_ratio'] = aspect_ratio
        
        # 添加参考图片（某些服务支持）
        if reference_image:
            payload['image'] = clean_base64(reference_image)
        
        try:
            response = requests.post(
                api_endpoint,
                json=payload,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                },
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            return self._extract_from_dalle_response(result)
        except HTTPError as e:
            raise self._create_friendly_error(e, api_endpoint)
        except ConnectionError:
            raise ConnectionError(f"无法连接到图片生成服务，请检查网络连接或 API 地址是否正确: {api_endpoint}")
        except Timeout:
            raise Timeout("图片生成请求超时，请稍后重试")
    
    def _generate_gemini(self, prompt: str, width: int, height: int, reference_image: Optional[str]) -> str:
        """使用 Google Gemini API 格式生成图片"""
        api_endpoint = self.api_url
        if '?' in api_endpoint:
            api_endpoint = f"{api_endpoint}&key={self.api_key}"
        else:
            api_endpoint = f"{api_endpoint}?key={self.api_key}"
        
        parts = [{"text": prompt}]
        
        # 添加参考图片
        if reference_image and reference_image.startswith('data:image'):
            mime_type = reference_image.split(';')[0].split(':')[1]
            base64_data = clean_base64(reference_image.split(',')[1])
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64_data
                }
            })
        
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "imageConfig": {
                    "aspectRatio": calculate_aspect_ratio(width, height),
                    "imageSize": calculate_image_size(width, height)
                }
            }
        }
        
        try:
            response = requests.post(
                api_endpoint,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                },
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            return self._extract_from_gemini_response(result)
        except HTTPError as e:
            raise self._create_friendly_error(e, api_endpoint)
        except ConnectionError:
            raise ConnectionError(f"无法连接到图片生成服务，请检查网络连接或 API 地址是否正确: {api_endpoint}")
        except Timeout:
            raise Timeout("图片生成请求超时，请稍后重试")
    
    @staticmethod
    def _extract_from_chat_response(result: dict) -> str:
        """从 Chat API 响应中提取图片 URL"""
        if 'choices' in result and len(result['choices']) > 0:
            message = result['choices'][0].get('message', {})
            content = message.get('content', '')
            
            # 直接返回 URL 或 base64
            if content.startswith(('http', 'data:image')):
                return content.strip()
            
            # 从 Markdown 中提取
            url = extract_url_from_markdown(content)
            if url:
                return url
        
        # 备用字段
        if 'image_url' in result:
            return result['image_url']
        if 'url' in result:
            return result['url']
        
        raise ValueError(f"无法从响应中获取图片URL: {result}")
    
    @staticmethod
    def _extract_from_dalle_response(result: dict) -> str:
        """从 DALL-E API 响应中提取图片 URL"""
        if 'data' in result and isinstance(result['data'], list) and len(result['data']) > 0:
            if 'url' in result['data'][0]:
                return result['data'][0]['url']
            if 'b64_json' in result['data'][0]:
                return f"data:image/png;base64,{result['data'][0]['b64_json']}"
        
        # 备用字段
        if 'image_url' in result:
            return result['image_url']
        if 'url' in result:
            return result['url']
        
        raise ValueError(f"无法从响应中获取图片URL: {result}")
    
    @staticmethod
    def _extract_from_gemini_response(result: dict) -> str:
        """从 Gemini API 响应中提取图片数据"""
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                for part in candidate['content']['parts']:
                    if 'inline_data' in part:
                        mime_type = part['inline_data'].get('mime_type', 'image/png')
                        data = part['inline_data'].get('data', '')
                        return f"data:{mime_type};base64,{data}"
        
        raise ValueError(f"无法从响应中获取图片数据: {result}")
    
    def _create_friendly_error(self, http_error: HTTPError, api_endpoint: str) -> Exception:
        """
        根据 HTTP 错误创建友好的错误信息
        
        Args:
            http_error: 原始 HTTP 错误
            api_endpoint: API 端点
            
        Returns:
            带有友好错误信息的异常
        """
        status_code = http_error.response.status_code if http_error.response is not None else 0
        
        # 根据状态码提供友好的错误信息
        error_messages = {
            400: "请求参数错误，请检查图片生成配置",
            401: "API 密钥无效或已过期，请检查配置",
            403: "API 访问被拒绝，请检查账户权限",
            404: "API 端点不存在，请检查 API 地址配置",
            429: "请求过于频繁，API 已限流，请稍后重试",
            500: "图片生成服务内部错误，请稍后重试",
            502: "图片生成服务网关错误，请稍后重试",
            503: "图片生成服务暂时不可用，可能正在维护中，请稍后重试",
            504: "图片生成服务响应超时，请稍后重试",
        }
        
        friendly_message = error_messages.get(
            status_code,
            f"图片生成服务返回错误 (HTTP {status_code})"
        )
        
        # 记录详细错误日志
        logger.error(f"图片 API 错误: {status_code} - {http_error} - 端点: {api_endpoint}")
        
        return Exception(friendly_message)