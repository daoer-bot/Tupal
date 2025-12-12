"""
小红书解析路由
"""
from flask import Blueprint, request
import logging

from sources.xiaohongshu_source import XiaohongshuSource
from ..utils.response import success_response, error_response

logger = logging.getLogger(__name__)

xiaohongshu_bp = Blueprint('xiaohongshu', __name__)


@xiaohongshu_bp.route('/xiaohongshu/parse', methods=['POST'])
def parse_xiaohongshu():
    """解析小红书内容"""
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return error_response('缺少url参数', 400)

        import asyncio
        xhs = XiaohongshuSource()
        result = asyncio.run(xhs.parse_content(url))

        if result:
            return success_response(result)
        else:
            return error_response('解析失败', 500)

    except Exception as e:
        logger.error(f'解析小红书内容失败: {e}', exc_info=True)
        return error_response(str(e), 500)
