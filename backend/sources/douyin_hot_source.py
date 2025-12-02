"""
抖音热榜数据源
参考 next-daily-hot 实现
"""
from typing import List, Dict
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
    
    def get_headers(self, referer=None) -> Dict[str, str]:
        """覆盖父类方法，添加抖音特定的请求头"""
        headers = super().get_headers(referer)
        headers.update({
            'Referer': 'https://www.douyin.com/',
            'Cookie': 'ttwid=1%7C',  # 最小化cookie
        })
        return headers
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取抖音热榜数据"""
        url = "https://aweme.snssdk.com/aweme/v1/hot/search/list/"
        
        try:
            # 使用自定义headers
            import requests
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
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
                trending_item = TrendingItem(
                    id=item.get('group_id', f"{index}"),
                    title=word,
                    url=f"https://www.douyin.com/hot/{sentence_id}",
                    mobile_url=f"https://www.douyin.com/hot/{sentence_id}",
                    hot_value=str(item.get('hot_value', '')),
                    index=index + 1,
                    extra={
                        'label': item.get('label', ''),
                        'pic': item.get('word_cover', {}).get('url_list', [''])[0] if item.get('word_cover') else ''
                    }
                )
                items.append(trending_item)
            
            logger.info(f"成功获取抖音热榜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取抖音热榜失败: {e}")
            return []