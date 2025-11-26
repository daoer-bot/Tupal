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
            # 构建请求数据
            payload = {
                'prompt': prompt,
                'width': width,
                'height': height,
                'num_inference_steps': 20,
                'guidance_scale': 7.5
            }
            
            if reference_image:
                payload['reference_image'] = reference_image
            
            # 添加自定义参数
            payload.update(kwargs)
            
            # 发送请求
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 解析响应 - 适配不同厂家的返回格式
            image_url = None
            if 'image_url' in result:
                image_url = result['image_url']
            elif 'url' in result:
                image_url = result['url']
            elif 'images' in result and len(result['images']) > 0:
                image_url = result['images'][0]
            
            if image_url:
                return self._create_success_result(
                    content_type=ContentType.IMAGE,
                    url=image_url,
                    format="png",
                    width=width,
                    height=height
                )
            else:
                return self._create_error_result(
                    ContentType.IMAGE,
                    '无法从响应中获取图片URL'
                )
                
        except requests.exceptions.Timeout:
            logger.error("Image API 请求超时")
            return self._create_error_result(ContentType.IMAGE, '请求超时')
        except requests.exceptions.RequestException as e:
            logger.error(f"Image API 请求失败: {e}")
            return self._create_error_result(ContentType.IMAGE, str(e))
        except Exception as e:
            logger.error(f"Image API 生成失败: {e}")
            return self._create_error_result(ContentType.IMAGE, str(e))
    
    
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