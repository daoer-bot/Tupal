"""
Image API 生成器
支持通用图片生成API（如 Nano banana Pro）
"""
import logging
from typing import Optional, Dict, Any
import requests
import time

from .base_generator import BaseGenerator, ContentType, GenerationResult

logger = logging.getLogger(__name__)


class ImageAPIGenerator(BaseGenerator):
    """Image API 生成器实现"""
    
    # 声明支持的内容类型（仅支持图片）
    SUPPORTED_TYPES = {ContentType.IMAGE}
    
    # 支持的模型列表（用于验证）
    SUPPORTED_MODELS = {
        'dall-e-3', 'dall-e-2', 'dalle-3', 'dalle-2',
        'dall-e-3-hd', 'stable-diffusion-xl', 'sdxl',
        'midjourney', 'flux-pro', 'flux-dev'
    }
    
    # 默认回退模型
    DEFAULT_MODEL = 'dall-e-3'
    
    def __init__(self, api_key: str, api_url: str = None, model: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.api_url = api_url or kwargs.get('url', '')
        requested_model = model or kwargs.get('model', self.DEFAULT_MODEL)
        
        # 验证并清理模型名称
        self.model = self._validate_and_normalize_model(requested_model)
        
        if not self.api_url:
            raise ValueError("Image API URL 不能为空")
        
        logger.info(f"ImageAPIGenerator 初始化: URL={self.api_url}, Model={self.model}")
        if self.model != requested_model:
            logger.warning(f"模型 '{requested_model}' 不受支持，已回退到 '{self.model}'")
    
    def _validate_and_normalize_model(self, model: str) -> str:
        """
        验证并规范化模型名称
        
        Args:
            model: 原始模型名称
            
        Returns:
            验证后的模型名称
        """
        if not model or not isinstance(model, str):
            logger.warning(f"无效的模型名称: {model}，使用默认模型: {self.DEFAULT_MODEL}")
            return self.DEFAULT_MODEL
        
        # 转换为小写进行比较
        model_lower = model.lower().strip()
        
        # 检查是否在支持列表中
        if model_lower in self.SUPPORTED_MODELS:
            return model_lower
        
        # 检查是否包含支持的关键词（部分匹配）
        for supported_model in self.SUPPORTED_MODELS:
            if supported_model in model_lower or model_lower in supported_model:
                logger.info(f"模型 '{model}' 部分匹配 '{supported_model}'，使用 '{supported_model}'")
                return supported_model
        
        # 检查是否是 Gemini 模型（不支持图片生成）
        if 'gemini' in model_lower:
            logger.warning(f"Gemini 模型 '{model}' 不支持图片生成，回退到 {self.DEFAULT_MODEL}")
            return self.DEFAULT_MODEL
        
        # 如果都不匹配，回退到默认模型
        logger.warning(f"不支持的模型 '{model}'，回退到默认模型: {self.DEFAULT_MODEL}")
        return self.DEFAULT_MODEL
    
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
        # 检查是否支持该类型
        if not self.supports(content_type):
            return self._create_unsupported_result(content_type)
        
        # 仅支持图片生成
        if content_type == ContentType.IMAGE:
            return self._generate_image(prompt, **kwargs)
        
        return self._create_unsupported_result(content_type)
    
    def _generate_image(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1440,
        reference_image: Optional[str] = None,
        **kwargs
    ) -> GenerationResult:
        """
        使用 Image API 生成图片
        
        Args:
            prompt: 图片描述
            width: 宽度
            height: 高度
            reference_image: 参考图片URL
            **kwargs: 其他参数
            
        Returns:
            GenerationResult对象
        """
        try:
            # 确保 API URL 包含完整的端点路径
            api_endpoint = self.api_url
            
            # 检查是否已经包含端点路径
            has_endpoint = api_endpoint.endswith('/images/generations')
            
            if not has_endpoint:
                # DALL-E 3 只支持 generations 端点，不支持 edits 或参考图片
                endpoint_suffix = '/images/generations'
                
                # 标准化 URL 拼接
                if api_endpoint.endswith('/v1'):
                    api_endpoint = f"{api_endpoint}{endpoint_suffix}"
                elif api_endpoint.endswith('/'):
                    api_endpoint = f"{api_endpoint.rstrip('/')}{endpoint_suffix}"
                else:
                    api_endpoint = f"{api_endpoint}{endpoint_suffix}"
            
            # 如果提供了参考图片，记录警告但继续生成（不使用参考图片）
            if reference_image:
                logger.warning(f"DALL-E 模型不支持参考图片功能，将忽略 reference_image 参数: {reference_image}")
            
            logger.info(f"使用 Image API 生成图片: {api_endpoint}")
            logger.info(f"提示词: {prompt[:100]}...")
            
            # 如果是 dall-e-3 模型，需要转换为支持的尺寸
            size = f"{width}x{height}"
            if self.model.lower() in ['dall-e-3', 'dalle-3', 'dall-e-3-hd']:
                size = self._get_dalle_size(width, height)
                logger.info(f"将尺寸 {width}x{height} 转换为 DALL-E 3 支持的尺寸: {size}")
            
            # 构建请求数据
            payload = {
                'model': self.model,  # 添加模型参数
                'prompt': prompt,
                'size': size,  # 使用转换后的尺寸
                'n': 1,
                'response_format': 'url'
            }
            
            # 注意: DALL-E 不支持 reference_image 参数
            # 如果 API 支持其他参数，可以通过 kwargs 传递
            
            # 添加自定义参数（会覆盖默认值），但排除 reference_image
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'reference_image'}
            payload.update(filtered_kwargs)
            
            logger.info(f"请求参数: {payload}")
            
            # 发送请求
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                api_endpoint,
                json=payload,
                headers=headers,
                timeout=120  # 增加超时时间，图片生成可能需要更长时间
            )
            
            logger.info(f"API 响应状态码: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"API 响应内容: {result}")
            
            # 解析响应 - 适配不同厂家的返回格式
            image_url = None
            
            # OpenAI 风格响应
            if 'data' in result and isinstance(result['data'], list) and len(result['data']) > 0:
                if 'url' in result['data'][0]:
                    image_url = result['data'][0]['url']
                elif 'b64_json' in result['data'][0]:
                    # 如果返回 base64，转换为 data URL
                    image_url = f"data:image/png;base64,{result['data'][0]['b64_json']}"
            # 其他常见格式
            elif 'image_url' in result:
                image_url = result['image_url']
            elif 'url' in result:
                image_url = result['url']
            elif 'images' in result and len(result['images']) > 0:
                if isinstance(result['images'][0], str):
                    image_url = result['images'][0]
                elif isinstance(result['images'][0], dict) and 'url' in result['images'][0]:
                    image_url = result['images'][0]['url']
            
            if image_url:
                logger.info(f"成功生成图片: {image_url[:100]}...")
                return self._create_success_result(
                    content_type=ContentType.IMAGE,
                    url=image_url,
                    format="png",
                    width=width,
                    height=height
                )
            else:
                error_msg = f'无法从响应中获取图片URL。响应内容: {result}'
                logger.error(error_msg)
                return self._create_error_result(ContentType.IMAGE, error_msg)
                
        except requests.exceptions.Timeout:
            logger.error("Image API 请求超时")
            return self._create_error_result(ContentType.IMAGE, '请求超时，请稍后重试')
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP 错误: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {e.response.text[:200]}"
            logger.error(f"Image API HTTP 错误: {error_msg}")
            return self._create_error_result(ContentType.IMAGE, error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"Image API 请求失败: {e}")
            return self._create_error_result(ContentType.IMAGE, f"请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"Image API 生成失败: {e}", exc_info=True)
            return self._create_error_result(ContentType.IMAGE, f"生成失败: {str(e)}")
    
    
    def _get_dalle_size(self, width: int, height: int) -> str:
        """
        将尺寸转换为 DALL-E 支持的格式
        
        Args:
            width: 宽度
            height: 高度
            
        Returns:
            DALL-E 尺寸字符串 (1024x1024, 1024x1792, 或 1792x1024)
        """
        # DALL-E 3 支持: 1024x1024, 1024x1792, 1792x1024
        ratio = width / height
        
        if ratio > 1.2:
            return "1792x1024"  # 横向
        elif ratio < 0.8:
            return "1024x1792"  # 竖向
        else:
            return "1024x1024"  # 正方形
    
    def generate_batch(
        self,
        prompts: list,
        width: int = 1080,
        height: int = 1440,
        reference_image: Optional[str] = None,
        delay: float = 0.1
    ) -> list:
        """
        批量生成图片
        
        Args:
            prompts: 提示词列表
            width: 宽度
            height: 高度
            reference_image: 参考图片
            delay: 请求间隔（秒）
            
        Returns:
            结果列表
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            logger.info(f"生成图片 {i+1}/{len(prompts)}")
            
            result = self.generate_image(
                prompt=prompt,
                width=width,
                height=height,
                reference_image=reference_image
            )
            
            results.append(result)
            
            # 添加延迟以避免速率限制
            if i < len(prompts) - 1:
                time.sleep(delay)
        
        return results