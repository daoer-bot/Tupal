"""
OpenAI 文本模型调用
纯粹的 API 调用，不包含业务逻辑
"""
import logging
import json
import re
from typing import Dict, Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)


class OpenAITextModel:
    """OpenAI 文本模型调用类"""
    
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4"):
        """
        初始化 OpenAI 文本模型
        
        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            model: 模型名称
        """
        if OpenAI is None:
            raise ImportError("openai 未安装，请运行: pip install openai")
        
        # 处理 base_url
        if base_url:
            base_url = base_url.rstrip('/')
            if not base_url.endswith('/v1'):
                base_url = f"{base_url}/v1"
        
        self.base_url = base_url or "https://api.openai.com/v1"
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=self.base_url)
        
        logger.info(f"OpenAI 文本模型初始化: base_url={self.base_url}, model={self.model}")
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        调用 OpenAI API 生成文本
        
        Args:
            prompt: 提示词
            temperature: 温度参数
            
        Returns:
            生成的文本内容
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的小红书内容策划专家。请务必返回有效的JSON格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        content = response.choices[0].message.content
        logger.debug(f"OpenAI 原始响应: {content[:200]}...")
        
        return content
    
    @staticmethod
    def extract_json(content: str) -> Dict[str, Any]:
        """
        从响应中提取并解析 JSON
        
        Args:
            content: 响应内容
            
        Returns:
            解析后的字典
        """
        # 策略1: 提取 markdown 代码块中的 JSON
        json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 策略2: 提取第一个 JSON 对象
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # 策略3: 提取第一个 JSON 数组
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # 策略4: 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # 策略5: 清理并重试
        cleaned = content.strip()
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise json.JSONDecodeError("无法从响应中提取有效的 JSON", content, 0)