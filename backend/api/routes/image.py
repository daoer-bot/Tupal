"""
图片生成路由
"""
from flask import Blueprint, request, Response
import logging
import json
import time
from datetime import datetime

from services.image_service import ImageService
from services.progress_service import ProgressService
from ..utils.response import success_response, error_response

logger = logging.getLogger(__name__)

image_bp = Blueprint('image', __name__)


@image_bp.route('/generate-images', methods=['POST'])
def generate_images():
    """
    生成图片
    
    请求体:
    {
        "task_id": "任务ID",
        "pages": [...],
        "topic": "主题（可选）",
        "reference_image": "参考图片URL（可选）",
        "generator_type": "生成器类型（可选，默认mock）",
        "image_model_config": {...},
        "image_generation_config": {...},
        "full_outline": "完整内容大纲（可选）"
    }
    """
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        pages = data.get('pages', [])
        topic = data.get('topic', '')
        reference_image = data.get('reference_image')
        generator_type = data.get('generator_type', 'mock')
        image_model_config = data.get('image_model_config', {})
        image_generation_config = data.get('image_generation_config', {})
        full_outline = data.get('full_outline', '')
        
        if not task_id or not pages:
            return error_response('任务ID和页面信息不能为空', 400)
        
        logger.info(f'Starting image generation for task: {task_id}, pages: {len(pages)}')
        
        image_service = ImageService(
            generator_type=generator_type,
            model_config=image_model_config
        )
        
        is_valid, error_msg = image_service.validate_pages(pages)
        if not is_valid:
            return error_response(error_msg, 400)
        
        image_service.generate_batch(
            task_id=task_id,
            pages=pages,
            topic=topic,
            reference_image=reference_image,
            image_generation_config=image_generation_config,
            full_outline=full_outline
        )
        
        return success_response({
            'task_id': task_id,
            'total_pages': len(pages)
        }, '图片生成任务已启动')
        
    except Exception as e:
        logger.error(f'Error starting image generation: {e}', exc_info=True)
        return error_response(str(e), 500)


@image_bp.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    """
    获取任务进度（SSE端点）
    """
    def generate_progress():
        progress_service = ProgressService()

        if not progress_service.task_exists(task_id):
            error_data = {
                'error': '任务已过期或不存在',
                'task_id': task_id,
                'message': '该任务可能已完成或已被清理，请刷新页面重新生成',
                'code': 'TASK_NOT_FOUND'
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            return
        
        logger.info(f"开始SSE进度推送: {task_id}")
        
        while True:
            try:
                progress = progress_service.get_progress(task_id)
                
                if not progress:
                    logger.error(f"无法获取任务进度: {task_id}")
                    break
                
                sse_data = {
                    'task_id': progress['task_id'],
                    'status': progress['status'],
                    'progress': progress['progress'],
                    'total_pages': progress['total_pages'],
                    'completed_pages': progress['completed_pages'],
                    'current_page': progress['current_page'],
                    'message': progress['message'],
                    'images': progress['images'],
                    'failed_pages': progress.get('failed_pages', []),
                    'timestamp': datetime.now().isoformat()
                }
                
                yield f"data: {json.dumps(sse_data)}\n\n"
                
                if progress_service.is_task_completed(task_id):
                    final_data = {
                        'done': True,
                        'status': progress['status'],
                        'task_id': task_id,
                        'images': progress['images'],  # 🔧 修复：包含完整的图片数组
                        'failed_pages': progress.get('failed_pages', [])
                    }
                    yield f"data: {json.dumps(final_data)}\n\n"
                    logger.info(f"SSE进度推送完成: {task_id}, 图片数量: {len(progress['images'])}")
                    break
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"SSE推送错误: {e}", exc_info=True)
                yield f"data: {json.dumps({'error': str(e), 'task_id': task_id})}\n\n"
                break
    
    return Response(
        generate_progress(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )