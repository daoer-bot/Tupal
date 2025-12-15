"""
抖音热榜数据源
参考 next-daily-hot 实现
"""
from typing import List
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class DouyinHotSource(BaseSource):
    """抖音热榜"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "douyin"
        self.source_name = "抖音热榜"
        self.icon = "/douyin.svg"
        self.interval = 300  # 5分钟刷新
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取抖音热榜数据"""
        url = "https://aweme.snssdk.com/aweme/v1/hot/search/list/"
        
        try:
            data = await self.fetch_json(url)
            
            # 检查状态码
            if data.get('status_code') != 0:
                logger.warning(f"抖音热榜返回状态码错误: {data.get('status_code')}")
                return []
            
            word_list = data.get('data', {}).get('word_list', [])
            if not word_list:
                logger.warning("抖音热榜返回数据为空")
                return []
            
            items = []
            for index, item in enumerate(word_list):
                word = item.get('word', '')
                sentence_id = item.get('sentence_id', '')
                
                # 获取封面图片
                pic = ''
                word_cover = item.get('word_cover')
                if word_cover and isinstance(word_cover, dict):
                    url_list = word_cover.get('url_list', [])
                    if url_list and len(url_list) > 0:
                        pic = url_list[0]
                
                trending_item = TrendingItem(
                    id=str(item.get('group_id', f"{index}")),
                    title=word,
                    url=f"https://www.douyin.com/hot/{sentence_id}",
                    mobile_url=f"https://www.douyin.com/hot/{sentence_id}",
                    hot_value=str(item.get('hot_value', '')),
                    index=index + 1,
                    extra={
                        'label': item.get('label', ''),
                        'pic': pic
                    }
                )
                items.append(trending_item)
            
            logger.info(f"成功获取抖音热榜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取抖音热榜失败: {e}")
            return []