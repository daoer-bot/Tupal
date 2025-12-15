"""
小红书 API 路由
提供完整的小红书 API 访问能力
"""
from flask import Blueprint, request
import logging
import asyncio
import uuid

from services.xhs_service import xhs_service
from xhs import XhsException, check_playwright_installed, login_manager, LoginStatus
from ..utils.response import success_response, error_response

logger = logging.getLogger(__name__)

xiaohongshu_bp = Blueprint('xiaohongshu', __name__)


# ==================== 客户端管理 ====================

@xiaohongshu_bp.route('/xiaohongshu/client', methods=['POST'])
def create_client():
    """创建小红书客户端
    
    请求体:
    {
        "cookie": "小红书 cookie 字符串",
        "user_agent": "可选，自定义 User-Agent",
        "timeout": 10,  // 可选，请求超时时间
        "proxies": {}   // 可选，代理配置
    }
    
    返回:
    {
        "success": true,
        "data": {
            "client_id": "xhs_client_1"
        }
    }
    """
    try:
        data = request.get_json() or {}
        cookie = data.get('cookie')
        
        if not cookie:
            return error_response('缺少 cookie 参数', 400)
        
        client_id = xhs_service.create_client(
            cookie=cookie,
            user_agent=data.get('user_agent'),
            timeout=data.get('timeout', 10),
            proxies=data.get('proxies')
        )
        
        return success_response({'client_id': client_id})
    
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f'创建小红书客户端失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/client/<client_id>', methods=['DELETE'])
def delete_client(client_id: str):
    """删除小红书客户端
    
    返回:
    {
        "success": true,
        "data": {"deleted": true}
    }
    """
    try:
        deleted = xhs_service.delete_client(client_id)
        return success_response({'deleted': deleted})
    except Exception as e:
        logger.error(f'删除小红书客户端失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/clients', methods=['GET'])
def list_clients():
    """列出所有客户端
    
    返回:
    {
        "success": true,
        "data": {
            "clients": ["xhs_client_1", "xhs_client_2"]
        }
    }
    """
    try:
        clients = xhs_service.list_clients()
        return success_response({'clients': clients})
    except Exception as e:
        logger.error(f'列出小红书客户端失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 笔记相关 ====================

@xiaohongshu_bp.route('/xiaohongshu/note', methods=['POST'])
def get_note():
    """获取笔记详情
    
    请求体:
    {
        "client_id": "xhs_client_1",
        "note_id": "笔记ID或链接",
        "xsec_token": "可选，安全令牌",
        "xsec_source": "pc_feed"  // 可选
    }
    
    返回:
    {
        "success": true,
        "data": {
            "note_id": "...",
            "title": "...",
            "desc": "...",
            ...
        }
    }
    """
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        note_id = data.get('note_id')
        
        if not client_id:
            return error_response('缺少 client_id 参数', 400)
        if not note_id:
            return error_response('缺少 note_id 参数', 400)
        
        note = xhs_service.get_note(
            client_id=client_id,
            note_id=note_id,
            xsec_token=data.get('xsec_token', ''),
            xsec_source=data.get('xsec_source', 'pc_feed')
        )
        
        return success_response(note)
    
    except ValueError as e:
        return error_response(str(e), 400)
    except XhsException as e:
        return error_response(str(e), 500)
    except Exception as e:
        logger.error(f'获取笔记失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/note/html', methods=['POST'])
def get_note_from_html():
    """从 HTML 获取笔记详情
    
    请求体:
    {
        "client_id": "xhs_client_1",
        "note_id": "笔记ID或链接",
        "xsec_token": "可选，安全令牌",
        "xsec_source": "pc_feed"  // 可选
    }
    """
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        note_id = data.get('note_id')
        
        if not client_id:
            return error_response('缺少 client_id 参数', 400)
        if not note_id:
            return error_response('缺少 note_id 参数', 400)
        
        note = xhs_service.get_note_from_html(
            client_id=client_id,
            note_id=note_id,
            xsec_token=data.get('xsec_token', ''),
            xsec_source=data.get('xsec_source', 'pc_feed')
        )
        
        return success_response(note)
    
    except ValueError as e:
        return error_response(str(e), 400)
    except XhsException as e:
        return error_response(str(e), 500)
    except Exception as e:
        logger.error(f'从 HTML 获取笔记失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 搜索相关 ====================

@xiaohongshu_bp.route('/xiaohongshu/search/notes', methods=['POST'])
def search_notes():
    """搜索笔记
    
    请求体:
    {
        "client_id": "xhs_client_1",
        "keyword": "搜索关键词",
        "page": 1,           // 可选，页码
        "page_size": 20,     // 可选，每页数量
        "sort": "general",   // 可选，排序方式: general/popularity_descending/time_descending
        "note_type": 0       // 可选，笔记类型: 0=全部, 1=视频, 2=图文
    }
    """
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        keyword = data.get('keyword')
        
        if not client_id:
            return error_response('缺少 client_id 参数', 400)
        if not keyword:
            return error_response('缺少 keyword 参数', 400)
        
        result = xhs_service.search_notes(
            client_id=client_id,
            keyword=keyword,
            page=data.get('page', 1),
            page_size=data.get('page_size', 20),
            sort=data.get('sort', 'general'),
            note_type=data.get('note_type', 0)
        )
        
        return success_response(result)
    
    except ValueError as e:
        return error_response(str(e), 400)
    except XhsException as e:
        return error_response(str(e), 500)
    except Exception as e:
        logger.error(f'搜索笔记失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/search/users', methods=['POST'])
def search_users():
    """搜索用户
    
    请求体:
    {
        "client_id": "xhs_client_1",
        "keyword": "搜索关键词",
        "page": 1,       // 可选
        "page_size": 20  // 可选
    }
    """
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        keyword = data.get('keyword')
        
        if not client_id:
            return error_response('缺少 client_id 参数', 400)
        if not keyword:
            return error_response('缺少 keyword 参数', 400)
        
        result = xhs_service.search_users(
            client_id=client_id,
            keyword=keyword,
            page=data.get('page', 1),
            page_size=data.get('page_size', 20)
        )
        
        return success_response(result)
    
    except ValueError as e:
        return error_response(str(e), 400)
    except XhsException as e:
        return error_response(str(e), 500)
    except Exception as e:
        logger.error(f'搜索用户失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/search/suggestion', methods=['POST'])
def get_search_suggestion():
    """获取搜索建议
    
    请求体:
    {
        "client_id": "xhs_client_1",
        "keyword": "搜索关键词"
    }
    """
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        keyword = data.get('keyword')
        
        if not client_id:
            return error_response('缺少 client_id 参数', 400)
        if not keyword:
            return error_response('缺少 keyword 参数', 400)
        
        suggestions = xhs_service.get_search_suggestion(client_id, keyword)
        
        return success_response({'suggestions': suggestions})
    
    except ValueError as e:
        return error_response(str(e), 400)
    except XhsException as e:
        return error_response(str(e), 500)
    except Exception as e:
        logger.error(f'获取搜索建议失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 用户相关 ====================

@xiaohongshu_bp.route('/xiaohongshu/user/self', methods=['POST'])
def get_self_info():
    """获取当前登录用户信息
    
    请求体:
    {
        "client_id": "xhs_client_1"
    }
    """
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        
        if not client_id:
            return error_response('缺少 client_id 参数', 400)
        
        user_info = xhs_service.get_self_info(client_id)
        
        return success_response(user_info)
    
    except ValueError as e:
        return error_response(str(e), 400)
    except XhsException as e:
        return error_response(str(e), 500)
    except Exception as e:
        logger.error(f'获取当前用户信息失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/user/info', methods=['POST'])
def get_user_info():
    """获取用户信息
    
    请求体:
    {
        "client_id": "xhs_client_1",
        "user_id": "用户ID或链接"
    }
    """
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        user_id = data.get('user_id')
        
        if not client_id:
            return error_response('缺少 client_id 参数', 400)
        if not user_id:
            return error_response('缺少 user_id 参数', 400)
        
        user_info = xhs_service.get_user_info(client_id, user_id)
        
        return success_response(user_info)
    
    except ValueError as e:
        return error_response(str(e), 400)
    except XhsException as e:
        return error_response(str(e), 500)
    except Exception as e:
        logger.error(f'获取用户信息失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/user/notes', methods=['POST'])
def get_user_notes():
    """获取用户笔记列表
    
    请求体:
    {
        "client_id": "xhs_client_1",
        "user_id": "用户ID或链接",
        "cursor": ""  // 可选，分页游标
    }
    """
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        user_id = data.get('user_id')
        
        if not client_id:
            return error_response('缺少 client_id 参数', 400)
        if not user_id:
            return error_response('缺少 user_id 参数', 400)
        
        result = xhs_service.get_user_notes(
            client_id=client_id,
            user_id=user_id,
            cursor=data.get('cursor', '')
        )
        
        return success_response(result)
    
    except ValueError as e:
        return error_response(str(e), 400)
    except XhsException as e:
        return error_response(str(e), 500)
    except Exception as e:
        logger.error(f'获取用户笔记失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 推荐流相关 ====================

@xiaohongshu_bp.route('/xiaohongshu/feed/categories', methods=['POST'])
def get_feed_categories():
    """获取推荐流分类
    
    请求体:
    {
        "client_id": "xhs_client_1"
    }
    """
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        
        if not client_id:
            return error_response('缺少 client_id 参数', 400)
        
        categories = xhs_service.get_feed_categories(client_id)
        
        return success_response({'categories': categories})
    
    except ValueError as e:
        return error_response(str(e), 400)
    except XhsException as e:
        return error_response(str(e), 500)
    except Exception as e:
        logger.error(f'获取推荐流分类失败: {e}', exc_info=True)
        return error_response(str(e), 500)


@xiaohongshu_bp.route('/xiaohongshu/feed', methods=['POST'])
def get_feed():
    """获取推荐流内容
    
    请求体:
    {
        "client_id": "xhs_client_1",
        "feed_type": "homefeed_recommend"  // 可选，推荐流类型
    }
    
    推荐流类型:
    - homefeed_recommend: 推荐
    - homefeed.fashion_v3: 穿搭
    - homefeed.food_v3: 美食
    - homefeed.cosmetics_v3: 彩妆
    - homefeed.movie_and_tv_v3: 影视
    - homefeed.career_v3: 职场
    - homefeed.love_v3: 情感
    - homefeed.household_product_v3: 家居
    - homefeed.gaming_v3: 游戏
    - homefeed.travel_v3: 旅行
    - homefeed.fitness_v3: 健身
    """
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        
        if not client_id:
            return error_response('缺少 client_id 参数', 400)
        
        result = xhs_service.get_feed(
            client_id=client_id,
            feed_type=data.get('feed_type', 'homefeed_recommend')
        )
        
        return success_response(result)
    
    except ValueError as e:
        return error_response(str(e), 400)
    except XhsException as e:
        return error_response(str(e), 500)
    except Exception as e:
        logger.error(f'获取推荐流失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 评论相关 ====================

@xiaohongshu_bp.route('/xiaohongshu/note/comments', methods=['POST'])
def get_note_comments():
    """获取笔记评论
    
    请求体:
    {
        "client_id": "xhs_client_1",
        "note_id": "笔记ID",
        "cursor": "",      // 可选，分页游标
        "xsec_token": ""   // 可选，安全令牌
    }
    """
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        note_id = data.get('note_id')
        
        if not client_id:
            return error_response('缺少 client_id 参数', 400)
        if not note_id:
            return error_response('缺少 note_id 参数', 400)
        
        result = xhs_service.get_note_comments(
            client_id=client_id,
            note_id=note_id,
            cursor=data.get('cursor', ''),
            xsec_token=data.get('xsec_token', '')
        )
        
        return success_response(result)
    
    except ValueError as e:
        return error_response(str(e), 400)
    except XhsException as e:
        return error_response(str(e), 500)
    except Exception as e:
        logger.error(f'获取笔记评论失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 旧版兼容接口 ====================

@xiaohongshu_bp.route('/xiaohongshu/parse', methods=['POST'])
def parse_xiaohongshu():
    """解析小红书内容（旧版兼容接口）
    
    请求体:
    {
        "url": "小红书链接"
    }
    
    注意：此接口使用第三方 API，可能不稳定
    """
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return error_response('缺少url参数', 400)

        import requests as req
        api_url = "https://api.bugpk.com/api/xhsjx"
        
        response = req.get(
            api_url,
            params={'url': url},
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=10
        )
        response.raise_for_status()
        result = response.json()

        if result.get('code') == 200:
            return success_response(result.get('data'))
        else:
            return error_response(result.get('msg', '解析失败'), 500)

    except Exception as e:
        logger.error(f'解析小红书内容失败: {e}', exc_info=True)
        return error_response(str(e), 500)


# ==================== 扫码登录相关 ====================

# 存储登录会话状态
_login_sessions = {}


@xiaohongshu_bp.route('/xiaohongshu/login/check', methods=['GET'])
def check_login_available():
    """检查扫码登录功能是否可用
    
    返回:
    {
        "success": true,
        "data": {
            "available": true,
            "message": "Playwright 已安装，扫码登录功能可用"
        }
    }
    """
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
    """启动扫码登录
    
    请求体:
    {
        "headless": false,  // 可选，是否无头模式（建议 false 以便用户扫码）
        "timeout": 120,     // 可选，超时时间（秒）
        "proxy": ""         // 可选，代理地址
    }
    
    返回:
    {
        "success": true,
        "data": {
            "session_id": "login_session_xxx",
            "message": "登录会话已启动，请在弹出的浏览器窗口中扫码登录"
        }
    }
    """
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
        
        # 生成会话 ID
        session_id = f"login_{uuid.uuid4().hex[:8]}"
        
        # 创建登录会话
        session = login_manager.create_session(
            session_id=session_id,
            headless=headless,
            timeout=timeout,
            proxy=proxy
        )
        
        # 存储会话状态
        _login_sessions[session_id] = {
            'status': 'starting',
            'cookie': None,
            'error': None,
            'qr_code': None
        }
        
        # 设置状态回调
        def status_callback(status: LoginStatus, data=None):
            if session_id in _login_sessions:
                _login_sessions[session_id]['status'] = status.value
                if data and isinstance(data, dict) and 'qr_code' in data:
                    _login_sessions[session_id]['qr_code'] = data['qr_code']
        
        session.set_status_callback(status_callback)
        
        # 在后台线程中启动登录
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
    """获取登录状态
    
    返回:
    {
        "success": true,
        "data": {
            "status": "waiting_scan",  // waiting_scan/scanned/success/failed/timeout/cancelled
            "cookie": null,            // 登录成功时返回 cookie
            "qr_code": "data:image/png;base64,...",  // 二维码图片（如果有）
            "error": null              // 错误信息（如果有）
        }
    }
    """
    try:
        if session_id not in _login_sessions:
            return error_response('登录会话不存在或已过期', 404)
        
        session_data = _login_sessions[session_id]
        
        # 如果登录完成（成功或失败），清理会话
        if session_data['status'] in ['success', 'failed', 'timeout', 'cancelled']:
            # 保留数据供前端获取，但标记为可清理
            pass
        
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
    """取消登录
    
    返回:
    {
        "success": true,
        "data": {
            "cancelled": true
        }
    }
    """
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
    """清理登录会话
    
    返回:
    {
        "success": true,
        "data": {
            "cleaned": true
        }
    }
    """
    try:
        login_manager.cancel_session(session_id)
        
        if session_id in _login_sessions:
            del _login_sessions[session_id]
        
        return success_response({'cleaned': True})
    
    except Exception as e:
        logger.error(f'清理登录会话失败: {e}', exc_info=True)
        return error_response(str(e), 500)
