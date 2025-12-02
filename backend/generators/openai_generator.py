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
        self.image_model = model or "dall-e-3"  # 图片模型，使用传入的model参数
        
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
            
            # 限制提示词长度（DALL-E 3 有长度限制，通常是 4000 字符）
            max_prompt_length = 4000
            if len(prompt) > max_prompt_length:
                logger.warning(f"提示词过长 ({len(prompt)} 字符)，截断到 {max_prompt_length} 字符")
                prompt = prompt[:max_prompt_length]
            
            logger.info(f"尝试使用 {self.image_model} 生成图片")
            logger.info(f"尺寸: {size}, 提示词长度: {len(prompt)} 字符")
            logger.debug(f"提示词内容: {prompt[:200]}...")
            
            # 检查是否是非标准模型（如 nano-banana）需要使用直接 HTTP 请求
            if self.image_model != 'dall-e-3' and self.image_model != 'dall-e-2':
                logger.info(f"检测到非标准模型 {self.image_model}，使用直接 HTTP 请求")
                return self._generate_image_http(prompt, width, height, size)
            
            # 标准 DALL-E API 调用
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
            error_type = type(e).__name__
            logger.error(f"OpenAI 图片生成失败 [{error_type}]: {error_msg}", exc_info=True)
            
            # 详细的错误分类
            if "does not support" in error_msg.lower():
                friendly_msg = (
                    "❌ 当前 API 端点不支持图片生成功能\n"
                    "💡 建议：\n"
                    "  1. 如果使用第三方 API，请在前端选择 'image_api' 生成器\n"
                    "  2. 或使用 'mock' 生成器进行测试\n"
                    f"原始错误: {error_msg}"
                )
            elif "content_policy_violation" in error_msg.lower() or "safety" in error_msg.lower():
                friendly_msg = (
                    "❌ 提示词违反了内容政策\n"
                    "💡 建议：修改提示词，避免敏感或不当内容\n"
                    f"原始错误: {error_msg}"
                )
            elif "invalid" in error_msg.lower() and ("key" in error_msg.lower() or "auth" in error_msg.lower()):
                friendly_msg = (
                    "❌ API 密钥无效或认证失败\n"
                    "💡 建议：检查 API 密钥配置是否正确\n"
                    f"原始错误: {error_msg}"
                )
            elif "rate" in error_msg.lower() or "quota" in error_msg.lower():
                friendly_msg = (
                    "❌ API 请求频率限制或配额不足\n"
                    "💡 建议：稍后重试或升级 API 套餐\n"
                    f"原始错误: {error_msg}"
                )
            elif len(prompt) > 1000:
                friendly_msg = (
                    f"❌ 图片生成失败，可能是提示词过长 ({len(prompt)} 字符)\n"
                    "💡 建议：简化提示词描述\n"
                    f"原始错误: {error_msg}"
                )
            else:
                friendly_msg = f"❌ 图片生成失败: {error_msg}"
            
            return self._create_error_result(ContentType.IMAGE, friendly_msg)
    
    def _generate_image_http(
        self,
        prompt: str,
        width: int,
        height: int,
        size: str
    ) -> GenerationResult:
        """
        使用直接 HTTP 请求生成图片（支持非标准模型如 nano-banana）
        
        Args:
            prompt: 图片描述
            width: 宽度
            height: 高度
            size: DALL-E 格式的尺寸字符串
            
        Returns:
            GenerationResult对象
        """
        try:
            # 计算 aspect_ratio（nano-banana 需要的格式）
            aspect_ratio = self._calculate_aspect_ratio(width, height)
            
            # 构建请求数据
            request_data = {
                "model": self.image_model,
                "prompt": prompt,
                "n": 1,
                "size": size
            }
            
            # 如果有 aspect_ratio，添加到请求中
            if aspect_ratio:
                request_data["aspect_ratio"] = aspect_ratio
                logger.info(f"添加 aspect_ratio 参数: {aspect_ratio}")
            
            logger.info(f"发送 HTTP 请求到: {self.base_url}/images/generations")
            logger.debug(f"请求数据: {request_data}")
            
            # 发送 HTTP POST 请求
            response = requests.post(
                f"{self.base_url}/images/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=request_data,
                timeout=60
            )
            
            # 检查响应
            response.raise_for_status()
            result = response.json()
            
            # 提取图片 URL
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0].get('url')
                if image_url:
                    logger.info(f"图片生成成功: {image_url[:100]}...")
                    return self._create_success_result(
                        content_type=ContentType.IMAGE,
                        url=image_url,
                        format="png",
                        width=width,
                        height=height,
                        size=size
                    )
            
            raise ValueError("响应中没有图片 URL")
            
        except requests.exceptions.HTTPError as e:
            # 解析错误响应
            error_detail = None
            try:
                error_detail = e.response.json()
            except:
                error_detail = {"message": e.response.text}
            
            # 提取错误信息
            error_message = ""
            if isinstance(error_detail, dict):
                if 'error' in error_detail:
                    if isinstance(error_detail['error'], dict):
                        error_message = error_detail['error'].get('message', '')
                    else:
                        error_message = str(error_detail['error'])
                else:
                    error_message = error_detail.get('message', '')
            
            # 识别尺寸不支持错误
            if 'invalid_value' in str(error_detail).lower() or 'supported values' in error_message.lower():
                friendly_msg = (
                    f"❌ 图片尺寸不支持 (HTTP {e.response.status_code}):\n"
                    f"当前尝试使用的尺寸 '{size}' 不被API提供商支持。\n"
                    f"💡 原因：不同的API提供商支持的尺寸规格不同\n"
                    f"  - 标准 DALL-E 3: 1024x1024, 1024x1792, 1792x1024\n"
                    f"  - 部分第三方API: 1024x1024, 1024x1536, 1536x1024, auto\n"
                    f"💡 建议：\n"
                    f"  1. 系统已自动调整为兼容尺寸，此错误应已修复\n"
                    f"  2. 如果问题仍存在，请尝试使用 'image_api' 生成器类型\n"
                    f"  3. 或在前端配置中调整图片尺寸设置\n"
                    f"原始错误: {error_message}"
                )
            else:
                friendly_msg = f"HTTP 错误 {e.response.status_code}: {error_message or e.response.text}"
            
            logger.error(friendly_msg)
            return self._create_error_result(ContentType.IMAGE, friendly_msg)
        except Exception as e:
            error_msg = f"生成图片失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self._create_error_result(ContentType.IMAGE, error_msg)
    
    def _calculate_aspect_ratio(self, width: int, height: int) -> Optional[str]:
        """
        计算标准的宽高比
        
        Args:
            width: 宽度
            height: 高度
            
        Returns:
            宽高比字符串（如 '3:4'）或 None
        """
        # 支持的宽高比列表
        supported_ratios = [
            (1, 1), (2, 3), (3, 2), (3, 4), (4, 3),
            (4, 5), (5, 4), (9, 16), (16, 9), (21, 9)
        ]
        
        ratio = width / height
        
        # 找到最接近的标准宽高比
        best_match = None
        min_diff = float('inf')
        
        for w, h in supported_ratios:
            standard_ratio = w / h
            diff = abs(ratio - standard_ratio)
            if diff < min_diff:
                min_diff = diff
                best_match = (w, h)
        
        if best_match:
            aspect_ratio = f"{best_match[0]}:{best_match[1]}"
            logger.info(f"计算宽高比: {width}x{height} -> {aspect_ratio}")
            return aspect_ratio
        
        return None
    
    
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
        
        注意：不同的API提供商支持的尺寸不同：
        - 标准 DALL-E 3: 1024x1024, 1024x1792, 1792x1024
        - 部分第三方API: 1024x1024, 1024x1536, 1536x1024
        
        Args:
            width: 宽度
            height: 高度
            
        Returns:
            DALL-E 尺寸字符串
        """
        ratio = width / height
        
        # 横向图片（宽度大于高度）
        if ratio > 1.2:
            # 优先使用 1536x1024（兼容性更好）
            return "1536x1024"
        # 竖向图片（高度大于宽度）
        elif ratio < 0.8:
            # 优先使用 1024x1536（兼容性更好）
            return "1024x1536"
        # 正方形或接近正方形
        else:
            return "1024x1024"
    
    def _build_outline_prompt(self, topic: str) -> str:
        """构建大纲生成提示词"""
        return f"""你是一个小红书内容创作专家。用户会给你一个要求以及说明，你需要生成一个适合小红书的图文内容大纲。

用户的要求以及说明：
{topic}

要求：
1. 第一页必须是吸引人的封面/标题页，包含标题和副标题
2. 内容控制在 6-12 页（包括封面）（如果用户特别要求页数，以用户的要求为准，页数可以适当放宽到2-18页的范围）
3. 每页内容简洁有力，适合配图展示
4. 使用小红书风格的语言（亲切、有趣、实用）
5. 可以适当使用 emoji 增加趣味性
6. 内容要有实用价值，能解决用户问题或提供有用信息
7. 最后一页可以是总结或行动呼吁

输出格式要求：
- 每页第一行是页面类型标记：[封面]、[内容]、[总结]
- 后面是该页的具体内容描述
- 内容要具体、详细，方便后续生成图片
- 避免在内容中使用 | 竖线符号（会与 markdown 表格冲突）

请严格以JSON格式返回：
```json
{{
  "xiaohongshu_content": "这里是完整的小红书文案内容，带emoji和排版📱✨\\n\\n第一段内容...\\n\\n第二段内容...",
  "image_prompts": [
    {{
      "page_number": 1,
      "title": "[封面] 标题文字",
      "description": "[封面]\\n标题：XXX\\n副标题：XXX\\n背景：XXX场景描述\\n\\n配图建议：XXX"
    }},
    {{
      "page_number": 2,
      "title": "[内容] 第一步标题",
      "description": "[内容]\\n第一步：XXX\\n\\n必备工具：\\n• 工具1\\n• 工具2\\n\\n小贴士💡：\\nXXX提示\\n\\n配图建议：XXX"
    }},
    {{
      "page_number": 3,
      "title": "[内容] 第二步标题",
      "description": "[内容]\\n第二步：XXX\\n\\n关键点⚠️：\\n• 要点1\\n• 要点2\\n\\n配图建议：XXX"
    }},
    {{
      "page_number": 4,
      "title": "[总结] 完成",
      "description": "[总结]\\n完成！XXX✨\\n\\n记住三个关键：\\n✅ 关键点1\\n✅ 关键点2\\n✅ 关键点3\\n\\n配图建议：XXX"
    }}
  ]
}}
```

注意：
- 内容要详细、具体、专业、有价值
- 适合制作成小红书图文
- 避免使用竖线符号 |
- 每页的 description 要包含完整的内容描述和配图建议"""