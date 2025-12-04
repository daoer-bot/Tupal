"""
历史记录路由
"""
from flask import Blueprint, request
import logging

from services.history_service import HistoryService
from ..utils.response import success_response, error_response

logger = logging.getLogger(__name__)

history_bp = Blueprint('history', __name__)


@history_bp.route('/history', methods=['GET'])
def get_history():
    """
    获取历史记录列表
    
    查询参数:
    - page: 页码（默认1）
    - page_size: 每页数量（默认20）
    - keyword: 搜索关键词（可选）
    """
    try:
        history_service = HistoryService()
        
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        keyword = request.args.get('keyword', '', type=str)
        
        if keyword:
            items = history_service.search_history(keyword)
            return success_response({
                'items': items,
                'pagination': {
                    'page': 1,
                    'page_size': len(items),
                    'total': len(items),
                    'total_pages': 1,
                    'has_more': False
                }
            })
        
        result = history_service.get_history_list(page=page, page_size=page_size)
        return success_response(result)
        
    except Exception as e:
        logger.error(f'Error getting history: {e}', exc_info=True)
        return error_response(str(e), 500)


@history_bp.route('/history/<history_id>', methods=['GET'])
def get_history_item(history_id):
    """获取特定历史记录详情"""
    try:
        history_service = HistoryService()
        item = history_service.get_history(history_id)
        
        if not item:
            return error_response('历史记录不存在', 404)
        
        return success_response(item)
        
    except Exception as e:
        logger.error(f'Error getting history item: {e}', exc_info=True)
        return error_response(str(e), 500)


@history_bp.route('/history/<history_id>', methods=['DELETE'])
def delete_history(history_id):
    """删除历史记录"""
    try:
        history_service = HistoryService()
        
        if history_service.delete_history(history_id):
            return success_response(message='删除成功')
        else:
            return error_response('删除失败或记录不存在', 404)
        
    except Exception as e:
        logger.error(f'Error deleting history: {e}', exc_info=True)
        return error_response(str(e), 500)


@history_bp.route('/history', methods=['POST'])
def save_history():
    """
    保存历史记录
    
    请求体:
    {
        "task_id": "任务ID",
        "topic": "主题",
        "pages": [...],
        "reference_image": "参考图片（可选）",
        "generator_type": "生成器类型（可选）",
        "status": "状态（可选）"
    }
    """
    try:
        history_service = HistoryService()
        data = request.get_json()
        
        task_id = data.get('task_id')
        topic = data.get('topic')
        pages = data.get('pages', [])
        reference_image = data.get('reference_image')
        generator_type = data.get('generator_type', 'mock')
        status = data.get('status', 'completed')
        
        if not task_id or not topic:
            return error_response('任务ID和主题不能为空', 400)
        
        history_id = history_service.save_generation(
            task_id=task_id,
            topic=topic,
            pages=pages,
            reference_image=reference_image,
            generator_type=generator_type,
            status=status
        )
        
        if history_id:
            return success_response({'history_id': history_id}, '保存成功')
        else:
            return error_response('保存失败', 500)
        
    except Exception as e:
        logger.error(f'Error saving history: {e}', exc_info=True)
        return error_response(str(e), 500)