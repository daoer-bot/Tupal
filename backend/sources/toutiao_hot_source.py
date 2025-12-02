"""
今日头条热榜数据源
参考 next-daily-hot 实现
"""
from typing import List, Dict
from .base_source import BaseSource, TrendingItem
import logging

logger = logging.getLogger(__name__)


class ToutiaoHotSource(BaseSource):
    """今日头条热榜"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "toutiao"
        self.source_name = "今日头条"
        self.icon = "/toutiao.svg"
        self.interval = 300  # 5分钟刷新
    
    def get_headers(self, referer=None) -> Dict[str, str]:
        """覆盖父类方法，添加头条特定的请求头"""
        headers = super().get_headers(referer)
        headers.update({
            'Referer': 'https://www.toutiao.com/',
        })
        return headers
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取今日头条热榜数据"""
        url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
        
        try:
            # 使用自定义headers
            import requests
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # 检查状态
            if data.get('status') != 'success':
                logger.warning(f"今日头条返回状态错误: {data.get('status')}")
                return []
            
            hot_list = data.get('data', [])
            if not hot_list:
                logger.warning("今日头条返回数据为空")
                return []
            
            items = []
            for index, item in enumerate(hot_list):
                title = item.get('Title', '')
                cluster_id_str = item.get('ClusterIdStr', '')
                trending_item = TrendingItem(
                    id=item.get('ClusterId', f"{index}"),
                    title=title,
                    url=f"https://www.toutiao.com/trending/{cluster_id_str}/",
                    mobile_url=f"https://api.toutiaoapi.com/feoffline/amos_land/new/html/main/index.html?topic_id={cluster_id_str}",
                    hot_value=str(item.get('HotValue', '')),
                    index=index + 1,
                    extra={
                        'label': item.get('LabelDesc', ''),
                        'pic': item.get('Image', {}).get('url', '')
                    }
                )
                items.append(trending_item)
            
            logger.info(f"成功获取今日头条热榜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取今日头条热榜失败: {e}")
            return []