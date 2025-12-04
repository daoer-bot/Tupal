"""
大纲生成路由
"""
from flask import Blueprint, request
import logging

from services.outline_service import OutlineService
from ..utils.response import success_response, error_response

logger = logging.getLogger(__name__)

outline_bp = Blueprint('outline', __name__)


@outline_bp.route('/generate-outline', methods=['POST'])
def generate_outline():
    """
    生成内容大纲
    
    请求体:
    {
        "topic": "主题描述",
        "reference_image": "参考图片URL（可选）",
        "generator_type": "生成器类型（可选，默认openai）",
        "text_model_config": {
            "url": "API URL",
            "apiKey": "API Key",
            "model": "模型名称"
        }
    }
    """
    try:
        data = request.get_json()
        topic = data.get('topic')
        reference_image = data.get('reference_image')
        generator_type = data.get('generator_type', 'openai')
        text_model_config = data.get('text_model_config', {})
        
        if not topic:
            return error_response('主题不能为空', 400)
        
        logger.info(f'Generating outline for topic: {topic}')
        logger.info(f'Text generator type: {generator_type}')
        
        outline_service = OutlineService(
            generator_type=generator_type,
            model_config=text_model_config
        )
        result = outline_service.generate(topic, reference_image)
        
        if result['success']:
            return success_response(result)
        else:
            return error_response(result.get('error', '生成失败'), 500)
        
    except Exception as e:
        logger.error(f'Error generating outline: {e}', exc_info=True)
        return error_response(str(e), 500)