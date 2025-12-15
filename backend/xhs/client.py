"""
小红书 API 客户端
提供完整的小红书 API 访问能力
"""
import json
import re
import time
from enum import Enum
from typing import Dict, List, Optional, NamedTuple

import requests

from .exception import (
    DataFetchError,
    ErrorEnum,
    IPBlockError,
    NeedVerifyError,
    SignError
)
from .help import (
    cookie_jar_to_cookie_str,
    get_imgs_url_from_note,
    get_search_id,
    get_video_url_from_note,
    sign,
    update_session_cookies_from_cookie
)


class FeedType(Enum):
    """推荐流类型"""
    # 推荐
    RECOMMEND = "homefeed_recommend"
    # 穿搭
    FASHION = "homefeed.fashion_v3"
    # 美食
    FOOD = "homefeed.food_v3"
    # 彩妆
    COSMETICS = "homefeed.cosmetics_v3"
    # 影视
    MOVIE = "homefeed.movie_and_tv_v3"
    # 职场
    CAREER = "homefeed.career_v3"
    # 情感
    EMOTION = "homefeed.love_v3"
    # 家居
    HOUSE = "homefeed.household_product_v3"
    # 游戏
    GAME = "homefeed.gaming_v3"
    # 旅行
    TRAVEL = "homefeed.travel_v3"
    # 健身
    FITNESS = "homefeed.fitness_v3"


class NoteType(Enum):
    """笔记类型"""
    NORMAL = "normal"
    VIDEO = "video"


class SearchSortType(Enum):
    """搜索排序类型"""
    # 综合
    GENERAL = "general"
    # 最热
    MOST_POPULAR = "popularity_descending"
    # 最新
    LATEST = "time_descending"


class SearchNoteType(Enum):
    """搜索笔记类型"""
    # 全部
    ALL = 0
    # 仅视频
    VIDEO = 1
    # 仅图文
    IMAGE = 2


class Note(NamedTuple):
    """笔记数据结构"""
    note_id: str
    title: str
    desc: str
    type: str
    user: dict
    img_urls: list
    video_url: str
    tag_list: list
    at_user_list: list
    collected_count: str
    comment_count: str
    liked_count: str
    share_count: str
    time: int
    last_update_time: int


class XhsClient:
    """小红书 API 客户端"""
    
    def __init__(
        self,
        cookie: str = None,
        user_agent: str = None,
        timeout: int = 10,
        proxies: Dict = None,
        external_sign=None
    ):
        """初始化客户端
        
        Args:
            cookie: 小红书登录后的 cookie 字符串
            user_agent: 自定义 User-Agent
            timeout: 请求超时时间（秒）
            proxies: 代理配置
            external_sign: 外部签名函数（可选）
        """
        self.proxies = proxies
        self.__session: requests.Session = requests.session()
        self.timeout = timeout
        self.external_sign = external_sign
        
        # API 端点
        self._host = "https://edith.xiaohongshu.com"
        self._creator_host = "https://creator.xiaohongshu.com"
        self._customer_host = "https://customer.xiaohongshu.com"
        self.home = "https://www.xiaohongshu.com"
        
        # 设置 User-Agent
        self.user_agent = user_agent or (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 设置默认请求头
        self.__session.headers = {
            "user-agent": self.user_agent,
            "Content-Type": "application/json",
        }
        
        # 设置 cookie
        self.cookie = cookie
    
    @property
    def cookie(self) -> str:
        """获取当前 cookie 字符串"""
        return cookie_jar_to_cookie_str(self.__session.cookies)
    
    @cookie.setter
    def cookie(self, cookie: str):
        """设置 cookie"""
        update_session_cookies_from_cookie(self.__session, cookie)
    
    @property
    def cookie_dict(self) -> Dict:
        """获取 cookie 字典"""
        return requests.utils.dict_from_cookiejar(self.__session.cookies)
    
    @property
    def session(self) -> requests.Session:
        """获取 session 对象"""
        return self.__session
    
    def _pre_headers(self, url: str, data=None, quick_sign: bool = False):
        """预处理请求头，添加签名"""
        if quick_sign:
            signs = sign(url, data, a1=self.cookie_dict.get("a1"))
            self.__session.headers.update({"x-s": signs["x-s"]})
            self.__session.headers.update({"x-t": signs["x-t"]})
            self.__session.headers.update({"x-s-common": signs["x-s-common"]})
        elif self.external_sign:
            self.__session.headers.update(
                self.external_sign(
                    url,
                    data,
                    a1=self.cookie_dict.get("a1"),
                    web_session=self.cookie_dict.get("web_session", ""),
                )
            )
        else:
            # 使用内置签名
            signs = sign(url, data, a1=self.cookie_dict.get("a1"))
            self.__session.headers.update({"x-s": signs["x-s"]})
            self.__session.headers.update({"x-t": signs["x-t"]})
            self.__session.headers.update({"x-s-common": signs["x-s-common"]})
    
    def request(self, method: str, url: str, **kwargs):
        """发送请求"""
        response = self.__session.request(
            method, url, timeout=self.timeout, proxies=self.proxies, **kwargs
        )
        
        if not len(response.text):
            return response
        
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            return response
        
        # 处理验证码
        if response.status_code in (471, 461):
            verify_type = response.headers.get('Verifytype', '')
            verify_uuid = response.headers.get('Verifyuuid', '')
            raise NeedVerifyError(
                f"出现验证码，请求失败，Verifytype: {verify_type}，Verifyuuid: {verify_uuid}",
                response=response,
                verify_type=verify_type,
                verify_uuid=verify_uuid
            )
        
        # 处理成功响应
        if data.get("success"):
            return data.get("data", data.get("success"))
        
        # 处理错误响应
        if data.get("code") == ErrorEnum.IP_BLOCK.value.code:
            raise IPBlockError(ErrorEnum.IP_BLOCK.value.msg, response=response)
        elif data.get("code") == ErrorEnum.SIGN_FAULT.value.code:
            raise SignError(ErrorEnum.SIGN_FAULT.value.msg, response=response)
        else:
            raise DataFetchError(data, response=response)
    
    def get(self, uri: str, params=None, is_creator: bool = False, is_customer: bool = False, **kwargs):
        """发送 GET 请求"""
        final_uri = uri
        if isinstance(params, dict):
            final_uri = f"{uri}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        
        self._pre_headers(final_uri, quick_sign=is_creator or is_customer)
        
        endpoint = self._host
        if is_customer:
            endpoint = self._customer_host
        elif is_creator:
            endpoint = self._creator_host
        
        return self.request(method="GET", url=f"{endpoint}{final_uri}", **kwargs)
    
    def post(self, uri: str, data: Optional[Dict], is_creator: bool = False, is_customer: bool = False, **kwargs):
        """发送 POST 请求"""
        json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False) if data else None
        
        self._pre_headers(uri, data, quick_sign=is_creator or is_customer)
        
        endpoint = self._host
        if is_customer:
            endpoint = self._customer_host
        elif is_creator:
            endpoint = self._creator_host
        
        if data:
            return self.request(
                method="POST", url=f"{endpoint}{uri}", data=json_str.encode(), **kwargs
            )
        else:
            return self.request(method="POST", url=f"{endpoint}{uri}", **kwargs)
    
    # ==================== 笔记相关 API ====================
    
    def get_note_by_id(self, note_id: str, xsec_token: str = "", xsec_source: str = "pc_feed") -> Dict:
        """通过笔记 ID 获取笔记详情
        
        Args:
            note_id: 笔记 ID
            xsec_token: 安全令牌（从笔记链接中获取）
            xsec_source: 来源标识
        
        Returns:
            笔记详情数据
        """
        data = {
            "source_note_id": note_id,
            "image_formats": ["jpg", "webp", "avif"],
            "extra": {"need_body_topic": 1},
            "xsec_source": xsec_source,
            "xsec_token": xsec_token
        }
        uri = "/api/sns/web/v1/feed"
        res = self.post(uri, data)
        return res["items"][0]["note_card"]
    
    def get_note_by_id_from_html(self, note_id: str, xsec_token: str = "", xsec_source: str = "pc_feed") -> Dict:
        """从 HTML 页面获取笔记详情
        
        Args:
            note_id: 笔记 ID
            xsec_token: 安全令牌
            xsec_source: 来源标识
        
        Returns:
            笔记详情数据
        """
        def camel_to_underscore(key):
            return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()
        
        def transform_json_keys(json_data):
            data_dict = json.loads(json_data) if isinstance(json_data, str) else json_data
            dict_new = {}
            for key, value in data_dict.items():
                new_key = camel_to_underscore(key)
                if not value:
                    dict_new[new_key] = value
                elif isinstance(value, dict):
                    dict_new[new_key] = transform_json_keys(value)
                elif isinstance(value, list):
                    dict_new[new_key] = [
                        transform_json_keys(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    dict_new[new_key] = value
            return dict_new
        
        url = f"https://www.xiaohongshu.com/explore/{note_id}"
        if xsec_token:
            url += f"?xsec_token={xsec_token}&xsec_source={xsec_source}"
        
        res = self.session.get(
            url,
            headers={"user-agent": self.user_agent, "referer": "https://www.xiaohongshu.com/"}
        )
        html = res.text
        
        # 提取页面中的初始状态数据
        match = re.findall(r"window.__INITIAL_STATE__=({.*})</script>", html)
        if match:
            state = match[0].replace("undefined", '""')
            if state != "{}":
                note_dict = transform_json_keys(json.loads(state))
                return note_dict["note"]["note_detail_map"][note_id]["note"]
        
        if ErrorEnum.IP_BLOCK.value.msg in html:
            raise IPBlockError(ErrorEnum.IP_BLOCK.value.msg)
        
        raise DataFetchError(html)
    
    # ==================== 搜索相关 API ====================
    
    def get_note_by_keyword(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        sort: SearchSortType = SearchSortType.GENERAL,
        note_type: SearchNoteType = SearchNoteType.ALL,
    ) -> Dict:
        """根据关键词搜索笔记
        
        Args:
            keyword: 搜索关键词
            page: 页码，从 1 开始
            page_size: 每页数量，默认 20
            sort: 排序方式
            note_type: 笔记类型筛选
        
        Returns:
            搜索结果，包含 has_more 和 items 字段
        """
        uri = "/api/sns/web/v1/search/notes"
        data = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
            "search_id": get_search_id(),
            "sort": sort.value if isinstance(sort, SearchSortType) else sort,
            "note_type": note_type.value if isinstance(note_type, SearchNoteType) else note_type,
        }
        return self.post(uri, data)
    
    def get_user_by_keyword(self, keyword: str, page: int = 1, page_size: int = 20) -> Dict:
        """根据关键词搜索用户
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
        
        Returns:
            搜索结果
        """
        uri = "/api/sns/web/v1/search/usersearch"
        data = {
            "search_user_request": {
                "keyword": keyword,
                "search_id": get_search_id(),
                "page": page,
                "page_size": page_size,
                "biz_type": "web_search_user",
                "request_id": f"{int(round(time.time()))}-{int(round(time.time() * 1000))}",
            }
        }
        return self.post(uri, data)
    
    def get_search_suggestion(self, keyword: str) -> List[str]:
        """获取搜索建议
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            搜索建议列表
        """
        uri = "/api/sns/web/v1/sug/recommend"
        params = {"keyword": keyword}
        result = self.get(uri, params)
        return [sug["text"] for sug in result.get("sug_items", [])]
    
    # ==================== 用户相关 API ====================
    
    def get_self_info(self) -> Dict:
        """获取当前登录用户信息"""
        uri = "/api/sns/web/v1/user/selfinfo"
        return self.get(uri)
    
    def get_user_info(self, user_id: str) -> Dict:
        """获取用户信息
        
        Args:
            user_id: 用户 ID
        
        Returns:
            用户信息
        """
        uri = "/api/sns/web/v1/user/otherinfo"
        params = {"target_user_id": user_id}
        return self.get(uri, params)
    
    def get_user_notes(self, user_id: str, cursor: str = "") -> Dict:
        """获取用户笔记列表
        
        Args:
            user_id: 用户 ID
            cursor: 分页游标
        
        Returns:
            笔记列表，包含 cursor, has_more, notes 字段
        """
        uri = "/api/sns/web/v1/user_posted"
        params = {
            "num": 30,
            "cursor": cursor,
            "user_id": user_id,
            "image_scenes": "FD_WM_WEBP"
        }
        return self.get(uri, params)
    
    def get_user_collect_notes(self, user_id: str, num: int = 30, cursor: str = "") -> Dict:
        """获取用户收藏的笔记
        
        Args:
            user_id: 用户 ID
            num: 数量
            cursor: 分页游标
        
        Returns:
            收藏笔记列表
        """
        uri = "/api/sns/web/v2/note/collect/page"
        params = {"user_id": user_id, "num": num, "cursor": cursor}
        return self.get(uri, params)
    
    def get_user_like_notes(self, user_id: str, num: int = 30, cursor: str = "") -> Dict:
        """获取用户点赞的笔记
        
        Args:
            user_id: 用户 ID
            num: 数量
            cursor: 分页游标
        
        Returns:
            点赞笔记列表
        """
        uri = "/api/sns/web/v1/note/like/page"
        params = {"user_id": user_id, "num": num, "cursor": cursor}
        return self.get(uri, params)
    
    # ==================== 推荐流相关 API ====================
    
    def get_home_feed_category(self) -> List[str]:
        """获取推荐流分类列表"""
        uri = "/api/sns/web/v1/homefeed/category"
        result = self.get(uri)
        return result.get("categories", [])
    
    def get_home_feed(self, feed_type: FeedType = FeedType.RECOMMEND) -> Dict:
        """获取推荐流内容
        
        Args:
            feed_type: 推荐流类型
        
        Returns:
            推荐内容列表
        """
        uri = "/api/sns/web/v1/homefeed"
        data = {
            "cursor_score": "",
            "num": 40,
            "refresh_type": 1,
            "note_index": 0,
            "unread_begin_note_id": "",
            "unread_end_note_id": "",
            "unread_note_count": 0,
            "category": feed_type.value if isinstance(feed_type, FeedType) else feed_type,
            "search_key": "",
            "need_num": 40,
            "image_scenes": ["FD_PRV_WEBP", "FD_WM_WEBP"]
        }
        return self.post(uri, data)
    
    # ==================== 评论相关 API ====================
    
    def get_note_comments(self, note_id: str, cursor: str = "", xsec_token: str = "") -> Dict:
        """获取笔记评论
        
        Args:
            note_id: 笔记 ID
            cursor: 分页游标
            xsec_token: 安全令牌
        
        Returns:
            评论列表
        """
        uri = "/api/sns/web/v2/comment/page"
        params = {
            "note_id": note_id,
            "cursor": cursor,
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token
        }
        return self.get(uri, params)
    
    def get_note_sub_comments(
        self,
        note_id: str,
        root_comment_id: str,
        num: int = 30,
        cursor: str = ""
    ) -> Dict:
        """获取笔记子评论
        
        Args:
            note_id: 笔记 ID
            root_comment_id: 父评论 ID
            num: 数量
            cursor: 分页游标
        
        Returns:
            子评论列表
        """
        uri = "/api/sns/web/v2/comment/sub/page"
        params = {
            "note_id": note_id,
            "root_comment_id": root_comment_id,
            "num": num,
            "cursor": cursor,
        }
        return self.get(uri, params)
    
    # ==================== 互动相关 API ====================
    
    def like_note(self, note_id: str) -> Dict:
        """点赞笔记"""
        uri = "/api/sns/web/v1/note/like"
        data = {"note_oid": note_id}
        return self.post(uri, data)
    
    def dislike_note(self, note_id: str) -> Dict:
        """取消点赞笔记"""
        uri = "/api/sns/web/v1/note/dislike"
        data = {"note_oid": note_id}
        return self.post(uri, data)
    
    def collect_note(self, note_id: str) -> Dict:
        """收藏笔记"""
        uri = "/api/sns/web/v1/note/collect"
        data = {"note_id": note_id}
        return self.post(uri, data)
    
    def uncollect_note(self, note_id: str) -> Dict:
        """取消收藏笔记"""
        uri = "/api/sns/web/v1/note/uncollect"
        data = {"note_ids": note_id}
        return self.post(uri, data)
    
    def follow_user(self, user_id: str) -> Dict:
        """关注用户"""
        uri = "/api/sns/web/v1/user/follow"
        data = {"target_user_id": user_id}
        return self.post(uri, data)
    
    def unfollow_user(self, user_id: str) -> Dict:
        """取消关注用户"""
        uri = "/api/sns/web/v1/user/unfollow"
        data = {"target_user_id": user_id}
        return self.post(uri, data)
    
    def comment_note(self, note_id: str, content: str) -> Dict:
        """评论笔记"""
        uri = "/api/sns/web/v1/comment/post"
        data = {"note_id": note_id, "content": content, "at_users": []}
        return self.post(uri, data)
    
    def delete_note_comment(self, note_id: str, comment_id: str) -> Dict:
        """删除评论"""
        uri = "/api/sns/web/v1/comment/delete"
        data = {"note_id": note_id, "comment_id": comment_id}
        return self.post(uri, data)