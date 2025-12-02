"""
数据源基类
定义热榜数据结构和爬虫基础接口
参考 next-daily-hot 设计理念进行优化
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, asdict
from functools import wraps
import requests
import logging
import time
import random

logger = logging.getLogger(__name__)


# User-Agent 池 - 模拟真实浏览器
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


def retry_on_failure(max_retries: int = 3, backoff_factor: float = 1.0):
    """
    请求重试装饰器 - 参考 next-daily-hot 的重试机制
    
    Args:
        max_retries: 最大重试次数
        backoff_factor: 退避因子（指数退避）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {wait_time:.2f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed: {e}")
            raise last_exception
        return wrapper
    return decorator


def handle_errors(fallback_value: Any = None):
    """
    统一错误处理装饰器
    
    Args:
        fallback_value: 发生错误时返回的默认值
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                if fallback_value is not None:
                    return fallback_value
                raise
        return wrapper
    return decorator


@dataclass
class TrendingItem:
    """热榜条目数据结构 - 参考 next-daily-hot 标准化格式"""
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
        self.timeout: int = 10  # 请求超时时间
        self.max_retries: int = 3  # 最大重试次数
        self.proxy: Optional[str] = None  # 代理地址
        
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
        获取请求头 - 使用 User-Agent 池提高成功率
        
        Returns:
            Dict[str, str]: 请求头字典
        """
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }
    
    @retry_on_failure(max_retries=3, backoff_factor=1.0)
    async def fetch_html(self, url: str, timeout: Optional[int] = None) -> str:
        """
        获取网页HTML内容 - 带重试机制
        
        Args:
            url: 目标URL
            timeout: 超时时间（秒），默认使用实例配置
            
        Returns:
            str: HTML内容
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        timeout = timeout or self.timeout
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        
        try:
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=timeout,
                proxies=proxies,
                verify=True
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.Timeout:
            logger.error(f"Timeout fetching {url}")
            raise Exception(f"请求超时: {url}")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise Exception(f"请求失败: {str(e)}")
    
    @retry_on_failure(max_retries=3, backoff_factor=1.0)
    async def fetch_json(self, url: str, timeout: Optional[int] = None) -> Dict:
        """
        获取JSON数据 - 带重试机制
        
        Args:
            url: 目标URL
            timeout: 超时时间（秒），默认使用实例配置
            
        Returns:
            Dict: JSON数据
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        timeout = timeout or self.timeout
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        
        try:
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=timeout,
                proxies=proxies,
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            logger.error(f"Timeout fetching JSON from {url}")
            raise Exception(f"请求超时: {url}")
        except requests.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from {url}: {e}")
            raise Exception(f"JSON解析失败: {str(e)}")
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