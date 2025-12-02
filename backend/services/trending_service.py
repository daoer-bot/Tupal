"""
热榜服务
统一管理所有热榜数据源，提供缓存和并发获取功能
"""
from typing import List, Dict, Optional
import asyncio
import logging
from datetime import datetime, timedelta
from threading import Lock

from sources.source_manager import SourceManager
from sources.baidu_hot_source import BaiduHotSource
from sources.zhihu_hot_source import ZhihuHotSource
from sources.weibo_hot_source import WeiboHotSource
from sources.bilibili_hot_source import BilibiliHotSource
# from sources.douyin_hot_source import DouyinHotSource
# from sources.toutiao_hot_source import ToutiaoHotSource

logger = logging.getLogger(__name__)


class TrendingService:
    """热榜服务类"""
    
    def __init__(self):
        self.source_manager = SourceManager()
        self._cache: Dict[str, Dict] = {}  # 缓存结构: {source_id: {data: [], timestamp: datetime}}
        self._cache_lock = Lock()
        self._init_sources()
    
    def _init_sources(self):
        """初始化所有热榜数据源"""
        sources = [
            BaiduHotSource(),
            ZhihuHotSource(),
            WeiboHotSource(),
            BilibiliHotSource(),
            # DouyinHotSource(),  # 暂时禁用：API需要特殊处理
            # ToutiaoHotSource(),  # 暂时禁用：API需要特殊处理
        ]
        
        for source in sources:
            self.source_manager.register(source)
            logger.info(f"注册热榜数据源: {source.source_name}")
    
    def get_all_sources(self) -> List[Dict]:
        """
        获取所有可用的热榜数据源信息
        
        Returns:
            List[Dict]: 数据源信息列表
        """
        return self.source_manager.get_sources_info()
    
    def _is_cache_valid(self, source_id: str) -> bool:
        """
        检查缓存是否有效
        
        Args:
            source_id: 数据源ID
            
        Returns:
            bool: 缓存是否有效
        """
        with self._cache_lock:
            if source_id not in self._cache:
                return False
            
            cache_entry = self._cache[source_id]
            timestamp = cache_entry.get('timestamp')
            
            if not timestamp:
                return False
            
            # 获取数据源配置的刷新间隔
            source = self.source_manager.get_source(source_id)
            if not source:
                return False
            
            cache_duration = timedelta(seconds=source.interval)
            return datetime.now() - timestamp < cache_duration
    
    def _get_from_cache(self, source_id: str) -> Optional[List[Dict]]:
        """
        从缓存获取数据
        
        Args:
            source_id: 数据源ID
            
        Returns:
            Optional[List[Dict]]: 缓存的数据，如果不存在或已过期则返回None
        """
        if not self._is_cache_valid(source_id):
            return None
        
        with self._cache_lock:
            cache_entry = self._cache.get(source_id, {})
            return cache_entry.get('data')
    
    def _set_cache(self, source_id: str, data: List[Dict]):
        """
        设置缓存
        
        Args:
            source_id: 数据源ID
            data: 要缓存的数据
        """
        with self._cache_lock:
            self._cache[source_id] = {
                'data': data,
                'timestamp': datetime.now()
            }
    
    async def get_trending_data(self, source_id: str, force_refresh: bool = False) -> Dict:
        """
        获取指定数据源的热榜数据
        
        Args:
            source_id: 数据源ID
            force_refresh: 是否强制刷新（忽略缓存）
            
        Returns:
            Dict: 包含数据和元信息的字典
        """
        # 检查缓存
        if not force_refresh:
            cached_data = self._get_from_cache(source_id)
            if cached_data is not None:
                logger.info(f"从缓存返回 {source_id} 数据")
                return {
                    'success': True,
                    'source_id': source_id,
                    'data': cached_data,
                    'from_cache': True,
                    'update_time': self._cache[source_id]['timestamp'].isoformat()
                }
        
        # 获取新数据
        try:
            items = await self.source_manager.fetch_source_data(source_id)
            data = [item.to_dict() for item in items]
            
            # 更新缓存
            self._set_cache(source_id, data)
            
            return {
                'success': True,
                'source_id': source_id,
                'data': data,
                'from_cache': False,
                'update_time': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"获取 {source_id} 数据失败: {e}")
            return {
                'success': False,
                'source_id': source_id,
                'error': str(e),
                'data': []
            }
    
    async def get_all_trending_data(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """
        并发获取所有数据源的热榜数据
        
        Args:
            force_refresh: 是否强制刷新（忽略缓存）
            
        Returns:
            Dict[str, Dict]: 所有数据源的数据，key为source_id
        """
        sources = self.get_all_sources()
        source_ids = [s['id'] for s in sources]
        
        # 并发获取所有数据源
        tasks = [self.get_trending_data(sid, force_refresh) for sid in source_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整理结果
        trending_data = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"获取数据异常: {result}")
                continue
            
            if result.get('success'):
                trending_data[result['source_id']] = result
        
        return trending_data
    
    def clear_cache(self, source_id: Optional[str] = None):
        """
        清除缓存
        
        Args:
            source_id: 数据源ID，如果为None则清除所有缓存
        """
        with self._cache_lock:
            if source_id:
                if source_id in self._cache:
                    del self._cache[source_id]
                    logger.info(f"清除 {source_id} 缓存")
            else:
                self._cache.clear()
                logger.info("清除所有缓存")


# 全局服务实例
_trending_service_instance = None


def get_trending_service() -> TrendingService:
    """获取热榜服务单例"""
    global _trending_service_instance
    if _trending_service_instance is None:
        _trending_service_instance = TrendingService()
    return _trending_service_instance