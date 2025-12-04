"""
AI 服务商工厂
根据配置创建合适的生成器实例
"""
import logging
from typing import Optional, Dict, Any, List
from flask import current_app

from .base_generator import BaseGenerator, ContentType
from .workflows.text_workflow import TextWorkflow
from .workflows.image_workflow import ImageWorkflow
from .workflows.mock_workflow import MockWorkflow

logger = logging.getLogger(__name__)


class GeneratorFactory:
    """生成器工厂类 - 统一的生成器创建接口"""
    
    # 支持的生成器类型映射
    GENERATOR_TYPES = {
        'openai': {'text': TextWorkflow, 'image': ImageWorkflow},
        'image_api': {'image': ImageWorkflow},
        'mock': {'text': MockWorkflow, 'image': MockWorkflow}
    }
    
    @staticmethod
    def create_generator(
        provider: str,
        content_type: Optional[ContentType] = None
    ) -> Optional[BaseGenerator]:
        """
        统一的生成器创建接口
        
        Args:
            provider: 服务商名称 ('openai', 'image_api', 'mock')
            content_type: 需要支持的内容类型（可选，用于验证）
            
        Returns:
            生成器实例，如果创建失败返回 None
        """
        try:
            if provider == 'mock':
                generator = MockWorkflow()
            elif provider == 'openai':
                # 根据 content_type 选择工作流
                if content_type == ContentType.TEXT:
                    api_key = current_app.config.get('OPENAI_API_KEY')
                    base_url = current_app.config.get('OPENAI_BASE_URL')
                    model = current_app.config.get('OPENAI_MODEL', 'gpt-4')
                    
                    if not api_key:
                        logger.error("OPENAI_API_KEY 未配置")
                        return None
                    
                    generator = TextWorkflow(
                        provider='openai',
                        api_key=api_key,
                        base_url=base_url,
                        model=model
                    )
                elif content_type == ContentType.IMAGE:
                    api_key = current_app.config.get('OPENAI_API_KEY')
                    base_url = current_app.config.get('OPENAI_BASE_URL')
                    model = current_app.config.get('OPENAI_MODEL', 'dall-e-3')
                    
                    if not api_key:
                        logger.error("OPENAI_API_KEY 未配置")
                        return None
                    
                    generator = ImageWorkflow(
                        provider='openai',
                        api_key=api_key,
                        base_url=base_url,
                        model=model
                    )
                else:
                    # 默认创建文本工作流
                    api_key = current_app.config.get('OPENAI_API_KEY')
                    base_url = current_app.config.get('OPENAI_BASE_URL')
                    model = current_app.config.get('OPENAI_MODEL', 'gpt-4')
                    
                    if not api_key:
                        logger.error("OPENAI_API_KEY 未配置")
                        return None
                    
                    generator = TextWorkflow(
                        provider='openai',
                        api_key=api_key,
                        base_url=base_url,
                        model=model
                    )
            elif provider == 'image_api':
                api_key = current_app.config.get('IMAGE_API_KEY')
                api_url = current_app.config.get('IMAGE_API_URL')
                model = current_app.config.get('IMAGE_MODEL', 'nano-banana')
                
                if not api_key or not api_url:
                    logger.error("IMAGE_API_KEY 或 IMAGE_API_URL 未配置")
                    return None
                
                generator = ImageWorkflow(
                    provider='image_api',
                    api_key=api_key,
                    api_url=api_url,
                    model=model
                )
            else:
                logger.error(f"不支持的生成器类型: {provider}")
                return None
            
            # 如果指定了内容类型，验证生成器是否支持
            if content_type and not generator.supports(content_type):
                logger.error(f"{provider} 不支持 {content_type.value} 类型的生成")
                return None
            
            return generator
            
        except Exception as e:
            logger.error(f"创建生成器失败 ({provider}): {e}")
            return None
    
    @staticmethod
    def get_available_providers(content_type: ContentType) -> List[str]:
        """
        获取支持指定内容类型的服务商列表
        
        Args:
            content_type: 内容类型
            
        Returns:
            支持的服务商名称列表
        """
        available = []
        
        # Mock 总是可用
        if content_type in MockWorkflow.SUPPORTED_TYPES:
            available.append('mock')
        
        # 检查 OpenAI
        if content_type in TextWorkflow.SUPPORTED_TYPES or content_type in ImageWorkflow.SUPPORTED_TYPES:
            if current_app.config.get('OPENAI_API_KEY'):
                available.append('openai')
        
        # 检查 Image API
        if content_type == ContentType.IMAGE:
            if current_app.config.get('IMAGE_API_KEY') and current_app.config.get('IMAGE_API_URL'):
                available.append('image_api')
        
        return available
    
    @staticmethod
    def get_provider_capabilities(provider: str) -> List[str]:
        """
        获取指定服务商支持的内容类型
        
        Args:
            provider: 服务商名称
            
        Returns:
            支持的内容类型列表
        """
        if provider == 'mock':
            return [ct.value for ct in MockWorkflow.SUPPORTED_TYPES]
        elif provider == 'openai':
            return [ContentType.TEXT.value, ContentType.IMAGE.value]
        elif provider == 'image_api':
            return [ContentType.IMAGE.value]
        
        return []
    
    @staticmethod
    def get_all_capabilities() -> Dict[str, List[str]]:
        """
        获取所有服务商及其支持的能力
        
        Returns:
            服务商能力字典 {provider: [content_types]}
        """
        return {
            'mock': [ContentType.TEXT.value, ContentType.IMAGE.value],
            'openai': [ContentType.TEXT.value, ContentType.IMAGE.value],
            'image_api': [ContentType.IMAGE.value]
        }
    
    @staticmethod
    def validate_generator(generator: BaseGenerator) -> bool:
        """
        验证生成器配置是否有效
        
        Args:
            generator: 生成器实例
            
        Returns:
            是否有效
        """
        if generator is None:
            return False
        
        return generator.validate_config()


# ========== 便捷函数（向后兼容） ==========

def get_outline_generator(generator_type: str = 'openai') -> Optional[BaseGenerator]:
    """
    获取大纲生成器（兼容旧接口）
    
    Args:
        generator_type: 生成器类型
        
    Returns:
        生成器实例
    """
    return GeneratorFactory.create_generator(generator_type, ContentType.TEXT)


def get_image_generator(generator_type: str = 'image_api') -> Optional[BaseGenerator]:
    """
    获取图片生成器（兼容旧接口）
    
    Args:
        generator_type: 生成器类型
        
    Returns:
        生成器实例
    """
    return GeneratorFactory.create_generator(generator_type, ContentType.IMAGE)