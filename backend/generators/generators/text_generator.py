"""
文本生成器
组合提示词构建和客户端调用，处理文本生成逻辑
"""
import logging
from typing import Optional
from flask import current_app

from ..base import BaseGenerator, ContentType, GenerationResult
from ..prompts.text_prompts import build_outline_prompt
from ..clients.text import OpenAITextClient, MockTextClient

logger = logging.getLogger(__name__)


class TextGenerator(BaseGenerator):
    """文本生成器"""
    
    SUPPORTED_TYPES = {ContentType.TEXT}
    
    def __init__(self, provider: str = 'openai', **kwargs):
        """
        初始化文本生成器
        
        Args:
            provider: 服务提供商 ('openai' 或 'mock')
            **kwargs: 其他配置参数 (api_key, base_url, model 等)
        """
        # 从 kwargs 中提取 api_key，避免重复传递
        api_key = kwargs.pop('api_key', '')
        super().__init__(api_key=api_key, **kwargs)
        
        self.provider = provider
        
        # 根据 provider 创建对应的客户端
        if provider == 'mock':
            self.client = MockTextClient()
        elif provider == 'openai':
            # 使用已提取的 api_key 或从配置获取
            effective_api_key = api_key or current_app.config.get('OPENAI_API_KEY')
            base_url = kwargs.get('base_url') or current_app.config.get('OPENAI_BASE_URL')
            model = kwargs.get('model') or current_app.config.get('OPENAI_MODEL', 'gpt-4')
            
            if not effective_api_key:
                raise ValueError("OPENAI_API_KEY 未配置")
            
            self.client = OpenAITextClient(api_key=effective_api_key, base_url=base_url, model=model)
        else:
            raise ValueError(f"不支持的 provider: {provider}")
        
        logger.info(f"文本生成器初始化完成: provider={provider}")
    
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
            
            # 2. 调用客户端生成
            if isinstance(self.client, MockTextClient):
                result_data = self.client.generate(full_prompt)
            else:
                content = self.client.generate(full_prompt)
                result_data = OpenAITextClient.extract_json(content)
            
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