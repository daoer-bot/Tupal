"""
模拟生成器
用于开发和测试，不需要真实的API Key
"""
import logging
from typing import Optional, Dict, Any
import time

from .base_generator import BaseGenerator, ContentType, GenerationResult

logger = logging.getLogger(__name__)


class MockGenerator(BaseGenerator):
    """模拟生成器实现 - 用于开发测试"""
    
    # 声明支持的内容类型（模拟器支持文本和图片）
    SUPPORTED_TYPES = {ContentType.TEXT, ContentType.IMAGE}
    
    def __init__(self, api_key: str = 'mock-key', **kwargs):
        super().__init__(api_key, **kwargs)
        logger.info("使用模拟生成器（Mock Generator）")
    
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
        # 根据类型分发
        if content_type == ContentType.TEXT:
            return self._generate_text(prompt, **kwargs)
        elif content_type == ContentType.IMAGE:
            return self._generate_image(prompt, **kwargs)
        
        return self._create_unsupported_result(content_type)
    
    def _generate_text(
        self,
        prompt: str,
        reference_image: Optional[str] = None,
        **kwargs
    ) -> GenerationResult:
        """
        模拟生成文本内容（大纲）
        
        Args:
            prompt: 主题描述
            reference_image: 参考图片
            **kwargs: 其他参数
            
        Returns:
            GenerationResult对象
        """
        logger.info(f"模拟生成大纲，主题: {prompt}")
        
        # 模拟API调用延迟
        time.sleep(0.5)
        
        # 生成模拟大纲
        pages = [
            {
                'page_number': 1,
                'title': '封面页',
                'description': f'关于「{prompt}」的完整指南 - 吸引眼球的封面设计'
            },
            {
                'page_number': 2,
                'title': '问题引入',
                'description': '为什么这个话题值得关注？痛点分析和场景描述'
            },
            {
                'page_number': 3,
                'title': '核心要点1',
                'description': '第一个重要知识点，配合实用案例说明'
            },
            {
                'page_number': 4,
                'title': '核心要点2',
                'description': '第二个关键技巧，提供具体操作步骤'
            },
            {
                'page_number': 5,
                'title': '核心要点3',
                'description': '第三个实用方法，展示前后对比效果'
            },
            {
                'page_number': 6,
                'title': '进阶技巧',
                'description': '更深入的应用场景和高级技巧分享'
            },
            {
                'page_number': 7,
                'title': '常见误区',
                'description': '避坑指南：需要注意的常见错误和解决方案'
            },
            {
                'page_number': 8,
                'title': '总结与行动',
                'description': '总结核心要点，提供可执行的行动清单'
            }
        ]
        
        return self._create_success_result(
            content_type=ContentType.TEXT,
            url="",
            format="json",
            pages=pages,
            topic=prompt
        )
    
    def _generate_image(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1440,
        reference_image: Optional[str] = None,
        **kwargs
    ) -> GenerationResult:
        """
        模拟生成图片
        
        Args:
            prompt: 图片描述
            width: 宽度
            height: 高度
            reference_image: 参考图片
            **kwargs: 其他参数
            
        Returns:
            GenerationResult对象
        """
        logger.info(f"模拟生成图片，提示: {prompt[:50]}...")
        
        # 模拟API调用延迟
        time.sleep(0.3)
        
        # 返回占位图片URL
        placeholder_url = f"https://via.placeholder.com/{width}x{height}/667eea/ffffff?text=Mock+Image"
        
        return self._create_success_result(
            content_type=ContentType.IMAGE,
            url=placeholder_url,
            format="png",
            width=width,
            height=height
        )
    
    