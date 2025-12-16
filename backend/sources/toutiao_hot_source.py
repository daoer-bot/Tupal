"""
今日头条热榜数据源
参考 next-daily-hot 实现
"""
from typing import List, Dict
from .base_source import BaseSource, TrendingItem
import logging
import requests
import random

logger = logging.getLogger(__name__)

# 今日头条专用 User-Agent
TOUTIAO_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


class ToutiaoHotSource(BaseSource):
    """今日头条热榜"""
    
    def __init__(self):
        super().__init__()
        self.source_id = "toutiao"
        self.source_name = "今日头条"
        self.icon = "/toutiao.svg"
        self.interval = 300  # 5分钟刷新
    
    def get_headers(self) -> Dict[str, str]:
        """
        获取今日头条专用请求头
        今日头条对请求头有特殊要求，需要模拟真实浏览器访问
        """
        return {
            'User-Agent': random.choice(TOUTIAO_USER_AGENTS),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.toutiao.com/',
            'Origin': 'https://www.toutiao.com',
            'Connection': 'keep-alive',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
    
    async def fetch_data(self) -> List[TrendingItem]:
        """获取今日头条热榜数据"""
        url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
        
        try:
            # 使用自定义请求头直接请求
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=self.timeout,
                verify=True
            )
            
            # 检查响应状态
            if response.status_code != 200:
                logger.warning(f"今日头条请求失败，状态码: {response.status_code}")
                # 记录响应内容用于调试
                logger.debug(f"响应内容: {response.text[:500] if response.text else 'empty'}")
                return []
            
            # 尝试解析JSON
            try:
                data = response.json()
            except Exception as e:
                logger.error(f"今日头条JSON解析失败: {e}")
                logger.debug(f"响应内容: {response.text[:500] if response.text else 'empty'}")
                return []
            
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
                
                # 获取图片
                pic = ''
                image = item.get('Image')
                if image and isinstance(image, dict):
                    pic = image.get('url', '')
                
                trending_item = TrendingItem(
                    id=str(item.get('ClusterId', f"{index}")),
                    title=title,
                    url=f"https://www.toutiao.com/trending/{cluster_id_str}/",
                    mobile_url=f"https://api.toutiaoapi.com/feoffline/amos_land/new/html/main/index.html?topic_id={cluster_id_str}",
                    hot_value=str(item.get('HotValue', '')),
                    index=index + 1,
                    extra={
                        'label': item.get('LabelDesc', ''),
                        'pic': pic
                    }
                )
                items.append(trending_item)
            
            logger.info(f"成功获取今日头条热榜 {len(items)} 条")
            return items
            
        except requests.Timeout:
            logger.error(f"今日头条请求超时")
            return []
        except requests.RequestException as e:
            logger.error(f"今日头条请求异常: {e}")
            return []
        except Exception as e:
            logger.error(f"获取今日头条热榜失败: {e}")
            return []