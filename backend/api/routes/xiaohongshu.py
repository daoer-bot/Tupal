"""
小红书 API 路由
基于 xhs_mcp_agent 架构优化
"""
from flask import Blueprint, request
import logging
import asyncio
from functools import wraps

from xhs import check_playwright_installed, login_manager, LoginStatus
from xhs.exception import NeedVerifyError, IPBlockError, SignError, DataFetchError
from ..utils.response import success_response, error_response

# 导入新的架构组件
from xhs.client_manager import client_manager
from xhs.async_api_client import ApiClient
from xhs.types import (
    CreateClientRequest,
    NoteRequest,
    SearchNotesRequest,
    SearchUsersRequest,
    UserNotesRequest,
    FeedRequest,
    CommentsRequest,
    BatchNotesRequest
)

logger = logging.getLogger(__name__)

xiaohongshu_bp = Blueprint('xiaohongshu', __name__)


# ==================== 异步工具函数 ====================

def async_route(f):
    """异步路由装饰器"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(f(*args, **kwargs))
            return result
        finally:
            loop.close()
    return wrapper


# ==================== 客户端管理 ====================

@xiaohongshu_bp.route('/xiaohongshu/client', methods=['POST'])
@async_route
async def create_client():
    """创建小红书客户端
    
    请求体:
    {
        "cookie": "小红书 cookie 字符串",
        "user_agent": "可选，自定义 User-Agent",
        "timeout": 10,           // 可选，请求超时时间
        "proxies": {},           // 可选，代理配置
        "max_retries": 3,        // 可选，最大重试次数
        "retry_delay": 1.0,      // 可选，重试延迟（秒）
        "rate_limit": 1.0        // 可选，请求间隔（秒）
    }
    """
    try:
        data = request.get_json() or {}
        
        if not data.get('cookie'):
            return error_response('缺少 cookie 参数', 400)
        
        req = CreateClientRequest(**data)
        
        async with ApiClient(req) as client:
            stats = await client.get_stats()
            
            return success_response({
                'client_id': client.client_id,
                'stats': stats,
                'message': '客户端创建成功'
            })
    
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f'创建小红书客户端失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/client/<client_id>', methods=['DELETE'])
@async_route
async def delete_client(client_id: str):
    """删除小红书客户端"""
    try:
        deleted = await client_manager.delete_client(client_id)
        return success_response({'deleted': deleted})
    except Exception as e:
        logger.error(f'删除小红书客户端失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/clients', methods=['GET'])
@async_route
async def list_clients():
    """列出所有客户端"""
    try:
        clients = await client_manager.list_clients()
        return success_response({
            'clients': clients,
            'count': len(clients)
        })
    except Exception as e:
        logger.error(f'列出小红书客户端失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/client/<client_id>/stats', methods=['GET'])
@async_route
async def get_client_stats(client_id: str):
    """获取客户端统计信息"""
    try:
        stats = await client_manager.get_client_stats(client_id)
        return success_response(stats)
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f'获取客户端统计失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 笔记相关 ====================

@xiaohongshu_bp.route('/xiaohongshu/note', methods=['POST'])
@async_route
async def get_note():
    """获取笔记详情
    
    请求体:
    {
        "client_id": "xhs_client_1",  // 可选，如果提供则复用现有客户端
        "cookie": "xxx",              // 可选，如果提供则创建新客户端
        "note_id": "笔记ID或链接",
        "xsec_token": "可选，安全令牌",
        "xsec_source": "pc_feed"      // 可选
    }
    """
    try:
        data = request.get_json() or {}
        note_id = data.get('note_id')
        
        if not note_id:
            return error_response('缺少 note_id 参数', 400)
        
        if data.get('cookie'):
            req = CreateClientRequest(
                cookie=data['cookie'],
                user_agent=data.get('user_agent'),
                timeout=data.get('timeout', 10),
                proxies=data.get('proxies'),
                max_retries=data.get('max_retries', 3),
                rate_limit=data.get('rate_limit', 1.0)
            )
            
            async with ApiClient(req) as client:
                note_req = NoteRequest(
                    note_id=note_id,
                    xsec_token=data.get('xsec_token'),
                    xsec_source=data.get('xsec_source')
                )
                result = await client.get_note(note_req)
                return success_response(result.to_dict())
        
        elif data.get('client_id'):
            client_id = data['client_id']
            
            req = CreateClientRequest(cookie="dummy")
            async with ApiClient(req) as client:
                client._client_id = client_id
                
                note_req = NoteRequest(
                    note_id=note_id,
                    xsec_token=data.get('xsec_token'),
                    xsec_source=data.get('xsec_source')
                )
                result = await client.get_note(note_req)
                return success_response(result.to_dict())
        
        else:
            return error_response('必须提供 cookie 或 client_id 参数', 400)
    
    except ValueError as e:
        return error_response(str(e), 400)
    except NeedVerifyError as e:
        return error_response(f'需要验证码: {e}', 403)
    except IPBlockError as e:
        return error_response(f'IP被封: {e}', 403)
    except SignError as e:
        return error_response(f'签名错误: {e}', 403)
    except DataFetchError as e:
        return error_response(f'数据获取失败: {e}', 500)
    except Exception as e:
        logger.error(f'获取笔记失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/note/batch', methods=['POST'])
@async_route
async def batch_get_notes():
    """批量获取笔记详情
    
    请求体:
    {
        "cookie": "xxx",
        "notes": [
            {"note_id": "笔记ID或链接", "xsec_token": "可选", "xsec_source": "pc_feed"}
        ],
        "batch_delay": 0.5  // 可选，批量操作间隔
    }
    """
    try:
        data = request.get_json() or {}
        
        if not data.get('cookie'):
            return error_response('缺少 cookie 参数', 400)
        if not data.get('notes'):
            return error_response('缺少 notes 参数', 400)
        
        req = CreateClientRequest(
            cookie=data['cookie'],
            user_agent=data.get('user_agent'),
            timeout=data.get('timeout', 10),
            proxies=data.get('proxies'),
            max_retries=data.get('max_retries', 3),
            rate_limit=data.get('rate_limit', 1.0)
        )
        
        async with ApiClient(req) as client:
            batch_req = BatchNotesRequest(
                notes=[NoteRequest(**note) for note in data['notes']],
                batch_delay=data.get('batch_delay', 0.5)
            )
            
            result = await client.batch_get_notes(batch_req)
            return success_response(result.to_dict())
    
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f'批量获取笔记失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 搜索相关 ====================

@xiaohongshu_bp.route('/xiaohongshu/search/notes', methods=['POST'])
@async_route
async def search_notes():
    """搜索笔记"""
    try:
        data = request.get_json() or {}
        
        if not data.get('cookie'):
            return error_response('缺少 cookie 参数', 400)
        if not data.get('keyword'):
            return error_response('缺少 keyword 参数', 400)
        
        req = CreateClientRequest(
            cookie=data['cookie'],
            user_agent=data.get('user_agent'),
            timeout=data.get('timeout', 10),
            proxies=data.get('proxies')
        )
        
        async with ApiClient(req) as client:
            search_req = SearchNotesRequest(
                keyword=data['keyword'],
                page=data.get('page', 1),
                page_size=data.get('page_size', 20),
                sort=data.get('sort', 'general'),
                note_type=data.get('note_type', 0)
            )
            
            result = await client.search_notes(search_req)
            return success_response(result.to_dict())
    
    except Exception as e:
        logger.error(f'搜索笔记失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/search/users', methods=['POST'])
@async_route
async def search_users():
    """搜索用户"""
    try:
        data = request.get_json() or {}
        
        if not data.get('cookie'):
            return error_response('缺少 cookie 参数', 400)
        if not data.get('keyword'):
            return error_response('缺少 keyword 参数', 400)
        
        req = CreateClientRequest(
            cookie=data['cookie'],
            user_agent=data.get('user_agent'),
            timeout=data.get('timeout', 10),
            proxies=data.get('proxies')
        )
        
        async with ApiClient(req) as client:
            search_req = SearchUsersRequest(
                keyword=data['keyword'],
                page=data.get('page', 1),
                page_size=data.get('page_size', 20)
            )
            
            result = await client.search_users(search_req)
            return success_response(result.to_dict())
    
    except Exception as e:
        logger.error(f'搜索用户失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 用户相关 ====================

@xiaohongshu_bp.route('/xiaohongshu/user/info', methods=['POST'])
@async_route
async def get_user_info():
    """获取用户信息"""
    try:
        data = request.get_json() or {}
        
        if not data.get('cookie'):
            return error_response('缺少 cookie 参数', 400)
        if not data.get('user_id'):
            return error_response('缺少 user_id 参数', 400)
        
        req = CreateClientRequest(
            cookie=data['cookie'],
            user_agent=data.get('user_agent'),
            timeout=data.get('timeout', 10),
            proxies=data.get('proxies')
        )
        
        async with ApiClient(req) as client:
            result = await client.get_user_info(data['user_id'])
            return success_response(result.to_dict())
    
    except Exception as e:
        logger.error(f'获取用户信息失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/user/notes', methods=['POST'])
@async_route
async def get_user_notes():
    """获取用户笔记列表"""
    try:
        data = request.get_json() or {}
        
        if not data.get('cookie'):
            return error_response('缺少 cookie 参数', 400)
        if not data.get('user_id'):
            return error_response('缺少 user_id 参数', 400)
        
        req = CreateClientRequest(
            cookie=data['cookie'],
            user_agent=data.get('user_agent'),
            timeout=data.get('timeout', 10),
            proxies=data.get('proxies')
        )
        
        async with ApiClient(req) as client:
            user_notes_req = UserNotesRequest(
                user_id=data['user_id'],
                cursor=data.get('cursor', '')
            )
            
            result = await client.get_user_notes(user_notes_req)
            return success_response(result.to_dict())
    
    except Exception as e:
        logger.error(f'获取用户笔记失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 推荐流相关 ====================

@xiaohongshu_bp.route('/xiaohongshu/feed/categories', methods=['POST'])
@async_route
async def get_feed_categories():
    """获取推荐流分类"""
    try:
        data = request.get_json() or {}
        
        if not data.get('cookie'):
            return error_response('缺少 cookie 参数', 400)
        
        req = CreateClientRequest(
            cookie=data['cookie'],
            user_agent=data.get('user_agent'),
            timeout=data.get('timeout', 10),
            proxies=data.get('proxies')
        )
        
        async with ApiClient(req) as client:
            result = await client.get_feed_categories()
            return success_response({'categories': result})
    
    except Exception as e:
        logger.error(f'获取推荐流分类失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/feed', methods=['POST'])
@async_route
async def get_feed():
    """获取推荐流内容"""
    try:
        data = request.get_json() or {}
        
        if not data.get('cookie'):
            return error_response('缺少 cookie 参数', 400)
        
        req = CreateClientRequest(
            cookie=data['cookie'],
            user_agent=data.get('user_agent'),
            timeout=data.get('timeout', 10),
            proxies=data.get('proxies')
        )
        
        async with ApiClient(req) as client:
            feed_req = FeedRequest(
                feed_type=data.get('feed_type', 'homefeed_recommend')
            )
            
            result = await client.get_feed(feed_req)
            return success_response(result.to_dict())
    
    except Exception as e:
        logger.error(f'获取推荐流失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 评论相关 ====================

@xiaohongshu_bp.route('/xiaohongshu/note/comments', methods=['POST'])
@async_route
async def get_note_comments():
    """获取笔记评论"""
    try:
        data = request.get_json() or {}
        
        if not data.get('cookie'):
            return error_response('缺少 cookie 参数', 400)
        if not data.get('note_id'):
            return error_response('缺少 note_id 参数', 400)
        
        req = CreateClientRequest(
            cookie=data['cookie'],
            user_agent=data.get('user_agent'),
            timeout=data.get('timeout', 10),
            proxies=data.get('proxies')
        )
        
        async with ApiClient(req) as client:
            comments_req = CommentsRequest(
                note_id=data['note_id'],
                cursor=data.get('cursor', ''),
                xsec_token=data.get('xsec_token')
            )
            
            result = await client.get_note_comments(comments_req)
            return success_response(result.to_dict())
    
    except Exception as e:
        logger.error(f'获取笔记评论失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 扫码登录相关 ====================

_login_sessions = {}


@xiaohongshu_bp.route('/xiaohongshu/login/check', methods=['GET'])
def check_login_available():
    """检查扫码登录功能是否可用"""
    try:
        available = check_playwright_installed()
        if available:
            return success_response({
                'available': True,
                'message': 'Playwright 已安装，扫码登录功能可用'
            })
        else:
            return success_response({
                'available': False,
                'message': 'Playwright 未安装。请运行: pip install playwright && playwright install chromium'
            })
    except Exception as e:
        logger.error(f'检查扫码登录功能失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/login/start', methods=['POST'])
def start_qr_login():
    """启动扫码登录"""
    try:
        if not check_playwright_installed():
            return error_response(
                'Playwright 未安装。请运行: pip install playwright && playwright install chromium',
                400
            )
        
        data = request.get_json() or {}
        headless = data.get('headless', False)
        timeout = data.get('timeout', 120)
        proxy = data.get('proxy')
        
        import uuid
        session_id = f"login_{uuid.uuid4().hex[:8]}"
        
        session = login_manager.create_session(
            session_id=session_id,
            headless=headless,
            timeout=timeout,
            proxy=proxy
        )
        
        _login_sessions[session_id] = {
            'status': 'starting',
            'cookie': None,
            'error': None,
            'qr_code': None
        }
        
        def status_callback(status: LoginStatus, data=None):
            if session_id in _login_sessions:
                _login_sessions[session_id]['status'] = status.value
                if data and isinstance(data, dict) and 'qr_code' in data:
                    _login_sessions[session_id]['qr_code'] = data['qr_code']
        
        session.set_status_callback(status_callback)
        
        import threading
        
        def run_login():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(session.login_with_qr_code())
                
                if session_id in _login_sessions:
                    _login_sessions[session_id]['status'] = result.status.value
                    _login_sessions[session_id]['cookie'] = result.cookie
                    _login_sessions[session_id]['error'] = result.error
            except Exception as e:
                if session_id in _login_sessions:
                    _login_sessions[session_id]['status'] = 'failed'
                    _login_sessions[session_id]['error'] = str(e)
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_login, daemon=True)
        thread.start()
        
        return success_response({
            'session_id': session_id,
            'message': '登录会话已启动，请在弹出的浏览器窗口中扫码登录'
        })
    
    except Exception as e:
        logger.error(f'启动扫码登录失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/login/status/<session_id>', methods=['GET'])
def get_login_status(session_id: str):
    """获取登录状态"""
    try:
        if session_id not in _login_sessions:
            return error_response('登录会话不存在或已过期', 404)
        
        session_data = _login_sessions[session_id]
        
        return success_response({
            'status': session_data['status'],
            'cookie': session_data['cookie'],
            'qr_code': session_data['qr_code'],
            'error': session_data['error']
        })
    
    except Exception as e:
        logger.error(f'获取登录状态失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/login/cancel/<session_id>', methods=['POST'])
def cancel_login(session_id: str):
    """取消登录"""
    try:
        login_manager.cancel_session(session_id)
        
        if session_id in _login_sessions:
            _login_sessions[session_id]['status'] = 'cancelled'
        
        return success_response({'cancelled': True})
    
    except Exception as e:
        logger.error(f'取消登录失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/login/cleanup/<session_id>', methods=['DELETE'])
def cleanup_login_session(session_id: str):
    """清理登录会话"""
    try:
        login_manager.cancel_session(session_id)
        
        if session_id in _login_sessions:
            del _login_sessions[session_id]
        
        return success_response({'cleaned': True})
    
    except Exception as e:
        logger.error(f'清理登录会话失败: {e}', exc_info=True)
        return error_response(str(e), 500)