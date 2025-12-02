"""
哔哩哔哩热门榜数据源
参考 next-daily-hot 实现
"""
from typing import List
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class BilibiliHotSource(BaseSource):
    """哔哩哔哩热门榜"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "bilibili"
        self.source_name = "哔哩哔哩"
        self.icon = "/bilibili.svg"
        self.interval = 300  # 5分钟刷新
    
    def get_headers(self):
        """重写请求头，添加B站特定头"""
        headers = super().get_headers()
        headers.update({
            'Referer': 'https://www.bilibili.com/ranking/all',
        })
        return headers
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取B站热门榜数据"""
        url = "https://api.bilibili.com/x/web-interface/ranking/v2"
        
        try:
            data = await self.fetch_json(url)
            
            # 尝试获取数据
            video_list = data.get('data', {}).get('list', [])
            if not video_list:
                video_list = data.get('data', {}).get('realtime', [])
            
            if not video_list:
                return []
            
            items = []
            for index, item in enumerate(video_list):
                bvid = item.get('bvid', '')
                pic = item.get('pic', '').replace('http:', 'https:')
                
                # 获取链接
                short_link = item.get('short_link_v2', '')
                url = short_link if short_link else f"https://b23.tv/{bvid}"
                mobile_url = f"https://m.bilibili.com/video/{bvid}"
                
                # 获取播放量
                stat = item.get('stat', {})
                view_count = stat.get('view', 0)
                
                trending_item = TrendingItem(
                    id=bvid,
                    title=item.get('title', ''),
                    url=url,
                    mobile_url=mobile_url,
                    hot_value=str(view_count),
                    index=index + 1,
                    extra={
                        'desc': item.get('desc', ''),
                        'pic': pic,
                        'owner': item.get('owner', {}).get('name', '')
                    }
                )
                items.append(trending_item)
            
            logger.info(f"成功获取B站热门榜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取B站热门榜失败: {e}")
            return []