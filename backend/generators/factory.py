"""
AI 服务商工厂
根据配置创建合适的生成器实例
"""
import logging
from typing import Optional, Dict, Any, List
from flask import current_app

from .base_generator import BaseGenerator, ContentType
from .gemini_generator import GeminiGenerator
from .openai_generator import OpenAIGenerator
from .image_api_generator import ImageAPIGenerator
from .mock_generator import MockGenerator

logger = logging.getLogger(__name__)


class GeneratorFactory:
    """生成器工厂类 - 统一的生成器创建接口"""
    
    # 支持的生成器类型映射
    GENERATOR_TYPES = {
        'gemini': GeminiGenerator,
        'openai': OpenAIGenerator,
        'image_api': ImageAPIGenerator,
        'mock': MockGenerator
    }
    
    @staticmethod
    def create_generator(
        provider: str,
        content_type: Optional[ContentType] = None
    ) -> Optional[BaseGenerator]:
        """
        统一的生成器创建接口
        
        Args:
            provider: 服务商名称 ('gemini', 'openai', 'image_api', 'mock')
            content_type: 需要支持的内容类型（可选，用于验证）
            
        Returns:
            生成器实例，如果创建失败返回 None
        """
        try:
            if provider == 'mock':
                generator = MockGenerator()
            elif provider == 'gemini':
                api_key = current_app.config.get('GEMINI_API_KEY')
                if not api_key:
                    logger.error("GEMINI_API_KEY 未配置")
                    return None
                generator = GeminiGenerator(api_key=api_key)
            elif provider == 'openai':
                api_key = current_app.config.get('OPENAI_API_KEY')
                base_url = current_app.config.get('OPENAI_BASE_URL')
                if not api_key:
                    logger.error("OPENAI_API_KEY 未配置")
                    return None
                generator = OpenAIGenerator(api_key=api_key, base_url=base_url)
            elif provider == 'image_api':
                api_key = current_app.config.get('IMAGE_API_KEY')
                api_url = current_app.config.get('IMAGE_API_URL')
                if not api_key or not api_url:
                    logger.error("IMAGE_API_KEY 或 IMAGE_API_URL 未配置")
                    return None
                generator = ImageAPIGenerator(api_key=api_key, api_url=api_url)
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
        
        for provider, generator_class in GeneratorFactory.GENERATOR_TYPES.items():
            # 检查该生成器类是否支持指定的内容类型
            if content_type in generator_class.SUPPORTED_TYPES:
                # 进一步检查配置是否完整
                if provider == 'mock':
                    available.append(provider)
                elif provider == 'gemini' and current_app.config.get('GEMINI_API_KEY'):
                    available.append(provider)
                elif provider == 'openai' and current_app.config.get('OPENAI_API_KEY'):
                    available.append(provider)
                elif provider == 'image_api' and current_app.config.get('IMAGE_API_KEY') and current_app.config.get('IMAGE_API_URL'):
                    available.append(provider)
        
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
        if provider not in GeneratorFactory.GENERATOR_TYPES:
            return []
        
        generator_class = GeneratorFactory.GENERATOR_TYPES[provider]
        return [ct.value for ct in generator_class.SUPPORTED_TYPES]
    
    @staticmethod
    def get_all_capabilities() -> Dict[str, List[str]]:
        """
        获取所有服务商及其支持的能力
        
        Returns:
            服务商能力字典 {provider: [content_types]}
        """
        capabilities = {}
        
        for provider in GeneratorFactory.GENERATOR_TYPES.keys():
            caps = GeneratorFactory.get_provider_capabilities(provider)
            if caps:
                capabilities[provider] = caps
        
        return capabilities
    
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

def get_outline_generator(generator_type: str = 'gemini') -> Optional[BaseGenerator]:
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