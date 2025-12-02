"""
知乎热榜数据源
参考 next-daily-hot 实现
"""
from typing import List, Dict
from .base_source import BaseSource, TrendingItem, USER_AGENTS
import logging
import random

logger = logging.getLogger(__name__)


class ZhihuHotSource(BaseSource):
    """知乎热榜"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "zhihu"
        self.source_name = "知乎热榜"
        self.icon = "/zhihu.svg"
        self.interval = 300  # 5分钟刷新
    
    def get_headers(self) -> Dict[str, str]:
        """
        知乎API需要简化的请求头，避免触发反爬虫
        只使用必要的User-Agent和Accept头
        """
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'application/json, text/plain, */*',
        }
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取知乎热榜数据"""
        url = "https://api.zhihu.com/topstory/hot-list"
        
        try:
            data = await self.fetch_json(url)
            
            hot_list = data.get('data', [])
            if not hot_list:
                return []
            
            items = []
            for index, item in enumerate(hot_list):
                target = item.get('target', {})
                card_id = item.get('card_id', '').replace('Q_', '')
                
                # 提取热度数值
                detail_text = item.get('detail_text', '')
                hot_value = ''.join(filter(str.isdigit, detail_text))
                if hot_value:
                    hot_value = str(int(hot_value) * 10000)
                
                # 获取缩略图
                pic = ''
                children = item.get('children', [])
                if children and len(children) > 0:
                    pic = children[0].get('thumbnail', '')
                
                trending_item = TrendingItem(
                    id=str(item.get('id', '')),
                    title=target.get('title', ''),
                    url=f"https://www.zhihu.com/question/{card_id}",
                    mobile_url=f"https://www.zhihu.com/question/{card_id}",
                    hot_value=hot_value,
                    index=index + 1,
                    extra={
                        'pic': pic,
                        'excerpt': target.get('excerpt', '')
                    }
                )
                items.append(trending_item)
            
            logger.info(f"成功获取知乎热榜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取知乎热榜失败: {e}")
            return []