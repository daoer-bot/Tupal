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
    
    def __init__(self, api_key: str, base_url: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        
        if OpenAI is None:
            raise ImportError("openai 未安装，请运行: pip install openai")
        
        self.base_url = base_url or "https://api.openai.com/v1"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
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
            
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash-lite-preview-09-2025",
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
            pages = self._extract_and_parse_json(content)
            
            if not pages or not isinstance(pages, list):
                raise ValueError("解析结果不是有效的列表格式")
            
            return self._create_success_result(
                content_type=ContentType.TEXT,
                url="",
                format="json",
                pages=pages,
                topic=prompt
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
            
            # 调用 DALL-E API
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            return self._create_success_result(
                content_type=ContentType.IMAGE,
                url=response.data[0].url,
                format="png",
                width=width,
                height=height,
                size=size
            )
            
        except Exception as e:
            logger.error(f"OpenAI 图片生成失败: {e}")
            return self._create_error_result(ContentType.IMAGE, str(e))
    
    
    def _extract_and_parse_json(self, content: str) -> list:
        """
        从响应中提取并解析 JSON
        
        Args:
            content: 响应内容
            
        Returns:
            解析后的列表
        """
        # 策略1: 提取 markdown 代码块中的 JSON
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                logger.debug("策略1失败: markdown 代码块解析失败")
        
        # 策略2: 提取第一个 JSON 数组
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                logger.debug("策略2失败: JSON 数组提取失败")
        
        # 策略3: 尝试直接解析整个内容
        try:
            result = json.loads(content)
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'pages' in result:
                return result['pages']
        except json.JSONDecodeError:
            logger.debug("策略3失败: 直接解析失败")
        
        # 策略4: 清理并重试
        cleaned = content.strip()
        # 移除可能的前后缀文本
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
        
        try:
            result = json.loads(cleaned)
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'pages' in result:
                return result['pages']
        except json.JSONDecodeError:
            logger.debug("策略4失败: 清理后解析失败")
        
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
        return f"""请根据以下主题，生成一个6-9页的小红书图文内容大纲。

主题: {topic}

要求：
1. 生成6-9页的内容结构
2. 第一页必须是封面页，包含吸引眼球的标题
3. 中间页面展开主题，提供实用价值
4. 最后一页总结并呼吁行动
5. 每页需要有标题和详细描述

请以JSON格式返回：
```json
[
  {{
    "page_number": 1,
    "title": "页面标题",
    "description": "页面详细描述"
  }}
]
```"""