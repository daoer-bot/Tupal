"""
小红书服务层
管理 XhsClient 实例，提供业务逻辑封装
"""
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from xhs import XhsClient, XhsException
from xhs.client import FeedType, SearchSortType, SearchNoteType
from xhs.help import parse_note_info, extract_note_id_from_url, extract_user_id_from_url

logger = logging.getLogger(__name__)


class XhsService:
    """小红书服务类 - 单例模式"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(XhsService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 客户端存储: {client_id: (XhsClient, last_used_time)}
        self._clients: Dict[str, Tuple[XhsClient, datetime]] = {}
        self._counter = 0
        self._cleanup_interval = timedelta(hours=1)  # 清理间隔
        self._client_timeout = timedelta(hours=2)  # 客户端超时时间
        self._last_cleanup = datetime.now()
        
        self._initialized = True
        logger.info("XhsService 初始化完成")
    
    def create_client(
        self,
        cookie: str,
        user_agent: Optional[str] = None,
        timeout: int = 10,
        proxies: Optional[Dict] = None
    ) -> str:
        """创建新的客户端实例
        
        Args:
            cookie: 小红书 cookie
            user_agent: 自定义 User-Agent
            timeout: 请求超时时间
            proxies: 代理配置
        
        Returns:
            客户端 ID
        
        Raises:
            ValueError: 如果 cookie 为空
        """
        if not cookie:
            raise ValueError("必须提供 cookie")
        
        with self._lock:
            # 定期清理过期客户端
            self._cleanup_expired_clients()
            
            # 创建客户端
            client = XhsClient(
                cookie=cookie,
                user_agent=user_agent,
                timeout=timeout,
                proxies=proxies
            )
            
            # 生成客户端 ID
            self._counter += 1
            client_id = f"xhs_client_{self._counter}"
            
            # 存储客户端
            self._clients[client_id] = (client, datetime.now())
            
            logger.info(f"创建小红书客户端: {client_id}")
            return client_id
    
    def get_client(self, client_id: str) -> XhsClient:
        """获取客户端实例
        
        Args:
            client_id: 客户端 ID
        
        Returns:
            XhsClient 实例
        
        Raises:
            ValueError: 如果客户端不存在
        """
        if client_id not in self._clients:
            raise ValueError(f"客户端不存在: {client_id}")
        
        client, _ = self._clients[client_id]
        # 更新最后使用时间
        self._clients[client_id] = (client, datetime.now())
        return client
    
    def delete_client(self, client_id: str) -> bool:
        """删除客户端实例
        
        Args:
            client_id: 客户端 ID
        
        Returns:
            是否删除成功
        """
        with self._lock:
            if client_id in self._clients:
                del self._clients[client_id]
                logger.info(f"删除小红书客户端: {client_id}")
                return True
            return False
    
    def list_clients(self) -> List[str]:
        """列出所有客户端 ID"""
        return list(self._clients.keys())
    
    def _cleanup_expired_clients(self):
        """清理过期的客户端"""
        now = datetime.now()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        expired = [
            client_id
            for client_id, (_, last_used) in self._clients.items()
            if now - last_used > self._client_timeout
        ]
        
        for client_id in expired:
            del self._clients[client_id]
            logger.info(f"清理过期客户端: {client_id}")
        
        self._last_cleanup = now
    
    # ==================== 笔记相关方法 ====================
    
    def get_note(
        self,
        client_id: str,
        note_id: str,
        xsec_token: str = "",
        xsec_source: str = "pc_feed"
    ) -> Dict:
        """获取笔记详情
        
        Args:
            client_id: 客户端 ID
            note_id: 笔记 ID 或链接
            xsec_token: 安全令牌
            xsec_source: 来源标识
        
        Returns:
            笔记详情
        """
        client = self.get_client(client_id)
        
        # 如果是链接，提取笔记 ID
        extracted_id = extract_note_id_from_url(note_id)
        if extracted_id:
            note_id = extracted_id
        
        try:
            note = client.get_note_by_id(note_id, xsec_token, xsec_source)
            return parse_note_info(note)
        except XhsException as e:
            logger.error(f"获取笔记失败: {e}")
            raise
    
    def get_note_from_html(
        self,
        client_id: str,
        note_id: str,
        xsec_token: str = "",
        xsec_source: str = "pc_feed"
    ) -> Dict:
        """从 HTML 获取笔记详情
        
        Args:
            client_id: 客户端 ID
            note_id: 笔记 ID 或链接
            xsec_token: 安全令牌
            xsec_source: 来源标识
        
        Returns:
            笔记详情
        """
        client = self.get_client(client_id)
        
        # 如果是链接，提取笔记 ID
        extracted_id = extract_note_id_from_url(note_id)
        if extracted_id:
            note_id = extracted_id
        
        try:
            note = client.get_note_by_id_from_html(note_id, xsec_token, xsec_source)
            return parse_note_info(note)
        except XhsException as e:
            logger.error(f"从 HTML 获取笔记失败: {e}")
            raise
    
    # ==================== 搜索相关方法 ====================
    
    def search_notes(
        self,
        client_id: str,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        sort: str = "general",
        note_type: int = 0
    ) -> Dict:
        """搜索笔记
        
        Args:
            client_id: 客户端 ID
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            sort: 排序方式 (general/popularity_descending/time_descending)
            note_type: 笔记类型 (0=全部, 1=视频, 2=图文)
        
        Returns:
            搜索结果
        """
        client = self.get_client(client_id)
        
        # 转换排序类型
        sort_map = {
            "general": SearchSortType.GENERAL,
            "popularity_descending": SearchSortType.MOST_POPULAR,
            "time_descending": SearchSortType.LATEST
        }
        sort_type = sort_map.get(sort, SearchSortType.GENERAL)
        
        # 转换笔记类型
        note_type_map = {
            0: SearchNoteType.ALL,
            1: SearchNoteType.VIDEO,
            2: SearchNoteType.IMAGE
        }
        search_note_type = note_type_map.get(note_type, SearchNoteType.ALL)
        
        try:
            result = client.get_note_by_keyword(
                keyword=keyword,
                page=page,
                page_size=page_size,
                sort=sort_type,
                note_type=search_note_type
            )
            return result
        except XhsException as e:
            logger.error(f"搜索笔记失败: {e}")
            raise
    
    def search_users(
        self,
        client_id: str,
        keyword: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """搜索用户
        
        Args:
            client_id: 客户端 ID
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
        
        Returns:
            搜索结果
        """
        client = self.get_client(client_id)
        
        try:
            result = client.get_user_by_keyword(
                keyword=keyword,
                page=page,
                page_size=page_size
            )
            return result
        except XhsException as e:
            logger.error(f"搜索用户失败: {e}")
            raise
    
    def get_search_suggestion(self, client_id: str, keyword: str) -> List[str]:
        """获取搜索建议
        
        Args:
            client_id: 客户端 ID
            keyword: 搜索关键词
        
        Returns:
            搜索建议列表
        """
        client = self.get_client(client_id)
        
        try:
            return client.get_search_suggestion(keyword)
        except XhsException as e:
            logger.error(f"获取搜索建议失败: {e}")
            raise
    
    # ==================== 用户相关方法 ====================
    
    def get_self_info(self, client_id: str) -> Dict:
        """获取当前登录用户信息
        
        Args:
            client_id: 客户端 ID
        
        Returns:
            用户信息
        """
        client = self.get_client(client_id)
        
        try:
            return client.get_self_info()
        except XhsException as e:
            logger.error(f"获取当前用户信息失败: {e}")
            raise
    
    def get_user_info(self, client_id: str, user_id: str) -> Dict:
        """获取用户信息
        
        Args:
            client_id: 客户端 ID
            user_id: 用户 ID 或链接
        
        Returns:
            用户信息
        """
        client = self.get_client(client_id)
        
        # 如果是链接，提取用户 ID
        extracted_id = extract_user_id_from_url(user_id)
        if extracted_id:
            user_id = extracted_id
        
        try:
            return client.get_user_info(user_id)
        except XhsException as e:
            logger.error(f"获取用户信息失败: {e}")
            raise
    
    def get_user_notes(
        self,
        client_id: str,
        user_id: str,
        cursor: str = ""
    ) -> Dict:
        """获取用户笔记列表
        
        Args:
            client_id: 客户端 ID
            user_id: 用户 ID 或链接
            cursor: 分页游标
        
        Returns:
            笔记列表
        """
        client = self.get_client(client_id)
        
        # 如果是链接，提取用户 ID
        extracted_id = extract_user_id_from_url(user_id)
        if extracted_id:
            user_id = extracted_id
        
        try:
            return client.get_user_notes(user_id, cursor)
        except XhsException as e:
            logger.error(f"获取用户笔记失败: {e}")
            raise
    
    # ==================== 推荐流相关方法 ====================
    
    def get_feed_categories(self, client_id: str) -> List[str]:
        """获取推荐流分类
        
        Args:
            client_id: 客户端 ID
        
        Returns:
            分类列表
        """
        client = self.get_client(client_id)
        
        try:
            return client.get_home_feed_category()
        except XhsException as e:
            logger.error(f"获取推荐流分类失败: {e}")
            raise
    
    def get_feed(self, client_id: str, feed_type: str = "homefeed_recommend") -> Dict:
        """获取推荐流内容
        
        Args:
            client_id: 客户端 ID
            feed_type: 推荐流类型
        
        Returns:
            推荐内容
        """
        client = self.get_client(client_id)
        
        # 转换推荐流类型
        try:
            ft = FeedType(feed_type)
        except ValueError:
            ft = FeedType.RECOMMEND
        
        try:
            return client.get_home_feed(ft)
        except XhsException as e:
            logger.error(f"获取推荐流失败: {e}")
            raise
    
    # ==================== 评论相关方法 ====================
    
    def get_note_comments(
        self,
        client_id: str,
        note_id: str,
        cursor: str = "",
        xsec_token: str = ""
    ) -> Dict:
        """获取笔记评论
        
        Args:
            client_id: 客户端 ID
            note_id: 笔记 ID
            cursor: 分页游标
            xsec_token: 安全令牌
        
        Returns:
            评论列表
        """
        client = self.get_client(client_id)
        
        # 如果是链接，提取笔记 ID
        extracted_id = extract_note_id_from_url(note_id)
        if extracted_id:
            note_id = extracted_id
        
        try:
            return client.get_note_comments(note_id, cursor, xsec_token)
        except XhsException as e:
            logger.error(f"获取笔记评论失败: {e}")
            raise


# 全局服务实例
xhs_service = XhsService()