"""
澎湃新闻热榜数据源
参考 next-daily-hot 实现
"""
from typing import List, Dict
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class ThePaperHotSource(BaseSource):
    """澎湃新闻热榜"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "thepaper"
        self.source_name = "澎湃新闻"
        self.icon = "/thepaper.svg"
        self.interval = 300  # 5分钟刷新
    
    def get_headers(self) -> Dict[str, str]:
        """覆盖父类方法，添加澎湃新闻特定的请求头"""
        headers = super().get_headers()
        headers.update({
            'Referer': 'https://www.thepaper.cn/',
        })
        return headers
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取澎湃新闻热榜数据"""
        url = "https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar"
        
        try:
            import requests
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # 检查返回状态
            if data.get('resultCode') != 1:
                logger.warning(f"澎湃新闻热榜返回状态错误: {data.get('resultCode')}")
                return []
            
            # 获取热门新闻列表
            hot_news = data.get('data', {}).get('hotNews', [])
            
            if not hot_news:
                logger.warning("澎湃新闻热榜返回数据为空")
                return []
            
            items = []
            for index, item in enumerate(hot_news):
                try:
                    cont_id = item.get('contId', '')
                    title = item.get('name', '')
                    pic = item.get('pic', '')
                    praise_times = item.get('praiseTimes', '')
                    
                    trending_item = TrendingItem(
                        id=str(cont_id),
                        title=title,
                        url=f"https://www.thepaper.cn/newsDetail_forward_{cont_id}",
                        mobile_url=f"https://m.thepaper.cn/newsDetail_forward_{cont_id}",
                        hot_value=str(praise_times) if praise_times else '',
                        index=index + 1,
                        extra={
                            'pic': pic
                        }
                    )
                    items.append(trending_item)
                    
                except Exception as e:
                    logger.warning(f"解析澎湃新闻热榜条目失败: {e}")
                    continue
            
            logger.info(f"成功获取澎湃新闻热榜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取澎湃新闻热榜失败: {e}")
            return []