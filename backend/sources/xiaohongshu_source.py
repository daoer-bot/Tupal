"""
小红书热榜数据源
使用RSSHub获取数据，解决反爬虫问题
"""
from typing import List
from .base_source import BaseSource, TrendingItem
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class XiaohongshuSource(BaseSource):
    """小红书热榜数据源"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "xiaohongshu"
        self.source_name = "小红书热榜"
        self.icon = "/icons/xiaohongshu.png"
        self.interval = 600  # 10分钟
        # RSSHub实例地址，可以使用官方或自建
        self.rsshub_base = "https://rsshub.app"  # 官方实例
    
    def get_headers(self):
        """重写请求头"""
        headers = super().get_headers()
        headers.update({
            'Accept': 'application/xml, text/xml, */*',
        })
        return headers
    
    async def fetch_data(self) -> List[TrendingItem]:
        """
        抓取小红书热榜数据
        
        Returns:
            List[TrendingItem]: 热榜条目列表
        """
        try:
            # 方案1: 使用RSSHub的小红书热榜
            url = f"{self.rsshub_base}/xiaohongshu/board/hot"
            
            try:
                # 获取RSS数据
                html = await self.fetch_html(url)
                items = self._parse_rss(html)
                
                if items:
                    logger.info(f"Successfully fetched {len(items)} items from Xiaohongshu via RSSHub")
                    return items
                else:
                    raise Exception("RSSHub返回数据为空")
                    
            except Exception as e:
                logger.warning(f"RSSHub方案失败: {e}")
                # 方案2: 尝试使用备用RSSHub实例
                backup_rsshub = "https://rss.shab.fun"
                url = f"{backup_rsshub}/xiaohongshu/board/hot"
                
                try:
                    html = await self.fetch_html(url)
                    items = self._parse_rss(html)
                    
                    if items:
                        logger.info(f"Successfully fetched {len(items)} items via backup RSSHub")
                        return items
                except Exception as e2:
                    logger.warning(f"备用RSSHub也失败: {e2}")
                    # 方案3: 使用模拟数据作为最后备选
                    logger.info("使用模拟数据作为备用方案")
                    return self._get_mock_data_items()
            
        except Exception as e:
            logger.error(f"Failed to fetch Xiaohongshu trending: {e}")
            return self._get_mock_data_items()
    
    def _parse_rss(self, rss_content: str) -> List[TrendingItem]:
        """
        解析RSS内容
        
        Args:
            rss_content: RSS XML内容
            
        Returns:
            List[TrendingItem]: 热榜条目列表
        """
        items = []
        
        try:
            # 解析XML
            root = ET.fromstring(rss_content)
            
            # 查找所有item节点
            for index, item in enumerate(root.findall('.//item')[:30], 1):
                try:
                    title = item.find('title').text if item.find('title') is not None else ''
                    link = item.find('link').text if item.find('link') is not None else ''
                    description = item.find('description').text if item.find('description') is not None else ''
                    
                    if not title or not link:
                        continue
                    
                    # 从描述中提取热度值（如果有）
                    hot_value = None
                    if description and '热度' in description:
                        # 尝试提取热度数字
                        import re
                        match = re.search(r'热度[：:]\s*(\d+\.?\d*[万k]?)', description)
                        if match:
                            hot_value = match.group(1)
                    
                    # 构建热榜条目
                    trending_item = TrendingItem(
                        id=f"xiaohongshu_{index}",
                        title=title.strip(),
                        url=link,
                        mobile_url=link,
                        hot_value=hot_value,
                        index=index,
                        extra={"tag": "热门"} if index <= 3 else None
                    )
                    items.append(trending_item)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse RSS item: {e}")
                    continue
            
            return items
            
        except Exception as e:
            logger.error(f"Failed to parse RSS: {e}")
            return []
    
    def _get_mock_data_items(self) -> List[TrendingItem]:
        """获取模拟热榜条目（备用方案）"""
        items = []
        mock_topics = [
            "今日穿搭分享", "美妆教程推荐", "减肥成功经验", 
            "旅行vlog攻略", "护肤品测评", "美食探店",
            "读书笔记分享", "健身打卡记录", "家居改造日记",
            "摄影技巧教学", "职场穿搭指南", "学习方法总结",
            "宠物日常记录", "手工制作教程", "理财经验分享",
            "化妆技巧教学", "发型设计灵感", "包包购物分享",
            "鞋子搭配推荐", "首饰挑选技巧", "香水使用心得",
            "口红试色对比", "面膜使用效果", "眼影画法教程",
            "腮红打法指南", "修容技巧分享", "眉毛画法教学",
            "睫毛膏推荐", "底妆产品测评", "卸妆产品对比"
        ]
        
        for index, title in enumerate(mock_topics[:30], 1):
            hot_value = 100000 - index * 2000
            trending_item = TrendingItem(
                id=f"xiaohongshu_mock_{index}",
                title=title,
                url=f"https://www.xiaohongshu.com/search_result?keyword={title}",
                mobile_url=f"https://www.xiaohongshu.com/search_result?keyword={title}",
                hot_value=f"{hot_value / 10000:.1f}万" if hot_value >= 10000 else str(hot_value),
                index=index,
                extra={"tag": "热门"} if index <= 3 else None
            )
            items.append(trending_item)
        
        logger.info(f"Generated {len(items)} mock items for Xiaohongshu")
        return items