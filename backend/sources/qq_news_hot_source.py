"""
腾讯新闻热榜数据源
参考 next-daily-hot 实现
"""
from typing import List, Dict
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class QQNewsHotSource(BaseSource):
    """腾讯新闻热榜"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "qq-news"
        self.source_name = "腾讯新闻"
        self.icon = "/qq.svg"
        self.interval = 300  # 5分钟刷新
    
    def get_headers(self) -> Dict[str, str]:
        """覆盖父类方法，添加腾讯新闻特定的请求头"""
        headers = super().get_headers()
        headers.update({
            'Referer': 'https://news.qq.com/',
        })
        return headers
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取腾讯新闻热榜数据"""
        url = "https://r.inews.qq.com/gw/event/hot_ranking_list"
        
        try:
            import requests
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # 检查返回状态
            if data.get('ret') != 0:
                logger.warning(f"腾讯新闻热榜返回状态错误: {data.get('ret')}")
                return []
            
            # 获取新闻列表（跳过第一个，通常是广告）
            id_list = data.get('idlist', [])
            if not id_list:
                logger.warning("腾讯新闻热榜返回数据为空")
                return []
            
            news_list = id_list[0].get('newslist', [])[1:]  # 跳过第一个
            
            if not news_list:
                logger.warning("腾讯新闻热榜新闻列表为空")
                return []
            
            items = []
            for index, item in enumerate(news_list):
                try:
                    news_id = item.get('id', '')
                    title = item.get('title', '')
                    abstract = item.get('abstract', '')
                    pic = item.get('miniProShareImage', '')
                    read_count = item.get('readCount', '')
                    
                    trending_item = TrendingItem(
                        id=news_id,
                        title=title,
                        url=f"https://new.qq.com/rain/a/{news_id}",
                        mobile_url=f"https://view.inews.qq.com/a/{news_id}",
                        hot_value=str(read_count) if read_count else '',
                        index=index + 1,
                        extra={
                            'desc': abstract,
                            'pic': pic
                        }
                    )
                    items.append(trending_item)
                    
                except Exception as e:
                    logger.warning(f"解析腾讯新闻热榜条目失败: {e}")
                    continue
            
            logger.info(f"成功获取腾讯新闻热榜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取腾讯新闻热榜失败: {e}")
            return []