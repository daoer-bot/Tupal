"""
图片生成工作流
组合提示词构建和模型调用，处理业务逻辑
"""
import logging
from typing import Optional
from flask import current_app

from ..base_generator import BaseGenerator, ContentType, GenerationResult
from ..prompts.image_prompts import build_image_prompt
from ..models.image.openai_image import OpenAIImageModel
from ..models.image.image_api import ImageAPIModel
from ..models.image.mock_image import MockImageModel

logger = logging.getLogger(__name__)


class ImageWorkflow(BaseGenerator):
    """图片生成工作流"""
    
    SUPPORTED_TYPES = {ContentType.IMAGE}
    
    def __init__(self, provider: str = 'image_api', **kwargs):
        """
        初始化图片工作流
        
        Args:
            provider: 服务提供商 ('openai', 'image_api' 或 'mock')
            **kwargs: 其他配置参数
        """
        super().__init__(api_key=kwargs.get('api_key', ''), **kwargs)
        
        self.provider = provider
        
        # 根据 provider 创建对应的模型
        if provider == 'mock':
            self.model = MockImageModel()
        elif provider == 'openai':
            api_key = kwargs.get('api_key') or current_app.config.get('OPENAI_API_KEY')
            base_url = kwargs.get('base_url') or current_app.config.get('OPENAI_BASE_URL')
            model = kwargs.get('model') or current_app.config.get('OPENAI_MODEL', 'dall-e-3')
            
            if not api_key:
                raise ValueError("OPENAI_API_KEY 未配置")
            
            self.model = OpenAIImageModel(api_key=api_key, base_url=base_url, model=model)
        elif provider == 'image_api':
            api_key = kwargs.get('api_key') or current_app.config.get('IMAGE_API_KEY')
            api_url = kwargs.get('api_url') or current_app.config.get('IMAGE_API_URL')
            model = kwargs.get('model') or current_app.config.get('IMAGE_MODEL', 'nano-banana')
            api_format = kwargs.get('apiFormat', 'chat')
            
            if not api_key or not api_url:
                raise ValueError("IMAGE_API_KEY 或 IMAGE_API_URL 未配置")
            
            self.model = ImageAPIModel(api_key=api_key, api_url=api_url, model=model, api_format=api_format)
        else:
            raise ValueError(f"不支持的 provider: {provider}")
        
        logger.info(f"图片工作流初始化完成: provider={provider}")
    
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
            
            # 2. 调用模型生成
            if isinstance(self.model, MockImageModel):
                image_url = self.model.generate(prompt, width, height, reference_image)
            elif isinstance(self.model, OpenAIImageModel):
                size = OpenAIImageModel.get_dalle_size(width, height)
                image_url = self.model.generate(prompt, size)
            elif isinstance(self.model, ImageAPIModel):
                image_url = self.model.generate(prompt, width, height, reference_image)
            else:
                raise ValueError(f"未知的模型类型: {type(self.model)}")
            
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