"""
大纲生成服务
处理内容大纲生成的业务逻辑
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from generators.factory import get_outline_generator

logger = logging.getLogger(__name__)


class OutlineService:
    """大纲生成服务类"""
    
    def __init__(self, generator_type: str = 'openai', model_config: Dict[str, Any] = None):
        """
        初始化服务
        
        Args:
            generator_type: 生成器类型
            model_config: 模型配置 (url, apiKey, model)
        """
        self.generator_type = generator_type
        self.model_config = model_config or {}
        self.generator = None
    
    def generate(
        self,
        topic: str,
        reference_image: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成内容大纲
        
        Args:
            topic: 主题描述
            reference_image: 参考图片URL
            
        Returns:
            包含大纲的字典
        """
        try:
            # 验证输入
            if not topic or not topic.strip():
                return {
                    'success': False,
                    'error': '主题不能为空'
                }
            
            # 获取生成器（传递模型配置）
            self.generator = self._create_generator_with_config()
            
            if not self.generator:
                return {
                    'success': False,
                    'error': f'无法创建生成器: {self.generator_type}'
                }
            
            # 生成大纲
            logger.info(f"开始生成大纲，主题: {topic}")
            result = self.generator.generate_outline(
                topic=topic,
                reference_image=reference_image
            )
            
            if result['success']:
                # 添加任务ID和元数据
                task_id = self._generate_task_id()
                result['task_id'] = task_id
                result['topic'] = topic
                result['created_at'] = datetime.now().isoformat()
                
                logger.info(f"大纲生成成功，任务ID: {task_id}")
            else:
                logger.error(f"大纲生成失败: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"大纲生成异常: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'生成失败: {str(e)}'
            }
    
    def validate_outline(self, outline: Dict[str, Any]) -> bool:
        """
        验证大纲格式是否正确
        
        Args:
            outline: 大纲数据
            
        Returns:
            是否有效
        """
        if not outline or not isinstance(outline, dict):
            return False
        
        if 'pages' not in outline:
            return False
        
        pages = outline['pages']
        if not isinstance(pages, list) or len(pages) == 0:
            return False
        
        # 检查每一页的格式
        for page in pages:
            if not isinstance(page, dict):
                return False
            
            required_fields = ['page_number', 'title', 'description']
            if not all(field in page for field in required_fields):
                return False
        
        return True
    
    def _generate_task_id(self) -> str:
        """
        生成任务ID
        
        Returns:
            任务ID
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f'task_{timestamp}'
    
    def get_supported_generators(self) -> list:
        """
        获取支持的生成器列表
        
        Returns:
            生成器类型列表
        """
        from generators.factory import GeneratorFactory
        available = GeneratorFactory.get_available_generators()
        return available.get('outline_generators', [])
    
    def _create_generator_with_config(self):
        """
        根据配置创建生成器
        
        Returns:
            生成器实例
        """
        try:
            # 检查是否有自定义配置（只要有配置对象就尝试使用）
            if self.model_config:
                logger.info(f"使用自定义配置创建大纲生成器: {self.generator_type}")
                
                # 获取配置，如果为空则回退到环境变量
                from flask import current_app
                
                custom_url = self.model_config.get('url', '').strip()
                custom_key = self.model_config.get('apiKey', '').strip()
                custom_model = self.model_config.get('model', '').strip()
                
                # 确定最终使用的配置
                api_key = custom_key or current_app.config.get('OPENAI_API_KEY')
                base_url = custom_url or current_app.config.get('OPENAI_BASE_URL')
                model = custom_model or current_app.config.get('OPENAI_MODEL', 'gpt-4')
                
                logger.info(f"最终配置 - URL: {base_url}, Model: {model}, HasKey: {bool(api_key)}")
                
                # 使用 TextGenerator 处理文本生成
                from generators.generators.text_generator import TextGenerator
                return TextGenerator(
                    provider='openai',
                    api_key=api_key,
                    base_url=base_url,
                    model=model
                )
            
            # 如果没有配置对象，使用默认配置（从环境变量）
            logger.info(f"使用默认配置创建大纲生成器: {self.generator_type}")
            return get_outline_generator(self.generator_type)
            
        except Exception as e:
            logger.error(f"创建大纲生成器失败: {e}", exc_info=True)
            return None