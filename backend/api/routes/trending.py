"""
热榜数据路由
"""
from flask import Blueprint, request
import logging
import asyncio

from services.trending_service import get_trending_service
from ..utils.response import success_response, error_response

logger = logging.getLogger(__name__)

trending_bp = Blueprint('trending', __name__)


@trending_bp.route('/trending/sources', methods=['GET'])
def get_trending_sources():
    """获取所有可用的热榜数据源"""
    try:
        trending_service = get_trending_service()
        sources = trending_service.get_all_sources()
        return success_response(sources)
        
    except Exception as e:
        logger.error(f'Error getting trending sources: {e}', exc_info=True)
        return error_response(str(e), 500)


@trending_bp.route('/trending/<source_id>', methods=['GET'])
def get_trending_by_source(source_id):
    """
    获取指定数据源的热榜数据
    
    Args:
        source_id: 数据源ID (baidu, zhihu, weibo, bilibili等)
    
    Query Parameters:
        force_refresh: 是否强制刷新 (true/false)
    """
    try:
        trending_service = get_trending_service()
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        result = asyncio.run(
            trending_service.get_trending_data(source_id, force_refresh)
        )
        
        if result.get('success'):
            return success_response(result)
        else:
            return error_response(result.get('error', '获取失败'), 500)
            
    except Exception as e:
        logger.error(f'Error getting trending data for {source_id}: {e}', exc_info=True)
        return error_response(str(e), 500, source_id=source_id)


@trending_bp.route('/trending', methods=['GET'])
def get_all_trending():
    """
    获取所有数据源的热榜数据
    
    Query Parameters:
        force_refresh: 是否强制刷新 (true/false)
    """
    try:
        trending_service = get_trending_service()
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        result = asyncio.run(
            trending_service.get_all_trending_data(force_refresh)
        )
        
        return success_response(result)
            
    except Exception as e:
        logger.error(f'Error getting all trending data: {e}', exc_info=True)
        return error_response(str(e), 500)