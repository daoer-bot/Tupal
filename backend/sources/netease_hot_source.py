"""
网易新闻热榜数据源
参考 next-daily-hot 实现
"""
from typing import List, Dict
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class NeteaseHotSource(BaseSource):
    """网易新闻热榜"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "netease"
        self.source_name = "网易新闻"
        self.icon = "/netease.svg"
        self.interval = 300  # 5分钟刷新
    
    def get_headers(self) -> Dict[str, str]:
        """覆盖父类方法，添加网易新闻特定的请求头"""
        headers = super().get_headers()
        headers.update({
            'Referer': 'https://www.163.com/',
        })
        return headers
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取网易新闻热榜数据"""
        url = "https://m.163.com/fe/api/hot/news/flow"
        
        try:
            import requests
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # 检查返回状态
            if data.get('msg') != 'success':
                logger.warning(f"网易新闻热榜返回状态错误: {data.get('msg')}")
                return []
            
            # 获取新闻列表
            news_list = data.get('data', {}).get('list', [])
            
            if not news_list:
                logger.warning("网易新闻热榜返回数据为空")
                return []
            
            items = []
            for index, item in enumerate(news_list):
                try:
                    skip_id = item.get('skipID', '')
                    title = item.get('title', '')
                    keyword = item.get('_keyword', '')
                    pic = item.get('imgsrc', '')
                    mobile_url = item.get('url', '')
                    
                    trending_item = TrendingItem(
                        id=skip_id,
                        title=title,
                        url=f"https://www.163.com/dy/article/{skip_id}.html",
                        mobile_url=mobile_url,
                        hot_value='',  # 网易新闻API不返回热度值
                        index=index + 1,
                        extra={
                            'desc': keyword,
                            'pic': pic
                        }
                    )
                    items.append(trending_item)
                    
                except Exception as e:
                    logger.warning(f"解析网易新闻热榜条目失败: {e}")
                    continue
            
            logger.info(f"成功获取网易新闻热榜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取网易新闻热榜失败: {e}")
            return []