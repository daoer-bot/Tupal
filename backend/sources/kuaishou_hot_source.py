"""
快手热榜数据源
参考 next-daily-hot 实现
"""
from typing import List, Dict
from .base_source import BaseSource, TrendingItem
import logging
import re
import json

logger = logging.getLogger(__name__)


class KuaishouHotSource(BaseSource):
    """快手热榜"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "kuaishou"
        self.source_name = "快手热榜"
        self.icon = "/kuaishou.svg"
        self.interval = 300  # 5分钟刷新
    
    def get_headers(self) -> Dict[str, str]:
        """覆盖父类方法，添加快手特定的请求头"""
        headers = super().get_headers()
        headers.update({
            'Referer': 'https://www.kuaishou.com/',
        })
        return headers
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取快手热榜数据"""
        url = "https://www.kuaishou.com/?isHome=1"
        
        try:
            import requests
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            response.raise_for_status()
            html_content = response.text
            
            # 从页面中提取 __APOLLO_STATE__ 数据
            pattern = r'window\.__APOLLO_STATE__=(.*?);\(function\(\)'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                logger.warning("快手热榜：无法提取 __APOLLO_STATE__ 数据")
                return []
            
            json_str = match.group(1)
            apollo_data = json.loads(json_str)
            default_client = apollo_data.get('defaultClient', {})
            
            # 获取热榜数据
            hot_rank_key = '$ROOT_QUERY.visionHotRank({"page":"home"})'
            hot_rank_data = default_client.get(hot_rank_key, {})
            all_items = hot_rank_data.get('items', [])
            
            if not all_items:
                logger.warning("快手热榜：热榜数据为空")
                return []
            
            items = []
            id_pattern = r'clientCacheKey=([A-Za-z0-9]+)'
            
            for index, item_ref in enumerate(all_items):
                try:
                    item_id = item_ref.get('id', '')
                    if not item_id:
                        continue
                    
                    item_data = default_client.get(item_id, {})
                    if not item_data:
                        continue
                    
                    title = item_data.get('name', '')
                    poster = item_data.get('poster', '')
                    hot_value = item_data.get('hotValue', '')
                    
                    # 从 poster URL 中提取视频 ID
                    video_id = ''
                    if poster:
                        id_match = re.search(id_pattern, poster)
                        if id_match:
                            video_id = id_match.group(1)
                    
                    if not video_id:
                        video_id = f"item_{index}"
                    
                    # 处理热度值
                    hot_value_num = ''
                    if hot_value:
                        if '万' in str(hot_value):
                            hot_value_num = str(float(str(hot_value).replace('万', '')) * 10000)
                        else:
                            hot_value_num = str(hot_value)
                    
                    trending_item = TrendingItem(
                        id=video_id,
                        title=title,
                        url=f"https://www.kuaishou.com/short-video/{video_id}",
                        mobile_url=f"https://www.kuaishou.com/short-video/{video_id}",
                        hot_value=hot_value_num,
                        index=index + 1,
                        extra={
                            'pic': poster
                        }
                    )
                    items.append(trending_item)
                    
                except Exception as e:
                    logger.warning(f"解析快手热榜条目失败: {e}")
                    continue
            
            logger.info(f"成功获取快手热榜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取快手热榜失败: {e}")
            return []