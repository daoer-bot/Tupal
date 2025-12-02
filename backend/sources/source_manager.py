"""
数据源管理器
负责注册和管理所有数据源
"""
from typing import Dict, List, Optional
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class SourceManager:
    """数据源管理器"""
    
    def __init__(self):
        self._sources: Dict[str, BaseSource] = {}
    
    def register(self, source: BaseSource):
        """
        注册数据源
        
        Args:
            source: 数据源实例
        """
        if not source.source_id:
            raise ValueError("数据源必须设置 source_id")
        
        self._sources[source.source_id] = source
        logger.info(f"Registered source: {source.source_id} - {source.source_name}")
    
    def get_source(self, source_id: str) -> Optional[BaseSource]:
        """
        获取数据源
        
        Args:
            source_id: 数据源ID
            
        Returns:
            Optional[BaseSource]: 数据源实例，不存在则返回None
        """
        return self._sources.get(source_id)
    
    def get_all_sources(self) -> Dict[str, BaseSource]:
        """
        获取所有数据源
        
        Returns:
            Dict[str, BaseSource]: 所有数据源字典
        """
        return self._sources.copy()
    
    def get_sources_info(self) -> List[Dict]:
        """
        获取所有数据源信息
        
        Returns:
            List[Dict]: 数据源信息列表
        """
        return [source.get_source_info() for source in self._sources.values()]
    
    async def fetch_source_data(self, source_id: str) -> List[TrendingItem]:
        """
        获取指定数据源的数据
        
        Args:
            source_id: 数据源ID
            
        Returns:
            List[TrendingItem]: 热榜条目列表
            
        Raises:
            ValueError: 数据源不存在
            Exception: 获取数据失败
        """
        source = self.get_source(source_id)
        if not source:
            raise ValueError(f"数据源不存在: {source_id}")
        
        try:
            items = await source.fetch_data()
            logger.info(f"Fetched {len(items)} items from {source_id}")
            return items
        except Exception as e:
            logger.error(f"Failed to fetch data from {source_id}: {e}")
            raise


# 全局数据源管理器实例
source_manager = SourceManager()