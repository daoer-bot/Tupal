"""
知乎热榜数据源
"""
from typing import List
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class ZhihuSource(BaseSource):
    """知乎热榜数据源"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "zhihu"
        self.source_name = "知乎热榜"
        self.icon = "/icons/zhihu.png"
        self.interval = 600  # 10分钟
    
    async def fetch_data(self) -> List[TrendingItem]:
        """
        抓取知乎热榜数据
        
        Returns:
            List[TrendingItem]: 热榜条目列表
        """
        try:
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
            params = {
                'limit': 50,
                'desktop': 'true'
            }
            
            # 构建完整URL
            full_url = f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            
            data = await self.fetch_json(full_url)
            
            items = []
            hot_list = data.get('data', [])
            
            for index, item in enumerate(hot_list[:30], 1):  # 只取前30条
                try:
                    target = item.get('target', {})
                    
                    title = target.get('title', '').strip()
                    question_id = target.get('id', '')
                    hot_value = item.get('detail_text', '')
                    
                    if not title or not question_id:
                        continue
                    
                    # 构建URL
                    url = f"https://www.zhihu.com/question/{question_id}"
                    
                    # 获取摘要
                    excerpt = target.get('excerpt', '')
                    
                    extra = {}
                    if excerpt:
                        extra['excerpt'] = excerpt[:100]  # 限制长度
                    
                    trending_item = TrendingItem(
                        id=f"zhihu_{question_id}",
                        title=title,
                        url=url,
                        mobile_url=url,
                        hot_value=hot_value,
                        index=index,
                        extra=extra if extra else None
                    )
                    items.append(trending_item)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse zhihu item: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(items)} items from Zhihu")
            return items
            
        except Exception as e:
            logger.error(f"Failed to fetch Zhihu trending: {e}")
            raise Exception(f"获取知乎热榜失败: {str(e)}")