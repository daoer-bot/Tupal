"""
热榜服务
负责热榜数据的获取、缓存和管理
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
from sources.source_manager import source_manager
from sources.weibo_source import WeiboSource
from sources.zhihu_source import ZhihuSource
from sources.douyin_source import DouyinSource
from sources.bilibili_source import BilibiliSource
from sources.baidu_source import BaiduSource
from sources.xiaohongshu_source import XiaohongshuSource

logger = logging.getLogger(__name__)


class TrendingCache:
    """热榜数据缓存"""
    
    def __init__(self, ttl: int = 1800):
        """
        初始化缓存
        
        Args:
            ttl: 缓存过期时间（秒），默认30分钟
        """
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, source_id: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存数据
        
        Args:
            source_id: 数据源ID
            
        Returns:
            Optional[Dict]: 缓存数据，不存在或已过期返回None
        """
        if source_id not in self._cache:
            return None
        
        cache_data = self._cache[source_id]
        cached_time = cache_data.get('cached_time')
        
        # 检查是否过期
        if datetime.now() - cached_time > timedelta(seconds=self.ttl):
            del self._cache[source_id]
            return None
        
        return cache_data
    
    def set(self, source_id: str, data: List[Dict], updated_time: datetime):
        """
        设置缓存数据
        
        Args:
            source_id: 数据源ID
            data: 热榜数据
            updated_time: 更新时间
        """
        self._cache[source_id] = {
            'data': data,
            'cached_time': datetime.now(),
            'updated_time': updated_time
        }
        logger.info(f"Cached data for {source_id}, items: {len(data)}")
    
    def clear(self, source_id: Optional[str] = None):
        """
        清除缓存
        
        Args:
            source_id: 数据源ID，为None则清除所有缓存
        """
        if source_id:
            if source_id in self._cache:
                del self._cache[source_id]
                logger.info(f"Cleared cache for {source_id}")
        else:
            self._cache.clear()
            logger.info("Cleared all cache")


class TrendingService:
    """热榜服务"""
    
    def __init__(self, cache_ttl: int = 1800):
        """
        初始化服务
        
        Args:
            cache_ttl: 缓存过期时间（秒），默认30分钟
        """
        self.cache = TrendingCache(ttl=cache_ttl)
        self._initialize_sources()
    
    def _initialize_sources(self):
        """初始化并注册所有数据源"""
        sources = [
            WeiboSource(),
            ZhihuSource(),
            DouyinSource(),
            BilibiliSource(),
            BaiduSource(),
            XiaohongshuSource()
        ]
        
        for source in sources:
            source_manager.register(source)
        
        logger.info(f"Initialized {len(sources)} trending sources")
    
    def get_sources_list(self) -> List[Dict[str, Any]]:
        """
        获取所有数据源列表
        
        Returns:
            List[Dict]: 数据源信息列表
        """
        return source_manager.get_sources_info()
    
    async def get_trending_data(self, source_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        获取热榜数据
        
        Args:
            source_id: 数据源ID
            force_refresh: 是否强制刷新（忽略缓存）
            
        Returns:
            Dict: 包含热榜数据和元信息的字典
            
        Raises:
            ValueError: 数据源不存在
            Exception: 获取数据失败
        """
        # 检查数据源是否存在
        source = source_manager.get_source(source_id)
        if not source:
            raise ValueError(f"数据源不存在: {source_id}")
        
        # 如果不强制刷新，先尝试从缓存获取
        if not force_refresh:
            cached_data = self.cache.get(source_id)
            if cached_data:
                logger.info(f"Returning cached data for {source_id}")
                return {
                    'source_id': source_id,
                    'source_name': source.source_name,
                    'icon': source.icon,
                    'items': cached_data['data'],
                    'updated_time': cached_data['updated_time'].isoformat(),
                    'from_cache': True
                }
        
        # 获取最新数据
        try:
            logger.info(f"Fetching fresh data for {source_id}")
            items = await source_manager.fetch_source_data(source_id)
            
            # 转换为字典格式
            items_dict = [item.to_dict() for item in items]
            
            # 更新缓存
            updated_time = datetime.now()
            self.cache.set(source_id, items_dict, updated_time)
            
            return {
                'source_id': source_id,
                'source_name': source.source_name,
                'icon': source.icon,
                'items': items_dict,
                'updated_time': updated_time.isoformat(),
                'from_cache': False
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch trending data for {source_id}: {e}")
            
            # 如果获取失败，尝试返回缓存数据（即使可能已过期）
            cached_data = self._cache.get(source_id) if hasattr(self, '_cache') else None
            if cached_data:
                logger.warning(f"Returning stale cache for {source_id} due to fetch error")
                return {
                    'source_id': source_id,
                    'source_name': source.source_name,
                    'icon': source.icon,
                    'items': cached_data['data'],
                    'updated_time': cached_data['updated_time'].isoformat(),
                    'from_cache': True,
                    'error': str(e)
                }
            
            raise
    
    async def get_all_trending_data(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        获取所有平台的热榜数据
        
        Args:
            force_refresh: 是否强制刷新
            
        Returns:
            List[Dict]: 所有平台的热榜数据列表
        """
        sources = source_manager.get_all_sources()
        tasks = []
        
        for source_id in sources.keys():
            tasks.append(self.get_trending_data(source_id, force_refresh))
        
        # 并发获取所有数据源，但捕获单个失败
        results = []
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to fetch one source: {e}")
                # 继续处理其他数据源
                continue
        
        return results
    
    def clear_cache(self, source_id: Optional[str] = None):
        """
        清除缓存
        
        Args:
            source_id: 数据源ID，为None则清除所有缓存
        """
        self.cache.clear(source_id)