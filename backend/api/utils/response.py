"""
统一响应格式工具
"""
from flask import jsonify
from typing import Any, Optional


def success_response(data: Any = None, message: str = None, status_code: int = 200):
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
        status_code: HTTP状态码
        
    Returns:
        Flask Response对象
    """
    response = {'success': True}
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    return jsonify(response), status_code


def error_response(error: str, status_code: int = 500, **kwargs):
    """
    错误响应
    
    Args:
        error: 错误信息
        status_code: HTTP状态码
        **kwargs: 额外的错误信息字段
        
    Returns:
        Flask Response对象
    """
    response = {
        'success': False,
        'error': error
    }
    
    # 添加额外字段
    response.update(kwargs)
    
    return jsonify(response), status_code