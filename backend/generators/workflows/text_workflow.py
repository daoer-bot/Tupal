"""
文本生成工作流
组合提示词构建和模型调用，处理业务逻辑
"""
import logging
from typing import Optional
from flask import current_app

from ..base_generator import BaseGenerator, ContentType, GenerationResult
from ..prompts.text_prompts import build_outline_prompt
from ..models.text.openai_text import OpenAITextModel
from ..models.text.mock_text import MockTextModel

logger = logging.getLogger(__name__)


class TextWorkflow(BaseGenerator):
    """文本生成工作流"""
    
    SUPPORTED_TYPES = {ContentType.TEXT}
    
    def __init__(self, provider: str = 'openai', **kwargs):
        """
        初始化文本工作流
        
        Args:
            provider: 服务提供商 ('openai' 或 'mock')
            **kwargs: 其他配置参数
        """
        super().__init__(api_key=kwargs.get('api_key', ''), **kwargs)
        
        self.provider = provider
        
        # 根据 provider 创建对应的模型
        if provider == 'mock':
            self.model = MockTextModel()
        elif provider == 'openai':
            api_key = kwargs.get('api_key') or current_app.config.get('OPENAI_API_KEY')
            base_url = kwargs.get('base_url') or current_app.config.get('OPENAI_BASE_URL')
            model = kwargs.get('model') or current_app.config.get('OPENAI_MODEL', 'gpt-4')
            
            if not api_key:
                raise ValueError("OPENAI_API_KEY 未配置")
            
            self.model = OpenAITextModel(api_key=api_key, base_url=base_url, model=model)
        else:
            raise ValueError(f"不支持的 provider: {provider}")
        
        logger.info(f"文本工作流初始化完成: provider={provider}")
    
    def generate(
        self,
        content_type: ContentType,
        prompt: str,
        **kwargs
    ) -> GenerationResult:
        """
        生成文本内容
        
        Args:
            content_type: 内容类型
            prompt: 主题描述
            **kwargs: 其他参数
            
        Returns:
            GenerationResult对象
        """
        if not self.supports(content_type):
            return self._create_unsupported_result(content_type)
        
        try:
            # 1. 构建提示词
            full_prompt = build_outline_prompt(prompt)
            
            # 2. 调用模型生成
            if isinstance(self.model, MockTextModel):
                result_data = self.model.generate(full_prompt)
            else:
                content = self.model.generate(full_prompt)
                result_data = OpenAITextModel.extract_json(content)
            
            # 3. 验证数据结构
            if not isinstance(result_data, dict):
                raise ValueError("解析结果不是有效的字典格式")
            
            if 'xiaohongshu_content' not in result_data or 'image_prompts' not in result_data:
                raise ValueError("缺少必要的字段: xiaohongshu_content 或 image_prompts")
            
            xiaohongshu_content = result_data['xiaohongshu_content']
            image_prompts = result_data['image_prompts']
            
            if not isinstance(image_prompts, list) or len(image_prompts) == 0:
                raise ValueError("image_prompts 必须是非空列表")
            
            # 4. 组装页面数据
            pages = []
            for prompt_item in image_prompts:
                page = {
                    'page_number': prompt_item.get('page_number'),
                    'title': prompt_item.get('title'),
                    'description': prompt_item.get('description'),
                    'xiaohongshu_content': xiaohongshu_content
                }
                pages.append(page)
            
            return self._create_success_result(
                content_type=ContentType.TEXT,
                url="",
                format="json",
                pages=pages,
                topic=prompt,
                xiaohongshu_content=xiaohongshu_content
            )
            
        except Exception as e:
            logger.error(f"文本生成失败: {e}", exc_info=True)
            return self._create_error_result(ContentType.TEXT, str(e))