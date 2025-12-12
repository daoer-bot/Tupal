"""
路由模块
按功能域组织的API路由
"""
from .outline import outline_bp
from .image import image_bp
from .history import history_bp
from .trending import trending_bp
from .upload import upload_bp
from .material import material_bp
from .template import template_bp
from .xiaohongshu import xiaohongshu_bp

__all__ = [
    'outline_bp',
    'image_bp',
    'history_bp',
    'trending_bp',
    'upload_bp',
    'material_bp',
    'template_bp',
    'xiaohongshu_bp'
]