"""
图片生成器
组合提示词构建和客户端调用，处理图片生成逻辑
"""
import logging
from typing import Optional
from flask import current_app

from ..base import BaseGenerator, ContentType, GenerationResult
from ..prompts.image_prompts import build_image_prompt
from ..clients.image import OpenAIImageClient, ImageAPIClient, MockImageClient

logger = logging.getLogger(__name__)


class ImageGenerator(BaseGenerator):
    """图片生成器"""
    
    SUPPORTED_TYPES = {ContentType.IMAGE}
    
    def __init__(self, provider: str = 'image_api', **kwargs):
        """
        初始化图片生成器
        
        Args:
            provider: 服务提供商 ('openai', 'image_api' 或 'mock')
            **kwargs: 其他配置参数
        """
        super().__init__(api_key=kwargs.get('api_key', ''), **kwargs)
        
        self.provider = provider
        
        # 根据 provider 创建对应的客户端
        if provider == 'mock':
            self.client = MockImageClient()
        elif provider == 'openai':
            api_key = kwargs.get('api_key') or current_app.config.get('OPENAI_API_KEY')
            base_url = kwargs.get('base_url') or current_app.config.get('OPENAI_BASE_URL')
            model = kwargs.get('model') or current_app.config.get('OPENAI_MODEL', 'dall-e-3')
            
            if not api_key:
                raise ValueError("OPENAI_API_KEY 未配置")
            
            self.client = OpenAIImageClient(api_key=api_key, base_url=base_url, model=model)
        elif provider == 'image_api':
            api_key = kwargs.get('api_key') or current_app.config.get('IMAGE_API_KEY')
            api_url = kwargs.get('api_url') or current_app.config.get('IMAGE_API_URL')
            model = kwargs.get('model') or current_app.config.get('IMAGE_MODEL', 'nano-banana')
            api_format = kwargs.get('apiFormat', 'chat')
            
            if not api_key or not api_url:
                raise ValueError("IMAGE_API_KEY 或 IMAGE_API_URL 未配置")
            
            self.client = ImageAPIClient(api_key=api_key, api_url=api_url, model=model, api_format=api_format)
        else:
            raise ValueError(f"不支持的 provider: {provider}")
        
        logger.info(f"图片生成器初始化完成: provider={provider}")
    
    def generate(
        self,
        content_type: ContentType,
        prompt: str,
        **kwargs
    ) -> GenerationResult:
        """
        生成图片
        
        Args:
            content_type: 内容类型
            prompt: 图片描述
            **kwargs: 其他参数（width, height, reference_image等）
            
        Returns:
            GenerationResult对象
        """
        if not self.supports(content_type):
            return self._create_unsupported_result(content_type)
        
        try:
            width = kwargs.get('width', 1080)
            height = kwargs.get('height', 1440)
            reference_image = kwargs.get('reference_image')
            
            # 1. 构建提示词（如果需要）
            # 对于图片生成，通常直接使用传入的 prompt
            # 但可以根据需要添加风格描述
            title = kwargs.get('title', '')
            description = kwargs.get('description', '')
            if title or description:
                prompt = build_image_prompt(title, description, kwargs.get('reference_style'))
            
            # 2. 调用客户端生成
            if isinstance(self.client, MockImageClient):
                image_url = self.client.generate(prompt, width, height, reference_image)
            elif isinstance(self.client, OpenAIImageClient):
                size = OpenAIImageClient.get_dalle_size(width, height)
                image_url = self.client.generate(prompt, size)
            elif isinstance(self.client, ImageAPIClient):
                image_url = self.client.generate(prompt, width, height, reference_image)
            else:
                raise ValueError(f"未知的客户端类型: {type(self.client)}")
            
            return self._create_success_result(
                content_type=ContentType.IMAGE,
                url=image_url,
                format="png",
                width=width,
                height=height
            )
            
        except Exception as e:
            logger.error(f"图片生成失败: {e}", exc_info=True)
            return self._create_error_result(ContentType.IMAGE, str(e))