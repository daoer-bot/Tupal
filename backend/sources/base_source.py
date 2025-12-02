"""
数据源基类
定义热榜数据结构和爬虫基础接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import requests
import logging

logger = logging.getLogger(__name__)


@dataclass
class TrendingItem:
    """热榜条目数据结构"""
    id: str  # 唯一标识
    title: str  # 标题
    url: str  # 链接地址
    mobile_url: Optional[str] = None  # 移动端链接
    hot_value: Optional[str] = None  # 热度值
    index: Optional[int] = None  # 排名
    extra: Optional[Dict[str, Any]] = None  # 额外信息（如图标、标签等）
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


class BaseSource(ABC):
    """数据源基类"""
    
    def __init__(self):
        self.source_id: str = ""  # 数据源ID
        self.source_name: str = ""  # 数据源名称
        self.icon: str = ""  # 图标URL
        self.interval: int = 600  # 刷新间隔（秒），默认10分钟
        
    @abstractmethod
    async def fetch_data(self) -> List[TrendingItem]:
        """
        抓取热榜数据
        子类必须实现此方法
        
        Returns:
            List[TrendingItem]: 热榜条目列表
        """
        pass
    
    def get_headers(self) -> Dict[str, str]:
        """
        获取请求头
        
        Returns:
            Dict[str, str]: 请求头字典
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
    
    async def fetch_html(self, url: str, timeout: int = 10) -> str:
        """
        获取网页HTML内容
        
        Args:
            url: 目标URL
            timeout: 超时时间（秒）
            
        Returns:
            str: HTML内容
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        try:
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=timeout
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise Exception(f"请求失败: {str(e)}")
    
    async def fetch_json(self, url: str, timeout: int = 10) -> Dict:
        """
        获取JSON数据
        
        Args:
            url: 目标URL
            timeout: 超时时间（秒）
            
        Returns:
            Dict: JSON数据
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        try:
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch JSON from {url}: {e}")
            raise Exception(f"请求失败: {str(e)}")
    
    def get_source_info(self) -> Dict[str, Any]:
        """
        获取数据源信息
        
        Returns:
            Dict[str, Any]: 数据源信息
        """
        return {
            'id': self.source_id,
            'name': self.source_name,
            'icon': self.icon,
            'interval': self.interval
        }