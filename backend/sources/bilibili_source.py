"""
B站热门数据源
"""
from typing import List
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class BilibiliSource(BaseSource):
    """B站热门数据源"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "bilibili"
        self.source_name = "B站热门"
        self.icon = "/icons/bilibili.png"
        self.interval = 600  # 10分钟
    
    async def fetch_data(self) -> List[TrendingItem]:
        """
        抓取B站热门数据
        
        Returns:
            List[TrendingItem]: 热榜条目列表
        """
        try:
            # B站热门榜API
            url = "https://api.bilibili.com/x/web-interface/popular"
            params = {
                'ps': 30,  # 每页数量
                'pn': 1    # 页码
            }
            
            # 构建完整URL
            full_url = f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            
            data = await self.fetch_json(full_url)
            
            items = []
            video_list = data.get('data', {}).get('list', [])
            
            for index, item in enumerate(video_list[:30], 1):  # 只取前30条
                try:
                    title = item.get('title', '').strip()
                    bvid = item.get('bvid', '')
                    aid = item.get('aid', '')
                    
                    if not title or not bvid:
                        continue
                    
                    # 构建视频URL
                    url = f"https://www.bilibili.com/video/{bvid}"
                    
                    # 获取统计数据
                    stat = item.get('stat', {})
                    view = stat.get('view', 0)
                    
                    # 格式化播放量
                    if view >= 10000:
                        hot_str = f"{view / 10000:.1f}万播放"
                    else:
                        hot_str = f"{view}播放"
                    
                    # 获取UP主信息
                    owner = item.get('owner', {})
                    owner_name = owner.get('name', '')
                    
                    extra = {}
                    if owner_name:
                        extra['author'] = owner_name
                    
                    trending_item = TrendingItem(
                        id=f"bilibili_{bvid}",
                        title=title,
                        url=url,
                        mobile_url=url,
                        hot_value=hot_str,
                        index=index,
                        extra=extra if extra else None
                    )
                    items.append(trending_item)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse bilibili item: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(items)} items from Bilibili")
            return items
            
        except Exception as e:
            logger.error(f"Failed to fetch Bilibili trending: {e}")
            raise Exception(f"获取B站热门失败: {str(e)}")