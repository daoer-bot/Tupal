"""
抖音热点数据源
"""
from typing import List
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class DouyinSource(BaseSource):
    """抖音热点数据源"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "douyin"
        self.source_name = "抖音热点"
        self.icon = "/icons/douyin.png"
        self.interval = 600  # 10分钟
    
    async def fetch_data(self) -> List[TrendingItem]:
        """
        抓取抖音热点数据
        
        Returns:
            List[TrendingItem]: 热榜条目列表
        """
        try:
            # 抖音热榜API
            url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"
            
            data = await self.fetch_json(url)
            
            items = []
            word_list = data.get('word_list', [])
            
            for index, item in enumerate(word_list[:30], 1):  # 只取前30条
                try:
                    word = item.get('word', '').strip()
                    hot_value = item.get('hot_value', 0)
                    sentence_id = item.get('sentence_id', '')
                    
                    if not word:
                        continue
                    
                    # 构建抖音搜索URL
                    url = f"https://www.douyin.com/search/{word}"
                    
                    # 格式化热度值
                    if hot_value >= 10000:
                        hot_str = f"{hot_value / 10000:.1f}万"
                    else:
                        hot_str = str(hot_value)
                    
                    trending_item = TrendingItem(
                        id=f"douyin_{sentence_id or index}",
                        title=word,
                        url=url,
                        mobile_url=url,
                        hot_value=hot_str,
                        index=index,
                        extra=None
                    )
                    items.append(trending_item)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse douyin item: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(items)} items from Douyin")
            return items
            
        except Exception as e:
            logger.error(f"Failed to fetch Douyin trending: {e}")
            raise Exception(f"获取抖音热点失败: {str(e)}")