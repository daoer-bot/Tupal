"""
小红书内容解析数据源
"""
from typing import List, Optional
from .base_source import BaseSource, TrendingItem
import logging
import requests

logger = logging.getLogger(__name__)


class XiaohongshuSource(BaseSource):
    """小红书内容解析"""

    def __init__(self):
        super().__init__()
        self.source_id = "xiaohongshu"
        self.source_name = "小红书"
        self.icon = "/xiaohongshu.svg"
        self.api_url = "https://api.bugpk.com/api/xhsjx"

    async def parse_content(self, url: str) -> Optional[dict]:
        """解析小红书内容"""
        try:
            response = requests.get(
                self.api_url,
                params={'url': url},
                headers=self.get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if result.get('code') == 200:
                return result.get('data')

            logger.warning(f"小红书解析失败: {result.get('msg')}")
            return None

        except Exception as e:
            logger.error(f"小红书解析异常: {e}")
            return None

    async def fetch_data(self) -> List[TrendingItem]:
        """小红书不提供热榜，返回空列表"""
        return []
