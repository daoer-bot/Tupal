"""
Image API 生成器
支持通用图片生成API（如 Nano banana Pro）
"""
import logging
from typing import Optional, Dict, Any
import requests
import time

from .base_generator import BaseGenerator, ContentType, GenerationResult

logger = logging.getLogger(__name__)


class ImageAPIGenerator(BaseGenerator):
    """Image API 生成器实现"""
    
    # 声明支持的内容类型（仅支持图片）
    SUPPORTED_TYPES = {ContentType.IMAGE}
    
    def __init__(self, api_key: str, api_url: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.api_url = api_url or kwargs.get('url', '')
        
        if not self.api_url:
            raise ValueError("Image API URL 不能为空")
    
    def generate(
        self,
        content_type: ContentType,
        prompt: str,
        **kwargs
    ) -> GenerationResult:
        """
        统一生成接口
        
        Args:
            content_type: 内容类型
            prompt: 生成提示词
            **kwargs: 其他参数
            
        Returns:
            GenerationResult对象
        """
        # 检查是否支持该类型
        if not self.supports(content_type):
            return self._create_unsupported_result(content_type)
        
        # 仅支持图片生成
        if content_type == ContentType.IMAGE:
            return self._generate_image(prompt, **kwargs)
        
        return self._create_unsupported_result(content_type)
    
    def _generate_image(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1440,
        reference_image: Optional[str] = None,
        **kwargs
    ) -> GenerationResult:
        """
        使用 Image API 生成图片
        
        Args:
            prompt: 图片描述
            width: 宽度
            height: 高度
            reference_image: 参考图片URL
            **kwargs: 其他参数
            
        Returns:
            GenerationResult对象
        """
        try:
            # 确保 API URL 包含完整的端点路径
            api_endpoint = self.api_url
            if not api_endpoint.endswith('/images/generations'):
                # 如果 URL 是 v1 结尾，添加图片生成端点
                if api_endpoint.endswith('/v1'):
                    api_endpoint = f"{api_endpoint}/images/generations"
                elif api_endpoint.endswith('/'):
                    api_endpoint = f"{api_endpoint}images/generations"
                else:
                    api_endpoint = f"{api_endpoint}/images/generations"
            
            logger.info(f"使用 Image API 生成图片: {api_endpoint}")
            logger.info(f"提示词: {prompt[:100]}...")
            
            # 构建请求数据
            payload = {
                'prompt': prompt,
                'size': f"{width}x{height}",  # 使用标准格式
                'n': 1,
                'response_format': 'url'
            }
            
            # 也支持原始格式以兼容不同的 API
            if reference_image:
                payload['reference_image'] = reference_image
            
            # 添加自定义参数
            payload.update(kwargs)
            
            logger.info(f"请求参数: {payload}")
            
            # 发送请求
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                api_endpoint,
                json=payload,
                headers=headers,
                timeout=120  # 增加超时时间，图片生成可能需要更长时间
            )
            
            logger.info(f"API 响应状态码: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"API 响应内容: {result}")
            
            # 解析响应 - 适配不同厂家的返回格式
            image_url = None
            
            # OpenAI 风格响应
            if 'data' in result and isinstance(result['data'], list) and len(result['data']) > 0:
                if 'url' in result['data'][0]:
                    image_url = result['data'][0]['url']
                elif 'b64_json' in result['data'][0]:
                    # 如果返回 base64，转换为 data URL
                    image_url = f"data:image/png;base64,{result['data'][0]['b64_json']}"
            # 其他常见格式
            elif 'image_url' in result:
                image_url = result['image_url']
            elif 'url' in result:
                image_url = result['url']
            elif 'images' in result and len(result['images']) > 0:
                if isinstance(result['images'][0], str):
                    image_url = result['images'][0]
                elif isinstance(result['images'][0], dict) and 'url' in result['images'][0]:
                    image_url = result['images'][0]['url']
            
            if image_url:
                logger.info(f"成功生成图片: {image_url[:100]}...")
                return self._create_success_result(
                    content_type=ContentType.IMAGE,
                    url=image_url,
                    format="png",
                    width=width,
                    height=height
                )
            else:
                error_msg = f'无法从响应中获取图片URL。响应内容: {result}'
                logger.error(error_msg)
                return self._create_error_result(ContentType.IMAGE, error_msg)
                
        except requests.exceptions.Timeout:
            logger.error("Image API 请求超时")
            return self._create_error_result(ContentType.IMAGE, '请求超时，请稍后重试')
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP 错误: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {e.response.text[:200]}"
            logger.error(f"Image API HTTP 错误: {error_msg}")
            return self._create_error_result(ContentType.IMAGE, error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"Image API 请求失败: {e}")
            return self._create_error_result(ContentType.IMAGE, f"请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"Image API 生成失败: {e}", exc_info=True)
            return self._create_error_result(ContentType.IMAGE, f"生成失败: {str(e)}")
    
    
    def generate_batch(
        self,
        prompts: list,
        width: int = 1080,
        height: int = 1440,
        reference_image: Optional[str] = None,
        delay: float = 0.1
    ) -> list:
        """
        批量生成图片
        
        Args:
            prompts: 提示词列表
            width: 宽度
            height: 高度
            reference_image: 参考图片
            delay: 请求间隔（秒）
            
        Returns:
            结果列表
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            logger.info(f"生成图片 {i+1}/{len(prompts)}")
            
            result = self.generate_image(
                prompt=prompt,
                width=width,
                height=height,
                reference_image=reference_image
            )
            
            results.append(result)
            
            # 添加延迟以避免速率限制
            if i < len(prompts) - 1:
                time.sleep(delay)
        
        return results