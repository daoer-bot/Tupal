"""
百度热搜数据源
"""
from typing import List
from bs4 import BeautifulSoup
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class BaiduSource(BaseSource):
    """百度热搜数据源"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "baidu"
        self.source_name = "百度热搜"
        self.icon = "/icons/baidu.png"
        self.interval = 600  # 10分钟
    
    async def fetch_data(self) -> List[TrendingItem]:
        """
        抓取百度热搜数据
        
        Returns:
            List[TrendingItem]: 热榜条目列表
        """
        try:
            # 百度热搜榜
            url = "https://top.baidu.com/board?tab=realtime"
            html = await self.fetch_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            
            items = []
            
            # 查找热搜列表
            content_items = soup.select('.category-wrap_iQLoo .c-single-text-ellipsis')
            
            for index, item in enumerate(content_items[:30], 1):  # 只取前30条
                try:
                    title = item.text.strip()
                    
                    if not title:
                        continue
                    
                    # 构建搜索URL
                    url = f"https://www.baidu.com/s?wd={title}"
                    
                    # 尝试获取热度值
                    hot_elem = item.find_parent('div', class_='content_1YWBm')
                    hot_value = None
                    if hot_elem:
                        hot_span = hot_elem.select_one('.hot-index_1Bl1a')
                        if hot_span:
                            hot_value = hot_span.text.strip()
                    
                    trending_item = TrendingItem(
                        id=f"baidu_{index}_{title[:20]}",
                        title=title,
                        url=url,
                        mobile_url=url,
                        hot_value=hot_value,
                        index=index,
                        extra=None
                    )
                    items.append(trending_item)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse baidu item: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(items)} items from Baidu")
            return items
            
        except Exception as e:
            logger.error(f"Failed to fetch Baidu trending: {e}")
            raise Exception(f"获取百度热搜失败: {str(e)}")