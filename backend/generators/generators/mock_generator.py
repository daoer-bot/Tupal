"""
Mock 生成器
用于开发测试，同时支持文本和图片生成
"""
import logging

from ..base import BaseGenerator, ContentType, GenerationResult
from ..clients.text import MockTextClient
from ..clients.image import MockImageClient

logger = logging.getLogger(__name__)


class MockGenerator(BaseGenerator):
    """Mock 生成器"""
    
    SUPPORTED_TYPES = {ContentType.TEXT, ContentType.IMAGE}
    
    def __init__(self, **kwargs):
        """初始化 Mock 生成器"""
        super().__init__(api_key='mock-key', **kwargs)
        
        self.text_client = MockTextClient()
        self.image_client = MockImageClient()
        
        logger.info("Mock 生成器初始化完成")
    
    def generate(
        self,
        content_type: ContentType,
        prompt: str,
        **kwargs
    ) -> GenerationResult:
        """
        生成内容
        
        Args:
            content_type: 内容类型
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            GenerationResult对象
        """
        if not self.supports(content_type):
            return self._create_unsupported_result(content_type)
        
        try:
            if content_type == ContentType.TEXT:
                return self._generate_text(prompt, **kwargs)
            elif content_type == ContentType.IMAGE:
                return self._generate_image(prompt, **kwargs)
            
            return self._create_unsupported_result(content_type)
            
        except Exception as e:
            logger.error(f"Mock 生成失败: {e}", exc_info=True)
            return self._create_error_result(content_type, str(e))
    
    def _generate_text(self, prompt: str, **kwargs) -> GenerationResult:
        """生成文本"""
        result_data = self.text_client.generate(prompt)
        
        xiaohongshu_content = result_data['xiaohongshu_content']
        image_prompts = result_data['image_prompts']
        
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
    
    def _generate_image(self, prompt: str, **kwargs) -> GenerationResult:
        """生成图片"""
        width = kwargs.get('width', 1080)
        height = kwargs.get('height', 1440)
        reference_image = kwargs.get('reference_image')
        
        image_url = self.image_client.generate(prompt, width, height, reference_image)
        
        return self._create_success_result(
            content_type=ContentType.IMAGE,
            url=image_url,
            format="png",
            width=width,
            height=height
        )