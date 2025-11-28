"""
OpenAI 兼容生成器
支持 OpenAI API 和兼容接口（如 DALL-E 3）
"""
import logging
import json
import re
from typing import Optional, Dict, Any
import requests

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .base_generator import BaseGenerator, ContentType, GenerationResult

logger = logging.getLogger(__name__)


class OpenAIGenerator(BaseGenerator):
    """OpenAI 兼容生成器实现"""
    
    # 声明支持的内容类型（OpenAI同时支持文本和图片）
    SUPPORTED_TYPES = {ContentType.TEXT, ContentType.IMAGE}
    
    def __init__(self, api_key: str, base_url: str = None, model: str = None, **kwargs):
        if OpenAI is None:
            raise ImportError("openai 未安装，请运行: pip install openai")
        
        # 调试：打印接收到的所有参数
        logger.info(f"OpenAIGenerator.__init__ 接收到的 kwargs: {kwargs}")
        
        # OpenAI SDK 支持的参数列表
        supported_params = ['timeout', 'max_retries', 'default_headers', 'default_query', 'http_client']
        
        # 过滤 kwargs，只保留支持的参数
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in supported_params}
        
        logger.info(f"过滤后的 kwargs: {filtered_kwargs}")
        
        # 调用父类初始化，只传递过滤后的参数
        super().__init__(api_key, **filtered_kwargs)
        
        # 处理 base_url：如果用户只提供域名，自动添加 /v1
        if base_url:
            base_url = base_url.rstrip('/')  # 移除末尾斜杠
            if not base_url.endswith('/v1'):
                base_url = f"{base_url}/v1"
        
        self.base_url = base_url or "https://api.openai.com/v1"
        self.text_model = model or "gpt-4"  # 默认文本模型
        self.image_model = "dall-e-3"  # 图片模型
        
        logger.info(f"OpenAI 生成器初始化 - base_url: {self.base_url}")
        
        # 构建 OpenAI 客户端参数
        client_kwargs = {
            'api_key': self.api_key,
            'base_url': self.base_url
        }
        
        # 添加支持的可选参数
        for param in supported_params:
            if param in filtered_kwargs:
                client_kwargs[param] = filtered_kwargs[param]
        
        logger.info(f"传递给 OpenAI 客户端的参数: {list(client_kwargs.keys())}")
        
        # 创建 OpenAI 客户端（此时 client_kwargs 只包含支持的参数）
        self.client = OpenAI(**client_kwargs)
        
        logger.info("OpenAI 客户端创建成功")
    
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
        使用 GPT 生成文本内容（大纲）
        
        Args:
            prompt: 主题描述
            reference_image: 参考图片
            **kwargs: 其他参数
            
        Returns:
            GenerationResult对象
        """
        try:
            full_prompt = self._build_outline_prompt(prompt)
            
            logger.info(f"使用文本模型: {self.text_model}")
            
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的小红书内容策划专家。请务必返回有效的JSON格式。"},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7
            )
            
            # 获取响应内容
            content = response.choices[0].message.content
            logger.debug(f"OpenAI 原始响应: {content[:200]}...")
            
            # 提取并解析 JSON
            result_data = self._extract_and_parse_json(content)
            
            # 验证数据结构
            if not isinstance(result_data, dict):
                raise ValueError("解析结果不是有效的字典格式")
            
            if 'xiaohongshu_content' not in result_data or 'image_prompts' not in result_data:
                raise ValueError("缺少必要的字段: xiaohongshu_content 或 image_prompts")
            
            xiaohongshu_content = result_data['xiaohongshu_content']
            image_prompts = result_data['image_prompts']
            
            if not isinstance(image_prompts, list) or len(image_prompts) == 0:
                raise ValueError("image_prompts 必须是非空列表")
            
            # 将小红书文案添加到每个页面中
            pages = []
            for prompt_item in image_prompts:
                page = {
                    'page_number': prompt_item.get('page_number'),
                    'title': prompt_item.get('title'),
                    'description': prompt_item.get('description'),
                    'xiaohongshu_content': xiaohongshu_content  # 所有页面共享同一个文案
                }
                pages.append(page)
            
            return self._create_success_result(
                content_type=ContentType.TEXT,
                url="",
                format="json",
                pages=pages,
                topic=prompt,
                xiaohongshu_content=xiaohongshu_content  # 额外返回文案
            )
            
        except Exception as e:
            logger.error(f"OpenAI 文本生成失败: {e}", exc_info=True)
            return self._create_error_result(ContentType.TEXT, str(e))
    
    def _generate_image(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1440,
        reference_image: Optional[str] = None,
        **kwargs
    ) -> GenerationResult:
        """
        使用 DALL-E 3 生成图片
        
        注意：此功能需要真实的 OpenAI API 密钥和 DALL-E 3 访问权限。
        如果你使用的是第三方 API，可能不支持图片生成功能。
        建议使用 'image_api' 或 'mock' 生成器。
        
        Args:
            prompt: 图片描述
            width: 宽度
            height: 高度
            reference_image: 参考图片
            **kwargs: 其他参数
            
        Returns:
            GenerationResult对象
        """
        try:
            # DALL-E 3 支持的尺寸
            size = self._get_dalle_size(width, height)
            
            logger.info(f"尝试使用 {self.image_model} 生成图片: {prompt[:50]}...")
            
            # 调用 DALL-E API
            response = self.client.images.generate(
                model=self.image_model,
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info(f"DALL-E 3 图片生成成功: {image_url[:100]}...")
            
            return self._create_success_result(
                content_type=ContentType.IMAGE,
                url=image_url,
                format="png",
                width=width,
                height=height,
                size=size
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"OpenAI 图片生成失败: {error_msg}", exc_info=True)
            
            # 提供更友好的错误提示
            if "does not support" in error_msg or "image" in error_msg.lower():
                friendly_msg = (
                    "当前 API 不支持图片生成功能。"
                    "请在前端选择 'image_api' 或 'mock' 生成器来生成图片。"
                )
            else:
                friendly_msg = f"图片生成失败: {error_msg}"
            
            return self._create_error_result(ContentType.IMAGE, friendly_msg)
    
    
    def _extract_and_parse_json(self, content: str):
        """
        从响应中提取并解析 JSON
        
        Args:
            content: 响应内容
            
        Returns:
            解析后的字典或列表
        """
        # 策略1: 提取 markdown 代码块中的 JSON（对象或数组）
        json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                logger.debug("策略1失败: markdown 代码块解析失败")
        
        # 策略2: 提取第一个 JSON 对象
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                logger.debug("策略2失败: JSON 对象提取失败")
        
        # 策略3: 提取第一个 JSON 数组（向后兼容）
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                logger.debug("策略3失败: JSON 数组提取失败")
        
        # 策略4: 尝试直接解析整个内容
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            logger.debug("策略4失败: 直接解析失败")
        
        # 策略5: 清理并重试
        cleaned = content.strip()
        # 移除可能的前后缀文本
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.debug("策略5失败: 清理后解析失败")
        
        # 所有策略都失败
        raise json.JSONDecodeError(
            "无法从响应中提取有效的 JSON",
            content,
            0
        )
    
    def _get_dalle_size(self, width: int, height: int) -> str:
        """
        将尺寸转换为 DALL-E 支持的格式
        
        Args:
            width: 宽度
            height: 高度
            
        Returns:
            DALL-E 尺寸字符串
        """
        # DALL-E 3 支持: 1024x1024, 1024x1792, 1792x1024
        ratio = width / height
        
        if ratio > 1.2:
            return "1792x1024"  # 横向
        elif ratio < 0.8:
            return "1024x1792"  # 竖向
        else:
            return "1024x1024"  # 正方形
    
    def _build_outline_prompt(self, topic: str) -> str:
        """构建大纲生成提示词"""
        return f"""请根据以下主题，生成小红书图文内容。

主题: {topic}

要求：
1. 生成 3-5 个图片生成提示词（用于AI生成图片）
2. 生成 1 个小红书文案（最终展示给用户）
3. 每个图片提示词要详细描述视觉元素、色彩、构图、风格等
4. 小红书文案要有emoji表情、分段排版、吸引眼球，适合小红书平台风格

请严格以JSON格式返回：
```json
{{
  "xiaohongshu_content": "这里是完整的小红书文案内容，带emoji和排版📱✨\n\n第一段内容...\n\n第二段内容...",
  "image_prompts": [
    {{
      "page_number": 1,
      "title": "封面图",
      "description": "详细的图片生成提示词，包含视觉元素、色彩、构图等信息"
    }},
    {{
      "page_number": 2,
      "title": "内容图1",
      "description": "详细的图片生成提示词"
    }},
    {{
      "page_number": 3,
      "title": "内容图2",
      "description": "详细的图片生成提示词"
    }}
  ]
}}
```"""