"""
配置文件
包含项目所有配置项
"""
import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

class Config:
    """基础配置"""
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # CORS配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
    
    # API配置
    API_PREFIX = '/api'
    
    # 文件上传配置
    UPLOAD_FOLDER = PROJECT_ROOT / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # 历史记录存储
    HISTORY_FOLDER = PROJECT_ROOT / 'history'
    
    # AI服务配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # 图片生成配置
    IMAGE_API_KEY = os.getenv('IMAGE_API_KEY', '')
    IMAGE_API_URL = os.getenv('IMAGE_API_URL', '')
    IMAGE_MODEL = os.getenv('IMAGE_MODEL', 'dall-e-3')
    
    # 并发配置
    MAX_CONCURRENT_GENERATIONS = int(os.getenv('MAX_CONCURRENT_GENERATIONS', '25'))
    
    # 图片配置
    IMAGE_WIDTH = 1080
    IMAGE_HEIGHT = 1440  # 小红书标准比例 3:4
    
    # 热榜抓取配置 - 参考 next-daily-hot 设计
    TRENDING_CACHE_TTL = int(os.getenv('TRENDING_CACHE_TTL', '1800'))  # 缓存有效期（秒），默认30分钟
    TRENDING_STALE_TTL = int(os.getenv('TRENDING_STALE_TTL', '7200'))  # 过期数据保留期（秒），默认2小时
    TRENDING_REQUEST_TIMEOUT = int(os.getenv('TRENDING_REQUEST_TIMEOUT', '5'))  # 请求超时（秒），优化为5秒
    TRENDING_MAX_RETRIES = int(os.getenv('TRENDING_MAX_RETRIES', '2'))  # 最大重试次数，优化为2次
    TRENDING_PROXY = os.getenv('TRENDING_PROXY', '')  # 代理地址，如 http://127.0.0.1:7890
    TRENDING_BACKOFF_FACTOR = float(os.getenv('TRENDING_BACKOFF_FACTOR', '0.5'))  # 重试退避因子，优化为0.5
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建必要的目录
        Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        Config.HISTORY_FOLDER.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}