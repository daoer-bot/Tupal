"""
小红书 API 客户端模块
提供完整的小红书 API 访问能力
"""

from .client import XhsClient
from .exception import (
    XhsException,
    DataFetchError,
    IPBlockError,
    NeedVerifyError,
    SignError,
    ErrorEnum
)
from .help import (
    sign,
    cookie_jar_to_cookie_str,
    update_session_cookies_from_cookie,
    get_imgs_url_from_note,
    get_video_url_from_note,
    get_valid_path_name,
    get_search_id,
    parse_note_info,
    extract_note_id_from_url,
    extract_user_id_from_url
)
from .browser import (
    XhsBrowserLogin,
    XhsBrowserLoginManager,
    LoginStatus,
    LoginResult,
    login_manager,
    get_cookie_by_qr_login,
    check_playwright_installed
)

__all__ = [
    'XhsClient',
    'XhsException',
    'DataFetchError',
    'IPBlockError',
    'NeedVerifyError',
    'SignError',
    'ErrorEnum',
    'sign',
    'cookie_jar_to_cookie_str',
    'update_session_cookies_from_cookie',
    'get_imgs_url_from_note',
    'get_video_url_from_note',
    'get_valid_path_name',
    'get_search_id',
    'parse_note_info',
    'extract_note_id_from_url',
    'extract_user_id_from_url',
    # 浏览器登录
    'XhsBrowserLogin',
    'XhsBrowserLoginManager',
    'LoginStatus',
    'LoginResult',
    'login_manager',
    'get_cookie_by_qr_login',
    'check_playwright_installed',
]