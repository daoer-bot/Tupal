"""
微博热搜榜数据源
参考 next-daily-hot 实现
"""
from typing import List
from .base_source import BaseSource, TrendingItem
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)


class WeiboHotSource(BaseSource):
    """微博热搜榜"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "weibo"
        self.source_name = "微博热搜"
        self.icon = "/weibo.svg"
        self.interval = 300  # 5分钟刷新
    
    def get_headers(self):
        """重写请求头，添加微博特定头"""
        headers = super().get_headers()
        headers.update({
            'Referer': 'https://weibo.com/',
            'Accept': 'application/json',
        })
        return headers
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取微博热搜数据"""
        url = "https://weibo.com/ajax/side/hotSearch"
        
        try:
            data = await self.fetch_json(url)
            
            if data.get('ok') != 1:
                logger.warning(f"微博热搜返回失败: {data}")
                return []
            
            realtime = data.get('data', {}).get('realtime', [])
            if not realtime:
                return []
            
            items = []
            for index, item in enumerate(realtime):
                word = item.get('word', '')
                word_scheme = item.get('word_scheme', '')
                key = word_scheme if word_scheme else f"#{word}"
                
                trending_item = TrendingItem(
                    id=str(item.get('mid', '')),
                    title=word,
                    url=f"https://s.weibo.com/weibo?q={quote(key)}&t=31&band_rank=1&Refer=top",
                    mobile_url=f"https://s.weibo.com/weibo?q={quote(key)}&t=31&band_rank=1&Refer=top",
                    hot_value=str(item.get('raw_hot', '')),
                    index=index + 1,
                    extra={
                        'desc': key,
                        'label': item.get('label_name', '')
                    }
                )
                items.append(trending_item)
            
            logger.info(f"成功获取微博热搜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取微博热搜失败: {e}")
            return []