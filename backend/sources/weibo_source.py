"""
微博热搜数据源
"""
from typing import List
from bs4 import BeautifulSoup
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class WeiboSource(BaseSource):
    """微博热搜数据源"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "weibo"
        self.source_name = "微博热搜"
        self.icon = "/icons/weibo.png"
        self.interval = 300  # 5分钟
    
    def get_headers(self):
        """重写请求头，微博需要特殊的Cookie"""
        headers = super().get_headers()
        headers.update({
            'Cookie': 'SUB=_2AkMWIuNSf8NxqwJRmP8dy2rhaoV2ygrEieKgfhKJJRMxHRl-yT9jqk86tRB6PaLNvQZR6zYUcYVT1zSjoSreQHidcUq7',
            'Referer': 'https://s.weibo.com/top/summary?cate=realtimehot'
        })
        return headers
    
    async def fetch_data(self) -> List[TrendingItem]:
        """
        抓取微博热搜数据
        
        Returns:
            List[TrendingItem]: 热榜条目列表
        """
        try:
            url = "https://s.weibo.com/top/summary?cate=realtimehot"
            html = await self.fetch_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            
            items = []
            rows = soup.select('#pl_top_realtimehot table tbody tr')[1:]  # 跳过第一行
            
            for index, row in enumerate(rows[:30], 1):  # 只取前30条
                try:
                    link = row.select_one('td.td-02 a')
                    if not link or 'javascript:void(0)' in link.get('href', ''):
                        continue
                    
                    title = link.text.strip()
                    href = link.get('href', '')
                    
                    if not title or not href:
                        continue
                    
                    # 获取热度标签
                    flag_elem = row.select_one('td.td-03')
                    flag = flag_elem.text.strip() if flag_elem else None
                    
                    # 获取热度值
                    hot_elem = row.select_one('td.td-02 span')
                    hot_value = hot_elem.text.strip() if hot_elem else None
                    
                    # 构建额外信息
                    extra = {}
                    if flag in ['新', '热', '爆']:
                        extra['tag'] = flag
                    
                    item = TrendingItem(
                        id=f"weibo_{index}_{title[:20]}",
                        title=title,
                        url=f"https://s.weibo.com{href}",
                        mobile_url=f"https://s.weibo.com{href}",
                        hot_value=hot_value,
                        index=index,
                        extra=extra if extra else None
                    )
                    items.append(item)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse weibo item: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(items)} items from Weibo")
            return items
            
        except Exception as e:
            logger.error(f"Failed to fetch Weibo trending: {e}")
            raise Exception(f"获取微博热搜失败: {str(e)}")