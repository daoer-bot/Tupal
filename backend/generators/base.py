"""
生成器基类
定义所有生成器的统一接口，支持多种内容生成能力

注意：文件已重命名为 base.py，此文件保持向后兼容
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Set, List
from enum import Enum


class ContentType(Enum):
    """内容类型枚举 - 简化为三大类"""
    TEXT = "text"          # 文本生成（大纲、文案等）
    IMAGE = "image"        # 图片生成（静态图、动图等）
    VIDEO = "video"        # 视频生成（短视频、动画等）


class GenerationResult:
    """统一的生成结果类"""
    
    def __init__(
        self,
        success: bool,
        content_type: ContentType,
        url: Optional[str] = None,
        format: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        self.success = success
        self.content_type = content_type
        self.url = url
        self.format = format
        self.metadata = metadata or {}
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            'success': self.success,
            'content_type': self.content_type.value
        }
        
        if self.success:
            result['result'] = {
                'url': self.url,
                'format': self.format,
                'metadata': self.metadata
            }
        else:
            result['error'] = self.error
        
        return result


class BaseGenerator(ABC):
    """生成器抽象基类"""
    
    # 子类需要声明支持的内容类型
    SUPPORTED_TYPES: Set[ContentType] = set()
    
    def __init__(self, api_key: str, **kwargs):
        """
        初始化生成器
        
        Args:
            api_key: API密钥
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.config = kwargs
    
    def supports(self, content_type: ContentType) -> bool:
        """
        检查是否支持指定的内容类型
        
        Args:
            content_type: 内容类型
            
        Returns:
            是否支持
        """
        return content_type in self.SUPPORTED_TYPES
    
    def get_supported_types(self) -> List[str]:
        """
        获取支持的内容类型列表
        
        Returns:
            内容类型字符串列表
        """
        return [ct.value for ct in self.SUPPORTED_TYPES]
    
    @abstractmethod
    def generate(
        self,
        content_type: ContentType,
        prompt: str,
        **kwargs
    ) -> GenerationResult:
        """
        统一的内容生成接口
        
        Args:
            content_type: 内容类型
            prompt: 生成提示词/主题描述
            **kwargs: 其他参数（如width, height, reference_image等）
            
        Returns:
            GenerationResult对象
            
        Raises:
            NotImplementedError: 当不支持该内容类型时
        """
        pass
    
    # ========== 兼容性方法（向后兼容旧代码） ==========
    
    def generate_image(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1440,
        reference_image: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成图片（兼容旧接口）
        
        Args:
            prompt: 图片描述文本
            width: 图片宽度
            height: 图片高度
            reference_image: 参考图片URL（可选）
            **kwargs: 其他参数
            
        Returns:
            包含生成结果的字典
        """
        if not self.supports(ContentType.IMAGE):
            return {
                'success': False,
                'error': f'{self.__class__.__name__} 不支持图片生成'
            }
        
        result = self.generate(
            content_type=ContentType.IMAGE,
            prompt=prompt,
            width=width,
            height=height,
            reference_image=reference_image,
            **kwargs
        )
        
        # 转换为旧格式
        if result.success:
            return {
                'success': True,
                'image_url': result.url
            }
        else:
            return {
                'success': False,
                'error': result.error
            }
    
    def generate_outline(
        self,
        topic: str,
        reference_image: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成内容大纲（兼容旧接口）
        
        Args:
            topic: 主题描述
            reference_image: 参考图片URL（可选）
            **kwargs: 其他参数
            
        Returns:
            包含大纲的字典
        """
        if not self.supports(ContentType.TEXT):
            return {
                'success': False,
                'error': f'{self.__class__.__name__} 不支持大纲生成',
                'pages': []
            }
        
        result = self.generate(
            content_type=ContentType.TEXT,
            prompt=topic,
            reference_image=reference_image,
            **kwargs
        )
        
        # 转换为旧格式
        if result.success:
            return {
                'success': True,
                'pages': result.metadata.get('pages', [])
            }
        else:
            return {
                'success': False,
                'error': result.error,
                'pages': []
            }
    
    def validate_config(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            配置是否有效
        """
        return bool(self.api_key)
    
    def _build_prompt(
        self,
        title: str,
        description: str,
        reference_style: Optional[str] = None
    ) -> str:
        """
        构建图片生成提示词
        
        Args:
            title: 页面标题
            description: 页面描述
            reference_style: 参考风格描述
            
        Returns:
            完整的提示词
        """
        prompt = f"{title}. {description}"
        
        if reference_style:
            prompt += f" Style: {reference_style}"
        
        # 添加小红书风格提示
        prompt += " Social media style, clean and modern design, vibrant colors."
        
        return prompt
    
    def _create_success_result(
        self,
        content_type: ContentType,
        url: str,
        format: str,
        **metadata
    ) -> GenerationResult:
        """
        创建成功的生成结果
        
        Args:
            content_type: 内容类型
            url: 生成内容的URL
            format: 文件格式
            **metadata: 其他元数据
            
        Returns:
            GenerationResult对象
        """
        return GenerationResult(
            success=True,
            content_type=content_type,
            url=url,
            format=format,
            metadata=metadata
        )
    
    def _create_error_result(
        self,
        content_type: ContentType,
        error: str
    ) -> GenerationResult:
        """
        创建失败的生成结果
        
        Args:
            content_type: 内容类型
            error: 错误信息
            
        Returns:
            GenerationResult对象
        """
        return GenerationResult(
            success=False,
            content_type=content_type,
            error=error
        )
    
    def _create_unsupported_result(
        self,
        content_type: ContentType
    ) -> GenerationResult:
        """
        创建不支持的内容类型结果
        
        Args:
            content_type: 内容类型
            
        Returns:
            GenerationResult对象
        """
        return GenerationResult(
            success=False,
            content_type=content_type,
            error=f'{self.__class__.__name__} 不支持 {content_type.value} 类型的生成'
        )