"""
Gemini AI 生成器
使用 Google Gemini API 生成大纲和图片
"""
import logging
from typing import Optional, Dict, Any, List
import json

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from .base_generator import BaseGenerator, ContentType, GenerationResult

logger = logging.getLogger(__name__)


class GeminiGenerator(BaseGenerator):
    """Gemini AI 生成器实现"""
    
    # 声明支持的内容类型
    SUPPORTED_TYPES = {ContentType.TEXT}
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        
        if genai is None:
            raise ImportError("google-generativeai 未安装，请运行: pip install google-generativeai")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
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
        
        return self._create_unsupported_result(content_type)
    
    def _generate_text(
        self,
        prompt: str,
        reference_image: Optional[str] = None,
        **kwargs
    ) -> GenerationResult:
        """
        生成文本内容（大纲）
        
        Args:
            prompt: 主题描述
            reference_image: 参考图片
            **kwargs: 其他参数
            
        Returns:
            GenerationResult对象
        """
        try:
            # 构建提示词
            full_prompt = self._build_outline_prompt(prompt)
            
            # 调用 Gemini API
            response = self.model.generate_content(full_prompt)
            
            # 解析响应
            pages = self._parse_outline_response(response.text)
            
            return self._create_success_result(
                content_type=ContentType.TEXT,
                url="",  # 文本类型没有URL
                format="json",
                pages=pages,
                topic=prompt
            )
            
        except Exception as e:
            logger.error(f"Gemini 文本生成失败: {e}")
            return self._create_error_result(ContentType.TEXT, str(e))
    
    
    def _build_outline_prompt(self, topic: str) -> str:
        """
        构建大纲生成提示词
        
        Args:
            topic: 主题
            
        Returns:
            完整提示词
        """
        prompt = f"""你是一个专业的小红书内容策划专家。请根据以下主题，生成一个6-9页的小红书图文内容大纲。

主题: {topic}

要求：
1. 生成6-9页的内容结构
2. 第一页必须是封面页，包含吸引眼球的标题
3. 中间页面展开主题，提供实用价值
4. 最后一页总结并呼吁行动
5. 每页需要有标题和详细描述
6. 描述要具体，适合生成配图

请以JSON格式返回，格式如下：
```json
[
  {{
    "page_number": 1,
    "title": "页面标题",
    "description": "页面详细描述，包含视觉元素说明"
  }}
]
```

只返回JSON数组，不要其他内容。"""
        
        return prompt
    
    def _parse_outline_response(self, response_text: str) -> List[Dict]:
        """
        解析 Gemini 响应为结构化大纲
        
        Args:
            response_text: Gemini 返回的文本
            
        Returns:
            页面列表
        """
        try:
            # 尝试从响应中提取 JSON
            # 移除可能的 markdown 代码块标记
            text = response_text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            # 解析 JSON
            pages = json.loads(text)
            
            # 验证和标准化数据
            validated_pages = []
            for i, page in enumerate(pages, 1):
                validated_pages.append({
                    'page_number': page.get('page_number', i),
                    'title': page.get('title', f'页面 {i}'),
                    'description': page.get('description', '')
                })
            
            return validated_pages
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            # 如果解析失败，返回默认结构
            return self._generate_fallback_outline()
        except Exception as e:
            logger.error(f"大纲解析失败: {e}")
            return self._generate_fallback_outline()
    
    def _generate_fallback_outline(self) -> List[Dict]:
        """
        生成默认大纲结构（当解析失败时使用）
        
        Returns:
            默认页面列表
        """
        return [
            {
                'page_number': 1,
                'title': '封面页',
                'description': '吸引眼球的标题和主题图'
            },
            {
                'page_number': 2,
                'title': '问题引入',
                'description': '提出用户关心的问题'
            },
            {
                'page_number': 3,
                'title': '核心内容1',
                'description': '第一个重点内容'
            },
            {
                'page_number': 4,
                'title': '核心内容2',
                'description': '第二个重点内容'
            },
            {
                'page_number': 5,
                'title': '核心内容3',
                'description': '第三个重点内容'
            },
            {
                'page_number': 6,
                'title': '总结',
                'description': '总结要点和行动建议'
            }
        ]