"""
百度热搜榜数据源
参考 next-daily-hot 实现
"""
from typing import List
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class BaiduHotSource(BaseSource):
    """百度热搜榜"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "baidu"
        self.source_name = "百度热搜"
        self.icon = "/baidu.svg"
        self.interval = 300  # 5分钟刷新
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取百度热搜数据"""
        url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
        
        try:
            data = await self.fetch_json(url)
            
            if not data.get('success'):
                logger.warning(f"百度热搜返回失败: {data}")
                return []
            
            cards = data.get('data', {}).get('cards', [])
            if not cards or len(cards) == 0:
                return []
            
            content = cards[0].get('content', [])
            
            items = []
            for index, item in enumerate(content):
                query = item.get('query', '')
                trending_item = TrendingItem(
                    id=f"{item.get('hotScore', '')}_{index}",
                    title=item.get('word', ''),
                    url=f"https://www.baidu.com/s?wd={query}",
                    mobile_url=item.get('url', ''),
                    hot_value=str(item.get('hotScore', '')),
                    index=index + 1,
                    extra={
                        'desc': item.get('desc', ''),
                        'pic': item.get('img', '')
                    }
                )
                items.append(trending_item)
            
            logger.info(f"成功获取百度热搜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取百度热搜失败: {e}")
            return []