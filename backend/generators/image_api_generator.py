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
    
    # 默认模型
    DEFAULT_MODEL = 'nano-banana'
    
    def __init__(self, api_key: str, api_url: str = None, model: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.api_url = api_url or kwargs.get('url', '')
        self.model = model or kwargs.get('model', self.DEFAULT_MODEL)
        self.api_format = kwargs.get('apiFormat', 'chat')  # 默认使用 chat 格式（与前端一致）
        
        if not self.api_url:
            raise ValueError("Image API URL 不能为空")
        
        logger.info(f"ImageAPIGenerator 初始化: URL={self.api_url}, Model={self.model}, Format={self.api_format}")
    
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
        使用 Image API 生成图片，根据 api_format 调用不同的端点
        
        Args:
            prompt: 图片描述
            width: 宽度
            height: 高度
            reference_image: 参考图片URL
            **kwargs: 其他参数
            
        Returns:
            GenerationResult对象
        """
        # 根据 API 格式选择生成方法
        if self.api_format == 'chat':
            return self._generate_with_chat_format(prompt, width, height, reference_image, **kwargs)
        elif self.api_format == 'generations':
            return self._generate_with_generations_format(prompt, width, height, reference_image, **kwargs)
        elif self.api_format == 'official':
            return self._generate_with_official_format(prompt, width, height, reference_image, **kwargs)
        else:
            logger.error(f"不支持的 API 格式: {self.api_format}")
            return self._create_error_result(ContentType.IMAGE, f"不支持的 API 格式: {self.api_format}")
    
    def _generate_with_generations_format(
        self,
        prompt: str,
        width: int,
        height: int,
        reference_image: Optional[str],
        **kwargs
    ) -> GenerationResult:
        """使用 OpenAI DALL-E generations 格式生成图片 (/v1/images/generations)"""
        try:
            # 构建完整端点
            base_url = self.api_url.rstrip('/')
            if not base_url.endswith('/v1/images/generations'):
                api_endpoint = f"{base_url}/v1/images/generations"
            else:
                api_endpoint = base_url
            
            logger.info(f"使用 Generations 格式生成图片: {api_endpoint}")
            logger.info(f"提示词: {prompt[:100]}...")
            if reference_image:
                logger.info(f"检测到参考图片，将添加到请求中")
            
            # 直接使用传入的尺寸
            size = f"{width}x{height}"
            
            # 计算宽高比（某些 API 需要）
            aspect_ratio = self._calculate_aspect_ratio(width, height)
            
            payload = {
                'model': self.model,
                'prompt': prompt,
                'size': size,
                'n': 1,
                'response_format': 'url'
            }
            
            # 添加宽高比参数（某些 API 支持）
            if aspect_ratio:
                payload['aspect_ratio'] = aspect_ratio
            
            # 如果有参考图片，添加到 payload 中
            if reference_image:
                # 清理 base64 字符串：如果是 Data URL，移除其中的空白字符
                cleaned_reference = reference_image
                if reference_image.startswith('data:image'):
                    import re
                    # 分离前缀和 base64 数据
                    if ',' in reference_image:
                        prefix, base64_data = reference_image.split(',', 1)
                        # 移除 base64 数据中的所有空白字符
                        base64_data = re.sub(r'\s+', '', base64_data)
                        cleaned_reference = f"{prefix},{base64_data}"
                        logger.info(f"Generations - 参考图片 base64 数据长度: {len(base64_data)} 字符")
                        logger.info(f"Generations - 参考图片前缀: {prefix}")
                else:
                    logger.info(f"Generations - 参考图片 URL: {reference_image[:200]}...")
                
                payload['image'] = [cleaned_reference]
            
            # 添加其他可选参数
            filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['reference_image', 'width', 'height']}
            payload.update(filtered_kwargs)
            
            logger.info(f"请求参数: {payload}")
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(api_endpoint, json=payload, headers=headers, timeout=120)
            
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
            logger.error("Generations API 请求超时")
            return self._create_error_result(ContentType.IMAGE, '请求超时，请稍后重试')
        except requests.exceptions.HTTPError as e:
            error_msg = self._parse_http_error(e)
            logger.error(f"Generations API HTTP 错误: {error_msg}")
            return self._create_error_result(ContentType.IMAGE, error_msg)
        except Exception as e:
            logger.error(f"Generations 格式生成失败: {e}", exc_info=True)
            return self._create_error_result(ContentType.IMAGE, f"生成失败: {str(e)}")
    
    def _generate_with_chat_format(
        self,
        prompt: str,
        width: int,
        height: int,
        reference_image: Optional[str],
        **kwargs
    ) -> GenerationResult:
        """使用 OpenAI Chat 格式生成图片 (/v1/chat/completions)"""
        try:
            # 构建完整端点
            base_url = self.api_url.rstrip('/')
            if not base_url.endswith('/v1/chat/completions'):
                api_endpoint = f"{base_url}/v1/chat/completions"
            else:
                api_endpoint = base_url
            
            logger.info(f"使用 Chat 格式生成图片: {api_endpoint}")
            logger.info(f"提示词: {prompt[:100]}...")
            
            # 构建 messages 内容
            content = []
            
            # 添加文本提示
            content.append({
                "type": "text",
                "text": prompt
            })
            
            # 如果有参考图片，添加到 content 中
            if reference_image:
                logger.info("检测到参考图片，添加到请求中")
                
                # 清理 base64 字符串：如果是 Data URL，移除其中的空白字符
                cleaned_reference = reference_image
                if reference_image.startswith('data:image'):
                    import re
                    # 分离前缀和 base64 数据
                    if ',' in reference_image:
                        prefix, base64_data = reference_image.split(',', 1)
                        # 移除 base64 数据中的所有空白字符
                        base64_data = re.sub(r'\s+', '', base64_data)
                        cleaned_reference = f"{prefix},{base64_data}"
                        logger.info(f"参考图片 base64 数据长度: {len(base64_data)} 字符")
                        logger.info(f"参考图片前缀: {prefix}")
                        # 记录前100个字符用于调试
                        logger.info(f"Base64 前100字符: {base64_data[:100]}")
                else:
                    logger.info(f"参考图片 URL: {reference_image[:200]}...")
                
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": cleaned_reference
                    }
                })
            
            # 构建请求体 - 符合 OpenAI Chat Completions API 规范
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': content
                    }
                ],
                'max_tokens': kwargs.get('max_tokens', 4096),
            }
            
            # 添加可选参数
            if 'temperature' in kwargs:
                payload['temperature'] = kwargs['temperature']
            if 'top_p' in kwargs:
                payload['top_p'] = kwargs['top_p']
            if 'n' in kwargs:
                payload['n'] = kwargs['n']
            if 'stream' in kwargs:
                payload['stream'] = kwargs['stream']
            if 'stop' in kwargs:
                payload['stop'] = kwargs['stop']
            if 'presence_penalty' in kwargs:
                payload['presence_penalty'] = kwargs['presence_penalty']
            if 'frequency_penalty' in kwargs:
                payload['frequency_penalty'] = kwargs['frequency_penalty']
            
            logger.info(f"请求参数: {payload}")
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(api_endpoint, json=payload, headers=headers, timeout=120)
            
            logger.info(f"API 响应状态码: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"API 响应内容: {result}")
            
            # 解析 Chat Completions 响应格式
            image_url = None
            
            # 标准 OpenAI Chat Completions 响应格式
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                if 'message' in choice:
                    message = choice['message']
                    message_content = message.get('content', '')
                    
                    # 尝试从 content 中提取图片 URL
                    # 格式1: 纯文本 URL
                    if message_content.startswith('http'):
                        image_url = message_content.strip()
                    # 格式2: data URL (base64)
                    elif message_content.startswith('data:image'):
                        image_url = message_content
                    # 格式3: Markdown 格式 ![](url)
                    elif '![' in message_content and '](' in message_content:
                        import re
                        match = re.search(r'!\[.*?\]\((.*?)\)', message_content)
                        if match:
                            image_url = match.group(1)
                    # 格式4: 可能包含 JSON 格式
                    else:
                        try:
                            import json
                            content_json = json.loads(message_content)
                            if isinstance(content_json, dict):
                                image_url = content_json.get('url') or content_json.get('image_url')
                        except:
                            pass
            
            # 如果还没找到，尝试其他可能的格式
            if not image_url:
                # 有些实现可能直接在顶层返回
                if 'image_url' in result:
                    image_url = result['image_url']
                elif 'url' in result:
                    image_url = result['url']
                elif 'data' in result and isinstance(result['data'], list) and len(result['data']) > 0:
                    if 'url' in result['data'][0]:
                        image_url = result['data'][0]['url']
            
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
            logger.error("Chat API 请求超时")
            return self._create_error_result(ContentType.IMAGE, '请求超时，请稍后重试')
        except requests.exceptions.HTTPError as e:
            error_msg = self._parse_http_error(e)
            logger.error(f"Chat API HTTP 错误: {error_msg}")
            return self._create_error_result(ContentType.IMAGE, error_msg)
        except Exception as e:
            logger.error(f"Chat 格式生成失败: {e}", exc_info=True)
            return self._create_error_result(ContentType.IMAGE, f"生成失败: {str(e)}")
    
    def _generate_with_official_format(
        self,
        prompt: str,
        width: int,
        height: int,
        reference_image: Optional[str],
        **kwargs
    ) -> GenerationResult:
        """使用 Gemini 原生格式生成图片 (/v1beta/models/{model}:generateContent)"""
        try:
            # 构建完整端点
            base_url = self.api_url.rstrip('/')
            model_name = kwargs.get('model', 'gemini-3-pro-image-preview')
            
            # 构建端点URL，支持带或不带key参数
            if '?' in base_url:
                api_endpoint = f"{base_url}&key={self.api_key}"
            else:
                api_endpoint = f"{base_url}?key={self.api_key}"
            
            # 如果URL中没有包含模型路径，添加它
            if ':generateContent' not in api_endpoint:
                api_endpoint = f"{base_url}/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            
            logger.info(f"使用 Official 格式生成图片: {api_endpoint}")
            logger.info(f"提示词: {prompt[:100]}...")
            
            # 计算宽高比
            aspect_ratio = self._calculate_aspect_ratio(width, height)
            
            # 计算图片尺寸等级（1K, 2K, 4K等）
            image_size = self._calculate_image_size(width, height)
            
            # 构建请求体
            parts = [{"text": prompt}]
            
            # 如果有参考图片，添加到parts中
            if reference_image:
                # 假设reference_image是base64编码的数据或URL
                # 需要根据实际情况处理
                if reference_image.startswith('data:image'):
                    # 提取base64数据
                    mime_type = reference_image.split(';')[0].split(':')[1]
                    base64_data = reference_image.split(',')[1]
                    
                    # 清理 base64 字符串：移除所有空白字符
                    import re
                    base64_data = re.sub(r'\s+', '', base64_data)
                    
                    parts.append({
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64_data
                        }
                    })
                else:
                    logger.warning("参考图片格式不支持，需要base64编码的data URL")
            
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": parts
                    }
                ],
                "generationConfig": {
                    "responseModalities": ["TEXT", "IMAGE"],
                    "imageConfig": {
                        "aspectRatio": aspect_ratio,
                        "imageSize": image_size
                    }
                }
            }
            
            logger.info(f"请求参数: {payload}")
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(api_endpoint, json=payload, headers=headers, timeout=120)
            
            logger.info(f"API 响应状态码: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"API 响应内容: {result}")
            
            # 解析Gemini响应格式
            image_url = None
            
            # Gemini响应格式: candidates[0].content.parts[]中可能包含图片
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        # 查找图片数据
                        if 'inline_data' in part:
                            mime_type = part['inline_data'].get('mime_type', 'image/png')
                            data = part['inline_data'].get('data', '')
                            image_url = f"data:{mime_type};base64,{data}"
                            break
                        elif 'image' in part:
                            # 某些实现可能直接返回图片URL
                            if isinstance(part['image'], str):
                                image_url = part['image']
                            elif isinstance(part['image'], dict) and 'url' in part['image']:
                                image_url = part['image']['url']
                            break
            
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
                error_msg = f'无法从响应中获取图片数据。响应内容: {result}'
                logger.error(error_msg)
                return self._create_error_result(ContentType.IMAGE, error_msg)
                
        except requests.exceptions.Timeout:
            logger.error("Official API 请求超时")
            return self._create_error_result(ContentType.IMAGE, '请求超时，请稍后重试')
        except requests.exceptions.HTTPError as e:
            error_msg = self._parse_http_error(e)
            logger.error(f"Official API HTTP 错误: {error_msg}")
            return self._create_error_result(ContentType.IMAGE, error_msg)
        except Exception as e:
            logger.error(f"Official 格式生成失败: {e}", exc_info=True)
            return self._create_error_result(ContentType.IMAGE, f"生成失败: {str(e)}")
    
    def _parse_http_error(self, error: requests.exceptions.HTTPError) -> str:
        """
        解析HTTP错误并生成友好的错误提示
        
        Args:
            error: HTTPError异常对象
            
        Returns:
            友好的错误提示信息
        """
        status_code = error.response.status_code
        error_detail = None
        
        try:
            error_detail = error.response.json()
        except:
            error_detail = {"message": error.response.text[:200]}
        
        # 提取错误信息
        error_message = ""
        if isinstance(error_detail, dict):
            error_message = error_detail.get('error', {}).get('message', '') if 'error' in error_detail else error_detail.get('message', '')
        
        # 识别特定错误类型并提供友好提示
        if status_code == 422 or 'could not generate' in error_message.lower() or 'bad_response_body' in str(error_detail).lower():
            return (f"❌ 提示词被拒绝 (HTTP {status_code}):\n"
                   f"AI无法根据当前提示词生成图片。\n"
                   f"💡 建议：\n"
                   f"  1. 修改提示词，避免敏感或不当内容\n"
                   f"  2. 简化提示词描述，使其更清晰具体\n"
                   f"  3. 尝试用英文重新描述\n"
                   f"  4. 如果是内容审核问题，请调整描述方式\n"
                   f"原始错误: {error_message}")
        
        elif 'not supported model' in error_message.lower():
            return (f"❌ 模型不支持错误 (HTTP {status_code}):\n"
                   f"当前使用的模型 '{self.model}' 不被API提供商支持。\n"
                   f"💡 建议：\n"
                   f"  1. 检查模型配置，确认使用正确的模型名称\n"
                   f"  2. 对于此API，推荐使用 'dall-e-3' 或 'dall-e-2'\n"
                   f"  3. 如果使用Gemini模型，请切换到官方Gemini API或使用apiFormat='official'\n"
                   f"原始错误: {error_message}")
        
        elif 'invalid' in error_message.lower() and 'api' in error_message.lower() and 'key' in error_message.lower():
            return (f"❌ API密钥无效 (HTTP {status_code}):\n"
                   f"API密钥验证失败，请检查配置。\n"
                   f"💡 建议：\n"
                   f"  1. 确认.env文件中的IMAGE_API_KEY是否正确\n"
                   f"  2. 检查API密钥是否已过期\n"
                   f"原始错误: {error_message}")
        
        elif 'rate limit' in error_message.lower() or status_code == 429:
            return (f"❌ 请求频率限制 (HTTP {status_code}):\n"
                   f"API请求过于频繁，已达到速率限制。\n"
                   f"💡 建议：\n"
                   f"  1. 稍后重试\n"
                   f"  2. 减少并发请求数量\n"
                   f"  3. 检查是否有升级套餐选项\n"
                   f"原始错误: {error_message}")
        
        elif status_code == 401:
            return (f"❌ 认证失败 (HTTP {status_code}):\n"
                   f"API认证失败，请检查密钥配置。\n"
                   f"原始错误: {error_message}")
        
        elif status_code == 403:
            return (f"❌ 访问被拒绝 (HTTP {status_code}):\n"
                   f"没有权限访问此API资源。\n"
                   f"原始错误: {error_message}")
        
        elif status_code >= 500:
            return (f"❌ 服务器错误 (HTTP {status_code}):\n"
                   f"API服务器遇到错误，这通常是临时性问题。\n"
                   f"💡 建议：稍后重试\n"
                   f"原始错误: {error_message}")
        
        # 默认错误信息
        return f"HTTP错误 {status_code}: {error_detail}"
    
    def _calculate_aspect_ratio(self, width: int, height: int) -> str:
        """
        根据宽高计算宽高比字符串
        
        Args:
            width: 宽度
            height: 高度
            
        Returns:
            宽高比字符串，如 "16:9", "9:16", "1:1"
        """
        import math
        
        # 计算最大公约数
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        
        divisor = gcd(width, height)
        ratio_w = width // divisor
        ratio_h = height // divisor
        
        # 简化常见比例
        ratio = width / height
        if abs(ratio - 16/9) < 0.1:
            return "16:9"
        elif abs(ratio - 9/16) < 0.1:
            return "9:16"
        elif abs(ratio - 4/3) < 0.1:
            return "4:3"
        elif abs(ratio - 3/4) < 0.1:
            return "3:4"
        elif abs(ratio - 1) < 0.1:
            return "1:1"
        else:
            return f"{ratio_w}:{ratio_h}"
    
    def _calculate_image_size(self, width: int, height: int) -> str:
        """
        根据宽高计算图片尺寸等级
        
        Args:
            width: 宽度
            height: 高度
            
        Returns:
            尺寸等级字符串，如 "1K", "2K", "4K"
        """
        # 计算像素总数
        total_pixels = width * height
        
        # 1K ≈ 1024x1024 ≈ 1,048,576 像素
        # 2K ≈ 2048x2048 ≈ 4,194,304 像素
        # 4K ≈ 4096x4096 ≈ 16,777,216 像素
        
        if total_pixels <= 1_500_000:
            return "1K"
        elif total_pixels <= 5_000_000:
            return "2K"
        else:
            return "4K"
    
    
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