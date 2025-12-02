"""
API路由定义
提供所有RESTful API端点
"""
from flask import Blueprint, request, jsonify, Response, current_app
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# 创建蓝图
api_bp = Blueprint('api', __name__)


@api_bp.route('/generate-outline', methods=['POST'])
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
        generator_type = data.get('generator_type', 'openai')  # 新增：支持动态选择生成器
        text_model_config = data.get('text_model_config', {})
        
        if not topic:
            return jsonify({
                'success': False,
                'error': '主题不能为空'
            }), 400
        
        logger.info(f'Generating outline for topic: {topic}')
        logger.info(f'Text generator type: {generator_type}')
        logger.info(f'Text model config: {text_model_config}')
        
        from services.outline_service import OutlineService
        outline_service = OutlineService(
            generator_type=generator_type,  # 修改：使用动态传入的生成器类型
            model_config=text_model_config
        )
        result = outline_service.generate(topic, reference_image)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '生成失败')
            }), 500
        
    except Exception as e:
        logger.error(f'Error generating outline: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/generate-images', methods=['POST'])
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
        "image_model_config": {
            "url": "API URL",
            "apiKey": "API Key",
            "model": "模型名称"
        },
        "image_generation_config": {
            "quality": "1k|2k|4k",
            "aspectRatio": "4:3|3:4|16:9|..."
        },
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
        full_outline = data.get('full_outline', '')  # 新增：完整内容大纲
        
        if not task_id or not pages:
            return jsonify({
                'success': False,
                'error': '任务ID和页面信息不能为空'
            }), 400
        
        logger.info(f'Starting image generation for task: {task_id}, pages: {len(pages)}')
        
        logger.info(f'Image model config: {image_model_config}')
        
        # 导入图片生成服务
        from services.image_service import ImageService
        
        # 创建服务实例
        image_service = ImageService(
            generator_type=generator_type,
            model_config=image_model_config
        )
        
        # 验证页面数据
        is_valid, error_msg = image_service.validate_pages(pages)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # 启动批量生成任务（异步）
        image_service.generate_batch(
            task_id=task_id,
            pages=pages,
            topic=topic,
            reference_image=reference_image,
            image_generation_config=image_generation_config,
            full_outline=full_outline  # 新增：传递完整内容大纲
        )
        
        return jsonify({
            'success': True,
            'message': '图片生成任务已启动',
            'task_id': task_id,
            'total_pages': len(pages)
        })
        
    except Exception as e:
        logger.error(f'Error starting image generation: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    """
    获取任务进度（SSE端点）
    
    返回实时进度流
    """
    import time
    
    def generate_progress():
        """生成进度事件流"""
        from services.progress_service import ProgressService
        
        progress_service = ProgressService()
        
        # 检查任务是否存在
        if not progress_service.task_exists(task_id):
            error_data = {
                'error': '任务不存在',
                'task_id': task_id
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            return
        
        logger.info(f"开始SSE进度推送: {task_id}")
        
        # 持续推送进度，直到任务完成
        while True:
            try:
                # 获取当前进度
                progress = progress_service.get_progress(task_id)
                
                if not progress:
                    logger.error(f"无法获取任务进度: {task_id}")
                    break
                
                # 构建SSE数据
                sse_data = {
                    'task_id': progress['task_id'],
                    'status': progress['status'],
                    'progress': progress['progress'],
                    'total_pages': progress['total_pages'],
                    'completed_pages': progress['completed_pages'],
                    'current_page': progress['current_page'],
                    'message': progress['message'],
                    'images': progress['images'],
                    'failed_pages': progress.get('failed_pages', []),  # 新增：失败页面信息
                    'timestamp': datetime.now().isoformat()
                }
                
                # 发送进度数据
                yield f"data: {json.dumps(sse_data)}\n\n"
                
                # 如果任务已完成或失败，发送完成信号并结束
                if progress_service.is_task_completed(task_id):
                    final_data = {
                        'done': True,
                        'status': progress['status'],
                        'task_id': task_id
                    }
                    yield f"data: {json.dumps(final_data)}\n\n"
                    logger.info(f"SSE进度推送完成: {task_id}")
                    break
                
                # 等待一段时间再检查（避免过于频繁）
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"SSE推送错误: {e}", exc_info=True)
                error_data = {
                    'error': str(e),
                    'task_id': task_id
                }
                yield f"data: {json.dumps(error_data)}\n\n"
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


@api_bp.route('/history', methods=['GET'])
def get_history():
    """
    获取历史记录列表
    
    查询参数:
    - page: 页码（默认1）
    - page_size: 每页数量（默认20）
    - keyword: 搜索关键词（可选）
    """
    try:
        from services.history_service import HistoryService
        history_service = HistoryService()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        keyword = request.args.get('keyword', '', type=str)
        
        # 如果有搜索关键词，执行搜索
        if keyword:
            items = history_service.search_history(keyword)
            return jsonify({
                'success': True,
                'data': {
                    'items': items,
                    'pagination': {
                        'page': 1,
                        'page_size': len(items),
                        'total': len(items),
                        'total_pages': 1,
                        'has_more': False
                    }
                }
            })
        
        # 获取分页列表
        result = history_service.get_history_list(page=page, page_size=page_size)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f'Error getting history: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/history/<history_id>', methods=['GET'])
def get_history_item(history_id):
    """
    获取特定历史记录详情
    """
    try:
        from services.history_service import HistoryService
        history_service = HistoryService()
        
        item = history_service.get_history(history_id)
        
        if not item:
            return jsonify({
                'success': False,
                'error': '历史记录不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': item
        })
        
    except Exception as e:
        logger.error(f'Error getting history item: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/history/<history_id>', methods=['DELETE'])
def delete_history(history_id):
    """
    删除历史记录
    """
    try:
        from services.history_service import HistoryService
        history_service = HistoryService()
        
        if history_service.delete_history(history_id):
            return jsonify({
                'success': True,
                'message': '删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '删除失败或记录不存在'
            }), 404
        
    except Exception as e:
        logger.error(f'Error deleting history: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/history', methods=['POST'])
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
        from services.history_service import HistoryService
        history_service = HistoryService()
        
        data = request.get_json()
        task_id = data.get('task_id')
        topic = data.get('topic')
        pages = data.get('pages', [])
        reference_image = data.get('reference_image')
        generator_type = data.get('generator_type', 'mock')
        status = data.get('status', 'completed')
        
        if not task_id or not topic:
            return jsonify({
                'success': False,
                'error': '任务ID和主题不能为空'
            }), 400
        
        history_id = history_service.save_generation(
            task_id=task_id,
            topic=topic,
            pages=pages,
            reference_image=reference_image,
            generator_type=generator_type,
            status=status
        )
        
        if history_id:
            return jsonify({
                'success': True,
                'message': '保存成功',
                'history_id': history_id
            })
        else:
            return jsonify({
                'success': False,
                'error': '保存失败'
            }), 500
        
    except Exception as e:
        logger.error(f'Error saving history: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@api_bp.route('/upload-reference', methods=['POST'])
def upload_reference():
    """
    上传参考图片
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传文件'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空'
            }), 400
        
        # 使用文件工具保存文件
        from utils.file_utils import FileUtils
        file_utils = FileUtils()
        
        success, file_path, error_msg = file_utils.save_upload_file(
            file=file,
            subdir='references'
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # 构建文件URL
        file_url = file_utils.get_file_url(file_path)
        
        return jsonify({
            'success': True,
            'message': '上传成功',
            'file_url': file_url,
            'file_path': file_path
        })
        
    except Exception as e:
        logger.error(f'Error uploading file: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/trending/sources', methods=['GET'])
def get_trending_sources():
    """
    获取所有热榜数据源列表
    
    Returns:
        JSON响应，包含所有可用的数据源信息
    """
    try:
        from services.trending_service import TrendingService
        trending_service = TrendingService()
        
        sources = trending_service.get_sources_list()
        
        return jsonify({
            'success': True,
            'data': sources
        })
        
    except Exception as e:
        logger.error(f'Error getting trending sources: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/trending/<source_id>', methods=['GET'])
def get_trending_data(source_id):
    """
    获取指定平台的热榜数据
    
    Args:
        source_id: 数据源ID（如 weibo, zhihu, douyin, bilibili, baidu）
    
    Query Parameters:
        force_refresh: 是否强制刷新（可选，默认false）
    
    Returns:
        JSON响应，包含热榜数据
    """
    try:
        import asyncio
        from services.trending_service import TrendingService
        
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        trending_service = TrendingService()
        
        # 在同步环境中运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            data = loop.run_until_complete(
                trending_service.get_trending_data(source_id, force_refresh)
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except ValueError as e:
        logger.error(f'Invalid source_id: {source_id}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
        
    except Exception as e:
        logger.error(f'Error getting trending data for {source_id}: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/trending', methods=['GET'])
def get_all_trending():
    """
    获取所有平台的热榜数据
    
    Query Parameters:
        force_refresh: 是否强制刷新（可选，默认false）
    
    Returns:
        JSON响应，包含所有平台的热榜数据
    """
    try:
        import asyncio
        from services.trending_service import TrendingService
        
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        trending_service = TrendingService()
        
        # 在同步环境中运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            data = loop.run_until_complete(
                trending_service.get_all_trending_data(force_refresh)
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        logger.error(f'Error getting all trending data: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500