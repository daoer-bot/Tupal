"""
小红书 API 辅助函数
包含签名生成、cookie处理、数据提取等工具函数
"""
import hashlib
import json
import os
import random
import re
import string
import time
from typing import Dict, List, Optional

import requests


def sign(url: str, data: Optional[Dict] = None, a1: Optional[str] = None) -> Dict[str, str]:
    """生成小红书 API 请求签名
    
    注意：这是一个简化的签名实现。实际的小红书签名算法更复杂，
    可能需要使用 JavaScript 引擎或其他方式来生成正确的签名。
    
    Args:
        url: 请求的 URI 路径
        data: 请求数据（POST 请求时使用）
        a1: cookie 中的 a1 值
    
    Returns:
        包含 x-s, x-t, x-s-common 的签名字典
    """
    timestamp = str(int(time.time() * 1000))
    nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    
    # 构建签名字符串
    sign_str = url
    if data:
        sign_str += json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    sign_str += timestamp + nonce
    if a1:
        sign_str += a1
    
    # 生成签名（简化版本）
    signature = hashlib.md5(sign_str.encode()).hexdigest()
    
    return {
        "x-s": signature,
        "x-t": timestamp,
        "x-s-common": nonce
    }


def cookie_jar_to_cookie_str(cookie_jar) -> str:
    """将 cookie jar 转换为 cookie 字符串
    
    Args:
        cookie_jar: requests 的 cookie jar 对象
    
    Returns:
        cookie 字符串，格式为 "key1=value1; key2=value2"
    """
    return '; '.join([f"{k}={v}" for k, v in requests.utils.dict_from_cookiejar(cookie_jar).items()])


def update_session_cookies_from_cookie(session: requests.Session, cookie: Optional[str]) -> None:
    """从 cookie 字符串更新 session 的 cookies
    
    Args:
        session: requests Session 对象
        cookie: cookie 字符串，格式为 "key1=value1; key2=value2"
    """
    if not cookie:
        return
    
    for item in cookie.split(';'):
        item = item.strip()
        if not item:
            continue
        
        if '=' not in item:
            continue
            
        name, value = item.split('=', 1)
        session.cookies.set(name.strip(), value.strip())


def get_imgs_url_from_note(note: Dict) -> List[str]:
    """从笔记数据中提取图片 URL 列表
    
    Args:
        note: 笔记数据字典
    
    Returns:
        图片 URL 列表
    """
    if note.get("type") != "normal":
        return []
    
    image_list = note.get("image_list", [])
    urls = []
    
    for img in image_list:
        # 优先使用 url_default，其次是 url
        url = img.get("url_default") or img.get("url") or img.get("info_list", [{}])[0].get("url", "")
        if url:
            urls.append(url)
    
    return urls


def get_video_url_from_note(note: Dict) -> str:
    """从笔记数据中提取视频 URL
    
    Args:
        note: 笔记数据字典
    
    Returns:
        视频 URL，如果不是视频笔记则返回空字符串
    """
    if note.get("type") != "video":
        return ""
    
    video = note.get("video", {})
    
    # 尝试多种可能的视频 URL 字段
    url = video.get("url") or video.get("media", {}).get("stream", {}).get("h264", [{}])[0].get("master_url", "")
    
    return url


def get_valid_path_name(name: str) -> str:
    """将字符串转换为有效的文件路径名
    
    Args:
        name: 原始名称
    
    Returns:
        处理后的有效路径名
    """
    if not name:
        return ""
    
    # 替换无效字符为下划线
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def get_search_id() -> str:
    """生成搜索 ID
    
    Returns:
        基于时间戳的搜索 ID
    """
    return str(int(time.time() * 1000))


def download_file(url: str, file_path: str, timeout: int = 30) -> bool:
    """从 URL 下载文件到本地
    
    Args:
        url: 文件 URL
        file_path: 本地保存路径
        timeout: 请求超时时间（秒）
    
    Returns:
        下载是否成功
    """
    if not url:
        return False
    
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception:
        return False


def parse_note_info(note: Dict) -> Dict:
    """解析笔记信息，提取关键字段
    
    Args:
        note: 原始笔记数据
    
    Returns:
        格式化后的笔记信息
    """
    interact_info = note.get("interact_info", {})
    user = note.get("user", {})
    
    return {
        "note_id": note.get("note_id", ""),
        "title": note.get("title", ""),
        "desc": note.get("desc", ""),
        "type": note.get("type", ""),
        "time": note.get("time", 0),
        "last_update_time": note.get("last_update_time", 0),
        "user": {
            "user_id": user.get("user_id", ""),
            "nickname": user.get("nickname", ""),
            "avatar": user.get("avatar", ""),
        },
        "interact_info": {
            "liked_count": interact_info.get("liked_count", "0"),
            "collected_count": interact_info.get("collected_count", "0"),
            "comment_count": interact_info.get("comment_count", "0"),
            "share_count": interact_info.get("share_count", "0"),
        },
        "image_list": get_imgs_url_from_note(note),
        "video_url": get_video_url_from_note(note),
        "tag_list": [tag.get("name", "") for tag in note.get("tag_list", [])],
    }


def extract_note_id_from_url(url: str) -> Optional[str]:
    """从小红书链接中提取笔记 ID
    
    支持的链接格式：
    - https://www.xiaohongshu.com/explore/xxxxx
    - https://www.xiaohongshu.com/discovery/item/xxxxx
    - https://xhslink.com/xxxxx (短链接需要先解析)
    
    Args:
        url: 小红书链接
    
    Returns:
        笔记 ID，如果无法提取则返回 None
    """
    if not url:
        return None
    
    # 匹配 explore 格式
    match = re.search(r'xiaohongshu\.com/explore/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)
    
    # 匹配 discovery/item 格式
    match = re.search(r'xiaohongshu\.com/discovery/item/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)
    
    # 匹配纯 ID 格式
    match = re.search(r'^[a-zA-Z0-9]{24}$', url)
    if match:
        return url
    
    return None


def extract_user_id_from_url(url: str) -> Optional[str]:
    """从小红书用户链接中提取用户 ID
    
    支持的链接格式：
    - https://www.xiaohongshu.com/user/profile/xxxxx
    
    Args:
        url: 小红书用户链接
    
    Returns:
        用户 ID，如果无法提取则返回 None
    """
    if not url:
        return None
    
    # 匹配 user/profile 格式
    match = re.search(r'xiaohongshu\.com/user/profile/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)
    
    # 匹配纯 ID 格式
    match = re.search(r'^[a-zA-Z0-9]{24}$', url)
    if match:
        return url
    
    return None