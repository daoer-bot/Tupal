"""
图片生成器
组合提示词构建和客户端调用，处理图片生成逻辑
"""
import logging
from typing import Optional

from ..base import BaseGenerator, ContentType, GenerationResult
from ..prompts.image_prompts import build_image_prompt
from ..clients.image import ImageAPIClient, MockImageClient
from ..clients.image.image_utils import get_dalle_size

logger = logging.getLogger(__name__)


def _get_flask_config(key: str, default: str = '') -> str:
    """
    安全地获取 Flask 配置，在应用上下文外返回默认值
    
    Args:
        key: 配置键名
        default: 默认值
        
    Returns:
        配置值或默认值
    """
    try:
        from flask import current_app
        return current_app.config.get(key, default)
    except RuntimeError:
        # 在应用上下文外，返回默认值
        return default


class ImageGenerator(BaseGenerator):
    """图片生成器"""
    
    SUPPORTED_TYPES = {ContentType.IMAGE}
    
    def __init__(self, provider: str = 'image_api', **kwargs):
        """
        初始化图片生成器
        
        Args:
            provider: 服务提供商 ('openai', 'image_api' 或 'mock')
            **kwargs: 其他配置参数，应包含所有必要的配置（api_key, api_url, model等）
                      在后台线程中调用时，必须显式传入所有配置
        """
        # 从 kwargs 中提取 api_key，避免重复传递给父类
        api_key = kwargs.pop('api_key', '')
        super().__init__(api_key=api_key, **kwargs)
        
        self.provider = provider
        
        # 根据 provider 创建对应的客户端
        if provider == 'mock':
            self.client = MockImageClient()
        elif provider == 'openai':
            # 优先使用传入的配置，回退到 Flask 配置（仅在应用上下文内有效）
            final_api_key = api_key or _get_flask_config('OPENAI_API_KEY')
            base_url = kwargs.get('base_url') or _get_flask_config('OPENAI_BASE_URL')
            model = kwargs.get('model') or _get_flask_config('OPENAI_MODEL', 'dall-e-3')
            
            if not final_api_key:
                raise ValueError("OPENAI_API_KEY 未配置")
            
            # 使用 ImageAPIClient 的 openai_dalle 格式
            self.client = ImageAPIClient(
                api_key=final_api_key,
                api_url=base_url or "https://api.openai.com",
                model=model,
                api_format='openai_dalle'
            )
        elif provider == 'image_api':
            # 优先使用传入的配置，回退到 Flask 配置（仅在应用上下文内有效）
            final_api_key = api_key or _get_flask_config('IMAGE_API_KEY')
            api_url = kwargs.get('api_url') or _get_flask_config('IMAGE_API_URL')
            model = kwargs.get('model') or _get_flask_config('IMAGE_MODEL', 'dall-e-3')
            api_format = kwargs.get('apiFormat', 'openai_dalle')
            
            if not final_api_key or not api_url:
                raise ValueError("IMAGE_API_KEY 或 IMAGE_API_URL 未配置")
            
            self.client = ImageAPIClient(
                api_key=final_api_key,
                api_url=api_url,
                model=model,
                api_format=api_format
            )
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
            elif isinstance(self.client, ImageAPIClient):
                # ImageAPIClient 统一处理所有格式
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